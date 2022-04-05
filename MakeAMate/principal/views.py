from datetime import datetime,timedelta
from urllib import request
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.http.response import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from .recommendations import rs_score
from .forms import RegistroForm
from .models import Usuario,Mate

def login_view(request):
    if request.user.is_authenticated:
        return redirect(homepage)
    template='loggeos/index.html'
    if request.method == "POST":
        nameuser = request.POST['username']
        passworduser = request.POST['pass']
        user = authenticate(username=nameuser, password=passworduser)
        if user is  None:
            return render(request,template, {'no_user':True})
        else:
            login(request, user)
            return redirect(homepage)
    return render(request,template)

def logout_view(request):
    logout(request)
    return redirect(homepage)


@login_required(login_url="/login")
def homepage(request):
    if request.user.is_authenticated:
        template = 'homepage.html'

        registrado= get_object_or_404(Usuario, usuario=request.user)
        ciudad= registrado.lugar
        if(registrado.piso):
            us= Usuario.objects.exclude(usuario=request.user).filter(lugar__contains=ciudad).filter(piso=False)
        else:
            us= Usuario.objects.exclude(usuario=request.user).filter(lugar__contains=ciudad)

        lista_mates=notificaciones_mates(request)
        tags_authenticated = registrado.tags.all()
        us_sorted = sorted(us, key=lambda u: rs_score(registrado, u), reverse=True)

        tags_usuarios = {u:{tag:tag in tags_authenticated for tag in u.tags.all()} for u in us_sorted}
        
        params = {'notificaciones':lista_mates,'usuarios': tags_usuarios, 'authenticated': registrado}
        return render(request,template,params)

    return login_view(request)

def accept_mate(request):
    if not request.user.is_authenticated:
        return redirect(login_view)

    id_us = request.POST['id_us']
    usuario = get_object_or_404(User, pk=id_us)

    if usuario == request.user:
        response = { 'success': False }
        return JsonResponse(response)

    mate, _ = Mate.objects.update_or_create(userEntrada=request.user, userSalida=usuario, defaults={'mate':True})

    # Comprueba si el mate es mutuo
    try:
        reverse_mate = Mate.objects.get(userEntrada=usuario, userSalida=request.user)
        mate_achieved = reverse_mate.mate
    except Mate.DoesNotExist:
        mate_achieved = False

    response = { 'success': True,
        'mate_achieved': mate_achieved, }

    return JsonResponse(response)

def reject_mate(request):
    if not request.user.is_authenticated:
        return redirect(login_view)

    id_us = request.POST['id_us']
    usuario = get_object_or_404(User, pk=id_us)

    if usuario == request.user:
        response = { 'success': False, }
        return JsonResponse(response)
    
    mate, _ = Mate.objects.update_or_create(userEntrada=request.user, userSalida=usuario, defaults={'mate':False})
    
    response = { 'success': True, }
    return JsonResponse(response)


def payments(request):
    template='payments.html'
    return render(request,template)

def notificaciones_mates(request):
    loggeado= request.user
    lista_usuarios=User.objects.filter(~Q(id=loggeado.id))
    lista_mates=[]
    for i in lista_usuarios:
        try:
            mate1=Mate.objects.get(mate=True,userEntrada=loggeado,userSalida=i)
            mate2=Mate.objects.get(mate=True,userEntrada=i,userSalida=loggeado)

            lista_mates.append(mate1.userSalida)
        except Mate.DoesNotExist:
            pass
    return lista_mates

def estadisticas_mates(request):
    loggeado= request.user
    perfil=Usuario.objects.get(usuario=loggeado)
    es_premium= perfil.es_premium()
    
    if(es_premium):
        #NUMERO DE INTERACIONES
        interacciones=Mate.objects.filter(userSalida=loggeado).count()
        
        #QUIEN TE HA DADO LIKE EN EL ÚLTIMO MES
        mesActual=datetime.now().month
        listmates=[]
        matesRecibidos=Mate.objects.filter(mate=True,userSalida=loggeado, fecha_mate__month=mesActual)
        for mR in matesRecibidos:
            listmates.append(mR.userEntrada)
        matesDados=Mate.objects.filter(userEntrada=loggeado)
        eliminados=0
        for mD in matesDados:
            #print(mD.userSalida)
            if(mD.userSalida in listmates):
                eliminados+=1
                listmates.remove(mD.userSalida)
        listperfiles=[]
        for us in listmates:
            listperfiles.append(Usuario.objects.get(usuario=us))

        #INTERACCIONES POR DÍA PARA LA GRÁFICA
        matesporFecha=matesRecibidos.values('fecha_mate__date').annotate(dcount=Count('fecha_mate__date')).order_by()
        listFecha=[]
        listdcount=[]
        for i in range(0,matesporFecha.count()):
            listFecha.append(matesporFecha[i]['fecha_mate__date'].strftime("%d/%m/%Y"))
            listdcount.append(matesporFecha[i]['dcount'])
        dictGrafica=dict(zip(listFecha,listdcount))
        
        #TOP TAGS CON QUIEN TE HA DADO LIKE
        listtags=[]
        tagsloggeado=perfil.tags.all().values()
        for tagl in tagsloggeado:
            listtags.append(tagl['etiqueta'])
        listTop=[]
        for m in listmates:
            tagsMates=Usuario.objects.get(usuario=m).tags.all().values()
            for tm in tagsMates:
                if tm['etiqueta'] in listtags:
                    listTop.append(tm['etiqueta'])
        dicTags=dict(zip(listTop,map(lambda x: listTop.count(x),listTop)))
        sorted_tuples = sorted(dicTags.items(), key=lambda item: item[1], reverse=True)
        sortedTags = {k: v for k, v in sorted_tuples}

        #COMPARATIVA NO PREMIUM VS PREMIUM
        fechaInicioPremium=perfil.fecha_premium - timedelta(days=30)
        mRNoPremium=Mate.objects.filter(mate=True,userSalida=loggeado, fecha_mate__lt=fechaInicioPremium).count()
        mRPremium=Mate.objects.filter(mate=True,userSalida=loggeado, fecha_mate__gt=fechaInicioPremium).count()

        #SCORE CON LAS PERSONAS QUE TE HAN DADO LIKE
        listScore=[]
        for i in listmates:
            perfilU=Usuario.objects.get(usuario=i)
            score = rs_score(perfil,perfilU)
            listScore.append(round(score*100) if(score*100 < 100)  else 100)
        dictScore=dict(zip(listmates,listScore))

        params={"interacciones":interacciones,"lista":listperfiles, "topTags":sortedTags, "matesGrafica":dictGrafica, "matesNPremium":mRNoPremium,
                "matesPremium":mRPremium, "scoreLikes":dictScore}
        return render(request,'estadisticas.html',params)
    else:
        return render(request,'homepage.html')

def registro(request):
    form = RegistroForm()
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid:
            usuario = form['usuario']
            contraseña = form['contraseña']
            form_piso = form['piso']
            form_foto = form['foto']
            form_fecha_nacimiento = form['fecha_nacimiento']
            form_lugar = form['lugar']
            form_nacionalidad = form['nacionalidad']
            form_genero = form['genero']
            form_pronombres = form['pronombres']
            form_universidad = form['universidad']
            form_estudios = form['estudios']
            form_idiomas = form['idiomas']
            form_tags = form['tags']
            form_aficiones = form['aficiones']

            user = User.objects.create(username=usuario,password=contraseña)
            user.save()
            perfil = Usuario.objects.create(usuario = user, piso = form_piso, foto = form_foto,
            fecha_nacimiento = form_fecha_nacimiento, lugar = form_lugar, nacionalidad = form_nacionalidad, genero = form_genero,
            pronombres = form_pronombres, universidad = form_universidad, estudios = form_estudios, idiomas = form_idiomas, tags = form_tags, aficiones = form_aficiones)
            perfil.save()
    return render(request, 'registro.html', {'form': form})

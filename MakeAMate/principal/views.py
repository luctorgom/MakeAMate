from urllib import request
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from .models import Usuario,Mate
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.http.response import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .recommendations import rs_score

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

    #QUIEN TE HA DADO LIKE EN EL ÚLTIMO MES
    mesActual=datetime.now().month
    listmates=[]
    matesRecibidos=Mates.objects.filter(mate=True,userSalida=loggeado, fecha_mate__month=mesActual)
    #print(matesRecibidos)
    for mR in matesRecibidos:
        listmates.append(mR.userEntrada)
    #print(listmates)
    matesDados=Mates.objects.filter(userEntrada=loggeado)
    #print(matesDados)
    eliminados=0
    for mD in matesDados:
        #print(mD.userSalida)
        if(mD.userSalida in listmates):
            eliminados+=1
            listmates.remove(mD.userSalida)
            #print(listmates)

    #LIKES POR DÍA PARA LA GRÁFICA
    matesporFecha=matesRecibidos.values('fecha_mate__date').annotate(dcount=Count('fecha_mate__date')-eliminados).order_by()
    #print(matesporFecha[0]['fecha_mate__date']) Recorrer diccionario par dia-numero likes

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

    #COMPARATIVA NO PREMIUM VS PREMIUM
    fechaPremium=perfil.fecha_premium
    #mRNoPremium=Mates.objects.filter(mate=True,userSalida=loggeado, fecha_mate__lt=fechaPremium).count
    #mRPremium=Mates.objects.filter(mate=True,userSalida=loggeado, fecha_mate__gt=fechaPremium).count

    params={"lista":listmates, "topTags":dicTags}
    return render(request,'homepage.html',params)

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

from django.contrib import admin
from .models import Usuario, Tag, Aficiones, Mate, Idioma, Oferta, Foto, Piso

# Register your models here.
admin.site.register(Usuario)
admin.site.register(Tag)
admin.site.register(Idioma)
admin.site.register(Aficiones)
admin.site.register(Mate)
admin.site.register(Oferta)
admin.site.register(Foto)
admin.site.register(Piso)
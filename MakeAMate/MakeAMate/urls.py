"""MakeAMate URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
#from turtle import home
from django.contrib import admin
from django.urls import path, include
from principal import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/',views.login_view,name="login"),
    path("logout/", views.logout_view, name= "logout"),
    path("accept-mate/", views.accept_mate, name= "accept-mate"),
    path("reject-mate/", views.reject_mate, name= "reject-mate"),
    path("payments/",views.payments,name="payments"),
    path('paypal/<int:pk>/', include('pagos.urls')),
    path('pagos/', include('pagos.urls')),
    path("mates/",views.estadisticas_mates,name="mates"),
    path("register/",views.registro,name="register"),
    path("register/terminos/",views.terminos,name="terminos"),
    path("register/registerSMS/<int:user_id>",views.twilio,name="registerSMS"),
    path("register/prueba/",views.prueba,name="prueba"),
    path('', views.homepage,name="home")

]

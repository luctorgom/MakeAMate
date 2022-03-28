from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('',views.paypal ,name='paypal' ),
    path('', views.paymentComplete, name="complete"),

]
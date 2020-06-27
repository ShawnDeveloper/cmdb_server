from django.urls import path
from django.conf.urls import url, include
from web import views

urlpatterns = [
    url(r'index/', views.index),
    url(r'server/create', views.create_server, name='create_server'),
]

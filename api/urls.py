
from django.urls import path
from django.conf.urls import url,include
from api import views
urlpatterns = [
    url(r'^get_data/',views.get_data),
    url(r'^get_server_list/',views.get_server_list)
]

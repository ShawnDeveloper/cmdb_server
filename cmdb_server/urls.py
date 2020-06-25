
from django.urls import path
from django.conf.urls import url,include

urlpatterns = [
    url(r'api/',include('api.urls')),
    url(r'web/',include('web.urls')),
]


from django.urls import path
from django.conf.urls import url,include
from api import views
urlpatterns = [
    url(r'^server/',views.ServerView.as_view()),
]

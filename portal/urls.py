from django.conf.urls import url
from portal import views


urlpatterns = [
    url(r'^panel/portal/$', views.index),
]

from django.conf.urls import url
from panel import views

urlpatterns = [
    url(r'^panel/$', views.index),
    url(r'^panel/login/$', views.login_user),
    url(r'^panel/logout/$', views.logout_user),
]
from django.conf.urls import url


urlpatterns = [
    url(r'^panel/$', 'panel.views.index'),
    url(r'^panel/login/$', 'panel.views.login_user'),
    url(r'^panel/logout/$', 'panel.views.logout_user' ),
]
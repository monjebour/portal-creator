# coding: utf-8
from django.contrib import admin
from models import Portal, Application, Server


@admin.register(Portal)
class PortalAdmin(admin.ModelAdmin):
    list_display = ['name', 'application', 'administrator', 'editor', 'customer']
    change_form_template = 'admin/portal.html'
    add_form_template = 'admin/change_form.html'


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['name', 'app_type', 'provider', 'internal_ip', 'external_ip', 'state', 'status']


@admin.register(Server)
class ServerAdmin(admin.ModelAdmin):
    list_display = ['name', 'server_type', 'ip']

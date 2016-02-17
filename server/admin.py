# coding: utf-8
from django.contrib import admin
from forms import ServerForm
from models import OperationalSystem, Recipe, Server


@admin.register(OperationalSystem)
class OperationalSystemAdmin(admin.ModelAdmin):
    list_display = ['name', 'os_type', 'server_type', 'architecture']


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['name', 'recipe_type', 'os_type']


@admin.register(Server)
class ServerAdmin(admin.ModelAdmin):
    form = ServerForm
    list_display = ['name', 'server_type', 'operational_system', 'external_ip', 'state']
    readonly_fields = ('external_id', 'state', 'message_error')
    change_form_template = 'admin/server.html'
    add_form_template = 'admin/change_form.html'

    def get_form(self, request, obj=None, **kwargs):
        form = super(ServerAdmin, self).get_form(request, obj=obj, **kwargs)
        form.request = request
        return form

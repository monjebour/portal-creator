# coding: utf-8
from __future__ import unicode_literals

from django.db import models


OS_TYPE = (
    ('linux', 'Linux'),
    ('windows', 'Windows')
)


class Server(models.Model):
    SERVER_TYPE = (
        ('docker', 'Docker'),
        ('vagrant', 'Vagrant')
    )

    SERVER_STATE = (
        ('draft', 'Draft'),
        ('creation', 'Creation'),
        ('done', 'Done'),
        ('stopped', 'Stopped'),
        ('destroyed', 'Destroyed'),
        ('error', 'Error')
    )

    name = models.CharField('Name', max_length=150)
    external_id = models.CharField('External ID', max_length=200, unique=True, null=True, blank=True)
    server_type = models.CharField('Server Type', choices=SERVER_TYPE, max_length=50, default='docker')
    memory_size = models.IntegerField('Memory Size', null=True, blank=True)
    disk_size = models.IntegerField('Disk Size', null=True, blank=True)
    operational_system = models.ForeignKey('OperationalSystem')
    recipe = models.ForeignKey('Recipe', null=True, blank=True)
    internal_ip = models.CharField('Internal IP', max_length=50, null=True, blank=True)
    external_ip = models.CharField('External IP', max_length=50, null=True, blank=True)
    state = models.CharField('State', choices=SERVER_STATE, max_length=50, default='draft')
    base_url = models.CharField('Base URL', max_length=255, null=True, blank=True, default='unix://var/run/docker.sock',
                                help_text="This URL is used on Docker containers to point a Kernel Server.")
    parent = models.ForeignKey('self', related_name='children', null=True, blank=True)
    initial_command = models.CharField('Initial Command', default='/bin/sh', max_length=200, null=True, blank=True)
    initial_port = models.IntegerField('Initial Port', null=True, blank=True)
    final_port = models.IntegerField('Final Port', null=True, blank=True)
    message_error = models.TextField('Message Erros', null=True, blank=True)

    class Meta:
        unique_together = (('server_type', 'name'),)
        verbose_name = 'Server/Container'
        verbose_name_plural = 'Servers/Containers'

    def __unicode__(self):
        return self.name


class OperationalSystem(models.Model):
    ARCHITECTURE = (
        ('32', '32 Bits'),
        ('64', '64 Bits')
    )

    SERVER_TYPE = (
        ('docker', 'Docker'),
        ('vagrant', 'Vagrant')
    )

    name = models.CharField('Name', max_length=200)
    os_type = models.CharField('Type', choices=OS_TYPE, max_length=50, default='linux')
    server_type = models.CharField('Server Type', choices=SERVER_TYPE, max_length=50, default='docker')
    architecture = models.CharField('Architecture', choices=ARCHITECTURE, max_length=50, default='64')
    image_name = models.CharField('Image Name', max_length=150, null=True, blank=True,
                                  help_text='Image Name is used on Docker Containers creation!')
    image_url = models.CharField('Image URL', max_length=200, null=True, blank=True)

    class Meta:
        unique_together = (('name', 'os_type'),)
        verbose_name = 'Operational System'
        verbose_name_plural = 'Operational Systems'

    def __unicode__(self):
        return self.name


class Recipe(models.Model):
    RECIPE_TYPE = (
        ('ansible', 'Ansible'),
        ('chef', 'Chef'),
        ('vagrant', 'Vagrant')
    )
    name = models.CharField('Name', max_length=150)
    recipe_type = models.CharField('Type', choices=RECIPE_TYPE, max_length=50, default='ansible')
    recipe_code = models.TextField('Recipe Code', null=True, blank=True)
    os_type = models.CharField('OS Type', choices=OS_TYPE, max_length=50, default='linux')

    class Meta:
        unique_together = (('name', 'recipe_type'),)
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'

    def __unicode__(self):
        return self.name

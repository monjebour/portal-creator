# coding: utf-8
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models
from portal.tasks import docker


class Portal(models.Model):
    STATE = (
        ('draft', 'Rascunho'),
        ('doing', 'Edição'),
        ('validation', 'Validação'),
        ('done', 'Publicado'),
        ('error', 'Erro'),
        ('destroyed', 'Destruído'),
        ('stopped', 'Parado')
    )

    administrator = models.ForeignKey(User, related_name='portal_administrator')
    editor = models.ForeignKey(User, related_name='portal_editor', null=True, blank=True)
    customer = models.ForeignKey(User, related_name='portal_customer', null=True, blank=True)
    name = models.CharField('Nome', max_length=200)
    description = models.TextField('Descrição', null=True, blank=True)
    application = models.ForeignKey('Application')
    state = models.CharField('Estado', choices=STATE, max_length=50, default='draft')
    current_task = models.CharField('Última Tarefa', max_length=200, null=True, blank=True)
    error = models.TextField('Mensagem de Erro', null=True, blank=True)

    class Meta:
        unique_together = (('name', 'application'),)

    def __unicode__(self):
        return self.name

    def run_task(self, task_name, application=None):
        tasks_list = {
            'docker': {
                'create': docker.create,
                'destroy': docker.destroy,
                'restart': docker.restart,
                'stop': docker.stop,
            },
        }
        task = tasks_list[application.provider][task_name]
        task.apply_async((application,), queue='creator')

    def save(self, *args, **kwargs):
        import ipdb; ipdb.set_trace()
        super(Portal, self).save(*args, **kwargs)
        if self.current_task:
            self.run_task(self.current_task, self.application)


class Application(models.Model):
    APP_TYPE = (
        ('default', 'Padrão'),
        ('secretariat', 'Secretaria')
    )

    PROVIDER = (
        ('os', 'Sistema Operacional'),
        ('docker', 'Docker'),
        ('kubernetes', 'Kubernetes')
    )

    APP_STATUS = (
        ('develop', 'Desenvolvimento'),
        ('uat', 'Homologação'),
        ('production', 'Produção'),
    )

    APP_STATE = (
        ('online', 'Online'),
        ('offline', 'Offline')
    )

    DISTRIBUTION = (
        ('single', 'Única'),
        ('multiple', 'Múltipla')
    )

    name = models.CharField('Nome', max_length=150)
    app_type = models.CharField('Tipo de Aplicação', choices=APP_TYPE, max_length=30, default='default')
    provider = models.CharField('Provedor da Aplicação', choices=PROVIDER, max_length=20, default='docker')
    uid = models.CharField('UID', max_length=200, unique=True, null=True, blank=True)
    internal_ip = models.CharField('IP Interno', max_length=50, null=True, blank=True)
    external_ip = models.CharField('IP Externo', max_length=50, null=True, blank=True)
    state = models.CharField('Estado', choices=APP_STATE, max_length=50, default='offline')
    status = models.CharField('Status', choices=APP_STATUS, max_length=50, default='develop')
    database = models.ForeignKey('Server', related_name="app_database", null=True, blank=True)
    message_error = models.TextField('Mensagem de Erro', null=True, blank=True)
    server = models.ManyToManyField('Server')
    distribution = models.CharField('Distribuição', choices=DISTRIBUTION, max_length=50, default='single')
    default = models.BooleanField('Padrão', default=0, unique=True)

    class Meta:
        unique_together = (('provider', 'name'),)
        verbose_name = 'Aplicação'
        verbose_name_plural = 'Aplicações'

    def __unicode__(self):
        return self.name


class Server(models.Model):
    SERVER_TYPE = (
        ('application', 'Aplicação'),
        ('database', 'Banco de Dados')
    )

    ENVIRONMENTS = (
        ('develop', 'Desenvolvimento'),
        ('uat', 'Homologação'),
        ('production', 'Produção')
    )

    name = models.CharField('Nome', max_length=200)
    server_type = models.CharField('Tipo de Servidor', choices=SERVER_TYPE, max_length=20, default='application')
    ip = models.CharField('IP', max_length=20)
    environment = models.CharField('Ambiente', choices=ENVIRONMENTS, max_length=20)
    description = models.TextField('Descrição', null=True, blank=True)
    load_balance_ip = models.CharField('IP Load Balance', max_length=20, null=True, blank=True)
    default = models.BooleanField('Padrão', default=0, unique=True)

    def __unicode__(self):
        return self.name

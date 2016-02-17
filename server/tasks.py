from __future__ import absolute_import

import celery
import docker
import time
import subprocess


class Command:

    def __init__(self, command_list=None):
        self.command_list = command_list
        self.run()

    def run(self):
        for command in self.command_list:
            proc = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            proc.communicate()


# DOCKER TASKS
@celery.task()
def docker_create_server(instance):
    time.sleep(5)
    client = docker.Client(base_url=instance.base_url)
    try:
        instance_name = instance.name.replace(' ', '_').lower()
        container = client.create_container(
            name=instance_name,
            image=instance.operational_system.image_name,
            ports=[instance.initial_port],
            stdin_open=True,
            tty=True,
            command=instance.initial_command,
            host_config=client.create_host_config(port_bindings={instance.initial_port: int(instance.initial_port) + 1}))

        instance.external_id = container.get('Id')
        instance.state = 'done'
        instance.message_error = ''
        client.start(container=container.get('Id'))
        log_message = 'SUCCESS! Container {} created.'.format(instance_name)
    except Exception as exc:
        instance.message_error = exc
        instance.state = 'error'
        log_message = 'ERROR! {}'.format(exc)
    instance.save()
    return log_message


@celery.task()
def docker_stop_server(instance):
    time.sleep(5)
    client = docker.Client(base_url=instance.base_url)
    try:
        client.stop(instance.external_id)
        instance.state = 'stopped'
        instance.save()
        log_message = 'SUCCESS! Container {} stopped.'.format(instance.name)
    except Exception as exc:
        log_message = 'ERROR! Container {} not stopped. EXCEPTION: {}'.format(instance.name, exc)
    return log_message


@celery.task()
def docker_restart_server(instance):
    time.sleep(5)
    client = docker.Client(base_url=instance.base_url)
    try:
        client.restart(instance.external_id)
        instance.state = 'done'
        instance.save()
        log_message = 'SUCCESS! Container {} restarted.'.format(instance.name)
    except Exception as exc:
        log_message = 'ERROR! Container {} not restarted. EXCEPTION: {}'.format(instance.name, exc)
    return log_message


@celery.task()
def docker_destroy_server(instance):
    time.sleep(5)
    client = docker.Client(base_url=instance.base_url)
    try:
        client.stop(instance.external_id)
        client.remove_container(instance.external_id or instance.name.replace(' ', '_').lower(), force=True)
        instance.state = 'destroyed'
        instance.save()
        log_message = 'SUCCESS! Container {} destroyed.'.format(instance.external_id)
    except Exception as exc:
        log_message = 'ERROR! Container {} not destroyed. EXCEPTION: {}'.format(instance.name, exc)
    return log_message


# VAGRANT TASKS
@celery.task()
def vagrant(instance, task_name, remote=None):
    name = instance.name.replace(' ', '_').lower()

    command_list = {
        'create_server': ['cd /vagrant; mkdir {}; cd {}; vagrant init {}; vagrant up'.format(
            name, name, instance.operational_system.image_name)],
        'destroy_server': ['cd /vagrant/{}; vagrant destroy --force; cd /vagrant; rm -rf {}'.format(name, name)],
        'restart_server': ['cd /vagrant/{}; vagrant reload'.format(name)],
        'start_server': ['cd /vagrant/{}; vagrant up'.format(name)],
        'stop_server': ['cd /vagrant/{}; vagrant halt --force'.format(name, name)]
    }

    instance_states = {
        'create_server': 'done',
        'destroy_server': 'destroyed',
        'restart_server': 'done',
        'start_server': 'done',
        'stop_server': 'stopped'
    }

    if remote:
        command_list = None

    try:
        Command(command_list=command_list[task_name])
        instance.state = instance_states[task_name]
    except Exception as exc:
        instance.state = 'error'
        instance.message_error = exc
    instance.save()

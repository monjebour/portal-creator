from __future__ import absolute_import

import celery
from docker import Client
import time


@celery.task()
def create_server(instance):
    time.sleep(5)
    client = Client(base_url=instance.base_url)
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
def stop_server(instance):
    time.sleep(5)
    client = Client(base_url=instance.base_url)
    try:
        client.stop(instance.external_id)
        instance.state = 'stopped'
        instance.save()
        log_message = 'SUCCESS! Container {} stopped.'.format(instance.name)
    except Exception as exc:
        log_message = 'ERROR! Container {} not stopped. EXCEPTION: {}'.format(instance.name, exc)
    return log_message


@celery.task()
def restart_server(instance):
    time.sleep(5)
    client = Client(base_url=instance.base_url)
    try:
        client.restart(instance.external_id)
        instance.state = 'done'
        instance.save()
        log_message = 'SUCCESS! Container {} restarted.'.format(instance.name)
    except Exception as exc:
        log_message = 'ERROR! Container {} not restarted. EXCEPTION: {}'.format(instance.name, exc)
    return log_message


@celery.task()
def destroy_server(instance):
    time.sleep(5)
    client = Client(base_url=instance.base_url)
    try:
        client.stop(instance.external_id)
        client.remove_container(instance.external_id or instance.name.replace(' ', '_').lower(), force=True)
        instance.state = 'destroyed'
        instance.save()
        log_message = 'SUCCESS! Container {} destroyed.'.format(instance.external_id)
    except Exception as exc:
        log_message = 'ERROR! Container {} not destroyed. EXCEPTION: {}'.format(instance.name, exc)
    return log_message

from __future__ import absolute_import

import celery
import docker
import time


# DOCKER
@celery.task()
def create(portal):
    client = docker.Client(base_url=portal.base_url)
    try:
        portal_name = portal.name.replace(' ', '_').lower()
        container = client.create_container(
            name=portal_name,
            image=portal.operational_system.image_name,
            ports=[portal.initial_port],
            stdin_open=True,
            tty=True,
            command=portal.initial_command,
            host_config=client.create_host_config(
                port_bindings={portal.initial_port: int(portal.initial_port) + 1}))

        portal.external_id = container.get('Id')
        portal.state = 'done'
        portal.message_error = ''
        client.start(container=container.get('Id'))
        log_message = 'SUCCESS! Site {} created.'.format(portal_name)
    except Exception as exc:
        portal.message_error = exc
        portal.state = 'error'
        log_message = 'ERROR! {}'.format(exc)
    portal.save()
    return log_message


@celery.task()
def stop(portal):
    client = docker.Client(base_url=portal.base_url)
    try:
        client.stop(portal.external_id)
        portal.state = 'stopped'
        portal.save()
        log_message = 'SUCCESS! Site {} stopped.'.format(portal.name)
    except Exception as exc:
        log_message = 'ERROR! Site {} not stopped. EXCEPTION: {}'.format(portal.name, exc)
    return log_message


@celery.task()
def restart(portal):
    client = docker.Client(base_url=portal.base_url)
    try:
        client.restart(portal.external_id)
        portal.state = 'done'
        portal.save()
        log_message = 'SUCCESS! Site {} restarted.'.format(portal.name)
    except Exception as exc:
        log_message = 'ERROR! Site {} not restarted. EXCEPTION: {}'.format(portal.name, exc)
    return log_message


@celery.task()
def destroy(portal):
    client = docker.Client(base_url=portal.base_url)
    try:
        client.stop(portal.external_id)
        client.remove_container(portal.external_id or portal.name.replace(' ', '_').lower(), force=True)
        portal.state = 'destroyed'
        portal.save()
        log_message = 'SUCCESS! Site {} destroyed.'.format(portal.external_id)
    except Exception as exc:
        log_message = 'ERROR! Site {} not destroyed. EXCEPTION: {}'.format(portal.name, exc)
    return log_message

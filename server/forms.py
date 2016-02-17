from django import forms
from tasks import docker_create_server, docker_destroy_server, docker_restart_server, docker_stop_server, vagrant


class ServerForm(forms.ModelForm):

    def run_task(self, instance, task_name):
        tasks = {
            'docker': {
                'create_server': docker_create_server,
                'destroy_server': docker_destroy_server,
                'restart_server': docker_restart_server,
                'stop_server': docker_stop_server
            },
            'vagrant': {
                'create_server': vagrant,
                'destroy_server': vagrant,
                'restart_server': vagrant,
                'stop_server': vagrant,
            }
        }
        task = tasks[instance.server_type][task_name]
        task.apply_async((instance, task_name), queue='creator')

    def save(self, commit=True):
        instance = super(ServerForm, self).save(commit)

        if instance.state in ['draft', 'destroyed', 'error']:
            if any(state in self.request.POST for state in ['create', 'recreate']):
                if instance.state == 'error':
                    self.run_task(instance, 'destroy_server')
                instance.state = 'creation'
                instance.save()
                self.run_task(instance, 'create_server')

        if instance.state in ['done', 'stopped']:
            if 'stop' in self.request.POST:
                self.run_task(instance, 'stop_server')

            if 'restart' in self.request.POST:
                self.run_task(instance, 'restart_server')

            if 'destroy' in self.request.POST:
                self.run_task(instance, 'destroy_server')
        return instance

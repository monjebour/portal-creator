from django import forms
from tasks import create_server, destroy_server, restart_server, stop_server
import time


class ServerForm(forms.ModelForm):

    def save(self, commit=True):

        instance = super(ServerForm, self).save(commit)

        if instance.state in ['draft', 'destroyed', 'error']:
            if any(state in self.request.POST for state in ['create', 'recreate']):
                if instance.state == 'error':
                    destroy_server.apply_async((instance,), queue='creator')

                instance.state = 'creation'
                instance.save()
                time.sleep(10)
                create_server.apply_async((instance,), queue='creator')

        if instance.state in ['done', 'stopped']:
            if 'stop' in self.request.POST:
                stop_server.apply_async((instance,), queue='creator')

            if 'restart' in self.request.POST:
                restart_server.apply_async((instance,), queue='creator')

            if 'destroy' in self.request.POST:
                destroy_server.apply_async((instance,), queue='creator')

        return instance

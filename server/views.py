from django.contrib.auth.decorators import login_required
from models import Server
from django.shortcuts import render


@login_required(login_url='/panel/login/')
def index(request):
    servers = Server.objects.all()
    return render(request, 'panel/server.html', {'servers': servers})

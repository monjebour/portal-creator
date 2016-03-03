from django.contrib.auth.decorators import login_required
from models import Portal
from django.shortcuts import render


@login_required(login_url='/panel/login/')
def index(request):
    portals = Portal.objects.all()
    return render(request, 'panel/portal.html', {'portals': portals})

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect


@login_required(login_url='/panel/login/')
def index(request):
    return render(request, 'panel/index.html')


def login_user(request):
    import ipdb; ipdb.set_trace()
    response = None
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                next_page = request.GET.get('next', None)
                if next_page:
                    return redirect(next_page)
                return redirect('/panel/')
            else:
                response = 'Username Disabled!'
        else:
            response = 'Invalid Username or Password!'
    return render(request, 'panel/login.html', {'response': response})


def logout_user(request):
    logout(request)
    return redirect('/panel/login/')

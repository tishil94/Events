from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, auth
from django.contrib import messages
# Create your views here.


def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        users = auth.authenticate(username=username, password=password)
        if users is not None:
            auth.login(request, users)
            return redirect('index')
        else:
            messages.info(request, 'invalid credentials')
            return redirect('login')
    else:
        return render(request, 'login.html')


def register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        name = request.POST.get('name')
        email = request.POST.get('email')
        if User.objects.filter(username=username).exists():
            messages.info(request, 'Username taken')
            return render(request, 'register.html')
        if User.objects.filter(email=email).exists():
            messages.info(request, 'email taken')
            return render(request, 'register.html')
        else:
            user = User.objects.create_user(username=username, password=password, email=email, first_name=name)
            user.save()
            return redirect('login')
    else:
        return render(request, 'register.html')


def user_logout(request):
    auth.logout(request)
    return redirect('index')


from django.shortcuts import render, redirect
from .models import Submission
from .forms import SubmissionForm
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from users.forms import CreateAccountForm
from django.db import IntegrityError


def news(request):
    submissions = Submission.objects.all().order_by('-created')
    return render(request, 'news.html', {'submissions': submissions})

def login(request):
    return render(request, 'login.html')

def submit(request):
    if request.method == 'POST':
        form = SubmissionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('news')
    else:
        form = SubmissionForm()
    return render(request, 'submit.html', {'form': form})

def newest(request):
    submissions = Submission.objects.all().order_by('-created')
    return render(request, 'newest.html', {'submissions': submissions})

def create_account(request):
    if request.method == 'POST':
        form = CreateAccountForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            try:
                user = User.objects.create_user(username=username, password=password)
                auth_login(request, user)
                return redirect('news')
            except IntegrityError:
                form.add_error('username', 'That username conflicts with an existing one. Names are case-insensitive. Please choose another.')
    else:
        form = CreateAccountForm()
    return render(request, 'create_account.html', {'form': form})

def logout(request):
    auth_logout(request)
    return redirect('news')
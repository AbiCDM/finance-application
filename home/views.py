from django.shortcuts import render, redirect
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login as user_login, logout as user_logout
from django.http import HttpResponseRedirect

def home(request):
    profile = Profile.objects.filter(user=request.user).first()
    expenses = Expense.objects.filter(user=request.user)
    
    if request.method == 'POST':
        text = request.POST.get('text')
        amount = request.POST.get('amount')
        expense_type = request.POST.get('expense_type')

        expense = Expense(name=text, amount=amount, expense_type=expense_type, user=request.user)
        expense.save()

        if expense_type == 'Positive':
            profile.balance += float(amount)
            profile.income += float(amount)
        else:
            profile.expenses += float(amount)
            profile.balance -= float(amount)

        profile.save()
        return redirect('/')

    context = {'profile': profile, 'expenses': expenses}
    return render(request, 'home.html', context)

def login_view(request):
    error = None  

    if request.method == 'POST':
        login = request.POST.get('login')
        password = request.POST.get('password')

        usr = authenticate(request, username=login, password=password)
        if usr is not None:
            user_login(request, usr)
            return HttpResponseRedirect('/')
        else:
            error = "Неверный логин или пароль."

    return render(request, 'login.html', {'error': error})

def reg_view(request):
    error = None  

    if request.method == 'POST':
        login = request.POST.get('login')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if password == password2:
            if User.objects.filter(username=login).exists():
                error = "Пользователь с таким логином уже существует."
            else:
                # Создаем пользователя и профиль для нового пользователя
                user = User.objects.create_user(username=login, password=password)
                Profile.objects.create(user=user, income=0, expenses=0, balance=0)
                user_login(request, user)
                return redirect('home')
        else:
            error = "Пароли не совпадают."

    return render(request, 'reg.html', {'error': error})
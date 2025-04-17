from django.shortcuts import render,redirect
from .models import *
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Автоматический вход после регистрации
            return redirect('home')  # Перенаправляем на главную
    else:
        form = UserCreationForm()
    
    return render(request, 'register.html', {'form': form})


def home(request):
    profile = Profile.objects.filter(user = request.user).first()
    expenses = Expense.objects.filter(user = request.user)
    if request.method == 'POST':
        text = request.POST.get('text')
        amount = request.POST.get('amount')
        expense_type = request.POST.get('expense_type') 

        expense = Expense(name=text , amount=amount , expense_type=expense_type , user= request.user)
        expense.save()
        
        if expense_type == 'Positive':
            profile.balance += float(amount)
        else:
            profile.expenses += float(amount)
            profile.balance -= float(amount)
            
        profile.save()
        return redirect('/')

    context = {'profile' : profile , 'expenses' : expenses}
    return render(request , 'home.html' , context)
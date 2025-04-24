from django.shortcuts import render, redirect
from .forms import RegisterForm
from .models import Profile, Expense
from django.contrib.auth import authenticate, login as user_login, logout as user_logout
from django.http import HttpResponseRedirect
from django.contrib.auth.forms import PasswordResetForm
def home(request):
    # Получаем профиль пользователя
    profile = Profile.objects.filter(user=request.user).first()

    # Если профиль не найден, перенаправляем на регистрацию
    if not profile:
        return redirect('reg')

    expenses = Expense.objects.filter(user=request.user)
    
    # Обработка POST-запроса для добавления новой операции
    if request.method == 'POST':
        text = request.POST.get('text')
        amount = request.POST.get('amount')
        expense_type = request.POST.get('expense_type')

        expense = Expense(name=text, amount=amount, expense_type=expense_type, user=request.user)
        expense.save()

        # Обновляем баланс в зависимости от типа операции
        if expense_type == 'Positive':
            profile.balance += float(amount)
            profile.income += float(amount)
        else:
            profile.expenses += float(amount)
            profile.balance -= float(amount)

        profile.save()
        return redirect('/')  # Перенаправление на домашнюю страницу

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
            return redirect('/')  # Перенаправляем на домашнюю страницу
        else:
            error = "Неверный логин или пароль."

    return render(request, 'login.html', {'error': error})

def reg_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():  # Если форма прошла валидацию
            user = form.save()  # Сохраняем нового пользователя
            # Создаем профиль для пользователя с начальными значениями
            Profile.objects.create(user=user, income=0, expenses=0, balance=0)
            # Логиним пользователя
            user_login(request, user)
            return redirect('/')  # Перенаправление на главную страницу
    else:
        form = RegisterForm()  # Если метод GET, создаем пустую форму

    return render(request, 'reg.html', {'form': form})

def logout_view(request):
    user_logout(request)
    return redirect('login')

def forgot_password_view(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            # Указываем локальный домен
            domain = '127.0.0.1:8000'  # Локальный сервер

            # Ссылка для сброса пароля генерируется автоматически
            form.save(
                request=request,
                use_https=request.is_secure(),
                from_email="noreply@yourdomain.com",  # Ваш email
                domain_override=domain,
            )

            return redirect('password_reset_done')  # Переход на страницу уведомления
        else:
            error = "Ошибка при восстановлении пароля."
    else:
        form = PasswordResetForm()

    return render(request, 'forgot_password.html', {'form': form, 'error': error if 'error' in locals() else None})
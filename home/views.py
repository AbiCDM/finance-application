from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from datetime import timedelta
from .models import Profile, Expense
from django.contrib.auth import authenticate, login as user_login, logout as user_logout
from django.contrib.auth.forms import PasswordResetForm
from .forms import RegisterForm

def home(request):
    # Получаем профиль пользователя
    profile = Profile.objects.filter(user=request.user).first()
    expenses = Expense.objects.filter(user=request.user)
    
    # Если профиль не найден, перенаправляем на регистрацию
    if not profile:
        return redirect('reg')

    current_datetime = timezone.now()

    period = request.GET.get('period', 'all')  # Получаем параметр периода из URL (по умолчанию - все)

    if period == 'last_week':
        last_week = current_datetime - timedelta(days=7)
        expenses = expenses.filter(date__gte=last_week)
    elif period == 'last_month':
        last_month = current_datetime - timedelta(days=30)
        expenses = expenses.filter(date__gte=last_month)

    # Сортировка по дате
    expenses = expenses.order_by('-date')  # Сортировка по убыванию даты

    # Обработка POST-запроса для добавления новой операции
    if request.method == 'POST':
        text = request.POST.get('text')
        amount = request.POST.get('amount')
        expense_type = request.POST.get('expense_type')
        date = request.POST.get('date')

        # Если дата не указана, используем текущую дату
        if not date:
            date = timezone.now()
        else:
            # Преобразуем строку в дату, если она была указана
            date = timezone.datetime.strptime(date, '%Y-%m-%dT%H:%M')

        expense = Expense(
            name=text,
            amount=amount,
            expense_type=expense_type,
            user=request.user,
            date=date  # Используем переданную или текущую дату
        )
        expense.save()

        # Обновляем баланс в зависимости от типа операции
        if expense_type == 'Positive':
            profile.balance += float(amount)
            profile.income += float(amount)
        else:
            profile.expenses += float(amount)
            profile.balance -= float(amount)

        profile.save()
        return redirect('/')  # Перенаправление на главную страницу

    context = {
        'profile': profile,
        'expenses': expenses,
        'current_datetime': current_datetime  # Передаем текущую дату для поля ввода
    }
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
    return redirect('reg')

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

def delete_transaction(request, transaction_id):
    try:
        transaction = Expense.objects.get(id=transaction_id, user=request.user)
        profile = Profile.objects.get(user=request.user)

        # Возвращаем сумму в зависимости от типа операции
        if transaction.expense_type == 'Positive':
            profile.balance -= transaction.amount
            profile.income -= transaction.amount
        else:
            profile.balance += transaction.amount
            profile.expenses -= transaction.amount

        profile.save()
        transaction.delete()
        return redirect('home')
    except Expense.DoesNotExist:
        # Если операция не найдена
        return redirect('home')
    


def edit_transaction(request, transaction_id):
    expense = get_object_or_404(Expense, id=transaction_id, user=request.user)
    profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':
        # Получаем данные из формы
        text = request.POST.get('text')
        amount = float(request.POST.get('amount'))
        expense_type = request.POST.get('expense_type')
        date_str = request.POST.get('date')

        # Конвертируем дату из строки в datetime
        from django.utils import timezone
        import datetime
        date = timezone.datetime.strptime(date_str, '%Y-%m-%dT%H:%M')

        # Корректируем баланс, вычитаем старую сумму операции
        if expense.expense_type == 'Positive':
            profile.balance -= expense.amount
            profile.income -= expense.amount
        else:
            profile.balance += expense.amount
            profile.expenses -= expense.amount

        # Обновляем поля операции
        expense.name = text
        expense.amount = amount
        expense.expense_type = expense_type
        expense.date = date
        expense.save()

        # Обновляем баланс с новыми значениями
        if expense_type == 'Positive':
            profile.balance += amount
            profile.income += amount
        else:
            profile.balance -= amount
            profile.expenses += amount

        profile.save()

        return redirect('home')

    else:
        # GET-запрос — отобразить форму с текущими данными операции
        context = {
            'expense': expense,
            'current_datetime': expense.date.strftime('%Y-%m-%dT%H:%M')
        }
        return render(request, 'edit_transaction.html', context)
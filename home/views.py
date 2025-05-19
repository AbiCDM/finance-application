from django.shortcuts import render, redirect, get_object_or_404
from datetime import timedelta, datetime
from django.utils import timezone
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

    period = request.GET.get('period', 'all')  
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    if start_date_str and end_date_str:
        try:
            # Преобразуем строки в объекты datetime
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d') + timedelta(days=1)  # включаем весь последний день
            expenses = expenses.filter(date__gte=start_date, date__lt=end_date)
        except ValueError:
            # Если дата некорректна, не фильтруем
            pass
    else:
        if period == 'last_week':
            last_week = current_datetime - timedelta(days=7)
            expenses = expenses.filter(date__gte=last_week)
        elif period == 'last_month':
            last_month = current_datetime - timedelta(days=30)
            expenses = expenses.filter(date__gte=last_month)

    # Сортировка по дате
    expenses = expenses.order_by('-date')  

    if request.method == 'POST':
        text = request.POST.get('text')
        amount = request.POST.get('amount')
        expense_type = request.POST.get('expense_type')
        date_str = request.POST.get('date')

        if not date_str:
            date = timezone.now()
        else:
            naive_date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
            date = timezone.make_aware(naive_date)

        expense = Expense(
            name=text,
            amount=amount,
            expense_type=expense_type,
            user=request.user,
            date=date
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
        return redirect('/') 

    context = {
        'profile': profile,
        'expenses': expenses,
        'current_datetime': current_datetime  
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
            return redirect('/')  
        else:
            error = "Неверный логин или пароль."

    return render(request, 'login.html', {'error': error})

def reg_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid(): 
            user = form.save() 
            # Логиним пользователя
            user_login(request, user)
            return redirect('/') 
    else:
        form = RegisterForm() 

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
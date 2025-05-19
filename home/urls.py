from . import views
from django.urls import path, include
from .views import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'), 
    path('login/', views.login_view, name='login'),  
    path('reg/', views.reg_view, name='reg'),
    path('forgot-password/', views.forgot_password_view, name='forgot-password'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('logout/', logout_view, name='logout'),
    path('delete/<int:transaction_id>/', delete_transaction, name='delete_transaction'),
    path('edit/<int:transaction_id>/', views.edit_transaction, name='edit_transaction'),
    path('add_category/', views.add_category, name='add_category'),
]
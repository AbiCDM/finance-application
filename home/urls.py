from . import views
from django.urls import path, include
from .views import *


urlpatterns = [
    path('', home),
    path('login/', login_view), 
    path('reg/', reg_view,name='reg')
]
from django.contrib import admin
from django.urls import path
from .views import UserLoginView, UsersignupView

urlpatterns = [
    path('login', UserLoginView.as_view(), name='login'),
    path('signup', UsersignupView.as_view(), name='signup')
]
from django.contrib import admin
from django.urls import path
from .views import UserLoginView, UsersignupView, UserLogoutView, UserSearchView, UserCheckAuthView

urlpatterns = [
    path('login', UserLoginView.as_view(), name='login'),
    path('signup', UsersignupView.as_view(), name='signup'),
    path('logout', UserLogoutView.as_view(), name='logout'),
    path('user-search', UserSearchView.as_view(), name='user-search'),
    path('check-auth', UserCheckAuthView.as_view(), name='check-auth')
]
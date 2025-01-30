from django.urls import path
from .views import FriendRequestView

urlpatterns = [path('add-friend', FriendRequestView.as_view(), name='add-friend')]
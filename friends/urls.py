from django.urls import path
from .views import FriendRequestView, FriendAcceptView

urlpatterns = [
    path('add-friend', FriendRequestView.as_view(), name='add-friend'),
    path('accept-friend-req', FriendAcceptView.as_view(), name='accept-friend-req')
]
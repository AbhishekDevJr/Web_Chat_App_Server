from django.urls import path
from .views import FriendRequestView, FriendAcceptView, GetFriendRequestsView

urlpatterns = [
    path('add-friend', FriendRequestView.as_view(), name='add-friend'),
    path('accept-friend-req', FriendAcceptView.as_view(), name='accept-friend-req'),
    path('get-friend-requests', GetFriendRequestsView.as_view(), name='get-friend-requests')
]
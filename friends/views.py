from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.authentication import  TokenAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from .models import FriendRequestModel
from django.db.models import Q
from .serializers import FriendRequestModelSerializer
import datetime
from authentication.models import CustomUser

# Create your views here.

class FriendRequestView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        try:
            sender_user = request.user.username
            receiver_user = request.data.get('username')
            
            if sender_user == receiver_user:
                return Response({
                    'title' : 'Self Friend Request',
                    'msg' : 'Sending friend request to yourself is not allowed!' 
                }, status=400)
            
            if sender_user and receiver_user:
                
                sender_pk = CustomUser.objects.get(username__icontains = sender_user).pk
                receiver_pk = CustomUser.objects.get(username__icontains = receiver_user).pk
                
                friend_request = FriendRequestModel.objects.filter(
                    Q(sender_id=sender_pk, receiver_id=receiver_pk, status__in=['pending', 'rejected', 'accepted']) | Q(sender_id=receiver_pk, receiver_id=sender_pk, status__in=['pending', 'rejected', 'accepted'])
                )
                
                if friend_request.exists():
                    return Response({
                        'title' : 'Request Already Exists',
                        'msg' : f"A Request between {sender_user} & {receiver_user} already exists."
                    }, status=200)
                else:
                    
                    friend_request_data = {
                        'sender' : sender_pk,
                        'receiver' : receiver_pk,
                        'status' : 'pending',
                        'timestamp' : datetime.datetime.now()
                    }
                    
                    friend_request_serialized = FriendRequestModelSerializer(data = friend_request_data)
                
                    if friend_request_serialized.is_valid():
                        friend_request_serialized.save()
                        return Response({
                            'title' : 'Friend Request Sent',
                            'msg' : f"Successfully sent Friend Request from {sender_user} to {receiver_user}",
                            'request_data' : friend_request_serialized.data
                        }, status=201)
                    else:
                        return Response({
                            'title' : 'Error creating Friend Request',
                            'msg' : 'Error creating Friend Request.', 'error_log' : friend_request_serialized.errors
                        }, status=500)
            else:
                return Response({
                    'title' : 'UserId Not Found',
                    'msg' : 'UserId Not Found.'
                }, status=400)
        except Exception as e:
            return Response({
                'title' : 'Unhandled Exception',
                'msg' : 'Unhandled Exception', 'error_log' : f"{e}"
            }, status=500)
        
class FriendAcceptView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        try:
            receiver_email = request.user.username
            sender_email = request.data.get('username')
            request_action = request.data.get('request_action')
            
            if sender_email and receiver_email and request_action:
                sender_user = CustomUser.objects.filter(email__icontains = sender_email).last()
                receiver_user = CustomUser.objects.filter(email__icontains = receiver_email).last()
                
                if sender_user and receiver_user:
                    friend_req_obj = FriendRequestModel.objects.filter(Q(sender=sender_user, receiver=receiver_user, status__iexact='pending') | Q(sender=receiver_user, receiver=sender_user, status__iexact='pending')).last()
                    
                    if friend_req_obj:
                        temp_frn_req_data = []
                        
                        if friend_req_obj.status == 'pending':
                            if request_action == 'accept':
                                request_status, friend_qs = friend_req_obj.accept_friend()
                            else:
                                request_status, friend_qs = friend_req_obj.reject_friend()
                                
                            
                            friend_request_data = FriendRequestModel.objects.filter(receiver=sender_user, status='pending')
                            friend_list = []
                            for item in friend_request_data:
                                temp_frn_req_data.append({
                                    'sender' : item.sender.email,
                                    'receiver' : item.receiver.email,
                                    'timestamp' : item.timestamp
                                })
                            if request_status == 'accepted':
                                
                                for friend in friend_qs:
                                    friend_list.append({
                                        'username' : friend.username if friend.username else None,
                                        'first_name' : friend.first_name if friend.first_name else None,
                                        'last_name' : friend.last_name if friend.last_name else None
                                    })
                                
                                return Response({
                                        'title' : 'Friend Request Accepted',
                                        'msg' : f"Friend request accepted B/W {sender_user.email} & {receiver_user.email}",
                                        'pending_requests' : temp_frn_req_data,
                                        'friendList' : friend_list
                                        
                                }, status=200)
                            elif request_status == 'rejected':
                                for friend in friend_qs:
                                    friend_list.append({
                                        'username' : friend.username if friend.username else None,
                                        'first_name' : friend.first_name if friend.first_name else None,
                                        'last_name' : friend.last_name if friend.last_name else None
                                    })
                                
                                return Response({
                                        'title' : 'Friend Request Rejected',
                                        'msg' : f"Friend request rejected B/W {sender_user.email} & {receiver_user.email}",
                                        'pending_requests' : temp_frn_req_data,
                                        'friendList' : friend_list
                                }, status=200)
                            else:
                                return Response({
                                    'title' : 'Error Accepting Friend Request',
                                    'msg' : 'Error while accepting friend request.'
                                }, status=500)
                        else:
                            return Response({
                                    'title' : 'Friend Request Already Accepted',
                                    'msg' : f"Friend Request b/w {sender_email} & {receiver_email} already accepted",
                                    'pending_requests' : temp_frn_req_data
                            }, status=200)
                    else:
                        return Response({
                            'title' : 'Friend Request Not Found',
                            'msg' : f"Friend Request between {sender_user} & {receiver_user} not found."
                        }, status=400)
                    
                else:
                    return Response({
                        'title' : 'User Not Found',
                        'msg' : 'User Not Found'
                    }, status=400)
            else:
                return Response({
                    'title' : 'Bad Request',
                    'msg' : 'Bad Request'
                }, status=400)
            
        except Exception as e:
            return Response({
                'title' : 'Unhandled Exception', 'error_log' : f"{e}",
                'msg' : 'Unhandled Exception', 'error_log' : f"{e}"
            }, status=500)
        
class GetFriendRequestsView(APIView):
    
    authentication_classes=[TokenAuthentication]
    permission_classes=[IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        try:
            friend_request_data = FriendRequestModel.objects.filter(receiver=request.user, status='pending')
            
            if friend_request_data.exists():
                curr_user_requests = []
                
                for friend_request in friend_request_data:
                    temp_user = CustomUser.objects.filter(id=friend_request.sender.pk).last()
                    curr_user_requests.append({
                        'firstName' : temp_user.first_name if temp_user.first_name else None,
                        'lastName' : temp_user.last_name if temp_user.last_name else None,
                        'username' : temp_user.username if temp_user.username else None
                    })
                
                return Response({
                    'title' : 'Request User Data',
                    'msg' : f"Friend Request Data for {request.user.email}.", 
                    'data' : curr_user_requests
                })
            else:
                return Response({
                    'title' : 'No Friend Requests Found',
                    'success' : f"No Friend Request Data found for {request.user.email}"
                })
                
        except Exception as e:
            return Response({
                'error' : 'Unhandled Exception', 'error_log' : f"{e}"
            }, status=500)
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
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
            sender_user = request.user.email
            receiver_user = request.data.get('email')
            
            if sender_user and receiver_user:
                
                sender_pk = CustomUser.objects.get(email__icontains = sender_user).pk
                receiver_pk = CustomUser.objects.get(email__icontains = receiver_user).pk
                
                friend_request = FriendRequestModel.objects.filter(
                    Q(sender_id=sender_pk, receiver_id=receiver_pk) | Q(sender_id=receiver_pk, receiver_id=sender_pk)
                )
                
                if friend_request.exists():
                    return Response({'error' : f"A Request between {sender_user} & {receiver_user} already exists."}, status=200)
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
                            'success' : f"Successfully sent Friend Request from {sender_user} to {receiver_user}",
                            'request_data' : friend_request_serialized.data
                        }, status=201)
                    else:
                        return Response({'error' : 'Error creating Friend Request.', 'error_log' : friend_request_serialized.errors}, status=500)
            else:
                return Response({'error' : 'UserId Not Found.'}, status=400)
        except Exception as e:
            return Response({'error' : 'Unhandled Exception', 'error_log' : f"{e}"}, status=500)
        
class FriendAcceptView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        try:
            sender_email = request.user.email
            receiver_email = request.data.get('email')
            
            if sender_email and receiver_email:
                sender_user = CustomUser.objects.filter(email__icontains = sender_email).last()
                receiver_user = CustomUser.objects.filter(email__icontains = receiver_email).last()
                
                if sender_user and receiver_user:
                    # Bug Alert : A Record shows in Pending even after Accepting, Because Fetching Pending Earlier
                    friend_req_obj = FriendRequestModel.objects.filter(Q(sender=sender_user, receiver=receiver_user) | Q(sender=receiver_user, receiver=sender_user)).last()
                    
                    if friend_req_obj:
                        temp_frn_req_data = []
                        friend_request_data = FriendRequestModel.objects.filter(receiver=sender_user, status='pending')
                        for item in friend_request_data:
                            temp_frn_req_data.append({
                                'sender' : item.sender.email,
                                'receiver' : item.receiver.email,
                                'timestamp' : item.timestamp
                            })
                        
                        if friend_req_obj.status == 'pending':
                            request_status = friend_req_obj.accept_friend()
                            
                            if request_status == 'accepted':
                                return Response(
                                    {
                                        'success' : f"Friend request accepted B/W {sender_user.email} & {receiver_user.email}",
                                        'pending_requests' : temp_frn_req_data
                                    }, status=200)
                            else:
                                return Response({'error' : 'Error while accepting friend request.'}, status=500)
                        else:
                            return Response(
                                {
                                    'success' : f"Friend Request b/w {sender_email} & {receiver_email} already accepted",
                                    'pending_requests' : temp_frn_req_data
                                }, status=200)
                    else:
                        return Response({'error' : f"Friend Request between {sender_user} & {receiver_user} not found."}, status=400)
                    
                else:
                    return Response({'error' : 'User Not Found'}, status=400)
            else:
                return Response({'error' : 'Bad Request'}, status=400)
            
        except Exception as e:
            return Response({'error' : 'Unhandled Exception', 'error_log' : f"{e}"}, status=500)
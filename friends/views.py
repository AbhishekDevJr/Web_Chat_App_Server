from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from .models import FriendRequestModel
from django.db.models import Q
from .serializers import FriendRequestModelSerializer
import datetime

# Create your views here.

class FriendRequestView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        try:
            sender_user = request.user.email
            receiver_user = request.data.get('email')
            
            if sender_user and receiver_user:
                # All Checks on FriendRequestModel has to be made using Primary Key
                friend_request = FriendRequestModel.objects.filter(
                    Q(sender=sender_user, receiver=receiver_user) | Q(sender=receiver_user, receiver=sender_user)
                )
                
                if friend_request.exists():
                    return Response({'error' : f"A Request between {sender_user} & {receiver_user} already exists."}, status=200)
                else:
                    
                    friend_request_data = {
                        'sender' : sender_user,
                        'receiver' : receiver_user,
                        'status' : 'pending',
                        'timestamp' : datetime.datetime.now()
                    }
                    new_friend_request = FriendRequestModelSerializer(data = friend_request_data)
                    
                    if new_friend_request.is_valid():
                        
                        new_friend_request.save()
                        return Response(new_friend_request.data, status=201)
                    else:
                        return Response({'error' : 'Error creating Friend Request.'}, status=500)
            else:
                return Response({'error' : 'UserId Not Found.'}, status=400)
        except Exception as e:
            return Response({'error' : 'Unhandled Exception', 'error_log' : f"{e}"}, status=500)
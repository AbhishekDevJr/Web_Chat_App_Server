from django.db import models
from authentication.models import CustomUser

# Create your models here.

class FriendRequestModel(models.Model):
    sender = models.ForeignKey(CustomUser, related_name='sent_requests', on_delete=models.CASCADE)
    receiver = models.ForeignKey(CustomUser, related_name='received_requests', on_delete=models.CASCADE)
    status = models.CharField(
        max_length=10,
        choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')],
        default='Pending'
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('sender', 'receiver')
        
    def __str__(self):
        return f"{self.sender} -> {self.receiver} ({self.status})"
    
    def accept_friend(self):
        if self.status == 'pending':
            self.status = 'accepted'
            
            self.sender.friends.add(self.receiver)
            self.receiver.friends.add(self.sender)
            self.save()
        
        return self.status
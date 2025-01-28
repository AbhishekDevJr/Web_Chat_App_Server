import datetime
from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    friends = models.ManyToManyField('self', blank=True, symmetrical=True)
    
    def __str__(self):
        return self.username
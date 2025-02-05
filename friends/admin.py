from django.contrib import admin
from .models import FriendRequestModel
# Register your models here.

class FriendRequestAdmin(admin.ModelAdmin):
    list_display=('sender', 'receiver', 'status', 'timestamp')
    search_fields=('sender', 'receiver', 'status')
    
admin.site.register(FriendRequestModel, FriendRequestAdmin)
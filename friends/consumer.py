import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        
        if not self.room_id:
            await self.disconnect()
            
        self.room_group_name = f"chat_{self.room_id}"
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        print(f'Server Logs: Web Socket connnection Established on Room ID {self.room_id}')
        await self.send(text_data=json.dumps({
            'Success': 'WebSocket Connection Established',
        }))
        
    async def disconnect(self):
        print(f'Server Logs: Web Socket Disconnecting from Room ID {self.room_id}')
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print(f'Server Logs: Web Socket Disconnected from Room ID {self.room_id}')
        
    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        sender = data['sender']
        message_type = data['message_type']
        receiver = {
            'userid': self.scope['user'].id,
            'username': self.scope['user'].username,
            'first_name': self.scope['user'].first_name,
            'last_name': self.scope['user'].last_name
        }
        
        # ADD MESSAGE STORING LOGIN IN DB HERE
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender,
                'message_type': message_type,
                'receiver': receiver
            }
        )
        
    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        message_type = event['message_type']
        receiver = event['receiver']
        
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
            'message_type': message_type,
            'receiver': receiver
        }))
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatGroup, ChatMessage
import pytz
from datetime import datetime

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        
        # Check if this is a delete message request
        if 'type' in text_data_json and text_data_json['type'] == 'delete_message':
            message_id = text_data_json['message_id']
            
            # Forward the delete message to the group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'delete_message',
                    'message_id': message_id
                }
            )
            return
        
        # Handle regular message
        message = text_data_json['message']
        user = self.scope["user"]
        
        # Save message to database
        message_obj = await self.save_message(message)
        
        # Get current time in IST
        ist = pytz.timezone('Asia/Kolkata')
        current_time = datetime.now(ist).strftime('%I:%M %p')
        
        # Send message to room group - ONLY ONCE
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': user.username,
                'timestamp': current_time,
                'message_id': message_obj.id
            }
        )
    
    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username'],
            'timestamp': event['timestamp'],
            'message_id': event['message_id']
        }))
    
    async def delete_message(self, event):
        message_id = event['message_id']
        
        # Send delete notification to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'delete_message',
            'message_id': message_id
        }))
    
    @database_sync_to_async
    def save_message(self, message_text):
        user = self.scope["user"]
        group_id = self.room_name
        
        # Get the chat group
        group = ChatGroup.objects.get(id=group_id)
        
        # Create and save the message
        message = ChatMessage.objects.create(
            group=group,
            sender=user,
            text_content=message_text,
            message_type='text'
        )
        
        return message
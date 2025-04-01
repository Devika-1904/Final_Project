from django.db import models
from django.conf import settings
import os

class ChatGroup(models.Model):
    name = models.CharField(max_length=100)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='chat_groups')

    def __str__(self):
        return self.name

class ChatMessage(models.Model):
    MESSAGE_TYPES = (
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
        ('audio', 'Audio'),
    )
    
    group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES, default='text')
    text_content = models.TextField(blank=True, null=True)
    media_file = models.FileField(upload_to='chat_media/', blank=True, null=True)
    transcription = models.TextField(blank=True, null=True)  # For audio transcription
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.sender.username}: {self.text_content[:50]}"
    
    def get_media_type(self):
        if not self.media_file:
            return None
        
        file_ext = os.path.splitext(self.media_file.name)[1].lower()
        
        if file_ext in ['.jpg', '.jpeg', '.png', '.gif']:
            return 'image'
        elif file_ext in ['.mp4', '.avi', '.mov', '.wmv']:
            return 'video'
        elif file_ext in ['.mp3', '.wav', '.ogg']:
            return 'audio'
        else:
            return 'file'
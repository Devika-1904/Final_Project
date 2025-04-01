from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import ChatGroup, ChatMessage
from django.contrib import messages
from django.http import JsonResponse
import json
import os
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import pytz
from datetime import datetime

@login_required
def chat_list(request):
    groups = ChatGroup.objects.all().order_by('-created_at')
    return render(request, 'chat/chat_list.html', {'groups': groups})

@login_required
def create_group(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        group = ChatGroup.objects.create(name=name, created_by=request.user)
        group.members.add(request.user)
        messages.success(request, 'Group created successfully!')
        return redirect('chat:chat_list')
    return render(request, 'chat/create_group.html')

@login_required
def chat_room(request, group_id):
    group = ChatGroup.objects.get(id=group_id)
    if request.user not in group.members.all():
        group.members.add(request.user)
    
    chat_messages = ChatMessage.objects.filter(group=group).order_by('timestamp')
    
    return render(request, 'chat/chat_room.html', {
        'group': group,
        'messages': chat_messages,
        'user': request.user
    })

@login_required
def send_message(request, group_id):
    if request.method == 'POST':
        try:
            group = ChatGroup.objects.get(id=group_id)
            if request.user not in group.members.all():
                return JsonResponse({'status': 'error', 'message': 'You are not a member of this group'})
            
            text_content = request.POST.get('text_content', '')
            message_type = request.POST.get('message_type', 'text')
            
            # Create a new message
            message = ChatMessage(
                group=group,
                sender=request.user,
                text_content=text_content,
                message_type=message_type
            )
            
            # Handle media files and documents
            if message_type in ['image', 'video', 'audio', 'document'] and 'media_file' in request.FILES:
                message.media_file = request.FILES['media_file']
                
                # For audio messages, add transcription if needed
                if message_type == 'audio':
                    # Transcription logic would go here if implemented
                    pass
            
            message.save()
            
            # Get current time in IST
            ist = pytz.timezone('Asia/Kolkata')
            current_time = datetime.now(ist).strftime('%I:%M %p')
            
            # Send message to WebSocket group
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'chat_{group_id}',
                {
                    'type': 'chat_message',
                    'message_id': message.id,
                    'sender': request.user.username,
                    'text_content': text_content,
                    'message_type': message_type,
                    'timestamp': current_time
                }
            )
            
            return JsonResponse({
                'status': 'success',
                'message_type': message_type
            })
            
        except ChatGroup.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Group not found'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


@login_required
def delete_message(request, message_id):
    if request.method == 'POST':
        try:
            message = ChatMessage.objects.get(id=message_id)
            
            # Check if the user is the sender of the message or an admin
            if message.sender != request.user and not request.user.is_staff:
                return JsonResponse({
                    'status': 'error',
                    'message': 'You can only delete your own messages'
                })
            
            # Store the group ID before deleting the message
            group_id = message.group.id
            
            # Delete the message
            message.delete()
            
            # Notify WebSocket group about the deletion
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'chat_{group_id}',
                {
                    'type': 'delete_message',
                    'message_id': message_id
                }
            )
            
            return JsonResponse({
                'status': 'success',
                'message': 'Message deleted successfully'
            })
            
        except ChatMessage.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Message not found'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request'
    })

from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.chat_list, name='chat_list'),
    path('create/', views.create_group, name='create_group'),
    path('room/<int:group_id>/', views.chat_room, name='chat_room'),
    path('room/<int:group_id>/send/', views.send_message, name='send_message'),
    path('message/<int:message_id>/delete/', views.delete_message, name='delete_message'),
]
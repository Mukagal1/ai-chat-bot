from django.db import models
from django.contrib.auth.models import User as DjangoUser

class ChatUser(models.Model):  # chatbot_user
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)

    class Meta:
        db_table = 'chatuser'

class ChatSessions(models.Model):  # chatbot_sessions
    username = models.CharField(max_length=255)
    session_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chatsessions'

class ChatDetails(models.Model):  # chatbot details
    SENDER_CHOICES = (
        ('user', 'user'),
        ('assistant', 'assistant'),
    )
    id = models.AutoField(primary_key=True)
    sender = models.CharField(max_length=255, choices=SENDER_CHOICES)
    session = models.ForeignKey(ChatSessions, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chatdetails'

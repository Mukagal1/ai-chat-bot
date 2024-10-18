import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_project.settings')

django.setup()

from chatbot.models import User, ChatSessions, ChatDetails


ChatDetails.objects.all().delete()
ChatSessions.objects.all().delete()

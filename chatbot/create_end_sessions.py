import os
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import User, ChatSessions, ChatDetails
import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from openai import OpenAI
from chat_project.settings import OPENAI_API_KEY
import threading
from chatbot.get_ai_response import get_ai_response, update_session_title
import logging
logger = logging.getLogger(__name__)

def sessions_list(request, username):
    sessions = ChatSessions.objects.filter(username=username).order_by('-created_at').values('session_id', 'title', 'is_active')
    request.session['sessions'] = list(sessions)
    return sessions


def end_chat(request, history):
    active_session_id = request.session.get('active_session_id')
    if active_session_id:
        try:
            session = ChatSessions.objects.get(session_id=active_session_id)
            update_session_title(session, history)
            session.is_active = False
            session.save()
        except ChatSessions.DoesNotExist:
            logger.error(f"Session with ID {active_session_id} does not exist.")
    else:
        logger.error("No active session ID found.")
    history.clear()


def create_chat(request, username):
    session = ChatSessions.objects.create(
        username=username,
        is_active=True,
        title='New session'
    )

    request.session['active_session_id'] = session.session_id

    return session
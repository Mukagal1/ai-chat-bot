import os
from django.http import JsonResponse
from .models import User, ChatSessions, ChatDetails
import json
from chatbot.get_ai_response import get_ai_response


import logging
logger = logging.getLogger(__name__)

def sessions_list(request, username):
    sessions = ChatSessions.objects.filter(username=username).order_by('-created_at').values('session_id', 'title', 'is_active')
    request.session['sessions'] = list(sessions)
    return sessions


def end_chat(request, history):
    active_session_id = request.session.get('active_session_id')
    session = None
    if active_session_id:
        try:
            session = ChatSessions.objects.get(session_id=active_session_id)
            theme = request.session.get('theme', 'light')
            session.title = get_ai_response(theme=theme, new_message="Generate a concise title based on the entire conversation history.", conversation_history=history)
            session.is_active = False
            session.save()
        except ChatSessions.DoesNotExist:
            logger.error(f"Session with ID {active_session_id} does not exist.")
    else:
        logger.error("No active session ID found.")
    history.clear()

    return session


def create_chat(request, username):
    session = ChatSessions.objects.create(
        username=username,
        is_active=True,
        title='New session'
    )

    request.session['active_session_id'] = session.session_id

    return session
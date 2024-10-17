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
from chatbot.create_end_sessions import sessions_list, end_chat, create_chat
from chatbot.get_ai_response import get_ai_response, update_session_title


history = []

import logging
logger = logging.getLogger(__name__)


@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            request.session['username'] = username

            sessions_list(request, username)

            return redirect('main')  # Redirect to main page
    return render(request, 'chatbot/login.html')


@csrf_exempt
def register_view(request):
    if request.user.is_authenticated:
        return redirect('main')
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        User.objects.create_user(username=username, email=email, password=password)
        return redirect('login')  # Redirecting to login page
    return render(request, 'chatbot/register.html')


@csrf_exempt
@login_required
def main(request):
    username = request.session.get('username', 'Guest')
    sessions = request.session.get('sessions', [])

    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            action = data.get('action')

            logger.debug("Action received: %s", action)

            if action == 'new_chat':
                logger.debug("Creating a new chat session")
                end_chat(request, history)
                last_session = (create_chat(request, username))

                return JsonResponse({
                    'success': True,
                    'last_session': {
                        'session_id': last_session.session_id,
                        'title': last_session.title,
                    },
                })

            active_session_id = request.session.get('active_session_id')

            if not active_session_id:
                last_session = create_chat(request, username)

                active_session_id = last_session.session_id
                request.session['active_session_id'] = active_session_id


            user_message = data.get('message', '')

            active_session = ChatSessions.objects.get(session_id=active_session_id)

            ChatDetails.objects.create(
                sender='user',
                session=active_session,
                message=user_message
            )

            response = get_ai_response(user_message, history)

            ChatDetails.objects.create(
                sender='assistant',
                session=active_session,
                message=response
            )

            return JsonResponse({'response': response})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User does not exist'}, status=404)
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)

    return render(request, 'chatbot/main.html', {
        'username': username,
        'sessions': sessions
    })


@csrf_exempt
def premain(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')

            response = get_ai_response(user_message, history)


            return JsonResponse({'response': response})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return render(request, 'chatbot/premain.html')


def logout_view(request):
    end_chat(request, history)
    request.session.pop('active_session_id', None)
    logout(request)
    return redirect('login')

import os
import json
import logging

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .models import ChatSessions, ChatDetails
from chat_project.settings import OPENAI_API_KEY
from chatbot.create_end_sessions import sessions_list, end_chat, create_chat
from openai import OpenAI
from chatbot.get_ai_response import get_ai_response

logger = logging.getLogger(__name__)

history = []


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

            history.clear()

            return redirect('main')
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
        return redirect('login')
    return render(request, 'chatbot/register.html')


@login_required
@csrf_exempt
def chat(request, session_id):
    try:
        if not session_id:
            return JsonResponse({'error': 'session_id is required'}, status=400)

        if not ChatSessions.objects.filter(session_id=session_id).exists():
            return JsonResponse({'error': 'Session does not exist'}, status=404)

        details = ChatDetails.objects.filter(session__session_id=session_id).values('role', 'message')
            
        details_list = list(details)

        history.clear()
        for detail in details_list[:10]:
            history.append({'role': detail['role'], 'content': detail['message']})

        request.session['active_session_id'] = session_id

        return JsonResponse({
            'details': details_list,
        })

    except ChatSessions.DoesNotExist:
        return JsonResponse({'error': 'Session does not exist'}, status=404)
    except Exception as e:
        logger.error(f"Error in chat view: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)



@csrf_exempt
@login_required
def main(request, session_id=None):
    username = request.session.get('username', 'Guest')
    sessions = request.session.get('sessions', [])

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            action = data.get('action')

            logger.debug("Action received: %s", action)

            if action == 'new_chat':
                logger.debug("Creating a new chat session")

                last_old_session = end_chat(request, history)
                last_session = create_chat(request, username)

                active_session_id = last_session.session_id
                request.session['active_session_id'] = active_session_id

                response_data = {
                    'success': True,
                    'new_session': {
                        'session_id': last_session.session_id,
                        'title': last_session.title,
                    },
                    'old_session': {
                        'session_id': last_old_session.session_id if last_old_session else None,
                        'title': last_old_session.title if last_old_session else None,
                    }
                }
                return JsonResponse(response_data)

            user_message = data.get('message', '')
            active_session_id = request.session.get('active_session_id')

            if not active_session_id:
                last_session = create_chat(request, username)
                active_session_id = last_session.session_id
                request.session['active_session_id'] = active_session_id

            active_session = ChatSessions.objects.get(session_id=active_session_id)

            ChatDetails.objects.create(
                role='user',
                session=active_session,
                message=user_message
            )

            theme = request.session.get('theme', 'light')
            response = get_ai_response(theme, user_message, history)

            ChatDetails.objects.create(
                role='assistant',
                session=active_session,
                message=response
            )

            return JsonResponse({
                'success': True,
                'response': response,
                'new_session': {
                    'session_id': int(active_session.session_id),
                    'title': active_session.title,
                }
            })
        
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User does not exist'}, status=404)
        except ChatSessions.DoesNotExist:
            return JsonResponse({'error': 'Active session does not exist'}, status=404)
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)


    return render(request, 'chatbot/main.html', {
        'username': username,
        'sessions': sessions
    })


@csrf_exempt
def theme(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        theme = data.get('theme', 'light')
        request.session['theme'] = theme
        return JsonResponse({'status': 'success', 'theme': theme})


@csrf_exempt
def premain(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')

            theme = request.session.get('theme', 'light')
            response = get_ai_response(theme, user_message, history)

            return JsonResponse({'response': response})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return render(request, 'chatbot/premain.html')


def logout_view(request):
    session = end_chat(request, history)
    request.session.pop('active_session_id', None)
    logout(request)
    return redirect('login')

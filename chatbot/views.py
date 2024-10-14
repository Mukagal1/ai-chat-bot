import os
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import ChatUser, ChatSessions, ChatDetails
import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from openai import OpenAI
from chat_project.settings import OPENAI_API_KEY


@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            request.session['username'] = username

            return redirect('main')  # Redirecting to main page
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


client = OpenAI(api_key=OPENAI_API_KEY)

def get_ai_response(new_message, conversation_history):
    try:
        conversation_history.append({"role": "user", "content": new_message})
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=conversation_history
        )
        
        conversation_history.append({"role": "assistant", "content": response.choices[0].message.content})
        
        return response.choices[0].message.content
    
    except Exception as e:
        print("Error in get_ai_response:", str(e))
        raise e


history = []

import logging
logger = logging.getLogger(__name__)

@csrf_exempt
@login_required
def main(request):
    username = request.session.get('username', 'Guest')

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')

            print(user_message)

            session, _ = ChatSessions.objects.get_or_create(
                username=username,
                is_active=True,
                defaults={'title': 'New session'}
            )

            print(session)

            ChatDetails.objects.create(
                sender='user',
                session_id=session,
                message=user_message
            )

            response = get_ai_response(user_message, history)

            ChatDetails.objects.create(
                sender='assistant',
                session_id=session,
                message=response
            )

            return JsonResponse({'response': response, 'username': username})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User does not exist'}, status=404)
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)

    return render(request, 'chatbot/main.html', {'username': username})


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
    logout(request)
    history.clear()
    print('logged out')
    return redirect('login')

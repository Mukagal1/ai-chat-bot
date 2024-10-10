import os
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import User, Message
import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from openai import OpenAI
from chat_project.settings import OPENAI_API_KEY


@csrf_exempt
def send_message(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        sender_id = data.get('sender_id')
        receiver_id = data.get('receiver_id')
        message_text = data.get('text')

        if not (sender_id and receiver_id and message_text):
            return JsonResponse({'error': 'Invalid data'}, status=400)

        try:
            sender = User.objects.get(id=sender_id)
            receiver = User.objects.get(id=receiver_id)

            message = Message.objects.create(
                sender=sender,
                receiver=receiver,
                text = message_text
            )

            return JsonResponse({'success': 'Message sent successfully!'}, status=200)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


@csrf_exempt
def get_messages(request):
    if request.method == 'GET':
        user_id = request.GET.get('user_id')

        if not user_id:
            return JsonResponse({'error': 'User ID is required'}, status=400)

        try:
            user = User.objects.get(id=user_id)

            sent_messages = Message.objects.filter(sender=user)
            received_messages = Message.objects.filter(receiver=user)

            messages = [
                {'from': msg.sender.username, 'to':msg.receiver.username, 'text': msg.text, 'timestamp': msg.timestamp}
                for msg in sent_messages.union(received_messages).order_by('timestamp')
            ]

            return JsonResponse({'messages': messages}, status=200)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
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

def get_ai_response(message):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": message}]
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        print("Error in get_ai_response:", str(e))
        raise e

@csrf_exempt
@login_required
def main(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')

            response = get_ai_response(user_message)


            return JsonResponse({'response': response})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return render(request, 'chatbot/main.html')


def logout_view(request):
    logout(request)
    print('logged out')
    return redirect('login')

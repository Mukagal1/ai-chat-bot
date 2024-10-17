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
import logging
logger = logging.getLogger(__name__)

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


def generate_session_title(session, conversation_history):
    try:
        messages = [{"role": "system", "content": "Generate a concise title based on the entire conversation history."}]

        messages += [{"role": item["role"], "content": item["content"]} for item in conversation_history]

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=20
        )

        new_title = response.choices[0].message.content.strip()
        session.title = new_title if new_title else "New session"
        session.save()

    except Exception as e:
        print(f"Error generating session title: {str(e)}")


def update_session_title(session, history):
    thread = threading.Thread(target=generate_session_title, args=(session, history[:10]))
    thread.start()
import os
from django.shortcuts import render, redirect
from django.http import JsonResponse
import json
from openai import OpenAI
from chat_project.settings import OPENAI_API_KEY
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
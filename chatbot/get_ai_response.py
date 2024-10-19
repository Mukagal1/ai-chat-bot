import os
import json
from openai import OpenAI
from chat_project.settings import OPENAI_API_KEY
import logging
logger = logging.getLogger(__name__)

client = OpenAI(api_key=OPENAI_API_KEY)

def get_ai_response(new_message, conversation_history):
    try:
        if not any(message['role'] == 'system' for message in conversation_history):
            system_prompt = {
                "role": "system",
                "content": (
                    "Вы универсальный эксперт, способный адаптироваться к любой сфере, упомянутой в сообщении пользователя. "
                    "Когда пользователь задает вопрос или делает запрос, вы должны ответить как высококвалифицированный специалист "
                    "в соответствующей области. Ваши ответы должны быть профессиональными, точными и детализированными, "
                    "независимо от темы запроса. Если пользователь спрашивает о технической теме — вы действуете как эксперт в "
                    "технологиях, если о медицине — как медицинский специалист, если о бизнесе — как эксперт в бизнес-стратегиях и так далее. "
                    "Ваши ответы должны быть структурированы и логичны. "
                    "Просто предоставьте ответ на вопрос пользователя без каких-либо дополнительных ключей или структур."
                )
            }
            conversation_history.insert(0, system_prompt)

        conversation_history.append({"role": "user", "content": new_message})

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=conversation_history
        )

        assistant_message = response.choices[0].message.content
        conversation_history.append({"role": "assistant", "content": assistant_message})

        return assistant_message

    except Exception as e:
        logger.error("Error in get_ai_response: %s", str(e))
        raise e
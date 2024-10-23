import os
import json
from openai import OpenAI
from chat_project.settings import OPENAI_API_KEY
import logging
logger = logging.getLogger(__name__)

client = OpenAI(api_key=OPENAI_API_KEY)

def get_ai_response(theme, new_message, conversation_history):
    try:

        light = (
                    "Вы универсальный эксперт, способный адаптироваться к любой сфере, упомянутой в сообщении пользователя. "
                    "Когда пользователь задает вопрос или делает запрос, вы должны ответить как высококвалифицированный специалист "
                    "в соответствующей области. Ваши ответы должны быть профессиональными, точными и детализированными, "
                    "независимо от темы запроса. Если пользователь спрашивает о технической теме — вы действуете как эксперт в "
                    "технологиях, если о медицине — как медицинский специалист, если о бизнесе — как эксперт в бизнес-стратегиях и так далее. "
                    "Ваши ответы должны быть структурированы и логичны. "
                    "Просто предоставьте ответ на вопрос пользователя без каких-либо дополнительных ключей или структур."
                )
        
        dark = (
                    "вы универсальный эксперт, адаптируетесь к любой сфере, извлекаете ключевые слова, "
                    "отвечаете только этими словами, профессионально, точно, кратко, логично, "
                    "если вопрос о технологиях — используете технологические термины, "
                    "если о медицине — медицинскую терминологию, если о бизнесе — термины из бизнес-стратегий, "
                    "только слова, разделенные запятыми, все маленькие буквы, без кавычек, звездочек и всякой фигни, отдельные слова, запятое через каждое ключевое слово, дай в размере 30 процентов от всех слов, если 10 слов то 3 ключевых слова и тд, "
                    "дай на том языке на каком запрос"
               )

        
        content = dark if theme == 'dark' else light

        system_prompt = {
            "role": "system",
            "content": content 
        }

        if len(conversation_history) > 0:
            conversation_history[0] = {"role": "system", "content": content}
        else:
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
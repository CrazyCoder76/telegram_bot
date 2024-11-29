import os
import time
import datetime
from uuid import uuid4
from dotenv import load_dotenv
from save_message import save_message_to_vector_db
from graph import generate_response, generate_intro
import telebot

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
tb = telebot.TeleBot(TOKEN)

last_message_time = time.time()
thread_id = ""

@tb.message_handler(func=lambda message: True)
def handle_message(message):
    current_date = datetime.datetime.now()
    try:
        chat_id = message.from_user.id
        question = f"[Author: {message.from_user.username} at {current_date.isoformat()}] Message: {message.text}"

        response = generate_response(question, chat_id)
        if response:
            tb.reply_to(message, response)

    except Exception as e:
        print(f"Failed to respond to message: {e}")
        raise

    # Save data
    try:
        data = {
            "content": f"Message: {question}",
            "author": message.from_user.username,
            "timestamp": current_date.isoformat()
        }
        save_message_to_vector_db(data)
        print(f"Message saved to the vector db: {question}")
    except Exception as e:
        print(f"Failed to save message: {e}")
        raise

@tb.channel_post_handler(func=lambda message: True)
def echo_all(message):
    global last_message_time
    global thread_id

    current_date = datetime.datetime.now()

    try:
        time_gap = time.time() - last_message_time
        if time_gap <= 5 * 60:
            question = f"[Author: {message.chat.title} at {current_date.isoformat()}] Message: {message.text}"
            chat_id = thread_id
            
            tb.send_chat_action(message.chat.id, 'typing')
            response = generate_response(question, chat_id)
            if len(response) > 0:
                tb.reply_to(message, response)
            last_message_time = time.time()
        elif 'divine' in message.text.lower():
            question = f"[Author: {message.chat.title} at {current_date.isoformat()}] Message: {message.text}"
            chat_id = uuid4()

            tb.send_chat_action(message.chat.id, 'typing')
            response = generate_response(question, chat_id)
            if len(response) > 0:
                tb.reply_to(message, response)
            thread_id = chat_id
            last_message_time = time.time()

    except Exception as e:
        print(f"Failed to respond message: {e}")
        raise

    # Save data
    try:
        data = {
            "content": f"[Author: {message.chat.title} at {current_date.isoformat()}] Message: {message.text}",
            "author": message.chat.title,
            "timestamp": current_date.isoformat()
        }
        save_message_to_vector_db(data)
        print(f"Message saved to the vector db: {data}")
    except Exception as e:
        print(f"Failed to save message: {e}")
        raise

tb.infinity_polling()

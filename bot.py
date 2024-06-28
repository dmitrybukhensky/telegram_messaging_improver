import logging
import sqlite3
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CallbackContext
from openai import OpenAI, OpenAIError, APIConnectionError, APIStatusError, RateLimitError
from utils import load_html_messages, store_messages_in_db

# Your OpenAI API key and Telegram bot token
OPENAI_API_KEY = 'your_openai_api_key'
TELEGRAM_TOKEN = 'your_telegram_token'

client = OpenAI(api_key=OPENAI_API_KEY)
logger = logging.getLogger(__name__)
conn = sqlite3.connect('chat_history.db')

def load_initial_history():
    messages = load_html_messages('your_messages_history_file')
    store_messages_in_db(conn, messages)

def get_history(user_id):
    c = conn.cursor()
    c.execute('SELECT role, content FROM history WHERE user_id = ?', (user_id,))
    return [{'role': row[0], 'content': row[1]} for row in c.fetchall()]

def add_to_history(user_id, role, content):
    c = conn.cursor()
    c.execute('INSERT INTO history (user_id, role, content) VALUES (?, ?, ?)', (user_id, role, content))
    conn.commit()

async def handle_message(update: Update, context: CallbackContext) -> None:
    user_id = update.message.chat_id
    user_message = update.message.text
    history = get_history(user_id)

    if not history:
        load_initial_history()
        history = get_history(user_id)

    history.append({"role": "user", "content": user_message})
    add_to_history(user_id, "user", user_message)

    try:
        response = client.chat.completions.create(model="gpt-3.5-turbo", messages=history)
        bot_response = response.choices[0].message.content.strip()
        add_to_history(user_id, "assistant", bot_response)
        await update.message.reply_text(bot_response)
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("An error occurred while processing your request.")

def main():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()

if __name__ == '__main__':
    main()

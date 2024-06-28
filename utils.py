from bs4 import BeautifulSoup
import sqlite3
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_html_messages(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')

        messages = []
        # Adjusting to new class names based on the structure
        for message in soup.find_all('div', class_='message default clearfix'):
            user = message.find('div', class_='from_name').get_text(strip=True)
            text_element = message.find('div', class_='text')
            if text_element:
                text = text_element.get_text(strip=True)
                role = 'user' if 'your_user' in user else 'assistant'  # Adjust according to how users are distinguished
                messages.append((111111111, role, text))  # Assuming '111111111' is your user_id
        return messages
    except Exception as e:
        logger.error(f"Failed to load HTML messages: {e}")
        return []

def store_messages_in_db(conn, messages):
    try:
        c = conn.cursor()
        c.executemany('INSERT INTO history (user_id, role, content) VALUES (?, ?, ?)', messages)
        conn.commit()
        logger.info(f"{len(messages)} messages stored in the database.")
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")

def load_initial_history():
    conn = sqlite3.connect('chat_history.db')
    messages = load_html_messages('route_to_messages_new.html')
    store_messages_in_db(conn, messages)
    conn.close()

def count_history(user_id):
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM history WHERE user_id = ?', (user_id,))
    count = c.fetchone()[0]
    conn.close()
    logger.info(f"Total messages loaded for user {user_id}: {count}")

if __name__ == '__main__':
    load_initial_history()
    count_history(111111111)  # Replace '111126561' with your user actual user ID

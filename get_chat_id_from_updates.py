"""
Скрипт для получения chat_id целевого бота через getUpdates
Этот метод работает, если целевой бот получал сообщения
"""
import asyncio
import requests
from dotenv import load_dotenv
import os

load_dotenv()

TARGET_BOT_TOKEN = os.getenv('TARGET_BOT_TOKEN', '8388533429:AAHwdPemw4edDjmEHlf5Mhqh7I_2SvzkJO0')
TARGET_BOT_USERNAME = os.getenv('TARGET_BOT_USERNAME', 'smeshnoto4kabot')

def get_chat_id_from_updates():
    """Получает chat_id из обновлений целевого бота"""
    print("=" * 60)
    print("Получение chat_id через getUpdates")
    print("=" * 60)
    print()
    print(f"🔍 Анализирую обновления бота @{TARGET_BOT_USERNAME}...")
    print()
    
    url = f"https://api.telegram.org/bot{TARGET_BOT_TOKEN}/getUpdates"
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if not data.get('ok'):
            print(f"❌ Ошибка API: {data.get('description', 'Неизвестная ошибка')}")
            return None
        
        updates = data.get('result', [])
        
        if not updates:
            print("⚠️  Бот не получал обновлений.")
            print()
            print("💡 Что делать:")
            print("1. Откройте Telegram")
            print(f"2. Найдите бота @{TARGET_BOT_USERNAME}")
            print("3. Отправьте ему команду /start")
            print("4. Запустите этот скрипт снова")
            return None
        
        print(f"✅ Найдено {len(updates)} обновлений\n")
        
        # Ищем chat_id в обновлениях
        chat_ids = set()
        
        for update in updates:
            # Проверяем сообщения
            if 'message' in update:
                chat = update['message'].get('chat', {})
                if 'id' in chat:
                    chat_ids.add((chat['id'], chat.get('type', 'unknown'), chat.get('username', 'N/A')))
            
            # Проверяем edited_message
            if 'edited_message' in update:
                chat = update['edited_message'].get('chat', {})
                if 'id' in chat:
                    chat_ids.add((chat['id'], chat.get('type', 'unknown'), chat.get('username', 'N/A')))
            
            # Проверяем channel_post
            if 'channel_post' in update:
                chat = update['channel_post'].get('chat', {})
                if 'id' in chat:
                    chat_ids.add((chat['id'], chat.get('type', 'unknown'), chat.get('title', 'N/A')))
        
        if chat_ids:
            print("📋 Найденные chat_id:\n")
            for chat_id, chat_type, name in sorted(chat_ids):
                print(f"  Chat ID: {chat_id}")
                print(f"  Тип: {chat_type}")
                print(f"  Имя: {name}")
                print()
            
            # Пытаемся найти chat_id целевого бота
            username = TARGET_BOT_USERNAME.lstrip('@')
            target_chat_id = None
            
            for chat_id, chat_type, name in chat_ids:
                if username.lower() in str(name).lower() or chat_type == 'private':
                    target_chat_id = chat_id
                    break
            
            if target_chat_id:
                print(f"✅ Вероятный chat_id целевого бота: {target_chat_id}")
                print()
                print("📝 Добавьте в переменные окружения:")
                print(f"TARGET_BOT_CHAT_ID={target_chat_id}")
                return target_chat_id
            else:
                print("⚠️  Не удалось определить chat_id целевого бота автоматически.")
                print("   Используйте один из найденных chat_id выше.")
                if len(chat_ids) == 1:
                    chat_id = list(chat_ids)[0][0]
                    print(f"\n💡 Попробуйте этот chat_id: {chat_id}")
                    print(f"TARGET_BOT_CHAT_ID={chat_id}")
                    return chat_id
        else:
            print("❌ Не найдено chat_id в обновлениях")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка при запросе: {str(e)}")
        return None
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {str(e)}")
        return None

if __name__ == "__main__":
    chat_id = get_chat_id_from_updates()
    
    if chat_id:
        print(f"\n✅ Успешно! Chat ID: {chat_id}")
    else:
        print(f"\n⚠️  Не удалось получить chat_id автоматически")
        print(f"\n📖 Смотрите инструкцию в файле get_chat_id_manual.md")

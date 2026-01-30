"""
Скрипт для инициализации диалога между ботами и получения chat_id целевого бота
"""
import asyncio
from aiogram import Bot
from dotenv import load_dotenv
import os

load_dotenv()

# Токены
BOT_TOKEN = os.getenv('BOT_TOKEN', '8352200865:AAHOl8DnhJA3tyfMADcHZzmhNwa9h5tArMc')
TARGET_BOT_TOKEN = os.getenv('TARGET_BOT_TOKEN', '8388533429:AAHwdPemw4edDjmEHlf5Mhqh7I_2SvzkJO0')
TARGET_BOT_USERNAME = os.getenv('TARGET_BOT_USERNAME', 'smeshnoto4kabot')

async def init_bot_chat():
    """Инициализирует диалог между ботами и получает chat_id"""
    print("🤖 Инициализация диалога между ботами...\n")
    
    # Создаем экземпляры ботов
    your_bot = Bot(token=BOT_TOKEN)
    target_bot = Bot(token=TARGET_BOT_TOKEN)
    
    try:
        # Получаем информацию о вашем боте
        your_bot_info = await your_bot.get_me()
        print(f"✅ Ваш бот: @{your_bot_info.username} (ID: {your_bot_info.id})")
        
        # Получаем информацию о целевом боте
        target_bot_info = await target_bot.get_me()
        print(f"✅ Целевой бот: @{target_bot_info.username} (ID: {target_bot_info.id})")
        
        # Пробуем получить chat_id целевого бота
        username = TARGET_BOT_USERNAME.lstrip('@')
        print(f"\n🔍 Пытаемся получить chat_id для @{username}...")
        
        try:
            # Метод 1: Пробуем получить через getChat
            chat = await your_bot.get_chat(f"@{username}")
            print(f"✅ Chat ID получен через getChat: {chat.id}")
            print(f"\n📝 Добавьте в переменные окружения:")
            print(f"TARGET_BOT_CHAT_ID={chat.id}")
            return chat.id
        except Exception as e1:
            print(f"❌ Не удалось получить через getChat: {str(e1)}")
            
            # Метод 2: Пробуем отправить сообщение от вашего бота целевому
            print(f"\n🔍 Пытаемся отправить сообщение от вашего бота целевому...")
            try:
                # Пробуем отправить сообщение
                sent_message = await your_bot.send_message(
                    chat_id=f"@{username}",
                    text="/start"
                )
                print(f"✅ Сообщение отправлено! Chat ID: {sent_message.chat.id}")
                print(f"\n📝 Добавьте в переменные окружения:")
                print(f"TARGET_BOT_CHAT_ID={sent_message.chat.id}")
                return sent_message.chat.id
            except Exception as e2:
                print(f"❌ Не удалось отправить сообщение: {str(e2)}")
                
                # Метод 3: Пробуем отправить от целевого бота вашему
                print(f"\n🔍 Пытаемся отправить сообщение от целевого бота вашему...")
                try:
                    your_bot_username = your_bot_info.username
                    sent_message = await target_bot.send_message(
                        chat_id=f"@{your_bot_username}",
                        text="/start"
                    )
                    print(f"✅ Сообщение отправлено! Chat ID вашего бота: {sent_message.chat.id}")
                    print(f"\n💡 Теперь попробуйте отправить сообщение от вашего бота целевому:")
                    print(f"   Используйте команду /get_chat_id в вашем боте")
                    return None
                except Exception as e3:
                    print(f"❌ Не удалось отправить сообщение: {str(e3)}")
                    print(f"\n❌ Все методы не сработали.")
                    print(f"\n💡 Альтернативные способы:")
                    print(f"1. Попросите администратора целевого бота добавить ваш бот в диалог")
                    print(f"2. Используйте команду /get_chat_id в вашем боте после того, как")
                    print(f"   кто-то отправит /start целевому боту от вашего имени")
                    print(f"3. Если целевой бот находится в группе/канале, используйте chat_id группы/канала")
                    return None
        
    except Exception as e:
        print(f"❌ Общая ошибка: {str(e)}")
        return None
    
    finally:
        await your_bot.session.close()
        await target_bot.session.close()

if __name__ == "__main__":
    print("=" * 60)
    print("Инициализация диалога между ботами")
    print("=" * 60)
    print()
    
    chat_id = asyncio.run(init_bot_chat())
    
    if chat_id:
        print(f"\n✅ Успешно! Chat ID: {chat_id}")
    else:
        print(f"\n⚠️  Не удалось автоматически получить chat_id")
        print(f"   Используйте команду /get_chat_id в вашем боте")

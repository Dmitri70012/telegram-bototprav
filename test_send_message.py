"""
Скрипт для тестирования отправки сообщения целевому боту
"""
import asyncio
from aiogram import Bot
from dotenv import load_dotenv
import os

load_dotenv()

TARGET_BOT_TOKEN = os.getenv('TARGET_BOT_TOKEN', '8388533429:AAHwdPemw4edDjmEHlf5Mhqh7I_2SvzkJO0')
TARGET_BOT_USERNAME = os.getenv('TARGET_BOT_USERNAME', 'smeshnoto4kabot')

# ID бота из JSON
BOT_ID_FROM_JSON = 8388533429

async def test_send_message():
    """Тестирует отправку сообщения разными способами"""
    print("=" * 60)
    print("Тестирование отправки сообщения целевому боту")
    print("=" * 60)
    print()
    
    target_bot = Bot(token=TARGET_BOT_TOKEN)
    test_message = "Тестовое сообщение для проверки отправки"
    
    # Список вариантов chat_id для проверки
    test_variants = [
        ("Bot ID из JSON", BOT_ID_FROM_JSON),
        ("Username с @", f"@{TARGET_BOT_USERNAME.lstrip('@')}"),
        ("Username без @", TARGET_BOT_USERNAME.lstrip('@')),
    ]
    
    print(f"Целевой бот: @{TARGET_BOT_USERNAME.lstrip('@')}")
    print(f"Bot ID из JSON: {BOT_ID_FROM_JSON}")
    print()
    
    success = False
    
    for name, chat_id in test_variants:
        print(f"🔍 Пробую отправить через: {name} ({chat_id})...")
        try:
            sent = await target_bot.send_message(
                chat_id=chat_id,
                text=test_message
            )
            print(f"✅ УСПЕХ! Сообщение отправлено!")
            print(f"   Chat ID: {sent.chat.id}")
            print(f"   Message ID: {sent.message_id}")
            print()
            print(f"📝 Используйте этот chat_id: {sent.chat.id}")
            print(f"   Добавьте в .env: TARGET_BOT_CHAT_ID={sent.chat.id}")
            success = True
            break
        except Exception as e:
            print(f"❌ Не сработало: {str(e)}")
            print()
    
    if not success:
        print("⚠️  Ни один из способов не сработал.")
        print()
        print("💡 Возможные причины:")
        print("1. Бот не может отправлять сообщения самому себе")
        print("2. Нужен chat_id диалога, а не bot_id")
        print("3. Целевой бот должен начать диалог с вашим ботом")
        print()
        print("📖 Попробуйте:")
        print("1. Отправить /start целевому боту от вашего личного аккаунта")
        print("2. Затем использовать команду /get_chat_id в вашем боте")
        print("3. Или использовать скрипт get_chat_id_from_updates.py")
    
    await target_bot.session.close()

if __name__ == "__main__":
    asyncio.run(test_send_message())

import asyncio
import os
from datetime import datetime, time
from typing import Dict
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Токены и настройки
BOT_TOKEN = os.getenv('BOT_TOKEN', '8352200865:AAHOl8DnhJA3tyfMADcHZzmhNwa9h5tArMc')
TARGET_BOT_TOKEN = os.getenv('TARGET_BOT_TOKEN', '8388533429:AAHwdPemw4edDjmEHlf5Mhqh7I_2SvzkJO0')
TARGET_BOT_USERNAME = os.getenv('TARGET_BOT_USERNAME', 'smeshnoto4kabot')

# Инициализация ботов
bot = Bot(token=BOT_TOKEN)
target_bot = Bot(token=TARGET_BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Хранилище для ссылок и времени отправки
scheduled_messages: Dict[int, Dict] = {}


class LinkSchedule(StatesGroup):
    waiting_for_time = State()


def is_valid_url(text: str) -> bool:
    """Проверяет, является ли текст ссылкой"""
    return text.startswith(('http://', 'https://', 'www.'))


def parse_time(time_str: str) -> time:
    """Парсит время в формате HH:MM"""
    try:
        hour, minute = map(int, time_str.split(':'))
        if 0 <= hour < 24 and 0 <= minute < 60:
            return time(hour, minute)
        else:
            raise ValueError("Время вне допустимого диапазона")
    except (ValueError, AttributeError):
        raise ValueError("Неверный формат времени")


async def send_scheduled_message(link: str, user_id: int):
    """Отправляет ссылку в целевой бот"""
    try:
        # Убираем @ если он есть в username
        chat_id = TARGET_BOT_USERNAME.lstrip('@')
        await target_bot.send_message(
            chat_id=chat_id,
            text=link
        )
        await bot.send_message(
            chat_id=user_id,
            text=f"✅ Ссылка успешно отправлена в {TARGET_BOT_USERNAME} в {datetime.now().strftime('%H:%M')}"
        )
    except Exception as e:
        await bot.send_message(
            chat_id=user_id,
            text=f"❌ Ошибка при отправке ссылки: {str(e)}"
        )


async def schedule_checker():
    """Проверяет и отправляет запланированные сообщения"""
    while True:
        now = datetime.now().time()
        current_time = time(now.hour, now.minute)
        
        # Проверяем все запланированные сообщения
        messages_to_send = []
        for msg_id, data in list(scheduled_messages.items()):
            if data['time'] == current_time:
                messages_to_send.append((msg_id, data))
        
        # Отправляем сообщения
        for msg_id, data in messages_to_send:
            await send_scheduled_message(data['link'], data['user_id'])
            del scheduled_messages[msg_id]
        
        # Ждем 1 секунду перед следующей проверкой
        await asyncio.sleep(1)


@dp.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    await message.answer(
        "👋 Привет! Я бот для планирования отправки ссылок.\n\n"
        "📝 Просто отправь мне ссылку, и я спрошу, в какое время её нужно отправить.\n"
        "⏰ Формат времени: HH:MM (например, 15:05)"
    )


@dp.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help"""
    await message.answer(
        "📖 Инструкция по использованию:\n\n"
        "1. Отправь мне ссылку (http:// или https://)\n"
        "2. Укажи время отправки в формате HH:MM (например, 15:05)\n"
        "3. Бот автоматически отправит ссылку в указанное время\n\n"
        "Команды:\n"
        "/start - Начать работу\n"
        "/help - Показать эту справку\n"
        "/list - Показать запланированные отправки"
    )


@dp.message(Command("list"))
async def cmd_list(message: Message):
    """Показывает список запланированных отправок"""
    user_scheduled = [
        (msg_id, data) for msg_id, data in scheduled_messages.items()
        if data['user_id'] == message.from_user.id
    ]
    
    if not user_scheduled:
        await message.answer("📋 У вас нет запланированных отправок.")
        return
    
    text = "📋 Ваши запланированные отправки:\n\n"
    for msg_id, data in user_scheduled:
        text += f"🔗 {data['link'][:50]}...\n"
        text += f"⏰ Время: {data['time'].strftime('%H:%M')}\n\n"
    
    await message.answer(text)


@dp.message(LinkSchedule.waiting_for_time)
async def process_time(message: Message, state: FSMContext):
    """Обработчик ввода времени"""
    try:
        send_time = parse_time(message.text)
        data = await state.get_data()
        link = data.get('link')
        
        if not link:
            await message.answer("❌ Ошибка: ссылка не найдена. Попробуйте снова.")
            await state.clear()
            return
        
        # Вычисляем время отправки на сегодня или завтра
        now = datetime.now()
        send_datetime = datetime.combine(now.date(), send_time)
        
        # Если время уже прошло сегодня, планируем на завтра
        if send_datetime <= now:
            from datetime import timedelta
            send_datetime = datetime.combine((now + timedelta(days=1)).date(), send_time)
        
        # Сохраняем в расписание
        msg_id = len(scheduled_messages) + 1
        scheduled_messages[msg_id] = {
            'link': link,
            'time': send_time,
            'user_id': message.from_user.id,
            'datetime': send_datetime
        }
        
        await message.answer(
            f"✅ Ссылка запланирована на отправку в {send_time.strftime('%H:%M')}\n\n"
            f"🔗 Ссылка: {link}"
        )
        await state.clear()
        
    except ValueError as e:
        await message.answer(
            f"❌ Неверный формат времени. Используйте формат HH:MM (например, 15:05)\n"
            f"Ошибка: {str(e)}"
        )


@dp.message()
async def process_link(message: Message, state: FSMContext):
    """Обработчик ссылок"""
    text = message.text.strip()
    
    if is_valid_url(text):
        # Сохраняем ссылку и запрашиваем время
        await state.update_data(link=text)
        await state.set_state(LinkSchedule.waiting_for_time)
        await message.answer(
            f"🔗 Ссылка получена: {text}\n\n"
            "⏰ Укажите время отправки в формате HH:MM (например, 15:05):"
        )
    else:
        await message.answer(
            "❌ Это не похоже на ссылку. Пожалуйста, отправьте ссылку, начинающуюся с http://, https:// или www."
        )


async def main():
    """Главная функция"""
    # Запускаем проверку расписания в фоне
    asyncio.create_task(schedule_checker())
    
    # Запускаем бота
    print("🤖 Бот запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

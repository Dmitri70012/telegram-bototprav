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
TARGET_BOT_CHAT_ID = os.getenv('TARGET_BOT_CHAT_ID', None)  # Chat ID целевого бота (если известен)

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
    print(f"\n{'='*60}")
    print(f"🔄 Попытка отправить ссылку: {link[:50]}...")
    print(f"⏰ Время: {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*60}")
    
    try:
        username = TARGET_BOT_USERNAME.lstrip('@')
        chat_id_to_use = None
        
        print(f"📋 Параметры:")
        print(f"   Целевой бот: @{username}")
        print(f"   TARGET_BOT_CHAT_ID из env: {TARGET_BOT_CHAT_ID}")
        
        # Приоритет 1: Используем chat_id из переменной окружения, если он указан
        if TARGET_BOT_CHAT_ID:
            try:
                chat_id_to_use = int(TARGET_BOT_CHAT_ID)
                print(f"✅ Используется chat_id из переменной окружения: {chat_id_to_use}")
            except ValueError:
                print(f"⚠️  TARGET_BOT_CHAT_ID не является числом: {TARGET_BOT_CHAT_ID}")
        
        # Приоритет 1.5: Пробуем использовать bot_id из токена (если chat_id не указан)
        if chat_id_to_use is None:
            try:
                bot_id_from_token = int(TARGET_BOT_TOKEN.split(':')[0])
                chat_id_to_use = bot_id_from_token
                print(f"⚠️  Используется bot_id из токена как chat_id: {chat_id_to_use}")
            except Exception as e:
                print(f"❌ Не удалось извлечь bot_id из токена: {str(e)}")
        
        # Приоритет 2: Пробуем получить chat_id через getChat (используя ВАШ бот)
        if chat_id_to_use is None:
            print(f"🔍 Пробую получить chat_id через getChat...")
            try:
                chat = await bot.get_chat(f"@{username}")
                chat_id_to_use = chat.id
                print(f"✅ Получен chat_id через getChat: {chat_id_to_use}")
            except Exception as e:
                print(f"❌ Не удалось получить chat_id через getChat: {type(e).__name__}: {str(e)}")
        
        # Приоритет 3: Пробуем отправить по username (используя ВАШ бот)
        if chat_id_to_use is None:
            print(f"🔍 Пробую отправить по username...")
            for chat_id_variant in [f"@{username}", username]:
                try:
                    print(f"   Пробую: {chat_id_variant}")
                    sent_message = await bot.send_message(
                        chat_id=chat_id_variant,
                        text=link
                    )
                    print(f"✅ Сообщение отправлено по username: {chat_id_variant}")
                    print(f"   Chat ID ответа: {sent_message.chat.id}")
                    await bot.send_message(
                        chat_id=user_id,
                        text=f"✅ Ссылка успешно отправлена в @{username} в {datetime.now().strftime('%H:%M:%S')}"
                    )
                    return
                except Exception as e:
                    print(f"❌ Ошибка отправки по {chat_id_variant}: {type(e).__name__}: {str(e)}")
                    continue
        
        # Если есть chat_id, используем его (используя ВАШ бот)
        if chat_id_to_use:
            print(f"📤 Отправка сообщения в chat_id: {chat_id_to_use}")
            try:
                sent_message = await bot.send_message(
                    chat_id=chat_id_to_use,
                    text=link
                )
                print(f"✅ Сообщение успешно отправлено!")
                print(f"   Message ID: {sent_message.message_id}")
                print(f"   Chat ID: {sent_message.chat.id}")
                await bot.send_message(
                    chat_id=user_id,
                    text=f"✅ Ссылка успешно отправлена в @{username} в {datetime.now().strftime('%H:%M:%S')}"
                )
                return
            except Exception as send_error:
                error_type = type(send_error).__name__
                error_details = str(send_error)
                print(f"❌ Ошибка отправки в chat_id {chat_id_to_use}:")
                print(f"   Тип: {error_type}")
                print(f"   Сообщение: {error_details}")
                
                # Пробуем альтернативный способ - через username еще раз
                try:
                    print(f"🔄 Пробую альтернативный способ через username...")
                    sent_message = await bot.send_message(
                        chat_id=f"@{username}",
                        text=link
                    )
                    print(f"✅ Сообщение отправлено через username после ошибки")
                    await bot.send_message(
                        chat_id=user_id,
                        text=f"✅ Ссылка успешно отправлена в @{username} в {datetime.now().strftime('%H:%M:%S')}"
                    )
                    return
                except Exception as e2:
                    print(f"❌ Альтернативный способ тоже не сработал: {type(e2).__name__}: {str(e2)}")
                    raise Exception(f"Не удалось отправить сообщение. Ошибки: {error_type}: {error_details}, {type(e2).__name__}: {str(e2)}")
        else:
            raise Exception("Не удалось определить chat_id целевого бота. Используйте команду /get_chat_id для получения chat_id.")
            
    except Exception as e:
        error_msg = str(e)
        error_type = type(e).__name__
        print(f"❌ КРИТИЧЕСКАЯ ОШИБКА отправки: {error_type}: {error_msg}")
        
        # Детальная информация об ошибке
        detailed_error = f"❌ Ошибка при отправке ссылки:\n\n"
        detailed_error += f"Тип: {error_type}\n"
        detailed_error += f"Сообщение: {error_msg}\n\n"
        detailed_error += f"💡 Возможные решения:\n"
        detailed_error += f"1. Используйте команду /get_chat_id\n"
        detailed_error += f"2. Убедитесь, что целевой бот @{TARGET_BOT_USERNAME.lstrip('@')} запущен\n"
        detailed_error += f"3. Проверьте, что TARGET_BOT_CHAT_ID указан в переменных окружения\n"
        detailed_error += f"4. В Telegram боты не могут отправлять сообщения друг другу напрямую.\n"
        detailed_error += f"   Возможно, нужно отправлять в группу/канал, где находится целевой бот"
        
        try:
            await bot.send_message(
                chat_id=user_id,
                text=detailed_error
            )
        except:
            print(f"Не удалось отправить сообщение об ошибке пользователю")


async def schedule_checker():
    """Проверяет и отправляет запланированные сообщения"""
    while True:
        try:
            now = datetime.now()
            current_time = time(now.hour, now.minute)
            
            # Проверяем все запланированные сообщения
            messages_to_send = []
            for msg_id, data in list(scheduled_messages.items()):
                scheduled_time = data['time']
                # Проверяем точное совпадение времени (час и минута)
                if scheduled_time.hour == current_time.hour and scheduled_time.minute == current_time.minute:
                    # Проверяем, что сообщение еще не отправлено (в пределах текущей минуты)
                    if 'sent' not in data or not data.get('sent', False):
                        messages_to_send.append((msg_id, data))
                        data['sent'] = True  # Помечаем как отправленное
            
            # Отправляем сообщения
            for msg_id, data in messages_to_send:
                try:
                    print(f"\n⏰ Время отправки наступило: {current_time.strftime('%H:%M')}")
                    print(f"📨 Отправляю сообщение ID {msg_id}")
                    await send_scheduled_message(data['link'], data['user_id'])
                    del scheduled_messages[msg_id]
                    print(f"✅ Успешно удалено из расписания: {msg_id}")
                except Exception as e:
                    error_type = type(e).__name__
                    print(f"❌ ОШИБКА при отправке сообщения {msg_id}:")
                    print(f"   Тип: {error_type}")
                    print(f"   Сообщение: {str(e)}")
                    # Не удаляем сообщение при ошибке, чтобы можно было повторить попытку
                    # Но помечаем, что была попытка отправки
                    data['last_error'] = str(e)
                    data['error_count'] = data.get('error_count', 0) + 1
            
            # Ждем 1 секунду перед следующей проверкой
            await asyncio.sleep(1)
        except Exception as e:
            print(f"Ошибка в schedule_checker: {str(e)}")
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


@dp.message(Command("test_send"))
async def cmd_test_send(message: Message):
    """Тестирует отправку сообщения целевому боту"""
    test_link = "https://test.example.com"
    await message.answer("🧪 Тестирую отправку сообщения...")
    try:
        await send_scheduled_message(test_link, message.from_user.id)
    except Exception as e:
        await message.answer(f"❌ Тест не прошел: {str(e)}\n\nПроверьте логи на Railway для деталей.")


@dp.message(Command("get_chat_id"))
async def cmd_get_chat_id(message: Message):
    """Получает chat_id целевого бота"""
    try:
        username = TARGET_BOT_USERNAME.lstrip('@')
        
        # Пробуем получить через getChat
        try:
            chat = await target_bot.get_chat(f"@{username}")
            await message.answer(
                f"📱 Chat ID целевого бота @{username}:\n\n"
                f"`{chat.id}`\n\n"
                f"💡 Добавьте это значение в переменную окружения TARGET_BOT_CHAT_ID для более надежной работы.",
                parse_mode="Markdown"
            )
            return
        except Exception as e1:
            pass
        
        # Пробуем получить через getUpdates
        try:
            import requests
            url = f"https://api.telegram.org/bot{TARGET_BOT_TOKEN}/getUpdates"
            response = requests.get(url, timeout=5)
            data = response.json()
            
            if data.get('ok') and data.get('result'):
                updates = data['result']
                chat_ids = set()
                
                for update in updates:
                    if 'message' in update:
                        chat = update['message'].get('chat', {})
                        if 'id' in chat:
                            chat_ids.add(chat['id'])
                
                if chat_ids:
                    chat_id = list(chat_ids)[0]
                    await message.answer(
                        f"📱 Chat ID найден через getUpdates:\n\n"
                        f"`{chat_id}`\n\n"
                        f"💡 Добавьте это значение в переменную окружения TARGET_BOT_CHAT_ID.",
                        parse_mode="Markdown"
                    )
                    return
        except Exception as e2:
            pass
        
        # Если ничего не получилось
        await message.answer(
            f"❌ Не удалось автоматически получить chat_id.\n\n"
            f"📖 Инструкция:\n\n"
            f"1. Откройте Telegram\n"
            f"2. Найдите бота @{username}\n"
            f"3. Отправьте ему команду /start\n"
            f"4. Запустите скрипт: python get_chat_id_from_updates.py\n"
            f"5. Или используйте бота @RawDataBot для получения chat_id\n\n"
            f"📄 Подробная инструкция в файле: КАК_ПОЛУЧИТЬ_CHAT_ID.txt"
        )
    except Exception as e:
        await message.answer(
            f"❌ Ошибка: {str(e)}\n\n"
            f"📖 Смотрите инструкцию в файле КАК_ПОЛУЧИТЬ_CHAT_ID.txt"
        )


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
    
    # Запускаем бота с обработкой ошибок
    print("🤖 Бот запущен...")
    try:
        # Очищаем предыдущие обновления перед запуском
        try:
            await bot.delete_webhook(drop_pending_updates=True)
            print("✅ Предыдущие обновления очищены")
        except Exception as e:
            print(f"⚠️  Не удалось очистить обновления: {str(e)}")
        
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as e:
        print(f"❌ Критическая ошибка: {str(e)}")
        print("💡 Убедитесь, что бот не запущен в другом месте")
        raise


if __name__ == "__main__":
    asyncio.run(main())

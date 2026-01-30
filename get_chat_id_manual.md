# Как получить Chat ID целевого бота вручную

Если автоматические методы не работают, используйте один из этих способов:

## Способ 1: Через специальных ботов

1. Найдите в Telegram бота **@userinfobot** или **@getidsbot**
2. Добавьте целевой бот `@smeshnoto4kabot` в группу
3. Добавьте бота `@userinfobot` в ту же группу
4. Отправьте любое сообщение в группу
5. Бот покажет информацию о всех участниках, включая chat_id

## Способ 2: Через ваш личный аккаунт

1. Откройте Telegram на вашем телефоне/компьютере
2. Найдите целевой бот `@smeshnoto4kabot`
3. Отправьте ему команду `/start`
4. Затем используйте бота **@RawDataBot**:
   - Найдите `@RawDataBot` в Telegram
   - Отправьте ему `/start`
   - Перешлите любое сообщение от `@smeshnoto4kabot` боту `@RawDataBot`
   - Бот покажет всю информацию, включая chat_id

## Способ 3: Через API напрямую

Если у вас есть доступ к токену целевого бота, можно использовать этот скрипт:

```python
import requests

TARGET_BOT_TOKEN = "8388533429:AAHwdPemw4edDjmEHlf5Mhqh7I_2SvzkJO0"

# Получаем информацию о боте
response = requests.get(f"https://api.telegram.org/bot{TARGET_BOT_TOKEN}/getMe")
print(response.json())

# Получаем обновления (если бот получал сообщения)
response = requests.get(f"https://api.telegram.org/bot{TARGET_BOT_TOKEN}/getUpdates")
updates = response.json()
if updates.get('result'):
    for update in updates['result']:
        if 'message' in update:
            chat = update['message']['chat']
            print(f"Chat ID: {chat['id']}, Type: {chat['type']}")
```

## Способ 4: Если целевой бот в группе/канале

Если `@smeshnoto4kabot` находится в группе или канале:
1. Добавьте вашего бота в эту группу/канал
2. Используйте chat_id группы/канала (обычно отрицательное число)
3. Получить его можно через `@userinfobot` в группе

## Важно!

Chat ID бота обычно выглядит как большое число (например, `123456789`).
Для групп chat_id отрицательный (например, `-1001234567890`).

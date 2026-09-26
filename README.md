# Лабораторна робота №3 — Telegram-бот з AI

Telegram-бот з меню, інформацією про студента та інтеграцією з Gemini API.

## Можливості

- інформація про студента Серкелі Артура, група ІП-32;
- перелік використаних IT-технологій;
- контактні дані;
- надсилання текстового prompt до Gemini AI;
- локальний запуск через long polling;
- робота на хостингу через захищений webhook.
- доступ лише для дозволених Telegram-користувачів.

## Технології

- Python 3.12;
- aiogram 3;
- Telegram Bot API;
- Google Gemini API та `google-genai`;
- aiohttp;
- Render або Koyeb.

## Локальний запуск

1. Створіть бота через [@BotFather](https://t.me/BotFather) і отримайте токен.
2. Створіть Gemini API key у [Google AI Studio](https://aistudio.google.com/apikey).
3. Створіть та активуйте віртуальне середовище:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

4. Встановіть залежності:

   ```powershell
   pip install -r requirements.txt
   ```

5. Скопіюйте `.env.example` у `.env` та вкажіть ключі:

   ```env
   TELEGRAM_BOT_TOKEN=ваш_telegram_token
   GEMINI_API_KEY=ваш_gemini_key
   RUN_MODE=polling
   ```

6. Запустіть бота:

   ```powershell
   python -m app.bot
   ```

Під час локального запуску одночасно не повинна працювати задеплоєна копія бота.

## Перевірка тестів

```powershell
pip install -r requirements-dev.txt
pytest
```

## Деплой на Render

1. Завантажте проєкт у GitHub-репозиторій.
2. У Render виберіть **New → Blueprint** та підключіть репозиторій.
3. Render прочитає `render.yaml` і створить Web Service.
4. Додайте секретні змінні:

   - `TELEGRAM_BOT_TOKEN` — токен від BotFather;
   - `GEMINI_API_KEY` — ключ Google AI Studio;
   - `ALLOWED_USER_IDS` — дозволені числові Telegram ID через кому;
   - `WEBHOOK_SECRET` — довільний секрет лише з латинських літер, цифр,
     `_` і `-`, наприклад `lab3_webhook_secret_2026`.

5. Після збереження змін виконайте redeploy.
6. Відкрийте `/health` на адресі сервісу. Відповідь має бути:

   ```json
   {"status": "ok"}
   ```

Webhook реєструється автоматично під час запуску застосунку. Сервер перевіряє
`WEBHOOK_SECRET` у кожному запиті Telegram. Не використовуйте в ньому пробіли,
крапки, `+`, `/` або `=` — Telegram такі символи не приймає.
Адресу webhook застосунок автоматично отримує зі стандартної змінної Render
`RENDER_EXTERNAL_URL`; вводити `WEBHOOK_BASE_URL` на Render не потрібно.

## Змінні середовища

| Змінна | Призначення |
|---|---|
| `TELEGRAM_BOT_TOKEN` | токен Telegram-бота |
| `GEMINI_API_KEY` | ключ Gemini API |
| `GEMINI_MODEL` | модель Gemini |
| `ALLOWED_USER_IDS` | Telegram ID користувачів, яким дозволено доступ |
| `RUN_MODE` | `polling` локально або `webhook` на сервері |
| `WEBHOOK_BASE_URL` | HTTPS-адреса задеплоєного сервісу |
| `WEBHOOK_PATH` | шлях webhook |
| `WEBHOOK_SECRET` | секрет перевірки запитів Telegram |
| `PORT` | порт HTTP-сервера |

Секрети не можна додавати до Git. Файл `.env` уже внесений до `.gitignore`.

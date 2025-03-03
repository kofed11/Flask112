import logging
import openai
import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import FSInputFile

# Установи свои API-ключи
TELEGRAM_BOT_TOKEN = "7153775434:AAHst-m5O8kHtKzjFMM6u2VfMOD-hM5vX_o"
OPENAI_API_KEY = "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"
openai.api_key = OPENAI_API_KEY

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Создаем бота и диспетчер
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

# История сообщений для контекста
user_contexts = {}

# Системное сообщение для контекста Python и веб-разработки
SYSTEM_MESSAGE = {
    "role": "system",
    "content": (
        "Ты — эксперт по разработке на Python, HTML, CSS и JavaScript. "
        "Проанализируй код, найди ошибки, предложи улучшения и исправь код, "
        "чтобы он соответствовал лучшим практикам."
    )
}

# Лимит хранимых сообщений
HISTORY_LIMIT = 100

# Папка для сохранения загруженных и исправленных файлов
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Разрешённые расширения файлов
ALLOWED_EXTENSIONS = {".py", ".html", ".css", ".js"}

# Функция проверки расширения файла
def is_valid_extension(file_name):
    return any(file_name.endswith(ext) for ext in ALLOWED_EXTENSIONS)

# Обработчик текстовых сообщений
@dp.message()
async def chatgpt_response(message: types.Message):
    user_id = message.from_user.id

    # Если у пользователя нет истории, создаем её
    if user_id not in user_contexts:
        user_contexts[user_id] = [SYSTEM_MESSAGE]

    # Добавляем сообщение пользователя в историю
    user_contexts[user_id].append({"role": "user", "content": message.text})

    try:
        # Отправляем запрос в OpenAI
        client = openai.OpenAI(api_key=OPENAI_API_KEY)

        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=user_contexts[user_id]
        )
        reply_text = response["choices"][0]["message"]["content"]

        # Добавляем ответ бота в историю
        user_contexts[user_id].append({"role": "assistant", "content": reply_text})

        # Ограничиваем историю сообщений
        if len(user_contexts[user_id]) > HISTORY_LIMIT:
            user_contexts[user_id] = [SYSTEM_MESSAGE] + user_contexts[user_id][-HISTORY_LIMIT:]

    except Exception as e:
        logging.error(f"Ошибка OpenAI: {e}")
        reply_text = "Ошибка при запросе к ChatGPT."

    # Отправляем ответ
    await message.answer(reply_text)

# Обработчик загруженных файлов
@dp.message(lambda message: message.document)
async def handle_document(message: types.Message):
    document = message.document

    # Проверяем разрешённый формат
    if not is_valid_extension(document.file_name):
        await message.answer("Пожалуйста, загружайте файлы с кодом Python (.py), HTML (.html), CSS (.css) или JavaScript (.js).")
        return

    # Ограничение на размер файла (до 50MB)
    if document.file_size > 50 * 1024 * 1024:
        await message.answer("Файл слишком большой! Максимальный размер — 50MB.")
        return

    # Скачиваем файл
    file_path = os.path.join(UPLOAD_DIR, document.file_name)
    await bot.download(document, file_path)

    # Читаем содержимое файла
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            code_content = file.read()

        # Определяем язык кода
        if document.file_name.endswith(".py"):
            language = "Python"
        elif document.file_name.endswith(".html"):
            language = "HTML"
        elif document.file_name.endswith(".css"):
            language = "CSS"
        elif document.file_name.endswith(".js"):
            language = "JavaScript"
        else:
            language = "неизвестный язык"

        # Отправляем код в ChatGPT для анализа и исправления
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                SYSTEM_MESSAGE, {"role": "user", "content": f"Проанализируй этот код ({language}), исправь ошибки и оптимизируй:\n\n{code_content}"}
            ]
        )
        fixed_code = response["choices"][0]["message"]["content"]

        # Сохраняем исправленный код
        fixed_file_path = os.path.join(UPLOAD_DIR, f"fixed_{document.file_name}")
        with open(fixed_file_path, "w", encoding="utf-8") as file:
            file.write(fixed_code)

    except Exception as e:
        logging.error(f"Ошибка обработки файла: {e}")
        await message.answer("Ошибка при обработке файла. Убедитесь, что это корректный код.")
        return

    # Отправляем результат анализа и исправленный файл
    await message.answer(f"📄 Исправленный код ({language}) в {document.file_name} готов! 🔧")
    await message.answer_document(FSInputFile(fixed_file_path))

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

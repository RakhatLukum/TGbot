import json
import requests
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
import os
from dotenv import load_dotenv
load_dotenv()

API_TOKEN = os.getenv("API_TOKEN") 
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Loading knowledge
with open("knowledge.json", "r", encoding="utf-8") as f:
    knowledge = json.load(f)

bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

def ask_mistral(user_input: str) -> str:
    # Context
    context = "\n".join([f"Q: {item['question']}\nA: {item['answer']}" for item in knowledge])      
    
    # Final prompt
    prompt = f"""Ты — AI-ассистент для студентов по прохождению производственной практики, который должен строго отвечать, используя только знания из базы ниже.
Если ты не знаешь ответа — просто скажи, что не можешь ответить.

База знаний:
{context}

Вопрос пользователя:
{user_input}
Ответ:"""

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "mistralai/mistral-7b-instruct:free",
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload)
    
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"].strip()
    else:
        return f"Ошибка от OpenRouter: {response.text}"


@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Привет! Задай вопрос по теме, и я постараюсь ответить!")

@dp.message()
async def handle_question(message: Message):
    user_input = message.text
    await message.answer("Думаю над ответом...")
    answer = ask_mistral(user_input)
    await message.answer(answer)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

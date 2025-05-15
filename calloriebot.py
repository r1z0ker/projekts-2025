import logging
import asyncio
import json
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import CommandStart, Command

API_TOKEN = '7626822244:AAE09A1kjkUOJ4ZYUtaz_LYkr51X0GjbNkI'

FOOD_DATA_FILE = "food_data.json"

# === Работа с JSON ===
def load_food_data():
    try:
        with open(FOOD_DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}

def save_food_data(data):
    with open(FOOD_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# === Логика расчёта ===
def get_product_data(product_name: str, weight: float):
    if weight <= 0:
        return None
    data = food_data.get(product_name.lower())
    if data is None:
        return None
    kkal, protein, fat, carbs = data
    w = weight / 100
    return {
        "calories": round(kkal * w, 1),
        "proteins": round(protein * w, 1),
        "fats": round(fat * w, 1),
        "carbs": round(carbs * w, 1)
    }

# === Инициализация ===
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
food_data = load_food_data()

# === Команды ===
@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "👋 Привет! Я бот для подсчёта калорий и БЖУ.\n\n"
        "📌 Просто напиши:\n"
        "`название_продукта количество_в_граммах`\n"
        "Пример: `сыр 50`\n\n"
        "Я покажу, сколько в нём калорий, белков, жиров и углеводов.",
        parse_mode=ParseMode.MARKDOWN
    )

@dp.message(Command("help"))
async def help_command(message: Message):
    await message.answer(
        "Напиши продукт и массу, например:\n\n"
        "`шоколад 30` — и я покажу калории, белки, жиры и углеводы.\n\n"
        "Дополнительные команды:\n"
        "/list_products — список всех продуктов\n"
        "/add_product <название> <ккал> <белки> <жиры> <углеводы>",
        parse_mode=ParseMode.MARKDOWN
    )

@dp.message(Command("list_products"))
async def list_products(message: Message):
    if not food_data:
        await message.answer("🥲 Пока нет ни одного продукта.")
        return

    text = "📋 *Доступные продукты:*\n"
    for name, values in food_data.items():
        text += f"• {name.title()} — {values[0]} ккал, {values[1]}б/{values[2]}ж/{values[3]}у\n"
    await message.answer(text, parse_mode=ParseMode.MARKDOWN)

@dp.message(Command("add_product"))
async def add_product_command(message: Message):
    parts = message.text.strip().split()
    if len(parts) != 6:
        await message.answer("⚠️ Формат команды: /add_product <название> <ккал> <белки> <жиры> <углеводы>")
        return

    _, name, k, b, j, u = parts
    try:
        food_data[name.lower()] = [int(k), float(b), float(j), float(u)]
        save_food_data(food_data)
        await message.answer(f"✅ Продукт '{name}' добавлен.")
    except Exception:
        await message.answer("❌ Ошибка: проверь правильность чисел.")

@dp.message(F.text)
async def handle_food(message: Message):
    text = message.text.lower().strip()
    if text.startswith("/add_product"):
        return

    try:
        name, grams = text.rsplit(" ", 1)
        weight = float(grams.replace(",", "."))

        result = get_product_data(name, weight)
        if result is None:
            await message.answer("❌ Продукт не найден или масса недопустима.")
            return

        reply = (
            f"🔍 *{name.title()}* ({weight:.0f} г):\n"
            f"🍽 Калории: *{result['calories']}* ккал\n"
            f"🥩 Белки: *{result['proteins']}* г\n"
            f"🧈 Жиры: *{result['fats']}* г\n"
            f"🍞 Углеводы: *{result['carbs']}* г"
        )
        await message.answer(reply, parse_mode=ParseMode.MARKDOWN)
    except:
        await message.answer("⚠️ Введи в формате: `продукт количество`, например: `сыр 50`", parse_mode=ParseMode.MARKDOWN)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

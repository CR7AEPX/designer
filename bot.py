import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ContentType, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.enums import ParseMode
from aiogram.filters.command import CommandStart
from aiogram.client.default import DefaultBotProperties
from datetime import datetime, timedelta

API_TOKEN = '7805117897:AAHZEdLRvtBlIPrrvxKaE1YYOTEk4o3MRdo'
ADMIN_ID = 7646706120

logging.basicConfig(level=logging.INFO)

bot = Bot(
    token=API_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

last_submission = {}
user_category = {}

CATEGORIES = {
    "tech": "🧠 Технологии",
    "movies": "🎬 Кино",
    "games": "🎮 Игры",
    "culture": "🌍 Культура"
}

WELCOME_TEXT = (
    "<b>👤 Добро пожаловать в предложка-бот канала «Кодекс»!</b>\n\n"
    "Выберите категорию, к которой относится ваше предложение:\n"
    "— Технологии, кино, игры, культура.\n\n"
    "⚠️ Пожалуйста, отправляйте только текст или фотографии.\n"
    "Другие форматы не принимаются.\n\n"
    "⏳ Повторные предложения можно отправлять не чаще, чем раз в 10 минут.\n\n"
    "<b>Спасибо за ваш вклад! Лучшие идеи будут опубликованы в канале.</b>"
)

def get_category_keyboard():
    buttons = [
        [InlineKeyboardButton(text=name, callback_data=key)]
        for key, name in CATEGORIES.items()
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@dp.message(CommandStart())
async def cmd_start(message: Message):
    user_category.pop(message.from_user.id, None)
    await message.answer(WELCOME_TEXT, reply_markup=get_category_keyboard())

@dp.callback_query(F.data.in_(CATEGORIES.keys()))
async def category_chosen(callback: CallbackQuery):
    category_key = callback.data
    user_id = callback.from_user.id
    user_category[user_id] = category_key
    back_button = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="↩️ Выбрать другую категорию", callback_data="change_category")]
        ]
    )
    await callback.message.edit_text(
        f"Вы выбрали категорию: {CATEGORIES[category_key]}\n\n"
        "Теперь отправьте ваше предложение в виде текста или фотографии.",
        reply_markup=back_button
    )
    await callback.answer()

@dp.callback_query(F.data == "change_category")
async def change_category(callback: CallbackQuery):
    user_category.pop(callback.from_user.id, None)
    await callback.message.edit_text(WELCOME_TEXT, reply_markup=get_category_keyboard())
    await callback.answer()

@dp.message(F.content_type.in_([ContentType.TEXT, ContentType.PHOTO]))
async def handle_proposal(message: Message):
    user_id = message.from_user.id
    if user_id not in user_category:
        await message.reply("Пожалуйста, сначала выберите категорию, нажав на кнопку /start")
        return
    now = datetime.now()
    last_time = last_submission.get(user_id)
    if last_time and now - last_time < timedelta(minutes=10):
        await message.reply("⛔️ Пожалуйста, не спамьте. Новое предложение можно отправить через 10 минут.")
        return
    last_submission[user_id] = now
    category_key = user_category[user_id]
    category_name = CATEGORIES[category_key]
    username = (
        f"@{message.from_user.username}"
        if message.from_user.username
        else f"<a href='tg://user?id={user_id}'>Пользователь</a>"
    )
    header = f"Новое предложение по категории <b>{category_name}</b> от {username}:"
    await bot.send_message(chat_id=ADMIN_ID, text=header)
    await message.copy_to(chat_id=ADMIN_ID)
    await message.reply("✅ Спасибо! Ваше предложение получено и будет рассмотрено.")

@dp.message()
async def reject_other_formats(message: Message):
    await message.reply("⚠️ Пожалуйста, отправляйте только текст или фотографии. Другие форматы не принимаются.")

if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))

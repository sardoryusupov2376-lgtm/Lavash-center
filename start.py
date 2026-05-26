from telegram import Update
from telegram.ext import ContextTypes
from utils.keyboards import main_menu_keyboard
from utils.db import register_user
from config import CAFE_NAME

WELCOME_TEXT = """
👋 Xush kelibsiz, <b>{name}</b>!

🫓 <b>Lavash Center</b> botiga xush kelibsiz!

Biz sizga eng mazali va yangi lavashlar, hot-doglar va burgerlarni taqdim etamiz. 

Quyidagi menyudan foydalaning 👇
"""

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    # Foydalanuvchini ro'yxatdan o'tkazish
    register_user({
        "id": user.id,
        "username": user.username,
        "full_name": user.full_name,
    })

    # Savatni tozalash (yangi sessiya)
    context.user_data.setdefault("cart", {})

    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            WELCOME_TEXT.format(name=user.first_name),
            reply_markup=main_menu_keyboard(),
            parse_mode="HTML"
        )
    else:
        await update.message.reply_text(
            WELCOME_TEXT.format(name=user.first_name),
            reply_markup=main_menu_keyboard(),
            parse_mode="HTML"
        )

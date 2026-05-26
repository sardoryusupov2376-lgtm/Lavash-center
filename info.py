from telegram import Update
from telegram.ext import ContextTypes
from utils.keyboards import back_to_menu_keyboard
from config import (
    CAFE_ADDRESS, CAFE_PHONE, CAFE_LOCATION_LAT, CAFE_LOCATION_LON, WORKING_HOURS
)

PROMOTIONS = [
    ("🎁 Har 5-ta buyurtmada sovg'a!", "5 marta buyurtma bering va bitta lavash <b>bepul</b> oling!"),
    ("🕐 Tushlik aksiyasi (12:00–14:00)", "Ikkita lavash olsangiz — ichimlik <b>bepul</b>!"),
    ("📱 Do'stni taklif et", "Do'stingiz birinchi buyurtma bersa, siz <b>10% chegirma</b> olasiz!"),
]

async def location_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        f"📍 <b>Bizning manzilimiz:</b>\n\n"
        f"🏠 {CAFE_ADDRESS}\n\n"
        f"Quyida xaritada ko'rishingiz mumkin 👇",
        reply_markup=back_to_menu_keyboard(),
        parse_mode="HTML"
    )
    await query.message.reply_location(
        latitude=CAFE_LOCATION_LAT,
        longitude=CAFE_LOCATION_LON
    )

async def working_hours_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    hours_text = "\n".join([f"📅 <b>{day}:</b> {time}" for day, time in WORKING_HOURS.items()])

    await query.edit_message_text(
        f"⏰ <b>Ish vaqtimiz:</b>\n\n{hours_text}",
        reply_markup=back_to_menu_keyboard(),
        parse_mode="HTML"
    )

async def phone_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        f"📞 <b>Bog'lanish:</b>\n\n"
        f"☎️ Telefon: <b>{CAFE_PHONE}</b>\n\n"
        f"Ish vaqtida qo'ng'iroq qiling!",
        reply_markup=back_to_menu_keyboard(),
        parse_mode="HTML"
    )

async def promotions_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    text = "🎁 <b>Joriy aksiyalar va chegirmalar:</b>\n\n"
    for title, desc in PROMOTIONS:
        text += f"━━━━━━━━━━━━━━━\n{title}\n{desc}\n\n"

    await query.edit_message_text(
        text,
        reply_markup=back_to_menu_keyboard(),
        parse_mode="HTML"
    )

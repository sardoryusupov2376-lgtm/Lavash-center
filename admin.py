from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from utils.db import get_orders, update_order_status, get_menu, add_menu_item, delete_menu_item, get_users
from utils.keyboards import admin_keyboard, order_status_keyboard, admin_menu_keyboard, main_menu_keyboard
from config import ADMIN_IDS

# Admin conversation states
ADMIN_ADD_NAME     = 10
ADMIN_ADD_PRICE    = 11
ADMIN_ADD_CATEGORY = 12
ADMIN_ADD_EMOJI    = 13
ADMIN_BROADCAST    = 20

STATUS_LABELS = {
    "pending":    "⏳ Kutilmoqda",
    "accepted":   "✅ Qabul qilindi",
    "cooking":    "👨‍🍳 Tayyorlanmoqda",
    "delivering": "🚚 Yo'lda",
    "done":       "✔️ Yetkazildi",
    "cancelled":  "❌ Bekor qilindi",
}

def is_admin(user_id):
    return user_id in ADMIN_IDS

async def admin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Sizda admin huquqi yo'q.")
        return

    orders = get_orders()
    users = get_users()
    pending = sum(1 for o in orders if o["status"] == "pending")

    text = (
        f"🔐 <b>Admin Panel — Lavash Center</b>\n\n"
        f"📦 Jami buyurtmalar: <b>{len(orders)}</b>\n"
        f"⏳ Kutilayotgan: <b>{pending}</b>\n"
        f"👥 Foydalanuvchilar: <b>{len(users)}</b>\n\n"
        f"Kerakli bo'limni tanlang:"
    )
    await update.message.reply_text(text, reply_markup=admin_keyboard(), parse_mode="HTML")

async def admin_orders_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not is_admin(query.from_user.id):
        await query.answer("⛔ Ruxsat yo'q!", show_alert=True)
        return

    orders = get_orders()
    active = [o for o in orders if o["status"] not in ("done", "cancelled")]

    if not active:
        await query.edit_message_text(
            "📦 Hozirda faol buyurtmalar yo'q.",
            reply_markup=admin_keyboard()
        )
        return

    for o in active[-10:]:
        status = STATUS_LABELS.get(o["status"], o["status"])
        text = (
            f"📦 <b>Buyurtma #{o['id']}</b>\n"
            f"👤 {o['full_name']} (@{o.get('username', '-')})\n"
            f"📱 {o.get('phone', '-')}\n"
            f"🚚 {'Yetkazib berish' if o.get('delivery_type') == 'deliver' else 'Olib ketish'}\n"
            f"💰 {int(o['total']):,} so'm\n"
            f"📊 {status}\n"
            f"🕐 {o.get('created_at', '')}"
        )
        try:
            await query.message.reply_text(
                text,
                reply_markup=order_status_keyboard(o["id"]),
                parse_mode="HTML"
            )
        except Exception:
            pass

    await query.edit_message_text(
        f"📋 Faol buyurtmalar: <b>{len(active)}</b> ta",
        reply_markup=admin_keyboard(),
        parse_mode="HTML"
    )

async def admin_update_status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not is_admin(query.from_user.id):
        await query.answer("⛔ Ruxsat yo'q!", show_alert=True)
        return

    parts = query.data.split("_")
    order_id = int(parts[1])
    new_status = parts[2]

    update_order_status(order_id, new_status)
    status_label = STATUS_LABELS.get(new_status, new_status)

    await query.edit_message_text(
        f"✅ Buyurtma #{order_id} holati yangilandi:\n{status_label}",
        reply_markup=order_status_keyboard(order_id)
    )

    # Foydalanuvchiga xabar yuborish
    orders = get_orders()
    order = next((o for o in orders if o["id"] == order_id), None)
    if order:
        try:
            await query.get_bot().send_message(
                order["user_id"],
                f"📦 <b>Buyurtma #{order_id} holati:</b>\n{status_label}",
                parse_mode="HTML"
            )
        except Exception:
            pass

async def admin_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not is_admin(query.from_user.id):
        return

    menu = get_menu()
    items = menu["items"]
    text = "🍽 <b>Menyu boshqaruvi</b>\n\n"

    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    keyboard = []
    for item in items:
        price = int(item["price"])
        keyboard.append([
            InlineKeyboardButton(
                f"{item['emoji']} {item['name']} — {price:,} so'm",
                callback_data=f"del_item_{item['id']}"
            )
        ])
    keyboard.append([InlineKeyboardButton("➕ Yangi mahsulot qo'shish", callback_data="admin_add_item")])
    keyboard.append([InlineKeyboardButton("🔙 Admin panel", callback_data="admin_panel")])

    await query.edit_message_text(
        text + "O'chirish uchun mahsulotga bosing:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )

async def admin_delete_item_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not is_admin(query.from_user.id):
        return

    item_id = int(query.data[9:])
    menu = get_menu()
    item = next((i for i in menu["items"] if i["id"] == item_id), None)
    if item:
        delete_menu_item(item_id)
        await query.answer(f"✅ '{item['name']}' o'chirildi!", show_alert=True)
    await admin_menu_handler(update, context)

async def admin_add_item_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Multi-step: nom → narx → kategoriya → emoji."""
    query = update.callback_query if update.callback_query else None
    message = update.message

    if not is_admin(update.effective_user.id):
        return ConversationHandler.END

    # 1-qadam: boshlash
    if query and query.data == "admin_add_item":
        await query.answer()
        context.user_data["admin_adding"] = True
        context.user_data["new_item"] = {}
        context.user_data["add_step"] = "name"
        await query.edit_message_text("➕ <b>Yangi mahsulot qo'shish</b>\n\nMahsulot nomini kiriting:", parse_mode="HTML")
        return ADMIN_ADD_NAME

    step = context.user_data.get("add_step")

    # 2-qadam: nom
    if step == "name" and message:
        context.user_data["new_item"]["name"] = message.text
        context.user_data["add_step"] = "price"
        await message.reply_text("💰 Narxini kiriting (so'mda, faqat raqam):")
        return ADMIN_ADD_PRICE

    # 3-qadam: narx
    if step == "price" and message:
        try:
            price = int(message.text.replace(" ", "").replace(",", ""))
        except ValueError:
            await message.reply_text("❌ Noto'g'ri narx. Faqat raqam kiriting:")
            return ADMIN_ADD_PRICE
        context.user_data["new_item"]["price"] = price
        context.user_data["add_step"] = "category"

        categories = get_menu()["categories"]
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        keyboard = [[InlineKeyboardButton(c["name"], callback_data=f"cat_{c['id']}")] for c in categories]
        await message.reply_text(
            "📂 Kategoriyani tanlang:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return ADMIN_ADD_CATEGORY

    # 4-qadam: kategoriya (callback)
    if step == "category" and query:
        await query.answer()
        cat_id = query.data[4:]
        context.user_data["new_item"]["category"] = cat_id
        context.user_data["add_step"] = "emoji"
        await query.edit_message_text("😊 Emoji kiriting (masalan: 🫓):")
        return ADMIN_ADD_EMOJI

    # 5-qadam: emoji
    if step == "emoji" and message:
        context.user_data["new_item"]["emoji"] = message.text.strip()
        context.user_data["new_item"]["description"] = ""
        item = context.user_data.pop("new_item")
        context.user_data.pop("admin_adding", None)
        context.user_data.pop("add_step", None)

        add_menu_item(item)
        price = int(item["price"])
        await message.reply_text(
            f"✅ <b>Mahsulot qo'shildi!</b>\n\n"
            f"{item['emoji']} {item['name']} — {price:,} so'm",
            reply_markup=admin_keyboard(),
            parse_mode="HTML"
        )
        return ConversationHandler.END

    return ConversationHandler.END

async def admin_broadcast_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not is_admin(query.from_user.id):
        return ConversationHandler.END

    await query.edit_message_text(
        "📢 <b>Ommaviy xabar yuborish</b>\n\nBarcha foydalanuvchilarga yuboriladigan xabarni kiriting:",
        parse_mode="HTML"
    )
    return ADMIN_BROADCAST

async def do_broadcast_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return ConversationHandler.END

    text = update.message.text
    users = get_users()
    sent, failed = 0, 0

    for user in users:
        try:
            await update.get_bot().send_message(
                user["id"],
                f"📢 <b>Lavash Center:</b>\n\n{text}",
                parse_mode="HTML"
            )
            sent += 1
        except Exception:
            failed += 1

    await update.message.reply_text(
        f"✅ Xabar yuborildi!\n✔️ Muvaffaqiyatli: {sent}\n❌ Yuborilmadi: {failed}",
        reply_markup=admin_keyboard()
    )
    return ConversationHandler.END

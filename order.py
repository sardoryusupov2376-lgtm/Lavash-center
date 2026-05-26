from datetime import datetime
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
from utils.db import get_item_by_id, save_order, get_user_orders
from utils.keyboards import (
    cart_keyboard, delivery_type_keyboard, location_keyboard,
    phone_keyboard, confirm_keyboard, back_to_menu_keyboard, main_menu_keyboard
)
from config import DELIVERY_PRICE, MIN_ORDER_AMOUNT, ADMIN_IDS

# Conversation states
CHOOSING_DELIVERY = 1
GETTING_LOCATION   = 2
GETTING_PHONE      = 3
CONFIRMING         = 4

STATUS_LABELS = {
    "pending":    "⏳ Kutilmoqda",
    "accepted":   "✅ Qabul qilindi",
    "cooking":    "👨‍🍳 Tayyorlanmoqda",
    "delivering": "🚚 Yo'lda",
    "done":       "✔️ Yetkazildi",
    "cancelled":  "❌ Bekor qilindi",
}

def cart_summary(cart, user_data):
    """Savat ma'lumotlarini chiroyli matn sifatida qaytaradi."""
    if not cart:
        return None, 0

    lines = []
    total = 0
    for item_id, qty in cart.items():
        item = get_item_by_id(int(item_id))
        if item:
            price = int(item["price"])
            subtotal = price * qty
            total += subtotal
            lines.append(f"{item['emoji']} {item['name']} x{qty} = {subtotal:,} so'm")

    return "\n".join(lines), total


# ── HANDLERS ─────────────────────────────────────

async def order_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mahsulot detail sahifasini ko'rsatish."""
    query = update.callback_query
    await query.answer()
    item_id = int(query.data[5:])
    item = get_item_by_id(item_id)
    if not item:
        await query.edit_message_text("Mahsulot topilmadi.")
        return
    from utils.keyboards import item_detail_keyboard
    price = int(item["price"])
    await query.edit_message_text(
        f"{item['emoji']} <b>{item['name']}</b>\n\n"
        f"📝 {item.get('description', '')}\n\n"
        f"💰 Narxi: <b>{price:,} so'm</b>",
        reply_markup=item_detail_keyboard(item_id),
        parse_mode="HTML"
    )


async def add_to_cart_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Savatga mahsulot qo'shish."""
    query = update.callback_query
    await query.answer("✅ Savatga qo'shildi!")

    item_id = str(query.data[4:])
    cart = context.user_data.setdefault("cart", {})
    cart[item_id] = cart.get(item_id, 0) + 1

    item = get_item_by_id(int(item_id))
    total_qty = sum(cart.values())

    await query.edit_message_text(
        f"✅ <b>{item['name']}</b> savatga qo'shildi!\n\n"
        f"🛒 Savatchada jami: <b>{total_qty} ta mahsulot</b>\n\n"
        f"Davom etishni xohlaysizmi?",
        reply_markup=back_to_menu_keyboard(),
        parse_mode="HTML"
    )


async def cart_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Savatni ko'rsatish."""
    query = update.callback_query
    await query.answer()

    cart = context.user_data.get("cart", {})
    if not cart:
        await query.edit_message_text(
            "🛒 <b>Savatcha bo'sh</b>\n\nAvval menyudan mahsulot tanlang.",
            reply_markup=back_to_menu_keyboard(),
            parse_mode="HTML"
        )
        return

    lines, total = cart_summary(cart, context.user_data)
    delivery_note = f"\n🚚 Yetkazib berish: <b>{DELIVERY_PRICE:,} so'm</b>" if total < MIN_ORDER_AMOUNT else ""

    await query.edit_message_text(
        f"🛒 <b>Sizning savatchingiz:</b>\n\n"
        f"{lines}\n\n"
        f"💰 Jami: <b>{total:,} so'm</b>{delivery_note}",
        reply_markup=cart_keyboard(cart),
        parse_mode="HTML"
    )


async def remove_from_cart_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Savatdan mahsulot o'chirish."""
    query = update.callback_query
    await query.answer()

    item_id = query.data[7:]
    cart = context.user_data.get("cart", {})
    if item_id in cart:
        del cart[item_id]

    if not cart:
        await query.edit_message_text(
            "🛒 Savat bo'shlashdi.",
            reply_markup=back_to_menu_keyboard()
        )
        return

    lines, total = cart_summary(cart, context.user_data)
    await query.edit_message_text(
        f"🛒 <b>Savatchingiz:</b>\n\n{lines}\n\n💰 Jami: <b>{total:,} so'm</b>",
        reply_markup=cart_keyboard(cart),
        parse_mode="HTML"
    )


async def checkout_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Buyurtma berishni boshlash."""
    query = update.callback_query
    await query.answer()

    cart = context.user_data.get("cart", {})
    if not cart:
        await query.edit_message_text(
            "🛒 Savat bo'sh! Avval mahsulot tanlang.",
            reply_markup=back_to_menu_keyboard()
        )
        return ConversationHandler.END

    await query.edit_message_text(
        "🚚 <b>Yetkazib berish usulini tanlang:</b>",
        reply_markup=delivery_type_keyboard(),
        parse_mode="HTML"
    )
    return CHOOSING_DELIVERY


async def delivery_type_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yetkazib berish turini tanlash."""
    query = update.callback_query
    await query.answer()

    delivery_type = query.data.split("_")[1]
    context.user_data["delivery_type"] = delivery_type

    inline_kb, reply_kb = location_keyboard()

    if delivery_type == "deliver":
        await query.edit_message_text(
            "📍 <b>Manzilingizni yuboring</b>\n\nYoki o'tkazib yuboring:",
            reply_markup=inline_kb,
            parse_mode="HTML"
        )
        await query.message.reply_text(
            "📍 Lokatsiyangizni ulashing:",
            reply_markup=reply_kb
        )
    else:
        await query.edit_message_text(
            "📍 Olib ketish tanlandi.\n\n<b>Manzilingizni yuboring yoki o'tkazib yuboring:</b>",
            reply_markup=inline_kb,
            parse_mode="HTML"
        )
        await query.message.reply_text("📍 Lokatsiya (ixtiyoriy):", reply_markup=reply_kb)

    return GETTING_LOCATION


async def get_location_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lokatsiyani qabul qilish."""
    if update.message and update.message.location:
        loc = update.message.location
        context.user_data["location"] = {"lat": loc.latitude, "lon": loc.longitude}
        await update.message.reply_text(
            "✅ Lokatsiya qabul qilindi!",
            reply_markup=ReplyKeyboardRemove()
        )
    elif update.callback_query:
        await update.callback_query.answer()
        context.user_data["location"] = None

    inline_kb, reply_kb = phone_keyboard()
    if update.message:
        await update.message.reply_text(
            "📱 <b>Telefon raqamingizni yuboring:</b>",
            reply_markup=reply_kb,
            parse_mode="HTML"
        )
    else:
        await update.callback_query.message.reply_text(
            "📱 <b>Telefon raqamingizni yuboring:</b>",
            reply_markup=reply_kb,
            parse_mode="HTML"
        )
    return GETTING_PHONE


async def get_phone_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Telefon raqamini qabul qilish va tasdiqlash."""
    if update.message and update.message.contact:
        context.user_data["phone"] = update.message.contact.phone_number
        await update.message.reply_text("✅ Raqam qabul qilindi!", reply_markup=ReplyKeyboardRemove())
    elif update.callback_query:
        await update.callback_query.answer()
        context.user_data["phone"] = "Ko'rsatilmagan"
        await update.callback_query.message.reply_text(
            "⬇️", reply_markup=ReplyKeyboardRemove()
        )

    # Tasdiqlash xabarini ko'rsatish
    cart = context.user_data.get("cart", {})
    lines, total = cart_summary(cart, context.user_data)
    delivery = context.user_data.get("delivery_type", "pickup")
    delivery_label = "🚚 Yetkazib berish" if delivery == "deliver" else "🏃 Olib ketish"
    phone = context.user_data.get("phone", "Ko'rsatilmagan")

    msg = update.message or update.callback_query.message
    await msg.reply_text(
        f"📋 <b>Buyurtmangizni tasdiqlang:</b>\n\n"
        f"{lines}\n\n"
        f"💰 Mahsulotlar: <b>{total:,} so'm</b>\n"
        f"🚚 Usul: <b>{delivery_label}</b>\n"
        f"📱 Telefon: <b>{phone}</b>\n\n"
        f"✅ Tasdiqlaysizmi?",
        reply_markup=confirm_keyboard(),
        parse_mode="HTML"
    )
    return CONFIRMING


async def confirm_order_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Buyurtmani yakunlash."""
    query = update.callback_query
    await query.answer()

    if query.data == "cancel_order":
        context.user_data["cart"] = {}
        await query.edit_message_text(
            "❌ Buyurtma bekor qilindi.",
            reply_markup=main_menu_keyboard()
        )
        return ConversationHandler.END

    cart = context.user_data.get("cart", {})
    lines, total = cart_summary(cart, context.user_data)

    order = {
        "user_id": query.from_user.id,
        "username": query.from_user.username,
        "full_name": query.from_user.full_name,
        "items": dict(cart),
        "total": total,
        "delivery_type": context.user_data.get("delivery_type", "pickup"),
        "location": context.user_data.get("location"),
        "phone": context.user_data.get("phone", "Ko'rsatilmagan"),
        "status": "pending",
        "created_at": datetime.now().strftime("%d.%m.%Y %H:%M"),
    }
    order_id = save_order(order)

    # Foydalanuvchiga xabar
    await query.edit_message_text(
        f"🎉 <b>Buyurtmangiz qabul qilindi!</b>\n\n"
        f"📦 Buyurtma raqami: <b>#{order_id}</b>\n"
        f"⏳ Holat: <b>Kutilmoqda</b>\n\n"
        f"Tez orada siz bilan bog'lanamiz!",
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML"
    )

    # Adminga xabar
    delivery_label = "🚚 Yetkazib berish" if order["delivery_type"] == "deliver" else "🏃 Olib ketish"
    location = order.get("location")

    admin_text = (
        f"🔔 <b>YANGI BUYURTMA #{order_id}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 Mijoz: <b>{order['full_name']}</b>\n"
        f"🆔 Username: @{order.get('username') or '-'}\n"
        f"📱 Telefon: <b>{order['phone']}</b>\n"
        f"🚚 Usul: <b>{delivery_label}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🛒 <b>Buyurtma tarkibi:</b>\n{lines}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 Jami: <b>{total:,} so'm</b>\n"
        f"🕐 Vaqt: {order['created_at']}"
    )

    from utils.keyboards import order_status_keyboard
    from config import ORDERS_CHANNEL_ID
    bot = query.get_bot()

    # 1 — Adminga xabar (holat tugmalari bilan)
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(
                admin_id,
                admin_text,
                reply_markup=order_status_keyboard(order_id),
                parse_mode="HTML"
            )
            if location:
                await bot.send_location(admin_id, latitude=location["lat"], longitude=location["lon"])
                await bot.send_message(admin_id, f"📍 <b>#{order_id} - lokatsiya</b>", parse_mode="HTML")
        except Exception:
            pass

    # 2 — Kanalga xabar
    try:
        await bot.send_message(
            ORDERS_CHANNEL_ID,
            admin_text,
            parse_mode="HTML"
        )
        if location:
            await bot.send_location(ORDERS_CHANNEL_ID, latitude=location["lat"], longitude=location["lon"])
            await bot.send_message(
                ORDERS_CHANNEL_ID,
                f"📍 <b>#{order_id} - mijoz lokatsiyasi</b>",
                parse_mode="HTML"
            )
    except Exception:
        pass

    context.user_data["cart"] = {}
    return ConversationHandler.END


async def my_orders_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchi buyurtmalarini ko'rsatish."""
    query = update.callback_query
    await query.answer()

    orders = get_user_orders(query.from_user.id)
    if not orders:
        await query.edit_message_text(
            "📦 <b>Sizda hali buyurtmalar yo'q.</b>\n\nMenyudan buyurtma bering!",
            reply_markup=main_menu_keyboard(),
            parse_mode="HTML"
        )
        return

    text = "📦 <b>Sizning buyurtmalaringiz:</b>\n\n"
    for o in reversed(orders[-5:]):  # oxirgi 5 ta
        status = STATUS_LABELS.get(o["status"], o["status"])
        text += (
            f"🔹 <b>Buyurtma #{o['id']}</b>\n"
            f"   💰 {int(o['total']):,} so'm\n"
            f"   {status}\n"
            f"   🕐 {o.get('created_at', '')}\n\n"
        )

    await query.edit_message_text(
        text,
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML"
    )
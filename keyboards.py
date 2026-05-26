from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("📋 Menyu", callback_data="menu"),
         InlineKeyboardButton("🛒 Savatcha", callback_data="cart")],
        [InlineKeyboardButton("📦 Mening buyurtmalarim", callback_data="my_orders")],
        [InlineKeyboardButton("📍 Lokatsiya", callback_data="location"),
         InlineKeyboardButton("⏰ Ish vaqti", callback_data="working_hours")],
        [InlineKeyboardButton("📞 Telefon", callback_data="contact"),
         InlineKeyboardButton("🎁 Aktsiyalar", callback_data="promotions")],
    ]
    return InlineKeyboardMarkup(keyboard)

def categories_keyboard(categories):
    keyboard = []
    for cat in categories:
        keyboard.append([InlineKeyboardButton(cat["name"], callback_data=f"cat_{cat['id']}")])
    keyboard.append([InlineKeyboardButton("🔙 Orqaga", callback_data="main_menu")])
    return InlineKeyboardMarkup(keyboard)

def items_keyboard(items, cat_id):
    keyboard = []
    for item in items:
        price = int(item["price"])
        keyboard.append([
            InlineKeyboardButton(
                f"{item['emoji']} {item['name']} — {price:,} so'm",
                callback_data=f"item_{item['id']}"
            )
        ])
    keyboard.append([InlineKeyboardButton("🔙 Kategoriyalar", callback_data="menu")])
    return InlineKeyboardMarkup(keyboard)

def item_detail_keyboard(item_id):
    keyboard = [
        [InlineKeyboardButton("➕ Savatga qo'shish", callback_data=f"add_{item_id}")],
        [InlineKeyboardButton("🛒 Savatchani ko'rish", callback_data="cart")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="menu")],
    ]
    return InlineKeyboardMarkup(keyboard)

def cart_keyboard(cart_items):
    keyboard = []
    for item_id, qty in cart_items.items():
        keyboard.append([
            InlineKeyboardButton(f"❌ O'chirish ({qty}x)", callback_data=f"remove_{item_id}")
        ])
    keyboard.append([InlineKeyboardButton("✅ Buyurtma berish", callback_data="checkout")])
    keyboard.append([InlineKeyboardButton("🔙 Menyu", callback_data="menu")])
    return InlineKeyboardMarkup(keyboard)

def delivery_type_keyboard():
    keyboard = [
        [InlineKeyboardButton("🚚 Yetkazib berish", callback_data="delivery_deliver")],
        [InlineKeyboardButton("🏃 Olib ketish", callback_data="delivery_pickup")],
        [InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel_order")],
    ]
    return InlineKeyboardMarkup(keyboard)

def location_keyboard():
    keyboard = [
        [InlineKeyboardButton("⏭ O'tkazib yuborish", callback_data="skip_location")]
    ]
    reply_kb = ReplyKeyboardMarkup(
        [[KeyboardButton("📍 Lokatsiya yuborish", request_location=True)]],
        resize_keyboard=True, one_time_keyboard=True
    )
    return InlineKeyboardMarkup(keyboard), reply_kb

def phone_keyboard():
    keyboard = [
        [InlineKeyboardButton("⏭ O'tkazib yuborish", callback_data="skip_phone")]
    ]
    reply_kb = ReplyKeyboardMarkup(
        [[KeyboardButton("📱 Raqamni ulashish", request_contact=True)]],
        resize_keyboard=True, one_time_keyboard=True
    )
    return InlineKeyboardMarkup(keyboard), reply_kb

def confirm_keyboard():
    keyboard = [
        [InlineKeyboardButton("✅ Tasdiqlash", callback_data="confirm_order")],
        [InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel_order")],
    ]
    return InlineKeyboardMarkup(keyboard)

def back_to_menu_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Bosh menyu", callback_data="main_menu")]])

def admin_keyboard():
    keyboard = [
        [InlineKeyboardButton("📦 Barcha buyurtmalar", callback_data="admin_orders")],
        [InlineKeyboardButton("🍽 Menyu boshqaruv", callback_data="admin_menu")],
        [InlineKeyboardButton("📢 Xabar yuborish", callback_data="admin_broadcast")],
    ]
    return InlineKeyboardMarkup(keyboard)

def order_status_keyboard(order_id):
    keyboard = [
        [InlineKeyboardButton("✅ Qabul qilindi", callback_data=f"status_{order_id}_accepted")],
        [InlineKeyboardButton("👨‍🍳 Tayyorlanmoqda", callback_data=f"status_{order_id}_cooking")],
        [InlineKeyboardButton("🚚 Yo'lda", callback_data=f"status_{order_id}_delivering")],
        [InlineKeyboardButton("✔️ Yetkazildi", callback_data=f"status_{order_id}_done")],
        [InlineKeyboardButton("❌ Bekor qilindi", callback_data=f"status_{order_id}_cancelled")],
    ]
    return InlineKeyboardMarkup(keyboard)

def admin_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("➕ Mahsulot qo'shish", callback_data="admin_add_item")],
        [InlineKeyboardButton("🔙 Admin panel", callback_data="admin_panel")],
    ]
    return InlineKeyboardMarkup(keyboard)

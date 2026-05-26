from telegram import Update
from telegram.ext import ContextTypes
from utils.db import get_categories, get_items_by_category, get_item_by_id
from utils.keyboards import categories_keyboard, items_keyboard, item_detail_keyboard

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    categories = get_categories()
    await query.edit_message_text(
        "🍽 <b>Menyu kategoriyalari</b>\n\nQuyidagi kategoriyalardan birini tanlang:",
        reply_markup=categories_keyboard(categories),
        parse_mode="HTML"
    )

async def menu_category_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # admin_add_item callback ham cat_ bilan boshlanadi — uni o'tkazib yuborish
    if query.data == "cat_" or not query.data.startswith("cat_"):
        return

    cat_id = query.data[4:]

    # Admin tomonidan kategoriya tanlash (buyurtma shart emas)
    if context.user_data.get("admin_adding"):
        context.user_data["new_item"]["category"] = cat_id
        from handlers.admin import admin_add_item_handler
        await admin_add_item_handler(update, context)
        return

    categories = get_categories()
    cat = next((c for c in categories if c["id"] == cat_id), None)
    if not cat:
        await query.edit_message_text("Kategoriya topilmadi.")
        return

    items = get_items_by_category(cat_id)
    if not items:
        await query.edit_message_text(
            f"{cat['name']}\n\n❌ Bu kategoriyada hozircha mahsulotlar yo'q.",
            reply_markup=categories_keyboard(categories),
            parse_mode="HTML"
        )
        return

    await query.edit_message_text(
        f"{cat['emoji']} <b>{cat['name']}</b>\n\nMahsulotni tanlang:",
        reply_markup=items_keyboard(items, cat_id),
        parse_mode="HTML"
    )

async def order_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    item_id = int(query.data[5:])
    item = get_item_by_id(item_id)
    if not item:
        await query.edit_message_text("Mahsulot topilmadi.")
        return

    price = int(item["price"])
    text = (
        f"{item['emoji']} <b>{item['name']}</b>\n\n"
        f"📝 {item.get('description', '')}\n\n"
        f"💰 Narxi: <b>{price:,} so'm</b>"
    )
    await query.edit_message_text(
        text,
        reply_markup=item_detail_keyboard(item_id),
        parse_mode="HTML"
    )

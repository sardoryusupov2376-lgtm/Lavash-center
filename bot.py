import logging
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ConversationHandler
from handlers.start import start_handler
from handlers.menu import menu_handler, menu_category_handler
from handlers.order import (
    order_handler, add_to_cart_handler, cart_handler,
    remove_from_cart_handler, checkout_handler,
    delivery_type_handler, get_location_handler,
    get_phone_handler, confirm_order_handler,
    my_orders_handler,
    CHOOSING_DELIVERY, GETTING_LOCATION, GETTING_PHONE, CONFIRMING
)
from handlers.info import location_handler, working_hours_handler, phone_handler, promotions_handler
from handlers.admin import (
    admin_handler, admin_orders_handler, admin_update_status_handler,
    admin_menu_handler, admin_add_item_handler, admin_delete_item_handler,
    admin_broadcast_handler, do_broadcast_handler,
    ADMIN_ADD_NAME, ADMIN_ADD_PRICE, ADMIN_ADD_CATEGORY, ADMIN_ADD_EMOJI,
    ADMIN_BROADCAST
)
from config import BOT_TOKEN

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Order conversation handler
    order_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(checkout_handler, pattern="^checkout$")],
        states={
            CHOOSING_DELIVERY: [CallbackQueryHandler(delivery_type_handler, pattern="^delivery_")],
            GETTING_LOCATION: [
                MessageHandler(filters.LOCATION, get_location_handler),
                CallbackQueryHandler(get_location_handler, pattern="^skip_location$")
            ],
            GETTING_PHONE: [
                MessageHandler(filters.CONTACT, get_phone_handler),
                CallbackQueryHandler(get_phone_handler, pattern="^skip_phone$")
            ],
            CONFIRMING: [CallbackQueryHandler(confirm_order_handler, pattern="^(confirm_order|cancel_order)$")],
        },
        fallbacks=[CommandHandler("start", start_handler)],
        per_message=False
    )

    # Admin add item conversation
    admin_add_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_add_item_handler, pattern="^admin_add_item$")],
        states={
            ADMIN_ADD_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_add_item_handler)],
            ADMIN_ADD_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_add_item_handler)],
            ADMIN_ADD_CATEGORY: [CallbackQueryHandler(admin_add_item_handler, pattern="^cat_")],
            ADMIN_ADD_EMOJI: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_add_item_handler)],
        },
        fallbacks=[CommandHandler("start", start_handler)],
        per_message=False
    )

    # Admin broadcast conversation
    admin_broadcast_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_broadcast_handler, pattern="^admin_broadcast$")],
        states={
            ADMIN_BROADCAST: [MessageHandler(filters.TEXT & ~filters.COMMAND, do_broadcast_handler)],
        },
        fallbacks=[CommandHandler("start", start_handler)],
        per_message=False
    )

    # Register handlers
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("admin", admin_handler))

    app.add_handler(order_conv)
    app.add_handler(admin_add_conv)
    app.add_handler(admin_broadcast_conv)

    app.add_handler(CallbackQueryHandler(menu_handler, pattern="^menu$"))
    app.add_handler(CallbackQueryHandler(menu_category_handler, pattern="^cat_"))
    app.add_handler(CallbackQueryHandler(order_handler, pattern="^item_"))
    app.add_handler(CallbackQueryHandler(add_to_cart_handler, pattern="^add_"))
    app.add_handler(CallbackQueryHandler(cart_handler, pattern="^cart$"))
    app.add_handler(CallbackQueryHandler(remove_from_cart_handler, pattern="^remove_"))
    app.add_handler(CallbackQueryHandler(my_orders_handler, pattern="^my_orders$"))
    app.add_handler(CallbackQueryHandler(location_handler, pattern="^location$"))
    app.add_handler(CallbackQueryHandler(working_hours_handler, pattern="^working_hours$"))
    app.add_handler(CallbackQueryHandler(phone_handler, pattern="^contact$"))
    app.add_handler(CallbackQueryHandler(promotions_handler, pattern="^promotions$"))
    app.add_handler(CallbackQueryHandler(admin_orders_handler, pattern="^admin_orders$"))
    app.add_handler(CallbackQueryHandler(admin_update_status_handler, pattern="^status_"))
    app.add_handler(CallbackQueryHandler(admin_menu_handler, pattern="^admin_menu$"))
    app.add_handler(CallbackQueryHandler(admin_delete_item_handler, pattern="^del_item_"))
    app.add_handler(CallbackQueryHandler(start_handler, pattern="^main_menu$"))

    logger.info("🚀 Lavash Center Bot ishga tushdi!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()

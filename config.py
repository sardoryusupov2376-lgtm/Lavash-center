# =====================================================
#   LAVASH CENTER BOT - KONFIGURATSIYA
# =====================================================

# Telegram Bot Token (@BotFather dan oling)
BOT_TOKEN = "8091638723:AAGYA2cEL9f_bt2qN5Q4H46EPyt6_zBck94"

# Admin Telegram ID (sizning Telegram ID'ingiz)
# ID olish uchun: @userinfobot ga /start yuboring
ADMIN_IDS = [7743062528]  # O'zingizning ID'ingizni kiriting

# Kafe ma'lumotlari
CAFE_NAME = "🫓 Lavash Center"
CAFE_ADDRESS = "Toshkent sh., Chilonzor tumani, Bunyodkor ko'chasi 15"
CAFE_PHONE = "+998 90 123 45 67"
CAFE_LOCATION_LAT = 41.2995  # Kafe koordinatasi
CAFE_LOCATION_LON = 69.2401  # Kafe koordinatasi

WORKING_HOURS = {
    "Dushanba - Juma": "09:00 - 22:00",
    "Shanba":           "10:00 - 23:00",
    "Yakshanba":        "10:00 - 22:00",
}

# Yetkazib berish narxi (so'm)
DELIVERY_PRICE = 10000

# Minimal buyurtma summasi (so'm)
MIN_ORDER_AMOUNT = 30000

# Ma'lumotlar fayllari
DATA_DIR = "data"
MENU_FILE = f"{DATA_DIR}/menu.json"
ORDERS_FILE = f"{DATA_DIR}/orders.json"
USERS_FILE = f"{DATA_DIR}/users.json"

# Buyurtmalar kanali
ORDERS_CHANNEL_ID = -1003808339728
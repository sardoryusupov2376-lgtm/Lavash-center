# 🫓 Lavash Center Telegram Bot

Professional kafe Telegram boti.

---

## 📁 Loyiha strukturasi

```
lavash_center_bot/
├── bot.py              ← Asosiy fayl (ishga tushirish)
├── config.py           ← TOKEN va sozlamalar
├── requirements.txt    ← Kerakli kutubxonalar
├── data/
│   ├── menu.json       ← Menyu ma'lumotlari
│   ├── orders.json     ← Buyurtmalar
│   └── users.json      ← Foydalanuvchilar
├── handlers/
│   ├── start.py        ← /start komandasi
│   ├── menu.py         ← Menyu ko'rish
│   ├── order.py        ← Buyurtma berish
│   ├── info.py         ← Lokatsiya, telefon, ish vaqti
│   └── admin.py        ← Admin panel
└── utils/
    ├── db.py           ← JSON baza funksiyalari
    └── keyboards.py    ← Barcha tugmalar
```

---

## ⚙️ O'rnatish va ishga tushirish

### 1. Bot token olish
1. Telegramda [@BotFather](https://t.me/BotFather) ga boring
2. `/newbot` yuboring
3. Bot nomini kiriting: `Lavash Center`
4. Username kiriting: `lavashcenter_bot` (yoki boshqa)
5. Tokenni nusxalab oling

### 2. config.py ni sozlash
```python
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"   # ← O'zingizning tokeningiz
ADMIN_IDS = [123456789]             # ← Telegram ID'ingiz
```

**Telegram ID olish:** [@userinfobot](https://t.me/userinfobot) ga `/start` yuboring

### 3. Kutubxonalarni o'rnatish
```bash
pip install -r requirements.txt
```

### 4. Botni ishga tushirish
```bash
python bot.py
```

---

## 🎛 Admin funksiyalari

Admin ID'si sifatida ro'yxatdan o'tgan foydalanuvchi `/admin` buyrug'ini yuboradi:

| Funksiya | Tavsif |
|----------|--------|
| 📦 Barcha buyurtmalar | Faol buyurtmalarni ko'rish va holat yangilash |
| 🍽 Menyu boshqaruv | Mahsulot qo'shish / o'chirish |
| 📢 Xabar yuborish | Barcha foydalanuvchilarga ommaviy xabar |

---

## 👤 Foydalanuvchi funksiyalari

| Funksiya | Tavsif |
|----------|--------|
| 📋 Menyu | Kategoriyalar bo'yicha menyu |
| 🛒 Savatcha | Savat va buyurtma berish |
| 📦 Mening buyurtmalarim | Oxirgi buyurtmalar holati |
| 📍 Lokatsiya | Kafe xaritada manzili |
| ⏰ Ish vaqti | Ish kunlari va vaqti |
| 📞 Telefon | Bog'lanish raqami |
| 🎁 Aktsiyalar | Joriy chegirmalar |

---

## 🔧 Konfiguratsiya (config.py)

```python
CAFE_ADDRESS = "..."          # Kafe manzili
CAFE_PHONE = "+998 ..."       # Telefon raqam
CAFE_LOCATION_LAT = 41.xxx   # Kafe koordinatasi
CAFE_LOCATION_LON = 69.xxx   # Kafe koordinatasi
DELIVERY_PRICE = 10000        # Yetkazib berish narxi
MIN_ORDER_AMOUNT = 30000      # Minimal buyurtma
```

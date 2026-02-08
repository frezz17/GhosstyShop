# ============================================================
# 👻 GHOSTY SHOP BOT — FULL PRODUCTION CORE (STABLE)
# ============================================================

import os
import sys
import logging
import asyncio
import random
from datetime import datetime, timedelta
from html import escape
from uuid import uuid4

# --- ВАЖЛИВО ДЛЯ BOTHOST ---
try:
    import nest_asyncio
    nest_asyncio.apply()
except ImportError:
    pass 

try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
    from telegram.ext import (
        Application, CommandHandler, CallbackQueryHandler, 
        MessageHandler, ContextTypes, filters, PicklePersistence, 
        AIORateLimiter, Defaults
    )
    from telegram.constants import ParseMode
except ImportError:
    print("❌ Помилка: Бібліотека python-telegram-bot не встановлена!")
    sys.exit(1)

# ============================================================
# ⚙️ CONFIG (Твої дані)
# ============================================================

TOKEN = "8351638507:AAEqc9p9b4AA8vTrzvvj_XArtUABqcfMGV4" 
MANAGER_ID = 7544847872

DISCOUNT_MULTIPLIER = 0.65
PROMO_DISCOUNT = 45

VIP_FREE_DELIVERY_UNTIL = datetime.strptime("25.03.2026", "%d.%m.%Y")
BASE_VIP_DATE = datetime.strptime("25.03.2026", "%d.%m.%Y")

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# ============================================================
# 📝 LOGGING
# ============================================================

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# ============================================================
# 🌍 ТВОЇ ТОВАРИ ТА МІСТА (ЗБЕРЕЖЕНО ПОВНІСТЮ)
# ============================================================

CITIES = ["Київ", "Дніпро", "Камʼянське", "Харків", "Одеса", "Львів", "Запоріжжя", "Кривий Ріг", "Полтава", "Черкаси"]

CITY_DISTRICTS = {
    "Київ": ["Шевченківський", "Дарницький", "Оболонський", "Печерський", "Соломʼянський", "Деснянський", "Подільський", "Голосіївський"],
    "Дніпро": ["Центральний", "Соборний", "Індустріальний", "Самарський", "Амур", "Новокодацький", "Чечелівський"],
    "Камʼянське": ["Центр", "Соцмісто", "Черемушки", "Романкове", "БАМ"],
    "Харків": ["Шевченківський", "Київський", "Салтівський", "Основʼянський", "Холодногірський"],
    "Одеса": ["Приморський", "Київський", "Малиновський", "Суворовський"],
    "Львів": ["Галицький", "Франківський", "Сихівський", "Шевченківський"],
    "Запоріжжя": ["Олександрівський", "Дніпровський", "Комунарський", "Хортицький"],
    "Кривий Ріг": ["Центрально-Міський", "Покровський", "Саксаганський", "Тернівський"],
    "Полтава": ["Центр", "Поділ", "Алмазний", "Левада"],
    "Черкаси": ["Соснівський", "Придніпровський"]
}

GIFT_LIQUIDS = ["🎁 Pumpkin Latte 30ml", "🎁 Glintwine 30ml", "🎁 Christmas Tree 30ml", "🎁 Strawberry Jelly 30ml", "🎁 Mystery One 30ml", "🎁 Fall Tea 30ml"]

LIQUIDS = {
    301: {"name": "🎃 Pumpkin Latte", "series": "Ghost Liquid", "price": 269, "desc": "☕ Осінній гарбузовий латте\nКремовий, теплий, насичений.", "imgs": ["https://i.ibb.co/Y7qn69Ds/photo.jpg"], "colors": [], "gift_liquid": True},
    302: {"name": "🍷 Glintwine", "series": "Ghost Liquid", "price": 269, "desc": "🍇 Пряний глінтвейн\nЗігріваючий аромат спецій.", "imgs": ["https://i.ibb.co/wF8r7Nmc/photo.jpg"], "colors": [], "gift_liquid": True},
    303: {"name": "🌲 Christmas Tree", "series": "Ghost Liquid", "price": 269, "desc": "🌲 Морозна хвоя\nСвіжий зимовий профіль.", "imgs": ["https://i.ibb.co/vCPGV8RV/photo.jpg"], "colors": [], "gift_liquid": True},
    304: {"name": "🍓 Strawberry Jelly", "series": "Ghost Liquid", "price": 289, "desc": "🍓 Полуничний джем\nСолодкий десертний смак.", "imgs": ["https://i.ibb.co/2q3Qz8C/strawberry.jpg"], "colors": [], "gift_liquid": True}
}

HHC_VAPES = {
    100: {"name": "🌴 Packwoods Purple", "series": "Packwoods", "price": 549, "desc": "💨 90% HHC • Hybrid", "imgs": ["https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg"]},
    101: {"name": "🍊 Packwoods Orange", "series": "Packwoods", "price": 629, "desc": "🍊 Sativa", "imgs": ["https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg"]},
    102: {"name": "🌸 Packwoods Pink", "series": "Packwoods", "price": 719, "desc": "🌸 Hybrid", "imgs": ["https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg"]},
    103: {"name": "🌿 Whole Mint", "series": "Whole Melt", "price": 849, "desc": "🌿 Mint", "imgs": ["https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg"]},
    104: {"name": "🌙 Jungle Boys White", "series": "Jungle Boys", "price": 999, "desc": "🌙 Indica", "imgs": ["https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg"]}
}

PODS = {
    500: {"name": "🔌 XROS 3 Mini", "series": "Vaporesso", "price": 499, "desc": "🔋 1000 mAh", "colors": ["Black", "Sky Blue", "Rose Gold"]},
    501: {"name": "🔌 XROS 5 Mini", "series": "Vaporesso", "price": 579, "desc": "⚡ COREX 2.0", "colors": ["Black", "Green", "Silver"]},
    502: {"name": "🔌 XROS Pro", "series": "Vaporesso", "price": 689, "desc": "⚙️ Pro-рівень", "colors": ["Black", "Blue", "Red"]},
    503: {"name": "🔌 XROS Nano", "series": "Vaporesso", "price": 519, "desc": "📦 Компактний", "colors": ["Black", "Lime", "Pink"]}
}

# ============================================================
# 🧠 ЛОГІКА ТА ДОПОМІЖНІ ФУНКЦІЇ
# ============================================================

def get_item(pid):
    all_items = {**LIQUIDS, **HHC_VAPES, **PODS}
    return all_items.get(int(pid))

def calc_price(price, promo):
    shop = int(price * DISCOUNT_MULTIPLIER)
    final = int(shop * (1 - promo/100))
    return shop, final

def cart_text(cart, profile):
    if not cart: return "🛒 Кошик порожній"
    total = 0
    lines = ["🛒 <b>Твій кошик:</b>\n"]
    for row in cart:
        item = get_item(row["pid"])
        if item:
            _, final = calc_price(item["price"], profile["promo"])
            total += final
            lines.append(f"• {item['name']} — {final} грн")
    lines.append(f"\n💰 <b>Разом: {total} грн</b>")
    return "\n".join(lines)

# ============================================================
# 🕹 HANDLERS (ПОВНИЙ ФУНКЦІОНАЛ)
# ============================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if "profile" not in context.user_data:
        context.user_data["profile"] = {
            "uid": user.id, "name": user.first_name, "promo": PROMO_DISCOUNT, 
            "referrals": 0, "orders": [], "city": None, "district": None, "address": None
        }
    if "cart" not in context.user_data: context.user_data["cart"] = []
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🛍 Каталог", callback_data="catalog")],
        [InlineKeyboardButton("🛒 Кошик", callback_data="cart"), InlineKeyboardButton("👤 Профіль", callback_data="profile")],
        [InlineKeyboardButton("⚡ Швидке замовлення", callback_data="fast")]
    ])
    await update.message.reply_text("👻 <b>Ghosty Shop</b> вітає тебе!\nОбери категорію:", reply_markup=kb)

async def router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ОБРОБКА КНОПОК
    if update.callback_query:
        q = update.callback_query
        data = q.data
        prof = context.user_data.get("profile")

        if data == "catalog":
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("💧 Рідини", callback_data="cat_liq")],
                [InlineKeyboardButton("🔥 HHC", callback_data="cat_hhc")],
                [InlineKeyboardButton("🔌 POD-системи", callback_data="cat_pod")],
                [InlineKeyboardButton("⬅️ Назад", callback_data="back_main")]
            ])
            await q.message.edit_text("📂 Обери категорію:", reply_markup=kb)
        
        elif data.startswith("cat_"):
            cat = data.split("_")[1]
            items = {"liq": LIQUIDS, "hhc": HHC_VAPES, "pod": PODS}.get(cat)
            buttons = [[InlineKeyboardButton(it["name"], callback_data=f"view_{pid}")] for pid, it in items.items()]
            buttons.append([InlineKeyboardButton("⬅️ Назад", callback_data="catalog")])
            await q.message.edit_text("👇 Обирай товар:", reply_markup=InlineKeyboardMarkup(buttons))

        elif data.startswith("view_"):
            pid = int(data.split("_")[1])
            item = get_item(pid)
            shop, final = calc_price(item["price"], prof["promo"])
            text = f"<b>{item['name']}</b>\n\n💰 Ціна: {final} грн\n📝 {item['desc']}"
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("🛒 Додати", callback_data=f"add_{pid}")],
                [InlineKeyboardButton("⬅️ Назад", callback_data="catalog")]
            ])
            await q.message.edit_text(text, reply_markup=kb)

        elif data.startswith("add_"):
            pid = int(data.split("_")[1])
            context.user_data["cart"].append({"pid": pid})
            await q.answer("✅ Додано в кошик!")

        elif data == "cart":
            text = cart_text(context.user_data["cart"], prof)
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Оформити", callback_data="checkout")],
                [InlineKeyboardButton("🗑 Очистити", callback_data="cart_clear")],
                [InlineKeyboardButton("⬅️ Меню", callback_data="back_main")]
            ])
            await q.message.edit_text(text, reply_markup=kb)

        elif data == "checkout":
            rows = [[InlineKeyboardButton(c, callback_data=f"city_{c}")] for c in CITIES]
            await q.message.edit_text("🏙 Обери місто:", reply_markup=InlineKeyboardMarkup(rows))

        elif data.startswith("city_"):
            city = data.split("_")[1]
            context.user_data["temp_city"] = city
            districts = CITY_DISTRICTS.get(city, [])
            rows = [[InlineKeyboardButton(d, callback_data=f"dist_{d}")] for d in districts]
            await q.message.edit_text("🏘 Обери район:", reply_markup=InlineKeyboardMarkup(rows))

        elif data.startswith("dist_"):
            context.user_data["temp_district"] = data.split("_")[1]
            context.user_data["state"] = "wait_addr"
            await q.message.edit_text("✍️ Напиши адресу (Вулиця/НП):")

        elif data == "back_main":
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("🛍 Каталог", callback_data="catalog")],
                [InlineKeyboardButton("🛒 Кошик", callback_data="cart"), InlineKeyboardButton("👤 Профіль", callback_data="profile")],
                [InlineKeyboardButton("⚡ Швидке замовлення", callback_data="fast")]
            ])
            await q.message.edit_text("👻 Головне меню:", reply_markup=kb)

        await q.answer()

    # ОБРОБКА ТЕКСТУ
    elif update.message and update.message.text:
        state = context.user_data.get("state")
        if state == "wait_addr":
            addr = update.message.text
            prof = context.user_data["profile"]
            cart = context.user_data["cart"]
            order_msg = f"📦 <b>НОВЕ ЗАМОВЛЕННЯ</b>\n👤 @{update.effective_user.username}\n📍 {context.user_data['temp_city']}, {addr}\n\n{cart_text(cart, prof)}"
            await context.bot.send_message(MANAGER_ID, order_msg)
            await update.message.reply_text("✅ Замовлення прийнято! Менеджер зв'яжеться з тобою.")
            context.user_data["cart"] = []
            context.user_data["state"] = None

# ============================================================
# 🏁 СТАБІЛЬНИЙ ЗАПУСК
# ============================================================

def main():
    # Налаштування для уникнення Timeout
    persistence = PicklePersistence(filepath="data/bot_data.pickle")
    
    app = (
        Application.builder()
        .token(TOKEN)
        .persistence(persistence)
        .rate_limiter(AIORateLimiter())
        .defaults(Defaults(parse_mode=ParseMode.HTML))
        .connect_timeout(30)
        .read_timeout(30)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(router))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, router))
    app.add_handler(MessageHandler(filters.PHOTO, router)) # Для чеків

    print("🚀 БОТ ЗАПУЩЕНИЙ ТА ГОТОВИЙ ДО РОБОТИ")
    
    # Використовуємо стандартний polling, але з drop_pending_updates
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()

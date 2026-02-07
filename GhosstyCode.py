import os
import sys
import logging
import random
import asyncio
from html import escape
from datetime import datetime, timedelta

import telegram
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
    PicklePersistence
)
from telegram.error import BadRequest, NetworkError, TelegramError

# Створюємо папку для бази даних (важливо для збереження юзерів на хостингу)
os.makedirs('data', exist_ok=True)

# ===================== LOGGING =====================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ===================== CONFIG =====================
TOKEN = "8351638507:AAEqc9p9b4AA8vTrzvvj_XArtUABqcfMGV4" # Ваш токен
MANAGER_ID = 7544847872
MANAGER_USERNAME = "ghosstydpbot"
CHANNEL_URL = "https://t.me/GhostyStaffDP"
PAYMENT_LINK = "https://heylink.me/ghosstyshop/"
WELCOME_PHOTO = "https://i.ibb.co/y7Q194N/1770068775663.png"

DISCOUNT_MULTIPLIER = 0.65
PROMO_DISCOUNT = 45
BASE_VIP_DATE = datetime.strptime("25.03.2026", "%d.%m.%Y")

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# ===================== DATA: CITIES & DISTRICTS =====================
CITIES = ["Київ", "Дніпро", "Кам'янське", "Харків", "Одеса", "Львів", "Запоріжжя", "Кривий Ріг", "Полтава", "Черкаси"]

CITY_DISTRICTS = {
    "Київ": ["Шевченківський", "Дарницький", "Оболонський", "Печерський", "Солом'янський", "Деснянський", "Подільський", "Голосіївський"],
    "Дніпро": ["Центральний", "Соборний", "Індустріальний", "Амур", "Новокодацький", "Чечелівський", "Самарський", "Доставка на адресу"],
    "Кам'янське": ["Центральний", "Південний", "Заводський", "Дніпровський", "Черемушки", "Романкове", "БАМ", "Соцмісто"],
    "Харків": ["Київський", "Салтівський", "Холодногірський", "Індустріальний", "Основ'янський", "Немишлянський", "Новобаварський", "Шевченківський"],
    "Одеса": ["Приморський", "Київський", "Малиновський", "Суворовський", "Пересипський", "Хаджибейський", "Таїровський", "Люстдорфський"],
    "Львів": ["Залізничний", "Личаківський", "Франківський", "Шевченківський", "Сихівський", "Галицький", "Королівський", "Новий"],
    "Запоріжжя": ["Олександрівський", "Заводський", "Комунарський", "Дніпровський", "Вознесенівський", "Шевченківський", "Хортицький", "Центральний"],
    "Кривий Ріг": ["Довгинцівський", "Інгулецький", "Металургійний", "Покровський", "Саксаганський", "Тернівський", "Центрально-Міський"],
    "Полтава": ["Шевченківський", "Подільський", "Київський", "Залізничний", "Октябрський", "Ленінський", "Центральний", "Новосанжарський"],
    "Черкаси": ["Придніпровський", "Соснівський", "Смілянський", "Канівський", "Золотоніський", "Уманський", "Звенигородський", "Городищенський"]
}

# ===================== DATA: PRODUCTS =====================
LIQUIDS = {
    301: {"name": "🎃 Pumpkin Latte", "price": 269, "discount": True, "img": "https://i.ibb.co/Y7qn69Ds/photo-2024-12-18-00-00-00.jpg", "desc": "☕ Гарбузовий латте з корицею"},
    302: {"name": "🍷 Glintwine", "price": 269, "discount": True, "img": "https://i.ibb.co/wF8r7Nmc/photo-2024-12-18-00-00-01.jpg", "desc": "🍇 Пряний глінтвейн"},
    303: {"name": "🎄 Christmas Tree", "price": 269, "discount": True, "img": "https://i.ibb.co/vCPGV8RV/photo-2024-12-18-00-00-02.jpg", "desc": "🌲 Хвоя + морозна свіжість"}
}

HHC_VAPES = {
    100: {"name": "🌴 Packwoods Purple 1ml", "price": 549, "discount": True, "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg", "desc": "🧠 90% ННС | Гібрид"},
    101: {"name": "🍊 Packwoods Orange 1ml", "price": 629, "discount": True, "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg", "desc": "🧠 90% ННС | Бадьорить"},
    102: {"name": "🌸 Packwoods Pink 1ml", "price": 719, "discount": True, "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg", "desc": "🧠 90% ННС | Спокій"},
    103: {"name": "🌿 Whole Mint 2ml", "price": 849, "discount": True, "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg", "desc": "🧠 95% ННС | Сатіва"},
    104: {"name": "🌴 Jungle Boys White 2ml", "price": 999, "discount": True, "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg", "desc": "🧠 95% ННС | Індика"}
}

PODS = {
    500: {"name": "🔌 XROS 3 Mini", "price": 499, "img": "https://i.ibb.co/yFSQ5QSn/vaporesso-xros-3-mini.jpg"},
    501: {"name": "🔌 XROS 5 Mini", "price": 579, "img": "https://i.ibb.co/RkNgt1Qr/vaporesso-xros-5-mini.jpg"},
    502: {"name": "🔌 XROS Pro", "price": 689, "img": "https://i.ibb.co/ynYwSMt6/vaporesso-xros-pro.jpg"},
    503: {"name": "🔌 XROS Nano", "price": 519, "img": "https://i.ibb.co/5XW2yN80/vaporesso-xros-nano.jpg"},
    504: {"name": "🔌 XROS 4", "price": 599, "img": "https://i.ibb.co/LDRbQxr1/vaporesso-xros-4.jpg"},
    505: {"name": "🔌 XROS 5", "price": 799, "img": "https://i.ibb.co/hxjmpHF2/vaporesso-xros-5.jpg"},
    506: {"name": "🔌 Voopoo Vmate Mini", "price": 459, "img": "https://i.ibb.co/8L0JNTHz/voopoo-vmate-mini.jpg"}
}

# ===================== HELPERS =====================
def get_vip_date(profile):
    base = profile.get("vip_base", BASE_VIP_DATE)
    if isinstance(base, str): base = datetime.strptime(base, "%d.%m.%Y")
    return base + timedelta(days=7 * profile.get("referrals", 0))

def calc_p(item, discount):
    b = item['price']
    d = int(b * DISCOUNT_MULTIPLIER)
    f = int(d * (1 - discount/100))
    return b, d, f

# ===================== HANDLERS =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    if "profile" not in context.user_data:
        context.user_data["profile"] = {
            "uid": u.id, "full_name": u.first_name, "username": u.username,
            "city": None, "district": None, "address": None, "phone": None,
            "referrals": 0, "vip_base": BASE_VIP_DATE, "promo_code": f"GH-{u.id % 10000}"
        }
        context.user_data["cart"] = []
    
    p = context.user_data["profile"]
    v_date = get_vip_date(p).strftime("%d.%m.%Y")
    text = f"👋 Вітаємо, <b>{escape(u.first_name)}</b>!\n🎫 Промокод: <code>{p['promo_code']}</code>\n👑 VIP до: {v_date}"
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("👤 Профіль", callback_data="prof"), InlineKeyboardButton("🛍 Асортимент", callback_data="cat")],
        [InlineKeyboardButton("🛒 Кошик", callback_data="cart"), InlineKeyboardButton("👨‍💻 Менеджер", url=f"https://t.me/{MANAGER_USERNAME}")]
    ])
    
    if update.message: await update.message.reply_photo(WELCOME_PHOTO, caption=text, parse_mode="HTML", reply_markup=kb)
    else: await update.callback_query.edit_message_caption(caption=text, parse_mode="HTML", reply_markup=kb)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    d = q.data
    await q.answer()
    
    if d == "prof":
        p = context.user_data["profile"]
        v = get_vip_date(p).strftime("%d.%m.%Y")
        txt = f"👤 <b>Профіль</b>\n\nМісто: {p['city'] or 'Не вказано'}\nАдреса: {p['address'] or '—'}\nVIP: {v}"
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("📍 Змінити місто", callback_data="set_city")], [InlineKeyboardButton("⬅️ Назад", callback_data="main")]])
        await q.edit_message_caption(caption=txt, parse_mode="HTML", reply_markup=kb)
        
    elif d == "main": await start(update, context)
    
    elif d == "cat":
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💧 Рідини", callback_data="list_300"), InlineKeyboardButton("🔌 POD-системи", callback_data="list_500")],
            [InlineKeyboardButton("💨 HHC", callback_data="list_100"), InlineKeyboardButton("🏠 Меню", callback_data="main")]
        ])
        await q.edit_message_caption(caption="🛍 Оберіть категорію:", reply_markup=kb)

    elif d.startswith("list_"):
        cid = int(d.split("_")[1])
        items = LIQUIDS if cid == 300 else (PODS if cid == 500 else HHC_VAPES)
        btns = [[InlineKeyboardButton(f"{v['name']} - {v['price']}грн", callback_data=f"view_{k}")] for k, v in items.items()]
        btns.append([InlineKeyboardButton("⬅️ Назад", callback_data="cat")])
        await q.edit_message_caption(caption="📦 Оберіть товар:", reply_markup=InlineKeyboardMarkup(btns))

    elif d.startswith("view_"):
        pid = int(d.split("_")[1])
        all_i = {**LIQUIDS, **HHC_VAPES, **PODS}
        item = all_i[pid]
        b, d_p, f = calc_p(item, PROMO_DISCOUNT)
        cap = f"<b>{item['name']}</b>\n\nЦіна: <s>{b}</s> -> <b>{d_p} грн</b>\nЗ промокодом: <b>{f} грн</b>"
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("🛒 Додати в кошик", callback_data=f"add_{pid}")], [InlineKeyboardButton("⬅️ Назад", callback_data="cat")]])
        await q.message.reply_photo(item['img'], caption=cap, parse_mode="HTML", reply_markup=kb)
        await q.message.delete()

    elif d.startswith("add_"):
        pid = int(d.split("_")[1])
        all_i = {**LIQUIDS, **HHC_VAPES, **PODS}
        context.user_data["cart"].append(all_i[pid])
        await q.answer("✅ Додано!")

    elif d == "cart":
        cart = context.user_data.get("cart", [])
        if not cart: return await q.answer("Кошик порожній!", show_alert=True)
        txt = "🛒 <b>Кошик:</b>\n\n" + "\n".join([f"- {i['name']}" for i in cart])
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("✅ Оформити", callback_data="checkout")], [InlineKeyboardButton("🗑 Очистити", callback_data="clear")]])
        if q.message.photo: await q.message.reply_text(txt, parse_mode="HTML", reply_markup=kb); await q.message.delete()
        else: await q.edit_message_text(txt, parse_mode="HTML", reply_markup=kb)

    elif d == "checkout":
        btns = [[InlineKeyboardButton(c, callback_data=f"city_{c}")] for c in CITIES]
        await q.edit_message_text("📍 Оберіть місто доставки:", reply_markup=InlineKeyboardMarkup(btns))

    elif d.startswith("city_"):
        city = d.split("_")[1]
        context.user_data["profile"]["city"] = city
        districts = CITY_DISTRICTS.get(city, ["Центр"])
        btns = [[InlineKeyboardButton(dist, callback_data=f"dist_{dist}")] for dist in districts]
        await q.edit_message_text(f"🏙 {city}. Оберіть район:", reply_markup=InlineKeyboardMarkup(btns))

    elif d.startswith("dist_"):
        context.user_data["profile"]["district"] = d.split("_")[1]
        context.user_data["state"] = "wait_addr"
        await q.edit_message_text("✍️ Введіть адресу (вулиця, будинок):")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = context.user_data.get("state")
    if state == "wait_addr":
        context.user_data["profile"]["address"] = update.message.text
        context.user_data["state"] = "wait_phone"
        await update.message.reply_text("📞 Введіть номер телефону:")
    elif state == "wait_phone":
        context.user_data["profile"]["phone"] = update.message.text
        context.user_data["state"] = None
        txt = f"📦 <b>Замовлення сформовано!</b>\nСума: {sum([i['price'] for i in context.user_data['cart']])} грн\n\nОплатіть за посиланням:"
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("💳 Оплатити", url=PAYMENT_LINK)], [InlineKeyboardButton("🏠 Меню", callback_data="main")]])
        await update.message.reply_text(txt, parse_mode="HTML", reply_markup=kb)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Чек отримано! Менеджер перевірить оплату протягом 15 хвилин.")
    await context.bot.send_photo(MANAGER_ID, update.message.photo[-1].file_id, caption=f"💰 Чек від @{update.effective_user.username}")

def main():
    pers = PicklePersistence(filepath="data/bot_data.pickle")
    app = Application.builder().token(TOKEN).persistence(pers).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    print("🤖 Ghosty Shop Bot запрацював!")
    app.run_polling()

if __name__ == "__main__":
    main()

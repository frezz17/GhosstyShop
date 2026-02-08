import logging
import os
import sys
import random
import asyncio
import warnings
from datetime import datetime, timedelta
from html import escape
from uuid import uuid4

from telegram import (
    Update, 
    InlineKeyboardButton, 
    InlineKeyboardMarkup, 
    InputMediaPhoto
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
    PicklePersistence,
    AIORateLimiter,
    Defaults
)
from telegram.constants import ParseMode
from telegram.error import NetworkError, BadRequest, TimedOut

# ==========================================
# ⚙️ НАЛАШТУВАННЯ КОНФІГУРАЦІЇ
# ==========================================

TOKEN = "8351638507:AAEqc9p9b4AA8vTrzvvj_XArtUABqcfMGV4"
MANAGER_ID = 7544847872  # Куди будуть приходити звіти
CHANNEL_URL = "https://t.me/GhostyStaffDP"
PAYMENT_LINK = "https://heylink.me/ghosstyshop/"
WELCOME_PHOTO = "https://i.ibb.co/y7Q194N/1770068775663.png"

# Економіка
DISCOUNT_MULTIPLIER = 0.65   # Базова націнка/знижка
PROMO_DISCOUNT_PERCENT = 45  # Додаткова знижка по промокоду
VIP_BASE_DATE = datetime.strptime("25.03.2026", "%d.%m.%Y")

# ==========================================
# 📝 ЛОГУВАННЯ (Щоб бачити помилки в консолі)
# ==========================================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Ігноруємо незначні попередження бібліотеки
warnings.filterwarnings("ignore", category=UserWarning)

# ==========================================
# 📦 БАЗА ДАНИХ ТОВАРІВ
# ==========================================

GIFT_LIQUIDS = {
    9001: "🎁 Pumpkin Latte 30ml",
    9002: "🎁 Glintwine 30ml",
    9003: "🎁 Christmas Tree 30ml",
    9004: "🎁 Strawberry Jelly 30ml",
    9005: "🎁 Mystery One 30ml",
    9006: "🎁 Fall Tea 30ml",
}

# --- КАТЕГОРІЯ 1: РІДИНИ ---
LIQUIDS = {
    301: {
        "name": "🎃 Pumpkin Latte", 
        "price": 269, 
        "img": "https://i.ibb.co/Y7qn69Ds/photo-2024-12-18-00-00-00.jpg", 
        "desc": "☕ Гарбузовий латте з корицею\n🎄 Зимовий настрій\n😌 Мʼякий та теплий смак"
    },
    302: {
        "name": "🍷 Glintwine", 
        "price": 269, 
        "img": "https://i.ibb.co/wF8r7Nmc/photo-2024-12-18-00-00-01.jpg", 
        "desc": "🍇 Пряний глінтвейн\n🔥 Теплий винний смак\n🎄 Святковий вайб"
    },
    303: {
        "name": "🎄 Christmas Tree", 
        "price": 269, 
        "img": "https://i.ibb.co/vCPGV8RV/photo-2024-12-18-00-00-02.jpg", 
        "desc": "🌲 Хвоя + морозна свіжість\n❄️ Дуже свіжа\n🎅 Атмосфера зими"
    }
}

# --- КАТЕГОРІЯ 2: POD СИСТЕМИ ---
PODS = {
    500: {"name": "🔌 XROS 3 Mini", "price": 499, "img": "https://i.ibb.co/yFSQ5QSn/vaporesso-xros-3-mini.jpg", "desc": "🔋 1000 mAh | MTL/RDL"},
    501: {"name": "🔌 XROS 5 Mini", "price": 579, "img": "https://i.ibb.co/RkNgt1Qr/vaporesso-xros-5-mini.jpg", "desc": "🔋 1000 mAh | COREX 2.0"},
    502: {"name": "🔌 XROS Pro", "price": 689, "img": "https://i.ibb.co/ynYwSMt6/vaporesso-xros-pro.jpg", "desc": "🔋 1200 mAh | Pro Series"},
    503: {"name": "🔌 XROS Nano", "price": 519, "img": "https://i.ibb.co/5XW2yN80/vaporesso-xros-nano.jpg", "desc": "🔋 1000 mAh | Стильний квадрат"},
    504: {"name": "🔌 XROS 4", "price": 599, "img": "https://i.ibb.co/LDRbQxr1/vaporesso-xros-4.jpg", "desc": "🔋 1000 mAh | Новинка"},
    505: {"name": "🔌 XROS 5", "price": 799, "img": "https://i.ibb.co/hxjmpHF2/vaporesso-xros-5.jpg", "desc": "🔋 1200 mAh | Флагман"},
    506: {"name": "🔌 Voopoo Vmate", "price": 459, "img": "https://i.ibb.co/8L0JNTHz/voopoo-vmate-mini.jpg", "desc": "🔋 900 mAh | Бюджетний топ"}
}

# --- КАТЕГОРІЯ 3: HHC / VAPES ---
HHC_VAPES = {
    100: {"name": "🌴 Packwoods Purple", "price": 549, "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg", "desc": "🧠 90% HHC | Hybrid"},
    101: {"name": "🍊 Packwoods Orange", "price": 629, "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg", "desc": "🧠 90% HHC | Sativa"},
    102: {"name": "🌸 Packwoods Pink", "price": 719, "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg", "desc": "🧠 90% HHC | Indica"},
    103: {"name": "🌿 Whole Mint", "price": 849, "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg", "desc": "🧠 95% HHC | Super Strong"},
    104: {"name": "🌴 Jungle Boys", "price": 999, "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg", "desc": "🧠 95% HHC | Exclusive"}
}

# --- ГЕОГРАФІЯ ---
CITIES = ["Київ", "Дніпро", "Камʼянське", "Харків", "Одеса", "Львів", "Запоріжжя", "Кривий Ріг", "Полтава", "Черкаси"]

CITY_DISTRICTS = {
    "Київ": ["Шевченківський", "Дарницький", "Оболонський", "Печерський", "Соломʼянський", "Деснянський", "Подільський", "Голосіївський"],
    "Дніпро": ["Центральний", "Соборний", "Індустріальний", "Амур", "Новокодацький", "Чечелівський", "Самарський", "Шевченківський"],
    "Камʼянське": ["Центральний", "Південний", "Заводський", "Дніпровський", "Черемушки", "Романкове", "БАМ", "Соцмісто"],
    "Харків": ["Київський", "Салтівський", "Холодногірський", "Індустріальний", "Основʼянський", "Немишлянський", "Новобаварський"],
    "Одеса": ["Приморський", "Київський", "Малиновський", "Суворовський", "Пересипський", "Хаджибейський"],
    "Львів": ["Залізничний", "Личаківський", "Франківський", "Шевченківський", "Сихівський", "Галицький"],
    "Запоріжжя": ["Олександрівський", "Заводський", "Комунарський", "Дніпровський", "Вознесенівський"],
    "Кривий Ріг": ["Довгинцівський", "Інгулецький", "Металургійний", "Покровський", "Саксаганський"],
    "Полтава": ["Шевченківський", "Подільський", "Київський"],
    "Черкаси": ["Придніпровський", "Соснівський"]
}

# ==========================================
# 🧠 ЛОГІКА ТА ДОПОМІЖНІ ФУНКЦІЇ
# ==========================================

def get_vip_date(profile):
    """Розрахунок дати закінчення VIP"""
    base = profile.get("vip_base", BASE_VIP_DATE)
    if isinstance(base, str):
        base = datetime.strptime(base, "%d.%m.%Y")
    extra_days = 7 * profile.get("referrals", 0)
    return base + timedelta(days=extra_days)

def is_vip_active(profile):
    """Перевірка чи активний VIP"""
    return get_vip_date(profile) > datetime.now()

def generate_promo_code(user_id):
    """Генерація унікального промокоду"""
    return f"GHOST-{user_id % 10000}{random.randint(100,999)}"

def calculate_price(item_price, profile):
    """Розрахунок трьох цін: Базова -> Магазин -> VIP"""
    # 1. Ціна магазину (звичайна знижка)
    shop_price = int(item_price * DISCOUNT_MULTIPLIER)
    
    # 2. Персональна VIP ціна
    promo_percent = profile.get("promo_discount", PROMO_DISCOUNT_PERCENT)
    final_price = int(shop_price * (1 - promo_percent / 100))
    
    return {
        "base": item_price,
        "shop": shop_price,
        "final": final_price
    }

def get_item_by_id(item_id):
    """Пошук товару в усіх категоріях"""
    return LIQUIDS.get(item_id) or PODS.get(item_id) or HHC_VAPES.get(item_id)

# ==========================================
# ⌨️ КЛАВІАТУРИ (UI)
# ==========================================

def get_main_menu_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👤 Мій Профіль", callback_data="profile"), InlineKeyboardButton("🛍 Каталог", callback_data="catalog")],
        [InlineKeyboardButton("📍 Налаштування доставки", callback_data="set_city"), InlineKeyboardButton("🛒 Кошик", callback_data="cart")],
        [InlineKeyboardButton("📦 Мої замовлення", callback_data="history"), InlineKeyboardButton("👨‍💻 Підтримка", url=f"https://t.me/ghosstydpbot")],
        [InlineKeyboardButton("📢 Наш канал", url=CHANNEL_URL)]
    ])

def get_back_kb():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 В головне меню", callback_data="main_menu")]])

# ==========================================
# 🎮 ОБРОБНИКИ (HANDLERS)
# ==========================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Точка входу. Створює профіль та обробляє рефералів."""
    user = update.effective_user
    args = context.args

    # Ініціалізація даних користувача
    if "profile" not in context.user_data:
        context.user_data["profile"] = {
            "uid": user.id,
            "full_name": user.first_name,
            "username": user.username,
            "city": None, 
            "district": None, 
            "address": None, 
            "phone": None,
            "promo_code": generate_promo_code(user.id),
            "promo_discount": PROMO_DISCOUNT_PERCENT,
            "referrals": 0,
            "vip_base": BASE_VIP_DATE,
            "ref_applied": False
        }
        context.user_data["cart"] = []
        context.user_data["orders"] = []

    profile = context.user_data["profile"]

    # Обробка реферального посилання
    if args and not profile.get("ref_applied"):
        try:
            referrer_id = int(args[0])
            if referrer_id != user.id:
                profile["ref_applied"] = True
                profile["referrals"] += 1
                # Спроба повідомити запросившого (може не спрацювати, якщо немає контексту, але це ок)
                try:
                    await context.bot.send_message(chat_id=referrer_id, text=f"🎉 У вас новий реферал: {user.first_name}! +7 днів VIP.")
                except:
                    pass
        except ValueError:
            pass

    # Вітальний текст
    vip_end = get_vip_date(profile).strftime("%d.%m.%Y")
    is_vip = is_vip_active(profile)
    delivery_status = "Безкоштовна (VIP)" if is_vip else "За тарифами пошти"

    text = (
        f"👋 Привіт, <b>{escape(user.first_name)}</b>!\n"
        f"Ласкаво просимо до <b>Ghosty Shop</b> 💨\n\n"
        f"🎫 Твій код: <code>{profile['promo_code']}</code>\n"
        f"💎 Твоя знижка: <b>-{profile['promo_discount']}%</b>\n"
        f"👑 VIP статус до: <b>{vip_end}</b>\n"
        f"🚚 Доставка: <b>{delivery_status}</b>\n\n"
        f"👇 Головне меню:"
    )

    # Відправка або редагування
    if update.callback_query:
        # Щоб уникнути мерехтіння, видаляємо старе і шлемо нове фото
        await update.callback_query.message.delete()
    
    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=WELCOME_PHOTO,
        caption=text,
        parse_mode=ParseMode.HTML,
        reply_markup=get_main_menu_kb()
    )

# --- ПРОФІЛЬ ---
async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    p = context.user_data["profile"]
    vip_end = get_vip_date(p).strftime("%d.%m.%Y")
    ref_link = f"https://t.me/{context.bot.username}?start={p['uid']}"
    
    text = (
        f"👤 <b>Особистий кабінет</b>\n\n"
        f"🏙 Місто: {p['city'] or '❌ Не вказано'}\n"
        f"📍 Район: {p['district'] or '❌ Не вказано'}\n"
        f"🏠 Адреса: {p['address'] or '❌ Не вказано'}\n"
        f"📞 Телефон: {p['phone'] or '❌ Не вказано'}\n\n"
        f"👥 Приведено друзів: <b>{p['referrals']}</b>\n"
        f"🔗 <b>Твоє посилання (тисни щоб скопіювати):</b>\n<code>{ref_link}</code>\n\n"
        f"🗓 VIP активний до: <b>{vip_end}</b>"
    )
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✏️ Змінити дані доставки", callback_data="set_city")],
        [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]
    ])
    
    await query.message.delete()
    await query.message.chat.send_message(text, parse_mode=ParseMode.HTML, reply_markup=kb)

# --- КАТАЛОГ ---
async def show_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("💧 Premium Liquids", callback_data="cat_300")],
        [InlineKeyboardButton("🔌 POD Systems", callback_data="cat_500")],
        [InlineKeyboardButton("💨 HHC / NNS Vapes", callback_data="cat_100")],
        [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]
    ])
    
    await query.message.delete()
    await query.message.chat.send_message("📂 <b>Оберіть категорію товарів:</b>", parse_mode=ParseMode.HTML, reply_markup=kb)

async def show_items(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    cat_id = int(query.data.split("_")[1])
    
    if cat_id == 300:
        items, title = LIQUIDS, "💧 Рідини"
    elif cat_id == 500:
        items, title = PODS, "🔌 POD-системи"
    else:
        items, title = HHC_VAPES, "💨 HHC Вейпи"
        
    buttons = []
    for pid, data in items.items():
        # Додаємо ціну прямо на кнопку
        profile = context.user_data["profile"]
        prices = calculate_price(data['price'], profile)
        btn_text = f"{data['name']} | {prices['final']} грн"
        buttons.append([InlineKeyboardButton(btn_text, callback_data=f"prod_{pid}")])
        
    buttons.append([InlineKeyboardButton("🔙 Назад", callback_data="catalog")])
    
    await query.message.delete()
    await query.message.chat.send_message(f"<b>{title}</b>\nОберіть товар:", parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(buttons))

async def show_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    prod_id = int(query.data.split("_")[1])
    item = get_item_by_id(prod_id)
    
    if not item:
        await query.answer("Товар не знайдено!", show_alert=True)
        return

    profile = context.user_data["profile"]
    prices = calculate_price(item['price'], profile)
    
    caption = (
        f"✨ <b>{item['name']}</b>\n\n"
        f"{item['desc']}\n\n"
        f"❌ Ціна вітрини: <s>{prices['base']} грн</s>\n"
        f"📉 Ціна зі знижкою: <s>{prices['shop']} грн</s>\n"
        f"✅ <b>ТВОЯ ЦІНА: {prices['final']} грн</b>\n\n"
        f"🎁 <b>Бонус:</b> 3 рідини у подарунок!"
    )
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🛒 Додати в кошик", callback_data=f"add_{prod_id}")],
        [InlineKeyboardButton("🔙 До списку", callback_data="catalog")]
    ])
    
    await query.message.delete()
    await query.message.chat.send_photo(photo=item["img"], caption=caption, parse_mode=ParseMode.HTML, reply_markup=kb)

# --- КОШИК ---
async def add_to_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    prod_id = int(query.data.split("_")[1])
    item = get_item_by_id(prod_id)
    
    profile = context.user_data["profile"]
    prices = calculate_price(item['price'], profile)
    
    context.user_data["cart"].append({
        "id": prod_id,
        "name": item["name"],
        "price": prices['final']
    })
    
    await query.answer("✅ Додано в кошик!", show_alert=False)

async def show_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    cart = context.user_data.get("cart", [])
    
    if not cart:
        await query.answer("Кошик порожній 🕸", show_alert=True)
        return

    total = sum(i['price'] for i in cart)
    text = "🛒 <b>ВАШ КОШИК:</b>\n\n"
    
    for idx, item in enumerate(cart, 1):
        text += f"▫️ {idx}. {item['name']} — <b>{item['price']} грн</b>\n"
        
    text += f"\n💰 <b>ЗАГАЛОМ: {total} грн</b>"
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ ОФОРМИТИ ЗАМОВЛЕННЯ", callback_data="checkout_start")],
        [InlineKeyboardButton("🗑 Очистити все", callback_data="clear_cart")],
        [InlineKeyboardButton("🔙 Меню", callback_data="main_menu")]
    ])
    
    await query.message.delete()
    await query.message.chat.send_message(text, parse_mode=ParseMode.HTML, reply_markup=kb)

async def clear_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["cart"] = []
    await update.callback_query.answer("Кошик очищено 🗑")
    await start(update, context)

# --- CHECKOUT FLOW (ОФОРМЛЕННЯ) ---

async def checkout_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Початок оформлення або налаштування міста"""
    query = update.callback_query
    await query.answer()
    
    # Генерація клавіатури міст (по 2 в ряд)
    buttons = []
    row = []
    for city in CITIES:
        row.append(InlineKeyboardButton(city, callback_data=f"setcity_{city}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row: buttons.append(row)
    buttons.append([InlineKeyboardButton("❌ Скасувати", callback_data="main_menu")])
    
    await query.message.delete()
    await query.message.chat.send_message("📍 <b>Крок 1:</b> Оберіть ваше місто доставки:", parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(buttons))

async def checkout_district(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    city_name = query.data.split("_")[1]
    context.user_data["profile"]["city"] = city_name
    
    districts = CITY_DISTRICTS.get(city_name, ["Центр", "Інший"])
    
    # Клавіатура районів
    buttons = []
    row = []
    for d in districts:
        row.append(InlineKeyboardButton(d, callback_data=f"setdist_{d}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row: buttons.append(row)
    buttons.append([InlineKeyboardButton("🔙 Назад", callback_data="checkout_start")])
    
    await query.message.delete()
    await query.message.chat.send_message(f"📍 Місто: <b>{city_name}</b>\n👇 Оберіть район:", parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(buttons))

async def checkout_address_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    dist_name = query.data.split("_")[1]
    context.user_data["profile"]["district"] = dist_name
    
    # Встановлюємо стан для очікування тексту
    context.user_data["input_state"] = "awaiting_address"
    
    await query.message.delete()
    await query.message.chat.send_message(
        f"📝 <b>Введіть адресу доставки:</b>\n"
        f"(Вулиця, будинок, квартира або номер відділення НП)",
        parse_mode=ParseMode.HTML
    )

# --- TEXT INPUT HANDLER (Універсальний) ---
async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = context.user_data.get("input_state")
    if not state:
        return # Не реагуємо на звичайний текст без стану

    text = update.message.text
    profile = context.user_data["profile"]
    
    if state == "awaiting_address":
        profile["address"] = text
        context.user_data["input_state"] = "awaiting_phone"
        await update.message.reply_text("📞 <b>Введіть ваш номер телефону:</b>\n(Приклад: 0931234567)", parse_mode=ParseMode.HTML)
    
    elif state == "awaiting_phone":
        profile["phone"] = text
        context.user_data["input_state"] = "awaiting_payment" # Готові приймати чек
        await checkout_final_invoice(update, context)

async def checkout_final_invoice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cart = context.user_data.get("cart", [])
    profile = context.user_data["profile"]
    total = sum(i['price'] for i in cart)
    
    # Якщо кошик пустий (наприклад, просто змінювали налаштування), повертаємо в меню
    if not cart:
        context.user_data["input_state"] = None
        await update.message.reply_text("✅ Дані збережено!", reply_markup=get_back_kb())
        return

    order_id = str(uuid4())[:8].upper()
    context.user_data["current_order"] = {
        "id": order_id,
        "total": total,
        "items": cart.copy(),
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    
    msg_text = (
        f"✅ <b>Замовлення сформовано!</b>\n"
        f"🆔 Номер: <code>{order_id}</code>\n\n"
        f"👤 {profile['full_name']}\n"
        f"📞 {profile['phone']}\n"
        f"📍 {profile['city']}, {profile['district']}\n"
        f"🏠 {profile['address']}\n\n"
        f"💳 <b>ДО СПЛАТИ: {total} грн</b>\n"
        f"🔗 <b><a href='{PAYMENT_LINK}'>НАТИСНІТЬ ТУТ ДЛЯ ОПЛАТИ</a></b>\n\n"
        f"⚠️ <b>Після оплати надішліть сюди скріншот квитанції!</b>"
    )
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 ОПЛАТИТИ", url=PAYMENT_LINK)],
        [InlineKeyboardButton("❌ Скасувати", callback_data="main_menu")]
    ])
    
    await update.message.reply_text(msg_text, parse_mode=ParseMode.HTML, disable_web_page_preview=True, reply_markup=kb)

# --- ОБРОБКА ФОТО (ЧЕКІВ) ---
async def handle_receipt_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = context.user_data.get("input_state")
    
    # Якщо ми не чекаємо оплату - ігноруємо (або можна відповідати "Я не розумію")
    if state != "awaiting_payment":
        return

    photo = update.message.photo[-1]
    order_data = context.user_data.get("current_order")
    profile = context.user_data["profile"]
    
    if not order_data:
        await update.message.reply_text("Помилка замовлення. Спробуйте оформити заново.")
        return

    # 1. Зберігаємо в історію
    order_data["status"] = "На перевірці"
    context.user_data["orders"].append(order_data)
    
    # 2. Формуємо звіт менеджеру
    items_list = "\n".join([f"- {i['name']} ({i['price']} грн)" for i in order_data['items']])
    is_vip = is_vip_active(profile)
    
    manager_report = (
        f"💰 <b>НОВЕ ЗАМОВЛЕННЯ!</b>\n"
        f"🆔 <code>{order_data['id']}</code>\n"
        f"👤 @{profile['username']} | {profile['full_name']}\n"
        f"📞 <code>{profile['phone']}</code>\n"
        f"📍 {profile['city']}, {profile['district']}\n"
        f"🏠 {profile['address']}\n\n"
        f"🛒 <b>Товари:</b>\n{items_list}\n\n"
        f"💎 VIP: {'ТАК' if is_vip else 'НІ'}\n"
        f"💵 <b>СУМА: {order_data['total']} грн</b>"
    )
    
    try:
        await context.bot.send_photo(
            chat_id=MANAGER_ID,
            photo=photo.file_id,
            caption=manager_report,
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        logger.error(f"Failed to send to manager: {e}")

    # 3. Очищуємо стан
    context.user_data["cart"] = []
    context.user_data["input_state"] = None
    context.user_data["current_order"] = None
    
    await update.message.reply_text(
        "✅ <b>Оплата отримана!</b>\n\n"
        "Менеджер перевірить платіж протягом 15 хвилин.\n"
        "Дякуємо, що обираєте Ghosty Shop! 👻",
        parse_mode=ParseMode.HTML,
        reply_markup=get_back_kb()
    )

# --- ІСТОРІЯ ---
async def show_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    orders = context.user_data.get("orders", [])
    if not orders:
        await query.message.delete()
        await query.message.chat.send_message("📭 Історія замовлень порожня.", reply_markup=get_back_kb())
        return

    text = "📦 <b>ІСТОРІЯ ЗАМОВЛЕНЬ:</b>\n\n"
    # Показуємо останні 5
    for o in orders[-5:]:
        text += f"🔹 <b>{o['date']}</b> | ID: {o['id']}\n💰 {o['total']} грн | Статус: {o['status']}\n\n"
        
    await query.message.delete()
    await query.message.chat.send_message(text, parse_mode=ParseMode.HTML, reply_markup=get_back_kb())

# ==========================================
# 📡 ГОЛОВНИЙ РОУТЕР (CALLBACKS)
# ==========================================

async def router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = update.callback_query.data
    
    # Головне меню
    if data == "main_menu":
        await start(update, context)
    
    # Профіль
    elif data == "profile":
        await show_profile(update, context)
    
    # Каталог
    elif data == "catalog":
        await show_categories(update, context)
    elif data.startswith("cat_"):
        await show_items(update, context)
    elif data.startswith("prod_"):
        await show_product(update, context)
    
    # Кошик
    elif data.startswith("add_"):
        await add_to_cart(update, context)
    elif data == "cart":
        await show_cart(update, context)
    elif data == "clear_cart":
        await clear_cart(update, context)
    
    # Оформлення
    elif data == "checkout_start" or data == "set_city":
        await checkout_start(update, context)
    elif data.startswith("setcity_"):
        await checkout_district(update, context)
    elif data.startswith("setdist_"):
        await checkout_address_prompt(update, context)
        
    # Історія
    elif data == "history":
        await show_history(update, context)

# ==========================================
# 🚀 ЗАПУСК ДОДАТКУ
# ==========================================

def main():
    # 1. Створюємо директорію для даних (щоб не було помилок на сервері)
    if not os.path.exists('data'):
        os.makedirs('data', exist_ok=True)

    # 2. Налаштування збереження (Persistence)
    # Це дозволяє боту "пам'ятати" кошики користувачів навіть після перезапуску
    persistence = PicklePersistence(filepath="data/bot_data.pickle")

    # 3. Створення додатку з налаштуваннями проти таймаутів
    app = (
        Application.builder()
        .token(TOKEN)
        .persistence(persistence)
        .defaults(Defaults(parse_mode=ParseMode.HTML))
        .rate_limiter(AIORateLimiter())  # Захист від блокування телеграмом
        .connect_timeout(60.0) # Важливо для повільних хостингів
        .read_timeout(60.0)
        .write_timeout(60.0)
        .pool_timeout(60.0)
        .build()
    )

    # 4. Реєстрація обробників
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(router))
    
    # Обробка тексту (адреса, телефон)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_input))
    
    # Обробка фото (чеки)
    app.add_handler(MessageHandler(filters.PHOTO, handle_receipt_photo))

    # 5. Інфо про запуск
    print("------------------------------------------------")
    print("🚀 GHOSTY SHOP BOT PRO STARTED SUCCESSFULLY")
    print("📍 Data Storage: data/bot_data.pickle")
    print("📡 Connection: Long Polling (Optimized)")
    print("------------------------------------------------")

    # 6. Запуск (drop_pending_updates видаляє старі повідомлення, щоб не було спаму при старті)
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    # Спеціальний фікс для Windows (якщо ви запускаєте на ПК), на Linux (хості) не заважає
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    try:
        main()
    except KeyboardInterrupt:
        print("🛑 Bot stopped by user")
    except Exception as e:
        logger.critical(f"CRITICAL ERROR: {e}", exc_info=True)

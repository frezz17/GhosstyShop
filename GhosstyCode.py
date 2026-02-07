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

# ===================== LOGGING =====================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ===================== CONFIG =====================
TOKEN = os.getenv("8351638507:AAEqc9p9b4AA8vTrzvvj_XArtUABqcfMGV4")

# Налаштування менеджера
try:
    MANAGER_ID = int(os.getenv("MANAGER_ID", "7544847872"))
except ValueError:
    MANAGER_ID = 7544847872

MANAGER_USERNAME = "ghosstydpbot"
CHANNEL_URL = "https://t.me/GhostyStaffDP"
PAYMENT_LINK = "https://heylink.me/ghosstyshop/"
WELCOME_PHOTO = "https://i.ibb.co/y7Q194N/1770068775663.png"

DISCOUNT_MULT = 0.65
PROMO_DISCOUNT = 45
DISCOUNT_MULTIPLIER = DISCOUNT_MULT
BASE_VIP_DATE = datetime.strptime("25.03.2026", "%d.%m.%Y")

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Налаштування для Windows (фікс для asyncio loop closed)
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# ===================== CITIES & DISTRICTS =====================
CITIES = [
    "Київ", "Дніпро", "Кам'янське", "Харків", "Одеса",
    "Львів", "Запоріжжя", "Кривий Ріг", "Полтава", "Черкаси"
]

CITY_DISTRICTS = {
    "Київ": [
        "Шевченківський", "Дарницький", "Оболонський", "Печерський",
        "Солом'янський", "Деснянський", "Подільський", "Голосіївський"
    ],
    "Дніпро": [
        "Центральний", "Соборний", "Індустріальний", "Амур",
        "Новокодацький", "Чечелівський", "Самарський", "Доставка на вказану адресу"
    ],
    "Кам'янське": [
        "Центральний", "Південний", "Заводський", "Дніпровський",
        "Черемушки", "Романкове", "БАМ", "Соцмісто"
    ],
    "Харків": [
        "Київський", "Салтівський", "Холодногірський", "Індустріальний",
        "Основ'янський", "Немишлянський", "Новобаварський", "Шевченківський"
    ],
    "Одеса": [
        "Приморський", "Київський", "Малиновський", "Суворовський",
        "Пересипський", "Хаджибейський", "Таїровський", "Люстдорфський"
    ],
    "Львів": [
        "Залізничний", "Личаківський", "Франківський", "Шевченківський",
        "Сихівський", "Галицький", "Королівський", "Новий"
    ],
    "Запоріжжя": [
        "Олександрівський", "Заводський", "Комунарський", "Дніпровський",
        "Вознесенівський", "Шевченківський", "Хортицький", "Центральний"
    ],
    "Кривий Ріг": [
        "Довгинцівський", "Інгулецький", "Металургійний", "Покровський",
        "Саксаганський", "Тернівський", "Центрально-Міський", "Червоногвардійський"
    ],
    "Полтава": [
        "Шевченківський", "Подільський", "Київський", "Залізничний",
        "Октябрський", "Ленінський", "Центральний", "Новосанжарський"
    ],
    "Черкаси": [
        "Придніпровський", "Соснівський", "Смілянський", "Канівський",
        "Золотоніський", "Уманський", "Звенигородський", "Городищенський"
    ]
}

# ===================== GIFT LIQUIDS =====================
GIFT_LIQUIDS = {
    9001: {"name": "🎁 Pumpkin Latte 30ml"},
    9002: {"name": "🎁 Glintwine 30ml"},
    9003: {"name": "🎁 Christmas Tree 30ml"},
    9004: {"name": "🎁 Strawberry Jelly 30ml"},
    9005: {"name": "🎁 Mystery One 30ml"},
    9006: {"name": "🎁 Fall Tea 30ml"},
}

def get_gift_liquids():
    return [v["name"] for v in GIFT_LIQUIDS.values()]

# ===================== PRODUCTS =====================
LIQUIDS = {
    301: {
        "name": "🎃 Pumpkin Latte",
        "series": "Chaser HO HO HO Edition",
        "price": 269,
        "discount": True,
        "img": "https://i.ibb.co/Y7qn69Ds/photo-2024-12-18-00-00-00.jpg",
        "desc": "☕ Гарбузовий латте з корицею\n🎄 Зимовий настрій\n😌 Мʼякий та теплий смак",
        "effect": "Затишок, солодкий aftertaste ☕",
        "payment_url": "https://heylink.me/ghosstyshop/"
    },
    302: {
        "name": "🍷 Glintwine",
        "series": "Chaser HO HO HO Edition",
        "price": 269,
        "discount": True,
        "img": "https://i.ibb.co/wF8r7Nmc/photo-2024-12-18-00-00-01.jpg",
        "desc": "🍇 Пряний глінтвейн\n🔥 Теплий винний смак\n🎄 Святковий вайб",
        "effect": "Тепло, релакс 🔥",
        "payment_url": "https://heylink.me/ghosstyshop/"
    },
    303: {
        "name": "🎄 Christmas Tree",
        "series": "Chaser HO HO HO Edition",
        "price": 269,
        "discount": True,
        "img": "https://i.ibb.co/vCPGV8RV/photo-2024-12-18-00-00-02.jpg",
        "desc": "🌲 Хвоя + морозна свіжість\n❄️ Дуже свіжа\n🎅 Атмосфера зими",
        "effect": "Свіжість, холодок ❄️",
        "payment_url": "https://heylink.me/ghosstyshop/"
    }
}

HHC_VAPES = {
    100: {
        "name": "🌴 Packwoods Purple 1ml",
        "type": "hhc",
        "gift_liquid": True,
        "price": 549,
        "discount": True,
        "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg",
        "desc": "🧠 90% ННС | Гібрид\n😌 Розслаблення + легка ейфорія\n🎨 Мʼякий виноградний профіль\n🎁 Рідина у подарунок на вибір\n⚠️ Потужний ефект — починай з малого",
        "payment_url": PAYMENT_LINK
    },
    101: {
        "name": "🍊 Packwoods Orange 1ml",
        "type": "hhc",
        "gift_liquid": True,
        "price": 629,
        "discount": True,
        "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg",
        "desc": "🧠 90% ННС | Гібрид\n⚡ Бадьорить та фокусує\n🍊 Соковитий апельсин\n🎁 Рідина у подарунок на вибір\n🔥 Яскравий та швидкий ефект",
        "payment_url": PAYMENT_LINK
    },
    102: {
        "name": "🌸 Packwoods Pink 1ml",
        "type": "hhc",
        "gift_liquid": True,
        "price": 719,
        "discount": True,
        "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg",
        "desc": "🧠 90% ННС | Гібрид\n😇 Спокій + підйом настрою\n🍓 Солодко-фруктовий мікс\n🎁 Рідина у подарунок на вибір\n✨ Комфортний та плавний",
        "payment_url": PAYMENT_LINK
    },
    103: {
        "name": "🌿 Whole Mint 2ml",
        "type": "hhc",
        "gift_liquid": True,
        "price": 849,
        "discount": True,
        "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg",
        "desc": "🧠 95% ННС | Сатіва\n⚡ Енергія та ясність\n❄️ Свіжа мʼята\n🎁 Рідина у подарунок на вибір\n🚀 Ідеально вдень",
        "payment_url": PAYMENT_LINK
    },
    104: {
        "name": "🌴 Jungle Boys White 2ml",
        "type": "hhc",
        "gift_liquid": True,
        "price": 999,
        "discount": True,
        "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg",
        "desc": "🧠 95% ННС | Індика\n😴 Глибокий релакс\n🌲 Насичений терпкий смак\n🎁 Рідина у подарунок на вибір\n🌙 Ідеально для вечора та сну",
        "payment_url": PAYMENT_LINK
    }
}

PODS = {
    500: {
        "name": "🔌 Vaporesso XROS 3 Mini",
        "type": "pod",
        "gift_liquid": False,
        "price": 499,
        "discount": True,
        "img": "https://i.ibb.co/yFSQ5QSn/vaporesso-xros-3-mini.jpg",
        "desc": "🔋 1000 mAh\n💨 MTL / RDL\n⚡ Type-C зарядка\n✨ Компактний та легкий\n😌 Мʼяка тяга, стабільний смак",
        "payment_url": PAYMENT_LINK
    },
    501: {
        "name": "🔌 Vaporesso XROS 5 Mini",
        "type": "pod",
        "gift_liquid": False,
        "price": 579,
        "discount": True,
        "img": "https://i.ibb.co/RkNgt1Qr/vaporesso-xros-5-mini.jpg",
        "desc": "🔋 1000 mAh\n🔥 COREX 2.0\n⚡ Швидка зарядка\n🎯 Яскравий смак\n💎 Оновлений дизайн",
        "payment_url": PAYMENT_LINK
    },
    502: {
        "name": "🔌 Vaporesso XROS Pro",
        "type": "pod",
        "gift_liquid": False,
        "price": 689,
        "discount": True,
        "img": "https://i.ibb.co/ynYwSMt6/vaporesso-xros-pro.jpg",
        "desc": "🔋 1200 mAh\n⚡ Регулювання потужності\n💨 RDL / MTL\n🔥 Максимальний смак\n🚀 Професійний рівень",
        "payment_url": PAYMENT_LINK
    },
    503: {
        "name": "🔌 Vaporesso XROS Nano",
        "type": "pod",
        "gift_liquid": False,
        "price": 519,
        "discount": True,
        "img": "https://i.ibb.co/5XW2yN80/vaporesso-xros-nano.jpg",
        "desc": "🔋 1000 mAh\n💨 MTL\n🧱 Міцний корпус\n🎒 Ідеальний у дорогу\n😌 Спокійна, рівна тяга",
        "payment_url": PAYMENT_LINK
    },
    504: {
        "name": "🔌 Vaporesso XROS 4",
        "type": "pod",
        "gift_liquid": False,
        "price": 599,
        "discount": True,
        "img": "https://i.ibb.co/LDRbQxr1/vaporesso-xros-4.jpg",
        "desc": "🔋 1000 mAh\n🔥 COREX\n🎨 Стильний дизайн\n👌 Баланс смаку та тяга\n✨ Щоденний комфорт",
        "payment_url": PAYMENT_LINK
    },
    505: {
        "name": "🔌 Vaporesso XROS 5",
        "type": "pod",
        "gift_liquid": False,
        "price": 799,
        "discount": True,
        "img": "https://i.ibb.co/hxjmpHF2/vaporesso-xros-5.jpg",
        "desc": "🔋 1200 mAh\n⚡ Fast Charge\n💎 Преміальна збірка\n🔥 Максимум смаку\n🚀 Флагман серії",
        "payment_url": PAYMENT_LINK
    },
    506: {
        "name": "🔌 Voopoo Vmate Mini Pod Kit",
        "type": "pod",
        "gift_liquid": False,
        "price": 459,
        "discount": True,
        "img": "https://i.ibb.co/8L0JNTHz/voopoo-vmate-mini.jpg",
        "desc": "🔋 1000 mAh\n💨 Автозатяжка\n🧲 Магнітний картридж\n🎯 Простий та надійний\n😌 Легкий старт для новачків",
        "payment_url": PAYMENT_LINK
    }
}

# ===================== HELPERS =====================

def get_gift_liquids():
    """Повертає список назв рідин, що йдуть у подарунок"""
    return [
        "🎃 Pumpkin Latte 30ml",
        "🍷 Glintwine 30ml",
        "🎄 Christmas Tree 30ml",
        "🍓 Strawberry Jelly 30ml",
        "🍁 Fall Tea 30ml"
    ]

def generate_promo_code(user_id: int) -> str:
    """Генерує унікальний промокод для користувача"""
    return f"GHOST-{user_id % 10000}{random.randint(100, 999)}"

def gen_order_id(uid: int) -> str:
    """Генерує номер замовлення"""
    return f"GHST-{uid}-{random.randint(1000, 9999)}"

def vip_until(profile: dict) -> datetime:
    """Рахує термін дії VIP статусу (база + реферальні дні)"""
    base = profile.get("vip_base", BASE_VIP_DATE)
    if isinstance(base, str):
        try:
            base = datetime.strptime(base, "%d.%m.%Y")
        except:
            base = BASE_VIP_DATE
    refs = profile.get("referrals", 0)
    return base + timedelta(days=7 * refs)

def calc_prices(item: dict, promo_percent: int) -> dict:
    """Розраховує базову ціну, ціну зі знижкою магазину та фінальну з промокодом"""
    base = item.get("price", 0)
    
    # Знижка магазину (наприклад, -35%)
    discounted = base
    if item.get("discount", True):
        discounted = int(base * DISCOUNT_MULTIPLIER)
    
    # Персональна знижка за промокодом
    final_price = discounted
    if promo_percent > 0:
        final_price = int(discounted * (1 - promo_percent / 100))

    return {
        "base": base,
        "discounted": discounted,
        "final": final_price
    }

def build_item_caption(item: dict, user_data: dict) -> str:
    """Створює гарний опис товару для повідомлення"""
    profile = user_data.get("profile", {})
    promo_percent = profile.get("promo_discount", PROMO_DISCOUNT)
    
    # Перевіряємо статус VIP через функцію vip_until
    v_date = vip_until(profile)
    is_vip = v_date > datetime.now()
    
    prices = calc_prices(item, promo_percent)

    text = f"<b>{escape(item['name'])}</b>\n\n"
    text += f"💰 Ціна: <s>{prices['base']} грн</s>\n"
    text += f"🔥 Акція: <b>{prices['discounted']} грн</b>\n"
    text += f"🎟 З промокодом (-{promo_percent}%): <b>{prices['final']} грн</b>\n\n"
    
    if item.get("desc"):
        text += f"📝 <b>Опис:</b>\n{item['desc']}\n\n"

    gifts = get_gift_liquids()
    text += "🎁 <b>Подарунки до замовлення (3 шт на вибір):</b>\n"
    for g in gifts:
        text += f"• {g}\n"
    
    text += "\n"
    if is_vip:
        text += "👑 <b>Ваш статус: VIP</b> (Доставка 0 грн)\n"
    else:
        text += "🚚 <b>Доставка:</b> за тарифами пошти\n"
    
    return text

# ===================== KEYBOARDS =====================
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👤 Профіль", callback_data="profile"),
         InlineKeyboardButton("🛍 Асортимент", callback_data="assortment")],
        [InlineKeyboardButton("📍 Місто", callback_data="city"),
         InlineKeyboardButton("🛒 Кошик", callback_data="cart")],
        [InlineKeyboardButton("📦 Замовлення", callback_data="orders"),
         InlineKeyboardButton("👨‍💻 Менеджер", url=f"https://t.me/{MANAGER_USERNAME}")],
        [InlineKeyboardButton("📢 Канал", url=CHANNEL_URL)]
    ])

def back_kb(back: str):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Назад", callback_data=back),
         InlineKeyboardButton("🏠 В головне меню", callback_data="main")]
    ])

# ===================== START =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = context.args
    
    # Ініціалізація даних
    if "profile" not in context.user_data:
        context.user_data["profile"] = {
            "uid": user.id,
            "full_name": user.first_name,
            "username": user.username,
            "phone": None,
            "address": None,
            "city": None,
            "district": None,
            "promo_code": generate_promo_code(user.id),
            "promo_discount": PROMO_DISCOUNT,
            "referrals": 0,
            "vip_base": BASE_VIP_DATE,
            "ref_applied": False
        }
        context.user_data["cart"] = []
        context.user_data["orders"] = []
        context.user_data["vip"] = False
    
    profile = context.user_data["profile"]
    
    # Реферальна система
    if args and not profile.get("ref_applied"):
        try:
            ref_id = int(args[0])
            if ref_id != user.id:
                profile["ref_applied"] = True
                profile["referrals"] += 1
                profile["vip_base"] = profile.get("vip_base", BASE_VIP_DATE) + timedelta(days=7)
        except ValueError:
            pass
    
    # VIP статус
    vip_date = vip_until(profile)
    context.user_data["vip"] = vip_date > datetime.now()
    
    # Повідомлення
    text = (
        f"👋 <b>{escape(user.first_name)}</b>, вітаємо у <b>Ghosty Shop</b> 💨\n\n"
        f"🎁 Подарунок до кожного замовлення — 3 рідини 30ml\n"
        f"🎫 Промокод: <code>{profile['promo_code']}</code> (-{profile.get('promo_discount', 45)}%)\n"
        f"👑 VIP до: <b>{vip_date.strftime('%d.%m.%Y')}</b>\n\n"
        f"👇 Оберіть дію:"
    )
    
    try:
        await update.message.reply_photo(
            photo=WELCOME_PHOTO,
            caption=text,
            parse_mode="HTML",
            reply_markup=main_menu()
        )
    except Exception as e:
        logger.error(f"Start error: {e}")
        await update.message.reply_text(
            text,
            parse_mode="HTML",
            reply_markup=main_menu()
        )

# ===================== PROFILE =====================
async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    profile = context.user_data.get("profile", {})
    vip_date = vip_until(profile).strftime("%d.%m.%Y")
    
    text = (
        f"👤 <b>Профіль користувача</b>\n\n"
        f"🧑 <b>Імʼя:</b> {escape(str(profile.get('full_name', '—')))}\n"
        f"👤 <b>Username:</b> @{profile.get('username', '—')}\n\n"
        f"🏙 <b>Місто:</b> {profile.get('city', '—')}\n"
        f"📍 <b>Район:</b> {profile.get('district', '—')}\n"
        f"🏠 <b>Адреса:</b> {profile.get('address', '—')}\n\n"
        f"🏷 <b>Промокод:</b> <code>{profile.get('promo_code', '—')}</code>\n"
        f"💸 <b>Знижка:</b> -{profile.get('promo_discount', PROMO_DISCOUNT)}%\n\n"
        f"💎 <b>VIP:</b> до <b>{vip_date}</b>\n"
        f"👥 <b>Рефералів:</b> {profile.get('referrals', 0)}\n"
    )
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✏️ Змінити адресу", callback_data="edit_address"),
         InlineKeyboardButton("📍 Місто", callback_data="city")],
        [InlineKeyboardButton("🔗 Реферальне посилання", callback_data="ref_link")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="main")]
    ])
    
    await query.edit_message_caption(
        caption=text,
        parse_mode="HTML",
        reply_markup=kb
    )

# ===================== REFERRAL LINK =====================
async def show_ref_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    bot_username = context.bot.username
    uid = context.user_data["profile"]["uid"]
    link = f"https://t.me/{bot_username}?start={uid}"
    
    text = (
        f"🔗 <b>Ваше реферальне посилання:</b>\n\n"
        f"<code>{link}</code>\n\n"
        f"За кожного друга +7 днів VIP!"
    )
    
    await query.edit_message_text(
        text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Назад", callback_data="profile")]
        ])
    )

# ===================== CITY SELECTION =====================
async def select_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    buttons = []
    for city in CITIES:
        buttons.append([InlineKeyboardButton(f"🏙 {city}", callback_data=f"city_{city}")])
    
    buttons.append([InlineKeyboardButton("⬅️ Назад", callback_data="profile")])
    
    await query.edit_message_text(
        "🏙 <b>Оберіть місто:</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def save_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    city = data.replace("city_", "")
    
    profile = context.user_data["profile"]
    profile["city"] = city
    profile["district"] = None
    
    districts = CITY_DISTRICTS.get(city, [])
    buttons = []
    for district in districts:
        buttons.append([InlineKeyboardButton(f"📍 {district}", callback_data=f"district_{district}")])
    
    buttons.append([InlineKeyboardButton("⬅️ Назад", callback_data="city")])
    
    await query.edit_message_text(
        f"🏙 <b>Місто збережено:</b> {city}\n\n👇 Оберіть район:",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def save_district(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    district = data.replace("district_", "")
    
    profile = context.user_data["profile"]
    profile["district"] = district
    
    await query.edit_message_text(
        f"✅ <b>Район збережено:</b> {district}",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("👤 Профіль", callback_data="profile")]
        ])
    )

# ===================== ASSORTMENT =====================
async def show_assortment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("💧 Рідини", callback_data="liquids"),
         InlineKeyboardButton("🔌 POD-системи", callback_data="pods")],
        [InlineKeyboardButton("💨 HHC / NNS", callback_data="hhc")],
        [InlineKeyboardButton("⚡ Швидке замовлення", callback_data="fast_all")],
        [InlineKeyboardButton("🏠 В головне меню", callback_data="main")]
    ])
    
    await query.edit_message_text(
        "🛍 <b>Асортимент товарів</b>\n\nОберіть категорію:",
        parse_mode="HTML",
        reply_markup=kb
    )

async def show_liquids(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    buttons = []
    for pid, item in LIQUIDS.items():
        buttons.append([
            InlineKeyboardButton(item["name"], callback_data=f"item_{pid}"),
            InlineKeyboardButton("⚡", callback_data=f"fast_{pid}")
        ])
    
    buttons.append([InlineKeyboardButton("⬅ Назад", callback_data="assortment")])
    
    await query.edit_message_text(
        "💧 <b>Рідини</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def show_pods(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    buttons = []
    for pid, item in PODS.items():
        buttons.append([
            InlineKeyboardButton(item["name"], callback_data=f"item_{pid}"),
            InlineKeyboardButton("⚡", callback_data=f"fast_{pid}")
        ])
    
    buttons.append([InlineKeyboardButton("⬅ Назад", callback_data="assortment")])
    
    await query.edit_message_text(
        "🔌 <b>POD-системи</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def show_hhc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    buttons = []
    for pid, item in HHC_VAPES.items():
        buttons.append([
            InlineKeyboardButton(item["name"], callback_data=f"item_{pid}"),
            InlineKeyboardButton("⚡", callback_data=f"fast_{pid}")
        ])
    
    buttons.append([InlineKeyboardButton("⬅ Назад", callback_data="assortment")])
    
    await query.edit_message_text(
        "💨 <b>HHC / NNS Вейпи</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# ===================== ITEM VIEW =====================
async def show_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    pid = int(data.split("_")[1])
    
    # Знайти товар
    item = LIQUIDS.get(pid) or HHC_VAPES.get(pid) or PODS.get(pid)
    
    if not item:
        await query.answer("❌ Товар не знайдено")
        return
    
    caption = build_item_caption(item, context.user_data)
    
    # Отримати фото
    photo = item.get("img", WELCOME_PHOTO)
    
    # Створити клавіатуру
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("⚡ Швидке замовлення", callback_data=f"fast_{pid}"),
         InlineKeyboardButton("🛒 В кошик", callback_data=f"add_{pid}")],
        [InlineKeyboardButton("👨‍💻 Менеджер", url=f"https://t.me/{MANAGER_USERNAME}")],
        [InlineKeyboardButton("⬅ Назад", callback_data="assortment"),
         InlineKeyboardButton("🏠 В головне меню", callback_data="main")]
    ])
    
    try:
        await query.edit_message_media(
            media=InputMediaPhoto(media=photo, caption=caption, parse_mode="HTML"),
            reply_markup=keyboard
        )
    except BadRequest:
        try:
            await query.message.delete()
            await query.message.chat.send_photo(
                photo=photo,
                caption=caption,
                parse_mode="HTML",
                reply_markup=keyboard
            )
        except Exception as e:
            logger.error(f"Show item error: {e}")

# ===================== ADD TO CART =====================
async def add_to_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    pid = int(data.split("_")[1])
    
    # Знайти товар
    item = LIQUIDS.get(pid) or HHC_VAPES.get(pid) or PODS.get(pid)
    
    if not item:
        await query.answer("❌ Товар не знайдено")
        return
    
    prices = calc_prices(item, context.user_data.get("profile", {}).get("promo_discount", PROMO_DISCOUNT))
    
    cart_item = {
        "pid": pid,
        "name": item["name"],
        "price": prices["final"],
        "base_price": item["price"],
        "gift_liquid": item.get("gift_liquid", False)
    }
    
    context.user_data.setdefault("cart", []).append(cart_item)
    await query.answer("✅ Додано в кошик")

# ===================== CART =====================
async def show_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    cart = context.user_data.get("cart", [])
    
    if not cart:
        await query.edit_message_text(
            "🛒 <b>Кошик порожній</b>",
            parse_mode="HTML",
            reply_markup=back_kb("main")
        )
        return
    
    text = "🛒 <b>Ваш кошик:</b>\n\n"
    total = 0
    
    for idx, item in enumerate(cart, 1):
        text += f"{idx}. {item['name']} — {item['price']} грн\n"
        total += item['price']
    
    text += f"\n💰 <b>Загальна сума:</b> {total} грн"
    text += f"\n🎁 <b>Подарунок:</b> 3 рідини 30ml"
    
    buttons = []
    for idx, item in enumerate(cart):
        buttons.append([InlineKeyboardButton(f"❌ Видалити {idx+1}", callback_data=f"del_{idx}")])
    
    buttons.append([
        InlineKeyboardButton("✅ Оформити замовлення", callback_data="checkout"),
        InlineKeyboardButton("⚡ Швидке замовлення", callback_data="fast_order")
    ])
    
    buttons.append([
        InlineKeyboardButton("⬅️ Назад", callback_data="main"),
        InlineKeyboardButton("🗑 Очистити кошик", callback_data="clear_cart")
    ])
    
    await query.edit_message_text(
        text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def delete_from_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    idx = int(data.split("_")[1])
    
    cart = context.user_data.get("cart", [])
    
    if 0 <= idx < len(cart):
        removed_item = cart.pop(idx)
        await query.answer(f"❌ Видалено: {removed_item.get('name', 'Товар')}")
    else:
        await query.answer("❌ Товар не знайдено")
    
    await show_cart(update, context)

async def clear_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    context.user_data["cart"] = []
    await query.answer("✅ Кошик очищено")
    await show_cart(update, context)

# ===================== ADDRESS SELECTION =====================
async def select_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    profile = context.user_data.get("profile", {})
    
    if profile.get("address"):
        text = (
            "📍 <b>Виберіть спосіб вказання адреси:</b>\n\n"
            f"Поточна адреса: {profile.get('address')}"
        )
        
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("📝 Вказати нову адресу", callback_data="enter_address")],
            [InlineKeyboardButton("✅ Використати з профілю", callback_data="use_profile_address")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="checkout")]
        ])
    else:
        text = "📍 <b>Вкажіть адресу доставки:</b>"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("📝 Вказати адресу", callback_data="enter_address")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="checkout")]
        ])
    
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=kb)

async def enter_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    context.user_data["state"] = "waiting_address"
    
    await query.edit_message_text(
        "📝 <b>Введіть адресу доставки:</b>\n\n"
        "Можна вказати:\n"
        "- Повну адресу з номером квартири\n"
        "- Відділення Нової Пошти\n"
        "- Google Maps посилання",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ Скасувати", callback_data="checkout")]
        ])
    )

async def use_profile_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    profile = context.user_data.get("profile", {})
    address = profile.get("address", "")
    
    if not address:
        await query.answer("❌ Адреса в профілі не вказана", show_alert=True)
        await select_address(update, context)
        return
    
    context.user_data["temp_address"] = address
    await confirm_order(update, context)

# ===================== CHECKOUT =====================
async def checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    cart = context.user_data.get("cart", [])
    if not cart:
        await query.answer("❌ Кошик порожній")
        return
    
    profile = context.user_data["profile"]
    
    # Перевірка міста та району
    if not profile.get("city") or not profile.get("district"):
        await query.edit_message_text(
            "📍 <b>Спочатку оберіть місто та район доставки</b>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📍 Вибрати місто", callback_data="city")],
                [InlineKeyboardButton("⬅️ Назад", callback_data="cart")]
            ])
        )
        return
    
    # Перехід до вибору адреси
    await select_address(update, context)

async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    cart = context.user_data.get("cart", [])
    profile = context.user_data["profile"]
    
    # Отримати адресу
    address = context.user_data.get("temp_address", profile.get("address", ""))
    if not address:
        await query.answer("❌ Адресу не вказано")
        await select_address(update, context)
        return
    
    # Створення замовлення
    orders = context.user_data.setdefault("orders", [])
    order_id = gen_order_id(update.effective_user.id)
    
    total = sum(item.get("price", 0) for item in cart)
    
    # Вартість доставки
    if context.user_data.get("vip"):
        delivery_cost = 0
    else:
        delivery_cost = 50  # Стандартна доставка
    
    final_total = total + delivery_cost
    
    order = {
        "id": order_id,
        "items": cart.copy(),
        "total": final_total,
        "delivery": delivery_cost,
        "status": "Очікує оплату",
        "date": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "address": f"{profile.get('city')}, {profile.get('district')}, {address}"
    }
    
    orders.append(order)
    
    # Формування тексту
    text = f"📦 <b>Замовлення #{order_id}</b>\n\n"
    text += f"👤 <b>Користувач:</b> {profile.get('full_name', '—')}\n"
    text += f"📍 <b>Адреса:</b> {order['address']}\n"
    text += f"📅 <b>Дата:</b> {order['date']}\n\n"
    text += "<b>Товари:</b>\n"
    
    for item in cart:
        text += f"• {item['name']} — {item['price']} грн\n"
    
    text += f"\n🎁 <b>Подарунок:</b> 3 рідини 30ml\n"
    text += f"📦 <b>Доставка:</b> {delivery_cost} грн\n"
    text += f"💰 <b>Загальна сума:</b> {final_total} грн\n\n"
    text += "💳 <b>Оплата за посиланням нижче:</b>"
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 Оплатити", url=PAYMENT_LINK)],
        [InlineKeyboardButton("📤 Надіслати менеджеру", callback_data=f"send_manager_{order_id}")],
        [InlineKeyboardButton("🏠 В головне меню", callback_data="main")]
    ])
    
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=kb)
    
    # Формування тексту для підтвердження
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=kb)
    
    # Очистити кошик та тимчасові дані
    context.user_data["cart"] = []
    context.user_data.pop("temp_address", None) 

# ===================== FAST ORDER =====================
async def fast_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Швидке оформлення замовлення безпосередньо з картки товару"""
    query = update.callback_query
    await query.answer()

    # Отримуємо ID товару з callback_data (наприклад, fast_301)
    try:
        data_parts = query.data.split("_")
        item_id = int(data_parts[1])
    except (IndexError, ValueError):
        await query.message.reply_text("❌ Помилка: Невірний ID товару")
        return

    # Збираємо всі товари в один словник для пошуку
    all_items = {**LIQUIDS, **HHC_VAPES, **PODS}
    item = all_items.get(item_id)

    if not item:
        await query.message.reply_text("❌ Товар не знайдено в базі")
        return

    # Очищаємо старий кошик і додаємо цей один товар
    context.user_data["cart"] = [{
        "id": item_id,
        "name": item["name"],
        "price": item["price"],
        "qty": 1
    }]

    # Кнопка для переходу до оформлення
    keyboard = [[InlineKeyboardButton("📍 Вказати дані для доставки", callback_data="order_city")]]
    
    await query.message.reply_text(
        f"⚡️ <b>Швидке замовлення:</b>\n"
        f"📦 Товар: {escape(item['name'])}\n"
        f"💰 Ціна: <b>{item['price']} грн</b>\n\n"
        "<i>Натисніть кнопку нижче, щоб завершити:</i>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
        # Швидке замовлення всього кошика
        cart = context.user_data.get("cart", [])
       async def show_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    if not cart:
        await query.edit_message_text(
            "🛒 Ваш кошик порожній.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛍 В магазин", callback_data="assortment")]])
        )
        return
        # Швидке замовлення конкретного товару
        pid = int(data.split("_")[1])
        
        item = LIQUIDS.get(pid) or HHC_VAPES.get(pid) or PODS.get(pid)
        if not item:
            await query.answer("❌ Товар не знайдено")
            return
        
        # Додати в кошик
        prices = calc_prices(item, context.user_data.get("profile", {}).get("promo_discount", PROMO_DISCOUNT))
        cart_item = {
            "pid": pid,
            "name": item["name"],
            "price": prices["final"],
            "base_price": item["price"],
            "gift_liquid": item.get("gift_liquid", False)
        }
        
        context.user_data.setdefault("cart", []).append(cart_item)
    
    # Перевірка даних користувача
    profile = context.user_data["profile"]
    
    if not profile.get("full_name") or not profile.get("phone") or not profile.get("address"):
        context.user_data["state"] = "fast_order"
        await query.edit_message_text(
            "⚡ <b>Швидке замовлення</b>\n\n"
            "✍️ Введіть ваше <b>Імʼя та Прізвище</b>:",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Скасувати", callback_data="main")]
            ])
        )
    else:
        await confirm_order(update, context)

# ===================== SEND TO MANAGER =====================
async def send_to_manager(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    order_id = data.replace("send_manager_", "")
    
    orders = context.user_data.get("orders", [])
    order = None
    
    for o in orders:
        if o["id"] == order_id:
            order = o
            break
    
    if not order:
        await query.answer("❌ Замовлення не знайдено")
        return
    
    profile = context.user_data.get("profile", {})
    user = update.effective_user
    
    # Формування повідомлення
    manager_text = f"🆕 <b>Нове замовлення #{order_id}</b>\n\n"
    manager_text += f"👤 <b>Користувач:</b> {user.first_name}\n"
    manager_text += f"🔗 <b>Username:</b> @{user.username or '—'}\n"
    manager_text += f"📞 <b>Телефон:</b> {profile.get('phone', '—')}\n"
    manager_text += f"📍 <b>Адреса:</b> {order['address']}\n\n"
    
    manager_text += "<b>Товари:</b>\n"
    for item in order["items"]:
        manager_text += f"• {item['name']} — {item['price']} грн\n"
    
    manager_text += f"\n🎁 <b>Подарунок:</b> 3 рідини 30ml\n"
    manager_text += f"💰 <b>Сума:</b> {order['total']} грн\n"
    manager_text += f"📦 <b>Доставка:</b> {order['delivery']} грн\n"
    manager_text += f"📅 <b>Дата:</b> {order['date']}\n"
    manager_text += f"🆔 <b>ID користувача:</b> {user.id}"
    
    try:
        await context.bot.send_message(
            chat_id=MANAGER_ID,
            text=manager_text,
            parse_mode="HTML"
        )
        
        # Оновити статус
        order["status"] = "Відправлено менеджеру"
        
        await query.answer("✅ Замовлення надіслано менеджеру", show_alert=True)
        await query.edit_message_text(
            "✅ <b>Замовлення надіслано менеджеру</b>\n\n"
            "Менеджер зв'яжеться з вами найближчим часом для підтвердження.",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 В головне меню", callback_data="main")]
            ])
        )
    except Exception as e:
        logger.error(f"Failed to send to manager: {e}")
        await query.answer("❌ Помилка відправки", show_alert=True)

# ===================== EDIT ADDRESS =====================
async def edit_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    context.user_data["state"] = "edit_address"
    
    await query.edit_message_text(
        "✍️ <b>Введіть нову адресу доставки:</b>\n\n"
        "Можна вказати:\n"
        "- Повну адресу з номером квартири\n"
        "- Відділення Нової Пошти\n"
        "- Google Maps посилання",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ Скасувати", callback_data="profile")]
        ])
    )

# ===================== ORDERS =====================
async def show_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    orders = context.user_data.get("orders", [])
    
    if not orders:
        await query.edit_message_text(
            "📭 <b>Замовлень ще немає</b>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🛍 До асортименту", callback_data="assortment")],
                [InlineKeyboardButton("🏠 В головне меню", callback_data="main")]
            ])
        )
        return
    
    text = "📦 <b>Мої замовлення:</b>\n\n"
    buttons = []
    
    for order in orders[-10:]:  # Останні 10 замовлень
        text += (
            f"🆔 <b>{order['id']}</b>\n"
            f"📅 {order['date']}\n"
            f"📦 Статус: {order['status']}\n"
            f"💰 {order['total']} грн\n\n"
        )
        
        if order["status"] == "Очікує оплату":
            buttons.append([
                InlineKeyboardButton(f"💳 Оплатити {order['id']}", url=PAYMENT_LINK),
                InlineKeyboardButton(f"📤 Надіслати {order['id']}", callback_data=f"send_manager_{order['id']}")
            ])
    
    buttons.append([
        InlineKeyboardButton("🏠 В головне меню", callback_data="main")
    ])
    
    await query.edit_message_text(
        text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# ===================== TEXT HANDLER =====================
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    
    text = update.message.text.strip()
    state = context.user_data.get("state")
    profile = context.user_data.get("profile", {})
    
    if state == "edit_address":
        profile["address"] = text
        context.user_data["state"] = None
        
        await update.message.reply_text(
            "✅ <b>Адресу оновлено</b>",
            parse_mode="HTML",
            reply_markup=main_menu()
        )
        return
    
    elif state == "waiting_address":
        context.user_data["temp_address"] = text
        context.user_data["state"] = None
        
        await update.message.reply_text(
            "✅ <b>Адресу збережено</b>",
            parse_mode="HTML"
        )
        await confirm_order_from_message(update, context)
        return
    
    elif state == "fast_order":
        if not profile.get("full_name"):
            profile["full_name"] = text
            context.user_data["state"] = "fast_phone"
            await update.message.reply_text(
                "📞 <b>Введіть номер телефону:</b>\n"
                "Формат: +380XXXXXXXXX",
                parse_mode="HTML"
            )
            return
        
        elif not profile.get("phone"):
            if not text.startswith("+380") or len(text) != 13:
                await update.message.reply_text(
                    "❌ Введіть номер у форматі <b>+380XXXXXXXXX</b>",
                    parse_mode="HTML"
                )
                return
            
            profile["phone"] = text
            
            if not profile.get("address"):
                context.user_data["state"] = "fast_address"
                await update.message.reply_text(
                    "📍 <b>Введіть адресу доставки:</b>",
                    parse_mode="HTML"
                )
            else:
                context.user_data["state"] = None
                await confirm_order_from_message(update, context)
            return
        
        elif not profile.get("address"):
            profile["address"] = text
            context.user_data["state"] = None
            await confirm_order_from_message(update, context)
            return
    
    else:
        await update.message.reply_text(
            "ℹ️ Скористайтеся кнопками меню 👇",
            reply_markup=main_menu()
        )

async def confirm_order_from_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cart = context.user_data.get("cart", [])
    if not cart:
        await update.message.reply_text(
            "❌ Кошик порожній",
            reply_markup=main_menu()
        )
        return
    
    profile = context.user_data.get("profile", {})

# ===================== HANDLERS (STUB) =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if "profile" not in context.user_data:
        context.user_data["profile"] = {"uid": user.id, "full_name": user.first_name, "referrals": 0, "promo_code": generate_promo_code(user.id), "promo_discount": PROMO_DISCOUNT}
        context.user_data["cart"] = []
        context.user_data["orders"] = []
    
    await update.message.reply_text(f"Привіт, {user.first_name}! Бот працює.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛍 Асортимент", callback_data="assortment")]]))

async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    # Логіка оформлення...
    await query.edit_message_text("✅ Замовлення оформлено!")
    
    # ВИПРАВЛЕНО: Правильні відступи тут
    context.user_data["cart"] = []
    context.user_data.pop("temp_address", None)
    
    # Створення замовлення
    orders = context.user_data.setdefault("orders", [])
    order_id = gen_order_id(update.effective_user.id)
    
    total = sum(item.get("price", 0) for item in cart)
    
    # Вартість доставки
    if context.user_data.get("vip"):
        delivery_cost = 0
    else:
        delivery_cost = 50
    
    final_total = total + delivery_cost
    
    order = {
        "id": order_id,
        "items": cart.copy(),
        "total": final_total,
        "delivery": delivery_cost,
        "status": "Очікує оплату",
        "date": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "address": f"{profile.get('city', '—')}, {profile.get('district', '—')}, {profile.get('address', '—')}"
    }
    
    orders.append(order)
    
    # Формування тексту
    text = f"⚡ <b>Швидке замовлення #{order_id}</b>\n\n"
    text += f"👤 <b>Користувач:</b> {profile.get('full_name', '—')}\n"
    text += f"📞 <b>Телефон:</b> {profile.get('phone', '—')}\n"
    text += f"📍 <b>Адреса:</b> {order['address']}\n\n"
    text += "<b>Товари:</b>\n"
    
    for item in cart:
        text += f"• {item['name']} — {item['price']} грн\n"
    
    text += f"\n🎁 <b>Подарунок:</b> 3 рідини 30ml\n"
    text += f"📦 <b>Доставка:</b> {delivery_cost} грн\n"
    text += f"💰 <b>Загальна сума:</b> {final_total} грн\n\n"
    text += "💳 <b>Оплата за посиланням нижче:</b>"
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 Оплатити", url=PAYMENT_LINK)],
        [InlineKeyboardButton("📤 Надіслати менеджеру", callback_data=f"send_manager_{order_id}")],
        [InlineKeyboardButton("🏠 В головне меню", callback_data="main")]
    ])
    
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=kb)
    
    # Очистити кошик
    context.user_data["cart"] = []

# ===================== PHOTO HANDLER (RECEIPTS) =====================
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    active_order_id = context.user_data.get("active_order_id")
    
    if not active_order_id:
        await update.message.reply_text(
            "📸 <b>Надіслано фото, але активного замовлення немає.</b>\n"
            "Будь ласка, спочатку створіть замовлення.",
            parse_mode="HTML"
        )
        return
    
    # Надіслати менеджеру
    photo_file = await update.message.photo[-1].get_file()
    
    caption = (
        f"🧾 <b>Квитанція про оплату</b>\n\n"
        f"🆔 Замовлення: {active_order_id}\n"
        f"👤 Користувач: {update.effective_user.mention_html()}\n"
        f"🆔 ID: {update.effective_user.id}"
    )
    
    try:
        await context.bot.send_photo(
            chat_id=MANAGER_ID,
            photo=photo_file.file_id,
            caption=caption,
            parse_mode="HTML"
        )
        
        await update.message.reply_text(
            "✅ <b>Квитанцію отримано!</b>\n"
            "Менеджер перевірить її та зв'яжеться з вами.",
            parse_mode="HTML"
        )
        
        # Оновити статус
        orders = context.user_data.get("orders", [])
        for order in orders:
            if order["id"] == active_order_id:
                order["status"] = "Оплачено (на перевірці)"
                break
        
        context.user_data["active_order_id"] = None
    except Exception as e:
        logger.error(f"Photo handler error: {e}")
        await update.message.reply_text(
            "❌ <b>Помилка відправки квитанції</b>",
            parse_mode="HTML"
        )

# ===================== CONTACT HANDLER =====================
async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробка надісланих контактів"""
    contact = update.message.contact
    user = update.effective_user
    
    if contact and contact.user_id == user.id:
        profile = context.user_data.setdefault("profile", {})
        profile["phone"] = contact.phone_number
        
        await update.message.reply_text(
            f"✅ Номер телефону збережено: {contact.phone_number}",
            parse_mode="HTML",
            reply_markup=main_menu()
        )
    else:
        await update.message.reply_text(
            "ℹ️ Будь ласка, надішліть свій власний контакт",
            reply_markup=main_menu()
        )

# ===================== CALLBACK ROUTER =====================
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    # Захист: якщо запит порожній або повідомлення вже видалено
    if not query or not query.message:
        return
    
    # Завжди відповідаємо на запит, щоб прибрати "годинник" на кнопці
    await query.answer()
    data = query.data
    
    try:
        # Головне меню та Профіль
        if data == "main":
            await start(update, context)
        elif data == "profile":
            await show_profile(update, context)
        elif data == "ref_link":
            await show_ref_link(update, context)
        elif data == "orders":
            await show_orders(update, context)

        # Логіка Міст та Адреси
        elif data == "city":
            await select_city(update, context)
        elif data.startswith("city_"):
            await save_city(update, context)
        elif data.startswith("district_"):
            await save_district(update, context)
        elif data == "edit_address":
            await edit_address(update, context)
        elif data == "enter_address":
            await enter_address(update, context)
        elif data == "use_profile_address":
            await use_profile_address(update, context)

        # Асортимент та Категорії
        elif data == "assortment":
            await show_assortment(update, context)
        elif data == "liquids":
            await show_liquids(update, context)
        elif data == "pods":
            await show_pods(update, context)
        elif data == "hhc":
            await show_hhc(update, context)
        elif data.startswith("item_"):
            await show_item(update, context)

        # Кошик
        elif data.startswith("add_"):
            await add_to_cart(update, context)
        elif data == "cart":
            await show_cart(update, context)
        elif data.startswith("del_"):
            await delete_from_cart(update, context)
        elif data == "clear_cart":
            await clear_cart(update, context)
        elif data == "checkout":
            await checkout(update, context)

        # Швидке замовлення (Fast Order)
        # Об'єднуємо перевірку, щоб спрацювало і fast_ID, і просто fast_order
        elif data.startswith("fast_"):
            await fast_start(update, context)

        # Взаємодія з менеджером
        elif data.startswith("send_manager_"):
            await send_to_manager(update, context)

        # Якщо дія не розпізнана
        else:
            logger.warning(f"Unknown callback: {data}")
            await query.answer("⚠️ Ця функція ще в розробці", show_alert=True)

    except Exception as e:
        logger.error(f"Помилка в handle_callback: {e}", exc_info=True)
        # Намагаємося повідомити користувача про проблему
        try:
            await query.message.reply_text(
                "❌ Сталася внутрішня помилка. Спробуйте оновити меню командою /start",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 В меню", callback_data="main")]])
            )
        except:
            pass

# ===================== ERROR HANDLER =====================
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Глобальний обробник помилок"""
    logger.error(f"Exception while handling an update: {context.error}")
    
    # Логуємо помилку
    if update and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "⚠️ Сталася помилка. Спробуйте ще раз або /start",
                reply_markup=main_menu()
            )
        except:
            pass

# ===================== FALLBACK HANDLER =====================
async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробник невідомих команд"""
    await update.message.reply_text(
        "❌ Невідома команда. Скористайтесь кнопками меню 👇",
        reply_markup=main_menu()
    )

# ===================== MAIN =====================
def main():
    try:
        print("🚀 Запуск Ghosty Shop Bot...")
        
        # Створюємо директорію для даних, якщо її немає
        data_dir = "/app/data" if os.path.exists("/app") else "./data"
        os.makedirs(data_dir, exist_ok=True)
        
        # Шлях до файлу з даними
        persistence_file = os.path.join(data_dir, "ghosty_data.pickle")
        print(f"📁 Використовується файл даних: {persistence_file}")
        
        # Ініціалізація Persistence
        persistence = PicklePersistence(filepath=persistence_file)
        
        # Перевірка наявності токена
        if not TOKEN:
            logger.error("❌ Помилка: Токен бота не знайдено!")
            logger.error("Встанови змінну середовища BOT_TOKEN")
            sys.exit(1)

        # Створення додатку
        print(f"🤖 Створення бота з токеном: {TOKEN[:10]}...")
        
        app = Application.builder() \
            .token(TOKEN) \
            .persistence(persistence) \
            .concurrent_updates(True) \
            .build()
        
        # Додаємо обробники
        print("🔧 Налаштування обробників...")
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CallbackQueryHandler(handle_callback))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
        app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
        
        # Додатково: обробник для контактів
        app.add_handler(MessageHandler(filters.CONTACT, handle_contact))
        
        # Обробник помилок
        app.add_error_handler(error_handler)
        
        print("✅ Бот налаштовано!")
        print("🤖 Ghosty Shop Bot запущено!")
        print("🔄 Бот працює... Натисніть Ctrl+C для зупинки.")
        
        # Запуск бота з обробкою помилок
        app.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,
            timeout=30,
            read_timeout=10,
            pool_timeout=10
        )
        
    except KeyboardInterrupt:
        print("\n⚠️ Бот зупинено користувачем")
        sys.exit(0)
    except telegram.error.InvalidToken as e:
        print(f"❌ Невірний токен бота: {e}")
        sys.exit(1)
    except telegram.error.NetworkError as e:
        print(f"❌ Мережева помилка: {e}")
        sys.exit(1)
    except telegram.error.TelegramError as e:
        print(f"❌ Помилка Telegram API: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Критична помилка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

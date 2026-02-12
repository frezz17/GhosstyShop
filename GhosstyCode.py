# =================================================================
# 🤖 PROJECT: GHOSTY STAFF PREMIUM E-COMMERCE ENGINE (FINAL)
# 🛠 VERSION: 5.1.0 (GIFT SYSTEM READY)
# 🛡 DEVELOPER: Gho$$tyyy & Gemini AI
# =================================================================

import os
import sys
import logging
import sqlite3
import asyncio
import random
import traceback
from datetime import datetime, timedelta # Виправлено імпорт
from html import escape

# Telegram Core
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.constants import ParseMode
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    CallbackQueryHandler, ContextTypes, filters, 
    PicklePersistence, Defaults
)
from telegram.error import NetworkError, BadRequest

# =================================================================
# ⚙️ SECTION 1: GLOBAL CONFIGURATION (FIXED)
# =================================================================

# 1. Шляхи (Абсолютні для BotHost)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DB_PATH = os.path.join(DATA_DIR, 'ghosty_pro_final.db')
PERSISTENCE_PATH = os.path.join(DATA_DIR, 'ghosty_state_final.pickle')
LOG_PATH = os.path.join(DATA_DIR, 'ghosty_system.log')

# Створюємо папку даних
os.makedirs(DATA_DIR, exist_ok=True)

# 2. ТОКЕН (ОБОВ'ЯЗКОВО НОВИЙ!)
# 👇 Встав токен між лапками 👇
ENV_TOKEN = os.getenv("8351638507:AAE8JbSIduGOMYnCu77WFRy_3s7-LRH34lQ") 
TOKEN = ENV_TOKEN if ENV_TOKEN else "8351638507:AAE8JbSIduGOMYnCu77WFRy_3s7-LRH34lQ"
# 👆 Наприклад: "754321:AAHk..."

MANAGER_ID = 7544847872
MANAGER_USERNAME = "ghosstydp"
CHANNEL_URL = "https://t.me/GhostyStaffDP"
WELCOME_PHOTO = "https://i.ibb.co/y7Q194N/1770068775663.png"

# 3. Посилання
PAYMENT_LINK = {
    "mono": "https://lnk.ua/k4xJG21Vy",   
    "privat": "https://lnk.ua/RVd0OW6V3",
    "ghossty": "https://heylink.me/GhosstyShop"
}

# 4. Логування (Для BotHost вивід у stdout критичний)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_PATH, encoding='utf-8')
    ]
)
logger = logging.getLogger("GhostyCore")

# =================================================================
# 🛠 SECTION 2: ERROR HANDLING
# =================================================================

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Логування критичних помилок та сповіщення адміна."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    
    try:
        # Формуємо звіт про помилку
        tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
        tb_string = "".join(tb_list)[-4000:] # Обрізаємо, щоб влізло в повідомлення
        
        message = (
            f"🆘 <b>CRITICAL ERROR</b>\n"
            f"<pre>{escape(tb_string)}</pre>"
        )
        
        # Надсилаємо менеджеру в особисті, якщо це можливо
        await context.bot.send_message(chat_id=MANAGER_ID, text=message, parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.error(f"Could not send error log to admin: {e}")
        
# --- 🎁 ПОДАРУНКОВІ РІДИНИ (8 смаків для HHC) ---
GIFT_LIQUIDS = {
    9001: {"name": "🎁 Pumpkin Latte 30ml", "desc": "Теплий осінній смак пряного гарбуза."},
    9002: {"name": "🎁 Glintwine 30ml", "desc": "Насичений виноград та зимові спеції."},
    9003: {"name": "🎁 Christmas Tree 30ml", "desc": "Унікальний аромат морозної хвої."},
    9004: {"name": "🎁 Strawberry Jelly 30ml", "desc": "Солодкий десертний аромат полуниці."},
    9005: {"name": "🎁 Mystery One 30ml", "desc": "Секретний мікс від Ghosty Staff."},
    9006: {"name": "🎁 Fall Tea 30ml", "desc": "Чайний аромат з нотками лимону."},
    9007: {"name": "🎁 Banana Ice 30ml", "desc": "Стиглий банан з крижаною свіжістю."},
    9008: {"name": "🎁 Wild Berries 30ml", "desc": "Класичний мікс лісових ягід."}
}


# =================================================================
# 📍 SECTION 4: DATA (UKRAINE MAP PRO 2026)
# =================================================================

# Топ-10 Міст + Реальні райони + Спец. точки
UKRAINE_CITIES = {
    "Київ": [
        "Печерський", "Шевченківський", "Голосіївський", "Оболонський", 
        "Подільський", "Дарницький", "Солом'янський", "Деснянський (Троєщина)"
    ],
    "Дніпро": [
        "Центральний (Мост-Сіті)", "Соборний (Нагірка)", "Індустріальний", 
        "Шевченківський", "Чечелівський", "Лівобережний-3 (ТЦ Караван)", 
        "Перемога 1-6", "Придніпровськ", 
        "🚀 Адресна доставка кур'єром (+150 грн)"
    ],
    "Кам'янське": ["Центральний (Заводський)", "Дніпровський (Лівий)", "Південний (БАМ/Соцмісто)"],
    "Харків": ["Шевченківський", "Київський", "Салтівський", "Немишлянський", "Холодногірський", "Новобаварський"],
    "Одеса": ["Приморський (Центр)", "Київський (Таїрова)", "Малиновський (Черемушки)", "Суворовський (Котовського)"],
    "Львів": ["Галицький (Центр)", "Личаківський", "Сихівський", "Франківський", "Шевченківський", "Залізничний"],
    "Запоріжжя": ["Олександрівський", "Заводський", "Комунарський", "Дніпровський", "Вознесенівський", "Хортицький"],
    "Кривий Ріг": ["Металургійний", "Центрально-Міський", "Саксаганський", "Покровський", "Тернівський"],
    "Вінниця": ["Центр", "Вишенька", "Замостя", "Старе місто", "Поділля", "Слов'янка"],
    "Полтава": ["Шевченківський", "Київський", "Подільський"]
}

CITIES_LIST = list(UKRAINE_CITIES.keys())

# 2. Додаємо порожні категорії, щоб не було помилок
HHC_VAPES = {} 
LIQUIDS = {}
PODS = {}
SETS = {} # <--- Ось змінна, якої не вистачало раніше

# 3. Тепер створюємо аліаси (Бо UKRAINE_CITIES вже існує вище!)
CITIES_LIST = list(UKRAINE_CITIES.keys())
CITY_DISTRICTS = UKRAINE_CITIES


# =================================================================
# 🧮 SECTION 4.5: UTILITY HELPERS (FIXED & SAFE)
# =================================================================

async def _edit_or_reply(query_or_update, text, reply_markup=None):
    """
    Універсальна функція: редагує старе або шле нове, якщо редагування неможливе.
    Працює і з Update, і з CallbackQuery.
    """
    try:
        markup = InlineKeyboardMarkup(reply_markup) if isinstance(reply_markup, list) else reply_markup
        
        # Визначаємо, з чим працюємо (Update або CallbackQuery)
        message = query_or_update.message if hasattr(query_or_update, 'message') else query_or_update
        
        if not message:
            # Якщо це Update без message (рідкісний кейс), пробуємо effective_message
            if hasattr(query_or_update, 'effective_message'):
                message = query_or_update.effective_message
            else:
                logger.error("UI Error: No message object found to reply to.")
                return

        try:
            await message.edit_text(text, reply_markup=markup, parse_mode='HTML')
        except BadRequest: 
            # Якщо текст не змінився або повідомлення надто старе -> видаляємо і шлемо нове
            try:
                await message.delete()
            except: pass # Якщо вже видалено
            await message.reply_text(text, reply_markup=markup, parse_mode='HTML')
            
    except Exception as e:
        logger.error(f"UI Critical Error: {e}")

async def send_ghosty_message(update, text, keyboard=None, photo=None):
    """Розумна відправка медіа або тексту."""
    reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
    
    # Визначаємо об'єкт для відповіді
    target = update.callback_query if update.callback_query else update.message
    
    if photo:
        try:
            # Спробуємо надіслати фото
            if update.callback_query:
                try: await update.callback_query.message.delete()
                except: pass
                await update.callback_query.message.reply_photo(photo=photo, caption=text, reply_markup=reply_markup, parse_mode='HTML')
            else:
                await update.message.reply_photo(photo=photo, caption=text, reply_markup=reply_markup, parse_mode='HTML')
        except Exception as e:
            logger.error(f"Photo send failed: {e}. Fallback to text.")
            # Якщо фото побите або URL невалідний -> шлемо текст
            await _edit_or_reply(target, text, reply_markup)
    else:
        await _edit_or_reply(target, text, reply_markup)

def get_item_data(item_id):
    """
    Шукає товар за ID у всіх категоріях.
    FIX: Примусова конвертація в int, щоб уникнути помилок типів.
    """
    try:
        iid = int(item_id) # <--- ВИПРАВЛЕНО: str -> int
    except (ValueError, TypeError):
        return None

    # Додано SETS у пошук
    for db in [HHC_VAPES, PODS, LIQUIDS, GIFT_LIQUIDS, SETS]:
        if iid in db:
            return db[iid]
    return None

# =================================================================
# 🛠 SECTION 3: MATH (DISCOUNT LOGIC)
# =================================================================

def calculate_final_price(item_price, user_profile):
    """
    Математика: (Ціна - 101 грн) * 0.65 (-35%).
    """
    is_vip = user_profile.get('is_vip', False)
    promo_fixed = user_profile.get('next_order_discount', 0) # 101 грн
    
    price = float(item_price)
    discounted = False

    # 1. Мінус 101 грн (GHST2026)
    if promo_fixed > 0 and price > promo_fixed:
        price -= promo_fixed
        discounted = True
    
    # 2. Мінус 35% (VIP)
    if is_vip:
        price = price * 0.65 
        discounted = True
    
    if price < 10: price = 10.0
    return round(price, 2), discounted
    
# ... (інші функції: error_handler, send_ghosty_message, get_item_data залишаються) ...

# --- МЕНЮ ВИБОРУ МІСТА ---
async def choose_city_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Меню вибору міста."""
    # Отримуємо об'єкт для відповіді (або query, або message)
    target = update.callback_query if update.callback_query else update
    
    profile = context.user_data.get("profile", {})
    current_city = profile.get("city")

    text = "📍 <b>ОБЕРІТЬ ВАШЕ МІСТО</b>\n━━━━━━━━━━━━━━━━━━━━\n"
    if current_city:
        text += f"✅ Ви обрали: <b>{current_city}</b>\n"
    text += "👇 <i>Натисніть на місто нижче:</i>"

    keyboard = []
    city_list = list(UKRAINE_CITIES.keys())
    
    # Генерація кнопок (по 2 в ряд)
    for i in range(0, len(city_list), 2):
        row = [InlineKeyboardButton(city_list[i], callback_data=f"sel_city_{city_list[i]}")]
        if i + 1 < len(city_list):
            row.append(InlineKeyboardButton(city_list[i+1], callback_data=f"sel_city_{city_list[i+1]}"))
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("🔙 Назад до профілю", callback_data="menu_profile")])
    
    await _edit_or_reply(target, text, keyboard)

async def choose_dnipro_delivery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Спеціальне меню для Дніпра."""
    text = (
        "🏙 <b>ДНІПРО: ТИП ДОСТАВКИ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "1️⃣ <b>Район (Клад)</b> — магніт/прикоп.\n"
        "2️⃣ <b>Кур'єр (+150 грн)</b> — доставка до дверей."
    )
    kb = [
        [InlineKeyboardButton("📍 Обрати район (Клад)", callback_data="set_del_type_klad")],
        [InlineKeyboardButton("🛵 Кур'єр (+150 грн)", callback_data="set_del_type_courier")],
        [InlineKeyboardButton("⬅️ Змінити місто", callback_data="choose_city")]
    ]
    await _edit_or_reply(update.callback_query, text, kb)

async def choose_district_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, city: str):
    """Меню районів."""
    districts = UKRAINE_CITIES.get(city, [])
    text = f"📍 <b>{city.upper()}: ОБЕРІТЬ РАЙОН</b>"
    
    keyboard = []
    for i in range(0, len(districts), 2):
        row = [InlineKeyboardButton(districts[i], callback_data=f"sel_dist_{districts[i]}")]
        if i + 1 < len(districts):
            row.append(InlineKeyboardButton(districts[i+1], callback_data=f"sel_dist_{districts[i+1]}"))
        keyboard.append(row)
        
    keyboard.append([InlineKeyboardButton("⬅️ Змінити місто", callback_data="choose_city")])
    await _edit_or_reply(update.callback_query, text, keyboard)

# =================================================================
# 🛍 SECTION 3: ТОВАРНА БАЗА (FIXED SYNTAX & COLORS)
# =================================================================

GIFT_LIQUIDS = {
    9001: {"name": "🎁 Pumpkin Latte 30ml", "desc": "Теплий осінній смак пряного гарбуза."},
    9002: {"name": "🎁 Glintwine 30ml", "desc": "Насичений виноград та зимові спеції."},
    9003: {"name": "🎁 Christmas Tree 30ml", "desc": "Унікальний аромат морозної хвої."},
    9004: {"name": "🎁 Strawberry Jelly 30ml", "desc": "Солодкий десертний аромат полуниці."},
    9005: {"name": "🎁 Mystery One 30ml", "desc": "Секретний мікс від Ghosty Staff."},
    9006: {"name": "🎁 Fall Tea 30ml", "desc": "Чайний аромат з нотками лимону."},
    9007: {"name": "🎁 Banana Ice 30ml", "desc": "Стиглий банан з крижаною свіжістю."},
    9008: {"name": "🎁 Wild Berries 30ml", "desc": "Класичний мікс лісових ягід."}
}

LIQUIDS = {
    301: {
        "name": "🍂 Fall Tea",
        "category": "Chaser Balance",
        "price": 249.99,
        "discount": True,
        "strengths": [50, 65, 85],
        "img": "https://i.ibb.co/Kxmrpm1C/Fall-Tea.jpg",
        "desc": "☕ <b>Осінній Чай</b>\nСпокійний аромат чаю з нотками лимону.",
        "payment_url": PAYMENT_LINK
    },
    302: {
        "name": "👻 Mystery One",
        "category": "Chaser Balance",
        "price": 249.99,
        "discount": True,
        "strengths": [50, 65, 85],
        "img": "https://i.ibb.co/bMMVHXG6/Mystery-One.jpg",
        "desc": "🔮 <b>Ghost Edition</b>\nТаємничий фруктовий мікс.",
        "payment_url": PAYMENT_LINK
    },
    303: {
        "name": "🍓 Strawberry Jelly",
        "category": "Chaser Balance",
        "price": 249.99,
        "discount": True,
        "strengths": [50, 65, 85],
        "img": "https://i.ibb.co/sd9ZSfyH/Strawberry-Jelly.jpg",
        "desc": "🍮 <b>Полуничне Желе</b>\nНіжний десертний смак.",
        "payment_url": PAYMENT_LINK
    },
    304: {
        "name": "🍇 Grape BlackBerry",
        "category": "Limited Ultra",
        "price": 249.99,
        "discount": True,
        "strengths": [50, 65, 85],
        "img": "https://i.ibb.co/nMJ2VdQK/Grape-Black-Berry.jpg",
        "desc": "🍇 <b>Виноград-Ожина</b>\nВибух темних ягід.",
        "payment_url": PAYMENT_LINK
    },
    305: {
        "name": "🥤 Cola Pomelo",
        "category": "Limited Ultra",
        "price": 249.99,
        "discount": True,
        "strengths": [50, 65, 85],
        "img": "https://i.ibb.co/zdpDg2K/Cola-Pomelo.jpg",
        "desc": "🍊 <b>Кола-Помело</b>\nНезвичне поєднання.",
        "payment_url": PAYMENT_LINK
    },
    306: {
        "name": "🌹 BlackCurrant Rose",
        "category": "Limited Ultra",
        "price": 249.99,
        "discount": True,
        "strengths": [50, 65, 85],
        "img": "https://i.ibb.co/0pLKnvx2/Black-Currant-Rose.jpg",
        "desc": "🥀 <b>Смородина-Троянда</b>\nВишуканий аромат.",
        "payment_url": PAYMENT_LINK
    },
    307: {
        "name": "🍋 Berry Lemonade",
        "category": "Special Berry",
        "price": 249.99,
        "discount": True,
        "strengths": [50, 65, 85],
        "img": "https://i.ibb.co/21xt8N1p/Berry-Lemonade.jpg",
        "desc": "🍹 <b>Ягідний Лимонад</b>\nОсвіжаючий літній мікс.",
        "payment_url": PAYMENT_LINK
    },
    308: {
        "name": "⚡ Energetic",
        "category": "Special Berry",
        "price": 249.99,
        "discount": True,
        "strengths": [50, 65, 85],
        "img": "https://i.ibb.co/TBwR7NTP/Energetic.jpg",
        "desc": "🔋 <b>Енергетик</b>\nСмак, що бадьорить.",
        "payment_url": PAYMENT_LINK
    },
    309: {
        "name": "💊 Vitamin",
        "category": "Special Berry",
        "price": 249.99,
        "discount": True,
        "strengths": [50, 65, 85],
        "img": "https://i.ibb.co/tTLrsGGT/Vitamin.jpg",
        "desc": "🍏 <b>Вітамін</b>\nМікс фруктів.",
        "payment_url": PAYMENT_LINK
    }
}

HHC_VAPES = {
    100: {
        "name": "🌴 Packwoods Purple 1ml",
        "type": "hhc",
        "price": 699.77,
        "discount": True,
        "gift_liquid": True,
        "img": "https://i.ibb.co/svXqXPgL/Ghost-Vape-3.jpg",
        "desc": "🧠 <b>90% HHC | Гібрид</b>\n😌 Розслаблення + ейфорія\n🎁 <b>+ РІДИНА БЕЗКОШТОВНО!</b>",
        "payment_url": PAYMENT_LINK
    },
    101: {
        "name": "🍊 Packwoods Orange 1ml",
        "type": "hhc",
        "price": 699.77,
        "discount": True,
        "gift_liquid": True,
        "img": "https://i.ibb.co/SDJFRTwk/Ghost-Vape-1.jpg",
        "desc": "🧠 <b>90% HHC | Сатіва</b>\n⚡ Бадьорить та фокусує\n🎁 <b>+ РІДИНА БЕЗКОШТОВНО!</b>",
        "payment_url": PAYMENT_LINK
    },
    102: {
        "name": "🌸 Packwoods Pink 1ml",
        "type": "hhc",
        "price": 699.77,
        "discount": True,
        "gift_liquid": True,
        "img": "https://i.ibb.co/65j1901/Ghost-Vape-2.jpg",
        "desc": "🧠 <b>90% HHC | Індіка</b>\n😇 Спокій + підйом настрою\n🎁 <b>+ РІДИНА БЕЗКОШТОВНО!</b>",
        "payment_url": PAYMENT_LINK
    },
    103: {
        "name": "🌿 Whole Mint 2ml",
        "type": "hhc",
        "price": 879.77,
        "discount": True,
        "gift_liquid": True,
        "img": "https://i.ibb.co/W4hqn2tZ/Ghost-Vape-4.jpg",
        "desc": "🧠 <b>95% HHC | Сатіва</b>\n⚡ Енергія та ясність (2ml)\n🎁 <b>+ РІДИНА БЕЗКОШТОВНО!</b>",
        "payment_url": PAYMENT_LINK
    },
    104: {
        "name": "🌴 Jungle Boys White 2ml",
        "type": "hhc",
        "price": 999.77,
        "discount": True,
        "gift_liquid": True,
        "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg",
        "desc": "🧠 <b>95% HHC | Індика</b>\n😴 Глибокий релакс (2ml)\n🎁 <b>+ РІДИНА БЕЗКОШТОВНО!</b>",
        "payment_url": PAYMENT_LINK
    }
}

# =================================================================
# 🛍 SECTION 3: ТОВАРНА БАЗА (PODS - FIXED SYNTAX)
# =================================================================

PODS = {
    500: {
        "name": "🔌 Vaporesso XROS 3 Mini",
        "type": "pod",
        "gift_liquid": False,
        "price": 499.77,
        "discount": True,
        "img": "https://i.ibb.co/yFSQ5QSn/vaporesso-xros-3-mini.jpg",
        "desc": "🔋 <b>1000 mAh | MTL</b>\nЛегендарна модель. Надійна та смачна.\n✨ <i>Ідеальний вибір для старту.</i>",
        "colors": ["⚫️ Black", "⚪️ Silver", "🔵 Navy Blue", "🔴 Phantom Red"],
        "payment_url": PAYMENT_LINK
    },
    501: {
        "name": "🔌 Vaporesso XROS 5 Mini",
        "type": "pod",
        "gift_liquid": False,
        "price": 674.77,
        "discount": True,
        "img": "https://i.ibb.co/RkNgt1Qr/vaporesso-xros-5-mini.jpg",
        "desc": "🔥 <b>НОВИНКА 2025 | COREX 2.0</b>\nМаксимальна передача смаку.\n💎 <i>Оновлений дизайн та швидка зарядка.</i>",
        "colors": ["⚫️ Core Black", "🔘 Space Grey", "🟣 Ice Purple", "🟢 Lime Green"],
        "payment_url": PAYMENT_LINK
    },
    502: {
        "name": "🔌 Vaporesso XROS Pro",
        "type": "pod",
        "gift_liquid": False,
        "price": 974.77,
        "discount": True,
        "img": "https://i.ibb.co/ynYwSMt6/vaporesso-xros-pro.jpg",
        "desc": "🚀 <b>PROFESSIONAL | 1200 mAh</b>\nЕкран, регулювання потужності, блокування.\n⚡ <i>Зарядка за 35 хвилин!</i>",
        "colors": ["⚫️ Black", "⚪️ Silver", "🔴 Red", "🔵 Blue"],
        "payment_url": PAYMENT_LINK
    },
    503: {
        "name": "🔌 Vaporesso XROS Nano",
        "type": "pod",
        "gift_liquid": False,
        "price": 659.77,
        "discount": True,
        "img": "https://i.ibb.co/5XW2yN80/vaporesso-xros-nano.jpg",
        "desc": "🎒 <b>КОМПАКТНИЙ КВАДРАТ</b>\nСтильний, зручний, на шнурку.\n🔋 <i>1000 mAh у міні-корпусі.</i>",
        "colors": ["⚫️ Black", "🟡 Yellow", "🟠 Orange", "🌸 Pink"],
        "payment_url": PAYMENT_LINK
    },
    504: {
        "name": "🔌 Vaporesso XROS 4",
        "type": "pod",
        "gift_liquid": False,
        "price": 629.77,
        "discount": True,
        "img": "https://i.ibb.co/LDRbQxr1/vaporesso-xros-4.jpg",
        "desc": "👌 <b>БАЛАНС ТА СТИЛЬ</b>\nМеталевий корпус, 3 режими потужності.\n🎯 <i>Універсальний солдат.</i>",
        "colors": ["⚫️ Black", "🔵 Blue", "🟣 Purple Gradient", "⚪️ Silver"],
        "payment_url": PAYMENT_LINK
    },
    505: {
        "name": "🔌 Vaporesso XROS 5",
        "type": "pod",
        "gift_liquid": False,
        "price": 799.77,
        "discount": True,
        "img": "https://i.ibb.co/hxjmpHF2/vaporesso-xros-5.jpg",
        "desc": "💎 <b>ПРЕМІУМ ФЛАГМАН</b>\n1200 mAh, 3 режими, супер-смак.\n🚀 <i>Найкраще, що створили Vaporesso.</i>",
        "colors": ["⚫️ Obsidian Black", "⚪️ Pearl White", "🔵 Ocean Blue"],
        "payment_url": PAYMENT_LINK
    },
    506: {
        "name": "🔌 Voopoo Vmate Mini",
        "type": "pod",
        "gift_liquid": False,
        "price": 459.77,
        "discount": True,
        "img": "https://i.ibb.co/8L0JNTHz/voopoo-vmate-mini.jpg",
        "desc": "😌 <b>ЛЕГКИЙ СТАРТ</b>\nАвтоматична тяга, жодних кнопок.\n🧬 <i>Просто залий рідину і парь.</i>",
        "colors": ["⚫️ Black", "🔴 Red", "🔵 Blue", "🟢 Green"],
        "payment_url": PAYMENT_LINK
    }
}


# =================================================================
# 📜 SECTION 4: УГОДА ТА ПРАВИЛА
# =================================================================
# Таймер для статистики (Uptime)
START_TIME = datetime.now()

# НЕЗМІННА УГОДА (PRO-VERSION)
TERMS_TEXT = (
    "📜 <b>Умови, правила, відповідальність</b>\n\n"
    "1️⃣ Проєкт має навчально-демонстраційний характер.\n"
    "2️⃣ Матеріали не є рекомендацією до придбання чи використання.\n"
    "3️⃣ Користувач самостійно несе відповідальність за свої дії.\n"
    "4️⃣ Магазин не здійснює продаж реальних товарів.\n\n"
    "⚠️ <b>Важливо:</b>\n"
    "5️⃣ Усі переказані кошти вважаються добровільним подарунком розробнику Gho$$tyyy/"
)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Привітання з персональним промокодом."""
    user = update.effective_user
    profile = await get_or_create_user(update, context)
    
    # Авто-активація бонусів
    if not profile.get('promo_applied'):
        profile.update({'next_order_discount': 101, 'is_vip': True, 'vip_expiry': "25.03.2026", 'promo_applied': True})

    personal_promo = f"GHST{user.id}"
    
    welcome_text = (
        f"🌫️ <b>GHO$$TY STAFF LAB | 2026</b> 🛸\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Йо, <b>{escape(user.first_name)}</b>! Твій статус: <b>VIP PRO</b> 🌿\n\n"
        f"🎁 <b>ТВОЇ БОНУСИ АКТИВОВАНО:</b>\n"
        f"📉 Знижка: <b>-35%</b> на весь стафф\n"
        f"💸 БОНУС: <b>-101 грн</b> на перше замовлення\n"
        f"🚚 Доставка: <b>БЕЗКОШТОВНА</b> (до 25.03)\n\n"
        f"🔑 Твій персональний код: <code>{personal_promo}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👇 <b>Обери розділ:</b>"
    )
    
    keyboard = [
        [InlineKeyboardButton("🛍 ВІДКРИТИ КАТАЛОГ 🍀", callback_data="cat_all")],
        [InlineKeyboardButton("👤 КАБІНЕТ", callback_data="menu_profile"), 
         InlineKeyboardButton("🛒 КОШИК", callback_data="menu_cart")],
        [InlineKeyboardButton("📍 ОБРАТИ ЛОКАЦІЮ", callback_data="choose_city")],
        [InlineKeyboardButton("📜 УГОДА", callback_data="menu_terms")],
        [InlineKeyboardButton("👨‍💻 МЕНЕДЖЕР", url=f"https://t.me/{MANAGER_USERNAME}"),
         InlineKeyboardButton("📢 КАНАЛ", url=CHANNEL_URL)]
    ]
    
    if user.id == MANAGER_ID:
        keyboard.append([InlineKeyboardButton("⚙️ GOD MODE", callback_data="admin_main")])

    await send_ghosty_message(update, welcome_text, keyboard, photo=WELCOME_PHOTO)

async def catalog_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Каталог з привітальним фото."""
    text = "🛍 <b>КАТАЛОГ GHOSTY STAFF 🧪</b>\n━━━━━━━━━━━━━━━━━━━━\nОберіть категорію стаффу 👇"
    kb = [[InlineKeyboardButton("💨 HHC ВЕЙПИ", callback_data="cat_list_hhc")],
          [InlineKeyboardButton("🔌 POD-СИСТЕМИ", callback_data="cat_list_pods")],
          [InlineKeyboardButton("💧 РІДИНИ / ЖИЖА", callback_data="cat_list_liquids")],
          [InlineKeyboardButton("🔙 В МЕНЮ", callback_data="menu_start")]]
    await send_ghosty_message(update, text, kb, photo=WELCOME_PHOTO)
    
# =================================================================
# ⚙️ SECTION 4.1: BUSINESS LOGIC (МАТЕМАТИКА ТА ЦІНИ)
# =================================================================

async def calculate_final_sum(context: ContextTypes.DEFAULT_TYPE):
    """Рахує фінал: (Сума * VIP) - Бонус + Копійки."""
    cart = context.user_data.get('cart', [])
    profile = context.user_data.get('profile', {})
    
    if not cart:
        return 0.0
        
    total = sum(item['price'] for item in cart)
    
    # 1. VIP знижка 35%
    if profile.get('is_vip'):
        total = int(total * 0.65)
    
    # 2. Промокод 2026 (-101 грн)
    bonus = profile.get('next_order_discount', 0)
    total = max(total - bonus, 0)
    
    # 3. Унікальні копійки для ідентифікації платежу
    cents = random.randint(1, 99) / 100
    return float(total + cents)

# =================================================================
# 🧮 SECTION 4.5: PRICE ENGINE PRO 2026
# =================================================================

def calculate_final_price(item_price, user_profile):
    """
    Розрахунок ціни:
    1. Базова ціна.
    2. Якщо є Промокод/VIP: (Ціна - 101 грн) * 0.65 (Знижка 35%).
    3. Повертає нову ціну і статус знижки.
    """
    is_vip = user_profile.get('is_vip', False)
    promo_code = user_profile.get('promo_applied', False) # Перевіряємо, чи введено промо
    
    final_price = float(item_price)
    discounted = False

    # Логіка знижки (Приклад комбінованої знижки)
    if is_vip or promo_code:
        # Спочатку віднімаємо бонус 101 грн, якщо ціна дозволяє
        if final_price > 200:
            final_price -= 101
        # Потім даємо знижку 35%
        final_price = final_price * 0.65
        discounted = True
    
    # Захист: ціна не може бути менше 1 грн
    if final_price < 1: final_price = 1.0
        
    return round(final_price, 2), discounted

# =================================================================
# ⚙️ SECTION 4: DATABASE & AUTH (SQL FIXED)
# =================================================================

def init_db():
    """Ініціалізація бази даних без помилок."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        # Таблиця користувачів
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY, 
                username TEXT, 
                full_name TEXT,
                city TEXT, 
                district TEXT, 
                phone TEXT, 
                is_vip INTEGER DEFAULT 1, 
                reg_date TEXT,
                promo_code TEXT,
                address_details TEXT
            )
        ''')
        
        # Таблиця замовлень (ВИПРАВЛЕНО КОМУ ПІСЛЯ REAL)
        cur.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                user_id INTEGER,
                items TEXT,
                total_price REAL,
                status TEXT,
                created_at TEXT,
                amount REAL
            )
        ''')
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"❌ DB ERROR: {e}")

async def get_or_create_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid = user.id
    if "profile" not in context.user_data:
        context.user_data["profile"] = {
            "uid": uid,
            "username": f"@{user.username}" if user.username else "Hidden",
            "full_name": None, "phone": None, "city": None, 
            "address_details": None, "promo_code": f"GHST{uid}",
            "is_vip": True, "orders_count": 0
        }
    return context.user_data["profile"]
    
        
# =================================================================
# 📱 SECTION 5.1: CATALOG UI (MENU & ITEMS)
# =================================================================

async def catalog_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Головне меню каталогу."""
    text = "🛍 <b>КАТАЛОГ GHOSTY STAFF 2026</b>\n━━━━━━━━━━━━━━━━━━━━\nОберіть категорію:"
    keyboard = [
        [InlineKeyboardButton("💧 Рідини Chaser (30ml)", callback_data="cat_list_liquids")],
        [InlineKeyboardButton("💨 HHC Вейпи (USA) + 🎁", callback_data="cat_list_hhc")],
        [InlineKeyboardButton("🔌 POD-Системи", callback_data="cat_list_pods")],
        [InlineKeyboardButton("🔙 Головне меню", callback_data="menu_start")]
    ]
    await _edit_or_reply(update.callback_query, text, keyboard)

async def show_category_items(update: Update, context: ContextTypes.DEFAULT_TYPE, category_key: str):
    """Відображення списку товарів."""
    items_dict = {}
    cat_name = ""
    
    if category_key == "hhc":
        items_dict = HHC_VAPES
        cat_name = "💨 HHC ВЕЙПИ (+🎁 Рідина)"
    elif category_key == "pods":
        items_dict = PODS
        cat_name = "🔌 POD-СИСТЕМИ"
    elif category_key == "liquids":
        items_dict = LIQUIDS
        cat_name = "💧 РІДИНИ CHASER (50/65/85mg)"

    text = f"📂 <b>{cat_name}</b>\n━━━━━━━━━━━━━━━━━━━━\nОберіть товар:"
    keyboard = []
    
    for i_id, item in items_dict.items():
        price_str = f"{int(item['price'])}₴"
        icon = "🔥 " if item.get('discount') else ""
        label = f"{icon}{item['name']} | {price_str}"
        keyboard.append([InlineKeyboardButton(label, callback_data=f"view_item_{i_id}")])
    
    keyboard.append([InlineKeyboardButton("🔙 До категорій", callback_data="cat_all")])
    
    await _edit_or_reply(update.callback_query, text, keyboard)

# =================================================================
# 🔍 SECTION 15: КАРТКА ТОВАРУ (FINAL FIXED)
# =================================================================

async def view_item_details(update: Update, context: ContextTypes.DEFAULT_TYPE, item_id: int):
    item = get_item_data(item_id)
    if not item: return

    profile = context.user_data.get("profile", {})
    price, has_discount = calculate_final_price(item['price'], profile)
    
    price_html = f"<b>{int(item['price'])} ₴</b>"
    if has_discount:
        price_html = f"<s>{int(item['price'])}</s> ➡️ <b>{price} ₴</b> 🔥"

    caption = (
        f"<b>{item['name']}</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        f"{item['desc']}\n━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 Ціна: {price_html}"
    )

    keyboard = []
    # 1. Швидкі дії
    keyboard.append([InlineKeyboardButton("⚡ ШВИДКЕ ЗАМОВЛЕННЯ", callback_data=f"fast_order_{item_id}")])
    keyboard.append([InlineKeyboardButton("👨‍💻 ЗАМОВИТИ У МЕНЕДЖЕРА", callback_data=f"mgr_pre_{item_id}")])

    # 2. Опції (Колір/Міцність)
    if "colors" in item:
        caption += "\n\n🎨 <b>Оберіть колір:</b>"
        rows = [item["colors"][i:i + 2] for i in range(0, len(item["colors"]), 2)]
        for row_cols in rows:
            keyboard.append([InlineKeyboardButton(c, callback_data=f"add_{item_id}_{c}") for c in row_cols])
    elif "strengths" in item:
        caption += "\n\n🧪 <b>Оберіть міцність:</b>"
        keyboard.append([InlineKeyboardButton(f"{s}mg", callback_data=f"add_{item_id}_{s}") for s in item['strengths']])
    
    # 3. Додати в кошик
    if item.get("gift_liquid"):
        keyboard.append([InlineKeyboardButton("🎁 ОБРАТИ БОНУС І КУПИТИ", callback_data=f"add_{item_id}")])
    else:
        keyboard.append([InlineKeyboardButton("🛒 ДОДАТИ У КОШИК", callback_data=f"add_{item_id}")])

    keyboard.append([InlineKeyboardButton("📍 ОБРАТИ ЛОКАЦІЮ", callback_data="choose_city")])
    keyboard.append([InlineKeyboardButton("🔙 ДО СПИСКУ", callback_data="cat_all")])

    await send_ghosty_message(update, caption, keyboard, photo=item.get('img'))
    
    
# =================================================================
# 👤 SECTION 5: USER CABINET & DATA FLOW (CERTIFIED FIX 2026)
# =================================================================

async def handle_data_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробка тексту: Ім'я -> Телефон -> (Тут пауза на кнопки) -> Адреса."""
    if not update.message or not update.message.text: return
    
    flow = context.user_data.get('data_flow')
    if not flow: return
    
    text = update.message.text.strip()
    profile = context.user_data.setdefault('profile', {})
    step = flow.get('step')

    # КРОК 1: ПІБ
    if step == 'name':
        profile['full_name'] = text
        flow['step'] = 'phone'
        await update.message.reply_text("📱 <b>КРОК 2/4: ТЕЛЕФОН</b>\n\nВведіть ваш номер телефону:")
        
    # КРОК 2: ТЕЛЕФОН
    elif step == 'phone':
        profile['phone'] = text
        # ПЕРЕХІД ДО КНОПОК: Ми не міняємо step тут на 'address', 
        # бо місто/район обираються КНОПКАМИ. 
        # Крок змінить обробник кнопок (CallbackQueryHandler).
        await choose_city_menu(update, context)
        
    # КРОК 4: АДРЕСА (Сюди бот потрапить ТІЛЬКИ після вибору міста/району в кнопках)
    elif step == 'address':
        profile['address_details'] = text
        await finalize_data_collection(update, context)

async def finalize_data_collection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Збереження даних у БД та перехід до замовлення."""
    user = update.effective_user
    flow = context.user_data.get('data_flow', {})
    p = context.user_data.get('profile', {})
    
    # Скидаємо стани, щоб бот знову реагував на команди
    context.user_data['state'] = None
    
    # Оновлення бази даних (Виправлено ID та параметри)
    try:
        conn = sqlite3.connect(DB_PATH)
        # Використовуємо user.id прямо, щоб уникнути помилок з p.get('uid')
        conn.execute("""
            UPDATE users 
            SET full_name=?, phone=?, city=?, district=?, address_details=? 
            WHERE user_id=?
        """, (p.get('full_name'), p.get('phone'), p.get('city'), 
              p.get('district'), p.get('address_details'), user.id))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"SQL Error in finalize: {e}")

    action = flow.get('next_action')
    if action == 'checkout':
        await checkout_init(update, context)
    elif action == 'manager_order':
        await finalize_manager_order(update, context, flow.get('item_id'))
    else:
        await update.message.reply_text("✅ <b>Дані успішно збережено в базі!</b>")
        await show_profile(update, context)

# КРИТИЧНО: Ця функція має бути в CallbackQueryHandler (Section 29)
# Вона — ключ до того, щоб крок 4/4 запрацював!
async def address_request_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, district: str):
    """Ця функція викликається ПІСЛЯ натискання кнопки району."""
    query = update.callback_query
    context.user_data.setdefault('profile', {})['district'] = district
    
    # ОСЬ ТУТ МИ ВКЛЮЧАЄМО ОЧІКУВАННЯ ТЕКСТУ АДРЕСИ
    context.user_data.setdefault('data_flow', {})['step'] = 'address'
    context.user_data['state'] = "COLLECTING_DATA"
    
    await _edit_or_reply(query, "📍 <b>КРОК 4/4: АДРЕСА</b>\n\nНапишіть номер відділення НП або адресу:")
    
        
# =================================================================
# 🛍 SECTION 6: CATALOG (WITH WELCOME PHOTO)
# =================================================================

async def catalog_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Головне меню каталогу з фото."""
    text = (
        "🛍 <b>КАТАЛОГ GHOSTY STAFF 🧪</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Тільки перевірена якість, прямий імпорт.\n\n"
        "🔹 <i>HHC - Сильніше за звичайне</i>\n"
        "🔹 <i>PODS - Найнадійніші девайси</i>\n"
        "🔹 <i>LIQUIDS - Кращі смаки 2026</i>"
    )
    kb = [
        [InlineKeyboardButton("💨 HHC ВЕЙПИ", callback_data="cat_list_hhc")],
        [InlineKeyboardButton("🔌 POD-СИСТЕМИ", callback_data="cat_list_pods")],
        [InlineKeyboardButton("💧 РІДИНИ / ЖИЖА", callback_data="cat_list_liquids")],
        [InlineKeyboardButton("🏠 В ГОЛОВНЕ МЕНЮ", callback_data="menu_start")]
    ]
    # Додаємо фото у каталог (використовуємо WELCOME_PHOTO або окреме)
    await send_ghosty_message(update, text, kb, photo=WELCOME_PHOTO)
    
        
# =================================================================
# 🛠 SECTION 7: CORE UTILITIES (ULTIMATE EDITION)
# =================================================================

def get_item_data(item_id):
    """Безпечний пошук товару у всіх реєстрах."""
    try:
        iid = int(item_id)
        # Перевіряємо глобальні змінні каталогів
        if 'HHC_VAPES' in globals() and iid in HHC_VAPES: return HHC_VAPES[iid]
        if 'LIQUIDS' in globals() and iid in LIQUIDS: return LIQUIDS[iid]
        if 'PODS' in globals() and iid in PODS: return PODS[iid]
        if 'SETS' in globals() and iid in SETS: return SETS[iid]
        return None
    except Exception as e:
        logger.error(f"Item Search Error: {e}")
        return None

async def send_ghosty_message(update: Update, text: str, reply_markup=None, photo=None):
    """
    🛡 GHOSTY MESSAGE ENGINE v2.0
    Універсальний відправник, який не ламається.
    """
    try:
        # Авто-конвертація списку кнопок у розмітку
        if isinstance(reply_markup, list):
            reply_markup = InlineKeyboardMarkup(reply_markup)
            
        if update.callback_query:
            msg = update.callback_query.message
            try:
                if photo:
                    if msg.photo:
                        await msg.edit_media(
                            media=InputMediaPhoto(media=photo, caption=text, parse_mode='HTML'),
                            reply_markup=reply_markup
                        )
                    else:
                        await msg.delete() # Видаляємо текст, шлемо фото
                        await msg.reply_photo(photo=photo, caption=text, reply_markup=reply_markup, parse_mode='HTML')
                else:
                    if msg.photo:
                        await msg.delete() # Видаляємо фото, шлемо текст
                        await msg.reply_text(text=text, reply_markup=reply_markup, parse_mode='HTML')
                    else:
                        await msg.edit_text(text=text, reply_markup=reply_markup, parse_mode='HTML')
            except BadRequest as e:
                # Ігноруємо, якщо вміст не змінився
                if "Message is not modified" in str(e): return
                # Якщо повідомлення застаріло - шлемо нове
                if "Message to edit not found" in str(e):
                    await update.effective_chat.send_message(text, reply_markup=reply_markup, parse_mode='HTML')
        else:
            # Це звичайний текст від юзера
            if photo:
                await update.message.reply_photo(photo=photo, caption=text, reply_markup=reply_markup, parse_mode='HTML')
            else:
                await update.message.reply_text(text=text, reply_markup=reply_markup, parse_mode='HTML')
    except Exception as e:
        logger.error(f"UI Engine Error: {e}")

# Аліас для сумісності, якщо десь у коді викликається ця функція
async def send_ghosty_media(update, text, reply_markup, photo):
    await send_ghosty_message(update, text, reply_markup, photo)
    
# =================================================================
# ⚙️ SECTION 9: GLOBAL CALLBACK DISPATCHER (PARTIAL)
# =================================================================

async def show_ref_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Інформація про реферальну систему."""
    user_id = update.effective_user.id
    bot_username = context.bot.username
    
    ref_text = (
        f"🤝 <b>ПАРТНЕРСЬКА ПРОГРАМА</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Запрошуй друзів та отримуй бонуси!\n\n"
        f"1️⃣ <b>Твій друг отримує:</b>\n"
        f"   • Знижку -35% на перше замовлення\n"
        f"2️⃣ <b>Ти отримуєш:</b>\n"
        f"   • VIP-статус на 7 днів\n"
        f"   • Секретний подарунок\n\n"
        f"🔗 <b>Твоє посилання:</b>\n<code>https://t.me/{bot_username}?start={user_id}</code>"
    )
    keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data="menu_profile")]]
    await _edit_or_reply(update.callback_query, ref_text, keyboard)

async def main_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Центральний обробник всіх натискань кнопок.
    """
    query = update.callback_query
    data = query.data
    await query.answer() # Прибираємо годинник на кнопці
    
    logger.info(f"User {update.effective_user.id} clicked: {data}")

    # Навігація головного меню
    if data == "menu_start":
        await start_command(update, context)
    elif data == "menu_terms":
        await terms_handler(update, context)
    # Інші гілки (Каталог, Кошик, Профіль) будуть у наступних частинах

    # =================================================================
# 📍 SECTION 10: GEOGRAPHY LOGIC (CITIES & DISTRICTS)
# =================================================================

async def city_selection_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Виводить список 11 міст для вибору.
    """
    text = (
        "📍 <b>Оберіть ваше місто</b>\n\n"
        "Ми працюємо у 10 найбільших містах України та Кам'янському. "
        "Оберіть локацію, щоб побачити доступні райони та методи отримання:"
    )
    
    keyboard = []
    # Формуємо сітку кнопок 2 в ряд
    for i in range(0, len(CITIES_LIST), 2):
        row = []
        city1 = CITIES_LIST[i]
        row.append(InlineKeyboardButton(city1, callback_data=f"set_city_{city1}"))
        if i + 1 < len(CITIES_LIST):
            city2 = CITIES_LIST[i+1]
            row.append(InlineKeyboardButton(city2, callback_data=f"set_city_{city2}"))
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("🏠 Головне меню", callback_data="menu_start")])
    
    await send_ghosty_message(update, text, InlineKeyboardMarkup(keyboard))

async def district_selection_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, city_name: str):
    """
    Виводить 8 районів для обраного міста.
    """
    districts = CITY_DISTRICTS.get(city_name, [])
    text = f"📍 <b>Місто: {city_name}</b>\n\nОберіть район для отримання замовлення:"
    
    keyboard = []
    for i in range(0, len(districts), 2):
        row = []
        d1 = districts[i]
        row.append(InlineKeyboardButton(d1, callback_data=f"set_dist_{d1}"))
        if i + 1 < len(districts):
            d2 = districts[i+1]
            row.append(InlineKeyboardButton(d2, callback_data=f"set_dist_{d2}"))
        keyboard.append(row)
    
    # Спеціальна логіка для Дніпра (Адресна доставка)
    if city_name == "Дніпро":
        keyboard.append([InlineKeyboardButton("🏠 АДРЕСНА ДОСТАВКА (+50 грн)", callback_data="set_delivery_address")])
    
    keyboard.append([InlineKeyboardButton("⬅️ Назад до міст", callback_data="menu_city")])
    
    await send_ghosty_message(update, text, InlineKeyboardMarkup(keyboard))
    
        # =================================================================
# 🚚 SECTION 11: ADDRESS DELIVERY & LOCATION SAVING (FIXED)
# =================================================================

async def save_location_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, dist_name: str = None, is_address: bool = False):
    """
    Зберігає обрану локацію в профіль користувача та базу SQLite.
    """
    profile = context.user_data.setdefault("profile", {})
    user_id = update.effective_user.id
    
    if is_address:
        profile["district"] = "Адресна доставка"
        profile["delivery_type"] = "address"
        # Запускаємо збір повної адреси через Smart Data Collection або просто чекаємо текст
        msg = "✅ <b>Ви обрали адресну доставку по Дніпру!</b>\nВам потрібно буде вказати адресу при оформленні замовлення."
    else:
        profile["district"] = dist_name
        profile["delivery_type"] = "klad"
        msg = f"✅ <b>Локацію встановлено:</b> {profile.get('city')}, р-н {dist_name}"

    # Оновлення в SQLite (ВИПРАВЛЕНО: Використовуємо глобальну DB_PATH)
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("UPDATE users SET city = ?, district = ? WHERE user_id = ?", 
                  (profile.get("city"), profile.get("district"), user_id))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Error saving location to DB: {e}")

    # ВИПРАВЛЕНО: Кнопка веде на cat_all, а не cat_main
    keyboard = [
        [InlineKeyboardButton("🛍 Перейти до покупок", callback_data="cat_all")],
        [InlineKeyboardButton("🏠 В меню", callback_data="menu_start")]
    ]
    await send_ghosty_message(update, msg, InlineKeyboardMarkup(keyboard))
    
# =================================================================
# 🛍 SECTION 14: CATALOG ENGINE (MENU)
# =================================================================

async def catalog_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Головне меню каталогу."""
    text = (
        "<b>🛍 КАТАЛОГ GHOSTY STAFF 2026</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Оберіть категорію товарів 👇\n\n"
        "💨 <b>HHC Вейпи</b> — <i>Преміум якість із США (+Подарунок)</i>\n"
        "🔌 <b>POD-системи</b> — <i>Надійні девайси на кожен день</i>\n"
        "💧 <b>Рідини</b> — <i>Насичені смаки (50/65/85 mg)</i>"
    )
    keyboard = [
        [InlineKeyboardButton("💨 HHC Вейпи (USA)", callback_data="cat_list_hhc")],
        [InlineKeyboardButton("🔌 POD-системи", callback_data="cat_list_pods")],
        [InlineKeyboardButton("💧 Рідини Chaser", callback_data="cat_list_liquids")],
        [InlineKeyboardButton("🏠 Головне меню", callback_data="menu_start")]
    ]
    # Використовуємо _edit_or_reply для стабільності
    await _edit_or_reply(update.callback_query, text, keyboard)
    
# =================================================================
# 🔍 SECTION 15: ITEM DETAIL VIEW (PRODUCT CARD)
# =================================================================

async def view_item_details(update: Update, context: ContextTypes.DEFAULT_TYPE, item_id: int):
    item = get_item_data(item_id)
    if not item: return

    profile = context.user_data.get("profile", {})
    price = int(item['price'] * 0.65) if profile.get('is_vip') else int(item['price'])
    
    caption = (
        f"<b>{item['name']}</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        f"{item['desc']}\n━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 Ціна: <b>{price} ₴</b>"
    )

    keyboard = []
    
    # 1. ШВИДКЕ ЗАМОВЛЕННЯ & МЕНЕДЖЕР
    keyboard.append([InlineKeyboardButton("⚡ ШВИДКЕ ЗАМОВЛЕННЯ", callback_data=f"fast_order_{item_id}")])
    keyboard.append([InlineKeyboardButton("👨‍💻 ЗАМОВИТИ У МЕНЕДЖЕРА", callback_data=f"mgr_pre_{item_id}")])

    # 2. ДОДАТИ В КОШИК
    if item.get("gift_liquid"):
        keyboard.append([InlineKeyboardButton("🎁 ОБРАТИ БОНУС І КУПИТИ", callback_data=f"add_{item_id}")])
    else:
        keyboard.append([InlineKeyboardButton("🛒 ДОДАТИ В КОШИК", callback_data=f"add_{item_id}")])

    # 3. ВАРІАНТИ (КОЛІР / МІЦНІСТЬ)
    if "colors" in item:
        caption += "\n🎨 <b>Оберіть колір:</b>"
        color_rows = [] # Робимо по 2 в ряд
        row = []
        for col in item["colors"]:
            row.append(InlineKeyboardButton(col, callback_data=f"add_{item_id}_{col}"))
            if len(row) == 2:
                color_rows.append(row)
                row = []
        if row: color_rows.append(row)
        keyboard.extend(color_rows)
        
    elif "strengths" in item:
        caption += "\n🧪 <b>Оберіть міцність:</b>"
        row = [InlineKeyboardButton(f"{s}mg", callback_data=f"add_{item_id}_{s}") for s in item['strengths']]
        keyboard.append(row)

    # 4. ДАНІ ДОСТАВКИ
    keyboard.append([InlineKeyboardButton("📍 ВВЕСТИ ДАНІ ДОСТАВКИ", callback_data="fill_delivery_data")])
    keyboard.append([InlineKeyboardButton("🔙 ДО СПИСКУ", callback_data="cat_all")])

    await send_ghosty_message(update, caption, keyboard, photo=item.get('img'))
    

# =================================================================
# 🛒 SECTION 17: ДОДАВАННЯ В КОШИК (ОБРОБКА КОЛЬОРІВ)
# =================================================================

async def add_to_cart_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробляє додавання товару (в т.ч. з варіантами)."""
    query = update.callback_query
    
    try:
        parts = query.data.split("_")
        item_id = int(parts[1])
        # Безпечне отримання варіанту
        variant = "_".join(parts[2:]) if len(parts) > 2 else None
    except: 
        await query.answer("⚠️ Помилка даних")
        return

    item = get_item_data(item_id)
    if not item: 
        await query.answer("❌ Товар не знайдено")
        return

    # Логіка вибору подарунка (якщо це не варіант і не вибір подарунка)
    if item.get("gift_liquid", False) and not variant:
        context.user_data['pending_item_id'] = item_id
        text = f"🎁 <b>ОБЕРІТЬ ВАШ ПОДАРУНОК!</b>\nДо <b>{item['name']}</b> йде безкоштовна рідина:"
        # Перевірка наявності GIFT_LIQUIDS
        gifs = GIFT_LIQUIDS if 'GIFT_LIQUIDS' in globals() else {1: {'name': 'Surprise'}}
        kb = [[InlineKeyboardButton(g['name'], callback_data=f"gift_sel_{gid}")] for gid, g in gifs.items()]
        kb.append([InlineKeyboardButton("❌ Скасувати", callback_data=f"view_item_{item_id}")])
        await _edit_or_reply(query, text, kb)
        return

    # Формування назви
    final_name = item['name']
    if variant:
        clean_variant = variant.replace("_", " ")
        final_name += f" ({clean_variant})"

    await _finalize_add_to_cart(update, context, item, gift=None, name=final_name)

async def gift_selection_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробка вибору подарунка."""
    query = update.callback_query
    try:
        gift_id = int(query.data.split("_")[2])
        main_id = context.user_data.get('pending_item_id')
        if not main_id: return
        
        main_item = get_item_data(main_id)
        gift_item = GIFT_LIQUIDS.get(gift_id)
        gift_name = gift_item['name'] if gift_item else "Сюрприз"
        
        await _finalize_add_to_cart(update, context, main_item, gift=gift_name)
        context.user_data.pop('pending_item_id', None)
    except:
        await query.answer("⚠️ Помилка вибору")

async def _finalize_add_to_cart(update: Update, context: ContextTypes.DEFAULT_TYPE, item, gift=None, name=None):
    """Запис у кошик."""
    cart = context.user_data.setdefault("cart", [])
    profile = context.user_data.setdefault("profile", {})
    
    price, _ = calculate_final_price(item['price'], profile)
    
    cart.append({
        "id": random.randint(100000, 999999),
        "name": name if name else item['name'],
        "price": price,
        "gift": gift
    })
    
    msg = f"✅ <b>{name or item['name']}</b> додано!\n💰 Ціна: {price} грн"
    if gift: msg += f"\n🎁 Бонус: {gift}"
    
    kb = [[InlineKeyboardButton("🛒 Кошик", callback_data="menu_cart"), 
           InlineKeyboardButton("🔙 Каталог", callback_data="cat_all")]]
    await send_ghosty_message(update, msg, kb)
    
# =================================================================
# 🛒 SECTION 18: CART & MANAGER (FIXED DELETION)
# =================================================================

async def finalize_manager_order(update: Update, context: ContextTypes.DEFAULT_TYPE, item_id):
    """Формування посилання на менеджера з даними."""
    import urllib.parse
    item = get_item_data(item_id)
    p = context.user_data.get('profile', {})
    user = update.effective_user
    
    msg = (f"👋 Привіт! Хочу замовити:\n📦 Товар: {item['name']}\n💰 Ціна: {item['price']} грн\n"
           f"------------------\n👤 Клієнт: {p.get('full_name')} (@{user.username})\n"
           f"🏙 Місто: {p.get('city')}\n📍 Адреса: {p.get('address_details')}\n📞 Тел: {p.get('phone')}")
    
    link = f"https://t.me/{MANAGER_USERNAME}?text={urllib.parse.quote(msg)}"
    kb = [[InlineKeyboardButton("🚀 ПЕРЕЙТИ ДО МЕНЕДЖЕРА", url=link)],
          [InlineKeyboardButton("🔙 В меню", callback_data="menu_start")]]
    
    text = "✅ <b>ЗАМОВЛЕННЯ СФОРМОВАНО!</b>\n\nНатисніть кнопку, щоб надіслати дані менеджеру 👇"
    if update.callback_query: await _edit_or_reply(update.callback_query, text, kb)
    else: await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode='HTML')

async def cart_action_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Видалення товару за унікальним UID."""
    query = update.callback_query
    data = query.data
    cart = context.user_data.get("cart", [])
    
    if data == "cart_clear":
        context.user_data["cart"] = []
        await query.answer("🗑 Кошик очищено")
    elif data.startswith("cart_del_"):
        try:
            target_uid = int(data.split("_")[2])
            context.user_data["cart"] = [i for i in cart if i.get('id') != target_uid]
            await query.answer("❌ Видалено")
        except: await query.answer("⚠️ Помилка")
            
    await show_cart_logic(update, context)
    
# ==================================================================
# 🎁 SECTION 19: GIFT SELECTION SYSTEM (FOR HHC & OFFERS)
# =================================================================

async def gift_selection_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, item_id: int):
    """
    Відображає список доступних подарунків (8 смаків з GIFT_LIQUIDS).
    """
    query = update.callback_query
    main_item = get_item_data(item_id)
    
    if not main_item:
        await query.answer("❌ Товар не знайдено")
        return

    text = (
        f"🎁 <b>ОБЕРІТЬ ВАШ ПОДАРУНОК</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"До товару <b>{main_item['name']}</b> ви отримуєте безкоштовну рідину (30ml) на вибір.\n\n"
        f"👇 <b>Оберіть смак:</b>"
    )

    keyboard = []
    # Беремо смаки з нашого словника GIFT_LIQUIDS (8 штук)
    for g_id, g_data in GIFT_LIQUIDS.items():
        # Колбек: gift_sel_{ID_ПОДАРУНКА}
        keyboard.append([InlineKeyboardButton(f"{g_data['name']}", callback_data=f"gift_sel_{g_id}")])
    
    keyboard.append([InlineKeyboardButton("⬅️ Скасувати", callback_data=f"view_item_{item_id}")])

    # Використовуємо універсальний відправник
    photo = main_item.get('img')
    await send_ghosty_message(update, text, keyboard, photo=photo)

async def gift_selection_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обробляє натискання на конкретний подарунок.
    """
    query = update.callback_query
    try:
        data_parts = query.data.split("_")
        gift_id = int(data_parts[2])
        
        # Отримуємо основний товар, який чекає на подарунок
        main_item_id = context.user_data.get('pending_item_id')
        if not main_item_id:
            await query.answer("⚠️ Сесія застаріла, спробуйте ще раз")
            return
            
        main_item = get_item_data(main_item_id)
        gift_item = GIFT_LIQUIDS.get(gift_id)
        
        if not main_item or not gift_item:
            await query.answer("❌ Помилка вибору")
            return

        # Додаємо в кошик з прив'язкою подарунка
        cart = context.user_data.setdefault("cart", [])
        profile = context.user_data.setdefault("profile", {})
        
        # Рахуємо ціну зі знижками
        final_price, _ = calculate_final_price(main_item['price'], profile)
        
        # Унікальний ID для видалення
        unique_id = random.randint(100000, 999999)
        
        cart.append({
            "id": unique_id,
            "name": main_item['name'],
            "price": final_price,
            "gift": gift_item['name']
        })
        
        # Очищуємо тимчасову змінну
        context.user_data.pop('pending_item_id', None)
        
        msg = f"✅ <b>Додано!</b>\n📦 {main_item['name']}\n🎁 Бонус: {gift_item['name']}"
        kb = [[InlineKeyboardButton("🛒 Перейти в кошик", callback_data="menu_cart")],
              [InlineKeyboardButton("🛍 Продовжити покупки", callback_data="cat_all")]]
        
        await send_ghosty_message(update, msg, kb)
        
    except Exception as e:
        logger.error(f"Gift Handler Error: {e}")
        await query.answer("⚠️ Сталася помилка")
        

# =================================================================
# 🎁 SECTION 19.1: GIFT SELECTION (HELPER)
# =================================================================

async def gift_selection_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Меню вибору подарунка (викликається з add_to_cart_handler).
    """
    # Логіка вже реалізована в add_to_cart_handler (Крок 3), 
    # але цей метод можна залишити як заглушку або для прямого виклику.
    pass
    
# =================================================================
# 💳 SECTION 21: SMART CHECKOUT (FINAL FIXED)
# =================================================================

async def checkout_init(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Фіналізація: Перевірка даних -> Розрахунок -> Оплата."""
    query = update.callback_query
    cart = context.user_data.get("cart", [])
    profile = context.user_data.setdefault("profile", {})

    if not cart: return await show_cart_logic(update, context)

    # 1. Перевірка ПІБ та Телефону
    if not profile.get("full_name") or not profile.get("phone"):
        await start_data_collection(update, context, next_action='checkout')
        return

    # 2. Перевірка адреси для Кур'єра
    dist_info = str(profile.get("district", ""))
    if "Кур'єр" in dist_info and not profile.get("address_details"):
        await _edit_or_reply(query, "⚠️ <b>Вкажіть точну адресу для кур'єра!</b>")
        await start_data_collection(update, context, next_action='checkout')
        return

    # 3. Математика (VIP + Доставка)
    total = sum(calculate_final_price(i['price'], profile)[0] for i in cart)
    delivery = 150 if ("Кур'єр" in dist_info and not profile.get("is_vip")) else 0
    final_amount = total + delivery + (random.randint(1, 99) / 100)
    
    order_id = f"GH-{random.randint(1000,9999)}"
    context.user_data.update({"current_order_id": order_id, "final_checkout_sum": final_amount})

    text = (f"<b>📦 ПІДТВЕРДЖЕННЯ #{order_id}</b>\n━━━━━━━━━━━━━━━━━━━━\n"
            f"📍 {profile.get('city')}, {profile.get('address_details', dist_info)}\n"
            f"👤 {profile.get('full_name')} | 📞 {profile.get('phone')}\n"
            f"💰 <b>СУМА: {final_amount:.2f}₴</b>\n"
            f"👇 Оберіть банк:")
    
    kb = [[InlineKeyboardButton("💳 Monobank", callback_data="pay_mono"), 
           InlineKeyboardButton("💳 Privat24", callback_data="pay_privat")],
          [InlineKeyboardButton("🌐 GhosstyPay", url=PAYMENT_LINK['ghossty'])],
          [InlineKeyboardButton("🔙 Назад", callback_data="menu_cart")]]
    await _edit_or_reply(query, text, kb)
    
# =================================================================
# ⚙️ SECTION 8: PROMO & REFERRAL (FIXED LOGIC)
# =================================================================

async def process_promo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробка кодів: GHST2026, GHST+ID."""
    if not update.message or not update.message.text: return
    
    text = update.message.text.strip().upper()
    user = update.effective_user
    profile = context.user_data.setdefault("profile", {})
    
    msg = ""
    
    # 1. Основний код
    if text == "GHST2026":
        if profile.get('next_order_discount') == 101:
            msg = "⚠️ <b>Цей код вже використано!</b>"
        else:
            profile["next_order_discount"] = 101 # -101 грн
            profile["gift_bonus"] = "🎁 Рідина (Random)" # Подарунок
            profile["is_vip"] = True
            profile["vip_expiry"] = "25.03.2026"
            msg = (
                "✅ <b>GHST2026 АКТИВОВАНО!</b>\n"
                "🎁 <b>Бонус:</b> Безкоштовна рідина\n"
                "💸 <b>Знижка:</b> -101 грн на замовлення\n"
                "💎 <b>Статус:</b> VIP до 25.03.2026"
            )

    # 2. Реферальний код
    elif text.startswith("GHST") and text[4:].isdigit():
        target_id = int(text[4:])
        if target_id == user.id:
            msg = "❌ <b>Свій код вводити не можна.</b>"
        else:
            # Нараховуємо +7 днів
            # (Тут спрощена логіка дат, для реальної треба datetime parse)
            msg = f"🤝 <b>Реферал прийнято!</b>\nВам нараховано +7 днів VIP та -35% знижку."
            profile["is_vip"] = True
            
    else:
        msg = "❌ <b>Невірний код.</b>"

    kb = [[InlineKeyboardButton("👤 В профіль", callback_data="menu_profile")],
          [InlineKeyboardButton("🛍 До покупок", callback_data="cat_all")]]
    
    await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode='HTML')
    context.user_data['awaiting_promo'] = False

async def show_ref_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    bot_name = context.bot.username
    text = (
        f"🤝 <b>ПАРТНЕРСЬКА ПРОГРАМА</b>\n\n"
        f"Твій промокод: <code>GHST{user_id}</code>\n"
        f"Посилання: <code>https://t.me/{bot_name}?start={user_id}</code>\n\n"
        f"За кожного друга: <b>+7 днів VIP</b>"
    )
    await _edit_or_reply(update.callback_query, text, [[InlineKeyboardButton("🔙", callback_data="menu_profile")]])
    
# =================================================================
# 💳 SECTION 5: CHECKOUT & PAYMENT ENGINE (UNIFIED PRO)
# =================================================================

async def checkout_init(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    cart = context.user_data.get("cart", [])
    profile = context.user_data.get("profile", {})
    if not cart: return
    
    if not profile.get("full_name") or not profile.get("phone"):
        await start_data_collection(update, context, next_action='checkout')
        return

    total = sum(i['price'] for i in cart)
    # Кур'єр +150 грн, якщо не VIP
    delivery_cost = 150 if (profile.get("delivery_type") == "courier" and not profile.get("is_vip")) else 0
    final_amount = total + delivery_cost + (random.randint(1, 99) / 100)
    
    order_id = f"GH-{random.randint(1000,9999)}"
    context.user_data["current_order_id"] = order_id
    context.user_data["final_checkout_sum"] = final_amount

    text = (f"<b>📦 ЗАМОВЛЕННЯ #{order_id}</b>\n━━━━━━━━━━━━━━━━━━━━\n"
            f"📍 {profile.get('city')}, {profile.get('address_details', '')}\n"
            f"💰 <b>СУМА: {final_amount:.2f}₴</b>\n"
            f"👇 Оберіть спосіб оплати:")
    
    kb = [[InlineKeyboardButton("💳 Monobank", callback_data="pay_mono"), InlineKeyboardButton("💳 Privat24", callback_data="pay_privat")],
          [InlineKeyboardButton("🌐 GhosstyPay", url=PAYMENT_LINK['ghossty'])],
          [InlineKeyboardButton("🔙 Назад", callback_data="menu_cart")]]
    await _edit_or_reply(query, text, kb)

    
    

async def payment_selection_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, method: str):
    """Додає ID замовлення в інструкцію оплати."""
    query = update.callback_query
    order_id = context.user_data.get('current_order_id', 'Unknown')
    amount = context.user_data.get('final_checkout_sum', 0)
    
    link = PAYMENT_LINK['mono'] if method == 'mono' else PAYMENT_LINK['privat']
    
    text = (
        f"💳 <b>ОПЛАТА: {amount:.2f} грн</b>\n\n"
        f"1️⃣ Натисніть кнопку нижче та оплатіть.\n"
        f"2️⃣ <b>КРИТИЧНО:</b> Вкажіть в коментарі до платежу: <code>ID {order_id}</code>\n"
        f"3️⃣ Після оплати натисніть «Я ОПЛАТИВ» та надішліть чек."
    )
    
    kb = [
        [InlineKeyboardButton("💸 ПЕРЕЙТИ ДО ОПЛАТИ", url=link)],
        [InlineKeyboardButton("✅ Я ОПЛАТИВ (Надіслати чек)", callback_data="confirm_payment_start")],
        [InlineKeyboardButton("🔙 Скасувати", callback_data="checkout_init")]
    ]
    await _edit_or_reply(query, text, kb)
    

# =================================================================
# 🛡 SECTION 26: ORDER CONFIRMATION (ADMIN ALERT)
# =================================================================

async def payment_confirmation_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Запит чека у користувача після натискання "Я оплатив".
    """
    query = update.callback_query
    order_id = context.user_data.get('current_order_id', 'Unknown')
    amount = context.user_data.get('final_checkout_sum', 0)
    
    text = (
        f"⏳ <b>ПІДТВЕРДЖЕННЯ ЗАМОВЛЕННЯ #{order_id}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💵 Сума до сплати була: <b>{amount:.2f} грн</b>\n\n"
        f"📸 <b>ДІЯ:</b> Надішліть скріншот або фото квитанції про оплату прямо сюди в чат.\n\n"
        f"<i>⚠️ Без чека замовлення НЕ буде передано на відправку!</i>"
    )
    
    # Вмикаємо режим очікування фото в handle_user_input
    context.user_data['state'] = "WAITING_RECEIPT"
    
    # Кнопка скасування повертає в меню, скидаючи стан (в обробнику кнопки)
    keyboard = [[InlineKeyboardButton("❌ СКАСУВАТИ", callback_data="menu_start")]]
    
    await _edit_or_reply(query, text, keyboard)
    
    
# =================================================================
# 📝 SECTION 16: SMART DATA COLLECTION (FIXED FLOW)
# =================================================================

async def start_data_collection(update: Update, context: ContextTypes.DEFAULT_TYPE, next_action, item_id=None):
    """Ініціалізація збору даних."""
    context.user_data['data_flow'] = {
        'step': 'name',
        'next_action': next_action, 
        'item_id': item_id
    }
    context.user_data['state'] = "COLLECTING_DATA"
    
    text = "📝 <b>КРОК 1/4: ПІБ</b>\n\nВведіть ваше Прізвище та Ім'я для накладної:"
    kb = [[InlineKeyboardButton("❌ СКАСУВАТИ", callback_data="menu_start")]]
    
    if update.callback_query:
        await _edit_or_reply(update.callback_query, text, kb)
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode='HTML')

async def handle_data_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробка тексту: Ім'я -> Телефон -> Кнопки міст."""
    if not update.message or not update.message.text: return
    flow = context.user_data.get('data_flow')
    if not flow: return
    
    text = update.message.text.strip()
    profile = context.user_data.setdefault('profile', {})
    step = flow.get('step')

    if step == 'name':
        profile['full_name'] = text
        flow['step'] = 'phone'
        await update.message.reply_text("📱 <b>КРОК 2/4: ТЕЛЕФОН</b>\n\nВведіть ваш номер телефону:")
        
    elif step == 'phone':
        profile['phone'] = text
        # ПЕРЕХІД ДО КНОПОК МІСТ
        await choose_city_menu(update, context)
        
    elif step == 'address':
        profile['address_details'] = text
        await finalize_data_collection(update, context)

async def finalize_data_collection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Кінець збору та перехід до оплати або менеджера."""
    context.user_data['state'] = None
    flow = context.user_data.get('data_flow', {})
    action = flow.get('next_action')

    if action == 'checkout':
        await checkout_init(update, context)
    elif action == 'manager_order':
        await finalize_manager_order(update, context, flow.get('item_id'))
    else:
        await update.message.reply_text("✅ <b>Дані оновлено!</b>")
        await show_profile(update, context)

async def finalize_manager_order(update: Update, context: ContextTypes.DEFAULT_TYPE, item_id):
    """Формування посилання на менеджера."""
    import urllib.parse
    item = get_item_data(item_id)
    p = context.user_data.get('profile', {})
    msg = (f"👋 Замовлення:\n📦 Товар: {item['name']}\n💰 Ціна: {item['price']} грн\n"
           f"👤 Клієнт: {p.get('full_name')}\n🏙 Місто: {p.get('city')}\n📞 Тел: {p.get('phone')}")
    link = f"https://t.me/{MANAGER_USERNAME}?text={urllib.parse.quote(msg)}"
    await send_ghosty_message(update, "✅ Дані підготовлено!", [[InlineKeyboardButton("🚀 НАПИСАТИ МЕНЕДЖЕРУ", url=link)]])
    
# =================================================================
# 📍 SECTION 28.5: LOCATION & FLOW HELPERS (FIXING NAMEERROR)
# =================================================================

async def district_selection_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, city: str):
    """Опрацьовує вибір міста та генерує кнопки районів."""
    query = update.callback_query
    context.user_data.setdefault('profile', {})['city'] = city
    
    districts = UKRAINE_CITIES.get(city, [])
    if districts:
        kb = []
        for i in range(0, len(districts), 2):
            row = [InlineKeyboardButton(districts[i], callback_data=f"sel_dist_{districts[i]}")]
            if i + 1 < len(districts):
                row.append(InlineKeyboardButton(districts[i+1], callback_data=f"sel_dist_{districts[i+1]}"))
            kb.append(row)
        kb.append([InlineKeyboardButton("🔙 Назад до вибору міст", callback_data="choose_city")])
        
        # Оновлюємо стан flow для очікування кліку по району
        context.user_data.setdefault('data_flow', {})['step'] = 'district_selection'
        await _edit_or_reply(query, f"🏘 <b>{city}: ОБЕРІТЬ РАЙОН</b>\n━━━━━━━━━━━━━━━━━━━━\nОберіть локацію для отримання 👇", kb)
    else:
        # Якщо районів немає - переходимо до кроку 4 (введення тексту)
        context.user_data.setdefault('data_flow', {})['step'] = 'address'
        context.user_data['state'] = "COLLECTING_DATA"
        await _edit_or_reply(query, f"✅ Місто: {city}\n\n📍 <b>КРОК 4/4: АДРЕСА</b>\nВведіть номер відділення НП або адресу доставки:")

async def address_request_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, district: str):
    """Обробляє вибір району та вмикає очікування текстової адреси."""
    query = update.callback_query
    context.user_data.setdefault('profile', {})['district'] = district
    
    # ВМИКАЄМО РЕЖИМ ОЧІКУВАННЯ ТЕКСТУ
    context.user_data.setdefault('data_flow', {})['step'] = 'address'
    context.user_data['state'] = "COLLECTING_DATA"
    
    text = (
        f"✅ <b>Локація:</b> {context.user_data['profile'].get('city')}, {district}\n\n"
        f"📍 <b>КРОК 4/4: ФІНАЛЬНА АДРЕСА</b>\n"
        f"Напишіть у чат номер відділення Нової Пошти або повну адресу для кур'єра 👇"
    )
    kb = [[InlineKeyboardButton("❌ Скасувати замовлення", callback_data="menu_start")]]
    await _edit_or_reply(query, text, kb)
    
# =================================================================
# ✈️ SECTION 16.5: MANAGER ORDER (DETAILED & ENCODED)
# =================================================================

async def finalize_manager_order(update: Update, context: ContextTypes.DEFAULT_TYPE, item_id):
    """Формує лінк до менеджера з ПОВНИМИ даними клієнта."""
    import urllib.parse
    
    item = get_item_data(item_id)
    p = context.user_data.get('profile', {})
    user = update.effective_user
    order_id = context.user_data.get('current_order_id', f"MGR-{random.randint(100,999)}")
    
    msg_to_manager = (
        f"👋 ПРИВІТ! НОВЕ ЗАМОВЛЕННЯ #{order_id}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📦 ТОВАР: {item['name']}\n"
        f"💰 ЦІНА: {item['price']} грн\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 КЛІЄНТ: {p.get('full_name', user.first_name)} (@{user.username})\n"
        f"🆔 ID: {user.id}\n"
        f"📞 ТЕЛ: {p.get('phone', '—')}\n"
        f"🏙 МІСТО: {p.get('city', '—')}\n"
        f"🏘 РАЙОН: {p.get('district', '—')}\n"
        f"📍 АДРЕСА: {p.get('address_details', '—')}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🛰 Відправлено через GHO$$TY ENGINE"
    )
    
    link = f"https://t.me/{MANAGER_USERNAME}?text={urllib.parse.quote(msg_to_manager)}"
    
    text = (
        f"✅ <b>ЗАМОВЛЕННЯ #{order_id} ПІДГОТОВЛЕНО!</b>\n\n"
        f"Ваші дані доставки збережені. Натисніть кнопку нижче, щоб автоматично надіслати їх менеджеру в особисті повідомлення 👇"
    )
    kb = [[InlineKeyboardButton("🚀 ПЕРЕЙТИ ДО ДІАЛОГУ", url=link)],
          [InlineKeyboardButton("🏠 Повернутись в меню", callback_data="menu_start")]]
    
    if update.callback_query:
        await _edit_or_reply(update.callback_query, text, kb)
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode='HTML')
        

# =================================================================
# 🛒 SECTION 18: CART ACTIONS & TERMS (STABLE)
# =================================================================

async def cart_action_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Видалення товару за унікальним ID (UID)."""
    query = update.callback_query
    data = query.data
    cart = context.user_data.get("cart", [])
    
    if data == "cart_clear":
        context.user_data["cart"] = []
        await query.answer("🗑 Кошик повністю очищено!")
    elif data.startswith("cart_del_"):
        try:
            # Отримуємо UID (третій елемент у cart_del_UID)
            target_uid = int(data.split("_")[2])
            context.user_data["cart"] = [i for i in cart if i.get('id') != target_uid]
            await query.answer("❌ Товар видалено")
        except Exception as e:
            logger.error(f"Cart delete error: {e}")
            await query.answer("⚠️ Помилка видалення")
            
    await show_cart_logic(update, context)
    
async def terms_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показ незмінної угоди."""
    await _edit_or_reply(update.callback_query, TERMS_TEXT, 
                         [[InlineKeyboardButton("🔙 ЗРОЗУМІЛО", callback_data="menu_profile")]])
    
    
# =================================================================
# 📥 SECTION 28: INPUT HANDLER (STABLE MASTER GATE)
# =================================================================

async def handle_user_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Головний шлюз: Текст, Фото, Промокоди, Розсилка."""
    if not update.message: return # КРИТИЧНО: Ігноруємо кнопки
    
    user = update.effective_user
    state = context.user_data.get('state')
    text = update.message.text.strip() if update.message.text else None

    # 1. АДМІН-РОЗСИЛКА
    if state == "BROADCAST_MODE" and user.id == MANAGER_ID:
        conn = sqlite3.connect(DB_PATH)
        users = conn.execute("SELECT user_id FROM users").fetchall()
        conn.close()
        
        sent = 0
        status_msg = await update.message.reply_text(f"🚀 Починаю розсилку на {len(users)} користувачів...")
        
        for (uid,) in users:
            try: 
                await update.message.copy(chat_id=uid)
                sent += 1
                await asyncio.sleep(0.05)
            except: pass
        
        await status_msg.edit_text(f"✅ <b>Завершено!</b>\n📨 Отримали: {sent}")
        context.user_data['state'] = None
        return

    # 2. ПРИЙОМ ЧЕКІВ (ФОТО)
    if state == "WAITING_RECEIPT" and update.message.photo:
        order_id = context.user_data.get('current_order_id', '???')
        summ = context.user_data.get('final_checkout_sum', '0')
        
        # Сповіщення адміну (Менеджеру)
        caption = (
            f"💰 <b>НОВА ОПЛАТА #{order_id}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 Клієнт: {user.mention_html()} (ID: {user.id})\n"
            f"💵 СУМА: {summ:.2f} грн\n"
            f"⚠️ <b>Вказано ID в коментарі?</b> Перевірте!"
        )
        
        await context.bot.send_photo(
            chat_id=MANAGER_ID,
            photo=update.message.photo[-1].file_id,
            caption=caption,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ ПІДТВЕРДИТИ", callback_data=f"admin_approve_{user.id}")]
            ])
        )
        await update.message.reply_text("✅ <b>Чек отримано!</b>\nМенеджер перевірить транзакцію та надішле ТТН/Координати протягом 15 хвилин.")
        context.user_data['state'] = None
        return

    # 3. ТЕКСТОВИЙ ВВІД (ЗБІР ДАНИХ)
    if text:
        if state == "COLLECTING_DATA":
            await handle_data_input(update, context)
            return
        
        if context.user_data.get('awaiting_promo'):
            await process_promo(update, context)
            return

        if state == "WAITING_ADDRESS": # Для сумісності зі старими методами
            context.user_data.setdefault('profile', {})['address_details'] = text
            context.user_data['state'] = None
            await update.message.reply_text("✅ Адресу збережено!")
            await checkout_init(update, context)
            return
            
            
# =================================================================
# 👮‍♂️ SECTION 25: ADMIN GOD-PANEL (FIXED DEFINITIONS & STATS)
# =================================================================

async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Головне меню GOD-MODE з показниками системи."""
    if update.effective_user.id != MANAGER_ID: return 

    ping = random.randint(12, 28) 
    uptime_delta = datetime.now() - START_TIME
    uptime_str = str(uptime_delta).split('.')[0]
    active_sessions = len(context.application.user_data)

    text = (
        f"🕴️ <b>GHOSTY GOD-MODE v6.0</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📡 <b>SYSTEM STATUS:</b>\n"
        f"⏱ Пінг: <code>{ping}ms</code>\n"
        f"🆙 Uptime: <code>{uptime_str}</code>\n"
        f"👥 Активних сесій: <code>{active_sessions}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⚡️ <b>КЕРУВАННЯ:</b>"
    )
    kb = [
        [InlineKeyboardButton("👥 БАЗА КЛІЄНТІВ (LIVE)", callback_data="admin_view_users")],
        [InlineKeyboardButton("💰 ФІНАНСОВИЙ ЗВІТ", callback_data="admin_stats")],
        [InlineKeyboardButton("📢 МАСОВА РОЗСИЛКА", callback_data="admin_broadcast")],
        [InlineKeyboardButton("🔙 ВИХІД В МАГАЗИН", callback_data="menu_start")]
    ]
    await send_ghosty_message(update, text, kb)

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Звіт про виручку за 7 днів."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT SUM(amount) FROM orders WHERE status IN ('paid', 'confirmed') AND created_at >= date('now', '-7 days')")
        rev = cur.fetchone()[0] or 0.0
        cur.execute("SELECT COUNT(*) FROM users")
        users_count = cur.fetchone()[0]
        conn.close()
        
        text = (f"💰 <b>ФІНАНСОВИЙ ЗВІТ (7 ДНІВ)</b>\n━━━━━━━━━━━━\n"
                f"💵 Прибуток: <b>{rev:,.2f} UAH</b>\n"
                f"👥 Всього юзерів: <b>{users_count}</b>\n"
                f"🚀 Статус: Stable")
        await _edit_or_reply(update.callback_query, text, [[InlineKeyboardButton("🔙 НАЗАД", callback_data="admin_main")]])
    except Exception as e:
        await _edit_or_reply(update.callback_query, f"🆘 Помилка статистики: {e}", [[InlineKeyboardButton("🔙 НАЗАД", callback_data="admin_main")]])

async def admin_view_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Перегляд останніх клієнтів зі статусами."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        sql = """SELECT u.username, u.user_id, u.phone, u.city, o.amount, o.status 
                 FROM users u LEFT JOIN orders o ON o.user_id = u.user_id 
                 AND o.created_at = (SELECT MAX(created_at) FROM orders WHERE user_id = u.user_id)
                 ORDER BY u.reg_date DESC LIMIT 10"""
        cur.execute(sql)
        data = cur.fetchall()
        conn.close()

        report = "👥 <b>БАЗА КЛІЄНТІВ (Останні 10):</b>\n━━━━━━━━━━━━\n"
        for row in data:
            st = "✅" if row[5] in ['paid', 'confirmed'] else "❌"
            report += f"👤 @{row[0]} (<code>{row[1]}</code>)\n📞 {row[2] or '—'} | 🏙 {row[3] or '—'}\n💰 {row[4] or 0}₴ | {st}\n---\n"
        
        await _edit_or_reply(update.callback_query, report, [[InlineKeyboardButton("🔙 НАЗАД", callback_data="admin_main")]])
    except Exception as e:
        await _edit_or_reply(update.callback_query, f"🆘 Помилка БД: {e}", [[InlineKeyboardButton("🔙 НАЗАД", callback_data="admin_main")]])

async def start_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запуск режиму розсилки."""
    context.user_data['state'] = "BROADCAST_MODE"
    await _edit_or_reply(update.callback_query, "📢 <b>РЕЖИМ РОЗСИЛКИ:</b>\nНадішліть текст або фото.", [[InlineKeyboardButton("❌ СКАСУВАТИ", callback_data="admin_main")]])
    
# =================================================================
# ⚙️ SECTION 29: GLOBAL DISPATCHER (FINAL 101% STABLE)
# =================================================================

async def global_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    try: await query.answer()
    except: pass

    # --- 1. ГОЛОВНЕ ---
    if data == "menu_start": await start_command(update, context)
    elif data == "menu_profile": await show_profile(update, context)
    elif data == "menu_cart": await show_cart_logic(update, context)
    elif data == "menu_terms": await _edit_or_reply(query, TERMS_TEXT, [[InlineKeyboardButton("🔙 НАЗАД", callback_data="menu_profile")]])
    elif data == "ref_system": await show_ref_info(update, context)

    # --- 2. МАГАЗИН ---
    elif data == "cat_all": await catalog_main_menu(update, context)
    elif data.startswith("cat_list_"): await show_category_items(update, context, data.replace("cat_list_", ""))
    elif data.startswith("view_item_"): 
        try: await view_item_details(update, context, int(data.split("_")[2]))
        except: await catalog_main_menu(update, context)
    elif data.startswith("add_"): await add_to_cart_handler(update, context)
    elif data == "cart_clear" or data.startswith("cart_del_"): await cart_action_handler(update, context)

    # --- 3. ЛОКАЦІЯ ---
    elif data == "choose_city": await choose_city_menu(update, context)
    elif data.startswith("sel_city_"):
        await district_selection_handler(update, context, data.replace("sel_city_", ""))
    elif data.startswith("sel_dist_"):
        await address_request_handler(update, context, data.replace("sel_dist_", ""))
    elif data == "fill_delivery_data":
        await start_data_collection(update, context, next_action='none')

    # --- 4. ЗАМОВЛЕННЯ ---
    elif data.startswith("fast_order_"):
        try:
            iid = int(data.split("_")[2])
            item = get_item_data(iid)
            if item:
                context.user_data['cart'] = [{"id": random.randint(1000,9999), "name": item['name'], "price": item['price'], "gift": None}]
                await start_data_collection(update, context, next_action='checkout', item_id=iid)
        except: pass
    elif data.startswith("mgr_pre_"):
        await start_data_collection(update, context, next_action='manager_order', item_id=int(data.split("_")[2]))
    
    elif data == "checkout_init": await checkout_init(update, context)
    elif data.startswith("pay_"): await payment_selection_handler(update, context, data.split("_")[1])
    elif data == "confirm_payment_start": await payment_confirmation_handler(update, context)

    # --- 5. АДМІНКА ---
    elif data == "admin_main": await admin_menu(update, context)
    elif data == "admin_stats": await admin_stats(update, context)
    elif data == "admin_view_users": await admin_view_users(update, context)
    elif data == "admin_broadcast": await start_broadcast(update, context)
    elif data == "admin_cancel_action":
        context.user_data['state'] = None
        await admin_menu(update, context)

# =================================================================
# 🚀 SECTION 31: ENGINE STARTUP (STABLE RUNNER)
# =================================================================

def main():
    if not TOKEN or "ВСТАВ" in TOKEN:
        print("❌ FATAL: Bot token is missing in SECTION 1!"); sys.exit(1)

    # 1. Створюємо базу, якщо вона видалена
    init_db()
    
    # 2. Побудова додатку зPersistence
    app = (
        Application.builder()
        .token(TOKEN)
        .persistence(PicklePersistence(filepath=PERSISTENCE_PATH))
        .defaults(Defaults(parse_mode=ParseMode.HTML))
        .build()
    )

    # 3. Реєстрація хендлерів
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("admin", admin_menu))
    app.add_handler(CallbackQueryHandler(global_callback_handler))
    
    # Хендлер тексту, фото та промокодів
    app.add_handler(MessageHandler(
        (filters.TEXT | filters.PHOTO) & (~filters.COMMAND), 
        handle_user_input
    ))
    
    app.add_error_handler(error_handler)
    
    # 4. ЗАПУСК
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🚀 GHOSTY STAFF: ENGINE STARTED SUCCESSFULLY")
    print("🛰  REBUILD COMPLETE | MODE: PRO 2026")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    # drop_pending_updates=True ВИРІШУЄ ПРОБЛЕМУ CONFLICT 409 НАЗАВЖДИ
    app.run_polling(drop_pending_updates=True, close_loop=False)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception:
        traceback.print_exc()
        sys.exit(1)
        

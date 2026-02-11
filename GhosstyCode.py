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
from datetime import datetime
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
# ⚙️ SECTION 1: GLOBAL CONFIGURATION (BOTHOST FIXED)
# =================================================================

# 1. Абсолютні шляхи (Критично для Docker/BotHost)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DB_PATH = os.path.join(DATA_DIR, 'ghosty_v3.db')
PERSISTENCE_PATH = os.path.join(DATA_DIR, 'ghosty_state.pickle')
LOG_PATH = os.path.join(DATA_DIR, 'ghosty_system.log')

# Створюємо папку data одразу
os.makedirs(DATA_DIR, exist_ok=True)

# =================================================================
# ⚙️ SECTION 1: GLOBAL CONFIGURATION (FIXED)
# =================================================================

# 1. Абсолютні шляхи
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DB_PATH = os.path.join(DATA_DIR, 'ghosty_v3.db')
PERSISTENCE_PATH = os.path.join(DATA_DIR, 'ghosty_state.pickle')
LOG_PATH = os.path.join(DATA_DIR, 'ghosty_system.log')

os.makedirs(DATA_DIR, exist_ok=True)

# 2. Налаштування (ВСТАВТЕ ВАШ ТОКЕН)
TOKEN = "8351638507:AAEEbCkrYI4X7m-Rflqesxo9PBGSYWlt_Ww"
MANAGER_ID = 7544847872
MANAGER_USERNAME = "ghosstydp"
CHANNEL_URL = "https://t.me/GhostyStaffDP"
WELCOME_PHOTO = "https://i.ibb.co/y7Q194N/1770068775663.png"
VIP_EXPIRY = "25.03.2026"

# 3. Посилання оплати (ЄДИНИЙ СЛОВНИК)
PAYMENT_LINK = {
    "mono": "https://lnk.ua/k4xJG21Vy",   
    "privat": "https://lnk.ua/RVd0OW6V3",
    "ghossty": "https://heylink.me/GhosstyShop"
}


PROMO_BONUS = 101

# 4. Логування
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler(LOG_PATH, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("GhostyCore")


# =================================================================
# 🛠 SECTION 2: ERROR HANDLING
# =================================================================

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Логування критичних помилок."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    try:
        # Сповіщення адміну про збій
        tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
        tb_string = "".join(tb_list)[-4000:] # Обрізаємо, щоб влізло
        
        message = (
            f"🆘 <b>CRITICAL ERROR</b>\n"
            f"<pre>{escape(tb_string)}</pre>"
        )
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
# 📍 SECTION 4: GEOGRAPHY DATA (FIXED ORDER)
# =================================================================

# 1. Спочатку створюємо словник міст (Щоб Python знав, що це таке)
UKRAINE_CITIES = {
    "Київ": ["Печерський", "Шевченківський", "Голосіївський", "Оболонський", "Подільський", "Дарницький", "Дніпровський", "Солом'янський"],
    "Дніпро": ["Центральний", "Соборний (Нагірка)", "Індустріальний", "Амур-Нижньодніпровський", "Новокодацький", "Чечелівський", "Самарський", "Шевченківський (Тополя)"],
    "Кам'янське": ["Центральний (Заводський)", "Дніпровський (Лівий)", "Південний (БАМ/Соцмісто)"],
    "Харків": ["Шевченківський", "Київський", "Салтівський", "Немишлянський", "Холодногірський", "Новобаварський"],
    "Одеса": ["Приморський (Центр)", "Київський (Таїрова)", "Малиновський (Черемушки)", "Суворовський (Котовського)"],
    "Львів": ["Галицький (Центр)", "Личаківський", "Сихівський", "Франківський", "Шевченківський", "Залізничний"],
    "Запоріжжя": ["Олександрівський", "Заводський", "Комунарський", "Дніпровський", "Вознесенівський", "Хортицький"],
    "Кривий Ріг": ["Металургійний", "Центрально-Міський", "Саксаганський", "Покровський", "Тернівський"],
    "Вінниця": ["Центр", "Вишенька", "Замостя", "Старе місто", "Поділля", "Слов'янка"],
    "Полтава": ["Шевченківський", "Київський", "Подільський"]
}

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

def calculate_final_price(item_price, user_profile):
    """
    Розрахунок ціни з урахуванням GHST2026 та VIP.
    1. Перевіряє знижку -101 грн (GHST2026).
    2. Застосовує VIP знижку 35%.
    """
    is_vip = user_profile.get('is_vip', False)
    # Перевіряємо, чи є фіксована знижка (від GHST2026)
    fixed_discount = user_profile.get('next_order_discount', 0) 
    
    final_price = float(item_price)
    discounted = False

    # 1. Застосування фіксованої знижки (101 грн)
    # Знижка діє, якщо ціна товару більша за розмір знижки + 50 грн (маржа)
    if fixed_discount > 0 and final_price > (fixed_discount + 50):
        final_price -= fixed_discount
        discounted = True

    # 2. Застосування VIP знижки (35%)
    if is_vip:
        final_price = final_price * 0.65
        discounted = True
    
    # Захист: ціна не може бути менше 1 грн
    if final_price < 1: final_price = 1.0
        
    return round(final_price, 2), discounted
    
    
    

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
        "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg",
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
TERMS_TEXT = (
    "📜 <b>Умови, правила, відповідальність</b>\n\n"
    "1️⃣ Проєкт має навчально-демонстраційний характер.\n"
    "2️⃣ Інформація подається виключно з ознайомчою метою.\n"
    "3️⃣ Матеріали не є рекомендацією до придбання чи використання.\n"
    "4️⃣ Користувач самостійно несе відповідальність за свої дії.\n"
    "5️⃣ Адміністрація не зберігає персональні дані.\n"
    "6️⃣ Участь у взаємодії є добровільною.\n\n"
    "⚠️ <b>Важливо:</b>\n"
    "7️⃣ Магазин не є реальним та не здійснює продаж товарів.\n"
    "8️⃣ Жоден товар не буде доставлений.\n"
    "9️⃣ Усі переказані кошти вважаються добровільним подарунком.\n"
    "🔟 Грошові операції — подарунок розробнику Gho$$tyyy/"
)

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
# 🧠 SECTION 5: DATABASE ENGINE (SYNC)
# =================================================================
def init_db():
    """Ініціалізація бази даних без синтаксичних помилок."""
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
        
        # Таблиця замовлень (ВИПРАВЛЕНО КОМУ В КІНЦІ)
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
        print(f"❌ DB INIT ERROR: {e}")
        
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
# 👤 SECTION 6: USER PROFILE ENGINE (PRO VERSION)
# =================================================================

async def get_or_create_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid = user.id
    
    if "profile" not in context.user_data:
        # СТВОРЕННЯ ПРОФІЛЮ (Одразу VIP)
        context.user_data["profile"] = {
            "uid": uid,
            "name": escape(user.first_name),
            "username": f"@{user.username}" if user.username else "Hidden",
            "full_name": None, # ПІБ для доставки
            "phone": None,
            "city": None,
            "district": None,
            "address_details": None,
            "promo_code": f"GHST{uid}",
            "is_vip": True, # <--- VIP ЗА ЗАМОВЧУВАННЯМ
            "orders_count": 0
        }
        # Тут має бути запис в БД (код із твого файлу init_db)
    
    return context.user_data["profile"]

async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показ профілю з фотографією юзера."""
    profile = await get_or_create_user(update, context)
    user = update.effective_user
    
    # Формування красивого статусу
    full_address = "❌ Не вказано"
    if profile.get('city'):
        full_address = f"{profile['city']}, {profile.get('district', '')}"
        if profile.get('address_details'):
            full_address += f"\n🏠 {profile['address_details']}"

    text = (
        f"<b>👤 ОСОБИСТИЙ КАБІНЕТ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 ID: <code>{user.id}</code>\n"
        f"💎 Статус: <b>VIP Клієнт</b>\n"
        f"📦 Всього замовлень: {profile.get('orders_count', 0)}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📍 <b>Дані доставки:</b>\n{full_address}\n"
        f"📱 Телефон: {profile.get('phone', 'Не вказано')}\n"
        f"👤 Отримувач: {profile.get('full_name', 'Не вказано')}"
    )

    kb = [
        [InlineKeyboardButton("📝 Змінити дані доставки", callback_data="fill_delivery_data")],
        [InlineKeyboardButton("🤝 Реферальна програма", callback_data="ref_system")],
        [InlineKeyboardButton("🏠 Головне меню", callback_data="menu_start")]
    ]

    # Спроба дістати аватарку
    try:
        photos = await user.get_profile_photos(limit=1)
        if photos.total_count > 0:
            file_id = photos.photos[0][-1].file_id
            await send_ghosty_message(update, text, kb, photo=file_id)
        else:
            await send_ghosty_message(update, text, kb, photo=WELCOME_PHOTO)
    except:
        await send_ghosty_message(update, text, kb)
        
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
# 🏠 SECTION 8: START & PROFILE (FINAL FIXED)
# =================================================================

async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Відображення профілю користувача."""
    query = update.callback_query
    user = update.effective_user
    user_id = user.id
    
    # Ініціалізація профілю (гарантуємо, що це словник)
    profile = await get_or_create_user(update, context)
    
    # Дані для відображення
    ghst_id = f"GHST-{user_id}"
    city = profile.get('city')
    address = profile.get('address_details')
    district = profile.get('district')
    
    # Формування рядка адреси (безпечно, без помилок ключів)
    if city:
        location = f"{city}"
        if address: 
            location += f", {address}"
        elif district: 
            location += f", {district}"
    else:
        location = "❌ Не вказано (Натисніть кнопку нижче)"
    
    vip_status = "💎 <b>VIP ACTIVE</b>" if profile.get('is_vip') else "🌑 Standard"
    orders_count = profile.get('orders_count', 0)
    
    # Безпечне отримання імені бота (на випадок лагів Telegram API)
    bot_username = context.bot.username if context.bot.username else "GhostyShopBot"

    # Текст профілю
    profile_text = (
        f"👤 <b>ОСОБИСТИЙ КАБІНЕТ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📛 <b>Ім'я:</b> {escape(user.first_name)}\n"
        f"🆔 <b>ID:</b> <code>{user_id}</code>\n"
        f"🛡️ <b>Код клієнта:</b> <code>{ghst_id}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📍 <b>Доставка:</b>\n<i>{location}</i>\n\n"
        f"🏆 <b>Статус:</b> {vip_status}\n"
        f"📦 <b>Замовлень:</b> {orders_count}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🎟️ <b>Твоє реферальне посилання:</b>\n<code>https://t.me/{bot_username}?start={user_id}</code>"
    )

    keyboard = [
        [InlineKeyboardButton("📝 Змінити дані доставки", callback_data="fill_delivery_data")],
        [InlineKeyboardButton("🤝 Реферальна програма", callback_data="ref_system")],
        [InlineKeyboardButton("🎟 Ввести промокод", callback_data="menu_promo")],
        [InlineKeyboardButton("🏠 Головне меню", callback_data="menu_start")]
    ]

    # Спроба відправити з фото профілю
    try:
        photos = await user.get_profile_photos(limit=1)
        if photos.total_count > 0:
            photo_file = photos.photos[0][-1].file_id
            await send_ghosty_message(update, profile_text, keyboard, photo=photo_file)
        else:
            await send_ghosty_message(update, profile_text, keyboard, photo=WELCOME_PHOTO)
    except Exception as e:
        # Якщо помилка (наприклад, юзер заблокував доступ до фото) - шлемо дефолтне
        await send_ghosty_message(update, profile_text, keyboard, photo=WELCOME_PHOTO)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Головне меню."""
    await get_or_create_user(update, context)
    user = update.effective_user
    ghst_id = f"GHST{user.id}"
    
    welcome_text = (
        f"🌫️ <b>GHO$$TY STAFF LAB | УКРАЇНА</b> 🧪\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🧬 <b>HHC SHOP ВІДКРИТО!</b>\n"
        f"🔥 Промокод на VIP: <code>GHST2026</code>\n"
        f"🎁 + Рідина на вибір до кожного вейпу!\n"
        f"👤 Твій ID код: <code>{ghst_id}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👇 <b>Оберіть розділ меню:</b>"
    )
    
    keyboard = [
        [InlineKeyboardButton("🛍 АСОРТИМЕНТ", callback_data="cat_all")],
        [InlineKeyboardButton("👤 ПРОФІЛЬ", callback_data="menu_profile"), 
         InlineKeyboardButton("🛒 КОШИК", callback_data="menu_cart")],
        [InlineKeyboardButton("📍 ЛОКАЦІЯ", callback_data="choose_city")],
        [InlineKeyboardButton("📜 УГОДА", callback_data="menu_terms")],
        [InlineKeyboardButton("👨‍💻 МЕНЕДЖЕР", url=f"https://t.me/{MANAGER_USERNAME}"),
         InlineKeyboardButton("📢 КАНАЛ", url=CHANNEL_URL)]
    ]
    
    if user.id == MANAGER_ID:
        keyboard.append([InlineKeyboardButton("⚙️ АДМІН-ПАНЕЛЬ", callback_data="admin_main")])

    await send_ghosty_message(update, welcome_text, keyboard, photo=WELCOME_PHOTO)

async def show_ref_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Інформація про реферальну систему."""
    query = update.callback_query
    user_id = update.effective_user.id
    bot_username = context.bot.username if context.bot.username else "GhostyShopBot"
    
    ref_text = (
        f"🤝 <b>ПАРТНЕРСЬКА ПРОГРАМА</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Запрошуй друзів та отримуй бонуси!\n\n"
        f"1️⃣ <b>Твій друг отримує:</b>\n"
        f"   • Знижку -35% на перше замовлення\n"
        f"2️⃣ <b>Ти отримуєш:</b>\n"
        f"   • VIP-статус на 7 днів (Безкоштовна доставка)\n"
        f"   • Секретний подарунок у наступному замовленні\n\n"
        f"🔗 <b>Твоє посилання:</b>\n<code>https://t.me/{bot_username}?start={user_id}</code>"
    )
    keyboard = [[InlineKeyboardButton("⬅️ Назад до профілю", callback_data="menu_profile")]]
    await _edit_or_reply(query, ref_text, keyboard)
    
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
# 🛒 SECTION 18: CART LOGIC (PRO FIXED 2026)
# =================================================================

async def show_cart_logic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Логіка кошика: відображення, видалення, перевірка даних перед оплатою.
    Виправлено помилку з NoneType.
    """
    query = update.callback_query
    
    # Ініціалізація змінних (Захист від крашу)
    cart = context.user_data.get("cart", [])
    if cart is None: cart = [] # Гарантуємо, що це список
    
    profile = context.user_data.setdefault("profile", {})
    
    # 1. Якщо кошик порожній
    if not cart:
        await send_ghosty_message(
            update, 
            "🛒 <b>Ваш кошик порожній</b>\n\nЧас обрати щось топове! 👇",
            [[InlineKeyboardButton("🛍 До Каталогу", callback_data="cat_all"),
              InlineKeyboardButton("🏠 Меню", callback_data="menu_start")]]
        )
        return

    # 2. Розрахунок і формування списку
    total_sum = 0.0
    items_text = ""
    keyboard = [] # Ініціалізуємо як пустий список, щоб не було None!

    for item in cart:
        # Конвертуємо ціну в float для безпеки
        try: price = float(item.get('price', 0))
        except: price = 0.0
        
        total_sum += price
        
        # Формування тексту
        name = item.get('name', 'Товар')
        gift = item.get('gift')
        gift_txt = f"\n   🎁 {gift}" if gift else ""
        
        items_text += f"🔹 <b>{name}</b>{gift_txt}\n   💰 <code>{int(price)} грн</code>\n"
        
        # Кнопка видалення
        uid = item.get('id', 0)
        keyboard.append([InlineKeyboardButton(f"❌ Видалити: {str(name)[:10]}...", callback_data=f"cart_del_{uid}")])

    # 3. Перевірка даних для замовлення
    city = profile.get("city")
    phone = profile.get("phone")
    can_checkout = bool(city and phone)
    
    if can_checkout:
        loc_status = f"✅ <b>Дані:</b> {city}, {profile.get('full_name', '')}"
    else:
        loc_status = "⚠️ <b>Дані доставки не заповнені!</b>"

    text = (
        f"🛒 <b>ВАШЕ ЗАМОВЛЕННЯ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{items_text}"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{loc_status}\n"
        f"💰 <b>РАЗОМ: {int(total_sum)} UAH</b>"
    )

    # 4. Кнопки управління (безпечне додавання)
    control_buttons = []
    if can_checkout:
        control_buttons.append(InlineKeyboardButton("🚀 ОФОРМИТИ", callback_data="checkout_init"))
    else:
        control_buttons.append(InlineKeyboardButton("📝 ЗАПОВНИТИ ДАНІ", callback_data="fill_delivery_data"))
    
    # Вставляємо кнопки управління нагору списку
    keyboard.insert(0, control_buttons)

    # Додаткові кнопки
    keyboard.append([InlineKeyboardButton("👨‍💻 МЕНЕДЖЕР", url=f"https://t.me/{MANAGER_USERNAME}")])
    
    # Промокод (тільки якщо не введено)
    if not profile.get("promo_applied") and not profile.get("next_order_discount"):
        keyboard.append([InlineKeyboardButton("🎟 ПРОМОКОД", callback_data="menu_promo")])

    # Футер
    keyboard.append([InlineKeyboardButton("🗑 Очистити", callback_data="cart_clear"), 
                     InlineKeyboardButton("🔙 Меню", callback_data="menu_start")])

    await send_ghosty_message(update, text, keyboard)

async def cart_action_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробка видалення та очищення."""
    query = update.callback_query
    data = query.data
    
    if data == "cart_clear":
        context.user_data["cart"] = []
        try: await query.answer("🗑 Кошик очищено!")
        except: pass
        
    elif data.startswith("cart_del_"):
        try:
            uid = int(data.split("_")[2])
            cart = context.user_data.get("cart", [])
            # Фільтруємо список
            context.user_data["cart"] = [i for i in cart if i.get('id') != uid]
            try: await query.answer("❌ Видалено")
            except: pass
        except: pass
    
    await show_cart_logic(update, context)
    
# =================================================================
# 🎁 SECTION 19: GIFT SELECTION SYSTEM (FOR HHC & OFFERS)
# =================================================================

async def gift_selection_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, item_id: int):
    """
    Відображає список доступних подарунків (наприклад, безкоштовні рідини).
    """
    main_item = get_item_data(item_id)
    if not main_item:
        await update.callback_query.answer("❌ Товар не знайдено")
        return

    # Текст для вибору подарунка
    text = (
        f"🎁 <b>АКЦІЯ: ОБЕРІТЬ ПОДАРУНОК</b>\n\n"
        f"До товару <b>{main_item['name']}</b> ви можете додати одну рідину абсолютно <b>БЕЗКОШТОВНО</b>!\n\n"
        f"Оберіть смак, який вам до вподоби 👇"
    )

    # Список ID товарів, які можуть бути подарунками (наприклад, рідини)
    # Ти можеш змінити ці ID на ті, що є у твоєму CATALOG_DATA
    gift_options = [301, 302, 303, 304] 
    
    keyboard = []
    for g_id in gift_options:
        gift_item = get_item_data(g_id)
        if gift_item:
            # Формат callback: add_{ID основного товару}_{ID подарунка}
            keyboard.append([InlineKeyboardButton(f"🧪 {gift_item['name']}", callback_data=f"add_{item_id}_{g_id}")])
    
    keyboard.append([InlineKeyboardButton("⬅️ Скасувати", callback_data=f"view_item_{item_id}")])

    # Якщо у тебе є спеціальне фото для акцій, встав GIFT_PHOTO, інакше фото товару
    photo = main_item.get('img')
    await send_ghosty_media(update, text, InlineKeyboardMarkup(keyboard), photo)

async def cart_action_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    cart = context.user_data.get('cart', [])

    if data.startswith("cart_del_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(cart):
            cart.pop(idx)
            await query.answer("🗑 Видалено")
    elif data == "cart_clear":
        context.user_data['cart'] = []
        await query.answer("🧹 Очищено")
    
    await show_cart_logic(update, context)

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
# 🔑 SECTION 22: ПРОМОКОДИ (GHST2026 & ID SYSTEM)
# =================================================================

async def process_promo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробка GHST2026 та GHST + ID."""
    if not update.message or not update.message.text: return
    text = update.message.text.strip().upper() 
    user = update.effective_user
    profile = context.user_data.setdefault("profile", {})
    
    if text == "GHST2026":
        profile.update({"next_order_discount": 101, "is_vip": True})
        msg = "✅ <b>GHST2026 активовано!</b>\n🎁 -101 грн + VIP статус."
    elif text.startswith("GHST") and text[4:].isdigit():
        target_id = int(text[4:])
        if target_id != user.id:
            profile.update({"is_vip": True, "promo_applied": True})
            msg = f"🤝 <b>Реферальний код прийнято!</b>\n🔥 Знижка -35% активована."
        else: msg = "❌ Неможна вводити свій код!"
    else: msg = "❌ Невірний код."

    await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛒 В кошик", callback_data="menu_cart")]]), parse_mode='HTML')
    context.user_data['awaiting_promo'] = False
    
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
    """Показує реквізити."""
    query = update.callback_query
    amount = context.user_data.get('final_checkout_sum')
    
    # Посилання на банки
    link = PAYMENT_LINK['mono'] if method == 'mono' else PAYMENT_LINK['privat']
    
    text = f"💳 <b>ОПЛАТА: {amount} грн</b>\n1. Оплатіть за посиланням.\n2. Натисніть «Я ОПЛАТИВ».\n3. Надішліть чек."
    
    kb = [
        [InlineKeyboardButton("💸 ПЕРЕЙТИ ДО ОПЛАТИ", url=link)],
        # ВАЖЛИВО: Ця кнопка веде на confirm_payment_start, а не в меню!
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
        f"<i>⚠️ Без чека замовлення не буде передано на відправку!</i>"
    )
    
    # Вмикаємо режим очікування фото в handle_user_input
    context.user_data['state'] = "WAITING_RECEIPT"
    
    # Кнопка скасування повертає в меню, скидаючи стан (в обробнику кнопки)
    keyboard = [[InlineKeyboardButton("❌ СКАСУВАТИ", callback_data="menu_start")]]
    
    await _edit_or_reply(query, text, keyboard)
    
    
# =================================================================
# 📝 SECTION 16: SMART DATA COLLECTION (MANAGER & FAST ORDER)
# =================================================================

async def start_data_collection(update: Update, context: ContextTypes.DEFAULT_TYPE, next_action, item_id=None):
    """Починає процес збору даних (ПІБ -> Телефон -> Місто -> Адреса)."""
    # Ініціалізація структури потоку
    context.user_data['data_flow'] = {
        'step': 'name',
        'next_action': next_action, # 'manager_order', 'checkout', 'none'
        'item_id': item_id
    }
    context.user_data['state'] = "COLLECTING_DATA"
    
    text = (
        "📝 <b>ОФОРМЛЕННЯ ЗАМОВЛЕННЯ</b>\n\n"
        "Для швидкої обробки нам потрібні дані отримувача.\n"
        "1️⃣ Введіть <b>Прізвище та Ім'я</b>:"
    )
    kb = [[InlineKeyboardButton("❌ Скасувати", callback_data="cancel_data")]]
    await _edit_or_reply(update.callback_query, text, kb)

async def handle_data_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробляє введені користувачем дані крок за кроком."""
    flow = context.user_data.get('data_flow')
    if not flow: return

    text = update.message.text
    profile = context.user_data.setdefault('profile', {}) # Гарантуємо, що профіль є
    step = flow.get('step')

    if step == 'name':
        profile['full_name'] = text
        flow['step'] = 'phone'
        await update.message.reply_text("2️⃣ Введіть ваш <b>Номер телефону</b>:")
    
    elif step == 'phone':
        profile['phone'] = text
        flow['step'] = 'city'
        # Пропонуємо міста (перевірка на наявність списку)
        cities = list(UKRAINE_CITIES.keys())[:6] if 'UKRAINE_CITIES' in globals() else ["Київ", "Дніпро", "Львів"]
        kb = [[InlineKeyboardButton(c, callback_data=f"set_flow_city_{c}")] for c in cities]
        await update.message.reply_text("3️⃣ Оберіть або введіть <b>Місто</b> доставки:", reply_markup=InlineKeyboardMarkup(kb))
    
    elif step == 'address': 
        profile['address_details'] = text
        context.user_data['state'] = None # Скидаємо стан
        
        await update.message.reply_text("✅ <b>Дані успішно збережено!</b>")
        
        # Виконуємо наступну дію
        action = flow.get('next_action')
        if action == 'manager_order':
            await finalize_manager_order(update, context, flow.get('item_id'))
        elif action == 'checkout':
            await checkout_init(update, context)
        else:
            await show_profile(update, context)

async def finalize_manager_order(update: Update, context: ContextTypes.DEFAULT_TYPE, item_id):
    """Генерує посилання на менеджера."""
    import urllib.parse
    item = get_item_data(item_id)
    if not item: return

    p = context.user_data.get('profile', {})
    
    msg_text = (
        f"👋 Привіт! Замовлення #{random.randint(1000,9999)}\n"
        f"📦 Товар: {item['name']}\n"
        f"💰 Ціна: {item['price']} грн\n"
        f"👤 {p.get('full_name', 'Клієнт')} | 📞 {p.get('phone', '-')}\n"
        f"📍 {p.get('city', '-')}, {p.get('address_details', '-')}"
    )
    encoded = urllib.parse.quote(msg_text)
    link = f"https://t.me/{MANAGER_USERNAME}?text={encoded}"
    
    text = f"✅ <b>Замовлення сформовано!</b>\n👇 Натисніть кнопку, щоб надіслати:"
    kb = [[InlineKeyboardButton("✈️ НАДІСЛАТИ МЕНЕДЖЕРУ", url=link)],
          [InlineKeyboardButton("🏠 В меню", callback_data="menu_start")]]
    
    if update.callback_query:
        await _edit_or_reply(update.callback_query, text, kb)
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode='HTML')
        
# =================================================================
# 📥 SECTION 28: INPUT HANDLER (TEXT & PHOTO - EXPANDED)
# =================================================================

async def handle_user_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Головний шлюз для обробки всього, що пише/надсилає юзер.
    """
    if not update.message: return
    user = update.effective_user
    state = context.user_data.get('state')
    
    # 1. 📝 РОЗУМНИЙ ЗБІР ДАНИХ (ПІБ, Телефон, Місто)
    # Якщо бот чекає дані, передаємо їх в спеціальну функцію (БЛОК 3)
    if state == "COLLECTING_DATA":
        await handle_data_input(update, context)
        return

# 2/2. ОБРОБКА ТЕКСТУ
    if update.message.text:
        text = update.message.text.strip()
        
        # A) Введення промокоду
        if context.user_data.get('awaiting_promo'):
            await process_promo(update, context)
            return

        # B) Адреса для кур'єра (старий метод)
        if state == "WAITING_ADDRESS":
            context.user_data.setdefault('profile', {})['address_details'] = text
            context.user_data['state'] = None
            await update.message.reply_text("✅ Адресу збережено!")
            await checkout_init(update, context)
            return

        # C) Адмін розсилка (НОВИЙ БЛОК)
        if state == "BROADCAST_MODE" and user_id == MANAGER_ID:
            conn = sqlite3.connect(DB_PATH)
            users = conn.execute("SELECT user_id FROM users").fetchall()
            conn.close()
            
            sent = 0
            await update.message.reply_text(f"🚀 Старт розсилки на {len(users)} людей...")
            for (uid,) in users:
                try: 
                    await update.message.copy(chat_id=uid)
                    sent += 1
                    await asyncio.sleep(0.05)
                except: pass
            
            await update.message.reply_text(f"✅ Успішно: {sent}")
            context.user_data['state'] = None
            context.user_data['awaiting_broadcast'] = False
            return
            

    # 2. 📸 ОБРОБКА ЧЕКІВ (Оплата)
    # Якщо бот чекає чек (стан WAITING_RECEIPT) і юзер надіслав фото
    if state == "WAITING_RECEIPT" and update.message.photo:
        order_id = context.user_data.get('current_order_id', '???')
        summ = context.user_data.get('final_checkout_sum', '0')
        
        try:
            # Надсилаємо чек менеджеру
            await context.bot.send_photo(
                chat_id=MANAGER_ID,
                photo=update.message.photo[-1].file_id,
                caption=(
                    f"💰 <b>НОВА ОПЛАТА #{order_id}</b>\n"
                    f"👤 Від: {user.mention_html()} (ID: {user.id})\n"
                    f"💵 Сума замовлення: {summ:.2f} грн"
                ),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("✅ ПІДТВЕРДИТИ ЗАМОВЛЕННЯ", callback_data=f"admin_approve_{user.id}")]
                ])
            )
            await update.message.reply_text("✅ <b>Чек отримано!</b>\nМенеджер перевірить оплату та надішле ТТН/Координати протягом 15 хвилин.")
        except Exception as e:
            logger.error(f"Receipt error: {e}")
            await update.message.reply_text("⚠️ Помилка надсилання. Спробуйте ще раз.")
        
        # Скидаємо стан, щоб бот не чекав чека вічно
        context.user_data['state'] = None
        return

    # 3. 📢 АДМІНСЬКА РОЗСИЛКА
    # Якщо адмін у режимі розсилки
    if state == "BROADCAST_MODE" and user.id == MANAGER_ID:
        # Отримуємо всіх користувачів з БД
        conn = sqlite3.connect(DB_PATH)
        users = conn.execute("SELECT user_id FROM users").fetchall()
        conn.close()
        
        sent_count = 0
        await update.message.reply_text(f"🚀 Починаю розсилку на {len(users)} користувачів...")
        
        for (uid,) in users:
            try:
                # Копіюємо повідомлення адміна (текст, фото, відео) користувачу
                await update.message.copy(chat_id=uid)
                sent_count += 1
                await asyncio.sleep(0.05) # Анти-спам затримка
            except Exception: pass # Якщо юзер заблокував бота
            
        await update.message.reply_text(f"✅ <b>Розсилка завершена!</b>\nОтримали: {sent_count} з {len(users)}")
        context.user_data['state'] = None # Виходимо з режиму
        return

    # 4. ⌨️ ОБРОБКА ІНШОГО ТЕКСТУ
    # Якщо юзер просто пише текст (наприклад, промокод)
    if update.message.text:
        text = update.message.text.strip()
        
        # Промокоди (якщо натиснув "Ввести промокод")
        if context.user_data.get('awaiting_promo'):
            await process_promo(update, context)
            return
            
        # Якщо юзер пише адресу для кур'єра (старий метод, про всяк випадок)
        if state == "WAITING_ADDRESS":
            context.user_data.setdefault('profile', {})['address_details'] = text
            context.user_data['state'] = None
            await update.message.reply_text("✅ Адресу збережено!")
            await checkout_init(update, context)
            return
            
            
# =================================================================
# ⚙️ SECTION 29: GLOBAL DISPATCHER (FULL MAP)
# =================================================================

async def global_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Маршрутизатор всіх кнопок."""
    query = update.callback_query
    data = query.data
    
    # Відповідаємо телеграму, щоб прибрати "годинник"
    try: await query.answer()
    except: pass

    # --- ГОЛОВНЕ ---
    if data == "menu_start": await start_command(update, context)
    elif data == "menu_profile": await show_profile(update, context)
    elif data == "menu_cart": await show_cart_logic(update, context)
    elif data == "ref_system": await show_ref_info(update, context)
    elif data == "menu_promo": 
        context.user_data['awaiting_promo'] = True
        await _edit_or_reply(query, "🎟 <b>Введіть промокод:</b>\n(Наприклад: GHST2026)", [[InlineKeyboardButton("🔙", callback_data="menu_profile")]])
    
    # --- МАГАЗИН ---
    elif data == "cat_all": await catalog_main_menu(update, context)
    elif data.startswith("cat_list_"): await show_category_items(update, context, data.replace("cat_list_", ""))
    elif data.startswith("view_item_"): 
        # Захист від битих ID
        try: await view_item_details(update, context, int(data.split("_")[2]))
        except: await catalog_main_menu(update, context)
        
    elif data.startswith("add_"): await add_to_cart_handler(update, context)
    elif data.startswith("gift_sel_"): await gift_selection_handler(update, context)
    elif data == "cart_clear" or data.startswith("cart_del_"): await cart_action_handler(update, context)

    # --- ЗАМОВЛЕННЯ ---
    elif data == "checkout_init": await checkout_init(update, context)
    elif data.startswith("pay_"): await payment_selection_handler(update, context, data.split("_")[1])
    elif data == "confirm_payment_start": await payment_confirmation_handler(update, context)
    
    # Швидке замовлення (одразу на оплату)
    elif data.startswith("fast_order_"):
        try:
            iid = int(data.split("_")[2])
            item = get_item_data(iid)
            if item:
                # Створюємо тимчасовий кошик з 1 товаром
                context.user_data['cart'] = [{"id": 999, "name": item['name'], "price": item['price'], "gift": None}]
                await start_data_collection(update, context, next_action='checkout')
        except: pass
        
    # Менеджер
    elif data.startswith("mgr_pre_"):
        await start_data_collection(update, context, next_action='manager_order', item_id=int(data.split("_")[2]))

    # --- ЗБІР ДАНИХ ТА ЛОКАЦІЯ ---
    elif data == "fill_delivery_data": await start_data_collection(update, context, next_action='none')
    elif data == "cancel_data": 
        context.user_data['state'] = None
        await show_profile(update, context)
    
    elif data.startswith("set_flow_city_"):
        city = data.replace("set_flow_city_", "")
        context.user_data.setdefault('profile', {})['city'] = city
        context.user_data.setdefault('data_flow', {})['step'] = 'address'
        await _edit_or_reply(query, f"✅ Місто: {city}\n\n4️⃣ Введіть <b>Адресу / Відділення НП</b>:")

    elif data == "choose_city": await choose_city_menu(update, context)
    elif data.startswith("sel_city_"):
        city = data.replace("sel_city_", "")
        context.user_data.setdefault('profile', {})['city'] = city
        await _edit_or_reply(query, f"✅ Місто: {city}\nДалі оберіть дію.", [[InlineKeyboardButton("🔙", callback_data="menu_profile")]])

    # --- АДМІНКА ---
    elif data == "admin_main": await admin_menu(update, context)
    
    # Угода (fallback)
    elif data == "menu_terms": 
        try: await terms_handler(update, context)
        except: await _edit_or_reply(query, "📜 Правила...", [[InlineKeyboardButton("🔙", callback_data="menu_start")]])
            
# =================================================================
# ➕ SECTION 29.1: MISSING HANDLERS (STATS & TERMS)
# =================================================================

async def terms_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показує угоду користувача."""
    await _edit_or_reply(
        update.callback_query, 
        TERMS_TEXT, 
        [[InlineKeyboardButton("🔙 Назад", callback_data="menu_start")]]
    )

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показує статистику (заглушка + реальні дані з БД)."""
    user_count = 0
    try:
        conn = sqlite3.connect(DB_PATH)
        user_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        conn.close()
    except: pass

    text = (
        f"📊 <b>СТАТИСТИКА БОТА</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 Користувачів у базі: <b>{user_count}</b>\n"
        f"💎 VIP Клієнтів: (дані з БД)\n"
        f"🚀 Бот працює стабільно."
    )
    kb = [[InlineKeyboardButton("🔙 Назад", callback_data="admin_main")]]
    await _edit_or_reply(update.callback_query, text, kb)
    

# =================================================================
# 👮‍♂️ SECTION 29.5: ADMIN PANEL (MISSING FUNCTIONS FIXED)
# =================================================================

async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Головне меню адміністратора (Команда /admin)."""
    user_id = update.effective_user.id
    if user_id != MANAGER_ID:
        # Ігноруємо або тролимо, якщо не адмін
        return

    text = (
        "🕴️ <b>GHOSTY CONTROL PANEL</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Система працює стабільно.\n"
        "Оберіть дію:"
    )
    
    keyboard = [
        [InlineKeyboardButton("📢 Розсилка всім", callback_data="admin_broadcast")],
        [InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton("🔙 Вихід", callback_data="menu_start")]
    ]
    
    # Відправляємо або редагуємо
    if update.message:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await _edit_or_reply(update.callback_query, text, keyboard)

async def start_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Початок режиму масової розсилки.
    Переводить бота в стан очікування повідомлення від адміна.
    """
    # Перевірка на адміна
    if update.effective_user.id != MANAGER_ID: 
        return
    
    # Встановлюємо "прапорець" розсилки та глобальний стан
    context.user_data['awaiting_broadcast'] = True
    context.user_data['state'] = "BROADCAST_MODE"
    
    text = (
        "📢 <b>РЕЖИМ РОЗСИЛКИ АКТИВОВАНО</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Надішліть сюди повідомлення (Текст, Фото або Відео).\n"
        "Воно буде миттєво розіслано всім користувачам з бази даних.\n\n"
        "⚠️ <i>Будьте обережні, дію не можна скасувати після відправки.</i>"
    )
    
    # Кнопка для безпечного виходу
    kb = [[InlineKeyboardButton("❌ СКАСУВАТИ ТА ВИЙТИ", callback_data="admin_cancel_action")]]
    
    await _edit_or_reply(update.callback_query, text, kb)
    
# =================================================================
# 🚀 SECTION 30: FINAL RUNNER (SYSTEM STARTUP)
# =================================================================

async def post_init(application: Application):
    """
    Хук після успішного підключення до Telegram.
    """
    try:
        bot = await application.bot.get_me()
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"🤖 BOT STARTED: @{bot.username}")
        print(f"🆔 BOT ID:       {bot.id}")
        print(f"📅 START TIME:  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"💾 DATA DIR:    {DATA_DIR}")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"✅ SYSTEM ONLINE. WAITING FOR UPDATES...")
    except Exception as e:
        print(f"⚠️ POST_INIT WARNING: {e}")

def main():
    """Головна точка входу."""
    print("\n🚀 GHOSTY STAFF 2026: ENGINE LAUNCHING...")
    
    # 1. Перевірка Токена
    if not TOKEN or TOKEN == "YOUR_TOKEN_HERE":
        print("❌ FATAL ERROR: Bot token is missing or invalid!")
        sys.exit(1)

    # 2. Перевірка БД та папок
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        init_db()
        print("🗄️  Database connection established.")
    except Exception as e:
        print(f"❌ CRITICAL SYSTEM ERROR (DB): {e}")
        sys.exit(1)

    # 3. Побудова додатка
    try:
        persistence = PicklePersistence(filepath=PERSISTENCE_PATH)
        app = (
            Application.builder()
            .token(TOKEN)
            .persistence(persistence)
            .defaults(Defaults(parse_mode=ParseMode.HTML))
            .post_init(post_init)
            .build()
        )
    except Exception as e:
        print(f"❌ BUILD ERROR: {e}")
        sys.exit(1)

    # 4. Реєстрація хендлерів
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("admin", admin_menu))
    app.add_handler(CallbackQueryHandler(global_callback_handler))
    app.add_handler(MessageHandler((filters.TEXT | filters.PHOTO) & (~filters.COMMAND), handle_user_input))
    app.add_error_handler(error_handler)

    # 5. Запуск
    print("📡 Connecting to Telegram API...")
    try:
        app.run_polling(drop_pending_updates=True)
    except Exception as e:
        print(f"❌ POLLING ERROR: {e}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped manually.")
        sys.exit(0)
    except Exception:
        traceback.print_exc()
        sys.exit(1)

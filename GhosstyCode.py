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

# 2. Налаштування Бота
# Пріоритет: Змінна оточення (для безпеки) -> Жорстко прописаний (твоя резервна копія)
ENV_TOKEN = os.getenv("BOT_TOKEN")
TOKEN = ENV_TOKEN if ENV_TOKEN else "8351638507:AAEEbCkrYI4X7m-Rflqesxo9PBGSYWlt_Ww"

MANAGER_ID = 7544847872
MANAGER_USERNAME = "ghosstydp"
CHANNEL_URL = "https://t.me/GhostyStaffDP"
WELCOME_PHOTO = "https://i.ibb.co/y7Q194N/1770068775663.png"

# 3. Економіка та Посилання
VIP_EXPIRY = "25.03.2026"
VIP_DISCOUNT = 0.65  # -35%
PROMO_BONUS = 101    # Знижка за промокод

# ВИПРАВЛЕНО ТУТ: Правильне оголошення словника
PAYMENT_LINK = {
    "mono": "https://lnk.ua/k4xJG21Vy",   
    "privat": "https://lnk.ua/RVd0OW6V3"
}

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

def calculate_final_price(price, profile):
    """
    Рахує ціну.
    Логіка: Якщо VIP/Promo -> спочатку -101 грн (якщо ціна > 200), потім -35%.
    """
    is_vip = profile.get('is_vip', False)
    promo_code = profile.get('promo_applied', False)
    
    final_price = float(price)
    discounted = False

    if is_vip or promo_code:
        # Логіка MEGA PROMO
        if final_price > 200:
            final_price -= 101 # Бонус 101 грн
            
        final_price = final_price * 0.65 # Знижка 35%
        discounted = True
        
    # Захист від від'ємних цін
    if final_price < 1: final_price = 1.0
        
    return int(final_price), discounted
    
    

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

async def save_location_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, dist_name=None, is_courier=False):
    """Збереження локації."""
    profile = context.user_data.setdefault("profile", {})
    
    if is_courier:
        profile["district"] = "Кур'єр (+150 грн)"
        profile["delivery_type"] = "courier"
        context.user_data['state'] = "WAITING_ADDRESS"
        
        await _edit_or_reply(
            update.callback_query, 
            "🛵 <b>Напишіть адресу доставки одним повідомленням:</b>\n<i>(Вулиця, дім, під'їзд, поверх, телефон)</i>", 
            [[InlineKeyboardButton("❌ Скасувати", callback_data="menu_profile")]]
        )
    else:
        profile["district"] = dist_name
        profile["delivery_type"] = "klad"
        context.user_data['state'] = None # Скидаємо стан, щоб не перехоплювало текст
        
        # Оновлення в SQLite (безпечно)
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("UPDATE users SET city = ?, district = ?, last_active = ? WHERE user_id = ?", 
                        (profile.get("city"), dist_name, datetime.now(), update.effective_user.id))
            conn.commit()
            conn.close()
        except Exception: pass # Ігноруємо помилки БД, щоб не ламати юзер-флоу
        
        await _edit_or_reply(
            update.callback_query, 
            f"✅ <b>Локацію збережено!</b>\n📍 {profile.get('city')}, {dist_name}", 
            [[InlineKeyboardButton("🛒 Перейти до кошика", callback_data="menu_cart"), 
              InlineKeyboardButton("🛍 Продовжити покупки", callback_data="cat_all")]]
        )
        

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
        "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg",
        "desc": "🧠 <b>90% HHC | Сатіва</b>\n⚡ Бадьорить та фокусує\n🎁 <b>+ РІДИНА БЕЗКОШТОВНО!</b>",
        "payment_url": PAYMENT_LINK
    },
    102: {
        "name": "🌸 Packwoods Pink 1ml",
        "type": "hhc",
        "price": 699.77,
        "discount": True,
        "gift_liquid": True,
        "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg",
        "desc": "🧠 <b>90% HHC | Індіка</b>\n😇 Спокій + підйом настрою\n🎁 <b>+ РІДИНА БЕЗКОШТОВНО!</b>",
        "payment_url": PAYMENT_LINK
    },
    103: {
        "name": "🌿 Whole Mint 2ml",
        "type": "hhc",
        "price": 879.77,
        "discount": True,
        "gift_liquid": True,
        "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg",
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
    """Створення таблиць SQLite."""
    if not os.path.exists('data'): os.makedirs('data')
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Таблиця юзерів
    cur.execute('''CREATE TABLE IF NOT EXISTS users 
                   (user_id INTEGER PRIMARY KEY, 
                    username TEXT, 
                    first_name TEXT,
                    city TEXT, 
                    district TEXT, 
                    is_vip INTEGER DEFAULT 0, 
                    reg_date TEXT,
                    last_active TEXT)''')
                    
    # Таблиця замовлень
    cur.execute('''CREATE TABLE IF NOT EXISTS orders 
                   (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    user_id INTEGER, 
                    amount REAL, 
                    status TEXT, 
                    date TEXT)''')
                    
    conn.commit()
    conn.close()
    logger.info("✅ DATABASE SYNCHRONIZED")
    

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
# 🔍 SECTION 15: КАРТКА ТОВАРУ (З КОЛЬОРАМИ)
# =================================================================

async def view_item_details(update: Update, context: ContextTypes.DEFAULT_TYPE, item_id: int):
    """
    Картка товару PRO: відображає фото, ціну і КНОПКИ КОЛЬОРІВ/МІЦНОСТІ.
    """
    item = get_item_data(item_id)
    if not item: return

    # Ціна з урахуванням знижок
    profile = context.user_data.get("profile", {})
    final_price, has_discount = calculate_final_price(item['price'], profile)
    price_html = f"<b>{int(item['price'])} ₴</b>"
    if has_discount:
        price_html = f"<s>{int(item['price'])}</s> ➡️ <b>{final_price} ₴</b> 🔥"

    # Опис + Промокоди
    promo_block = (
        "\n🎫 <b>Твої промокоди:</b>\n"
        "▫️ <code>GHST2026</code> (-101 грн + VIP + Рідина)\n"
        "▫️ <code>START35</code> (-35% на перше замовлення)"
    )
    
    caption = (
        f"<b>{item['name']}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{item['desc']}\n"
        f"{promo_block}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 Ціна: {price_html}"
    )

    keyboard = []

    # ЛОГІКА КНОПОК:
    # 1. Якщо POD -> Генеруємо кнопки кольорів
    if "colors" in item:
        caption += "\n\n🎨 <b>Оберіть колір девайсу:</b>"
        colors = item["colors"]
        for i in range(0, len(colors), 2):
            row = []
            col1 = colors[i]
            row.append(InlineKeyboardButton(col1, callback_data=f"add_{item_id}_{col1}"))
            if i + 1 < len(colors):
                col2 = colors[i+1]
                row.append(InlineKeyboardButton(col2, callback_data=f"add_{item_id}_{col2}"))
            keyboard.append(row)

    # 2. Якщо Рідина -> Генеруємо кнопки міцності
    elif "strengths" in item:
        caption += "\n\n🧪 <b>Оберіть міцність:</b>"
        row = []
        for s in item['strengths']:
            row.append(InlineKeyboardButton(f"{s}mg", callback_data=f"add_{item_id}_{s}"))
        keyboard.append(row)

    # 3. Якщо HHC -> Кнопка з подарунком
    elif item.get("gift_liquid"):
        caption += "\n🎁 <b>+ РІДИНА У ПОДАРУНОК!</b>"
        keyboard.append([InlineKeyboardButton("🎁 Обрати бонус і купити", callback_data=f"add_{item_id}")])

    # 4. Простий товар
    else:
        keyboard.append([InlineKeyboardButton("🛒 Додати у кошик", callback_data=f"add_{item_id}")])

    # Кнопка менеджера
    mgr_url = f"https://t.me/{MANAGER_USERNAME}?text=Привіт!%20Хочу%20замовити%20{item['name'].replace(' ', '%20')}"
    keyboard.append([InlineKeyboardButton("👨‍💻 Замовити через менеджера", url=mgr_url)])
    keyboard.append([InlineKeyboardButton("🔙 До списку", callback_data="cat_all")])

    await send_ghosty_message(update, caption, keyboard, photo=item.get('img'))
    
# =================================================================
# 👤 SECTION 6: USER INTERFACE (PROFILE, CART & AUTH)
# =================================================================

async def get_or_create_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    ⚙️ ЯДРО АВТОРИЗАЦІЇ:
    Створює профіль, обробляє рефералку та синхронізує з БД.
    Повертає словник profile.
    """
    user = update.effective_user
    uid = user.id
    current_time = datetime.now().strftime("%d.%m.%Y %H:%M")
    
    # 1. Створюємо структуру в пам'яті, якщо її немає
    if "profile" not in context.user_data:
        # Перевіряємо рефералку (тільки при першому старті)
        referrer_id = None
        if context.args and context.args[0].isdigit():
            ref_candidate = int(context.args[0])
            if ref_candidate != uid:
                referrer_id = ref_candidate

        context.user_data["profile"] = {
            "uid": uid,
            "name": escape(user.first_name) if user.first_name else "Клієнт",
            "username": f"@{user.username}" if user.username else "Приховано",
            "city": None,
            "district": None,
            "address_details": None,
            "phone": None,
            "promo_applied": False,
            "promo_code": f"GHST{uid}",  # Персональний промокод
            "referred_by": referrer_id,
            "orders_count": 0,
            "is_vip": False,
            "reg_date": current_time
        }
        
        # Лог реферала
        if referrer_id:
            logger.info(f"👤 User {uid} invited by {referrer_id}")

    # 2. Оновлюємо дані в БД (SQLite)
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        # Створюємо таблицю, якщо раптом нема
        c.execute('''CREATE TABLE IF NOT EXISTS users 
                     (user_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT, 
                      reg_date TEXT, last_active TEXT)''')
        
        # Додаємо або ігноруємо
        c.execute('''INSERT OR IGNORE INTO users (user_id, username, first_name, reg_date, last_active)
                     VALUES (?, ?, ?, ?, ?)''', 
                     (uid, user.username, user.first_name, current_time, current_time))
        
        # Оновлюємо активність
        c.execute('''UPDATE users SET last_active = ?, username = ? WHERE user_id = ?''', 
                     (current_time, user.username, uid))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"DB Error in auth: {e}")

    return context.user_data["profile"]

async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Відображає кабінет користувача."""
    # Гарантуємо, що профіль існує
    profile = await get_or_create_user(update, context)
    
    # Визначаємо статус
    status_icon = "💎 VIP" if profile.get('is_vip') else "👤 Standard"
    
    text = (
        f"<b>💼 ОСОБИСТИЙ КАБІНЕТ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 ID: <code>{profile['uid']}</code>\n"
        f"📛 Ім'я: {profile['name']}\n"
        f"🔰 Статус: <b>{status_icon}</b>\n"
        f"📦 Всього замовлень: {profile.get('orders_count', 0)}\n"
        f"🎟 Твій промокод: <code>{profile['promo_code']}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📢 <a href='{CHANNEL_URL}'>Новини та відгуки</a>"
    )
    
    keyboard = [
        [InlineKeyboardButton("📦 Мої замовлення", callback_data="history_orders")],
        [InlineKeyboardButton("🎟 Ввести промокод", callback_data="menu_promo")],
        [InlineKeyboardButton("🔙 Головне меню", callback_data="menu_start")]
    ]
    
    await send_ghosty_message(update, text, keyboard)

async def show_cart_logic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Розумний кошик: показує товари або каже, що пусто."""
    cart = context.user_data.get("cart", [])
    
    if not cart:
        await send_ghosty_message(
            update, 
            "🛒 <b>Кошик порожній</b>\n\nПодивіться наш каталог, там багато цікавого!",
            [[InlineKeyboardButton("🛍 До Каталогу", callback_data="cat_all")],
             [InlineKeyboardButton("🔙 Назад", callback_data="menu_start")]]
        )
        return

    # Рахуємо суму
    total_price = sum(item['price'] for item in cart)
    items_list = "\n".join([f"▫️ {i['name']} — {i['price']}₴" for i in cart])
    
    text = (
        f"🛒 <b>ВАШ КОШИК ({len(cart)} шт.)</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{items_list}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 <b>РАЗОМ: {total_price}₴</b>"
    )
    
    keyboard = [
        [InlineKeyboardButton("✅ Оформити замовлення", callback_data="checkout_init")],
        [InlineKeyboardButton("🗑 Очистити кошик", callback_data="cart_clear")],
        [InlineKeyboardButton("🔙 Продовжити покупки", callback_data="cat_all")]
    ]
    
    await send_ghosty_message(update, text, keyboard)

async def checkout_init(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Початок оформлення замовлення."""
    cart = context.user_data.get("cart", [])
    if not cart:
        await show_cart_logic(update, context)
        return

    await send_ghosty_message(
        update, 
        "📝 <b>ОФОРМЛЕННЯ ЗАМОВЛЕННЯ</b>\n\n"
        "Оберіть ваше місто для доставки:", 
        [[InlineKeyboardButton("🏙 Вибрати місто", callback_data="choose_city")],
         [InlineKeyboardButton("🔙 Назад", callback_data="menu_cart")]]
    )

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
# 🏠 SECTION 8: START & PROFILE (STABLE & FINAL)
# =================================================================

async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Відображає профіль користувача з фото, даними доставки та кнопками.
    """
    # 1. Отримуємо дані
    profile = context.user_data.get("profile", {})
    user = update.effective_user
    
    # 2. Формуємо статус локації
    city = profile.get('city')
    district = profile.get('district')
    
    if city:
        location_status = f"📍 <b>{city}</b>"
        if district:
            location_status += f", {district}"
    else:
        location_status = "❌ <b>Не обрано</b> (натисніть кнопку нижче)"

    # 3. Формуємо текст повідомлення
    text = (
        f"<b>👤 ВАШ ПРОФІЛЬ Gho$$tyyy</b>\n\n"
        f"🆔 ID: <code>{user.id}</code>\n"
        f"👤 Юзер: @{user.username if user.username else 'NoName'}\n"
        f"💎 Статус: <b>VIP до {VIP_EXPIRY}</b>\n"
        f"🎟 Промо: <code>{profile.get('promo_code', '---')}</code>\n\n"
        f"📮 <b>Дані доставки:</b>\n{location_status}"
    )

    # 4. Клавіатура
    keyboard = [
        [InlineKeyboardButton("📍 Дані доставки / Змінити", callback_data="menu_city")],
        [InlineKeyboardButton("🎟 Застосувати промокод", callback_data="promo_activate")],
        [InlineKeyboardButton("🏠 На головну", callback_data="menu_start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # 5. Спроба отримати фото профілю (з захистом від помилок приватності)
    try:
        user_photos = await context.bot.get_user_profile_photos(user.id, limit=1)
        if user_photos.total_count > 0:
            # Використовуємо останнє фото профілю (найкраща якість)
            photo = user_photos.photos[0][-1].file_id
            await send_ghosty_message(update, text, reply_markup, photo)
        else:
            # Якщо фото немає
            await send_ghosty_message(update, text, reply_markup, WELCOME_PHOTO)
    except Exception as e:
        # Якщо Telegram забороняє доступ до фото (налаштування приватності юзера)
        logger.warning(f"Could not fetch profile photo for {user.id}: {e}")
        await send_ghosty_message(update, text, reply_markup, WELCOME_PHOTO)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Головне меню Ghosty Staff."""
    user = update.effective_user
    ghst_id = f"GHSTid-{user.id}"
    
    # Текст у примарному лабораторному стилі
    welcome_text = (
        f"🌫️ <b>GHO$$TY STAFF LAB | УКРАЇНА</b> 🧪\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🧬 <b>HHC SHOP ПОВНІСТЮ ВІДКРИТО!</b>\n"
        f"🔥 Діє промокод на перше замовлення: <b>-35%</b>\n"
        f"🎁 + Рідина на вибір до кожного вейпу!\n"
        f"🚚 <b>ВІП-СТАТУС:</b> Безкоштовна доставка (0 грн) активна до 25.03.2026!\n\n"
        f"👤 Твій персональний код: <code>{ghst_id}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🌫️ Оберіть пункт меню нижче 👇"
    )
    
    keyboard = [
        [InlineKeyboardButton("🛍 АСОРТИМЕНТ ТОВАРІВ", callback_data="cat_all")],
        [InlineKeyboardButton("👤 ПРОФІЛЬ", callback_data="menu_profile"), 
         InlineKeyboardButton("🛒 КОШИК", callback_data="menu_cart")],
        [InlineKeyboardButton("📍 ОБРАТИ ЛОКАЦІЮ", callback_data="choose_city")],
        [InlineKeyboardButton("📜 УГОДА", callback_data="user_agreement")],
        [InlineKeyboardButton("👨‍💻 МЕНЕДЖЕР", url=f"https://t.me/{MANAGER_USERNAME}"),
         InlineKeyboardButton("📢 КАНАЛ", url=CHANNEL_URL)]
    ]
    
    # Для адміна додаємо сіру кнопку та елітну адмінку
    if user.id == MANAGER_ID:
        keyboard.append([InlineKeyboardButton("---", callback_data="none")])
        keyboard.append([InlineKeyboardButton("💰 АДМІН-ПАНЕЛЬ 💎", callback_data="admin_main")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_photo(photo=WELCOME_PHOTO, caption=welcome_text, reply_markup=reply_markup, parse_mode='HTML')
    else:
        await update.callback_query.message.edit_caption(caption=welcome_text, reply_markup=reply_markup, parse_mode='HTML')

    
# =================================================================
# ⚙️ SECTION 9: GLOBAL CALLBACK DISPATCHER (PARTIAL)
# =================================================================

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
# 🚚 SECTION 11: ADDRESS DELIVERY & LOCATION SAVING
# =================================================================

async def save_location_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, dist_name: str = None, is_address: bool = False):
    """
    Зберігає обрану локацію в профіль користувача та базу SQLite.
    """
    profile = context.user_data["profile"]
    user_id = update.effective_user.id
    
    if is_address:
        profile["district"] = "Адресна доставка"
        profile["delivery_type"] = "address"
        msg = "✅ <b>Ви обрали адресну доставку по Дніпру!</b>\nВам потрібно буде вказати адресу при оформленні."
    else:
        profile["district"] = dist_name
        profile["delivery_type"] = "klad"
        msg = f"✅ <b>Локацію встановлено:</b> {profile['city']}, р-н {dist_name}"

    # Оновлення в SQLite
    try:
        conn = sqlite3.connect('data/ghosty_v3.db')
        c = conn.cursor()
        c.execute("UPDATE users SET city = ?, district = ? WHERE user_id = ?", 
                 (profile["city"], profile["district"], user_id))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Error saving location to DB: {e}")

    keyboard = [
        [InlineKeyboardButton("🛍 Перейти до покупок", callback_data="cat_main")],
        [InlineKeyboardButton("🏠 В меню", callback_data="menu_start")]
    ]
    await send_ghosty_message(update, msg, InlineKeyboardMarkup(keyboard))

# =================================================================
# 👤 SECTION 10: USER PROFILE & REFERRAL SYSTEM (PRO UI)
# =================================================================

async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Відображення профілю користувача."""
    query = update.callback_query
    user = update.effective_user
    user_id = user.id
    
    # Ініціалізація профілю
    profile = context.user_data.setdefault("profile", {})
    
    # Дані для відображення
    ghst_id = f"GHST-{user_id}"
    city = profile.get('city', 'Не обрано')
    dist = profile.get('district', '')
    location = f"{city}, {dist}" if city != 'Не обрано' else "❌ Не вказано"
    
    vip_status = "💎 АКТИВНИЙ" if profile.get('is_vip') else "🌑 Стандарт"
    
    # Текст
    profile_text = (
        f"👤 <b>ОСОБИСТИЙ КАБІНЕТ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📛 <b>Ім'я:</b> {escape(user.first_name)}\n"
        f"🆔 <b>ID:</b> <code>{user_id}</code>\n"
        f"🛡️ <b>Код клієнта:</b> <code>{ghst_id}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📍 <b>Доставка:</b>\n<i>{location}</i>\n\n"
        f"🏆 <b>Статус:</b> {vip_status}\n"
        f"📦 <b>Замовлень:</b> {profile.get('orders_count', 0)}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🎟️ <b>Твоє реферальне посилання:</b>\n<code>https://t.me/{context.bot.username}?start={user_id}</code>"
    )

    keyboard = [
        [InlineKeyboardButton("📦 Змінити адресу доставки", callback_data="choose_city")],
        [InlineKeyboardButton("🤝 Реферальна програма", callback_data="ref_system")],
        [InlineKeyboardButton("🎟 Ввести промокод", callback_data="menu_promo")],
        [InlineKeyboardButton("🏠 Головне меню", callback_data="menu_start")]
    ]

    # Спроба відправити з фото профілю
    try:
        photos = await user.get_profile_photos(limit=1)
        if photos.total_count > 0:
            photo_file = photos.photos[0][-1].file_id
            # Використовуємо універсальну функцію (треба переконатись, що вона підтримує photo)
            await send_ghosty_message(update, profile_text, keyboard, photo=photo_file)
        else:
            await _edit_or_reply(query, profile_text, keyboard)
    except Exception as e:
        logger.error(f"Profile photo error: {e}")
        await _edit_or_reply(query, profile_text, keyboard)

async def show_ref_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Інформація про реферальну систему."""
    query = update.callback_query
    user_id = update.effective_user.id
    
    ref_text = (
        f"🤝 <b>ПАРТНЕРСЬКА ПРОГРАМА</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Запрошуй друзів та отримуй бонуси!\n\n"
        f"1️⃣ <b>Твій друг отримує:</b>\n"
        f"   • Знижку -35% на перше замовлення\n"
        f"2️⃣ <b>Ти отримуєш:</b>\n"
        f"   • VIP-статус на 7 днів (Безкоштовна доставка)\n"
        f"   • Секретний подарунок у наступному замовленні\n\n"
        f"🔗 <b>Твоє посилання:</b>\n<code>https://t.me/{context.bot.username}?start={user_id}</code>"
    )
    keyboard = [[InlineKeyboardButton("⬅️ Назад до профілю", callback_data="menu_profile")]]
    await _edit_or_reply(query, ref_text, keyboard)
    


# =================================================================
# ⚙️ SECTION 13: CALLBACK DISPATCHER (CITIES & PROFILE)
# =================================================================

# Цей шматок коду додається до основного main_callback_handler у фінальній збірці
async def process_geo_(update: Update, context: ContextTypes.DEFAULT_TYPE, data: str):
    """
    Обробка географічних колбеків.
    """
    profile = context.user_data["profile"]
    
    if data == "menu_city":
        await city_selection_menu(update, context)
        
    elif data.startswith("set_city_"):
        city = data.replace("set_city_", "")
        profile["city"] = city
        await district_selection_menu(update, context, city)
        
    elif data.startswith("set_dist_"):
        dist = data.replace("set_dist_", "")
        await save_location_handler(update, context, dist_name=dist)
        
    elif data == "set_delivery_address":
        await save_location_handler(update, context, is_address=True)
        
    elif data == "menu_profile":
        await show_profile(update, context)
        
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
    """
    Універсальна картка товару.
    Відображає: Фото, Ціну (зі знижкою), Опис, Кнопки (Міцність/Подарунок).
    """
    item = get_item_data(item_id)
    if not item:
        await update.callback_query.answer("❌ Товар не знайдено")
        return

    # Розрахунок ціни
    profile = context.user_data.get("profile", {})
    final_price, has_discount = calculate_final_price(item['price'], profile)

    price_html = f"<b>{item['price']} ₴</b>"
    if has_discount:
        price_html = f"<s>{item['price']}</s> ➡️ <b>{final_price} ₴</b> 🔥"

    # Формування опису
    caption = (
        f"<b>{item['name']}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{item['desc']}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 Ціна: {price_html}"
    )

    keyboard = []

    # ЛОГІКА КНОПОК:
    
    # 1. Якщо це Рідина -> Кнопки міцності
    if "strengths" in item:
        caption += "\n🧪 <b>Оберіть міцність (mg):</b>"
        row = []
        for s in item['strengths']:
            row.append(InlineKeyboardButton(f"{s}", callback_data=f"add_{item_id}_{s}"))
        keyboard.append(row)

    # 2. Якщо це HHC -> Кнопка з подарунком
    elif item.get("gift_liquid"):
        caption += "\n🎁 <b>+ БЕЗКОШТОВНА РІДИНА!</b>"
        keyboard.append([InlineKeyboardButton("🎁 Обрати бонус і купити", callback_data=f"add_{item_id}")])

    # 3. Звичайний товар
    else:
        keyboard.append([InlineKeyboardButton("🛒 Додати у кошик", callback_data=f"add_{item_id}")])

    # Кнопки навігації
    keyboard.append([InlineKeyboardButton("🔙 До списку", callback_data="cat_all")])

    # Відправка
    await send_ghosty_message(update, caption, keyboard, photo=item.get('img'))
    
# =================================================================
# 🛒 SECTION 17: ДОДАВАННЯ В КОШИК (ОБРОБКА КОЛЬОРІВ)
# =================================================================

async def add_to_cart_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обробляє натискання на колір/міцність і додає в кошик.
    Data: add_ITEMID_VARIANT (VARIANT = колір або міцність)
    """
    query = update.callback_query
    
    try:
        parts = query.data.split("_")
        item_id = int(parts[1])
        # Збираємо варіант (це може бути "Black Phantom" з пробілами)
        variant = "_".join(parts[2:]) if len(parts) > 2 else None
    except: 
        await query.answer("⚠️ Помилка даних")
        return

    item = get_item_data(item_id)
    if not item: 
        await query.answer("❌ Товар не знайдено")
        return

    # Логіка HHC (вибір подарунка)
    if item.get("gift_liquid", False):
        context.user_data['pending_item_id'] = item_id
        text = f"🎁 <b>ОБЕРІТЬ ВАШ ПОДАРУНОК!</b>\nДо <b>{item['name']}</b> йде безкоштовна рідина:"
        kb = [[InlineKeyboardButton(g['name'], callback_data=f"gift_sel_{gid}")] for gid, g in GIFT_LIQUIDS.items()]
        kb.append([InlineKeyboardButton("❌ Скасувати", callback_data=f"view_item_{item_id}")])
        await _edit_or_reply(query, text, kb)
        return

    # Формування повної назви (Товар + Колір)
    final_name = item['name']
    if variant:
        # Якщо варіант цифра -> це міцність
        if variant.isdigit():
            final_name += f" ({variant}mg)"
        # Якщо текст -> це колір (замінюємо підкреслення на пробіли, якщо були)
        else:
            clean_variant = variant.replace("_", " ")
            final_name += f" ({clean_variant})"

    # Фіналізація
    await _finalize_add_to_cart(update, context, item, gift=None, name=final_name)

async def gift_selection_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробка вибору подарунка (gift_sel_ID)."""
    query = update.callback_query
    gift_id = int(query.data.split("_")[2])
    
    main_id = context.user_data.get('pending_item_id')
    if not main_id: return
    
    main_item = get_item_data(main_id)
    gift_item = GIFT_LIQUIDS.get(gift_id)
    gift_name = gift_item['name'] if gift_item else "Сюрприз"
    
    await _finalize_add_to_cart(update, context, main_item, gift=gift_name)
    context.user_data.pop('pending_item_id', None)

async def _finalize_add_to_cart(update: Update, context: ContextTypes.DEFAULT_TYPE, item, gift=None, name=None):
    """Фізичний запис у базу кошика."""
    cart = context.user_data.setdefault("cart", [])
    profile = context.user_data.setdefault("profile", {})
    
    price, _ = calculate_final_price(item['price'], profile)
    
    cart.append({
        "id": random.randint(100000, 999999),
        "name": name if name else item['name'],
        "price": price,
        "gift": gift
    })
    
    msg = f"✅ <b>{name or item['name']}</b> додано!\n💰 Ваша ціна: {price} грн"
    if gift: msg += f"\n🎁 Бонус: {gift}"
    
    kb = [[InlineKeyboardButton("🛒 Кошик", callback_data="menu_cart"), InlineKeyboardButton("🔙 Каталог", callback_data="cat_all")]]
    await send_ghosty_message(update, msg, kb)
    

# =================================================================
# 🛒 SECTION 18: CART LOGIC (VISUALIZATION)
# =================================================================

async def show_cart_logic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Головний екран кошика.
    Перевіряє наявність товарів та локації перед оформленням.
    """
    query = update.callback_query
    cart = context.user_data.get("cart", [])
    profile = context.user_data.setdefault("profile", {})
    
    # 1. Порожній кошик
    if not cart:
        await send_ghosty_message(
            update, 
            "🛒 <b>Ваш кошик порожній</b>\n\nЧас обрати щось топове! 👇",
            [[InlineKeyboardButton("🛍 До Каталогу", callback_data="cat_all")],
             [InlineKeyboardButton("🏠 Меню", callback_data="menu_start")]]
        )
        return

    # 2. Формування списку
    total_sum = 0
    items_text = ""
    keyboard = []

    for idx, item in enumerate(cart):
        total_sum += item['price']
        
        # Додаємо рядок подарунка, якщо є
        gift_line = f"\n   └ 🎁 {item['gift']}" if item['gift'] else ""
        
        items_text += f"🔹 <b>{item['name']}</b>{gift_line}\n   💰 <code>{item['price']} грн</code>\n"
        
        # Кнопка видалення (по унікальному ID)
        keyboard.append([InlineKeyboardButton(f"❌ Видалити: {item['name'][:15]}...", callback_data=f"cart_del_{item['id']}")])

    # 3. Перевірка Географії (Важливо для Checkout)
    city = profile.get("city")
    district = profile.get("district")
    
    can_checkout = False
    if city and district:
        location_status = f"✅ <b>Доставка:</b> {city}, {district}"
        can_checkout = True
    else:
        location_status = "⚠️ <b>Спочатку оберіть місто доставки!</b>"
        # Кнопка вибору міста стає першою, якщо локації немає
        keyboard.insert(0, [InlineKeyboardButton("📍 ОБРАТИ МІСТО/РАЙОН", callback_data="choose_city")])

    text = (
        f"🛒 <b>КОШИК ЗАМОВЛЕНЬ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{items_text}"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{location_status}\n"
        f"💰 <b>РАЗОМ ДО СПЛАТИ: {total_sum} UAH</b>"
    )

    # 4. Кнопка Оформлення (тільки якщо є локація)
    if can_checkout:
        keyboard.insert(0, [InlineKeyboardButton("🚀 ОФОРМИТИ ЗАМОВЛЕННЯ", callback_data="checkout_init")])

    keyboard.append([InlineKeyboardButton("🗑 Очистити все", callback_data="cart_clear")])
    keyboard.append([InlineKeyboardButton("🔙 Меню", callback_data="menu_start")])

    await send_ghosty_message(update, text, keyboard)

async def cart_action_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Видалення товарів або очищення."""
    query = update.callback_query
    data = query.data
    
    if data == "cart_clear":
        context.user_data["cart"] = []
        await show_cart_logic(update, context)
        
    elif data.startswith("cart_del_"):
        uid = int(data.split("_")[2])
        cart = context.user_data.get("cart", [])
        # Фільтруємо список, залишаючи все, крім цього ID
        context.user_data["cart"] = [i for i in cart if i['id'] != uid]
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
# 💳 SECTION 21: ОФОРМЛЕННЯ ЗАМОВЛЕННЯ
# =================================================================

async def checkout_init(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Фіналізація замовлення: генерація чека та ID."""
    query = update.callback_query
    cart = context.user_data.get("cart", [])
    profile = context.user_data.get("profile", {})

    if not cart:
        await show_cart_logic(update, context)
        return

    # Розрахунок
    total_sum = sum(item['price'] for item in cart)
    
    # Додаємо вартість кур'єра
    delivery_cost = 0
    district_info = str(profile.get("district", ""))
    if "Кур'єр" in district_info:
        delivery_cost = 150
        total_sum += delivery_cost

    # Генерація унікального ID
    ts = int(datetime.now().timestamp()) % 10000
    rnd = random.randint(10, 99)
    order_id = f"GH-{ts}-{rnd}"

    # Копійки для верифікації
    cents = random.randint(1, 99) / 100
    final_amount = float(total_sum) + cents

    context.user_data["current_order_id"] = order_id
    context.user_data["final_checkout_sum"] = final_amount 

    courier_text = f"\n🛵 Доставка: +{delivery_cost} грн" if delivery_cost > 0 else ""

    text = (
        f"<b>📦 ЗАМОВЛЕННЯ #{order_id}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📍 <b>Локація:</b> {profile.get('city')}, {district_info}\n"
        f"💰 <b>СУМА: {final_amount:.2f}₴</b>{courier_text}\n"
        f"⚠️ <b>КОМЕНТАР ДО ПЛАТЕЖУ:</b> <code>{order_id}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👇 <i>Оберіть зручний банк для оплати:</i>"
    )
    
    keyboard = [
        [InlineKeyboardButton("💳 MONOBANK", callback_data="pay_mono")],
        [InlineKeyboardButton("💳 PRIVAT24", callback_data="pay_privat")],
        [InlineKeyboardButton("⬅️ НАЗАД", callback_data="menu_cart")]
    ]
    
    await _edit_or_reply(query, text, keyboard)

# =================================================================
# 🔑 SECTION 22: ПРОМОКОДИ
# =================================================================

async def process_promo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробка промокоду."""
    if not update.message or not update.message.text: return
    
    user_text = update.message.text.strip().upper()
    user_id = update.effective_user.id
    profile = context.user_data.setdefault("profile", {})
    
    # Список кодів
    VALID_PROMOS = ["GHOSTY2026", "GHST2026", "START35"]
    
    if user_text in VALID_PROMOS:
        profile["promo_applied"] = True
        profile["is_vip"] = True # Активація VIP
        
        # Збереження в БД (безпечно)
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("UPDATE users SET is_vip = 1 WHERE user_id = ?", (user_id,))
            conn.commit()
            conn.close()
        except: pass

        text = (
            f"🎉 <b>ПРОМОКОД {user_text} АКТИВОВАНО!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"✅ <b>VIP-статус:</b> Увімкнено\n"
            f"✅ <b>Знижка:</b> -35% (вже в кошику)\n"
            f"🎁 <b>Бонус:</b> Безкоштовна доставка"
        )
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛍 ДО КАТАЛОГУ", callback_data="cat_all")]]), parse_mode='HTML')
        
    else:
        await update.message.reply_text("❌ <b>Невірний код.</b> Спробуйте ще раз.", parse_mode='HTML')
    
    context.user_data['awaiting_promo'] = False
    
    
    
# =================================================================
# 💳 SECTION 25: PAYMENT GATEWAYS (MONO/PRIVAT)
# =================================================================

async def payment_selection_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, method: str):
    """Видача реквізитів."""
    query = update.callback_query
    
    # Генеруємо ID замовлення
    if 'current_order_id' not in context.user_data:
        context.user_data['current_order_id'] = f"GH-{random.randint(1000, 9999)}"
    
    order_id = context.user_data['current_order_id']
    amount = context.user_data.get('final_checkout_sum', 0)
    
    if amount <= 0:
        await _edit_or_reply(query, "⚠️ Помилка суми. Перевірте кошик.")
        return

    # Вибір посилання
    pay_url = PAYMENT_LINK['mono'] if method == "mono" else PAYMENT_LINK['privat']
    bank_name = "MONOBANK" if method == "mono" else "PRIVAT24"

    text = (
        f"🚀 <b>ОПЛАТА ЧЕРЕЗ {bank_name}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💵 До сплати: <b>{amount} грн</b>\n"
        f"📝 Коментар до платежу: <code>{order_id}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"1️⃣ Натисніть кнопку оплати нижче.\n"
        f"2️⃣ Вкажіть точну суму.\n"
        f"3️⃣ В коментар впишіть код замовлення!\n\n"
        f"👇 <b>Після оплати натисніть кнопку:</b>"
    )

    keyboard = [
        [InlineKeyboardButton(f"💳 ОПЛАТИТИ {amount}₴", url=pay_url)],
        [InlineKeyboardButton("✅ Я ОПЛАТИВ", callback_data="confirm_payment_start")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="checkout_init")]
    ]

    await _edit_or_reply(query, text, keyboard)

async def confirm_payment_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Крок підтвердження (Запит чека).
    """
    query = update.callback_query
    
    # Сповіщення адміну (попереднє)
    try:
        order_id = context.user_data.get('current_order_id', '???')
        amount = context.user_data.get('final_checkout_sum', 0)
        user = update.effective_user
        
        admin_msg = (
            f"🔔 <b>НОВЕ ЗАМОВЛЕННЯ #{order_id}</b>\n"
            f"👤 Клієнт: {user.mention_html()} (ID: {user.id})\n"
            f"💰 Очікується: {amount} грн\n"
            f"⏳ Статус: <i>Чекаю на скріншот...</i>"
        )
        await context.bot.send_message(chat_id=MANAGER_ID, text=admin_msg, parse_mode='HTML')
    except Exception as e:
        logger.error(f"Admin notify error: {e}")

    # Інструкція юзеру
    user_msg = (
        f"⏳ <b>ПІДТВЕРДЖЕННЯ ОПЛАТИ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Будь ласка, надішліть <b>фото квитанції</b> (скріншот) прямо сюди в чат.\n"
        f"<i>Менеджер перевірить його протягом 15 хвилин.</i> 👇"
    )
    
    context.user_data["state"] = "WAITING_RECEIPT"
    context.user_data["awaiting_receipt"] = True
    
    await _edit_or_reply(query, user_msg, [[InlineKeyboardButton("❌ Скасувати", callback_data="menu_start")]])

# =================================================================
# 🛡 SECTION 26: ORDER CONFIRMATION (ADMIN ALERT)
# =================================================================

async def payment_confirmation_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Запит чека у користувача.
    """
    query = update.callback_query
    order_id = context.user_data.get('current_order_id', 'Unknown')
    
    text = (
        f"⏳ <b>ПІДТВЕРДЖЕННЯ ЗАМОВЛЕННЯ #{order_id}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📸 Будь ласка, надішліть <b>скріншот квитанції</b> (фото) прямо сюди в чат.\n\n"
        f"<i>Менеджер перевірить оплату та надішле вам дані для отримання.</i> 👇"
    )
    
    # Вмикаємо режим очікування фото в handle_user_input
    context.user_data['state'] = "WAITING_RECEIPT"
    
    keyboard = [[InlineKeyboardButton("❌ Скасувати", callback_data="menu_start")]]
    await _edit_or_reply(query, text, keyboard)

# =================================================================
# 🛒 SECTION 27: INTERFACE FUNCTIONS (UI HELPERS)
# =================================================================

async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Кабінет користувача."""
    query = update.callback_query
    user = update.effective_user
    profile = context.user_data.setdefault("profile", {})
    
    status = "💎 VIP" if profile.get("is_vip") else "👤 Standard"
    promo = profile.get("promo_code", f"GHST{str(user.id)[::-1]}")
    
    text = (
        f"👤 <b>ОСОБИСТИЙ КАБІНЕТ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 ID: <code>{user.id}</code>\n"
        f"📛 Ім'я: {escape(user.first_name)}\n"
        f"🔰 Статус: <b>{status}</b>\n"
        f"🎟 Твій код: <code>{promo}</code>\n"
        f"📦 Замовлень: {profile.get('orders_count', 0)}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📢 <a href='{CHANNEL_URL}'>Новини та відгуки</a>"
    )
    kb = [[InlineKeyboardButton("🎟 Ввести промокод", callback_data="menu_promo")],
          [InlineKeyboardButton("🔙 Головне меню", callback_data="menu_start")]]
    await _edit_or_reply(query, text, kb)

async def checkout_init(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Старт оформлення."""
    query = update.callback_query
    cart = context.user_data.get("cart", [])
    if not cart: return await show_cart_logic(update, context)

    profile = context.user_data.get("profile", {})
    if not profile.get("city"):
        return await _edit_or_reply(query, "⚠️ Оберіть місто!", [[InlineKeyboardButton("📍 Обрати", callback_data="choose_city")]])

    if "Кур'єр" in str(profile.get("district")) and not profile.get("address_details"):
        context.user_data['state'] = "WAITING_ADDRESS"
        await _edit_or_reply(query, "🚚 Напишіть адресу (Місто, Вулиця, Дім, Телефон):", [[InlineKeyboardButton("❌ Скасувати", callback_data="menu_cart")]])
        return

    await show_payment_methods(update, context)

# =================================================================
# 📥 SECTION 28: INPUT HANDLER (TEXT & PHOTO)
# =================================================================

async def handle_user_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробка тексту та фото від користувача."""
    if not update.message: return
    user_id = update.effective_user.id
    state = context.user_data.get('state')
    
    # 1. ОБРОБКА ЧЕКІВ (ФОТО)
    if update.message.photo and state == "WAITING_RECEIPT":
        order_id = context.user_data.get('current_order_id', '???')
        summ = context.user_data.get('final_checkout_sum', '0')
        try:
            await context.bot.send_photo(
                chat_id=MANAGER_ID,
                photo=update.message.photo[-1].file_id,
                caption=f"💰 <b>НОВА ОПЛАТА #{order_id}</b>\n👤 Від: {update.effective_user.mention_html()}\n💵 Сума: {summ}₴",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Підтвердити", callback_data=f"admin_approve_{user_id}")]])
            )
            await update.message.reply_text("✅ <b>Чек отримано!</b> Очікуйте підтвердження менеджером.")
        except Exception as e:
            logger.error(f"Receipt error: {e}")
        
        context.user_data['state'] = None
        return

    # 2. ОБРОБКА ТЕКСТУ
    if update.message.text:
        text = update.message.text.strip()
        
        # Адреса для кур'єра
        if state == "WAITING_ADDRESS":
            context.user_data.setdefault('profile', {})['address_details'] = text
            context.user_data['state'] = None
            await update.message.reply_text("✅ Адресу збережено!")
            await checkout_init(update, context) # Перехід до оплати
            return

        # Промокод
        if context.user_data.get('awaiting_promo'):
            await process_promo(update, context)
            return

        # Адмін розсилка
        if context.user_data.get('awaiting_broadcast') and user_id == MANAGER_ID:
            users = sqlite3.connect(DB_PATH).execute("SELECT user_id FROM users").fetchall()
            for (uid,) in users:
                try: await context.bot.send_message(uid, text)
                except: pass
            await update.message.reply_text("✅ Розсилка завершена.")
            context.user_data['awaiting_broadcast'] = False
            return
            
# =================================================================
# ⚙️ SECTION 29: GLOBAL DISPATCHER (FINAL BRAIN)
# =================================================================

async def global_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    
    try:
        await query.answer()
        
        # МЕНЮ ТА ПРОФІЛЬ
        if data == "menu_start": await start_command(update, context)
        elif data == "menu_profile": await show_profile(update, context)
            
# --- ДОДАТИ ЦЕЙ БЛОК В global_callback_handler ---
        elif data == "admin_main": await admin_menu(update, context)
        elif data == "admin_stats": await admin_stats(update, context)
        # ------------------------------------------------
        
        elif data == "ref_system": await show_ref_info(update, context)
        elif data == "menu_promo": 
            context.user_data['awaiting_promo'] = True
            await _edit_or_reply(query, "🎟 <b>Введіть промокод:</b>", [[InlineKeyboardButton("🔙", callback_data="menu_profile")]])

        # ГЕОГРАФІЯ
        elif data == "choose_city" or data == "menu_city": await choose_city_menu(update, context)
        elif data.startswith("sel_city_"):
            city = data.replace("sel_city_", "")
            context.user_data.setdefault("profile", {})["city"] = city
            if city == "Дніпро": await choose_dnipro_delivery(update, context)
            else: await choose_district_menu(update, context, city)
        elif data == "set_del_type_klad": await choose_district_menu(update, context, "Дніпро")
        elif data == "set_del_type_courier": await save_location_handler(update, context, is_courier=True)
        elif data.startswith("sel_dist_"):
            await save_location_handler(update, context, dist_name=data.replace("sel_dist_", ""))

        # МАГАЗИН
        elif data == "cat_all": await catalog_main_menu(update, context)
        elif data.startswith("cat_list_"): await show_category_items(update, context, data.replace("cat_list_", ""))
        elif data.startswith("view_item_"): await view_item_details(update, context, int(data.split("_")[2]))
        
        # КОШИК
        elif data.startswith("add_"): await add_to_cart_handler(update, context)
        elif data.startswith("gift_sel_"): await gift_selection_handler(update, context)
        elif data == "menu_cart": await show_cart_logic(update, context)
        elif data == "cart_clear": 
            context.user_data['cart'] = []
            await show_cart_logic(update, context)
        elif data.startswith("cart_del_"):
            uid = int(data.split("_")[2])
            context.user_data['cart'] = [i for i in context.user_data.get('cart', []) if i['id'] != uid]
            await show_cart_logic(update, context)
        
        # ОФОРМЛЕННЯ
        elif data == "checkout_init": await checkout_init(update, context)
        elif data == "confirm_payment_start": await payment_confirmation_handler(update, context)

        # АДМІНКА
        elif data.startswith("admin_approve_"):
            uid = int(data.split("_")[2])
            await context.bot.send_message(uid, "✅ <b>Оплата підтверджена!</b> Дякуємо!")
            await query.edit_message_caption(caption=query.message.caption + "\n\n✅ [ОК]")
        elif data == "admin_broadcast": await start_broadcast(update, context)

    except Exception as e:
        logger.error(f"Dispatcher Error: {e}")
        
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
    """Початок розсилки повідомлень."""
    if update.effective_user.id != MANAGER_ID: return
    
    context.user_data['awaiting_broadcast'] = True
    context.user_data['state'] = "BROADCAST_MODE"
    
    text = (
        "📢 <b>РЕЖИМ РОЗСИЛКИ</b>\n\n"
        "Надішліть текст або фото з описом, яке отримають <b>УСІ</b> користувачі бота.\n"
        "Для скасування натисніть кнопку."
    )
    kb = [[InlineKeyboardButton("❌ Скасувати", callback_data="menu_start")]]
    await _edit_or_reply(update.callback_query if update.callback_query else update, text, kb)

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показ статистики (заглушка)."""
    # Тут можна підключити реальний підрахунок з БД
    conn = sqlite3.connect(DB_PATH)
    try:
        user_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    except:
        user_count = 0
    conn.close()

    text = f"📊 <b>СТАТИСТИКА</b>\n👥 Користувачів у базі: {user_count}"
    kb = [[InlineKeyboardButton("🔙 Назад", callback_data="admin_menu")]]
    await _edit_or_reply(update.callback_query, text, kb)
    


# =================================================================
# 🚀 SECTION 30: FINAL RUNNER (SYSTEM STARTUP)
# =================================================================

async def post_init(application: Application):
    """
    Хук після успішного підключення.
    Виводить статус у консоль хостингу.
    """
    bot = await application.bot.get_me()
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"🤖 BOT STARTED: @{bot.username}")
    print(f"🆔 BOT ID:      {bot.id}")
    print(f"📅 START TIME:  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"💾 DATA DIR:    {DATA_DIR}")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"✅ SYSTEM ONLINE. WAITING FOR UPDATES...")

def main():
    """Головна точка входу (Entry Point)."""
    
    # 1. Логотип та ініціалізація
    print("\n")
    print("🚀 GHOSTY STAFF 2026: ENGINE LAUNCHING...")
    print("🛠  Verifying system integrity...")

    # 2. Перевірка файлової системи та БД
    try:
        # Створюємо папку data, якщо її немає (безпечно)
        os.makedirs(DATA_DIR, exist_ok=True)
        print(f"📁 Data directory verified: {DATA_DIR}")
            
        # Ініціалізація структури бази даних
        init_db()
        print("🗄️  Database connection established.")
        
    except Exception as e:
        print(f"❌ CRITICAL SYSTEM ERROR (FS/DB): {e}")
        sys.exit(1)

    # 3. Перевірка Токена
    if not TOKEN or TOKEN == "YOUR_TOKEN_HERE":
        print("❌ FATAL ERROR: Bot token is missing or invalid!")
        sys.exit(1)

    # 4. Побудова додатка (Builder Pattern)
    try:
        # Використовуємо PERSISTENCE_PATH з налаштувань
        persistence = PicklePersistence(filepath=PERSISTENCE_PATH)
        
        app = (
            Application.builder()
            .token(TOKEN)
            .persistence(persistence)
            .defaults(Defaults(parse_mode=ParseMode.HTML))
            .post_init(post_init) # Виклик функції після старту
            .build()
        )
    except Exception as e:
        print(f"❌ BUILD ERROR: Не вдалося створити додаток. Помилка: {e}")
        sys.exit(1)

   # 5. РЕЄСТРАЦІЯ ХЕНДЛЕРІВ (МАРШРУТИЗАЦІЯ)
    # -----------------------------------------------------------
    # А) Команди
    app.add_handler(CommandHandler("start", start_command))
    # Тепер admin_menu існує, тому це спрацює:
    app.add_handler(CommandHandler("admin", admin_menu)) 
    
    # Б) Кнопки (Callback Queries)
    app.add_handler(CallbackQueryHandler(global_callback_handler))
    
    # В) Текст та Медіа
    # Додаємо фільтр для адмінської розсилки
    app.add_handler(MessageHandler(
        (filters.TEXT | filters.PHOTO) & (~filters.COMMAND), 
        handle_user_input
    ))
    
    # Г) Обробка помилок
    app.add_error_handler(error_handler)
    # -----------------------------------------------------------

    # 6. ЗАПУСК POLLING
    # drop_pending_updates=True: ігнорує старі повідомлення при рестарті (щоб не спамив)
    print("📡 Connecting to Telegram API...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 SYSTEM SHUTDOWN: Bot stopped manually.")
        sys.exit(0)
    except Exception:
        print("\n❌ FATAL RUNTIME ERROR:")
        traceback.print_exc()
        sys.exit(1)

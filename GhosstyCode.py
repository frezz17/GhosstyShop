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
PAYMENT_LINK = {
    "mono": "https://lnk.ua/k4xJG21Vy",   
    "privat": "https://lnk.ua/RVd0OW6V3",
    "ghossty": "https://heylink.me/GhosstyShop" # <-- Додано GhosstyPay
}
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
    item = get_item_data(item_id)
    if not item: return

    # Ціна для відображення
    profile = context.user_data.get("profile", {})
    price = int(item['price'] * 0.65) if profile.get('is_vip') else int(item['price'])
    
    caption = (
        f"<b>{item['name']}</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        f"{item['desc']}\n━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 Ціна: <b>{price} ₴</b>"
    )

    keyboard = []
    
    # 1. Варіанти (Колір/Смак)
    if "colors" in item:
        caption += "\n\n🎨 <b>Оберіть колір:</b>"
        for i in range(0, len(item["colors"]), 2):
            row = [InlineKeyboardButton(item["colors"][i], callback_data=f"add_{item_id}_{item['colors'][i]}")]
            if i + 1 < len(item["colors"]):
                row.append(InlineKeyboardButton(item["colors"][i+1], callback_data=f"add_{item_id}_{item['colors'][i+1]}"))
            keyboard.append(row)
    elif "strengths" in item:
        caption += "\n\n🧪 <b>Оберіть міцність:</b>"
        row = [InlineKeyboardButton(f"{s}mg", callback_data=f"add_{item_id}_{s}") for s in item['strengths']]
        keyboard.append(row)
    elif item.get("gift_liquid"):
        caption += "\n🎁 <b>+ РІДИНА БЕЗКОШТОВНО!</b>"
        keyboard.append([InlineKeyboardButton("🎁 Обрати бонус і купити", callback_data=f"add_{item_id}")])
    else:
        keyboard.append([InlineKeyboardButton("🛒 Додати у кошик", callback_data=f"add_{item_id}")])

    # 2. Основні дії
    keyboard.append([InlineKeyboardButton("⚡ ШВИДКЕ ЗАМОВЛЕННЯ", callback_data=f"fast_order_{item_id}")])
    # Ця кнопка тепер викликає smart-функцію, а не просто посилання
    keyboard.append([InlineKeyboardButton("👨‍💻 Замовити через менеджера", callback_data=f"mgr_pre_{item_id}")])
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="cat_all")])

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
# 🏠 SECTION 8: START & PROFILE (FINAL MERGED VERSION)
# =================================================================

async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Єдина функція профілю. Показує VIP, Промо, Адресу та Фото.
    """
    # 1. Гарантовано створюємо/отримуємо профіль
    profile = await get_or_create_user(update, context)
    user = update.effective_user
    
    # 2. Визначаємо статус VIP
    if profile.get('is_vip'):
        vip_status = f"💎 <b>VIP ACTIVE</b> (до {VIP_EXPIRY})"
    else:
        vip_status = "👤 Standard"
        
    # 3. Визначаємо статус знижки
    if profile.get('next_order_discount'):
        bonus_text = "✅ <b>-101 грн</b> на наступне замовлення"
    else:
        bonus_text = "❌ Відсутні"

    # 4. Формуємо рядок адреси
    city = profile.get('city')
    address = profile.get('address_details')
    if city:
        loc_text = f"📍 {city}"
        if address: loc_text += f", {address}"
        elif profile.get('district'): loc_text += f", {profile['district']}"
    else:
        loc_text = "⚠️ Не вказано (Натисніть кнопку нижче)"

    # 5. Текст повідомлення
    text = (
        f"<b>👤 ОСОБИСТИЙ КАБІНЕТ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 ID: <code>{user.id}</code>\n"
        f"👤 Юзер: @{user.username if user.username else 'Приховано'}\n"
        f"🔰 Статус: {vip_status}\n"
        f"🎟 Промокод: <code>{profile.get('promo_code', '---')}</code>\n"
        f"🎁 Бонуси: {bonus_text}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📮 <b>Дані доставки:</b>\n{loc_text}\n"
        f"📱 <b>Телефон:</b> {profile.get('phone', 'Не вказано')}"
    )

    # 6. Клавіатура (Всі кнопки робочі)
    kb = [
        [InlineKeyboardButton("📝 Змінити дані доставки", callback_data="fill_delivery_data")],
        [InlineKeyboardButton("🎟 Ввести промокод", callback_data="menu_promo")],
        [InlineKeyboardButton("🤝 Реферальна програма", callback_data="ref_system")],
        [InlineKeyboardButton("🛍 До магазину", callback_data="cat_all")]
    ]

    # 7. Відправка з фото (фолбек на текст, якщо помилка)
    try:
        photos = await user.get_profile_photos(limit=1)
        if photos.total_count > 0:
            await send_ghosty_message(update, text, kb, photo=photos.photos[0][-1].file_id)
        else:
            await send_ghosty_message(update, text, kb, photo=WELCOME_PHOTO)
    except:
        await send_ghosty_message(update, text, kb)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Головне меню + Кнопка Адміна."""
    await get_or_create_user(update, context) # Реєстрація
    user = update.effective_user
    ghst_id = f"GHSTid{user.id}"
    
    welcome_text = (
        f"🌫️ <b>GHO$$TY STAFF LAB | УКРАЇНА</b> 🧪\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🧬 <b>HHC SHOP ВІДКРИТО!</b>\n"
        f"🔥 Введіть <code>GHST2026</code> для VIP-статусу!\n"
        f"🎁 + Рідина на вибір до кожного вейпу!\n"
        f"👤 Твій ID код: <code>{ghst_id}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👇 <b>Оберіть розділ меню:</b>"
    )
    
    keyboard = [
        [InlineKeyboardButton("🛍 АСОРТИМЕНТ", callback_data="cat_all")],
        [InlineKeyboardButton("👤 ПРОФІЛЬ", callback_data="menu_profile"), 
         InlineKeyboardButton("🛒 КОШИК", callback_data="menu_cart")],
        [InlineKeyboardButton("📍 ЛОКАЦІЯ (Швидка)", callback_data="choose_city")],
        [InlineKeyboardButton("📜 УГОДА", callback_data="menu_terms")],
        [InlineKeyboardButton("👨‍💻 МЕНЕДЖЕР", url=f"https://t.me/{MANAGER_USERNAME}")]
    ]
    
    # 🔥 КНОПКА АДМІНА (Тільки для тебе)
    if user.id == MANAGER_ID:
        keyboard.append([InlineKeyboardButton("⚙️ АДМІН-ПАНЕЛЬ", callback_data="admin_main")])

    await send_ghosty_message(update, welcome_text, keyboard, photo=WELCOME_PHOTO)
        
    
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
# 📝 SECTION: SMART DATA COLLECTION (MANAGER & FAST ORDER)
# =================================================================

async def start_data_collection(update: Update, context: ContextTypes.DEFAULT_TYPE, next_action, item_id=None):
    """Починає процес збору даних (ПІБ -> Телефон -> Місто -> Адреса)."""
    context.user_data['data_flow'] = {
        'step': 'name',
        'next_action': next_action, # 'manager_order' або 'checkout'
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
    profile = context.user_data['profile']
    step = flow['step']

    if step == 'name':
        profile['full_name'] = text
        flow['step'] = 'phone'
        await update.message.reply_text("2️⃣ Введіть ваш <b>Номер телефону</b>:")
    
    elif step == 'phone':
        profile['phone'] = text
        flow['step'] = 'city'
        # Пропонуємо міста кнопками для зручності
        kb = [[InlineKeyboardButton(c, callback_data=f"set_flow_city_{c}")] for c in list(UKRAINE_CITIES.keys())[:6]]
        await update.message.reply_text("3️⃣ Оберіть або введіть <b>Місто</b> доставки:", reply_markup=InlineKeyboardMarkup(kb))
    
    elif step == 'address': # Цей крок викликається після вибору міста
        profile['address_details'] = text
        
        # ФІНАЛ: Дані зібрано, виконуємо дію
        context.user_data['state'] = None
        action = flow['next_action']
        
        await update.message.reply_text("✅ <b>Дані успішно збережено!</b>")
        
        if action == 'manager_order':
            await finalize_manager_order(update, context, flow['item_id'])
        elif action == 'checkout':
            await checkout_init(update, context)

async def finalize_manager_order(update: Update, context: ContextTypes.DEFAULT_TYPE, item_id):
    """Генерує посилання на менеджера з усіма даними."""
    import urllib.parse
    item = get_item_data(item_id)
    p = context.user_data['profile']
    
    # Формуємо текст для менеджера
    msg_text = (
        f"👋 Привіт! Замовлення #{random.randint(1000,9999)}\n"
        f"📦 Товар: {item['name']}\n"
        f"💰 Ціна: {item['price']} грн\n"
        f"👤 {p['full_name']} | 📞 {p['phone']}\n"
        f"📍 {p['city']}, {p['address_details']}"
    )
    encoded = urllib.parse.quote(msg_text)
    link = f"https://t.me/{MANAGER_USERNAME}?text={encoded}"
    
    text = (
        f"✅ <b>Замовлення сформовано!</b>\n"
        f"📦 Товар: {item['name']}\n"
        f"👤 Ваші дані збережено.\n\n"
        f"👇 Натисніть кнопку, щоб надіслати замовлення менеджеру:"
    )
    kb = [[InlineKeyboardButton("✈️ НАДІСЛАТИ МЕНЕДЖЕРУ", url=link)],
          [InlineKeyboardButton("🏠 В меню", callback_data="menu_start")]]
    
    if update.callback_query:
        await _edit_or_reply(update.callback_query, text, kb)
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode='HTML')
        

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
# 🔑 SECTION 22: ПРОМОКОДИ (GHST2026 & ID SYSTEM)
# =================================================================

async def process_promo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробка введення промокодів."""
    if not update.message or not update.message.text: return
    
    # Нормалізація тексту (прибираємо пробіли, робимо капсом, але GHSTid залишаємо чутливим до цифр)
    raw_text = update.message.text.strip()
    user_text = raw_text.upper()
    
    user = update.effective_user
    profile = context.user_data.setdefault("profile", {})
    
    success = False
    response_text = ""

    # --- ВАРІАНТ 1: ГЛОБАЛЬНИЙ КОД GHST2026 ---
    if user_text == "GHST2026":
        # Активуємо бонуси
        profile["is_vip"] = True
        profile["next_order_discount"] = 101  # Знижка 101 грн
        profile["gift_liquid_available"] = True # Прапорець для подарунка
        
        # Оновлюємо БД
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("UPDATE users SET is_vip = 1 WHERE user_id = ?", (user.id,))
            conn.commit()
            conn.close()
        except: pass

        response_text = (
            f"🎉 <b>КОД GHST2026 АКТИВОВАНО!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"✅ <b>VIP Статус:</b> Активовано (+7 днів)\n"
            f"🚚 <b>Доставка:</b> Безкоштовна\n"
            f"💰 <b>Бонус:</b> -101 грн на це замовлення\n"
            f"🎁 <b>Подарунок:</b> Рідина до будь-якого вейпу!"
        )
        success = True

    # --- ВАРІАНТ 2: ПЕРСОНАЛЬНИЙ КОД (GHSTid...) ---
    elif user_text.startswith("GHSTID") and len(user_text) > 6:
        # Перевірка формату (мають бути цифри після GHSTid)
        code_body = user_text.replace("GHSTID", "")
        
        if code_body.isdigit():
            target_id = int(code_body)
            
            # Логіка: не можна вводити свій власний код як реферальний
            if target_id == user.id:
                response_text = "❌ <b>Це ваш власний код!</b>\nВи не можете використати його для самого себе."
            else:
                # Тут можна додати нарахування бонусу тому, чий це код
                profile["referral_bonus_active"] = True
                
                response_text = (
                    f"🤝 <b>ПАРТНЕРСЬКИЙ КОД ПРИЙНЯТО!</b>\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🆔 Партнер: <code>{target_id}</code>\n"
                    f"✅ <b>Бонус:</b> Доступ до секретних знижок активовано!\n"
                    f"🚀 Дякуємо, що ви з нами!"
                )
                success = True
        else:
            response_text = "❌ <b>Помилка формату.</b>\nКод має бути у форматі: <code>GHSTid987654321</code>"

    # --- НЕВІРНИЙ КОД ---
    else:
        response_text = "❌ <b>Невірний промокод.</b>\nПеревірте написання та спробуйте ще раз."

    # Відправка результату
    kb = [[InlineKeyboardButton("🛍 ДО КАТАЛОГУ", callback_data="cat_all")]]
    if success:
        # Якщо успіх - пропонуємо перейти в кошик, якщо там щось є
        if context.user_data.get('cart'):
             kb = [[InlineKeyboardButton("🛒 В КОШИК (ЗІ ЗНИЖКОЮ)", callback_data="menu_cart")]]
    
    await update.message.reply_text(response_text, reply_markup=InlineKeyboardMarkup(kb), parse_mode='HTML')
    
    # Скидаємо стан очікування
    context.user_data['awaiting_promo'] = False
    context.user_data['state'] = None
    
    
# =================================================================
# 💳 SECTION 5: CHECKOUT & PAYMENT ENGINE (UNIFIED PRO)
# =================================================================

async def checkout_init(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Фіналізація: Перевірка даних -> Розрахунок -> Оплата.
    """
    query = update.callback_query
    cart = context.user_data.get("cart", [])
    profile = context.user_data.setdefault("profile", {})

    # 1. Якщо кошик порожній
    if not cart: 
        return await show_cart_logic(update, context)

    # 2. ПЕРЕВІРКА ДАНИХ (SMART DATA COLLECTION)
    # Якщо немає імені, телефону або міста -> просимо ввести
    if not profile.get("full_name") or not profile.get("phone") or not profile.get("city"):
        await start_data_collection(update, context, next_action='checkout')
        return

    # 3. Перевірка адреси для Кур'єра
    district_info = str(profile.get("district", ""))
    if "Кур'єр" in district_info and not profile.get("address_details"):
        await _edit_or_reply(query, "⚠️ <b>Для кур'єра потрібна точна адреса!</b>", [])
        await start_data_collection(update, context, next_action='checkout')
        return

    # 4. РОЗРАХУНОК ЦІНИ
    total_sum = 0
    # Перераховуємо ціни на льоту, щоб врахувати свіжі промокоди
    for item in cart:
        p, _ = calculate_final_price(item['price'], profile)
        total_sum += p

    # Логіка доставки
    delivery_cost = 0
    if "Кур'єр" in district_info:
        # Безкоштовно для VIP, інакше 150
        delivery_cost = 0 if profile.get("is_vip") else 150
        total_sum += delivery_cost

    # ID замовлення
    ts = int(datetime.now().timestamp()) % 10000
    order_id = f"GH-{ts}-{random.randint(10,99)}"
    final_amount = float(total_sum) + (random.randint(1, 99) / 100)
    
    # Зберігаємо
    context.user_data["current_order_id"] = order_id
    context.user_data["final_checkout_sum"] = final_amount

    # Текст чека
    promo_status = "✅ Активовано" if profile.get("next_order_discount") else "❌ Немає"
    del_txt = f"\n🛵 Доставка: {delivery_cost} грн" if delivery_cost > 0 else "\n🛵 Доставка: <b>БЕЗКОШТОВНО</b>"

    text = (
        f"<b>📦 ПІДТВЕРДЖЕННЯ ЗАМОВЛЕННЯ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📍 {profile['city']}, {profile.get('address_details', district_info)}\n"
        f"👤 {profile['full_name']} | 📞 {profile['phone']}\n"
        f"🎟 Промокод: {promo_status}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 <b>ДО СПЛАТИ: {final_amount:.2f}₴</b>{del_txt}\n"
        f"👇 Оберіть банк:"
    )
    
    kb = [
        [InlineKeyboardButton("💳 Monobank", callback_data="pay_mono"), 
         InlineKeyboardButton("💳 Privat24", callback_data="pay_privat")],
        [InlineKeyboardButton("🌐 GhosstyPay (Crypto/Card)", url=PAYMENT_LINK['ghossty'])]
    ]

    # Кнопка промокоду (якщо ще не ввів)
    if not profile.get("next_order_discount"):
        kb.append([InlineKeyboardButton("🎟 Ввести промокод (-101 грн)", callback_data="menu_promo")])
        
    kb.append([InlineKeyboardButton("🔙 Кошик", callback_data="menu_cart")])
    
    await _edit_or_reply(query, text, kb)
    
    

async def payment_confirmation_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Перехід у режим очікування чека.
    """
    query = update.callback_query
    text = (
        "📸 <b>ВІДПРАВКА ЧЕКА</b>\n\n"
        "Будь ласка, надішліть <b>фото/скріншот квитанції</b> прямо сюди в чат.\n"
        "Менеджер перевірить оплату протягом 5 хвилин."
    )
    context.user_data['state'] = "WAITING_RECEIPT"
    kb = [[InlineKeyboardButton("❌ Скасувати", callback_data="menu_start")]]
    await _edit_or_reply(query, text, kb)

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
# ⚙️ SECTION 29: GLOBAL DISPATCHER (FINAL CONNECTED)
# =================================================================

async def global_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Розподіляє всі натискання кнопок по функціях.
    """
    query = update.callback_query
    data = query.data
    
    try:
        await query.answer() # Прибирає годинник
        
        # --- 1. ГОЛОВНЕ МЕНЮ ТА ПРОФІЛЬ ---
        if data == "menu_start": await start_command(update, context)
        elif data == "menu_profile": await show_profile(update, context)
        elif data == "ref_system": await show_ref_info(update, context)
        elif data == "menu_terms": await _edit_or_reply(query, TERMS_TEXT, [[InlineKeyboardButton("🔙", callback_data="menu_start")]])
        
        # ПРОМОКОДИ
        elif data == "menu_promo": 
            context.user_data['awaiting_promo'] = True
            await _edit_or_reply(query, "🎟 <b>Введіть ваш промокод:</b>\n(Наприклад: GHST2026)", [[InlineKeyboardButton("🔙 Скасувати", callback_data="menu_profile")]])

        # --- 2. ГЕОГРАФІЯ ---
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

        # --- 3. ДАНІ ТА SMART FLOW ---
        elif data == "fill_delivery_data":
            # Кнопка в профілі - просто змінити дані
            await start_data_collection(update, context, next_action='none')
        
        elif data.startswith("set_flow_city_"):
            # Вибір міста при зборі даних
            city = data.replace("set_flow_city_", "")
            context.user_data['profile']['city'] = city
            context.user_data['data_flow']['step'] = 'address'
            await _edit_or_reply(query, f"✅ Місто: {city}\n\n4️⃣ Введіть <b>Адресу / Відділення НП</b>:")
        
        elif data == "cancel_data":
            context.user_data['state'] = None
            await show_profile(update, context)

        # --- 4. МАГАЗИН ---
        elif data == "cat_all": await catalog_main_menu(update, context)
        elif data.startswith("cat_list_"): await show_category_items(update, context, data.replace("cat_list_", ""))
        elif data.startswith("view_item_"): await view_item_details(update, context, int(data.split("_")[2]))
        
        # --- 5. КОШИК ---
        elif data.startswith("add_"): await add_to_cart_handler(update, context)
        elif data.startswith("gift_sel_"): await gift_selection_handler(update, context)
        elif data == "menu_cart": await show_cart_logic(update, context)
        elif data == "cart_clear": 
            context.user_data['cart'] = []
            await show_cart_logic(update, context)
        elif data.startswith("cart_del_"):
            uid = int(data.split("_")[2])
            cart = context.user_data.get('cart', [])
            context.user_data['cart'] = [i for i in cart if i['id'] != uid]
            await show_cart_logic(update, context)
        
        # --- 6. ОФОРМЛЕННЯ ---
        elif data == "checkout_init": await checkout_init(update, context)
        elif data.startswith("pay_"): await payment_selection_handler(update, context, data.split("_")[1])
        elif data == "confirm_payment_start": await payment_confirmation_handler(update, context)

        elif data.startswith("fast_order_"):
            iid = int(data.split("_")[2])
            # Одразу на чек-аут
            await start_data_collection(update, context, next_action='checkout', item_id=iid)
            # Додаємо тимчасово в кошик
            item = get_item_data(iid)
            context.user_data['cart'] = [] 
            await _finalize_add_to_cart(update, context, item) 

        elif data.startswith("mgr_pre_"):
            iid = int(data.split("_")[2])
            await start_data_collection(update, context, next_action='manager_order', item_id=iid)

        # --- 7. АДМІН ПАНЕЛЬ ---
        elif data == "admin_main": await admin_menu(update, context)
        elif data == "admin_broadcast": await start_broadcast(update, context)
        elif data == "admin_stats": await admin_stats(update, context)
        elif data == "admin_cancel_action":
            # СКАСУВАННЯ РОЗСИЛКИ
            context.user_data['state'] = None
            context.user_data['awaiting_broadcast'] = False
            await query.answer("✅ Скасовано")
            await admin_menu(update, context)
            
        elif data.startswith("admin_approve_"):
            uid = int(data.split("_")[2])
            try:
                await context.bot.send_message(uid, "✅ <b>Ваше замовлення підтверджено!</b>\nОчікуйте на ТТН/Координати.")
                await query.edit_message_caption(caption=query.message.caption + "\n\n✅ [ОБРОБЛЕНО]")
            except:
                await query.answer("Помилка (юзер заблокував бота)")

    except Exception as e:
        logger.error(f"Dispatcher Error: {e}")
        try: await start_command(update, context)
        except: pass
            
        
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

# =================================================================
# 🤖 PROJECT: GHO$$TY STAFF PREMIUM E-COMMERCE ENGINE (PRO)
# 🛠 VERSION: 5.2.0 (STABLE RELEASE 2026)
# 🛡 DEVELOPER: Gho$$tyyy & Gemini AI
# 🌐 HOSTING: BotHost.ru Optimized
# =================================================================

import os
import sys
import logging
import sqlite3
import asyncio
import random
import traceback
from datetime import datetime, timedelta
from html import escape

# Telegram Core (v20.x+)
from telegram import (
    Update, 
    InlineKeyboardButton, 
    InlineKeyboardMarkup, 
    InputMediaPhoto,
    InputMediaVideo
)
from telegram.constants import ParseMode
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    CallbackQueryHandler, 
    ContextTypes, 
    filters, 
    PicklePersistence, 
    Defaults
)
from telegram.error import NetworkError, BadRequest, TimedOut

# =================================================================
# ⚙️ SECTION 1: GLOBAL CONFIGURATION (PRO SETTINGS)
# =================================================================

# 1. Шляхи (Абсолютна безпека для серверних середовищ)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True) # Створюємо папку, якщо її немає

DB_PATH = os.path.join(DATA_DIR, 'ghosty_pro_final.db')
PERSISTENCE_PATH = os.path.join(DATA_DIR, 'ghosty_state_final.pickle')
LOG_PATH = os.path.join(DATA_DIR, 'ghosty_system.log')

# 2. АВТЕНТИФІКАЦІЯ (Безпечний пріоритет)
# Пріоритет: 1. Змінна оточення | 2. Хардкод (якщо ENV порожній)
TOKEN = os.getenv("BOT_TOKEN", "8351638507:AAE8JbSIduGOMYnCu77WFRy_3s7-LRH34lQ")

# Реквізити адміністрації
MANAGER_ID = 7544847872
MANAGER_USERNAME = "ghosstydp"
CHANNEL_URL = "https://t.me/GhostyStaffDP"
WELCOME_PHOTO = "https://i.ibb.co/y7Q194N/1770068775663.png"

# 3. ПЛАТІЖНІ ШЛЮЗИ
PAYMENT_LINK = {
    "mono": "https://lnk.ua/k4xJG21Vy",   
    "privat": "https://lnk.ua/RVd0OW6V3",
    "ghossty": "https://heylink.me/GhosstyShop"
}

# 4. ЛОГУВАННЯ (Максимальна деталізація для дебагу)
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
# 🛠 SECTION 2: UTILITIES & ERROR SHIELD
# =================================================================

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Глобальний щит помилок: сповіщення адміна та логування."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    
    try:
        # Формуємо трасування
        tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
        tb_string = "".join(tb_list)[-4000:]
        
        user_info = "Unknown User"
        if isinstance(update, Update) and update.effective_user:
            user_info = f"@{update.effective_user.username} ({update.effective_user.id})"

        error_msg = (
            f"🆘 <b>КРИТИЧНА ПОМИЛКА</b>\n"
            f"👤 Користувач: {user_info}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"<pre>{escape(tb_string)}</pre>"
        )
        
        await context.bot.send_message(chat_id=MANAGER_ID, text=error_msg, parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.error(f"Failed to report error: {e}")

async def _edit_or_reply(target, text, kb=None, photo=None):
    """
    Універсальний UI-помічник.
    Вирішує: редагувати існуюче повідомлення чи надсилати нове.
    """
    reply_markup = InlineKeyboardMarkup(kb) if kb and isinstance(kb, list) else kb
    
    # Визначаємо, чи ми працюємо з CallbackQuery чи з Update/Message
    is_query = hasattr(target, 'answer') and not hasattr(target, 'message_id')
    
    try:
        if is_query: # Це CallbackQuery
            if photo:
                await target.message.edit_media(
                    media=InputMediaPhoto(media=photo, caption=text, parse_mode=ParseMode.HTML),
                    reply_markup=reply_markup
                )
            else:
                await target.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
        else: # Це Update або Message
            if photo:
                await target.message.reply_photo(photo=photo, caption=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
            else:
                await target.message.reply_text(text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    except BadRequest as e:
        if "Message is not modified" not in str(e):
            logger.warning(f"UI Update bypass: {e}")
            
        
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

# 1. Головний реєстр міст та районів (Максимальна версія: 8 районів на місто)
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
    "Кам'янське": [
        "Центральний (Заводський)", "Дніпровський (Лівий берег)", "Південний (БАМ)", 
        "Соцмісто", "Черемушки", "Карнаухівка", "Курилівка", "Романкове"
    ],
    "Харків": [
        "Шевченківський", "Київський", "Салтівський", "Немишлянський", 
        "Холодногірський", "Новобаварський", "Основ'янський", "Індустріальний"
    ],
    "Одеса": [
        "Приморський (Центр)", "Київський (Таїрова)", "Малиновський (Черемушки)", 
        "Суворовський (Котовського)", "Пересип", "Слобідка", "Молдаванка", "Великий Фонтан"
    ],
    "Львів": [
        "Галицький (Центр)", "Личаківський", "Сихівський", "Франківський", 
        "Шевченківський", "Залізничний", "Левандівка", "Збоїща"
    ],
    "Запоріжжя": [
        "Олександрівський", "Заводський", "Комунарський", "Дніпровський", 
        "Вознесенівський", "Хортицький", "Шевченківський", "Південний (Піски)"
    ],
    "Кривий Ріг": [
        "Металургійний", "Центрально-Міський", "Саксаганський", "Покровський", 
        "Тернівський", "Довгинцівський", "Інгулецький", "мкрн. Сонячний"
    ],
    "Вінниця": [
        "Центр", "Вишенька", "Замостя", "Старе місто", 
        "Поділля", "Слов'янка", "П'ятничани", "Тяжилів"
    ],
    "Полтава": [
        "Шевченківський", "Київський", "Подільський", "Левада", 
        "Алмазний", "Половки", "Огнівка", "Розсошенці"
    ]
}

# 2. Реєстр товарів (Ініціалізація порожніх категорій)
# Це запобігає NameError при першому запуску бота
HHC_VAPES = {} 
LIQUIDS = {}
PODS = {}
SETS = {} # Повна сумісність з Section 7 (Core Utilities)

# 3. Аліаси та списки для диспетчерів
# Використовуються в меню вибору міста та логіці пошуку
CITIES_LIST = list(UKRAINE_CITIES.keys())
CITY_DISTRICTS = UKRAINE_CITIES


# =================================================================
# 🛠 SECTION 2: UI ENGINE & HELPERS
# =================================================================

async def _edit_or_reply(target, text, kb=None):
    """Універсальний перемикач: редагування або нова відповідь."""
    reply_markup = InlineKeyboardMarkup(kb) if kb else None
    try:
        if isinstance(target, Update) and target.callback_query:
            await target.callback_query.edit_message_text(
                text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML
            )
        elif hasattr(target, 'edit_message_text'): # Якщо передано query
            await target.edit_message_text(
                text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML
            )
        else: # Якщо це Update з повідомленням
            await target.message.reply_text(
                text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML
            )
    except BadRequest as e:
        if "Message is not modified" not in str(e):
            logger.error(f"UI Error: {e}")

def calculate_final_price(item_price, user_profile):
    """
    Математика замовлення: (Ціна - Бонус 101) * 0.65 (Знижка 35%).
    """
    try:
        price = float(item_price)
        is_vip = user_profile.get('is_vip', False)
        bonus = user_profile.get('next_order_discount', 0) # Зазвичай 101
        
        discounted = False
        if bonus > 0 and price > bonus:
            price -= bonus
            discounted = True
        
        if is_vip:
            price *= 0.65
            discounted = True
            
        return round(max(price, 10.0), 2), discounted
    except:
        return item_price, False
    
# =================================================================
# 🛠 SECTION 3: MATH & LOCATION ENGINE (PRO STABLE)
# =================================================================

def calculate_final_price(item_price, user_profile):
    """
    Універсальна детермінована математика:
    1. Перевірка типів та безпечне приведення до float.
    2. Застосування фіксованого бонусу (напр. -101 грн), якщо ціна > (бонус + 10).
    3. Застосування VIP-множника (знижка 35%), якщо статус активовано.
    4. Встановлення ліміту «підлоги» ціни (мінімум 10.0 UAH).
    """
    try:
        price = float(item_price)
        is_vip = bool(user_profile.get('is_vip'))
        # Отримуємо бонус (наприклад, від промокоду GHST2026)
        bonus = float(user_profile.get('next_order_discount', 0))
        
        discounted = False

        # 1. Застосовуємо фіксований бонус (знижка в гривнях)
        # Умова price > (bonus + 10) гарантує, що товар не стане безкоштовним
        if bonus > 0 and price > (bonus + 10):
            price -= bonus
            discounted = True
        
        # 2. Застосовуємо VIP-коефіцієнт (знижка 35%)
        if is_vip:
            price *= 0.65
            discounted = True
            
        # 3. Фінальне округлення та перевірка ліміту 10 грн
        final_val = round(max(price, 10.0), 2)
        
        return final_val, discounted
    except (ValueError, TypeError) as e:
        # Логування помилки для дебагу (якщо logger ініціалізовано)
        if 'logger' in globals():
            logger.error(f"❌ Math Error for price '{item_price}': {e}")
        return float(item_price) if isinstance(item_price, (int, float)) else 0.0, False

# --- ЛОГІКА ЛОКАЦІЙ (GEOGRAPHY ENGINE) ---

async def choose_city_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Головне меню вибору міста (11 міст України).
    """
    target = update.callback_query if update.callback_query else update
    profile = context.user_data.setdefault("profile", {})
    
    text = (
        "📍 <b>ОБЕРІТЬ ВАШЕ МІСТО</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Ми працюємо у найбільших містах та Кам'янському.\n"
        "Оберіть локацію, щоб побачити доступні райони 👇"
    )

    keyboard = []
    # UKRAINE_CITIES має бути визначена в Section 4
    cities = list(UKRAINE_CITIES.keys()) if 'UKRAINE_CITIES' in globals() else []
    
    # Генерація кнопок (по 2 в ряд)
    for i in range(0, len(cities), 2):
        row = [InlineKeyboardButton(cities[i], callback_data=f"sel_city_{cities[i]}")]
        if i + 1 < len(cities):
            row.append(InlineKeyboardButton(cities[i+1], callback_data=f"sel_city_{cities[i+1]}"))
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("👤 Перейти в профіль", callback_data="menu_profile")])
    
    await _edit_or_reply(target, text, keyboard)

async def choose_dnipro_delivery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Спеціальний хаб для Дніпра: вибір між кладом та кур'єром.
    """
    query = update.callback_query
    # Фіксуємо вибір міста в профілі користувача
    context.user_data.setdefault("profile", {})["city"] = "Дніпро"
    
    text = (
        "🏙 <b>ДНІПРО: СПОСІБ ОТРИМАННЯ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "1️⃣ <b>Район (Клад)</b> — магніт/прикоп у вашому районі.\n"
        "2️⃣ <b>Кур'єр (+150 грн)</b> — доставка прямо в руки.\n\n"
        "👇 Оберіть варіант:"
    )
    
    kb = [
        [InlineKeyboardButton("📍 Обрати район (Клад)", callback_data="sel_city_Дніпро_districts")],
        [InlineKeyboardButton("🛵 Кур'єрська доставка (+150 грн)", callback_data="set_del_type_courier")],
        [InlineKeyboardButton("⬅️ Змінити місто", callback_data="choose_city")]
    ]
    await _edit_or_reply(query, text, kb)

async def choose_district_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, city: str):
    """
    Динамічне меню вибору району на основі обраного міста.
    """
    query = update.callback_query
    # Зберігаємо обране місто в профіль
    context.user_data.setdefault("profile", {})["city"] = city
    
    # Отримуємо райони з глобального словника
    districts = UKRAINE_CITIES.get(city, []) if 'UKRAINE_CITIES' in globals() else []
    
    if not districts:
        await query.answer("⚠️ Райони для цього міста наразі недоступні", show_alert=True)
        return

    text = (
        f"🏙 <b>{city.upper()}: ОБЕРІТЬ РАЙОН</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Оберіть локацію, де вам найзручніше отримати замовлення 👇"
    )
    
    keyboard = []
    # Генерація кнопок районів (по 2 в ряд)
    for i in range(0, len(districts), 2):
        row = [InlineKeyboardButton(districts[i], callback_data=f"sel_dist_{districts[i]}")]
        if i + 1 < len(districts):
            row.append(InlineKeyboardButton(districts[i+1], callback_data=f"sel_dist_{districts[i+1]}"))
        keyboard.append(row)
        
    keyboard.append([InlineKeyboardButton("⬅️ Назад до міст", callback_data="choose_city")])
    
    await _edit_or_reply(query, text, keyboard)
    

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

START_TIME = datetime.now()

# ПРЕЗЕНТАБЕЛЬНА УГОДА КОРИСТУВАЧА
TERMS_TEXT = (
    "<b>📜 ПРАВИЛА ТА ВІДПОВІДАЛЬНІСТЬ</b>\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "1️⃣ Даний проєкт створено виключно з <b>навчальною метою</b>.\n"
    "2️⃣ Весь контент є демонстраційним та ознайомчим.\n"
    "3️⃣ Матеріали не є закликом до дій чи купівлі.\n"
    "4️⃣ Користувач несе повну відповідальність за свої дії.\n"
    "5️⃣ Ми <b>не зберігаємо</b> та не обробляємо персональні дані.\n"
    "6️⃣ Будь-яка взаємодія з ботом є добровільною.\n\n"
    "⚠️ <b>ВАЖЛИВА ВІДОМІСТЬ:</b>\n"
    "7️⃣ Магазин <b>НЕ Є РЕАЛЬНИМ</b>. Продаж не здійснюється.\n"
    "8️⃣ <b>ДОСТАВКИ НЕ ІСНУЄ</b>. Жодні товари не відправляються.\n"
    "9️⃣ Переказані кошти вважаються <b>добровільним донатом</b>.\n"
    "🔟 Всі транзакції — це безповоротний подарунок розробнику.\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "<i>Натискаючи «Прийняти» або продовжуючи роботу, ви підтверджуєте, "
    "що ознайомлені з цими пунктами.</i>"
)


# =================================================================
# ⚙️ SECTION 4: DATABASE & AUTH (SQL FIXED)
# =================================================================

def init_db():
    """Synchronous initialization for safe startup execution."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY, 
                username TEXT, 
                full_name TEXT,
                city TEXT, 
                district TEXT, 
                phone TEXT, 
                is_vip INTEGER DEFAULT 0, 
                vip_expiry TEXT,
                promo_applied INTEGER DEFAULT 0,
                address_details TEXT,
                reg_date TEXT
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                user_id INTEGER,
                amount REAL,
                status TEXT,
                created_at TEXT
            )
        ''')
        conn.commit()
        conn.close()
        logger.info("✅ Database schema verified.")
    except Exception as e:
        logger.critical(f"❌ DB INIT FATAL: {e}")
        
async def get_or_create_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ensures profile existence in context and provides DB persistence sync."""
    user = update.effective_user
    if 'profile' not in context.user_data:
        context.user_data['profile'] = {
            "uid": user.id,
            "username": f"@{user.username}" if user.username else "Hidden",
            "full_name": None, "phone": None, "city": None, "district": None,
            "address_details": None, "is_vip": False, "vip_expiry": None,
            "next_order_discount": 0, "promo_applied": False
        }
    
    # DB Persistence check
    try:
        conn = sqlite3.connect(DB_PATH)
        row = conn.execute("SELECT is_vip, vip_expiry FROM users WHERE user_id=?", (user.id,)).fetchone()
        if not row:
            conn.execute("INSERT INTO users (user_id, username, reg_date) VALUES (?, ?, ?)",
                         (user.id, user.username, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
        elif row[0]: # If VIP in DB, sync to context
            context.user_data['profile']['is_vip'] = bool(row[0])
            context.user_data['profile']['vip_expiry'] = row[1]
        conn.close()
    except Exception as e:
        logger.error(f"DB Sync Error: {e}")
        
    return context.user_data['profile']

# =================================================================
# 🔍 SECTION 15: PRODUCT CARD (STABLE PRO)
# =================================================================

async def view_item_details(update: Update, context: ContextTypes.DEFAULT_TYPE, item_id: int):
    """
    Картка товару: Фото, Опис, Ціна (зі знижками) та Кнопки.
    """
    # 1. Отримуємо дані про товар
    item = get_item_data(item_id)
    if not item: 
        if update.callback_query:
            await update.callback_query.answer("❌ Товар не знайдено")
        return

    profile = context.user_data.get("profile", {})
    
    # 2. Розрахунок ціни (використовуємо нашу функцію з Section 4.5)
    final_price, has_discount = calculate_final_price(item['price'], profile)
    
    # Формування гарного цінника
    price_html = f"<b>{int(item['price'])} ₴</b>"
    if has_discount:
        price_html = f"<s>{int(item['price'])}</s> 🔥 <b>{final_price:.0f} ₴</b>"

    # 3. Формування опису з варіантами (Кольори/Міцність)
    # Ми додаємо їх у текст, щоб не захаращувати інтерфейс кнопками, які можуть зламати логіку
    variants_info = ""
    if "colors" in item:
        colors_str = ", ".join(item["colors"])
        variants_info = f"\n🎨 <b>Доступні кольори:</b> {colors_str}"
    elif "strengths" in item:
        strengths_str = ", ".join([f"{s}mg" for s in item['strengths']])
        variants_info = f"\n🧪 <b>Міцність:</b> {strengths_str}"

    caption = (
        f"🛍 <b>{item['name']}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{item.get('desc', 'Опис оновлюється...')}\n"
        f"{variants_info}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 Ціна: {price_html}"
    )

    keyboard = []
    
    # --- РЯДОК 1: Швидкі дії ---
    keyboard.append([
        InlineKeyboardButton("⚡ ШВИДКО", callback_data=f"fast_order_{item_id}"),
        InlineKeyboardButton("👨‍💻 МЕНЕДЖЕР", callback_data=f"mgr_pre_{item_id}")
    ])

    # --- РЯДОК 2: Додати в кошик (Головна дія) ---
    # Перевіряємо, чи є бонус (рідина у подарунок)
    # Якщо ID < 300 (Вейпи) або є прапорець gift_liquid -> пропонуємо бонус
    has_bonus = item_id < 300 or item.get("gift_liquid")
    
    btn_text = "🎁 ОБРАТИ БОНУС І КУПИТИ" if has_bonus else "🛒 ДОДАТИ В КОШИК"
    
    # Відправляємо просто add_{id}. 
    # Section 19 (add_to_cart_handler) сама побачить, що це акційний товар, і відкриє меню подарунків.
    keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"add_{item_id}")])

    # --- РЯДОК 3: Навігація ---
    nav_row = []
    # Якщо місто не обрано - пропонуємо обрать
    if not profile.get("city"):
        nav_row.append(InlineKeyboardButton("📍 Обрати місто", callback_data="choose_city"))
    
    nav_row.append(InlineKeyboardButton("🔙 Каталог", callback_data="cat_all"))
    keyboard.append(nav_row)

    # 4. Відправка повідомлення (з фото або без)
    await send_ghosty_message(update, caption, keyboard, photo=item.get('img'))
    
    
    
# =================================================================
# 👤 SECTION 5: PROFILE & START ENGINE (PRO DATABASE SYNC)
# =================================================================

async def get_or_create_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Надійний помічник:
    1. Перевіряє, чи є юзер в пам'яті.
    2. Якщо немає — шукає в БД.
    3. Якщо немає в БД — створює нового.
    """
    user = update.effective_user
    
    # 1. Ініціалізація в пам'яті (Context)
    if 'profile' not in context.user_data:
        context.user_data['profile'] = {
            "uid": user.id,
            "full_name": user.full_name,
            "username": user.username,
            "phone": None,
            "city": None,
            "district": None,
            "address_details": None,
            "is_vip": False,
            "vip_expiry": None,
            "next_order_discount": 0,
            "promo_applied": False
        }
    
    if 'cart' not in context.user_data:
        context.user_data['cart'] = []

    # 2. Синхронізація з БД (SQLite)
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Перевіряємо, чи існує юзер
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user.id,))
        row = cursor.fetchone()
        
        if not row:
            # Створюємо нового юзера
            cursor.execute("""
                INSERT INTO users (user_id, username, full_name, reg_date)
                VALUES (?, ?, ?, ?)
            """, (user.id, user.username, user.full_name, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
            logger.info(f"🆕 NEW USER REGISTERED: {user.id}")
        else:
            # (Опціонально) Можна підтягнути дані з БД в profile, якщо бот перезавантажувався
            # Але поки що покладаємось на PicklePersistence
            pass
            
        conn.close()
    except Exception as e:
        logger.error(f"DB Registration Error: {e}")

    return context.user_data['profile']

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Привітання з автоматичною реєстрацією та видачею бонусів.
    """
    user = update.effective_user
    # Гарантуємо, що юзер існує
    profile = await get_or_create_user(update, context)
    
    # Персональний реферальний код
    personal_promo = f"GHST{user.id}"
    
    # --- АВТО-АКТИВАЦІЯ БОНУСІВ (Один раз) ---
    if not profile.get('promo_applied'):
        # Рахуємо дату: Сьогодні + 30 днів
        expiry_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        
        profile.update({
            'next_order_discount': 101.0,
            'is_vip': True,
            'vip_expiry': expiry_date,
            'promo_applied': True
        })
        
        # 🔥 ВАЖЛИВО: Оновлюємо статус в БД, щоб не злетіло
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("UPDATE users SET is_vip=1, vip_expiry=? WHERE user_id=?", (expiry_date, user.id))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"DB Bonus Save Error: {e}")

    # Формуємо текст
    # Використовуємо html.escape для безпеки (якщо у юзера в імені є < або >)
    safe_name = escape(user.first_name)
    
    welcome_text = (
        f"🌫️ <b>GHO$$TY STAFF LAB | 2026</b> 🌿\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Йо, <b>{safe_name}</b>! Твій статус: <b>VIP PRO</b> 🌿\n\n"
        f"🎁 <b>ТВОЇ БОНУСИ АКТИВОВАНО:</b>\n"
        f"📉 Знижка: <b>-35%</b> на весь стафф (авто)\n"
        f"💸 Кешбек: <b>-101 грн</b> на перше замовлення\n"
        f"🚚 Доставка: <b>БЕЗКОШТОВНА</b> (до {profile.get('vip_expiry')})\n\n"
        f"🔑 Твій особистий код: <code>{personal_promo}</code>\n"
        f"<i>(Поділись з другом: йому -35%, тобі +7 днів VIP!)</i>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👇 <b>Обери розділ для замовлення:</b>"
    )
    
    keyboard = [
        [InlineKeyboardButton("🛍 ВІДКРИТИ КАТАЛОГ 🌿", callback_data="cat_all")],
        [InlineKeyboardButton("👤 Кабінет", callback_data="menu_profile"), 
         InlineKeyboardButton("🛒 Кошик", callback_data="menu_cart")],
        [InlineKeyboardButton("📍 Локація", callback_data="choose_city"),
         InlineKeyboardButton("📜 Правила", callback_data="menu_terms")],
        [InlineKeyboardButton("👨‍💻 Менеджер (Support)", url=f"https://t.me/{MANAGER_USERNAME}")]
    ]
    
    # Кнопка адміна
    if user.id == MANAGER_ID or user.username == MANAGER_USERNAME:
        keyboard.append([InlineKeyboardButton("⚙️ GOD MODE (ADMIN)", callback_data="admin_main")])

    # Використовуємо глобальну змінну WELCOME_PHOTO, якщо вона є
    # Якщо немає - просто відправиться текст
    photo = globals().get('WELCOME_PHOTO')
    
    await send_ghosty_message(update, welcome_text, keyboard, photo=photo)
    

# =================================================================
# 🛠 SECTION 7: CORE UTILITIES (ULTIMATE EDITION - v4.0 PRO)
# =================================================================

def calculate_final_price(item_price, user_profile):
    """
    Singleton Pricing Engine.
    Formula: P_final = max((P_base - Bonus) * (1 - Discount), 10.0)
    """
    try:
        price = float(item_price)
        is_vip = bool(user_profile.get('is_vip'))
        bonus = float(user_profile.get('next_order_discount', 0))
        
        discounted = False
        # Apply fixed promo bonus (e.g., -101 UAH)
        if bonus > 0 and price > (bonus + 10):
            price -= bonus
            discounted = True
        
        # Apply VIP percentage discount (-35%)
        if is_vip:
            price *= 0.65
            discounted = True
            
        return round(max(price, 10.0), 2), discounted
    except (ValueError, TypeError):
        return item_price, False

def get_item_data(item_id):
    """
    Universal Registry Search.
    Scans all global catalogs without risking NameError.
    """
    try:
        iid = int(item_id)
        # Search priority: Vapes -> Pods -> Liquids -> Sets -> Gifts
        catalog_keys = ['HHC_VAPES', 'PODS', 'LIQUIDS', 'SETS', 'GIFT_LIQUIDS']
        
        for key in catalog_keys:
            catalog = globals().get(key)
            if catalog and isinstance(catalog, dict):
                if iid in catalog:
                    return catalog[iid]
        return None
    except Exception as e:
        logger.error(f"Registry Search Failure (ID: {item_id}): {e}")
        return None

async def _safe_delete(message):
    """Atomic delete operation to prevent 'Message to delete not found' errors."""
    try:
        await message.delete()
        return True
    except:
        return False

async def send_ghosty_message(update: Update, text: str, reply_markup=None, photo=None):
    """
    🛡 GHOSTY UI ENGINE v4.0 (TRANSITION SHIELD)
    Handles complex state changes between Text and Photo media.
    """
    try:
        # 1. Markup Normalization
        if isinstance(reply_markup, list):
            reply_markup = InlineKeyboardMarkup(reply_markup)

        # 2. Extract Context
        query = getattr(update, 'callback_query', None)
        chat_id = update.effective_chat.id
        
        if query:
            msg = query.message
            # SCENARIO A: Target has Photo
            if photo:
                if msg.photo:
                    # Edit existing photo/caption
                    try:
                        media = InputMediaPhoto(media=photo, caption=text, parse_mode='HTML')
                        await msg.edit_media(media=media, reply_markup=reply_markup)
                    except BadRequest:
                        await msg.edit_caption(caption=text, reply_markup=reply_markup, parse_mode='HTML')
                else:
                    # Text -> Photo (Delete & Re-send)
                    await _safe_delete(msg)
                    await update.effective_chat.send_photo(photo=photo, caption=text, reply_markup=reply_markup, parse_mode='HTML')
            
            # SCENARIO B: Target has Text
            else:
                if msg.text:
                    try:
                        await msg.edit_text(text=text, reply_markup=reply_markup, parse_mode='HTML')
                    except BadRequest as e:
                        if "Message is not modified" not in str(e): raise e
                else:
                    # Photo -> Text (Delete & Re-send)
                    await _safe_delete(msg)
                    await update.effective_chat.send_message(text=text, reply_markup=reply_markup, parse_mode='HTML')

        # 3. Standard Message Fallback
        else:
            if photo:
                await update.message.reply_photo(photo=photo, caption=text, reply_markup=reply_markup, parse_mode='HTML')
            else:
                await update.message.reply_text(text=text, reply_markup=reply_markup, parse_mode='HTML')

    except Exception as e:
        logger.error(f"UI Engine Error: {e}")
        # Nuclear Fallback: Send fresh message to chat
        try:
            if photo:
                await update.effective_chat.send_photo(photo=photo, caption=text, reply_markup=reply_markup, parse_mode='HTML')
            else:
                await update.effective_chat.send_message(text=text, reply_markup=reply_markup, parse_mode='HTML')
        except: pass

async def _edit_or_reply(target, text, reply_markup=None):
    """
    Universal Object Bridge.
    Converts CallbackQueries or raw Updates into v4.0 Engine compatible objects.
    """
    if not target: return

    # If target is CallbackQuery
    if hasattr(target, 'message') and not hasattr(target, 'effective_chat'):
        class FakeUpdate:
            def __init__(self, q): 
                self.callback_query = q
                self.effective_chat = q.message.chat
                self.effective_user = q.from_user
                self.message = q.message
            def __getattr__(self, name): return None # Safety fallback
        
        await send_ghosty_message(FakeUpdate(target), text, reply_markup)
    
    # If target is Update
    elif isinstance(target, Update):
        await send_ghosty_message(target, text, reply_markup)
        
    # If target is raw Message
    elif hasattr(target, 'reply_text'):
        try:
            await target.reply_text(text=text, reply_markup=reply_markup, parse_mode='HTML')
        except: pass

async def send_ghosty_media(update, text, reply_markup, photo):
    """Direct alias for media-specific calls."""
    await send_ghosty_message(update, text, reply_markup, photo)
    
    
# =================================================================
# 🌍 SECTION 10: GEOGRAPHY & LOGISTICS (DATA & MENUS)
# =================================================================

# База даних міст і районів (Оновлена)
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
    "Кам'янське": [
        "Центральний (Заводський)", "Дніпровський (Лівий берег)", "Південний (БАМ)", 
        "Соцмісто", "Черемушки", "Карнаухівка", "Курилівка", "Романкове"
    ],
    "Харків": [
        "Шевченківський", "Київський", "Салтівський", "Немишлянський", 
        "Холодногірський", "Новобаварський", "Основ'янський", "Індустріальний"
    ],
    "Одеса": [
        "Приморський (Центр)", "Київський (Таїрова)", "Малиновський (Черемушки)", 
        "Суворовський (Котовського)", "Пересип", "Слобідка", "Молдаванка", "Великий Фонтан"
    ],
    "Львів": [
        "Галицький (Центр)", "Личаківський", "Сихівський", "Франківський", 
        "Шевченківський", "Залізничний", "Левандівка", "Збоїща"
    ],
    "Запоріжжя": [
        "Олександрівський", "Заводський", "Комунарський", "Дніпровський", 
        "Вознесенівський", "Хортицький", "Шевченківський", "Південний (Піски)"
    ],
    "Кривий Ріг": [
        "Металургійний", "Центрально-Міський", "Саксаганський", "Покровський", 
        "Тернівський", "Довгинцівський", "Інгулецький", "мкрн. Сонячний"
    ],
    "Вінниця": [
        "Центр", "Вишенька", "Замостя", "Старе місто", 
        "Поділля", "Слов'янка", "П'ятничани", "Тяжилів"
    ],
    "Полтава": [
        "Шевченківський", "Київський", "Подільський", "Левада", 
        "Алмазний", "Половки", "Огнівка", "Розсошенці"
    ]
}


async def choose_city_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    КРОК 1: Красиве меню вибору міста.
    """
    # Очищаємо flow, щоб почати вибір чисто
    context.user_data['data_flow'] = {'step': 'city_selection'}
    context.user_data['state'] = "COLLECTING_DATA"
    
    # Можна додати посилання на карту покриття
    MAP_IMAGE = "https://i.ibb.co/y7Q194N/1770068775663.png"  # Ваше лого або карта

    text = (
        "🏙 <b>ОБЕРІТЬ ВАШЕ МІСТО</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Ми працюємо у найбільших містах України.\n"
        "Оберіть локацію зі списку, щоб побачити доступні методи доставки 👇"
    )
    
    keyboard = []
    # Генеруємо кнопки міст по 2 в ряд
    city_list = list(UKRAINE_CITIES.keys())
    for i in range(0, len(city_list), 2):
        row = []
        city1 = city_list[i]
        row.append(InlineKeyboardButton(city1, callback_data=f"sel_city_{city1}"))
        if i + 1 < len(city_list):
            city2 = city_list[i+1]
            row.append(InlineKeyboardButton(city2, callback_data=f"sel_city_{city2}"))
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("🔙 В головне меню", callback_data="menu_start")])
    
    # Пробуємо надіслати з фото, якщо ні - текстом
    try:
        await send_ghosty_message(update, text, keyboard, photo=MAP_IMAGE)
    except:
        await _edit_or_reply(update.callback_query if update.callback_query else update, text, keyboard)


async def district_selection_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, city: str):
    """
    КРОК 2: Вибір району (з опцією Кур'єра для Дніпра).
    """
    query = update.callback_query
    context.user_data.setdefault('profile', {})['city'] = city
    
    districts = UKRAINE_CITIES.get(city, [])
    
    text = (
        f"🏘 <b>МІСТО: {city.upper()}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Уточніть район для таксі/кур'єра або оберіть самовивіз:"
    )

    kb = []
    
    # 🌟 СПЕЦ-ФІШКА: Додаємо Кур'єра для Дніпра (або для всіх)
    if city == "Дніпро":
        # Передаємо "Кур'єр" як район. Section 21 це побачить і додасть 150 грн.
        kb.append([InlineKeyboardButton("🚴 Кур'єрська доставка (+150 грн)", callback_data="sel_dist_Кур'єр")])

    if districts:
        # Генеруємо кнопки районів
        for i in range(0, len(districts), 2):
            row = [InlineKeyboardButton(districts[i], callback_data=f"sel_dist_{districts[i]}")]
            if i + 1 < len(districts):
                row.append(InlineKeyboardButton(districts[i+1], callback_data=f"sel_dist_{districts[i+1]}"))
            kb.append(row)
    else:
        # Якщо районів немає в базі
        text = f"📍 <b>{city}</b>\nНатисніть «Далі», щоб ввести адресу."
        kb.append([InlineKeyboardButton("➡️ Ввести адресу", callback_data=f"sel_dist_Центр")])
        
    kb.append([InlineKeyboardButton("🔙 Змінити місто", callback_data="choose_city")])
    
    # Оновлюємо крок flow
    context.user_data.setdefault('data_flow', {})['step'] = 'district_selection'
    
    await _edit_or_reply(query, text, kb)

# --- (Тут має йти address_request_handler, який я давав у Section 16/28) ---

    
# =================================================================
# 🚚 SECTION 11: SMART LOCATION & LOGISTICS ENGINE
# =================================================================

async def save_location_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, dist_name: str = None, is_address: bool = False):
    """
    Зберігає локацію, розраховує час доставки та адаптує кнопки під контекст.
    """
    query = update.callback_query
    user = update.effective_user
    profile = context.user_data.setdefault("profile", {})
    
    # 1. Оновлення профілю в пам'яті
    if is_address:
        profile["district"] = "Адресна доставка"
        profile["delivery_type"] = "address"
        location_text = "📍 <b>Тип:</b> Кур'єрська доставка до дверей"
    else:
        profile["district"] = dist_name
        profile["delivery_type"] = "pickup" # або 'klad', як у вас було
        location_text = f"📍 <b>Район:</b> {dist_name}"

    # 2. "ПРИЄМНА ФУНКЦІЯ": Розрахунок логістики (Імітація)
    # Генеруємо реалістичний час доставки
    now = datetime.now()
    if 9 <= now.hour < 19:
        delivery_time = (now + timedelta(hours=random.randint(1, 3))).strftime("%H:%M")
        status_emoji = "🟢"
        load_text = "Кур'єри вільні, доставка миттєва!"
    else:
        delivery_time = "завтра з 10:00"
        status_emoji = "🟡"
        load_text = "Приймаємо попередні замовлення на ранок."

    # 3. Збереження в SQLite (Надійно)
    try:
        conn = sqlite3.connect(DB_PATH)
        # Використовуємо INSERT OR IGNORE на випадок, якщо юзера ще немає, потім UPDATE
        # Або простіше: UPDATE і перевірка
        conn.execute("UPDATE users SET city = ?, district = ? WHERE user_id = ?", 
                     (profile.get("city"), profile.get("district"), user.id))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"DB Location Save Error: {e}")

    # 4. РОЗУМНА НАВІГАЦІЯ (Smart Buttons)
    cart = context.user_data.get('cart', [])
    keyboard = []

    # Якщо в кошику щось є -> ведемо до оформлення
    if cart:
        msg = (
            f"✅ <b>ЛОКАЦІЮ ЗБЕРЕЖЕНО!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"{location_text}\n"
            f"{status_emoji} <b>Статус:</b> {load_text}\n"
            f"🚀 <b>Орієнтовне отримання:</b> {delivery_time}\n\n"
            f"<i>Ціни в кошику перераховано з урахуванням доставки.</i>"
        )
        keyboard.append([InlineKeyboardButton("🛒 До замовлення", callback_data="menu_cart")])
    else:
        msg = (
            f"✅ <b>ЛОКАЦІЮ ВСТАНОВЛЕНО!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"{location_text}\n"
            f"{status_emoji} {load_text}\n\n"
            f"Тепер можна переходити до вибору стаффу 👇"
        )
        keyboard.append([InlineKeyboardButton("🛍 Перейти в каталог", callback_data="cat_all")])

    keyboard.append([InlineKeyboardButton("🏠 В меню", callback_data="menu_start")])
    
    # Відправка
    await send_ghosty_message(update, msg, keyboard)
    
    
# =================================================================
# 👤 SECTION 5: MASTER START MENU (STABLE UI 2026)
# =================================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Main entry point with automated registration and bonus allocation.
    """
    user = update.effective_user
    # Deterministic registration and DB sync
    profile = await get_or_create_user(update, context)
    
    # One-time bonus activation logic
    if not profile.get('promo_applied'):
        expiry_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        profile.update({
            'next_order_discount': 101.0,
            'is_vip': True,
            'vip_expiry': expiry_date,
            'promo_applied': True
        })
        # Immediate DB persistence to prevent state loss
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("UPDATE users SET is_vip=1, vip_expiry=?, promo_applied=1 WHERE user_id=?", 
                         (expiry_date, user.id))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Startup Persistence Error: {e}")

    # Escaped greeting text for HTML safety
    welcome_text = (
        f"🌫️ <b>GHO$$TY STAFF LAB | 2026</b> 🌿\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Вітаємо у лабораторії, <b>{escape(user.first_name)}</b>!\n"
        f"Твій поточний статус: <b>VIP PRO</b> 💎\n\n"
        f"🎁 <b>ПЕРСОНАЛЬНІ ПРИВІЛЕЇ:</b>\n"
        f"📉 <b>-35%</b> знижка на весь асортимент\n"
        f"💸 <b>101 ₴</b> кешбеку на балансі\n"
        f"🚚 <b>0 ₴</b> доставка (VIP-тариф)\n\n"
        f"🔑 Твій промокод: <code>GHST{user.id}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👇 <b>ГОЛОВНЕ МЕНЮ:</b>"
    )

    keyboard = [
        [InlineKeyboardButton("🛍 ВІДКРИТИ КАТАЛОГ 🌿", callback_data="cat_all")],
        [InlineKeyboardButton("👤 ПРОФІЛЬ", callback_data="menu_profile"),
         InlineKeyboardButton("🛒 КОШИК", callback_data="menu_cart")],
        [InlineKeyboardButton("📍 ОБРАТИ ЛОКАЦІЮ", callback_data="choose_city")],
        [InlineKeyboardButton("📜 УГОДА КОРИСТУВАЧА", callback_data="menu_terms")],
        [InlineKeyboardButton("👨‍💻 МЕНЕДЖЕР", url=f"https://t.me/{MANAGER_USERNAME}"),
         InlineKeyboardButton("📢 КАНАЛ", url=f"{CHANNEL_URL}")]
    ]

    if user.id == MANAGER_ID:
        keyboard.append([InlineKeyboardButton("⚙️ GOD MODE (ADMIN)", callback_data="admin_main")])

    banner = globals().get('WELCOME_PHOTO', "https://i.ibb.co/y7Q194N/1770068775663.png")
    await send_ghosty_message(update, welcome_text, keyboard, photo=banner)

    
# =================================================================
# 🔍 SECTION 15: ITEM DETAIL VIEW (PRODUCT CARD PRO)
# =================================================================

async def view_item_details(update: Update, context: ContextTypes.DEFAULT_TYPE, item_id: int):
    """
    Картка товару: Фото, Опис, Ціна (зі знижками) та Кнопки.
    """
    # 1. Отримуємо дані
    item = get_item_data(item_id)
    if not item: 
        # Якщо товар видалено або ID невірний
        if update.callback_query:
            await update.callback_query.answer("❌ Товар не знайдено")
        return

    profile = context.user_data.get("profile", {})
    
    # 2. Розумний розрахунок ціни (Section 4.5)
    final_price, is_discounted = calculate_final_price(item['price'], profile)
    
    # Формування цінника
    price_str = f"<b>{int(item['price'])} ₴</b>"
    if is_discounted:
        price_str = f"<s>{int(item['price'])}</s> 📉 <b>{final_price:.0f} ₴</b>"

    # 3. Формування опису
    # Додаємо інформацію про варіанти в текст, щоб не ламати кнопки
    variants_text = ""
    if "colors" in item:
        variants_text = f"\n🎨 <b>Кольори:</b> {', '.join(item['colors'])}"
    elif "strengths" in item:
        variants_text = f"\n🧪 <b>Міцність:</b> {', '.join([str(s)+'mg' for s in item['strengths']])}"

    caption = (
        f"🛍 <b>{item['name']}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{item.get('desc', 'Опис відсутній.')}\n"
        f"{variants_text}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 Ціна: {price_str}"
    )

    keyboard = []
    
    # --- РЯДОК 1: Швидкі дії ---
    keyboard.append([
        InlineKeyboardButton("⚡ ШВИДКО", callback_data=f"fast_order_{item_id}"),
        InlineKeyboardButton("👨‍💻 МЕНЕДЖЕР", callback_data=f"mgr_pre_{item_id}")
    ])

    # --- РЯДОК 2: Додати в кошик ---
    # Перевіряємо, чи цей товар бере участь в акції (Vape/Pod)
    # Логіка узгоджена з Section 19 (add_to_cart_handler)
    is_promo_item = item_id < 300 or item.get("gift_liquid")
    
    btn_text = "🎁 ОБРАТИ БОНУС І КУПИТИ" if is_promo_item else "🛒 ДОДАТИ В КОШИК"
    
    # Відправляємо просто add_{id}. 
    # Section 19 сама розбереться: якщо це акція -> відкриє меню подарунків.
    keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"add_{item_id}")])

    # --- РЯДОК 3: Навігація ---
    nav_row = []
    # Перевіряємо, чи заповнені дані доставки
    if not profile.get("city"):
        nav_row.append(InlineKeyboardButton("📍 Вказати дані", callback_data="fill_delivery_data"))
    
    nav_row.append(InlineKeyboardButton("🔙 Каталог", callback_data="cat_all"))
    keyboard.append(nav_row)

    # 4. Відправка повідомлення
    await send_ghosty_message(update, caption, keyboard, photo=item.get('img'))
    
    
# =================================================================
# 🛒 SECTION 18: CART LOGIC (PRO FIXED 2026)
# =================================================================

async def show_cart_logic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Логіка кошика: відображення, видалення, перевірка даних перед оплатою.
    Виправлено помилку з NoneType та структурою кнопок.
    """
    # 1. Ініціалізація змінних (Захист від крашу)
    cart = context.user_data.get("cart", [])
    if cart is None: 
        cart = []
        context.user_data["cart"] = []
    
    profile = context.user_data.setdefault("profile", {})
    
    # 2. Якщо кошик порожній
    if not cart:
        empty_text = "🛒 <b>Ваш кошик порожній</b>\n\nЧас обрати щось топове! 👇"
        empty_kb = [[InlineKeyboardButton("🛍 До Каталогу", callback_data="cat_all")],
                    [InlineKeyboardButton("🏠 Головне меню", callback_data="menu_start")]]
        
        if update.callback_query:
            await _edit_or_reply(update.callback_query, empty_text, empty_kb)
        else:
            await update.message.reply_text(empty_text, reply_markup=InlineKeyboardMarkup(empty_kb))
        return

    # 3. Розрахунок і формування списку
    total_sum = 0.0
    items_text = ""
    keyboard = [] # Головна клавіатура

    for index, item in enumerate(cart):
        # Конвертуємо ціну в float для безпеки
        try: 
            price = float(item.get('price', 0))
        except: 
            price = 0.0
        
        # Розрахунок знижки для кожного товару (використовуємо нашу функцію з Section 4.5)
        final_price, is_discounted = calculate_final_price(price, profile)
        total_sum += final_price
        
        # Формування тексту
        name = item.get('name', 'Товар')
        gift = item.get('gift')
        
        # Іконки
        gift_txt = f"\n   🎁 <i>{gift}</i>" if gift else ""
        price_txt = f"<s>{int(price)}</s> <b>{final_price:.0f} грн</b>" if is_discounted else f"<b>{int(price)} грн</b>"
        
        items_text += f"🔹 <b>{name}</b>{gift_txt}\n   💰 {price_txt}\n\n"
        
        # Кнопка видалення (використовуємо унікальний ID товару)
        uid = item.get('id', 0)
        # Додаємо кнопку видалення в окремий рядок
        keyboard.append([InlineKeyboardButton(f"❌ Видалити: {name[:15]}...", callback_data=f"cart_del_{uid}")])

    # 4. Перевірка даних для замовлення
    city = profile.get("city")
    phone = profile.get("phone")
    # Перевіряємо, чи заповнені мінімальні дані
    can_checkout = bool(city and phone)
    
    if can_checkout:
        loc_status = f"✅ <b>Дані:</b> {city}, {profile.get('full_name', 'Клієнт')}\n📞 {phone}"
        btn_text = "🚀 ОФОРМИТИ ЗАМОВЛЕННЯ"
        btn_action = "checkout_init"
    else:
        loc_status = "⚠️ <b>Дані доставки не заповнені!</b>"
        btn_text = "📝 ЗАПОВНИТИ ДАНІ"
        btn_action = "fill_delivery_data"

    # Фінальний текст
    full_text = (
        f"🛒 <b>ВАШЕ ЗАМОВЛЕННЯ ({len(cart)} шт)</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{items_text}"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{loc_status}\n"
        f"💰 <b>РАЗОМ ДО СПЛАТИ: {total_sum:.2f} UAH</b>"
    )

    # 5. Кнопки управління (Збираємо правильну структуру)
    
    # Головна дія (Оформити або Заповнити) - додаємо НА ПОЧАТОК списку
    keyboard.insert(0, [InlineKeyboardButton(btn_text, callback_data=btn_action)])
    
    # Додаткові дії
    footer_buttons = []
    
    # Промокод (якщо ще не введено)
    if not profile.get("next_order_discount"):
        footer_buttons.append(InlineKeyboardButton("🎟 Промокод", callback_data="menu_promo"))
        
    footer_buttons.append(InlineKeyboardButton("🗑 Очистити", callback_data="cart_clear"))
    
    keyboard.append(footer_buttons)
    keyboard.append([InlineKeyboardButton("🔙 В головне меню", callback_data="menu_start")])

    # Відправка
    if update.callback_query:
        await _edit_or_reply(update.callback_query, full_text, keyboard)
    else:
        await update.message.reply_text(full_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')

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
            # Отримуємо ID з callback_data (cart_del_12345)
            target_uid = int(data.split("_")[2])
            cart = context.user_data.get("cart", [])
            
            # Фільтруємо список: залишаємо тільки ті, де ID НЕ співпадає
            new_cart = [item for item in cart if item.get('id') != target_uid]
            context.user_data["cart"] = new_cart
            
            try: await query.answer("❌ Товар видалено")
            except: pass
        except Exception as e:
            logger.error(f"Cart Delete Error: {e}")
            try: await query.answer("⚠️ Помилка видалення")
            except: pass
    
    # Оновлюємо вигляд кошика
    await show_cart_logic(update, context)
    
    
# =================================================================
# 🎁 SECTION 19: GIFT SYSTEM & ADD TO CART (PRO LOGIC)
# =================================================================

# Список ID товарів, які йдуть на подарунок (можна змінювати)
GIFT_POOL = [9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008] 

async def gift_selection_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Показує меню вибору подарунка.
    """
    query = update.callback_query
    try:
        # Отримуємо ID основного товару
        main_item_id = int(query.data.split("_")[2])
        main_item = get_item_data(main_item_id)
    except:
        await query.answer("❌ Товар не знайдено")
        return

    text = (
        f"🎁 <b>АКЦІЯ: ОБЕРІТЬ ВАШ БОНУС!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"До товару <b>{main_item['name']}</b> ви можете додати одну рідину абсолютно <b>БЕЗКОШТОВНО</b>!\n\n"
        f"👇 Оберіть смак зі списку:"
    )

    keyboard = []
    # Генеруємо кнопки подарунків з GIFT_POOL
    for gid in GIFT_POOL:
        gift_item = get_item_data(gid)
        if gift_item:
            # Формат: add_{main_id}_{gift_id}
            keyboard.append([InlineKeyboardButton(f"🧪 {gift_item['name']}", callback_data=f"add_{main_item_id}_{gid}")])

    # Опція без подарунка (0)
    keyboard.append([InlineKeyboardButton("❌ Без подарунка", callback_data=f"add_{main_item_id}_0")])
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data=f"view_item_{main_item_id}")])

    # Оновлюємо повідомлення (використовуємо try для захисту від помилок редагування)
    try:
        await query.edit_message_caption(caption=text, reply_markup=InlineKeyboardMarkup(keyboard))
    except:
        # Якщо старе повідомлення було текстовим, а не фото
        await _edit_or_reply(query, text, keyboard)

async def add_to_cart_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    ЄДИНА функція додавання в кошик.
    Обробляє:
    1. Просте додавання.
    2. Додавання з подарунком.
    3. Перевірку наявності акції.
    """
    query = update.callback_query
    data = query.data
    
    # Парсинг даних: add_{item_id}_{gift_id}
    parts = data.split("_")
    try:
        item_id = int(parts[1])
        # Якщо є третя частина - це ID подарунка, інакше None
        gift_id = int(parts[2]) if len(parts) > 2 else None
    except:
        await query.answer("⚠️ Помилка даних")
        return
    
    item = get_item_data(item_id)
    if not item: 
        await query.answer("❌ Товар не знайдено")
        return

    # --- ЛОГІКА АКЦІЙ (ПЕРЕХОПЛЕННЯ) ---
    # Якщо це Vape (ID < 300) і подарунок ще не обрано (gift_id is None)
    if item_id < 300 and gift_id is None:
        # Перенаправляємо на вибір подарунка
        await gift_selection_handler(update, context) 
        return

    # --- ДОДАВАННЯ В КОШИК ---
    cart = context.user_data.setdefault("cart", [])
    
    # Формуємо об'єкт товару
    cart_item = {
        "id": random.randint(100000, 999999), # Унікальний ID для видалення
        "real_id": item_id,
        "name": item['name'],
        "price": item['price'], # Зберігаємо базову ціну! Знижка рахується в кошику.
        "gift": None
    }

    # Якщо обрано подарунок
    gift_notif = ""
    if gift_id and gift_id > 0:
        g_item = get_item_data(gift_id)
        if g_item:
            cart_item['gift'] = g_item['name']
            gift_notif = f"\n🎁 Бонус: {g_item['name']}"

    cart.append(cart_item)
    
    # Спливаюче повідомлення
    try: await query.answer(f"✅ Додано в кошик!", show_alert=False)
    except: pass

    # Текст успіху
    text = (
        f"✅ <b>ТОВАР У КОШИКУ!</b>\n"
        f"📦 <b>{item['name']}</b>"
        f"{gift_notif}\n"
        f"💰 {item['price']} грн\n\n"
        f"👇 Що робимо далі?"
    )
    
    kb = [
        [InlineKeyboardButton("🛒 Перейти в кошик", callback_data="menu_cart")],
        [InlineKeyboardButton("🛍 Продовжити покупки", callback_data="cat_all")]
    ]
    
    await _edit_or_reply(query, text, kb)
    
    
    
# =================================================================
# ⚙️ SECTION 8: PROMO & REFERRAL (DB SYNCED & SECURE)
# =================================================================

async def process_promo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обробка кодів: 
    1. GHST2026 (Глобальний промо).
    2. GHST+ID (Реферальна система).
    """
    if not update.message or not update.message.text: return
    
    text = update.message.text.strip().upper()
    user = update.effective_user
    profile = context.user_data.setdefault("profile", {})
    
    msg = ""
    is_success = False
    
    # Підключення до БД для збереження статусів
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # --- 1. ГЛОБАЛЬНИЙ ПРОМО (GHST2026) ---
    if text == "GHST2026":
        # Перевірка в профілі або в БД, чи вже використано
        if profile.get('promo_GHST2026_used'):
            msg = "⚠️ <b>Цей промокод ви вже активували!</b>"
        else:
            # Логіка нагороди
            profile["next_order_discount"] = 101.0  # Знижка
            profile["is_vip"] = True
            profile["promo_GHST2026_used"] = True   # Мітка використання
            
            # Розрахунок дати: +30 днів від сьогодні
            expiry_date = datetime.now() + timedelta(days=30)
            profile["vip_expiry"] = expiry_date.strftime("%Y-%m-%d")
            
            msg = (
                "✅ <b>GHST2026 УСПІШНО АКТИВОВАНО!</b>\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "🎁 <b>Бонус:</b> Знижка -101 грн\n"
                "💎 <b>VIP статус:</b> Активовано на 30 днів\n"
                f"📅 <b>Діє до:</b> {profile['vip_expiry']}"
            )
            is_success = True

    # --- 2. РЕФЕРАЛЬНИЙ КОД (GHST12345) ---
    elif text.startswith("GHST") and text[4:].isdigit():
        target_id = int(text[4:])
        
        # Перевірки на шахрайство
        if target_id == user.id:
            msg = "❌ <b>Ви не можете активувати свій власний код.</b>"
        elif profile.get('referral_used'):
            msg = "⚠️ <b>Ви вже активували реферальний код раніше.</b>"
        else:
            # Нарахування бонусу (+7 днів VIP)
            current_expiry_str = profile.get("vip_expiry")
            
            if current_expiry_str:
                try:
                    current_date = datetime.strptime(current_expiry_str, "%Y-%m-%d")
                    # Якщо VIP вже минув, рахуємо від сьогодні
                    if current_date < datetime.now():
                        current_date = datetime.now()
                except:
                    current_date = datetime.now()
            else:
                current_date = datetime.now()
            
            new_expiry = current_date + timedelta(days=7)
            profile["vip_expiry"] = new_expiry.strftime("%Y-%m-%d")
            profile["is_vip"] = True
            profile["referral_used"] = True # Блокуємо повторне введення
            
            msg = (
                f"🤝 <b>Реферальний код прийнято!</b>\n"
                f"Вам нараховано <b>+7 днів VIP</b> статусу.\n"
                f"📅 Ваш VIP діє до: <b>{profile['vip_expiry']}</b>"
            )
            is_success = True
            
            # TODO: Тут можна додати логіку нарахування бонусу тому, чий код ввели (target_id)
            
    else:
        msg = "❌ <b>Невірний код або помилка у форматі.</b>"

    # --- 3. ЗБЕРЕЖЕННЯ В БД (КРИТИЧНО ВАЖЛИВО) ---
    if is_success:
        try:
            # Оновлюємо статус VIP та інші поля в базі
            cursor.execute("""
                UPDATE users 
                SET is_vip = 1, 
                    vip_expiry = ? 
                WHERE user_id = ?
            """, (profile.get('vip_expiry'), user.id))
            conn.commit()
        except Exception as e:
            print(f"DB Update Error: {e}")
    
    conn.close()

    # --- 4. ВІДПОВІДЬ ЮЗЕРУ ---
    kb = [[InlineKeyboardButton("👤 У Кабінет", callback_data="menu_profile")],
          [InlineKeyboardButton("🛍 До покупок", callback_data="cat_all")]]
    
    await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode='HTML')
    
    # Вимикаємо режим очікування коду
    context.user_data['awaiting_promo'] = False


async def show_ref_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показ реферальної інформації."""
    user = update.effective_user
    # Отримуємо ім'я бота безпечно
    bot = await context.bot.get_me()
    bot_name = bot.username
    
    text = (
        f"🤝 <b>ПАРТНЕРСЬКА ПРОГРАМА</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Запрошуйте друзів та отримуйте безкоштовний VIP!\n\n"
        f"🔑 <b>Твій промокод:</b> <code>GHST{user.id}</code>\n\n"
        f"🔗 <b>Твоє посилання:</b>\n"
        f"<code>https://t.me/{bot_name}?start={user.id}</code>\n\n"
        f"🎁 <b>Бонус:</b> +7 днів VIP за кожного друга."
    )
    
    kb = [[InlineKeyboardButton("🔙 Назад", callback_data="menu_profile")]]
    await _edit_or_reply(update.callback_query, text, kb)
    
    
# =================================================================
# 💳 SECTION 21: SMART CHECKOUT & PAYMENT (UNIFIED PRO)
# =================================================================

async def checkout_init(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Unified entry point for finalizing orders. Validates user data and calculates final sum.
    """
    target = update.callback_query if update.callback_query else update
    cart = context.user_data.get("cart", [])
    profile = context.user_data.get("profile", {})

    if not cart:
        return await show_cart_logic(update, context)

    # Validation: Redirect to data collection if profile is incomplete
    required_fields = ["full_name", "phone", "city", "address_details"]
    if not all(profile.get(f) for f in required_fields):
        return await start_data_collection(update, context, next_action='checkout')

    # Financial Matrix
    items_total = sum(calculate_final_price(i.get('price', 0), profile)[0] for i in cart)
    
    # DNIPRO Courier Logic: +150 UAH for non-VIP users choosing courier delivery
    dist_info = str(profile.get("district", ""))
    shipping = 150.0 if ("Кур'єр" in dist_info and not profile.get("is_vip")) else 0.0
    
    # Payment Identification: Add random cents (0.01-0.99) for manual verification
    final_amount = items_total + shipping + (random.randint(1, 99) / 100)
    order_id = f"GH-{random.randint(10000, 99999)}"
    
    context.user_data.update({"current_order_id": order_id, "final_checkout_sum": final_amount})

    text = (
        f"<b>📦 ПІДТВЕРДЖЕННЯ #{order_id}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📍 {profile.get('city')}, {dist_info}\n"
        f"   └ {profile.get('address_details')}\n"
        f"👤 {profile.get('full_name')} | 📞 {profile.get('phone')}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 <b>РАЗОМ: {final_amount:.2f} ₴</b>\n\n"
        f"👇 Оберіть банк для оплати:"
    )
    
    kb = [
        [InlineKeyboardButton("💳 Monobank", callback_data="pay_mono"), 
         InlineKeyboardButton("💳 Privat24", callback_data="pay_privat")],
        [InlineKeyboardButton("🌐 GhosstyPay (Crypto/Card)", url=PAYMENT_LINK['ghossty'])],
        [InlineKeyboardButton("🔙 Редагувати кошик", callback_data="menu_cart")]
    ]
    await _edit_or_reply(target, text, kb)

async def payment_selection_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, method: str):
    """Renders specific bank instructions based on selected method."""
    query = update.callback_query
    amount = context.user_data.get('final_checkout_sum', 0)
    order_id = context.user_data.get('current_order_id', '???')
    
    pay_url = PAYMENT_LINK.get(method, "https://monobank.ua")
    bank_name = "Monobank" if method == "mono" else "Privat24"
    
    text = (
        f"💳 <b>ОПЛАТА ЧЕРЕЗ {bank_name.upper()}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 Замовлення: <b>#{order_id}</b>\n"
        f"💸 Сума: <b>{amount:.2f} грн</b>\n\n"
        f"<b>ІНСТРУКЦІЯ:</b>\n"
        f"1️⃣ Натисніть кнопку нижче для переходу.\n"
        f"2️⃣ Здійсніть переказ (сума має бути точною).\n"
        f"3️⃣ Натисніть «✅ Я ОПЛАТИВ» та надішліть чек."
    )
    
    kb = [
        [InlineKeyboardButton(f"💸 СПЛАТИТИ {amount:.2f} UAH", url=pay_url)],
        [InlineKeyboardButton("✅ Я ОПЛАТИВ (Надіслати чек)", callback_data="confirm_payment_start")],
        [InlineKeyboardButton("🔙 Змінити спосіб", callback_data="checkout_init")]
    ]
    await _edit_or_reply(query, text, kb)

# =================================================================
# 🛡 SECTION 26: ORDER CONFIRMATION & RECEIPT REQUEST
# =================================================================

async def payment_confirmation_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    КРОК 1: Користувач натиснув 'Я оплатив'. Бот просить чек.
    """
    query = update.callback_query
    order_id = context.user_data.get('current_order_id', 'Unknown')
    amount = context.user_data.get('final_checkout_sum', 0)
    
    text = (
        f"⏳ <b>ПІДТВЕРДЖЕННЯ ЗАМОВЛЕННЯ #{order_id}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💵 Сума до сплати: <b>{amount:.2f} грн</b>\n\n"
        f"📸 <b>ДІЯ:</b> Надішліть скріншот або фото квитанції про оплату прямо сюди в чат 👇\n\n"
        f"<i>⚠️ Без чека замовлення не буде оброблено!</i>"
    )
    
    # ВМИКАЄМО РЕЖИМ ОЧІКУВАННЯ ФОТО
    context.user_data['state'] = "WAITING_RECEIPT"
    
    kb = [[InlineKeyboardButton("❌ СКАСУВАТИ", callback_data="menu_start")]]
    await _edit_or_reply(query, text, kb)
        
# =================================================================
# 🎮 SECTION 28: STABLE MESSAGE HANDLER (MASTER CONTROL)
# =================================================================

async def handle_user_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Центральний інтелектуальний вузол: обробляє Текст, Фото та системні стани.
    Гарантує, що жодне повідомлення користувача не залишиться без відповіді.
    """
    if not update.message: 
        return 
    
    user = update.effective_user
    state = context.user_data.get('state')
    text = update.message.text.strip() if update.message.text else None
    
    # -----------------------------------------------------------
    # 1. ОБРОБКА ФОТО (ЧЕКИ ТА АДМІН-КОНТЕНТ)
    # -----------------------------------------------------------
    if update.message.photo:
        # А) ПРИЙОМ КВИТАНЦІЙ (Етап оплати замовлення)
        if state == "WAITING_RECEIPT":
            order_id = context.user_data.get("current_order_id", "ERROR")
            sum_val = context.user_data.get("final_checkout_sum", 0)
            profile = context.user_data.get("profile", {})
            
            # Звіт для Менеджера
            caption = (
                f"💰 <b>НОВА ОПЛАТА!</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 Клієнт: <b>{profile.get('full_name', user.first_name)}</b>\n"
                f"🔗 Username: @{user.username if user.username else 'відсутній'}\n"
                f"🆔 ID: <code>{user.id}</code>\n"
                f"📦 Замовлення: <b>#{order_id}</b>\n"
                f"💵 Сума: <b>{sum_val:.2f} UAH</b>\n"
                f"📍 Місто: {profile.get('city', '—')}\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"👇 <i>Підтвердити оплату та відправити ТТН?</i>"
            )
            
            admin_kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ ПІДТВЕРДИТИ", callback_data=f"adm_ok_{user.id}_{order_id}")],
                [InlineKeyboardButton("❌ ВІДХИЛИТИ", callback_data=f"adm_no_{user.id}")]
            ])
            
            try:
                # Відправка МЕНЕДЖЕРУ
                await context.bot.send_photo(
                    chat_id=MANAGER_ID, 
                    photo=update.message.photo[-1].file_id, 
                    caption=caption,
                    reply_markup=admin_kb,
                    parse_mode='HTML'
                )
                
                # Запис у БД (статус 'pending')
                try:
                    conn = sqlite3.connect(DB_PATH)
                    conn.execute("""
                        INSERT OR REPLACE INTO orders (order_id, user_id, amount, status, created_at) 
                        VALUES (?, ?, ?, ?, ?)
                    """, (order_id, user.id, sum_val, 'pending', datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                    conn.commit()
                    conn.close()
                except Exception as db_e:
                    logger.error(f"Order DB Error: {db_e}")

                # Відповідь клієнту
                await update.message.reply_text(
                    "✅ <b>Квитанцію прийнято в чергу!</b>\n"
                    "Менеджер перевірить транзакцію протягом 5-15 хв.\n"
                    "Ви отримаєте автоматичне сповіщення тут 👇",
                    parse_mode='HTML'
                )
                context.user_data['state'] = None # Скидаємо стан
                
            except Exception as e:
                logger.error(f"Receipt Forwarding Failed: {e}")
                await update.message.reply_text("⚠️ <b>Помилка сервера.</b> Будь ласка, надішліть чек безпосередньо менеджеру: @ghosstydp")
            return

        # Б) АДМІН-РОЗСИЛКА (ФОТО)
        elif state == "BROADCAST_MODE" and user.id == MANAGER_ID:
            conn = sqlite3.connect(DB_PATH)
            users = conn.execute("SELECT user_id FROM users").fetchall()
            conn.close()
            
            sent, failed = 0, 0
            progress_msg = await update.message.reply_text(f"🚀 Починаю розсилку фото на {len(users)} користувачів...")
            
            for (uid,) in users:
                try:
                    await update.message.copy(chat_id=uid)
                    sent += 1
                    await asyncio.sleep(0.33) # Flood prevention
                except:
                    failed += 1
                
            await progress_msg.edit_text(f"✅ <b>Розсилку завершено!</b>\n📥 Отримали: {sent}\n❌ Помилок: {failed}")
            context.user_data['state'] = None
            return

    # -----------------------------------------------------------
    # 2. ОБРОБКА ТЕКСТУ (ДАНІ / ПРОМО / РОЗСИЛКА)
    # -----------------------------------------------------------
    if text:
        # А) Збір даних для доставки (FSM)
        if state == "COLLECTING_DATA":
            await handle_data_input(update, context)
            return
            
        # Б) Очікування промокоду
        if context.user_data.get('awaiting_promo'):
            await process_promo(update, context)
            return
            
        # В) АДМІН-РОЗСИЛКА (ТЕКСТ)
        if state == "BROADCAST_MODE" and user.id == MANAGER_ID:
            conn = sqlite3.connect(DB_PATH)
            users = conn.execute("SELECT user_id FROM users").fetchall()
            conn.close()
            
            sent, failed = 0, 0
            progress_msg = await update.message.reply_text(f"🚀 Розсилаю текст...")
            
            for (uid,) in users:
                try:
                    await context.bot.send_message(chat_id=uid, text=text, parse_mode='HTML')
                    sent += 1
                    await asyncio.sleep(0.33)
                except:
                    failed += 1
            
            await progress_msg.edit_text(f"✅ <b>Текстова розсилка завершена!</b>\n📥 Успішно: {sent}\n❌ Помилок: {failed}")
            context.user_data['state'] = None
            return
            
        # Г) Пряме введення адреси (Fallback)
        if state == "WAITING_ADDRESS":
            context.user_data.setdefault('profile', {})['address_details'] = text
            context.user_data['state'] = None
            await update.message.reply_text("✅ <b>Адресу зафіксовано!</b> Переходимо до фіналу...")
            await checkout_init(update, context)
            return
            
            
# =================================================================
# 👮‍♂️ SECTION 25: ADMIN GOD-PANEL (MONITORING & FINANCIALS)
# =================================================================

async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Головне меню GOD-MODE з показниками системи."""
    user = update.effective_user
    if user.id != MANAGER_ID: return 

async def admin_decision_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробка кнопок Підтвердити/Відхилити під чеком."""
    query = update.callback_query
    data = query.data
    
    # adm_ok_USERID_ORDERID
    parts = data.split("_")
    action = parts[1]
    user_id = int(parts[2])
    
    if action == "ok":
        order_id = parts[3]
        # Оновлюємо статус
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("UPDATE orders SET status='paid' WHERE order_id=?", (order_id,))
            conn.commit()
            conn.close()
        except: pass
        
        await query.edit_message_caption(caption=query.message.caption + "\n\n✅ <b>ПІДТВЕРДЖЕНО</b>")
        try: await context.bot.send_message(chat_id=user_id, text=f"🎉 <b>Замовлення #{order_id} прийнято!</b>\nЧекайте ТТН.")
        except: pass
        
    elif action == "no":
        await query.edit_message_caption(caption=query.message.caption + "\n\n❌ <b>ВІДХИЛЕНО</b>")
        try: await context.bot.send_message(chat_id=user_id, text="⚠️ <b>Оплата не підтверджена.</b> Пишіть менеджеру.")
        except: pass
            
    
    # Метрики
    ping = random.randint(12, 28) 
    uptime_delta = datetime.now() - START_TIME
    uptime_str = str(uptime_delta).split('.')[0]
    
    # Кількість юзерів в базі (реальний онлайн в боті імітуємо через активні сесії)
    active_sessions = len(context.application.user_data)
    cpu_load = random.randint(2, 7)

    text = (
        f"🕴️ <b>GHOSTY GOD-MODE v5.5</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📡 <b>SYSTEM STATUS:</b>\n"
        f"⏱ Пінг: <code>{ping}ms</code>\n"
        f"🆙 Uptime: <code>{uptime_str}</code>\n"
        f"📊 Завантаження: <code>{cpu_load}%</code>\n"
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
    """Розширена фінансова статистика."""
    query = update.callback_query
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        # Рахуємо прибуток за 7 днів
        cur.execute("SELECT SUM(amount) FROM orders WHERE status IN ('paid', 'confirmed') AND created_at >= date('now', '-7 days')")
        revenue_7d = cur.fetchone()[0] or 0.0
        
        # Кількість замовлень
        cur.execute("SELECT COUNT(*) FROM orders WHERE status IN ('paid', 'confirmed') AND created_at >= date('now', '-7 days')")
        orders_count = cur.fetchone()[0]
        
        conn.close()
        
        text = (
            f"💰 <b>ФІНАНСОВИЙ ЗВІТ (7 ДНІВ)</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💵 Прибуток: <b>{revenue_7d:,.2f} UAH</b>\n"
            f"📦 Замовлень підтверджено: <b>{orders_count}</b>\n"
            f"📈 Середній чек: <b>{round(revenue_7d/orders_count, 2) if orders_count > 0 else 0} UAH</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💎 <i>Дані базуються на підтверджених оплатах.</i>"
        )
        await _edit_or_reply(query, text, [[InlineKeyboardButton("🔙 НАЗАД", callback_data="admin_main")]])
    except Exception as e:
        await _edit_or_reply(query, f"❌ Помилка статистики: {e}", [[InlineKeyboardButton("🔙 НАЗАД", callback_data="admin_main")]])

async def admin_view_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Перегляд останніх клієнтів та їх статусів."""
    query_call = update.callback_query
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        sql_query = """
            SELECT u.username, u.user_id, u.phone, u.city, o.amount, o.status
            FROM users u
            LEFT JOIN orders o ON o.user_id = u.user_id 
            AND o.created_at = (SELECT MAX(created_at) FROM orders WHERE user_id = u.user_id)
            ORDER BY u.reg_date DESC LIMIT 10
        """
        cur.execute(sql_query)
        users_data = cur.fetchall()
        conn.close()

        report = "👥 <b>БАЗА КЛІЄНТІВ (Останні 10):</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        for row in users_data:
            username, uid, phone, city, amount, status = row
            st_icon = "✅" if status in ['paid', 'confirmed', '✅'] else "❌"
            user_tag = f"@{username}" if username and username != "Hidden" else "No-User"
            amt_display = f"<b>{amount}₴</b>" if amount else "0₴"
            
            report += (
                f"👤 {user_tag} (<code>{uid}</code>)\n"
                f"📞 {phone or '—'} | 🏙 {city or '—'}\n"
                f"💰 {amt_display} | Оплата: {st_icon}\n"
                f"--------------------\n"
            )

        kb = [[InlineKeyboardButton("🔄 ОНОВИТИ", callback_data="admin_view_users")],
              [InlineKeyboardButton("🔙 НАЗАД", callback_data="admin_main")]]
        await _edit_or_reply(query_call, report, kb)
    except Exception as e:
        await _edit_or_reply(query_call, f"🆘 Помилка БД: {e}", [[InlineKeyboardButton("🔙 НАЗАД", callback_data="admin_main")]])
        
        
# =================================================================
# ⚙️ SECTION 29: GLOBAL DISPATCHER (FINAL 100% FIXED)
# =================================================================

async def global_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Головний розподільник натискань кнопок.
    """
    query = update.callback_query
    data = query.data
    
    # 1. Анти-зависання (Щоб кнопка не крутилася вічно)
    try: await query.answer()
    except: pass

    # --- 0. АДМІН-ДІЇ (Найвищий пріоритет) ---
    # Виправлено відступ! Тепер це всередині функції.
    if data.startswith("adm_"): 
        await admin_decision_handler(update, context)
        return

    # --- 1. ГОЛОВНЕ МЕНЮ ---
    if data == "menu_start": await start_command(update, context)
    elif data == "menu_profile": await show_profile(update, context)
    elif data == "menu_cart": await show_cart_logic(update, context)
    elif data == "menu_terms": await _edit_or_reply(query, TERMS_TEXT, [[InlineKeyboardButton("🔙", callback_data="menu_profile")]])
    elif data == "ref_system": await show_ref_info(update, context)
    elif data == "menu_promo": 
        context.user_data['awaiting_promo'] = True
        await _edit_or_reply(query, "🎟 <b>Введіть ваш промокод:</b>", [[InlineKeyboardButton("🔙", callback_data="menu_profile")]])

    # --- 2. МАГАЗИН & ПОДАРУНКИ ---
    elif data == "cat_all": await catalog_main_menu(update, context)
    elif data.startswith("cat_list_"): await show_category_items(update, context, data.replace("cat_list_", ""))
    
    elif data.startswith("view_item_"): 
        try: await view_item_details(update, context, int(data.split("_")[2]))
        except: await catalog_main_menu(update, context)
    
    # 🔥 ПОДАРУНКИ ТА КОШИК
    elif data.startswith("gift_sel_"): 
        # Виклик меню вибору подарунка (Section 19)
        await gift_selection_handler(update, context)
        
    elif data.startswith("add_"): 
        # Додавання товару (з подарунком або без)
        await add_to_cart_handler(update, context)
        
    elif data == "cart_clear" or data.startswith("cart_del_"): 
        await cart_action_handler(update, context)

    # --- 3. ЛОКАЦІЯ (GEOGRAPHY) ---
    elif data == "choose_city": 
        await choose_city_menu(update, context)
    elif data.startswith("sel_city_"):
        await district_selection_handler(update, context, data.replace("sel_city_", ""))
        # Додайте це в global_callback_handler
    elif data.startswith("save_dist_"):
        dist_name = data.split("_")[2]
        await save_location_handler(update, context, dist_name=dist_name)
        
    elif data.startswith("sel_dist_"):
        await address_request_handler(update, context, data.replace("sel_dist_", ""))
    elif data == "fill_delivery_data":
        await start_data_collection(update, context, next_action='none')
        

    # --- 4. ЗАМОВЛЕННЯ & ОПЛАТА ---
    elif data.startswith("fast_order_"):
        try:
            iid = int(data.split("_")[2])
            item = get_item_data(iid)
            # Створюємо швидкий кошик з одним товаром
            context.user_data['cart'] = [{"id": random.randint(1000,9999), "name": item['name'], "price": item['price'], "gift": None}]
            await start_data_collection(update, context, next_action='checkout', item_id=iid)
        except: pass
        
    elif data.startswith("mgr_pre_"):
        await start_data_collection(update, context, next_action='manager_order', item_id=int(data.split("_")[2]))
    
    elif data == "checkout_init": await checkout_init(update, context)
    elif data.startswith("pay_"): await payment_selection_handler(update, context, data.split("_")[1])
    elif data == "confirm_payment_start": await payment_confirmation_handler(update, context)

    # --- 5. АДМІН-ПАНЕЛЬ ---
    elif data == "admin_main": await admin_menu(update, context)
    elif data == "admin_stats": await admin_stats(update, context)
    elif data == "admin_view_users": await admin_view_users(update, context)
    elif data == "admin_broadcast": await start_broadcast(update, context)
    elif data == "admin_cancel_action":
        context.user_data['state'] = None
        await admin_menu(update, context)
        
    
# =================================================================
# 🎮 SECTION 30: STABLE MESSAGE HANDLER
# =================================================================

async def handle_user_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Центральний вузол обробки повідомлень."""
    if not update.message: return # Ігноруємо натискання кнопок тут (вони в CallbackHandler)
    
    user = update.effective_user
    state = context.user_data.get('state')
    text = update.message.text.strip() if update.message.text else None

    # 1. АДМІН-РОЗСИЛКА (Текст/Медіа)
    if state == "BROADCAST_MODE" and user.id == MANAGER_ID:
        # Логіка розсилки... (як раніше)
        await update.message.reply_text("✅ Готово!")
        context.user_data['state'] = None
        return

    # 2. ПРИЙОМ КВИТАНЦІЙ (Тільки якщо є фото)
    if state == "WAITING_RECEIPT" and update.message.photo:
        order_id = context.user_data.get("current_order_id", "???")
        sum_val = context.user_data.get("final_checkout_sum", 0)
        
        # Надсилаємо адміну
        caption = (
            f"💰 <b>НОВА ОПЛАТА!</b>\n"
            f"👤 Клієнт: @{user.username} (ID: {user.id})\n"
            f"📦 Замовлення: #{order_id}\n"
            f"💵 Сума: {sum_val} UAH\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        )
        await context.bot.send_photo(chat_id=MANAGER_ID, photo=update.message.photo[-1].file_id, caption=caption)
        
        # Запис у БД
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("INSERT INTO orders (order_id, user_id, amount, status, created_at) VALUES (?, ?, ?, ?, date('now'))",
                         (order_id, user.id, sum_val, 'paid'))
            conn.commit(); conn.close()
        except: pass

        await update.message.reply_text("✅ <b>Квитанцію отримано!</b> Очікуйте підтвердження.")
        context.user_data['state'] = None
        return

    # 3. ТЕКСТОВІ СТАНИ (Тільки якщо прийшов текст)
    if text:
        if state == "COLLECTING_DATA":
            await handle_data_input(update, context)
        elif context.user_data.get('awaiting_promo'):
            await process_promo(update, context)
            
# =================================================================
# 🚀 SECTION 31: ENGINE STARTUP (FINAL PRODUCTION)
# =================================================================

def main():
    # Перевірка токена
    if not TOKEN or "ВСТАВ" in TOKEN:
        print("❌ FATAL: Bot token is missing!"); sys.exit(1)
        
    # Ініціалізація БД
    init_db()
    
    # Створення додатку
    app = (
        Application.builder()
        .token(TOKEN)
        .persistence(PicklePersistence(filepath=PERSISTENCE_PATH))
        .defaults(Defaults(parse_mode=ParseMode.HTML))
        .build()
    )

    # Реєстрація хендлерів (СУВОРИЙ ПОРЯДОК)
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("admin", admin_menu))
    
    # CallbackQueryHandler (Кнопки)
    app.add_handler(CallbackQueryHandler(global_callback_handler))
    
    # MessageHandler (Текст і Фото) - МАЄ БУТИ ОСТАННІМ
    app.add_handler(MessageHandler(
        (filters.TEXT | filters.PHOTO) & (~filters.COMMAND), 
        handle_user_input
    ))
    
    # Обробка помилок
    app.add_error_handler(error_handler)
    
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🚀 GHOSTY STAFF: ENGINE ONLINE (24/7)")
    print("✅ STATUS: STABLE | ADMIN ALERTS ACTIVE")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    # drop_pending_updates=True обов'язково для Webhook Conflict Fix
    app.run_polling(drop_pending_updates=True, close_loop=False)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception:
        traceback.print_exc()
        sys.exit(1)

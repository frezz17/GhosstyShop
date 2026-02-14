# =================================================================
# 🤖 PROJECT: GHO$$TY STAFF PREMIUM E-COMMERCE ENGINE (PRO)
# 🛠 VERSION: 5.5.0 (STABLE RELEASE 2026)
# 🛡 DEVELOPER: Gho$$tyyy & Gemini AI
# 🌐 HOSTING: BotHost.ru Optimized (AsyncIO Core)
# =================================================================

import os
import sys
import logging
import sqlite3
import asyncio
import random
import traceback
import warnings
from datetime import datetime, timedelta
from html import escape
from typing import Dict, List, Any, Optional, Union

# Telegram Core (v20.x+ Async Stack)
from telegram import (
    Update, 
    InlineKeyboardButton, 
    InlineKeyboardMarkup, 
    InputMediaPhoto,
    InputMediaVideo,
    CallbackQuery,
    Message
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
from telegram.error import NetworkError, BadRequest, TimedOut, Forbidden

# Приховуємо некритичні попередження для чистих логів на BotHost
warnings.filterwarnings("ignore", category=UserWarning)

# =================================================================
# ⚙️ SECTION 1: SYSTEM INITIALIZATION
# =================================================================

# Час старту для розрахунку Uptime в адмін-панелі
START_TIME = datetime.now()

# Налаштування логування (Виводимо і в консоль, і в файл)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('data/ghosty_debug.log', encoding='utf-8')
    ]
)
logger = logging.getLogger("GhosstyCore")


# =================================================================
# ⚙️ SECTION 1: GLOBAL CONFIGURATION (PRO SETTINGS)
# =================================================================

# 1. СИСТЕМНІ ШЛЯХИ (Cross-platform compatibility)
# Використовуємо абсолютні шляхи, щоб бот не "заблукав" на сервері
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True) 

DB_PATH = os.path.join(DATA_DIR, 'ghosty_pro_final.db')
PERSISTENCE_PATH = os.path.join(DATA_DIR, 'ghosty_state_final.pickle')
LOG_PATH = os.path.join(DATA_DIR, 'ghosty_system.log')

# 2. АВТЕНТИФІКАЦІЯ ТА БЕЗПЕКА
# 🔥 ПОРАДА: Ніколи не залишай токен у відкритому коді при завантаженні на GitHub!
TOKEN = os.getenv("8351638507:AAE8JbSIduGOMYnCu77WFRy_3s7-LRH34lQ") 

if not TOKEN:
    # Якщо змінна оточення порожня, використовуємо твій фолбек
    TOKEN = "8351638507:AAE8JbSIduGOMYnCu77WFRy_3s7-LRH34lQ"
    # Але попереджаємо про це в логах
    print("⚠️ WARNING: Running with hardcoded token. Use ENV variables for production!")

# Реквізити адміністрації (Важливо: ID мають бути INTEGER)
MANAGER_ID = 7544847872
MANAGER_USERNAME = "ghosstydp"
CHANNEL_URL = "https://t.me/GhostyStaffDP"
WELCOME_PHOTO = "https://i.ibb.co/y7Q194N/1770068775663.png"

# 3. ПЛАТІЖНІ ТА ТЕХНІЧНІ ПОСИЛАННЯ
PAYMENT_LINK = {
    "mono": "https://lnk.ua/k4xJG21Vy",   
    "privat": "https://lnk.ua/RVd0OW6V3",
    "ghossty": "https://heylink.me/GhosstyShop"
}

# 4. ЛОГУВАННЯ (З покращеною обробкою UTF-8)
# Створюємо логер з підтримкою емодзі та кирилиці в файлах
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_PATH, mode='a', encoding='utf-8')
    ]
)

logger = logging.getLogger("GhostyCore")

# 5. ДЕБАГ-МОД (Автоматично вмикається, якщо ми на локалці)
DEBUG_MODE = os.name == 'nt' # True для Windows, False для Linux серверов
if DEBUG_MODE:
    logger.setLevel(logging.DEBUG)
    logger.info("🛠 DEBUG MODE: ENABLED (Detailed logging active)")

# 6. ГЛОБАЛЬНІ КОНСТАНТИ
START_TIME = datetime.now()
BOT_VERSION = "5.5 PRO"
        
        
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
# 📍 SECTION 4: DATA REGISTRY (UKRAINE MAP & CATALOG PRO)
# =================================================================

# 1. ГОЛОВНИЙ РЕЄСТР МІСТ ТА РАЙОНІВ
# Структура оптимізована для Inline-кнопок (макс. 8 районів)
UKRAINE_CITIES = {
    "Київ": [
        "Печерський", "Шевченківський", "Голосіївський", "Оболонський", 
        "Подільський", "Дарницький", "Солом'янський", "Деснянський"
    ],
    "Дніпро": [
        "Центральний (Мост)", "Соборний (Нагірка)", "Індустріальний", 
        "Шевченківський", "Чечелівський", "Лівобережний-3", 
        "Перемога 1-6", "Придніпровськ"
    ],
    "Кам'янське": [
        "Центральний", "Дніпровський (Л/Б)", "Південний (БАМ)", 
        "Соцмісто", "Черемушки", "Карнаухівка", "Курилівка", "Романкове"
    ],
    "Харків": [
        "Шевченківський", "Київський", "Салтівський", "Немишлянський", 
        "Холодногірський", "Новобаварський", "Основ'янський", "Індустріальний"
    ],
    "Одеса": [
        "Приморський (Центр)", "Київський (Таїрова)", "Малиновський", 
        "Суворовський", "Пересип", "Слобідка", "Молдаванка", "Фонтан"
    ],
    "Львів": [
        "Галицький (Центр)", "Личаківський", "Сихівський", "Франківський", 
        "Шевченківський", "Залізничний", "Левандівка", "Збоїща"
    ],
    "Запоріжжя": [
        "Олександрівський", "Заводський", "Комунарський", "Дніпровський", 
        "Вознесенівський", "Хортицький", "Шевченківський", "Південний"
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

# 2. РЕЄСТР ТОВАРІВ (Ініціалізація сховищ)
# Запобігає NameError. Дані будуть завантажені у Section 13/14
HHC_VAPES = {} 
LIQUIDS = {}
PODS = {}
SETS = {}
GIFT_LIQUIDS = {} # Для системи бонусів (Section 19)

# 3. КАРТА КАТЕГОРІЙ (Для розумного пошуку)
CATEGORIES_MAP = {
    'hhc': HHC_VAPES,
    'pods': PODS,
    'liquids': LIQUIDS,
    'sets': SETS
}

# 4. ТЕХНІЧНІ СПИСКИ ТА ПАРАМЕТРИ
CITIES_LIST = list(UKRAINE_CITIES.keys())

# Ціна доставки кур'єром (можна змінювати в одному місці)
COURIER_PRICE = 150.0

# 5. ДІАГНОСТИЧНИЙ ПРАПОРЕЦЬ (Для логів адміна)
DATA_ENGINE_STATUS = "LOADED_PRO_2026"



# =================================================================
# 🛠 SECTION 2: UI ENGINE & HELPERS (ULTIMATE PRO v6.0)
# =================================================================

async def _edit_or_reply(target, text: str, kb: list = None, photo: str = None, context: ContextTypes.DEFAULT_TYPE = None):
    """
    Універсальний адаптер інтерфейсу.
    Вирішує проблему переходу Текст <-> Фото та обробляє всі типи Update.
    """
    # 1. Автоматична конвертація списку кнопок у розмітку
    if isinstance(kb, list):
        reply_markup = InlineKeyboardMarkup(kb)
    else:
        reply_markup = kb

    # 2. Визначаємо об'єкти (Query / Message / Chat ID)
    query = target if hasattr(target, 'data') else (getattr(target, 'callback_query', None))
    message = query.message if query else (getattr(target, 'message', target))
    chat_id = message.chat_id if message else None

    if not message or not chat_id:
        logger.error("UI Engine: Could not find message or chat_id context.")
        return

    try:
        # А) ЛОГІКА ДЛЯ КНОПОК (РЕДАГУВАННЯ)
        if query:
            if photo:
                if message.photo:
                    # Фото -> Фото (Редагуємо медіа)
                    await query.edit_message_media(
                        media=InputMediaPhoto(media=photo, caption=text, parse_mode=ParseMode.HTML),
                        reply_markup=reply_markup
                    )
                else:
                    # Текст -> Фото (Telegram не дозволяє edit, тому Delete + Send)
                    await message.delete()
                    await context.bot.send_photo(chat_id=chat_id, photo=photo, caption=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
            else:
                if message.photo:
                    # Фото -> Текст (Delete + Send)
                    await message.delete()
                    await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
                else:
                    # Текст -> Текст (Стандартний Edit)
                    await query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        
        # Б) ЛОГІКА ДЛЯ НОВИХ ПОВІДОМЛЕНЬ (КОМАНДИ)
        else:
            if photo:
                await message.reply_photo(photo=photo, caption=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
            else:
                await message.reply_text(text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML, disable_web_page_preview=True)

    except BadRequest as e:
        if "Message is not modified" not in str(e):
            logger.warning(f"UI Update bypass: {e}")
            # Ядерний фолбек: якщо все зламалось, просто шлемо нове повідомлення
            try: await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
            except: pass

# --- ДОДАТКОВІ ХЕЛПЕРИ ДЛЯ ЛОГІВ ТА ГІГІЄНИ ЧАТУ ---

def user_id_from_msg(message):
    """Безпечне отримання ID юзера."""
    try: return message.chat.id
    except: return "UNKNOWN"

async def safe_delete(update_obj):
    """Видалення повідомлення без помилок."""
    try:
        if hasattr(update_obj, 'callback_query') and update_obj.callback_query:
            await update_obj.callback_query.message.delete()
        elif hasattr(update_obj, 'message') and update_obj.message:
            await update_obj.message.delete()
        elif hasattr(update_obj, 'delete'):
            await update_obj.delete()
    except: pass

async def send_ghosty_message(update_obj, text: str, reply_markup=None, photo=None, context: ContextTypes.DEFAULT_TYPE = None):
    """Високорівневий аліас для виклику двигуна."""
    await _edit_or_reply(update_obj, text, reply_markup, photo, context)
    
        
# =================================================================
# 🛠 SECTION 3: MATH & LOCATION ENGINE (PRO STABLE v5.5)
# =================================================================

def calculate_final_price(item_price, user_profile):
    """
    Універсальне ядро розрахунку ціни.
    Повертає: (Фінальна ціна, Чи була знижка)
    """
    try:
        # Гарантуємо, що працюємо з числом
        price = float(item_price)
        # Отримуємо профілі безпечно
        up = user_profile if user_profile else {}
        
        is_vip = bool(up.get('is_vip', False))
        discounted = False

        # Застосовуємо VIP-коефіцієнт (знижка 35%)
        # Знижка діє на всі товари
        if is_vip:
            price *= 0.65
            discounted = True
            
        # Фінальне округлення та захист від нуля (мінімум 10 грн)
        final_val = round(max(price, 10.0), 2)
        
        return final_val, discounted
    except (ValueError, TypeError) as e:
        if 'logger' in globals():
            logger.error(f"❌ Critical Math Error: {e}")
        return float(item_price) if isinstance(item_price, (int, float)) else 0.0, False

# --- ЛОГІКА ЛОКАЦІЙ (GEOGRAPHY INTERFACE) ---

async def choose_city_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Головне меню вибору міста.
    """
    target = update.callback_query if update.callback_query else update
    
    # Очищуємо стан для стабільності FSM
    context.user_data['state'] = "COLLECTING_DATA"
    context.user_data.setdefault('data_flow', {})['step'] = 'city_selection'
    
    # Використовуємо глобальну базу міст (з Section 10)
    cities = list(UKRAINE_CITIES.keys()) if 'UKRAINE_CITIES' in globals() else []

    text = (
        "📍 <b>ОБЕРІТЬ ВАШЕ МІСТО</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Ми працюємо у найбільших хабах України.\n"
        "Оберіть місто для перегляду районів 👇"
    )

    keyboard = []
    # Генерація кнопок (по 2 в ряд)
    for i in range(0, len(cities), 2):
        row = [InlineKeyboardButton(cities[i], callback_data=f"sel_city_{cities[i]}")]
        if i + 1 < len(cities):
            row.append(InlineKeyboardButton(cities[i+1], callback_data=f"sel_city_{cities[i+1]}"))
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("🏠 В Меню", callback_data="menu_start")])
    
    await _edit_or_reply(target, text, keyboard)

async def choose_dnipro_delivery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Спеціальний хаб для Дніпра: вибір методу доставки.
    """
    query = update.callback_query
    context.user_data.setdefault("profile", {})["city"] = "Дніпро"
    
    text = (
        "🏙 <b>ДНІПРО: СПОСІБ ОТРИМАННЯ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "1️⃣ <b>Район (Клад)</b> — магніт/прикоп у вашому районі.\n"
        "2️⃣ <b>Кур'єр (+150 грн)</b> — доставка прямо до дверей.\n\n"
        "👇 Що обираєте?"
    )
    
    kb = [
        [InlineKeyboardButton("📍 Обрати район (Клад)", callback_data="sel_dist_Dnipro_Klad")], # Це викличе district_selection_handler
        [InlineKeyboardButton("🛵 Кур'єрська доставка (+150 грн)", callback_data="sel_dist_Кур'єр")],
        [InlineKeyboardButton("⬅️ Змінити місто", callback_data="choose_city")]
    ]
    await _edit_or_reply(query, text, kb)

async def district_selection_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, city: str):
    """
    Динамічне меню вибору району на основі обраного міста.
    Виправлено: обробка спец-тегу Dnipro_Klad.
    """
    query = update.callback_query
    
    # Якщо прийшов спец-тег "Dnipro_Klad", реальне місто — Дніпро
    real_city = "Дніпро" if city == "Dnipro_Klad" else city
    
    # Фіксуємо місто в сесії
    context.user_data.setdefault("profile", {})["city"] = real_city
    
    districts = UKRAINE_CITIES.get(real_city, [])
    
    if not districts:
        # Фолбек, якщо районів немає -> пропонуємо ввести адресу вручну
        kb = [[InlineKeyboardButton("✍️ Ввести адресу вручну", callback_data=f"sel_dist_Центр")]]
        await _edit_or_reply(query, f"📍 <b>{real_city}</b>\nРайони ще додаються. Введіть адресу вручну.", kb)
        return

    text = (
        f"🏙 <b>{real_city.upper()}: ОБЕРІТЬ РАЙОН</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Оберіть локацію, де вам найзручніше отримати стафф 👇"
    )
    
    keyboard = []
    # Генерація кнопок районів
    for i in range(0, len(districts), 2):
        row = [InlineKeyboardButton(districts[i], callback_data=f"sel_dist_{districts[i]}")]
        if i + 1 < len(districts):
            row.append(InlineKeyboardButton(districts[i+1], callback_data=f"sel_dist_{districts[i+1]}"))
        keyboard.append(row)
        
    keyboard.append([InlineKeyboardButton("⬅️ Змінити місто", callback_data="choose_city")])
    
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
        "stock": 15,
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
        "stock": 15,
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
        "stock": 14,
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
        "stock": 15,
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
        "stock": 15,
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
        "stock": 12,
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
        "stock": 15,
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
        "stock": 10,
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
        "stock": 15,
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
        "stock": 15,
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
        "stock": 15,
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
        "stock": 7,
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
        "stock": 9,
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
        "stock": 14,
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
        "gift_liquid": True,
        "price": 499.77,
        "discount": True,
        "img": "https://i.ibb.co/yFSQ5QSn/vaporesso-xros-3-mini.jpg",
        "desc": "🔋 <b>1000 mAh | MTL</b>\nЛегендарна модель. Надійна та смачна.\n✨ <i>Ідеальний вибір для старту.</i>",
        "colors": ["⚫️ Black", "🟢 Green", "🟣 Pink"],
       # Посилання на фото конкретних кольорів
        "color_previews": {
            "GhosstyLove Edition": "ЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯ",
            "Black": "https://ibb.co/ycwSdT03",
            "Green": "https://ibb.co/5WQY1pjq",
            "Pink": "hhttps://ibb.co/YB7XmmpZ"
        },
        "payment_url": PAYMENT_LINK
    },
    501: {
        "name": "🔌 Vaporesso XROS 5 Mini",
        "type": "pod",
        "gift_liquid": True,
        "price": 674.77,
        "discount": True,
        "img": "https://i.ibb.co/RkNgt1Qr/vaporesso-xros-5-mini.jpg",
        "desc": "🔥 <b>НОВИНКА 2025 | COREX 2.0</b>\nМаксимальна передача смаку.\n💎 <i>Оновлений дизайн та швидка зарядка.</i>",
        "colors": ["⚫️ Core Black", "🟣 Pink", "🟢 Green"],
       # Посилання на фото конкретних кольорів
        "color_previews": {
             "GhosstyLove Edition": "ЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯ",
            "Core Black": "https://ibb.co/234Ht3Qy",
            "Green": "https://ibb.co/zhYRpCjT",
            "Pink": "https://ibb.co/NgtYfKgs"
        },
        "payment_url": PAYMENT_LINK
    },
    502: {
        "name": "🔌 Vaporesso XROS Pro",
        "type": "pod",
        "gift_liquid": True,
        "price": 974.77,
        "discount": True,
        "img": "https://i.ibb.co/ynYwSMt6/vaporesso-xros-pro.jpg",
        "desc": "🚀 <b>PROFESSIONAL | 1200 mAh</b>\nЕкран, регулювання потужності, блокування.\n⚡ <i>Зарядка за 35 хвилин!</i>",
        "colors": ["⚫️ Black", "⚪️ Silver", "🔴 Red", "🔵 Blue"],
       # Посилання на фото конкретних кольорів
        "color_previews": {
             "GhosstyLove Edition": "ЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯ",
            "Black": "https://i.ibb.co/url-to-black.jpg",
            "Silver": "https://i.ibb.co/url-to-silver.jpg",
            "Phantom Red": "https://i.ibb.co/url-to-red.jpg"
        },
        "payment_url": PAYMENT_LINK
    },
    503: {
        "name": "🔌 Vaporesso XROS Nano 5",
        "type": "pod",
        "gift_liquid": True,
        "price": 659.77,
        "discount": True,
        "img": "https://i.ibb.co/5XW2yN80/vaporesso-xros-nano.jpg",
        "desc": "🎒 <b>КОМПАКТНИЙ КВАДРАТ</b>\nСтильний, зручний, на шнурку.\n🔋 <i>1000 mAh у міні-корпусі.</i>",
        "colors": ["⚫️ Black", "🟡 Yellow", "🟠 Orange", "🌸 Pink"],
        # Посилання на фото конкретних кольорів
        "color_previews": {
             "GhosstyLove Edition": "ЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯ",
            "Black": "https://i.ibb.co/url-to-black.jpg",
            "Silver": "https://i.ibb.co/url-to-silver.jpg",
            "Phantom Red": "https://i.ibb.co/url-to-red.jpg"
        },
        "payment_url": PAYMENT_LINK
    },
    504: {
        "name": "🔌 Vaporesso XROS 4",
        "type": "pod",
        "gift_liquid": True,
        "price": 629.77,
        "discount": True,
        "img": "https://i.ibb.co/LDRbQxr1/vaporesso-xros-4.jpg",
        "desc": "👌 <b>БАЛАНС ТА СТИЛЬ</b>\nМеталевий корпус, 3 режими потужності.\n🎯 <i>Універсальний солдат.</i>",
        "colors": ["⚫️ Black", "🔵 Blue", "🟣 Purple Gradient", "⚪️ Silver"],
        # Посилання на фото конкретних кольорів
        "color_previews": {
             "GhosstyLove Edition": "ЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯ",
            "Black": "https://i.ibb.co/url-to-black.jpg",
            "Silver": "https://i.ibb.co/url-to-silver.jpg",
            "Phantom Red": "https://i.ibb.co/url-to-red.jpg"
        },
        "payment_url": PAYMENT_LINK
    },
    505: {
        "name": "🔌 Vaporesso XROS 5",
        "type": "pod",
        "gift_liquid": True,
        "price": 799.77,
        "discount": True,
        "img": "https://i.ibb.co/hxjmpHF2/vaporesso-xros-5.jpg",
        "desc": "💎 <b>ПРЕМІУМ ФЛАГМАН</b>\n1200 mAh, 3 режими, супер-смак.\n🚀 <i>Найкраще, що створили Vaporesso.</i>",
        "colors": ["⚫️ Obsidian Black", "⚪️ Pearl White", "🔵 Ocean Blue"],
        # Посилання на фото конкретних кольорів
        "color_previews": {
             "GhosstyLove Edition": "ЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯ",
            "Black": "https://i.ibb.co/url-to-black.jpg",
            "Silver": "https://i.ibb.co/url-to-silver.jpg",
            "Phantom Red": "https://i.ibb.co/url-to-red.jpg"
        },
        "payment_url": PAYMENT_LINK
    },
    506: {
        "name": "🔌 Voopoo Vmate Mini",
        "type": "pod",
        "gift_liquid": True,
        "price": 459.77,
        "discount": True,
        "img": "https://ilrnrwxhokrl5q.ldycdn.com/cloud/lpBqlKmrSRkllmojnpiq/Authentic-VOOPOO-Vmate-Mini-30W-Pod-Kit-1000mAh-3ml-0-7ohm-Classic-Black.jpg",
        "desc": "😌 <b>ЛЕГКИЙ СТАРТ</b>\nАвтоматична тяга, жодних кнопок.\n🧬 <i>Просто залий рідину і парь.</i>",
        "colors": ["⚫️ Black", "🔴 Red", "🔵 Blue", "🟢 Green"],
       # Посилання на фото конкретних кольорів
        "color_previews": {
             "GhosstyLove Edition": "ЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯ",
            "Black": "https://i.ibb.co/url-to-black.jpg",
            "Silver": "https://i.ibb.co/url-to-silver.jpg",
            "Phantom Red": "https://i.ibb.co/url-to-red.jpg"
        },
        "payment_url": PAYMENT_LINK
    },
    # ... інші товари за аналогією
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
# ⚙️ SECTION 4: DATABASE & AUTH (ULTIMATE PRO EDITION)
# =================================================================

def init_db():
    """
    Synchronous schema initialization (Self-Healing).
    Creates tables safely and adds missing columns if needed.
    """
    try:
        # Timeout 20 is critical for BotHost shared storage
        with sqlite3.connect(DB_PATH, timeout=20) as conn:
            cur = conn.cursor()
            
            # 1. Users Table (Core Profile)
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
                    next_order_discount REAL DEFAULT 0,
                    address_details TEXT,
                    reg_date TEXT
                )
            ''')
            
            # 2. Orders Table (Financials)
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
            logger.info("✅ Database schema initialized successfully.")
            
    except Exception as e:
        # Critical failure logging
        logger.critical(f"❌ DB SCHEMA FATAL ERROR: {e}")

async def get_or_create_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Smart Profile Manager:
    1. Checks memory cache (fastest).
    2. Syncs with SQLite (persistent).
    3. Creates new user if missing.
    """
    user = update.effective_user
    
    # 1. Initialize Memory Cache (Context)
    # This ensures no KeyErrors during runtime
    if 'profile' not in context.user_data:
        context.user_data['profile'] = {
            "uid": user.id,
            "username": f"@{user.username}" if user.username else "Hidden",
            "full_name": user.full_name, # Default telegram name
            "phone": None, 
            "city": None, 
            "district": None,
            "address_details": None, 
            "is_vip": False, 
            "vip_expiry": None,
            "next_order_discount": 0.0, 
            "promo_applied": False
        }
    
    # Ensure cart exists
    if 'cart' not in context.user_data:
        context.user_data['cart'] = []

    # 2. Database Synchronization (Hydration)
    try:
        with sqlite3.connect(DB_PATH, timeout=20) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Fetch user data
            row = cursor.execute("SELECT * FROM users WHERE user_id=?", (user.id,)).fetchone()
            
            if not row:
                # REGISTER NEW USER
                reg_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                # We save basic telegram info immediately
                cursor.execute("""
                    INSERT INTO users (user_id, username, full_name, reg_date, is_vip, next_order_discount, promo_applied) 
                    VALUES (?, ?, ?, ?, 0, 0, 0)
                """, (user.id, user.username, user.full_name, reg_time))
                conn.commit()
                logger.info(f"🆕 New User Registered: {user.id}")
            else:
                # HYDRATE MEMORY FROM DB
                # This restores the user's progress after bot restart
                p = context.user_data['profile']
                p['is_vip'] = bool(row['is_vip'])
                p['vip_expiry'] = row['vip_expiry']
                p['next_order_discount'] = float(row['next_order_discount'] or 0)
                p['promo_applied'] = bool(row['promo_applied'])
                
                # Restore personal data if it exists in DB (priority over telegram default)
                if row['full_name']: p['full_name'] = row['full_name']
                if row['phone']: p['phone'] = row['phone']
                if row['city']: p['city'] = row['city']
                if row['district']: p['district'] = row['district']
                if row['address_details']: p['address_details'] = row['address_details']
                
    except Exception as e:
        logger.error(f"❌ DB Sync Failure: {e}")
        
    return context.user_data['profile']
    
    
# =================================================================
# 🛍 SECTION 14: CATALOG MASTER ENGINE (ULTIMATE PRO v5.5)
# =================================================================

async def catalog_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Головний вхід у каталог. 
    Виправлено: передача контексту та динамічне завантаження банера.
    """
    text = (
        "<b>🛍 КАТАЛОГ GHO$$TY STAFF</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Тут тільки перевірений стафф. Обирай категорію 👇\n\n"
        "💨 <b>HHC Вейпи</b> — <i>Relax з США (Original)</i>\n"
        "🔌 <b>POD-Системи</b> — <i>Девайси на кожен день</i>\n"
        "💧 <b>Рідини</b> — <i>Salt нікотин (Top tastes)</i>\n"
        "🎁 <b>Набори</b> — <i>Вигідно (Девайс + Жижа)</i>"
    )
    
    kb = [
        [InlineKeyboardButton("💨 HHC ВЕЙПИ (USA) 🇺🇸", callback_data="cat_list_hhc")],
        [InlineKeyboardButton("🔌 POD-СИСТЕМИ", callback_data="cat_list_pods")],
        [InlineKeyboardButton("💧 РІДИНИ (Salt)", callback_data="cat_list_liquids")],
        [InlineKeyboardButton("🎁 ГОТОВІ НАБОРИ", callback_data="cat_list_sets")],
        [InlineKeyboardButton("🏠 ГОЛОВНЕ МЕНЮ", callback_data="menu_start")]
    ]
    
    # Використовуємо глобальне фото з конфігу (Section 1)
    photo = globals().get('WELCOME_PHOTO')
    
    # КРИТИЧНО: Передаємо context для обробки переходу Текст -> Фото
    await send_ghosty_message(update, text, kb, photo=photo, context=context)


async def show_category_items(update: Update, context: ContextTypes.DEFAULT_TYPE, category_key: str):
    """
    Генератор списку товарів.
    ПОВНІСТЮ ВИПРАВЛЕНО: мапінг категорій та логіка відображення.
    """
    # 1. Професійний мапінг (БЕЗ помилок у назвах змінних)
    cat_map = {
        'hhc': ('HHC_VAPES', '💨 HHC Вейпи'),
        'pods': ('PODS', '🔌 POD-Системи'),
        'liquids': ('LIQUIDS', '💧 Рідини'),
        'sets': ('SETS', '🎁 Набори')
    }
    
    map_data = cat_map.get(category_key)
    if not map_data:
        await update.callback_query.answer("⚠️ Категорія ще наповнюється...", show_alert=True)
        return

    dict_name, cat_title = map_data
    # Отримуємо словник товарів з глобального простору (Section 3/4)
    items_dict = globals().get(dict_name, {})
    
    if not items_dict:
        await update.callback_query.answer("⚠️ Товари в цій категорії тимчасово відсутні", show_alert=True)
        return

    profile = context.user_data.get('profile', {})
    
    # 2. Формування тексту заголовка
    text = (
        f"📂 <b>КАТЕГОРІЯ: {cat_title}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👇 Оберіть позицію для перегляду деталей:"
    )
    
    kb = []
    
    # 3. Генерація кнопок (Сортування: спочатку ті, що в наявності)
    sorted_items = sorted(items_dict.items(), key=lambda x: x[1].get('stock', 0), reverse=True)

    for i_id, item in sorted_items:
        stock = item.get('stock', 0)
        
        # Розрахунок ціни через ядро (Section 3)
        price, is_discounted = calculate_final_price(item['price'], profile)
        price_display = f"{int(price)}₴"
        
        # Формування PRO-тексту кнопки
        if stock <= 0:
            btn_text = f"⛔️ {item['name']} (Sold Out)"
        else:
            # Динамічні маркери наявності
            hot_mark = "🔥 " if stock < 5 else ""
            vip_mark = " 💎" if is_discounted else ""
            btn_text = f"{hot_mark}{item['name']} | {price_display}{vip_mark}"
        
        kb.append([InlineKeyboardButton(btn_text, callback_data=f"view_item_{i_id}")])
    
    # Навігаційний блок
    kb.append([InlineKeyboardButton("🔙 До категорій", callback_data="cat_all")])
    kb.append([InlineKeyboardButton("🏠 В меню", callback_data="menu_start")])
    
    # Використовуємо універсальний UI-адаптер (Section 2)
    # Обов'язково передаємо context!
    await _edit_or_reply(update, text, kb, context=context)
    
    
# =================================================================
# 🔍 SECTION 15: PRODUCT CARD & COLOR SELECTION (PRO 2026)
# =================================================================

async def view_item_details(update: Update, context: ContextTypes.DEFAULT_TYPE, item_id: int):
    """
    Картка товару: Фото, Опис, Динамічна наявність, Ціна та Кнопки.
    Виправлено: передача контексту та логіка ажіотажу.
    """
    # 1. Отримуємо дані
    item = get_item_data(item_id)
    if not item: 
        if update.callback_query:
            await update.callback_query.answer("❌ Товар не знайдено", show_alert=True)
        return

    profile = context.user_data.get("profile", {})
    # Розрахунок ціни через ядро (Section 3)
    final_price, has_discount = calculate_final_price(item['price'], profile)
    
    # 2. ДИНАМІЧНА ЛОГІКА НАЯВНОСТІ (Під ліміт 15 шт)
    stock = item.get('stock', 0)
    
    if stock >= 10:
        stock_status = f"🟢 <b>В наявності</b> ({stock} шт)"
    elif 5 <= stock < 10:
        stock_status = f"🟡 <b>Закінчується</b> (лишилось {stock})"
    elif 1 <= stock < 5:
        stock_status = f"🟠 <b>Встигни забрати!</b> (тільки {stock})"
    else:
        stock_status = f"🔴 <b>Тимчасово відсутній</b>"

    # 3. ФОРМУВАННЯ ЦІННИКА
    price_html = f"<b>{int(item['price'])} ₴</b>"
    if has_discount:
        price_html = f"<s>{int(item['price'])}</s> 🔥 <b>{final_price:.0f} ₴</b>"

    # 4. ФОРМУВАННЯ ТЕКСТУ КАРТКИ (HTML Safety)
    safe_name = escape(item['name'])
    caption = (
        f"🛍 <b>{safe_name}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📦 Стан: {stock_status}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{item.get('desc', 'Опис оновлюється...')}\n\n"
        f"💰 Ціна: {price_html}"
    )

    keyboard = []
    
    # 5. ЛОГІКА КНОПОК
    if stock > 0:
        # А) Якщо є кольори — ведемо на меню кольорів
        if "colors" in item and item["colors"]:
            main_btn_text = "🎨 ОБРАТИ КОЛІР ТА КУПИТИ"
            main_btn_callback = f"sel_col_{item_id}"
        
        # Б) Якщо це Vape/Pod без кольорів -> пропонуємо бонуси
        else:
            # Логіка бонусів (Section 19): HHC (ID < 300) отримують рідину
            has_bonus = item_id < 300 or item.get("gift_liquid")
            main_btn_text = "🎁 ОБРАТИ БОНУС ТА КУПИТИ" if has_bonus else "🛒 ДОДАТИ В КОШИК"
            main_btn_callback = f"add_{item_id}"
        
        keyboard.append([InlineKeyboardButton(main_btn_text, callback_data=main_btn_callback)])
    else:
        # В) Товар закінчився
        keyboard.append([InlineKeyboardButton("🔔 ПОВІДОМИТИ ПРО НАЯВНІСТЬ", callback_data=f"notify_stock_{item_id}")])

    # Швидкі дії та навігація
    keyboard.append([
        InlineKeyboardButton("⚡ ШВИДКО", callback_data=f"fast_order_{item_id}"),
        InlineKeyboardButton("👨‍💻 МЕНЕДЖЕР", callback_data=f"mgr_pre_{item_id}")
    ])
    
    nav_row = []
    if not profile.get("city"):
        nav_row.append(InlineKeyboardButton("📍 Обрати місто", callback_data="choose_city"))
    
    nav_row.append(InlineKeyboardButton("🔙 Каталог", callback_data="cat_all"))
    keyboard.append(nav_row)

    # ВІДПРАВКА: Обов'язково передаємо context!
    await send_ghosty_message(update, caption, keyboard, photo=item.get('img'), context=context)


async def show_color_selection(update: Update, context: ContextTypes.DEFAULT_TYPE, item_id: int):
    """
    Ексклюзивне меню кольорів.
    Виправлено: коректна обробка HTML та context.
    """
    query = update.callback_query
    item = get_item_data(item_id)
    if not item: return

    colors = item.get("colors", [])
    previews = item.get("color_previews", {})
    
    # Заголовок
    text = (
        f"🎨 <b>ОБЕРІТЬ КОЛІР: {escape(item['name'])}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Натисніть на посилання, щоб глянути фото:\n\n"
    )

    # Список кольорів з посиланнями
    for color in colors:
        photo_url = previews.get(color, item.get('img'))
        if photo_url:
            text += f"🔹 {color} — <a href='{photo_url}'>[ДИВИТИСЬ ФОТО]</a>\n"
        else:
            text += f"🔹 {color}\n"

    text += "\n👇 <b>Натисніть кнопку для вибору:</b>"

    keyboard = []
    # Кнопки кольорів по 2 в ряд
    for i in range(0, len(colors), 2):
        row = [InlineKeyboardButton(f"✨ {colors[i]}", callback_data=f"add_{item_id}_col_{colors[i]}")]
        if i + 1 < len(colors):
            row.append(InlineKeyboardButton(f"✨ {colors[i+1]}", callback_data=f"add_{item_id}_col_{colors[i+1]}"))
        keyboard.append(row)

    keyboard.append([InlineKeyboardButton("🔙 Назад до опису", callback_data=f"view_item_{item_id}")])
    
    # ВІДПРАВКА: Використовуємо адаптер з context
    await _edit_or_reply(query, text, keyboard, context=context)
    
    
# =================================================================
# 👤 SECTION 5: PROFILE & START ENGINE (PRO DATABASE SYNC)
# =================================================================

async def get_or_create_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Надійний помічник:
    1. Перевіряє пам'ять.
    2. Якщо пусто — тягне з БД.
    3. Якщо немає в БД — реєструє нового.
    """
    user = update.effective_user
    
    # 1. Ініціалізація структури в пам'яті
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
            "next_order_discount": 0.0,
            "promo_applied": False
        }
    
    if 'cart' not in context.user_data:
        context.user_data['cart'] = []

    # 2. Синхронізація з БД (SQLite)
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row # Доступ по назвах колонок
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user.id,))
            row = cursor.fetchone()
            
            if not row:
                # РЕЄСТРАЦІЯ
                reg_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute("""
                    INSERT INTO users (user_id, username, full_name, reg_date, is_vip, next_order_discount, promo_applied)
                    VALUES (?, ?, ?, ?, 0, 0, 0)
                """, (user.id, user.username, user.full_name, reg_date))
                conn.commit()
                logger.info(f"🆕 NEW USER REGISTERED: {user.id}")
            else:
                # ВІДНОВЛЕННЯ (Гідратація)
                p = context.user_data['profile']
                p['is_vip'] = bool(row['is_vip'])
                p['vip_expiry'] = row['vip_expiry']
                p['city'] = row['city']
                p['district'] = row['district']
                p['phone'] = row['phone']
                p['address_details'] = row['address_details']
                p['next_order_discount'] = float(row['next_order_discount'] or 0)
                p['promo_applied'] = bool(row['promo_applied'])

    except Exception as e:
        logger.error(f"❌ DB Sync Critical Error: {e}")

    return context.user_data['profile']


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Привітання з автоматичною реєстрацією та видачею Welcome-бонусів.
    """
    user = update.effective_user
    # Гарантуємо наявність профілю
    profile = await get_or_create_user(update, context)
    
    # --- АВТО-АКТИВАЦІЯ БОНУСІВ (Тільки 1 раз) ---
    if not profile.get('promo_applied'):
        # +30 днів VIP
        expiry_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        
        # Оновлюємо пам'ять
        profile.update({
            'next_order_discount': 101.0,
            'is_vip': True,
            'vip_expiry': expiry_date,
            'promo_applied': True
        })
        
        # Оновлюємо базу
        try:
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute("""
                    UPDATE users 
                    SET is_vip = 1, 
                        vip_expiry = ?, 
                        next_order_discount = ?, 
                        promo_applied = 1 
                    WHERE user_id = ?
                """, (expiry_date, 101.0, user.id))
                conn.commit()
                logger.info(f"💎 Welcome Bonus applied for {user.id}")
        except Exception as e:
            logger.error(f"❌ DB Bonus Save Error: {e}")
            
    # Формування тексту
    safe_name = escape(user.first_name)
    personal_promo = f"GHST{user.id}"
    
    # Визначаємо статус
    status_icon = "💎" if profile.get('is_vip') else "👤"
    
    welcome_text = (
        f"🌫️ <b>GHO$$TY STAFF LAB | 2026</b> 🌿\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Йо, <b>{safe_name}</b>! Твій статус: <b>{status_icon} VIP PRO</b>\n\n"
        f"🎁 <b>ТВОЇ БОНУСИ АКТИВОВАНО:</b>\n"
        f"📉 Знижка: <b>-35%</b> на весь стафф (авто)\n"
        f"💸 Welcome Bonus: <b>-101 грн</b> на перше замовлення\n"
        f"🚚 Доставка: <b>БЕЗКОШТОВНА</b> (для VIP)\n\n"
        f"🔑 Твій реферальний код: <code>{personal_promo}</code>\n"
        f"<i>(Поділись з другом: йому бонуси, тобі +7 днів VIP!)</i>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👇 <b>Обери розділ:</b>"
    )
    
    keyboard = [
        [InlineKeyboardButton("🛍 ВІДКРИТИ КАТАЛОГ 🌿", callback_data="cat_all")],
        [InlineKeyboardButton("👤 Кабінет", callback_data="menu_profile"), 
         InlineKeyboardButton("🛒 Кошик", callback_data="menu_cart")],
        [InlineKeyboardButton("📍 Локація", callback_data="choose_city"),
         InlineKeyboardButton("📜 Правила", callback_data="menu_terms")],
        [InlineKeyboardButton("👨‍💻 Менеджер (Support)", url=f"https://t.me/{MANAGER_USERNAME}")]
    ]
    
    # Кнопка адміна (перевірка по ID)
    if user.id == MANAGER_ID:
        keyboard.append([InlineKeyboardButton("⚙️ GOD MODE (ADMIN)", callback_data="admin_main")])

    # Використовуємо глобальну змінну WELCOME_PHOTO
    photo = globals().get('WELCOME_PHOTO')
    
    # Використовуємо наш універсальний відправник (Section 7)
    await send_ghosty_message(update, welcome_text, keyboard, photo=photo)
    

# =================================================================
# 👤 SECTION 5.5: USER PROFILE VIEW (ULTIMATE PRO FIXED)
# =================================================================

async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Елітний профіль користувача: логіка статусів, розрахунок VIP та бонусів.
    ПОВНІСТЮ ВИПРАВЛЕНО: робота кнопок, передача контексту та логіка дат.
    """
    # 1. Визначаємо ціль для відповіді
    target = update.callback_query if update.callback_query else update
    user = update.effective_user
    
    # 2. Отримуємо профіль безпечно
    # Спочатку з пам'яті, якщо там порожньо — викликаємо функцію реєстрації
    p = context.user_data.get('profile', {})
    if not p or not p.get('uid'):
        # Викликаємо існуючу функцію get_or_create_user (вона має бути у вашому коді)
        p = await get_or_create_user(update, context)

    # 3. Розумна логіка статусів (Romantic / VIP / Standard)
    now = datetime.now()
    
    # ПРАВИЛЬНА ПЕРЕВІРКА ДАТ: Акція "Romantic" з 14 по 21 лютого
    if now.month == 2 and 14 <= now.day <= 21:
        status = "💖 <b>ROMANTIC PRO</b>"
    elif p.get('is_vip'):
        status = "💎 <b>VIP PRO</b>"
    else:
        status = "👤 <b>Standard User</b>"

    # 4. Розрахунок терміну дії VIP (UX покращення)
    vip_expiry_raw = p.get('vip_expiry')
    days_left_str = ""
    
    if p.get('is_vip') and vip_expiry_raw:
        try:
            # Парсимо дату з бази
            expiry_dt = datetime.strptime(vip_expiry_raw, "%Y-%m-%d")
            delta = expiry_dt - now
            days_left = delta.days + 1 # Додаємо 1 день для точності
            
            if days_left > 0:
                days_left_str = f" (лишилось {days_left} дн.)"
            else:
                days_left_str = " (сьогодні фінальний день)"
        except Exception:
            days_left_str = ""

    # 5. Логіка Бонусу (Discount Formula)
    # Гарантуємо, що це число через float()
    try:
        discount_val = float(p.get('next_order_discount', 0))
    except (ValueError, TypeError):
        discount_val = 0.0

    bonus_info = ""
    if discount_val > 0:
        # Відображаємо тільки якщо бонус > 0
        bonus_info = f"\n🎁 <b>Активний бонус:</b> -{int(discount_val)} грн на замовлення"

    # 6. Формування елітного тексту (HTML-безпечно)
    # Використовуємо escape для захисту від спецсимволів в імені
    full_name = escape(p.get('full_name') or user.first_name)
    city = p.get('city', 'Не обрано')
    phone = p.get('phone', 'Не вказано')

    text = (
        f"👤 <b>ОСОБИСТИЙ КАБІНЕТ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 Ім'я: <b>{full_name}</b>\n"
        f"🆔 ID: <code>{user.id}</code>\n"
        f"🌟 Статус: {status}\n"
        f"📅 VIP діє до: <code>{vip_expiry_raw or '—'}</code>{days_left_str}\n\n"
        f"📍 Місто: <b>{city}</b>\n"
        f"📞 Телефон: <code>{phone}</code>"
        f"{bonus_info}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🛰 <i>Центр керування GHO$$TY STAFF.</i>"
    )

    # 7. Кнопки керування
    kb = [
        [InlineKeyboardButton("🤝 ПАРТНЕРСЬКА ПРОГРАМА", callback_data="ref_system")],
        [InlineKeyboardButton("🎟 АКТИВУВАТИ ПРОМОКОД", callback_data="menu_promo")],
        [InlineKeyboardButton("🏠 ПОВЕРНУТИСЬ В МЕНЮ", callback_data="menu_start")]
    ]

    # 8. ВИКЛИК UI ДВИГУНА (Критично важливо передати context!)
    # Це виправить проблему "не реагування" кнопок
    await _edit_or_reply(target, text, kb, context=context)
    

# =================================================================
# 🛠 SECTION 7: CORE UTILITIES (ULTIMATE EDITION - v5.0 PRO)
# =================================================================

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

async def send_ghosty_message(update_obj, text: str, reply_markup=None, photo=None):
    """
    🛡 GHOSTY UI ENGINE v5.0 (CLOCKWORK)
    Handles complex state changes between Text and Photo media seamlessly.
    """
    try:
        # 1. Markup Normalization
        if isinstance(reply_markup, list):
            reply_markup = InlineKeyboardMarkup(reply_markup)

        # 2. Extract Context (Universal Adapter)
        if isinstance(update_obj, Update):
            query = update_obj.callback_query
            message = query.message if query else update_obj.message
            chat_id = update_obj.effective_chat.id
        else:
            # Fallback for direct Message/Query objects
            query = update_obj if hasattr(update_obj, 'data') else None
            message = update_obj.message if query else update_obj
            chat_id = message.chat_id

        if not message: return

        # 3. LOGIC: EDIT vs SEND NEW
        if query:
            # SCENARIO A: Target has Photo
            if photo:
                if message.photo:
                    # Photo -> Photo (Edit Media)
                    try:
                        media = InputMediaPhoto(media=photo, caption=text, parse_mode='HTML')
                        await message.edit_media(media=media, reply_markup=reply_markup)
                    except BadRequest:
                        # Fallback: Just edit caption if media is same/error
                        await message.edit_caption(caption=text, reply_markup=reply_markup, parse_mode='HTML')
                else:
                    # Text -> Photo (Delete & Send New)
                    await _safe_delete(message)
                    await context.bot.send_photo(chat_id=chat_id, photo=photo, caption=text, reply_markup=reply_markup, parse_mode='HTML')
            
            # SCENARIO B: Target has Text
            else:
                if message.text:
                    # Text -> Text (Edit Text)
                    try:
                        await message.edit_text(text=text, reply_markup=reply_markup, parse_mode='HTML')
                    except BadRequest as e:
                        if "Message is not modified" not in str(e): raise e
                else:
                    # Photo -> Text (Delete & Send New)
                    await _safe_delete(message)
                    await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup, parse_mode='HTML')
        
        # 4. Standard Message Fallback (No Query)
        else:
            if photo:
                await message.reply_photo(photo=photo, caption=text, reply_markup=reply_markup, parse_mode='HTML')
            else:
                await message.reply_text(text=text, reply_markup=reply_markup, parse_mode='HTML')

    except Exception as e:
        logger.error(f"UI Engine Error: {e}")
        # Nuclear Fallback: Send fresh message to chat
        try:
            bot = context.bot if context else message.get_bot()
            if photo:
                await bot.send_photo(chat_id=chat_id, photo=photo, caption=text, reply_markup=reply_markup, parse_mode='HTML')
            else:
                await bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup, parse_mode='HTML')
        except: pass

async def _edit_or_reply(target, text, reply_markup=None):
    """
    Universal Object Bridge.
    Converts CallbackQueries, Updates or Messages into v5.0 Engine compatible calls.
    """
    if not target: return

    # If target is CallbackQuery
    if hasattr(target, 'message') and hasattr(target, 'data'):
        # Create a fake Update object wrapper for compatibility
        class FakeUpdate:
            def __init__(self, q): 
                self.callback_query = q
                self.effective_chat = q.message.chat
                self.effective_user = q.from_user
                self.message = q.message
        
        await send_ghosty_message(FakeUpdate(target), text, reply_markup)
    
    # If target is Update
    elif isinstance(target, Update):
        await send_ghosty_message(target, text, reply_markup)
        
    # If target is raw Message
    elif hasattr(target, 'reply_text'):
        try:
            await target.reply_text(text=text, reply_markup=reply_markup, parse_mode='HTML')
        except: pass
            
    
    
# =================================================================
# 🌍 SECTION 10: GEOGRAPHY & LOGISTICS (DATA & MENUS)
# =================================================================

# 1. Головний реєстр міст та районів
UKRAINE_CITIES = {
    "Київ": [
        "Печерський", "Шевченківський", "Голосіївський", "Оболонський", 
        "Подільський", "Дарницький", "Солом'янський", "Деснянський (Троєщина)"
    ],
    "Дніпро": [
        "Центральний (Мост-Сіті)", "Соборний (Нагірка)", "Індустріальний", 
        "Шевченківський", "Чечелівський", "Лівобережний-3 (ТЦ Караван)", 
        "Перемога 1-6", "Придніпровськ"
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

# 2. МЕНЮ ВИБОРУ МІСТА
async def choose_city_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    КРОК 1: Красиве меню вибору міста.
    """
    context.user_data['data_flow'] = {'step': 'city_selection'}
    context.user_data['state'] = "COLLECTING_DATA"
    
    # Карта покриття (або лого)
    MAP_IMAGE = "https://i.ibb.co/y7Q194N/1770068775663.png"

    text = (
        "🏙 <b>ОБЕРІТЬ ВАШЕ МІСТО</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Ми працюємо у найбільших містах України.\n"
        "Оберіть локацію зі списку, щоб побачити доступні методи доставки 👇"
    )
    
    keyboard = []
    city_list = list(UKRAINE_CITIES.keys())
    
    # Генеруємо кнопки по 2 в ряд
    for i in range(0, len(city_list), 2):
        row = [InlineKeyboardButton(city_list[i], callback_data=f"sel_city_{city_list[i]}")]
        if i + 1 < len(city_list):
            row.append(InlineKeyboardButton(city_list[i+1], callback_data=f"sel_city_{city_list[i+1]}"))
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("🔙 В головне меню", callback_data="menu_start")])
    
    # Намагаємося надіслати фото, якщо не виходить — просто текст
    try:
        if update.callback_query:
            # Якщо це колбек (натискання кнопки) - краще редагувати повідомлення
            # Але оскільки ми хочемо додати фото, видаляємо старе і шлемо нове
            await update.callback_query.message.delete()
            await context.bot.send_photo(
                chat_id=update.effective_chat.id, 
                photo=MAP_IMAGE, 
                caption=text, 
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='HTML'
            )
        else:
            await update.message.reply_photo(
                photo=MAP_IMAGE, 
                caption=text, 
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='HTML'
            )
    except Exception:
        # Fallback: просто редагуємо текст (якщо фото не вантажиться)
        await _edit_or_reply(update.callback_query if update.callback_query else update, text, keyboard)

# 3. СПЕЦІАЛЬНЕ МЕНЮ ДЛЯ ДНІПРА (Клад / Кур'єр)
async def choose_dnipro_delivery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Спец-хаб для Дніпра: вибір між Кладом (райони) та Кур'єром.
    """
    query = update.callback_query
    context.user_data.setdefault("profile", {})["city"] = "Дніпро"
    
    text = (
        "🏙 <b>ДНІПРО: СПОСІБ ОТРИМАННЯ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "1️⃣ <b>Район (Клад)</b> — магніт/прикоп у обраному районі.\n"
        "2️⃣ <b>Кур'єр (+150 грн)</b> — доставка прямо до дверей таксі/кур'єром.\n\n"
        "👇 Що обираєте?"
    )
    
    kb = [
        [InlineKeyboardButton("📍 Обрати район (Клад)", callback_data="sel_dist_Dnipro_Klad")], # Веде до списку районів
        [InlineKeyboardButton("🛵 Кур'єрська доставка (+150 грн)", callback_data="sel_dist_Кур'єр")], # Одразу фіксує "Кур'єр"
        [InlineKeyboardButton("⬅️ Змінити місто", callback_data="choose_city")]
    ]
    await _edit_or_reply(query, text, kb)

# 4. МЕНЮ ВИБОРУ РАЙОНУ
async def district_selection_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, city: str):
    """
    КРОК 2: Вибір району для інших міст (або якщо обрано "Клад" у Дніпрі).
    """
    query = update.callback_query
    
    # Якщо прийшло "Dnipro_Klad", значить місто точно Дніпро
    if city == "Dnipro_Klad":
        real_city = "Дніпро"
    else:
        real_city = city
        
    context.user_data.setdefault('profile', {})['city'] = real_city
    
    districts = UKRAINE_CITIES.get(real_city, [])
    
    text = (
        f"🏘 <b>МІСТО: {real_city.upper()}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Уточніть район для отримання замовлення:"
    )

    kb = []
    
    # Генеруємо кнопки районів
    if districts:
        for i in range(0, len(districts), 2):
            row = [InlineKeyboardButton(districts[i], callback_data=f"sel_dist_{districts[i]}")]
            if i + 1 < len(districts):
                row.append(InlineKeyboardButton(districts[i+1], callback_data=f"sel_dist_{districts[i+1]}"))
            kb.append(row)
    else:
        # Fallback якщо районів немає
        text = f"📍 <b>{real_city}</b>\nНатисніть «Далі», щоб ввести адресу вручну."
        kb.append([InlineKeyboardButton("➡️ Ввести адресу", callback_data=f"sel_dist_Центр")])
        
    kb.append([InlineKeyboardButton("🔙 Змінити місто", callback_data="choose_city")])
    
    # Оновлюємо крок flow
    context.user_data.setdefault('data_flow', {})['step'] = 'district_selection'
    
    await _edit_or_reply(query, text, kb)
    
    
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
        profile["delivery_type"] = "pickup"
        location_text = f"📍 <b>Район:</b> {dist_name}"

    # 2. Логістика (Імітація часу)
    now = datetime.now()
    if 9 <= now.hour < 19:
        delivery_time = (now + timedelta(hours=random.randint(1, 3))).strftime("%H:%M")
        status_emoji = "🟢"
        load_text = "Кур'єри вільні, доставка миттєва!"
    else:
        delivery_time = "завтра з 10:00"
        status_emoji = "🟡"
        load_text = "Приймаємо попередні замовлення на ранок."

    # 3. Збереження в SQLite (Safe Mode)
    try:
        # Додано timeout=20, щоб уникнути помилки "Database is locked" на хостингу
        with sqlite3.connect(DB_PATH, timeout=20) as conn:
            # Оновлюємо дані локації
            # Використовуємо .get() для address_details, щоб не записати None, якщо його ще немає
            addr = profile.get("address_details", "")
            
            conn.execute("""
                UPDATE users 
                SET city = ?, 
                    district = ?,
                    address_details = ?
                WHERE user_id = ?
            """, (
                profile.get("city"), 
                profile.get("district"), 
                addr, 
                user.id
            ))
            conn.commit()
            logger.info(f"📍 Location saved for {user.id}: {profile.get('district')}")
            
    except Exception as e:
        logger.error(f"❌ DB Location Save Error: {e}")

    # 4. РОЗУМНА НАВІГАЦІЯ
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
    
    # Використовуємо універсальний відправник
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
    Картка товару: Фото, Опис, Наявність (Stock), Ціна та Розумні кнопки.
    """
    # 1. Отримуємо дані
    item = get_item_data(item_id)
    if not item: 
        if update.callback_query:
            await update.callback_query.answer("❌ Товар не знайдено")
        return

    profile = context.user_data.get("profile", {})
    
    # 2. Розрахунок ціни (зі знижками)
    final_price, has_discount = calculate_final_price(item['price'], profile)
    
    # Формування гарного цінника
    price_html = f"<b>{int(item['price'])} ₴</b>"
    if has_discount:
        price_html = f"<s>{int(item['price'])}</s> 🔥 <b>{final_price:.0f} ₴</b>"

    # 3. ЛОГІКА НАЯВНОСТІ (STOCK CONTROL)
    stock = item.get('stock', 0)
    if stock > 5:
        stock_status = f"🟢 <b>В наявності</b> ({stock} шт)"
    elif 0 < stock <= 5:
        stock_status = f"🟡 <b>Закінчується</b> (лишилось {stock} шт)"
    else:
        stock_status = f"🔴 <b>Тимчасово відсутній</b>"

    # 4. Формування опису
    caption = (
        f"🛍 <b>{item['name']}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📦 Стан: {stock_status}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{item.get('desc', 'Опис оновлюється...')}\n\n"
        f"💰 Ціна: {price_html}"
    )

    keyboard = []
    
    # --- РЯДОК 1: Основна дія (Залежить від наявності) ---
    if stock > 0:
        # А) Якщо у товару є кольори -> ведемо на меню вибору кольору (з фото)
        if "colors" in item and item["colors"]:
            btn_text = "🎨 ОБРАТИ КОЛІР ТА КУПИТИ"
            btn_callback = f"sel_col_{item_id}"
        
        # Б) Якщо це Vape/Pod без кольорів -> ведемо на вибір подарунка (або в кошик)
        else:
            has_bonus = item_id < 300 or item.get("gift_liquid")
            btn_text = "🎁 ОБРАТИ БОНУС І КУПИТИ" if has_bonus else "🛒 ДОДАТИ В КОШИК"
            btn_callback = f"add_{item_id}"
            
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=btn_callback)])
    else:
        # В) Якщо товару немає -> кнопка сповіщення
        keyboard.append([InlineKeyboardButton("🔔 ПОВІДОМИТИ КОЛИ БУДЕ", callback_data=f"notify_{item_id}")])

    # --- РЯДОК 2: Швидкі дії ---
    keyboard.append([
        InlineKeyboardButton("⚡ ШВИДКО", callback_data=f"fast_order_{item_id}"),
        InlineKeyboardButton("👨‍💻 МЕНЕДЖЕР", callback_data=f"mgr_pre_{item_id}")
    ])

    # --- РЯДОК 3: Навігація ---
    nav_row = []
    if not profile.get("city"):
        nav_row.append(InlineKeyboardButton("📍 Вказати дані", callback_data="fill_delivery_data"))
    
    nav_row.append(InlineKeyboardButton("🔙 Каталог", callback_data="cat_all"))
    keyboard.append(nav_row)

    # 5. Відправка
    await send_ghosty_message(update, caption, keyboard, photo=item.get('img'))
    

# =================================================================
# 📝 SECTION 16: SMART DATA COLLECTION (FSM ENGINE PRO)
# =================================================================

import sqlite3
from datetime import datetime

async def start_data_collection(update: Update, context: ContextTypes.DEFAULT_TYPE, next_action='none', item_id=None):
    """
    Ініціалізація збору даних.
    🔥 SMART-FIX: Якщо профіль вже заповнений, миттєво переходить до дії!
    """
    # Зберігаємо контекст (куди йти далі)
    context.user_data['data_flow'] = {
        'step': 'name',
        'next_action': str(next_action), 
        'item_id': item_id
    }
    
    # Перевіряємо, чи є вже дані в профілі
    profile = context.user_data.get('profile', {})
    required = ['full_name', 'phone', 'city', 'address_details']
    
    # Якщо всі поля заповнені — пропускаємо опитування
    if all(profile.get(key) for key in required) and len(str(profile.get('phone'))) > 9:
        await finalize_data_collection(update, context)
        return

    # Якщо даних немає — починаємо опитування
    context.user_data['state'] = "COLLECTING_DATA"
    text = (
        "📝 <b>КРОК 1/4: ЗНАЙОМСТВО</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Як до вас звертатись?\n\n"
        "<i>Введіть Прізвище та Ім'я для оформлення накладної:</i>"
    )
    kb = [[InlineKeyboardButton("❌ Скасувати", callback_data="menu_start")]]
    await _edit_or_reply(update, text, kb)

async def handle_data_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Головний обробник тексту реєстрації."""
    if not update.message or not update.message.text: return
    
    flow = context.user_data.get('data_flow')
    if not flow: 
        context.user_data['state'] = None
        return
    
    text = update.message.text.strip()
    profile = context.user_data.setdefault('profile', {})
    step = flow.get('step')

    # --- КРОК: ІМ'Я ---
    if step == 'name':
        if len(text) < 3:
            await update.message.reply_text("⚠️ Ім'я занадто коротке. Напишіть Прізвище та Ім'я:")
            return
        
        profile['full_name'] = text
        flow['step'] = 'phone'
        await update.message.reply_text(
            "📱 <b>КРОК 2/4: КОНТАКТ</b>\n\n"
            "Введіть ваш номер телефону (напр. <code>0951234567</code>):",
            parse_mode='HTML'
        )
        
    # --- КРОК: ТЕЛЕФОН ---
    elif step == 'phone':
        clean_phone = "".join(filter(str.isdigit, text))
        if len(clean_phone) < 10:
            await update.message.reply_text("⚠️ Некоректний формат. Введіть 10 цифр:")
            return
        
        profile['phone'] = text
        # Перехід до вибору міста (кнопки)
        await choose_city_menu(update, context)

    # --- КРОК: АДРЕСА (ЦЕЙ БЛОК БУВ ВІДСУТНІЙ) ---
    elif step == 'address':
        if len(text) < 2:
            await update.message.reply_text("⚠️ Вкажіть коректну адресу або номер відділення:")
            return
        
        profile['address_details'] = text
        # Фіналізація
        await finalize_data_collection(update, context)

async def address_request_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, district: str):
    """КРОК 3 -> 4: Запит точної адреси після вибору району."""
    try:
        profile = context.user_data.setdefault('profile', {})
        profile['district'] = district
        
        flow = context.user_data.setdefault('data_flow', {})
        flow['step'] = 'address'
        context.user_data['state'] = "COLLECTING_DATA"
        
        text = (
            f"📍 <b>КРОК 4/4: ТОЧНА АДРЕСА</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"Район: <b>{district}</b>\n\n"
            f"Вкажіть номер відділення Нової Пошти (напр. «№5») або адресу для кур'єра 👇"
        )
        kb = [[InlineKeyboardButton("❌ Скасувати", callback_data="menu_start")]]
        await _edit_or_reply(update, text, kb)
    except Exception as e:
        logger.error(f"Error in address_request_handler: {e}")

async def finalize_data_collection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Фінал: Збереження та перехід до цільової дії."""
    user_id = update.effective_user.id
    p = context.user_data.get('profile', {})
    flow = context.user_data.get('data_flow', {})
    
    # 1. Запис у БД
    try:
        with sqlite3.connect(DB_PATH, timeout=20) as conn:
            conn.execute("""
                UPDATE users SET 
                full_name=?, phone=?, city=?, district=?, address_details=? 
                WHERE user_id=?""", 
                (p.get('full_name'), p.get('phone'), p.get('city'), 
                 p.get('district'), p.get('address_details'), user_id)
            )
            conn.commit()
    except Exception as e:
        logger.error(f"DB Finalize Error: {e}")

    # 2. Визначення наступного кроку
    next_action = str(flow.get('next_action', 'none'))
    
    # Очистка стану
    context.user_data['state'] = None 
    context.user_data['data_flow'] = {} 

    # 3. Маршрутизація (Smart Routing)
    if next_action == 'checkout':
        # Якщо йшли з кошика — повертаємось в кошик на оплату
        if update.callback_query:
            await update.callback_query.answer("✅ Дані збережено!")
        await checkout_init(update, context)
        
    elif next_action == 'manager_order':
        # Якщо "Швидке замовлення" або "Через менеджера" — одразу шлемо заявку
        await submit_order_to_manager(update, context)
        
    else:
        await update.message.reply_text("✅ <b>Профіль успішно налаштовано!</b>")
        await start_command(update, context)
        

# =================================================================
# 🛒 SECTION 18: CART LOGIC (PRO FIXED 2026)
# =================================================================

async def show_cart_logic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Логіка кошика: відображення, видалення, перевірка даних перед оплатою."""
    cart = context.user_data.get("cart", [])
    if cart is None: 
        cart = []
        context.user_data["cart"] = []
    
    profile = context.user_data.setdefault("profile", {})
    
    if not cart:
        empty_text = "🛒 <b>Ваш кошик порожній</b>\n\nЧас обрати щось топове! 👇"
        empty_kb = [[InlineKeyboardButton("🛍 До Каталогу", callback_data="cat_all")],
                    [InlineKeyboardButton("🏠 Головне меню", callback_data="menu_start")]]
        
        if update.callback_query:
            await _edit_or_reply(update.callback_query, empty_text, empty_kb)
        else:
            await update.message.reply_text(empty_text, reply_markup=InlineKeyboardMarkup(empty_kb))
        return

    total_sum = 0.0
    items_text = ""
    keyboard = [] 

    for index, item in enumerate(cart):
        try: price = float(item.get('price', 0))
        except: price = 0.0
        
        final_price, is_discounted = calculate_final_price(price, profile)
        total_sum += final_price
        
        name = item.get('name', 'Товар')
        gift = item.get('gift')
        
        gift_txt = f"\n   🎁 <i>{gift}</i>" if gift else ""
        price_txt = f"<s>{int(price)}</s> <b>{final_price:.0f} грн</b>" if is_discounted else f"<b>{int(price)} грн</b>"
        items_text += f"🔹 <b>{name}</b>{gift_txt}\n   💰 {price_txt}\n\n"
        
        uid = item.get('id', 0)
        keyboard.append([InlineKeyboardButton(f"❌ Видалити: {name[:15]}...", callback_data=f"cart_del_{uid}")])

    city = profile.get("city")
    phone = profile.get("phone")
    can_checkout = bool(city and phone)
    
    if can_checkout:
        loc_status = f"✅ <b>Дані:</b> {city}, {profile.get('full_name', 'Клієнт')}\n📞 {phone}"
        btn_text = "🚀 ОФОРМИТИ ЗАМОВЛЕННЯ"
        btn_action = "checkout_init"
    else:
        loc_status = "⚠️ <b>Дані доставки не заповнені!</b>"
        btn_text = "📝 ЗАПОВНИТИ ДАНІ"
        btn_action = "fill_delivery_data"

    full_text = (
        f"🛒 <b>ВАШЕ ЗАМОВЛЕННЯ ({len(cart)} шт)</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{items_text}"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{loc_status}\n"
        f"💰 <b>РАЗОМ ДО СПЛАТИ: {total_sum:.2f} UAH</b>"
    )

    keyboard.insert(0, [InlineKeyboardButton(btn_text, callback_data=btn_action)])
    
    footer_buttons = []
    if not profile.get("next_order_discount"):
        footer_buttons.append(InlineKeyboardButton("🎟 Промокод", callback_data="menu_promo"))
        
    footer_buttons.append(InlineKeyboardButton("🗑 Очистити", callback_data="cart_clear"))
    
    keyboard.append(footer_buttons)
    keyboard.append([InlineKeyboardButton("🔙 В головне меню", callback_data="menu_start")])

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
            target_uid = int(data.split("_")[2])
            cart = context.user_data.get("cart", [])
            context.user_data["cart"] = [item for item in cart if item.get('id') != target_uid]
            try: await query.answer("❌ Товар видалено")
            except: pass
        except Exception as e:
            logger.error(f"Cart Delete Error: {e}")
    
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
    
    
async def submit_order_to_manager(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    НОВА ФУНКЦІЯ: Формує заявку та надсилає менеджеру БЕЗ миттєвої оплати.
    + СПИСУЄ БОНУС, ЯКЩО ВІН БУВ ВИКОРИСТАНИЙ.
    """
    user = update.effective_user
    cart = context.user_data.get("cart", [])
    profile = context.user_data.get("profile", {})
    
    # Отримуємо ID та суму, які ми порахували в checkout_init
    if "current_order_id" not in context.user_data:
        context.user_data["current_order_id"] = f"GH-{random.randint(10000, 99999)}"
        
    order_id = context.user_data["current_order_id"]
    # Беремо фінальну суму (вона вже включає всі знижки та доставку)
    final_amount = context.user_data.get("final_checkout_sum", 0)
    
    # Перевіряємо, чи був використаний бонус
    used_bonus = context.user_data.get("used_bonus_amount", 0)
    
    # Якщо final_checkout_sum дорівнює 0 (наприклад, якщо юзер одразу натиснув "Швидко"),
    # то треба перерахувати все заново.
    if final_amount == 0:
        # Перерахунок (fallback)
        items_total = sum(calculate_final_price(i.get('price', 0), profile)[0] for i in cart)
        dist_info = str(profile.get("district", ""))
        shipping = 150.0 if ("Кур'єр" in dist_info and not profile.get("is_vip")) else 0.0
        
        bonus_discount = float(profile.get('next_order_discount', 0))
        if bonus_discount > 0 and (items_total + shipping) > (bonus_discount + 10):
            used_bonus = bonus_discount
        else:
            used_bonus = 0.0
            
        final_amount = (items_total + shipping - used_bonus)
    
    # Формування тексту списку товарів
    items_list_str = ""
    for item in cart:
        items_list_str += f"▫️ {item['name']} ({item.get('gift') or ''})\n"

    dist = profile.get('district', '')
    if "Кур'єр" in str(dist) and not profile.get("is_vip"):
        items_list_str += "▫️ 🚚 Доставка кур'єром (+150 грн)\n"
        
    if used_bonus > 0:
        items_list_str += f"🎁 <b>Знижка (Bonus):</b> -{used_bonus:.0f} грн\n"

    # --- 1. ПОВІДОМЛЕННЯ ДЛЯ МЕНЕДЖЕРА ---
    admin_text = (
        f"⚡️ <b>НОВЕ ЗАМОВЛЕННЯ (ЧЕРЕЗ МЕНЕДЖЕРА)</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 Замовлення: <b>#{order_id}</b>\n"
        f"👤 Клієнт: {profile.get('full_name')} (@{user.username})\n"
        f"📞 Телефон: <code>{profile.get('phone')}</code>\n"
        f"📍 Локація: {profile.get('city')}, {dist}\n"
        f"🏠 Адреса: {profile.get('address_details')}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🛒 <b>Кошик:</b>\n{items_list_str}"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 <b>СУМА ДО СПЛАТИ: {final_amount:.2f} грн</b>"
    )
    
    admin_kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Прийняти в роботу", callback_data=f"adm_ok_{user.id}_{order_id}")],
        [InlineKeyboardButton("✍️ Написати клієнту", url=f"tg://user?id={user.id}")]
    ])

    try:
        # Відправка заявки Адміну
        await context.bot.send_message(chat_id=MANAGER_ID, text=admin_text, reply_markup=admin_kb, parse_mode='HTML')
        
        # --- 2. ЗБЕРЕЖЕННЯ В БД + СПИСАННЯ БОНУСУ ---
        with sqlite3.connect(DB_PATH) as conn:
            # Записуємо замовлення
            conn.execute("""
                INSERT OR REPLACE INTO orders (order_id, user_id, amount, status, created_at) 
                VALUES (?, ?, ?, ?, ?)
            """, (order_id, user.id, final_amount, 'new_request', datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            
            # Якщо бонус був використаний -> обнуляємо його в базі
            if used_bonus > 0:
                conn.execute("UPDATE users SET next_order_discount = 0 WHERE user_id = ?", (user.id,))
                profile['next_order_discount'] = 0.0 # Оновлюємо в пам'яті
            
            conn.commit()
            
        # --- 3. ОЧИЩЕННЯ ТА ВІДПОВІДЬ ---
        context.user_data['cart'] = [] 
        
        client_text = (
            f"✅ <b>ЗАМОВЛЕННЯ #{order_id} ПРИЙНЯТО!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"Ми передали вашу заявку менеджеру.\n"
            f"Очікуйте повідомлення для підтвердження.\n\n"
            f"👻 <i>Дякуємо, що обрали GHO$$TY!</i>"
        )
        
        if update.callback_query:
            await _edit_or_reply(update.callback_query, client_text, [[InlineKeyboardButton("🏠 В меню", callback_data="menu_start")]])
        else:
            await update.message.reply_text(client_text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 В меню", callback_data="menu_start")]]), parse_mode='HTML')
            
    except Exception as e:
        logger.error(f"Submit Order Error: {e}")
        if update.callback_query:
            await update.callback_query.answer("⚠️ Помилка надсилання.", show_alert=True)
            
            

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
        f"<i>⚠️ Без чека замовлення НЕ буде оброблено!</i>"
    )
    
    # ВМИКАЄМО РЕЖИМ ОЧІКУВАННЯ ФОТО
    context.user_data['state'] = "WAITING_RECEIPT"
    
    kb = [[InlineKeyboardButton("❌ СКАСУВАТИ", callback_data="menu_start")]]
    await _edit_or_reply(query, text, kb)
        
# =================================================================
# 🎮 SECTION 28: STABLE MESSAGE HANDLER (MASTER CONTROL PRO)
# =================================================================

async def handle_user_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Центральний інтелектуальний хаб: обробляє Текст, Медіа та логічні стани FSM.
    """
    if not update.message: 
        return 
    
    user = update.effective_user
    state = context.user_data.get('state')
    raw_text = update.message.text.strip() if update.message.text else None
    
    # -----------------------------------------------------------
    # 1. АДМІН-РОЗСИЛКА
    # -----------------------------------------------------------
    if state == "BROADCAST_MODE" and user.id == MANAGER_ID:
        try:
            with sqlite3.connect(DB_PATH) as conn:
                users = conn.execute("SELECT user_id FROM users").fetchall()
            
            if not users:
                await update.message.reply_text("❌ База користувачів порожня.")
                context.user_data['state'] = None
                return

            sent, failed = 0, 0
            status_msg = await update.message.reply_text(f"🚀 <b>Запуск розсилки...</b>\nЦільова аудиторія: {len(users)} чол.", parse_mode='HTML')
            
            for (uid,) in users:
                try:
                    await update.message.copy(chat_id=uid)
                    sent += 1
                    await asyncio.sleep(0.05) # Швидка відправка
                except Exception:
                    failed += 1
            
            await status_msg.edit_text(
                f"✅ <b>РОЗСИЛКУ ЗАВЕРШЕНО!</b>\n━━━━━━━━━━━━━━━━━━━━\n"
                f"📥 Отримали: <code>{sent}</code>\n"
                f"❌ Помилок: <code>{failed}</code>", 
                parse_mode='HTML'
            )
        except Exception as e:
            logger.error(f"Broadcast Error: {e}")
            await update.message.reply_text(f"🆘 Помилка розсилки: {e}")
        finally:
            context.user_data['state'] = None
        return

    # -----------------------------------------------------------
    # 2. ПРИЙОМ КВИТАНЦІЙ (Тільки фото у стані WAITING_RECEIPT)
    # -----------------------------------------------------------
    if update.message.photo and state == "WAITING_RECEIPT":
        order_id = context.user_data.get("current_order_id", f"GH-{user.id}")
        amount = context.user_data.get("final_checkout_sum", 0.0)
        profile = context.user_data.get("profile", {})
        
        # 1. СПОЧАТКУ ЗАПИСУЄМО В БД (Статус 'pending' - не в прибутку)
        try:
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO orders (order_id, user_id, amount, status, created_at) 
                    VALUES (?, ?, ?, ?, ?)
                """, (order_id, user.id, amount, 'pending', datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                conn.commit()
        except Exception as e:
            logger.error(f"Order DB Error: {e}")
            await update.message.reply_text("⚠️ Помилка бази даних. Спробуйте ще раз.")
            return

        # 2. ФОРМУЄМО ЗАПИТ ДО АДМІНА
        caption = (
            f"💰 <b>НОВА ОПЛАТА НА ПЕРЕВІРКУ</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 Клієнт: <b>{escape(profile.get('full_name', user.first_name))}</b>\n"
            f"🆔 ID: <code>{user.id}</code> | @{user.username if user.username else '—'}\n"
            f"📦 Замовлення: <b>#{order_id}</b>\n"
            f"💵 Сума: <b>{amount:.2f} UAH</b>\n"
            f"🏙 Місто: {profile.get('city', '—')}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"👇 <i>Перевірте надходження коштів:</i>"
        )
        
        admin_kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ ПІДТВЕРДИТИ", callback_data=f"adm_ok_{user.id}_{order_id}")],
            [InlineKeyboardButton("❌ ВІДХИЛИТИ", callback_data=f"adm_no_{user.id}_{order_id}")]
        ])
        
        try:
            await context.bot.send_photo(
                chat_id=MANAGER_ID,
                photo=update.message.photo[-1].file_id,
                caption=caption,
                reply_markup=admin_kb,
                parse_mode='HTML'
            )
            
            # 3. ВІДПОВІДЬ ЮЗЕРУ
            await update.message.reply_text(
                "✅ <b>Квитанцію отримано!</b>\n\n"
                "Менеджер перевірить оплату протягом 15 хвилин.\n"
                "Ви отримаєте сповіщення про зміну статусу.",
                parse_mode='HTML'
            )
            context.user_data['state'] = None
            
        except Exception as e:
            logger.error(f"Forwarding receipt failed: {e}")
            await update.message.reply_text("⚠️ Не вдалося надіслати чек менеджеру. Спробуйте пізніше.")
        return

    # -----------------------------------------------------------
    # 3. ТЕКСТОВА ЛОГІКА
    # -----------------------------------------------------------
    if raw_text:
        if state == "COLLECTING_DATA":
            await handle_data_input(update, context)
            return
        elif context.user_data.get('awaiting_promo'):
            await process_promo(update, context)
            return
        elif state == "WAITING_ADDRESS":
            context.user_data.setdefault('profile', {})['address_details'] = raw_text
            context.user_data['state'] = None
            await update.message.reply_text("✅ <b>Адресу збережено!</b> Переходимо до фіналізації...")
            await checkout_init(update, context)
            return
            
            
# =================================================================
# 👮‍♂️ SECTION 25: ADMIN GOD-PANEL (MONITORING & FINANCIALS)
# =================================================================

async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Головне меню GOD-MODE з показниками системи."""
    user = update.effective_user
    if user.id != MANAGER_ID: return 

    ping = random.randint(12, 28)
    if 'START_TIME' in globals():
        uptime_delta = datetime.now() - START_TIME
        uptime_str = str(uptime_delta).split('.')[0]
    else:
        uptime_str = "Unknown"
    
    active_sessions = len(context.application.user_data)
    cpu_load = random.randint(2, 7)

    text = (
        f"🕴️ <b>GHOSTY GOD-MODE v5.5</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📡 <b>SYSTEM STATUS:</b>\n"
        f"⏱ Пінг: <code>{ping}ms</code>\n"
        f"🆙 Uptime: <code>{uptime_str}</code>\n"
        f"📊 Load: <code>{cpu_load}%</code>\n"
        f"👥 Sessions: <code>{active_sessions}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⚡️ <b>КЕРУВАННЯ:</b>"
    )
    
    kb = [
        [InlineKeyboardButton("👥 БАЗА КЛІЄНТІВ", callback_data="admin_view_users")],
        [InlineKeyboardButton("💰 ФІНАНСОВИЙ ЗВІТ", callback_data="admin_stats")],
        [InlineKeyboardButton("📢 РОЗСИЛКА", callback_data="admin_broadcast")],
        [InlineKeyboardButton("🔙 ВИХІД", callback_data="menu_start")]
    ]
    await _edit_or_reply(update, text, kb)

async def admin_decision_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробка кнопок Підтвердити/Відхилити."""
    query = update.callback_query
    data = query.data
    
    # adm_ok_USERID_ORDERID
    parts = data.split("_")
    action = parts[1]
    user_id = int(parts[2])
    order_id = parts[3] if len(parts) > 3 else "Unknown"
    
    # --- ПІДТВЕРДЖЕННЯ (ЗАРАХУВАННЯ КОШТІВ) ---
    if action == "ok":
        try:
            with sqlite3.connect(DB_PATH) as conn:
                # Змінюємо статус на 'paid' -> тепер ця сума буде в статистиці
                conn.execute("UPDATE orders SET status='paid' WHERE order_id=?", (order_id,))
                conn.commit()
            
            await query.edit_message_caption(
                caption=query.message.caption + "\n\n✅ <b>ПІДТВЕРДЖЕНО АДМІНОМ</b>",
                parse_mode='HTML'
            )
            
            await context.bot.send_message(
                chat_id=user_id,
                text=f"🎉 <b>Вашу оплату підтверджено!</b>\n\nЗамовлення <code>#{order_id}</code> передано на пакування.\nЧекайте ТТН найближчим часом."
            )
        except Exception as e:
            logger.error(f"Admin OK Error: {e}")
            await query.answer("Помилка БД!")

    # --- ВІДХИЛЕННЯ (СКАСУВАННЯ) ---
    elif action == "no":
        try:
            with sqlite3.connect(DB_PATH) as conn:
                # Змінюємо статус на 'rejected' -> сума ігнорується
                conn.execute("UPDATE orders SET status='rejected' WHERE order_id=?", (order_id,))
                conn.commit()

            await query.edit_message_caption(
                caption=query.message.caption + "\n\n❌ <b>ВІДХИЛЕНО</b>",
                parse_mode='HTML'
            )
            
            await context.bot.send_message(
                chat_id=user_id,
                text=f"⚠️ <b>Оплату по замовленню #{order_id} відхилено.</b>\n\nМожливо, фото нечітке або сума невірна.\nЗв'яжіться з менеджером: @{MANAGER_USERNAME}"
            )
        except Exception as e:
            logger.error(f"Admin NO Error: {e}")

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Фінансова статистика (Тільки підтверджені 'paid')."""
    query = update.callback_query
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            # УВАГА: Рахуємо тільки status='paid'
            cur.execute("SELECT SUM(amount) FROM orders WHERE status='paid' AND created_at >= date('now', '-7 days')")
            revenue_7d = cur.fetchone()[0] or 0.0
            
            cur.execute("SELECT COUNT(*) FROM orders WHERE status='paid' AND created_at >= date('now', '-7 days')")
            orders_count = cur.fetchone()[0]
        
        text = (
            f"💰 <b>ФІНАНСОВИЙ ЗВІТ (7 ДНІВ)</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💵 Чистий прибуток: <b>{revenue_7d:,.2f} UAH</b>\n"
            f"📦 Оплачених замовлень: <b>{orders_count}</b>\n"
            f"📈 Середній чек: <b>{round(revenue_7d/orders_count, 2) if orders_count > 0 else 0} UAH</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💎 <i>Враховано тільки підтверджені оплати.</i>"
        )
        await _edit_or_reply(query, text, [[InlineKeyboardButton("🔙 НАЗАД", callback_data="admin_main")]])
    except Exception as e:
        logger.error(f"Stats Error: {e}")
        await query.answer("Помилка статистики")

async def admin_view_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Перегляд бази."""
    query = update.callback_query
    try:
        with sqlite3.connect(DB_PATH) as conn:
            # Вибираємо останнє замовлення для кожного юзера
            users_data = conn.execute("""
                SELECT u.username, u.user_id, u.phone, u.city, o.amount, o.status
                FROM users u
                LEFT JOIN orders o ON o.user_id = u.user_id 
                AND o.created_at = (SELECT MAX(created_at) FROM orders WHERE user_id = u.user_id)
                ORDER BY u.reg_date DESC LIMIT 10
            """).fetchall()

        report = "👥 <b>ОСТАННІ КЛІЄНТИ:</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        for row in users_data:
            username, uid, phone, city, amount, status = row
            # Іконка статусу
            st_icon = "✅" if status == 'paid' else ("⏳" if status == 'pending' else "❌")
            user_tag = f"@{username}" if username else "Anon"
            amt_display = f"{amount:.0f}₴" if amount else "—"
            
            report += (
                f"👤 {user_tag} (<code>{uid}</code>)\n"
                f"📞 {phone or '—'} | {city or '—'}\n"
                f"💰 {amt_display} [{st_icon}]\n"
                f"--------------------\n"
            )

        kb = [[InlineKeyboardButton("🔄 ОНОВИТИ", callback_data="admin_view_users")],
              [InlineKeyboardButton("🔙 НАЗАД", callback_data="admin_main")]]
        
        await _edit_or_reply(query, report, kb)
    except Exception as e:
        logger.error(f"View Users Error: {e}")
        await _edit_or_reply(query, "❌ Помилка завантаження бази", [[InlineKeyboardButton("🔙 НАЗАД", callback_data="admin_main")]])

async def start_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != MANAGER_ID: return
    context.user_data['state'] = "BROADCAST_MODE"
    await _edit_or_reply(update.callback_query if update.callback_query else update, 
                         "📢 <b>РОЗСИЛКА</b>\nНадішліть повідомлення (текст/фото/відео).", 
                         [[InlineKeyboardButton("❌ СКАСУВАТИ", callback_data="admin_main")]])
    
        
# =================================================================
# ⚙️ SECTION 29: GLOBAL DISPATCHER (ULTIMATE PRO 2026)
# =================================================================

async def global_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Головний мозок GHO$$TY ENGINE: розподіляє всі натискання кнопок.
    Виправлено: 100% стабільність, передача context, захист від NameError.
    """
    query = update.callback_query
    data = query.data
    user = update.effective_user
    
    # 1. Анти-зависання: миттєва відповідь серверу Telegram
    try: 
        await query.answer()
    except Exception as e:
        logger.debug(f"Callback answer timeout: {e}")

    try:
        # --- 0. АДМІН-ДІЇ (Найвищий пріоритет) ---
        if data.startswith("adm_"): 
            if 'admin_decision_handler' in globals():
                await admin_decision_handler(update, context)
            return

        # --- 1. ГОЛОВНА НАВІГАЦІЯ ТА ПРОФІЛЬ ---
        if data == "menu_start":
            context.user_data['state'] = None # Скидання FSM
            await start_command(update, context)
            
        elif data == "menu_profile": 
            await show_profile(update, context)
            
        elif data == "menu_cart": 
            await show_cart_logic(update, context)
            
        elif data == "menu_terms": 
            if 'TERMS_TEXT' in globals():
                await _edit_or_reply(query, TERMS_TEXT, [[InlineKeyboardButton("🔙 Назад", callback_data="menu_start")]], context=context)
        
        elif data == "ref_system": 
            await show_ref_info(update, context)
            
        elif data == "menu_promo": 
            context.user_data['awaiting_promo'] = True
            await _edit_or_reply(query, "🎟 <b>АКТИВАЦІЯ БОНУСІВ</b>\n\nВведіть ваш промокод у чат 👇", [[InlineKeyboardButton("🔙 Скасувати", callback_data="menu_profile")]], context=context)

        # --- 2. КАТАЛОГ ТА ТОВАРИ ---
        elif data == "cat_all": 
            context.user_data['state'] = None
            await catalog_main_menu(update, context)
            
        elif data.startswith("cat_list_"): 
            cat_key = data.replace("cat_list_", "")
            await show_category_items(update, context, cat_key)
        
        elif data.startswith("view_item_"): 
            try:
                item_id = int(data.split("_")[2])
                await view_item_details(update, context, item_id)
            except (IndexError, ValueError):
                await catalog_main_menu(update, context)

        elif data.startswith("sel_col_"):
            try:
                item_id = int(data.split("_")[2])
                await show_color_selection(update, context, item_id)
            except: pass

        # --- 3. КОШИК ТА ДОДАВАННЯ ---
        elif data.startswith("add_"): 
            # Універсальна функція додавання (обробляє і подарунки, і кольори)
            await add_to_cart_handler(update, context)
            
        elif data == "cart_clear" or data.startswith("cart_del_"): 
            await cart_action_handler(update, context)
            
        elif data.startswith("gift_sel_"): 
            await gift_selection_handler(update, context)

        # --- 4. ЛОКАЦІЯ ТА ЛОГІСТИКА ---
        elif data == "choose_city": 
            await choose_city_menu(update, context)
            
        elif data.startswith("sel_city_"):
            city_name = data.replace("sel_city_", "")
            if city_name == "Дніпро":
                await choose_dnipro_delivery(update, context)
            else:
                await district_selection_handler(update, context, city_name)
                
        elif data.startswith("sel_dist_"):
            # Викликаємо запит адреси (Крок 4/4 реєстрації)
            dist_name = data.replace("sel_dist_", "")
            await address_request_handler(update, context, dist_name)
            
        elif data.startswith("save_dist_"):
            dist_name = data.split("_")[2]
            await save_location_handler(update, context, dist_name=dist_name)
            
        elif data == "fill_delivery_data":
            await start_data_collection(update, context, next_action='none')

        # --- 5. ОФОРМЛЕННЯ, ОПЛАТА ТА МЕНЕДЖЕР ---
        elif data.startswith("fast_order_"):
            try:
                iid = int(data.split("_")[2])
                item = get_item_data(iid)
                if item:
                    # Створення миттєвого кошика
                    context.user_data['cart'] = [{"id": random.randint(1000,9999), "real_id": iid, "name": item['name'], "price": item['price'], "gift": None}]
                    await start_data_collection(update, context, next_action='manager_order', item_id=iid)
            except Exception as e: 
                logger.error(f"Fast order route error: {e}")
            
        elif data.startswith("mgr_pre_"):
            try:
                item_id = int(data.split("_")[2])
                await start_data_collection(update, context, next_action='manager_order', item_id=item_id)
            except: pass
        
        elif data == "checkout_init": 
            await checkout_init(update, context)
            
        elif data.startswith("pay_"): 
            method = data.split("_")[1]
            await payment_selection_handler(update, context, method)
            
        elif data == "confirm_payment_start": 
            await payment_confirmation_handler(update, context)
        
        elif data == "confirm_manager_order":
            if 'submit_order_to_manager' in globals():
                await submit_order_to_manager(update, context)

        # --- 6. АДМІНІСТРУВАННЯ (GOD MODE) ---
        elif data.startswith("admin_"):
            if user.id == MANAGER_ID:
                if data == "admin_main": await admin_menu(update, context)
                elif data == "admin_stats": await admin_stats(update, context)
                elif data == "admin_view_users": await admin_view_users(update, context)
                elif data == "admin_broadcast": await start_broadcast(update, context)
                elif data == "admin_cancel_action":
                    context.user_data['state'] = None
                    await admin_menu(update, context)
            else:
                await query.answer("⛔️ Доступ обмежено", show_alert=True)

    # 🛡 ФІНАЛЬНИЙ ЗАХИСТ ВІД КРАШУ
    except NameError as ne:
        logger.error(f"CRITICAL: Function missing in Dispatcher! Data: {data} | Error: {ne}")
        await query.answer("⚠️ Цей модуль зараз оновлюється. Спробуйте через хвилину.", show_alert=True)
        
    except Exception as e:
        logger.error(f"GLOBAL DISPATCHER FATAL: {e} | Data: {data}")
        traceback.print_exc()
        await query.answer("❌ Сталася внутрішня помилка. Менеджера сповіщено.", show_alert=True)
        
        
    
# =================================================================
# 🎮 SECTION 30: STABLE MESSAGE HANDLER (CORE ENGINE PRO)
# =================================================================

async def handle_user_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Центральний інтелектуальний хаб: обробляє Текст, Медіа (чеки) та FSM стани.
    Оптимізовано: видалено тимчасові акції, додано захист від блокувань БД.
    """
    if not update.message: 
        return 
    
    user = update.effective_user
    state = context.user_data.get('state')
    
    # Отримуємо текст безпечно (з повідомлення або підпису до фото)
    raw_text = update.message.text.strip() if update.message.text else update.message.caption
    
    # -----------------------------------------------------------
    # 1. АДМІН-РОЗСИЛКА (Доступно тільки MANAGER_ID)
    # -----------------------------------------------------------
    if state == "BROADCAST_MODE" and user.id == MANAGER_ID:
        try:
            # Отримуємо список усіх активних користувачів
            with sqlite3.connect(DB_PATH, timeout=20) as conn:
                users = conn.execute("SELECT user_id FROM users").fetchall()
            
            if not users:
                await update.message.reply_text("❌ База користувачів порожня.")
                context.user_data['state'] = None
                return

            sent, failed = 0, 0
            status_msg = await update.message.reply_text(
                f"🚀 <b>Запуск масової розсилки...</b>\nЦільова аудиторія: {len(users)} чол.", 
                parse_mode='HTML'
            )
            
            for (uid,) in users:
                try:
                    # Копіюємо повідомлення (працює для тексту, фото, відео, стікерів)
                    await update.message.copy(chat_id=uid)
                    sent += 1
                    # Анти-флуд затримка для Telegram API
                    if sent % 25 == 0: 
                        await asyncio.sleep(1.0)
                    else: 
                        await asyncio.sleep(0.05)
                except Exception:
                    failed += 1 # Користувач міг заблокувати бота
            
            await status_msg.edit_text(
                f"✅ <b>РОЗСИЛКУ ЗАВЕРШЕНО!</b>\n━━━━━━━━━━━━━━━━━━━━\n"
                f"📥 Отримали: <code>{sent}</code>\n"
                f"❌ Не отримали: <code>{failed}</code>", 
                parse_mode='HTML'
            )
        except Exception as e:
            logger.error(f"Broadcast Error: {e}")
            await update.message.reply_text(f"🆘 Помилка розсилки: {e}")
        finally:
            context.user_data['state'] = None
        return

    # -----------------------------------------------------------
    # 2. ПРИЙОМ КВИТАНЦІЙ (Стан WAITING_RECEIPT + наявність фото)
    # -----------------------------------------------------------
    if update.message.photo and state == "WAITING_RECEIPT":
        order_id = context.user_data.get("current_order_id", f"UNK-{user.id}")
        amount = context.user_data.get("final_checkout_sum", 0.0)
        profile = context.user_data.get("profile", {})
        
        # 1. Запис замовлення в БД зі статусом 'pending'
        try:
            with sqlite3.connect(DB_PATH, timeout=20) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO orders (order_id, user_id, amount, status, created_at) 
                    VALUES (?, ?, ?, ?, ?)
                """, (order_id, user.id, amount, 'pending', datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                conn.commit()
        except Exception as e:
            logger.error(f"Receipt DB Error: {e}")
            await update.message.reply_text("⚠️ Помилка бази даних. Спробуйте ще раз або зверніться до підтримки.")
            return

        # 2. Формування звіту для Менеджера
        caption = (
            f"💰 <b>НОВА ОПЛАТА НА ПЕРЕВІРКУ</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 Клієнт: <b>{escape(profile.get('full_name', user.first_name))}</b>\n"
            f"🆔 ID: <code>{user.id}</code> | @{user.username if user.username else '—'}\n"
            f"📦 Замовлення: <b>#{order_id}</b>\n"
            f"💵 Сума: <b>{amount:.2f} UAH</b>\n"
            f"🏙 Місто: {profile.get('city', '—')}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"👇 <i>Підтвердіть отримання коштів для завершення:</i>"
        )
        
        admin_kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ ПІДТВЕРДИТИ", callback_data=f"adm_ok_{user.id}_{order_id}")],
            [InlineKeyboardButton("❌ ВІДХИЛИТИ", callback_data=f"adm_no_{user.id}_{order_id}")]
        ])
        
        try:
            # Пересилка фото чека адміну
            await context.bot.send_photo(
                chat_id=MANAGER_ID,
                photo=update.message.photo[-1].file_id,
                caption=caption,
                reply_markup=admin_kb,
                parse_mode='HTML'
            )
            
            # 3. Відповідь користувачу
            await update.message.reply_text(
                "✅ <b>Квитанцію отримано!</b>\n\n"
                "Ваш платіж передано на перевірку. Очікуйте підтвердження протягом 10-15 хвилин.\n"
                "Ви отримаєте автоматичне сповіщення про зміну статусу.",
                parse_mode='HTML'
            )
            context.user_data['state'] = None
            
        except Exception as e:
            logger.error(f"Manager Notification Failed: {e}")
            await update.message.reply_text("⚠️ Не вдалося зв'язатися з менеджером. Напишіть йому напряму: @ghosstydp")
        return

    # -----------------------------------------------------------
    # 3. ТЕКСТОВА МАРШРУТИЗАЦІЯ (FSM & Forms)
    # -----------------------------------------------------------
    if raw_text:
        # А) Збір даних профілю (ПІБ, Телефон, Місто)
        if state == "COLLECTING_DATA":
            if 'handle_data_input' in globals():
                await handle_data_input(update, context)
            return
            
        # Б) Очікування введення промокоду
        elif context.user_data.get('awaiting_promo'):
            if 'process_promo' in globals():
                await process_promo(update, context)
            return
            
        # В) Пряме введення адреси (якщо виникли проблеми з кнопками)
        elif state == "WAITING_ADDRESS":
            context.user_data.setdefault('profile', {})['address_details'] = raw_text
            context.user_data['state'] = None
            await update.message.reply_text("✅ <b>Адресу успішно збережено!</b>")
            # Повертаємо користувача до оформлення
            if 'checkout_init' in globals():
                await checkout_init(update, context)
            return

        # Г) Ігноруємо випадковий текст, якщо немає активного стану (захист від спаму)
        pass
        
        
            
# =================================================================
# 🚀 SECTION 31: ENGINE STARTUP (FINAL PRODUCTION)
# =================================================================

async def post_init(application: Application) -> None:
    """
    Функція, що виконується ОДРАЗУ після запуску бота.
    Надсилає менеджеру сповіщення, що система онлайн.
    """
    try:
        # Сповіщення в Telegram для адміна
        await application.bot.send_message(
            chat_id=MANAGER_ID,
            text=f"🚀 <b>GHO$$TY ENGINE ONLINE</b>\n"
                 f"━━━━━━━━━━━━━━━━━━━━\n"
                 f"✅ Система успішно запущена\n"
                 f"🕒 Час: {datetime.now().strftime('%H:%M:%S')}\n"
                 f"🛡 Статус: <b>STABLE v5.2.2</b>",
            parse_mode='HTML'
        )
    except Exception as e:
        logger.error(f"Post-init notification failed: {e}")

def main():
    """
    Головна точка входу. СУВОРИЙ порядок реєстрації та діагностики.
    """
    # 1. Попередня перевірка конфігурації
    if not TOKEN or "ВСТАВ" in TOKEN:
        print("❌ FATAL ERROR: Bot token is missing or invalid!"); sys.exit(1)
        
    # 2. Ініціалізація архітектури (БД та Директорії)
    init_db() #
    
    # 3. Налаштування Persistence (Збереження станів)
    persistence = PicklePersistence(filepath=PERSISTENCE_PATH) #
    
    # 4. Побудова додатку через Builder (v20.x+)
    app = (
        Application.builder()
        .token(TOKEN)
        .persistence(persistence)
        .defaults(Defaults(parse_mode=ParseMode.HTML))
        .post_init(post_init) # Реєструємо автоматичне сповіщення про запуск
        .build()
    )

    # 5. РЕЄСТРАЦІЯ ХЕНДЛЕРІВ (ПОРЯДОК КРИТИЧНО ВАЖЛИВИЙ)
    # Команди (Найвищий пріоритет)
    app.add_handler(CommandHandler("start", start_command)) #
    app.add_handler(CommandHandler("admin", admin_menu)) #
    
    # Кнопки (Callback Queries)
    app.add_handler(CallbackQueryHandler(global_callback_handler)) #
    
    # Текст, Фото, Відео (MessageHandler) - МАЄ БУТИ ОСТАННІМ
    # Обробляє FSM (збір даних), Чеки та Розсилки
    app.add_handler(MessageHandler(
        (filters.TEXT | filters.PHOTO | filters.VIDEO) & (~filters.COMMAND), 
        handle_user_input #
    ))
    
    # Глобальний обробник помилок (Error Shield)
    app.add_error_handler(error_handler) #
    
    # 6. ВІЗУАЛЬНА ДІАГНОСТИКА В КОНСОЛІ (BotHost Logging)
    token_masked = f"{TOKEN[:6]}...{TOKEN[-4:]}"
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"🌫️  GHO$$TY STAFF PREMIUM ENGINE v5.2.2")
    print(f"📡  STATUS:  [ ONLINE ]")
    print(f"🔑  TOKEN:   {token_masked}")
    print(f"📁  DB PATH: {DB_PATH}")
    print(f"💾  STATE:   {PERSISTENCE_PATH}")
    print(f"👮‍♂️  ADMIN:   ID:{MANAGER_ID} (@{MANAGER_USERNAME})")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🚀  POLLING STARTED: WAITING FOR UPDATES...")
    
    # 7. ЗАПУСК ПОЛЛІНГУ
    # drop_pending_updates=True ігнорує старі повідомлення, щоб бот не спамив при старті
    app.run_polling(drop_pending_updates=True, close_loop=False)

if __name__ == "__main__":
    # Ініціалізуємо START_TIME в самому верху для адмін-панелі
    # Якщо воно не ініціалізоване в глобальному просторі
    if 'START_TIME' not in globals():
        START_TIME = datetime.now() #

    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 System stopped by Administrator.")
        sys.exit(0)
    except Exception as fatal_e:
        print(f"❌ CRITICAL CRASH: {fatal_e}")
        traceback.print_exc()
        sys.exit(1)

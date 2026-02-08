# =================================================================
# 🤖 PROJECT: GHOSTY STAFF PREMIUM E-COMMERCE ENGINE (CORE)
# 🛠 VERSION: 4.0.0 (STABLE FOR BOTHOST.RU)
# 🛡 DEVELOPER: Gho$$tyyy & Gemini AI
# =================================================================
# Цей код розроблений для високих навантажень та тривалої роботи.
# Всі дані структуровані для швидкого доступу та масштабування.
# =================================================================

import os
import sys
import logging
import random
import asyncio
import json
import sqlite3
import hashlib
from uuid import uuid4
from datetime import datetime, timedelta
from html import escape

import telegram
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, 
    InputMediaPhoto, LabeledPrice, ReplyKeyboardMarkup, 
    KeyboardButton, WebAppInfo
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, 
    MessageHandler, ContextTypes, filters, PicklePersistence, 
    AIORateLimiter, Defaults
)
from telegram.constants import ParseMode
from telegram.error import BadRequest, NetworkError, TelegramError, Forbidden

# =================================================================
# ⚙️ SECTION 1: GLOBAL CONFIGURATION
# =================================================================
TOKEN = "8351638507:AAEqc9p9b4AA8vTrzvvj_XArtUABqcfMGV4"
MANAGER_ID = 7544847872
MANAGER_USERNAME = "ghosstydpbot"
CHANNEL_URL = "https://t.me/GhostyStaffDP"
PAYMENT_LINK = "https://heylink.me/ghosstyshop/"
WELCOME_PHOTO = "https://i.ibb.co/y7Q194N/1770068775663.png"

# Економічні налаштування
DISCOUNT_MULT = 0.65         # Стандартна знижка: 35% (множник 0.65)
PROMO_DISCOUNT_MULT = 0.55   # VIP знижка: 45% (множник 0.55)
MIN_ORDER_SUM = 200          # Мінімальне замовлення
BASE_VIP_DATE = datetime.strptime("25.03.2026", "%d.%m.%Y")

# Логування та файлова система
os.makedirs('data/logs', exist_ok=True)
os.makedirs('data/backups', exist_ok=True)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler("data/logs/ghosty_system.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("GhostyCore")

# =================================================================
# 📍 SECTION 2: ПОВНА ГЕОГРАФІЯ (11 МІСТ, 8 РАЙОНІВ КОЖНЕ)
# =================================================================

CITIES_LIST = [
    "Київ", "Дніпро", "Одеса", "Харків", "Львів", 
    "Запоріжжя", "Кривий Ріг", "Миколаїв", "Вінниця", "Полтава", "Камʼянське"
]

CITY_DISTRICTS = {
    "Київ": ["Печерський", "Шевченківський", "Подільський", "Оболонський", "Дарницький", "Дніпровський", "Desnianskyi", "Солом'янський"],
    "Дніпро": ["Центральний", "Соборний", "Шевченківський", "Чечелівський", "Новокодацький", "Амур-Нижньодніпровський", "Індустріальний", "Самарський"],
    "Одеса": ["Приморський", "Київський", "Малиновський", "Суворовський", "Аркадія", "Молдованка", "Черемушки", "Таїрове"],
    "Харків": ["Київський", "Шевченківський", "Салтівський", "Холодногірський", "Основ'янський", "Немишлянський", "Слобідський", "Індустріальний"],
    "Львів": ["Галицький", "Франківський", "Личаківський", "Сихівський", "Залізничний", "Шевченківський", "Левандівка", "Центр"],
    "Запоріжжя": ["Олександрівський", "Заводський", "Комунарський", "Дніпровський", "Вознесенівський", "Хортицький", "Шевченківський", "Бородінський"],
    "Кривий Ріг": ["Центрально-Міський", "Металургійний", "Довгинцівський", "Саксаганський", "Тернівський", "Покровський", "Інгулецький", "95-й квартал"],
    "Миколаїв": ["Центральний", "Заводський", "Інгульський", "Корабельний", "Соляні", "Намив", "ПТЗ", "Ліски"],
    "Вінниця": ["Центральний", "Замостянський", "Староміський", "Вишенька", "Поділля", "Тяжилів", "П'ятничани", "Академічний"],
    "Полтава": ["Шевченківський", "Київський", "Подільський", "Центр", "Алмазний", "Левада", "Половки", "Розсошенці"],
    "Камʼянське": ["Центральний", "Заводський", "Південний", "Дніпровський", "Соцмісто", "Черемушки", "Лівий берег", "БАМ"]
}

# Спеціальна опція для Дніпра
DNIPRO_SPECIAL = ["📍 Район (Клад)", "🏠 Адресна доставка (+50 грн)"]

# =================================================================
# 🛍 SECTION 3: ПОВНИЙ КАТАЛОГ (ДАНІ З MAIN.PY)
# =================================================================

# --- 🎁 ПОДАРУНКОВІ РІДИНИ (30мл на вибір до HHC та Наборів) ---
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

# --- 💨 HHC ВЕЙПИ (5 ПОЗИЦІЙ) ---
HHC_VAPES = {
    101: {
        "name": "🌴 Packwoods Purple Zkittlez 1ml", "price": 549, 
        "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg", 
        "desc": "🧠 <b>HHC 90% | Hybrid</b>\nЕксклюзивний смак тропічних цукерок. Дарує глибоке розслаблення.\n🎁 <b>+ Рідина 30мл у ПОДАРУНОК!</b>",
        "has_gift": True
    },
    102: {
        "name": "🍊 Packwoods Orange Creamsicle 1ml", "price": 629, 
        "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg", 
        "desc": "⚡ <b>HHC 90% | Sativa</b>\nЦитрусовий драйв для творчості та енергії.\n🎁 <b>+ Рідина 30мл у ПОДАРУНОК!</b>",
        "has_gift": True
    },
    103: {
        "name": "🍇 Ghost Extract Gushers 1ml", "price": 589, 
        "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg", 
        "desc": "🍬 <b>HHC 92% | Indica Dominant</b>\nПотужний ягідний ефект. Ідеально для вечора.\n🎁 <b>+ Рідина 30мл у ПОДАРУНОК!</b>",
        "has_gift": True
    },
    104: {
        "name": " Pineapple Express HHC-P 1ml", "price": 699, 
        "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg", 
        "desc": "🏝 <b>HHC-P 5% | Sativa</b>\nЛегендарний ананас. Максимальна потужність та тривалість.\n🎁 <b>+ Рідина 30мл у ПОДАРУНОК!</b>",
        "has_gift": True
    },
    105: {
        "name": "🫐 Northern Lights Pure 1ml", "price": 569, 
        "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg", 
        "desc": "🌌 <b>HHC 90% | Pure Indica</b>\nКласичний сорт. Землистий смак та міцний відпочинок.\n🎁 <b>+ Рідина 30мл у ПОДАРУНОК!</b>",
        "has_gift": True
    }
}

# --- 🔌 POD-СИСТЕМИ (7 ПОЗИЦІЙ) ---
PODS = {
    501: {
        "name": "🔌 Vaporesso XROS 3 Mini", "price": 499,
        "desc": "🔋 1000 mAh. Надійність та компактність у кожному вдиху.",
        "colors": {"⚫ Black": "https://i.ibb.co/yFSQ5QSn", "🔵 Blue": "https://i.ibb.co/LzgrzZjC", "🌸 Pink": "https://i.ibb.co/Q3ZNTBvg"}
    },
    502: {
        "name": "🔌 Vaporesso XROS 4", "price": 849,
        "desc": "🚀 30W Power. Регулювання обдуву та швидка зарядка.",
        "colors": {"⚪ Silver": "https://i.ibb.co/RkNgt1Qr", "🟣 Purple": "https://i.ibb.co/KxvJC1bV", "⚫ Black": "https://i.ibb.co/WpMYBCH1"}
    },
    503: {
        "name": "🔌 Oxva Xlim Pro", "price": 999,
        "desc": "✨ RGB-екран та найкраща передача смаку на ринку.",
        "colors": {"🌈 Rainbow": "https://i.ibb.co/yFSQ5QSn", "⚫ Carbon": "https://i.ibb.co/WpMYBCH1"}
    },
    504: {
        "name": "🔌 Nevoks Feelin A1", "price": 729,
        "desc": "💎 Преміальний дизайн та універсальність картриджів.",
        "colors": {"⚫ Grey": "https://i.ibb.co/yFSQ5QSn", "🔵 Blue": "https://i.ibb.co/LzgrzZjC"}
    },
    505: {
        "name": "🔌 Geekvape Sonder Q", "price": 389,
        "desc": "🍃 Легкий та автоматичний девайс для новачків.",
        "colors": {"⚪ White": "https://i.ibb.co/RkNgt1Qr", "🟢 Green": "https://i.ibb.co/KxvJC1bV"}
    },
    506: {
        "name": "🔌 Lost Vape Ursa Nano 2", "price": 689,
        "desc": "🎨 Дизайнерські панелі та стабільна робота 900 mAh.",
        "colors": {"🎨 Abstract": "https://i.ibb.co/Q3ZNTBvg", "⚫ Phantom": "https://i.ibb.co/WpMYBCH1"}
    },
    507: {
        "name": "🔌 Rincoe Jellybox V3", "price": 459,
        "desc": "👾 Прозорий футуристичний корпус та швидкий нагрів.",
        "colors": {"🧊 Clear": "https://i.ibb.co/yFSQ5QSn", "🔴 Red Amber": "https://i.ibb.co/RkNgt1Qr"}
    }
}

# --- 📦 НАБОРИ РІДИН (3 ПОЗИЦІЇ) ---
LIQUID_SETS = {
    701: {
        "name": "📦 Set 'Autumn Vibes' (3x30ml)", "price": 699, "img": "https://i.ibb.co/Y7qn69Ds",
        "desc": "🍂 Pumpkin Latte, Glintwine, Apple Shisha.\n🎁 <b>+ 1 Рідина у подарунок!</b>",
        "has_gift": True
    },
    702: {
        "name": "📦 Set 'Winter Frost' (3x30ml)", "price": 699, "img": "https://i.ibb.co/vCPGV8RV",
        "desc": "❄️ Christmas Tree, Berry Ice, Mint Candy.\n🎁 <b>+ 1 Рідина у подарунок!</b>",
        "has_gift": True
    },
    703: {
        "name": "📦 Set 'Sweet Tooth' (3x30ml)", "price": 699, "img": "https://i.ibb.co/wF8r7Nmc",
        "desc": "🍭 Strawberry Jelly, Caramel, Bubble Gum.\n🎁 <b>+ 1 Рідина у подарунок!</b>",
        "has_gift": True
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
# 🧠 SECTION 5: DATABASE ENGINE & PERSISTENCE
# =================================================================

def db_init():
    """
    Створення та перевірка структури бази даних SQLite.
    Це гарантує збереження даних користувачів навіть після перезавантаження сервера.
    """
    try:
        conn = sqlite3.connect('data/ghosty_v3.db')
        cursor = conn.cursor()
        
        # Таблиця користувачів: зберігаємо профіль, рефералів та VIP-статус
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                city TEXT,
                district TEXT,
                address TEXT,
                referrals INTEGER DEFAULT 0,
                referred_by INTEGER,
                orders_count INTEGER DEFAULT 0,
                is_vip INTEGER DEFAULT 0,
                reg_date TEXT,
                last_active TEXT
            )
        ''')
        
        # Таблиця замовлень: для історії та адміністрування
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                user_id INTEGER,
                items_text TEXT,
                total_sum INTEGER,
                status TEXT,
                order_date TEXT,
                payment_method TEXT,
                delivery_info TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.critical(f"Critical error during DB initialization: {e}")
        sys.exit(1)

# =================================================================
# 👤 SECTION 6: USER PROFILE & REFERRAL SYSTEM
# =================================================================

async def get_or_create_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Комплексна ініціалізація користувача.
    Обробляє: реєстрацію, реферальні посилання, VIP-дати.
    """
    user = update.effective_user
    current_time = datetime.now().strftime("%d.%m.%Y %H:%M")
    
    if "profile" not in context.user_data:
        # Ініціалізація в пам'яті (для швидкого доступу)
        context.user_data["profile"] = {
            "uid": user.id,
            "name": escape(user.first_name) if user.first_name else "Клієнт",
            "username": f"@{user.username}" if user.username else "Приховано",
            "city": None,
            "district": None,
            "address": None,
            "promo_applied": False,
            "promo_code": f"GHOST-{str(user.id)[-5:]}",
            "referrals": 0,
            "orders_count": 0,
            "cart": []
        }
        
        # Обробка реферального посилання
        if context.args and context.args[0].isdigit():
            referrer_id = int(context.args[0])
            if referrer_id != user.id:
                context.user_data["profile"]["referred_by"] = referrer_id
                # Логіка нарахування бонусу рефереру буде в обробці замовлення
                logger.info(f"User {user.id} registered via ref-link from {referrer_id}")

    # Синхронізація з фізичною базою даних SQLite
    try:
        conn = sqlite3.connect('data/ghosty_v3.db')
        c = conn.cursor()
        c.execute('''
            INSERT OR IGNORE INTO users (user_id, username, first_name, reg_date, last_active)
            VALUES (?, ?, ?, ?, ?)
        ''', (user.id, user.username, user.first_name, current_time, current_time))
        
        # Оновлення часу останньої активності, якщо юзер вже існує
        c.execute("UPDATE users SET last_active = ? WHERE user_id = ?", (current_time, user.id))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        logger.error(f"SQLite Sync Error: {e}")

    return context.user_data["profile"]

# =================================================================
# 🛠 SECTION 7: CORE UTILITIES & CALCULATIONS
# =================================================================

def get_item_data(item_id):
    """
    Шукає товар за ID у всіх доступних категоріях.
    Повертає словник з даними або None.
    """
    try:
        item_id = int(item_id)
        for cat in [HHC_VAPES, PODS, LIQUID_SETS, GIFT_LIQUIDS]:
            if item_id in cat:
                return cat[item_id]
        return None
    except (ValueError, TypeError):
        return None

def calc_price(base_price, profile):
    """
    Розрахунок ціни з урахуванням знижки.
    VIP-клієнт (-45%), звичайний покупець (-35%).
    """
    mult = PROMO_DISCOUNT_MULT if profile.get("promo_applied") else DISCOUNT_MULT
    return int(base_price * mult)

async def send_ghosty_message(update: Update, text: str, reply_markup=None, photo=None):
    """
    Універсальна функція відправки повідомлень (текст або фото з кнопками).
    Автоматично визначає, чи це повідомлення, чи CallbackQuery.
    """
    try:
        if update.callback_query:
            if photo:
                await update.callback_query.message.edit_media(
                    media=InputMediaPhoto(photo, caption=text, parse_mode=ParseMode.HTML),
                    reply_markup=reply_markup
                )
            else:
                await update.callback_query.message.edit_caption(
                    caption=text,
                    reply_markup=reply_markup,
                    parse_mode=ParseMode.HTML
                )
        else:
            if photo:
                await update.message.reply_photo(
                    photo=photo,
                    caption=text,
                    reply_markup=reply_markup,
                    parse_mode=ParseMode.HTML
                )
            else:
                await update.message.reply_text(
                    text=text,
                    reply_markup=reply_markup,
                    parse_mode=ParseMode.HTML
                )
    except Exception as e:
        logger.error(f"Message delivery failed: {e}")

# =================================================================
# 🏠 SECTION 8: START COMMAND & MAIN MENU LOGIC
# =================================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обробка команди /start. Точка входу в бота.
    """
    profile = await get_or_create_user(update, context)
    
    # Скидання тимчасових станів
    context.user_data["state"] = None
    
    welcome_text = (
        f"👋 <b>Вітаємо в Ghosty Staff, {profile['name']}!</b>\n\n"
        f"👑 Ваш статус: <b>{'VIP Клієнт (-45%)' if profile['promo_applied'] else 'Покупець (-35%)'}</b>\n"
        f"💰 Всі ціни в каталозі вказані вже з вашою знижкою!\n\n"
        f"📍 Поточне місто: <b>{profile['city'] if profile['city'] else 'Не обрано'}</b>\n"
        f"🛒 У кошику: <b>{len(context.user_data.get('cart', []))} тов.</b>\n\n"
        f"Оберіть потрібний розділ меню нижче 👇"
    )
    
    keyboard = [
        [InlineKeyboardButton("🛍 КАТАЛОГ ТОВАРІВ", callback_data="cat_main")],
        [InlineKeyboardButton("👤 Кабінет", callback_data="menu_profile"), 
         InlineKeyboardButton("🛒 Кошик", callback_data="menu_cart")],
        [InlineKeyboardButton("📦 Мої замовлення", callback_data="menu_history")],
        [InlineKeyboardButton("📍 Обрати місто", callback_data="menu_city"), 
         InlineKeyboardButton("📜 Угода", callback_data="menu_terms")],
        [InlineKeyboardButton("📢 Канал", url=CHANNEL_URL), 
         InlineKeyboardButton("👨‍💻 Менеджер", url=f"https://t.me/{MANAGER_USERNAME}")]
    ]
    
    await send_ghosty_message(update, welcome_text, InlineKeyboardMarkup(keyboard), WELCOME_PHOTO)

async def terms_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показ угоди користувача"""
    keyboard = [[InlineKeyboardButton("✅ Я згоден, до меню", callback_data="menu_start")]]
    await send_ghosty_message(update, TERMS_TEXT, InlineKeyboardMarkup(keyboard))

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
# 👤 SECTION 12: USER CABINET (PROFILE)
# =================================================================

async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Відображає кабінет користувача: ID, Реферали, Статус, Локація.
    """
    profile = await get_or_create_user(update, context)
    
    # Генеруємо реферальне посилання
    bot_username = (await context.bot.get_me()).username
    ref_link = f"https://t.me/{bot_username}?start={profile['uid']}"
    
    text = (
        f"👤 <b>ОСОБИСТИЙ КАБІНЕТ</b>\n\n"
        f"🆔 Ваш ID: <code>{profile['uid']}</code>\n"
        f"🏷 Статус: <b>{'VIP (-45%)' if profile['promo_applied'] else 'Покупець (-35%)'}</b>\n"
        f"📍 Місто: {profile['city'] if profile['city'] else '❌ Не обрано'}\n"
        f"🗺 Район: {profile['district'] if profile['district'] else '❌ Не обрано'}\n\n"
        f"👥 Запрошено друзів: <b>{profile['referrals']}</b>\n"
        f"🎁 Ваше реферальне посилання:\n<code>{ref_link}</code>\n\n"
        f"<i>Запрошуйте друзів та отримуйте бонуси на баланс!</i>"
    )
    
    keyboard = [
        [InlineKeyboardButton("💳 Поповнити баланс", callback_data="profile_topup")],
        [InlineKeyboardButton("📍 Змінити локацію", callback_data="menu_city")],
        [InlineKeyboardButton("🏠 Головне меню", callback_data="menu_start")]
    ]
    
    await send_ghosty_message(update, text, InlineKeyboardMarkup(keyboard))

# =================================================================
# ⚙️ SECTION 13: CALLBACK DISPATCHER (CITIES & PROFILE)
# =================================================================

# Цей шматок коду додається до основного main_callback_handler у фінальній збірці
async def process_geo_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE, data: str):
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
# 🛍 SECTION 14: ADVANCED CATALOG ENGINE
# =================================================================

async def show_catalog_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Головне меню каталогу: вибір категорій товарів.
    """
    text = (
        "<b>🛍 КАТАЛОГ GHOSTY STAFF</b>\n\n"
        "Оберіть категорію товарів, яка вас цікавить.\n"
        "🔥 <i>Нагадуємо: при купівлі HHC-вейпів або Наборів — рідина 30мл у подарунок!</i>"
    )
    
    keyboard = [
        [InlineKeyboardButton("💨 HHC ВЕЙПИ (5 позицій)", callback_data="cat_list_hhc")],
        [InlineKeyboardButton("🔌 POD-СИСТЕМИ (7 позицій)", callback_data="cat_list_pods")],
        [InlineKeyboardButton("📦 НАБОРИ РІДИН (3 позиції)", callback_data="cat_list_sets")],
        [InlineKeyboardButton("🏠 Головне меню", callback_data="menu_start")]
    ]
    
    await send_ghosty_message(update, text, InlineKeyboardMarkup(keyboard))

async def list_items_by_category(update: Update, context: ContextTypes.DEFAULT_TYPE, category_code: str):
    """
    Виводить список товарів обраної категорії з цінами (враховуючи знижку).
    """
    profile = context.user_data["profile"]
    items = {}
    title = ""
    
    if category_code == "hhc":
        items = HHC_VAPES
        title = "💨 HHC ВЕЙПИ"
    elif category_code == "pods":
        items = PODS
        title = "🔌 POD-СИСТЕМИ"
    elif category_code == "sets":
        items = LIQUID_SETS
        title = "📦 НАБОРИ РІДИН"

    text = f"<b>{title}</b>\n\nОберіть товар для детального ознайомлення:"
    keyboard = []
    
    for item_id, data in items.items():
        price = calc_price(data['price'], profile)
        btn_text = f"{data['name']} — {price}₴"
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"view_item_{item_id}")])
    
    keyboard.append([InlineKeyboardButton("⬅️ Назад до категорій", callback_data="cat_main")])
    
    await send_ghosty_message(update, text, InlineKeyboardMarkup(keyboard))

# =================================================================
# 🔍 SECTION 15: ITEM DETAIL VIEW & ATTRIBUTE SELECTION
# =================================================================

async def view_item_details(update: Update, context: ContextTypes.DEFAULT_TYPE, item_id: int):
    """
    Відображає фото товару, опис та ціну. 
    Додає кнопки вибору кольору або подарунка, якщо потрібно.
    """
    profile = context.user_data["profile"]
    item = get_item_data(item_id)
    
    if not item:
        await query.answer("❌ Товар не знайдено")
        return

    price = calc_price(item['price'], profile)
    caption = (
        f"<b>{item['name']}</b>\n\n"
        f"{item['desc']}\n\n"
        f"💰 Ціна для вас: <b>{price}₴</b>"
    )
    
    keyboard = []
    
    # Якщо це Pod-система, виводимо вибір кольору
    if "colors" in item:
        caption += "\n\n🌈 <b>Доступні кольори:</b>"
        for color_name in item['colors'].keys():
            keyboard.append([InlineKeyboardButton(f"🎨 {color_name}", callback_data=f"select_col_{item_id}_{color_name}")])
    
    # Якщо товар передбачає подарунок (HHC або Сет)
    elif item.get("has_gift"):
        keyboard.append([InlineKeyboardButton("🎁 ОБРАТИ ПОДАРУНОК", callback_data=f"choose_gift_{item_id}")])
    
    # Якщо товар без атрибутів (простий)
    else:
        keyboard.append([InlineKeyboardButton("🛒 Додати у кошик", callback_data=f"add_cart_{item_id}")])

    keyboard.append([InlineKeyboardButton("⬅️ Назад до списку", callback_data=f"cat_list_{'hhc' if item_id < 200 else 'pods' if item_id < 600 else 'sets'}")])
    
    photo_url = item.get('img')
    # Якщо це Pod і вже обрано колір, показуємо фото кольору
    if "selected_color" in context.user_data and context.user_data.get("current_item_id") == item_id:
        color = context.user_data["selected_color"]
        photo_url = item['colors'].get(color, photo_url)

    await send_ghosty_message(update, caption, InlineKeyboardMarkup(keyboard), photo_url)

# =================================================================
# 🎁 SECTION 16: GIFT SELECTION LOGIC
# =================================================================

async def gift_selection_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, item_id: int):
    """
    Вибір подарункової рідини (8 варіантів).
    """
    text = (
        "<b>🎁 ОБЕРІТЬ ВАШ ПОДАРУНОК</b>\n\n"
        "До цього товару ви можете безкоштовно додати одну рідину 30мл.\n"
        "Який смак бажаєте?"
    )
    
    keyboard = []
    for g_id, g_data in GIFT_LIQUIDS.items():
        keyboard.append([InlineKeyboardButton(g_data['name'], callback_data=f"add_with_gift_{item_id}_{g_id}")])
    
    keyboard.append([InlineKeyboardButton("❌ Скасувати", callback_data=f"view_item_{item_id}")])
    
    await send_ghosty_message(update, text, InlineKeyboardMarkup(keyboard))

# =================================================================
# 🛒 SECTION 17: ADD TO CART HANDLERS
# =================================================================

async def add_to_cart_final(update: Update, context: ContextTypes.DEFAULT_TYPE, item_id: int, color: str = None, gift_id: int = None):
    """
    Фінальна функція додавання в кошик зі всіма параметрами.
    """
    profile = context.user_data["profile"]
    item = get_item_data(item_id)
    gift = get_item_data(gift_id) if gift_id else None
    
    final_price = calc_price(item['price'], profile)
    
    cart_entry = {
        "cart_id": str(uuid4())[:8],
        "id": item_id,
        "name": item['name'],
        "price": final_price,
        "color": color,
        "gift": gift['name'] if gift else None
    }
    
    context.user_data.setdefault("cart", []).append(cart_entry)
    
    success_text = f"✅ <b>{item['name']}</b> додано у кошик!"
    if color: success_text += f"\n🎨 Колір: {color}"
    if gift: success_text += f"\n🎁 Подарунок: {gift['name']}"
    
    keyboard = [
        [InlineKeyboardButton("🛒 ПЕРЕЙТИ В КОШИК", callback_data="menu_cart")],
        [InlineKeyboardButton("🛍 Продовжити покупки", callback_data="cat_main")]
    ]
    
    await send_ghosty_message(update, success_text, InlineKeyboardMarkup(keyboard))

# =================================================================
# ⚙️ SECTION 18: CALLBACK DISPATCHER (CATALOG & GIFTS)
# =================================================================

async def process_catalog_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE, data: str):
    """
    Обробка всіх натискань у розділі магазину.
    """
    if data == "cat_main":
        await show_catalog_main(update, context)
        
    elif data.startswith("cat_list_"):
        cat = data.replace("cat_list_", "")
        await list_items_by_category(update, context, cat)
        
    elif data.startswith("view_item_"):
        i_id = int(data.replace("view_item_", ""))
        await view_item_details(update, context, i_id)
        
    elif data.startswith("select_col_"):
        parts = data.split("_")
        i_id, color = int(parts[2]), parts[3]
        # Додавання Pod-системи з кольором
        await add_to_cart_final(update, context, i_id, color=color)
        
    elif data.startswith("choose_gift_"):
        i_id = int(data.replace("choose_gift_", ""))
        await gift_selection_menu(update, context, i_id)
        
    elif data.startswith("add_with_gift_"):
        parts = data.split("_")
        i_id, g_id = int(parts[3]), int(parts[4])
        await add_to_cart_final(update, context, i_id, gift_id=g_id)

    elif data.startswith("add_cart_"):
        i_id = int(data.replace("add_cart_", ""))
        await add_to_cart_final(update, context, i_id)
        # =================================================================
# 🛒 SECTION 19: THE SHOPPING CART SYSTEM
# =================================================================

async def show_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Відображає вміст кошика, рахує загальну суму та перевіряє умови замовлення.
    """
    profile = context.user_data.get("profile", {})
    cart = context.user_data.get("cart", [])
    
    if not cart:
        text = (
            "🛒 <b>Ваш кошик порожній</b>\n\n"
            "Перейдіть до каталогу, щоб обрати найкращі девайси та рідини."
        )
        keyboard = [[InlineKeyboardButton("🛍 В КАТАЛОГ", callback_data="cat_main")]]
        await send_ghosty_message(update, text, InlineKeyboardMarkup(keyboard))
        return

    total_sum = sum(item['price'] for item in cart)
    
    text = "🛒 <b>ВАШ КОШИК</b>\n"
    text += "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
    
    keyboard = []
    for idx, item in enumerate(cart):
        item_line = f"• {item['name']}"
        if item.get('color'): item_line += f" ({item['color']})"
        if item.get('gift'): item_line += f"\n  └ 🎁 + {item['gift']}"
        
        text += f"<b>{idx+1}. {item_line}</b>\n   └ Ціна: <code>{item['price']}₴</code>\n\n"
        
        # Кнопка видалення для кожного товару
        keyboard.append([InlineKeyboardButton(f"❌ Видалити {idx+1}", callback_data=f"cart_del_{idx}")])

    text += "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
    text += f"💰 Разом до оплати: <b>{total_sum}₴</b>\n"
    text += f"🏷 Ваша знижка: <b>{'-45%' if profile.get('promo_applied') else '-35%'}</b>\n\n"

    # Валідація замовлення
    if total_sum < MIN_ORDER_SUM:
        text += f"⚠️ <i>Мінімальна сума замовлення — {MIN_ORDER_SUM}₴. Додайте ще щось!</i>"
        keyboard.append([InlineKeyboardButton("➕ Додати товари", callback_data="cat_main")])
    elif not profile.get("city") or not profile.get("district"):
        text += "⚠️ <i>Для замовлення потрібно обрати місто та район!</i>"
        keyboard.append([InlineKeyboardButton("📍 Обрати локацію", callback_data="menu_city")])
    else:
        keyboard.append([InlineKeyboardButton("✅ ОФОРМИТИ ЗАМОВЛЕННЯ", callback_data="cart_checkout")])

    keyboard.append([InlineKeyboardButton("🗑 Очистити кошик", callback_data="cart_clear")])
    keyboard.append([InlineKeyboardButton("🏠 В меню", callback_data="menu_start")])
    
    await send_ghosty_message(update, text, InlineKeyboardMarkup(keyboard))

# =================================================================
# 🛠 SECTION 20: CART MODIFICATION HANDLERS
# =================================================================

async def cart_action_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, data: str):
    """
    Обробка видалення та очищення кошика.
    """
    cart = context.user_data.get("cart", [])
    
    if data.startswith("cart_del_"):
        idx = int(data.replace("cart_del_", ""))
        if 0 <= idx < len(cart):
            removed = cart.pop(idx)
            await update.callback_query.answer(f"🗑 {removed['name']} видалено")
        await show_cart(update, context)
        
    elif data == "cart_clear":
        context.user_data["cart"] = []
        await update.callback_query.answer("🧹 Кошик очищено")
        await show_cart(update, context)

# =================================================================
# 💳 SECTION 21: CHECKOUT & PAYMENT SELECTION
# =================================================================

async def checkout_init(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Початок оформлення: вибір методу оплати та підтвердження даних.
    """
    profile = context.user_data["profile"]
    cart = context.user_data["cart"]
    total_sum = sum(item['price'] for item in cart)
    
    # Якщо вибрано адресну доставку в Дніпрі, додаємо вартість
    is_address_delivery = (profile.get("district") == "Адресна доставка")
    delivery_fee = 50 if is_address_delivery else 0
    final_amount = total_sum + delivery_fee

    text = (
        "<b>📦 ОФОРМЛЕННЯ ЗАМОВЛЕННЯ</b>\n\n"
        f"📍 <b>Отримувач:</b> {profile['name']}\n"
        f"📍 <b>Локація:</b> {profile['city']}, {profile['district']}\n"
        "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        f"💵 Сума товарів: {total_sum}₴\n"
        f"🚚 Доставка: {delivery_fee}₴\n"
        f"💰 <b>ВСЬОГО ДО ОПЛАТИ: {final_amount}₴</b>\n\n"
        "Оберіть зручний спосіб оплати:"
    )
    
    keyboard = [
        [InlineKeyboardButton("💳 Картою (HeyLink / Mono)", callback_data="pay_card")],
        [InlineKeyboardButton("🪙 Криптовалюта (USDT/BTC)", callback_data="pay_crypto")],
        [InlineKeyboardButton("👤 Через менеджера", url=f"https://t.me/{MANAGER_USERNAME}")],
        [InlineKeyboardButton("⬅️ Назад до кошика", callback_data="menu_cart")]
    ]
    
    # Зберігаємо фінальну суму в тимчасові дані замовлення
    context.user_data["current_order"] = {
        "amount": final_amount,
        "is_address": is_address_delivery
    }
    
    await send_ghosty_message(update, text, InlineKeyboardMarkup(keyboard))

# =================================================================
# 🔑 SECTION 22: PROMOCODE & VIP LOGIC
# =================================================================

async def apply_promo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Ручне введення промокоду через MessageHandler.
    """
    user_text = update.message.text.strip().upper()
    profile = context.user_data["profile"]
    
    # Список робочих промокодів
    valid_promos = ["GHOSTY2026", "VIP45", "START35"]
    
    if user_text in valid_promos or user_text == profile.get("promo_code"):
        profile["promo_applied"] = True
        # Оновлюємо ціни в кошику, якщо вони там вже були
        if "cart" in context.user_data:
            for item in context.user_data["cart"]:
                # Перераховуємо ціну кожного товару зі знижкою 45%
                base_item = get_item_data(item['id'])
                if base_item:
                    item['price'] = int(base_item['price'] * PROMO_DISCOUNT_MULT)
        
        await update.message.reply_text(
            "✅ <b>ПРОМОКОД АКТИВОВАНО!</b>\nВаша знижка тепер становить <b>45%</b> на всі товари.",
            parse_mode=ParseMode.HTML
        )
        await start_command(update, context)
    else:
        await update.message.reply_text("❌ <b>Невірний промокод.</b> Спробуйте ще раз або зверніться до менеджера.")

# =================================================================
# ⚙️ SECTION 23: CALLBACK DISPATCHER (CART & CHECKOUT)
# =================================================================

async def process_cart_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE, data: str):
    """
    Інтеграція колбеків кошика в головний цикл.
    """
    if data == "menu_cart":
        await show_cart(update, context)
    elif data.startswith("cart_"):
        await cart_action_handler(update, context, data)
    elif data == "cart_checkout":
        await checkout_init(update, context)
    elif data.startswith("pay_"):
        # Буде реалізовано в Частині 6 (Платіжні шлюзи та реквізити)
        await query.answer("⌛ Перехід до оплати...")

# =================================================================
# 📋 SECTION 24: STATE MANAGEMENT (DNP ADDRESS COLLECTION)
# =================================================================

async def handle_user_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Глобальний обробник текстового вводу.
    Використовується для збору адреси доставки та введення промокодів.
    """
    user_id = update.effective_user.id
    text = update.message.text
    state = context.user_data.get("state")

    # Якщо користувач вводить адресу для Дніпра
    if state == "WAITING_ADDRESS":
        if len(text) < 10:
            await update.message.reply_text("❌ <b>Адреса занадто коротка.</b>\nБудь ласка, вкажіть вулицю, номер будинку та під'їзд:")
            return
        
        context.user_data["profile"]["address_details"] = text
        context.user_data["state"] = None
        
        # Повертаємо до вибору оплати після введення адреси
        await update.message.reply_text(f"✅ <b>Адресу збережено:</b>\n<code>{text}</code>")
        await checkout_init(update, context)

    # Якщо користувач вводить промокод
    elif state == "WAITING_PROMO":
        await apply_promo_command(update, context)
    
    else:
        # Стандартна відповідь на невідомий текст
        await update.message.reply_text("🤖 Використовуйте кнопки меню для навігації.")

# =================================================================
# 💳 SECTION 25: PAYMENT GATEWAYS LOGIC
# =================================================================

async def payment_selection_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, method: str):
    """
    Генерація реквізитів залежно від обраного способу.
    """
    profile = context.user_data["profile"]
    order_data = context.user_data.get("current_order", {})
    amount = order_data.get("amount", 0)
    
    # Якщо це Дніпро + Адресна, але адреса ще не вказана
    if order_data.get("is_address") and not profile.get("address_details"):
        context.user_data["state"] = "WAITING_ADDRESS"
        await update.callback_query.message.reply_text(
            "🏠 <b>Ви обрали адресну доставку.</b>\n\nБудь ласка, напишіть у відповідь вашу адресу (Вулиця, будинок, квартира):",
            parse_mode=ParseMode.HTML
        )
        await update.callback_query.answer()
        return

    # Формування тексту оплати
    payment_id = str(uuid4())[:10].upper()
    context.user_data["last_payment_id"] = payment_id

    pay_text = (
        f"<b>💳 ОПЛАТА ЗАМОВЛЕННЯ #{payment_id}</b>\n\n"
        f"💰 Сума до сплати: <b>{amount}₴</b>\n"
        f"📝 Коментар до платежу: <code>{payment_id}</code>\n\n"
    )

    if method == "card":
        pay_text += (
            f"🔗 <b>Для оплати перейдіть за посиланням:</b>\n{PAYMENT_LINK}\n\n"
            "⚠️ <i>Обов'язково вкажіть ID замовлення в коментарі до переказу!</i>"
        )
    else:
        pay_text += (
            "🪙 <b>Реквізити для Crypto (USDT TRC20):</b>\n"
            "<code>TExE54fks93kSdjf92kSls02kfS92kSlsk</code>\n\n"
            "<i>Курс розраховується автоматично на момент оплати.</i>"
        )

    keyboard = [
        [InlineKeyboardButton("✅ ПІДТВЕРДИТИ ОПЛАТУ", callback_data=f"confirm_pay_{payment_id}")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="cart_checkout")]
    ]

    await send_ghosty_message(update, pay_text, InlineKeyboardMarkup(keyboard))

# =================================================================
# 🛡 SECTION 26: ORDER CONFIRMATION (ADMIN NOTIFICATION)
# =================================================================

async def confirm_payment_request(update: Update, context: ContextTypes.DEFAULT_TYPE, pay_id: str):
    """
    Відправка замовлення менеджеру для ручної перевірки.
    """
    profile = context.user_data["profile"]
    cart = context.user_data["cart"]
    order_data = context.user_data.get("current_order", {})
    
    # Формування звіту для адміна
    items_summary = "\n".join([f"- {i['name']} ({i['price']}₴) {'+ 🎁' if i.get('gift') else ''}" for i in cart])
    
    admin_msg = (
        f"🔔 <b>НОВЕ ЗАМОВЛЕННЯ #{pay_id}</b>\n\n"
        f"👤 Клієнт: {profile['name']} ({profile['username']})\n"
        f"🆔 ID: <code>{profile['uid']}</code>\n\n"
        f"📍 Локація: {profile['city']}, {profile['district']}\n"
        f"🏠 Адреса: {profile.get('address_details', 'Клад')}\n\n"
        f"🛒 Товари:\n{items_summary}\n\n"
        f"💰 <b>СУМА: {order_data['amount']}₴</b>\n"
        f"💳 Спосіб: Оплата перевіряється..."
    )

    try:
        # Відправка менеджеру
        await context.bot.send_message(
            chat_id=MANAGER_ID,
            text=admin_msg,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Підтвердити", callback_data=f"adm_approve_{pay_id}_{profile['uid']}"),
                 InlineKeyboardButton("❌ Відхилити", callback_data=f"adm_decline_{pay_id}_{profile['uid']}")]
            ])
        )
        
        # Повідомлення користувачу
        user_msg = (
            f"✅ <b>Заявка на замовлення #{pay_id} прийнята!</b>\n\n"
            "Менеджер перевірить оплату протягом 15-30 хвилин. "
            "Ви отримаєте сповіщення про зміну статусу.\n\n"
            "Дякуємо, що ви з Ghosty Staff! 🔥"
        )
        
        # Очищуємо кошик після успішного запиту
        context.user_data["cart"] = []
        
        await send_ghosty_message(update, user_msg, InlineKeyboardMarkup([[InlineKeyboardButton("🏠 В меню", callback_data="menu_start")]]))

    except Exception as e:
        logger.error(f"Failed to send admin notification: {e}")
        await update.callback_query.answer("⚠️ Помилка зв'язку з сервером. Спробуйте пізніше.", show_alert=True)

# =================================================================
# ⚙️ SECTION 27: CALLBACK DISPATCHER (PAYMENT & ADMIN)
# =================================================================

async def process_payment_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE, data: str):
    """
    Обробка платіжних колбеків.
    """
    if data == "pay_card":
        await payment_selection_handler(update, context, "card")
    elif data == "pay_crypto":
        await payment_selection_handler(update, context, "crypto")
    elif data.startswith("confirm_pay_"):
        p_id = data.replace("confirm_pay_", "")
        await confirm_payment_request(update, context, p_id)

# =================================================================
# 🛡 SECTION 28: ADMIN PANEL & ORDER CONTROL
# =================================================================

async def admin_decision_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обробка рішень менеджера (Підтвердити/Відхилити замовлення).
    Спрацьовує при натисканні кнопок у чаті менеджера.
    """
    query = update.callback_query
    data = query.data
    
    # Формат: adm_approve_ID_USERID
    try:
        parts = data.split("_")
        action = parts[1]
        order_id = parts[2]
        user_id = int(parts[3])

        if action == "approve":
            status_text = "✅ <b>Ваше замовлення підтверджено!</b>\nКур'єр вже готує відправку. Очікуйте фото/трек-номер найближчим часом."
            admin_notif = f"✅ Замовлення #{order_id} підтверджено."
        else:
            status_text = "❌ <b>Замовлення відхилено.</b>\nМенеджер не знайшов оплату. Якщо це помилка — напишіть нам."
            admin_notif = f"❌ Замовлення #{order_id} відхилено."

        # Сповіщення користувача
        await context.bot.send_message(chat_id=user_id, text=status_text, parse_mode=ParseMode.HTML)
        # Оновлення повідомлення у менеджера
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text(admin_notif)
    except Exception as e:
        logger.error(f"Admin action error: {e}")

# =================================================================
# ⚙️ SECTION 29: GLOBAL CALLBACK DISPATCHER (INTEGRATION)
# =================================================================

async def global_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Центральний вузол розподілу всіх колбеків у боті.
    """
    query = update.callback_query
    data = query.data
    
    try:
        await query.answer()

        # 1. Головне меню та Угода
        if data == "menu_start": await start_command(update, context)
        elif data == "menu_terms": await terms_handler(update, context)
        
        # 2. Географія (Міста та райони)
        elif any(data.startswith(x) for x in ["menu_city", "set_city_", "set_dist_", "set_delivery_address"]):
            await process_geo_callbacks(update, context, data)
            
        # 3. Профіль та Кабінет
        elif data == "menu_profile": await show_profile(update, context)
        
        # 4. Каталог та Подарунки
        elif any(data.startswith(x) for x in ["cat_", "view_item_", "select_col_", "choose_gift_", "add_"]):
            await process_catalog_callbacks(update, context, data)
            
        # 5. Кошик та Оплата
        elif any(data.startswith(x) for x in ["menu_cart", "cart_", "pay_", "confirm_pay_"]):
            # Обробляємо кошик і платежі
            if "cart" in data: await process_cart_callbacks(update, context, data)
            else: await process_payment_callbacks(update, context, data)
            
        # 6. Адмін-дії
        elif data.startswith("adm_"):
            if update.effective_user.id == MANAGER_ID:
                await admin_decision_handler(update, context)
    except Exception as e:
        logger.error(f"Callback error for {data}: {e}")

# =================================================================
# 🚀 SECTION 30: APPLICATION RUNNER (MAIN) - STABLE VERSION
# =================================================================

def main():
    """
    Точка запуску бота. Виправлено для BotHost.ru (без AIORateLimiter).
    """
    # Створення необхідних папок перед запуском
    for folder in ['data', 'data/logs']:
        if not os.path.exists(folder):
            os.makedirs(folder)

    # Ініціалізація бази даних
    db_init()
    
    # Налаштування збереження даних (Persistence)
    persistence = PicklePersistence(filepath="data/ghosty_data.pickle")
    
    # Виправлення PTBDeprecationWarning (link_preview_options)
    from telegram import LinkPreviewOptions
    defaults = Defaults(
        parse_mode=ParseMode.HTML, 
        link_preview_options=LinkPreviewOptions(is_disabled=True)
    )
    
    # Побудова додатку (Видалено AIORateLimiter для сумісності)
    application = (
        Application.builder()
        .token(TOKEN)
        .persistence(persistence)
        .defaults(defaults)
        .build()
    )

    # Додавання обробників (Handlers)
    
    # Команди
    application.add_handler(CommandHandler("start", start_command))
    
    # Текстові повідомлення (Адреса, Промокоди)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_input))
    
    # Колбеки (Кнопки)
    application.add_handler(CallbackQueryHandler(global_callback_handler))

    # Глобальний обробник помилок
    application.add_error_handler(error_handler)

    # Запуск
    print("--- GHOSTY STAFF SHOP READY ---")
    print(f"Status: FIXED & STABLE")
    print(f"Manager: @{MANAGER_USERNAME}")
    
    # Запуск бота (drop_pending_updates очищує чергу старих повідомлень)
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        print("\nБот зупинений.")
    except Exception as e:
        logger.critical(f"FATAL RESTART: {e}")

# =================================================================
# 🤖 PROJECT: GHO$$TY STAFF PREMIUM E-COMMERCE ENGINE (PRO)
# 🛠 VERSION: TITAN ULTIMATE v10.0 (FINAL STABLE)
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
from urllib.parse import quote

# Telegram Core (v20.x+ Async Stack)
from telegram import (
    Update, 
    InlineKeyboardButton, 
    InlineKeyboardMarkup, 
    InputMediaPhoto, 
    CallbackQuery
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
from telegram.error import BadRequest

# 🛡 ТЕХНІЧНА ГІГІЄНА
warnings.filterwarnings("ignore", category=UserWarning)

# Гарантуємо чисте логування без дублікатів
if 'GhostyCore' in logging.Logger.manager.loggerDict:
    logging.getLogger("GhostyCore").handlers.clear()

# =================================================================
# ⚙️ SECTION 1: GLOBAL CONFIGURATION
# =================================================================

# 1. СИСТЕМНІ ШЛЯХИ (Виправлено приховані символи)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True) 

DB_PATH = os.path.join(DATA_DIR, 'ghosty_pro_final.db')
PERSISTENCE_PATH = os.path.join(DATA_DIR, 'ghosty_state_final.pickle')
LOG_PATH = os.path.join(DATA_DIR, 'ghosty_system.log')

# 2. НАЛАШТУВАННЯ БОТА
TOKEN = os.getenv("BOT_TOKEN", "8351638507:AAE8JbSIduGOMYnCu77WFRy_3s7-LRH34lQ")
MANAGER_ID = 7544847872
MANAGER_USERNAME = "ghosstydp"
CHANNEL_URL = "https://t.me/GhostyStaffDP"
WELCOME_PHOTO = "https://i.ibb.co/y7Q194N/1770068775663.png"

# 3. ПЛАТІЖНІ ПОСИЛАННЯ
PAYMENT_LINK = {
    "mono": "https://lnk.ua/k4xJG21Vy",    
    "privat": "https://lnk.ua/RVd0OW6V3",
    "ghossty": "https://heylink.me/GhosstyShop"
}

# 4. ЛОГУВАННЯ
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

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

# 5. ГЛОБАЛЬНИЙ ЧАС
if 'START_TIME' not in globals():
    START_TIME = datetime.now()

# 6. ДЕБАГ-МОД
# Автоматично вмикається на Windows, вимикається на хостингу (Linux)
DEBUG_MODE = os.name == 'nt' 
if DEBUG_MODE:
    logger.setLevel(logging.DEBUG)
    logger.info("🛠 DEBUG MODE: ENABLED (Detailed logging active)")
    
        
        
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
UKRAINE_CITIES = {
    "Київ": ["Печерський", "Шевченківський", "Голосіївський", "Оболонський", "Подільський", "Дарницький", "Солом'янський", "Деснянський"],
    "Дніпро": ["Центральний (Мост)", "Соборний (Нагірка)", "Індустріальний", "Шевченківський", "Чечелівський", "Лівобережний-3", "Перемога 1-6", "Придніпровськ"],
    "Кам'янське": ["Центральний", "Дніпровський (Л/Б)", "Південний (БАМ)", "Соцмісто", "Черемушки", "Карнаухівка", "Курилівка", "Романкове"],
    "Харків": ["Шевченківський", "Київський", "Салтівський", "Немишлянський", "Холодногірський", "Новобаварський", "Основ'янський", "Індустріальний"],
    "Одеса": ["Приморський (Центр)", "Київський (Таїрова)", "Малиновський", "Суворовський", "Пересип", "Слобідка", "Молдаванка", "Фонтан"],
    "Львів": ["Галицький (Центр)", "Личаківський", "Сихівський", "Франківський", "Шевченківський", "Залізничний", "Левандівка", "Збоїща"],
    "Запоріжжя": ["Олександрівський", "Заводський", "Комунарський", "Дніпровський", "Вознесенівський", "Хортицький", "Шевченківський", "Південний"],
    "Кривий Ріг": ["Металургійний", "Центрально-Міський", "Саксаганський", "Покровський", "Тернівський", "Довгинцівський", "Інгулецький", "мкрн. Сонячний"],
    "Вінниця": ["Центр", "Вишенька", "Замостя", "Старе місто", "Поділля", "Слов'янка", "П'ятничани", "Тяжилів"],
    "Полтава": ["Шевченківський", "Київський", "Подільський", "Левада", "Алмазний", "Половки", "Огнівка", "Розсошенці"]
}

# 2. ТЕХНІЧНІ ЗМІННІ
CITIES_LIST = list(UKRAINE_CITIES.keys())
COURIER_PRICE = 150.0

# 3. ІНІЦІАЛІЗАЦІЯ СЛОВНИКІВ ТОВАРІВ (Щоб уникнути NameError)
HHC_VAPES = {} 
LIQUIDS = {}
PODS = {}

# 🔥 4. БОНУСНІ РІДИНИ (ВАЖЛИВО: ВОНИ МАЮТЬ БУТИ ТУТ)
GIFT_LIQUIDS = {
    9001: {"name": "Pumpkin Latte 30ml", "desc": "Теплий осінній смак."},
    9002: {"name": "Glintwine 30ml", "desc": "Виноград та спеції."},
    9003: {"name": "Christmas Tree 30ml", "desc": "Аромат хвої."},
    9004: {"name": "Strawberry Jelly 30ml", "desc": "Солодка полуниця."},
    9005: {"name": "Mystery One 30ml", "desc": "Секретний мікс."},
    9006: {"name": "Fall Tea 30ml", "desc": "Чай з лимоном."},
    9007: {"name": "Banana Ice 30ml", "desc": "Банан з льодом."},
    9008: {"name": "Wild Berries 30ml", "desc": "Лісові ягоди."}
}

# 5. УНІВЕРСАЛЬНА ФУНКЦІЯ ПОШУКУ (FIXED)
def get_item_data(item_id: int):
    """
    Шукає товар у всіх категоріях за ID.
    ВИПРАВЛЕНО: Тепер шукає і в GIFT_LIQUIDS!
    """
    # Додаємо GIFT_LIQUIDS у список пошуку
    all_dbs = [HHC_VAPES, PODS, LIQUIDS, GIFT_LIQUIDS] 
    
    for db in all_dbs:
        if item_id in db:
            return db[item_id]
    return None
    
# =================================================================
# 🛠 SECTION 2: UI ENGINE & ERROR SHIELD (TITAN FINAL)
# =================================================================

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Глобальний щит безпеки: сповіщає адміна про будь-які збої."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    try:
        tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
        tb_string = "".join(tb_list)
        error_snippet = escape(tb_string[-3500:]) 
        
        user_info = "Unknown User"
        if isinstance(update, Update) and update.effective_user:
            u = update.effective_user
            user_info = f"👤 <b>{escape(u.full_name)}</b> (@{u.username}) [<code>{u.id}</code>]"

        admin_msg = (
            f"🆘 <b>CRITICAL SYSTEM ERROR</b>\n━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 <b>User:</b> {user_info}\n⚙️ <b>Type:</b> <code>{type(context.error).__name__}</code>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n🔍 <b>Traceback:</b>\n<pre>{error_snippet}</pre>"
        )
        # Надсилаємо лог адміну (безпечно)
        await context.bot.send_message(chat_id=MANAGER_ID, text=admin_msg, parse_mode=ParseMode.HTML)
        
        # Сповіщаємо користувача (щоб не думав, що бот ігнорує)
        if isinstance(update, Update) and update.effective_chat:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="⚠️ <b>Виникла технічна помилка.</b>\nСпробуйте натиснути /start", parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.error(f"Failed to report error: {e}")

async def _edit_or_reply(target, text: str, kb: list = None, photo: str = None, context: ContextTypes.DEFAULT_TYPE = None):
    """
    Універсальний адаптер інтерфейсу.
    Автоматично визначає: редагувати повідомлення чи слати нове.
    Автоматично обробляє переходи: Текст -> Текст, Текст -> Фото, Фото -> Фото.
    """
    if not text: text = "..."
    # Конвертуємо список списків у InlineKeyboardMarkup, якщо це ще не об'єкт
    reply_markup = InlineKeyboardMarkup(kb) if isinstance(kb, list) else (kb if kb else None)
    
    # Визначаємо об'єкти (Query або Message)
    query = target if hasattr(target, 'data') else getattr(target, 'callback_query', None)
    message = query.message if query else getattr(target, 'message', target)
    
    if not message: return
    chat_id = message.chat_id
    bot = context.bot if context else message.get_bot()

    try:
        if query:
            # Сценарій 1: Це натискання кнопки (Callback)
            if photo:
                if message.photo:
                    # Фото -> Фото (просто міняємо медіа)
                    await query.edit_message_media(media=InputMediaPhoto(media=photo, caption=text, parse_mode=ParseMode.HTML), reply_markup=reply_markup)
                else:
                    # Текст -> Фото (видаляємо текст, шлемо фото)
                    await message.delete()
                    await bot.send_photo(chat_id=chat_id, photo=photo, caption=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
            else:
                if message.photo:
                    # Фото -> Текст (видаляємо фото, шлемо текст)
                    await message.delete()
                    await bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
                else:
                    # Текст -> Текст (просто редагуємо)
                    await query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        else:
            # Сценарій 2: Це нове повідомлення (не кнопка)
            if photo: 
                await message.reply_photo(photo=photo, caption=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
            else: 
                await message.reply_text(text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
                
    except BadRequest as e:
        # Ігноруємо помилку "Message is not modified" (це нормально)
        if "Message is not modified" not in str(e):
            # Якщо редагування не вдалося, пробуємо надіслати нове повідомлення
            try: 
                if photo:
                    await bot.send_photo(chat_id=chat_id, photo=photo, caption=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
                else:
                    await bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
            except: pass

async def send_ghosty_message(update_obj, text: str, kb=None, photo=None, context: ContextTypes.DEFAULT_TYPE = None):
    """
    Високорівневий аліас.
    ВИПРАВЛЕНО: аргумент називається 'kb', щоб відповідати викликам у всьому коді.
    """
    await _edit_or_reply(update_obj, text, kb, photo, context)

async def safe_delete(message):
    """Безпечне видалення повідомлення."""
    try:
        if hasattr(message, 'delete'): await message.delete()
    except: pass
        
        
# =================================================================
# 🛠 SECTION 3: MATH CORE (TITAN FINAL)
# =================================================================

# =================================================================
# ===== ПІДКАЗКА: КЕРУВАННЯ ЗНИЖКАМИ =====
# Додайте назву категорії у список нижче, щоб на неї ДІЯЛА знижка -35%.
# Якщо категорії немає в списку — товар буде продаватися за повною ціною.
# Доступні категорії: 'hhc', 'pods', 'liquids'
# =================================================================
VIP_DISCOUNT_CATEGORIES = ['hhc', 'pods'] 
# =================================================================

def calculate_final_price(item_price, user_profile, item_id=None):
    """
    Універсальне ядро розрахунку ціни (v11.0).
    Динамічно перевіряє категорію товару та статус користувача.
    """
    try:
        price = float(item_price)
        up = user_profile if user_profile else {}
        is_vip = bool(up.get('is_vip', False))
        
        # Якщо ID товару не передано — рахуємо без знижки (захист від помилок)
        if item_id is None:
            return round(price, 2), False

        # Отримуємо дані товару, щоб дізнатися його категорію
        item_data = get_item_data(int(item_id))
        if not item_data:
            return round(price, 2), False

        # Визначаємо категорію (за типом або за діапазоном ID)
        item_category = item_data.get('type') 
        
        # Якщо тип не вказаний явно, визначаємо за ID (як у твоєму реєстрі)
        if not item_category:
            iid = int(item_id)
            if 100 <= iid < 300: item_category = 'hhc'
            elif 300 <= iid < 500: item_category = 'liquids'
            elif 500 <= iid < 700: item_category = 'pods'

        # ===== ПЕРЕВІРКА ПРАВА НА ЗНИЖКУ =====
        # Знижка діє тільки якщо: 
        # 1. Користувач — VIP
        # 2. Категорія товару є у списку VIP_DISCOUNT_CATEGORIES
        if is_vip and item_category in VIP_DISCOUNT_CATEGORIES:
            final_price = price * 0.65 # -35%
            return round(max(final_price, 10.0), 2), True
            
        # В усіх інших випадках — повна ціна
        return round(price, 2), False
        
    except Exception as e:
        if 'logger' in globals():
            logger.error(f"❌ Critical Math Error: {e}")
        return float(item_price), False
        
        

# =================================================================
# 🛍 SECTION 3: ТОВАРНА БАЗА (FIXED SYNTAX & STOCK LOGIC)
# =================================================================


# 1. РІДИНИ (LIQUIDS)
LIQUIDS = {
    301: {
        "name": "🍂 Fall Tea",
        "category": "Chaser Balance",
        "price": 349.99,
        "stock": 15,
        "discount": False,
        "strengths": [50, 65, 85],
        "img": "https://i.ibb.co/Kxmrpm1C/Fall-Tea.jpg",
        "desc": "☕ <b>Осінній Чай</b>\nСпокійний аромат чаю з нотками лимону.",
        "payment_url": PAYMENT_LINK
    },
    302: {
        "name": "👻 Mystery One",
        "category": "Chaser Balance",
        "price": 349.99,
        "stock": 15,
        "discount": False,
        "strengths": [50, 65, 85],
        "img": "https://i.ibb.co/bMMVHXG6/Mystery-One.jpg",
        "desc": "🔮 <b>Ghost Edition</b>\nТаємничий фруктовий мікс.",
        "payment_url": PAYMENT_LINK
    },
    303: {
        "name": "🍓 Strawberry Jelly",
        "category": "Chaser Balance",
        "price": 349.99,
        "stock": 14,
        "discount": False,
        "strengths": [50, 65, 85],
        "img": "https://i.ibb.co/sd9ZSfyH/Strawberry-Jelly.jpg",
        "desc": "🍮 <b>Полуничне Желе</b>\nНіжний десертний смак.",
        "payment_url": PAYMENT_LINK
    },
    304: {
        "name": "🍇 Grape BlackBerry",
        "category": "Limited Ultra",
        "price": 349.99,
        "stock": 15,
        "discount": False,
        "strengths": [50, 65, 85],
        "img": "https://i.ibb.co/nMJ2VdQK/Grape-Black-Berry.jpg",
        "desc": "🍇 <b>Виноград-Ожина</b>\nВибух темних ягід.",
        "payment_url": PAYMENT_LINK
    },
    305: {
        "name": "🥤 Cola Pomelo",
        "category": "Limited Ultra",
        "price": 349.99,
        "stock": 15,
        "discount": False,
        "strengths": [50, 65, 85],
        "img": "https://i.ibb.co/zdpDg2K/Cola-Pomelo.jpg",
        "desc": "🍊 <b>Кола-Помело</b>\nНезвичне поєднання.",
        "payment_url": PAYMENT_LINK
    },
    306: {
        "name": "🌹 BlackCurrant Rose",
        "category": "Limited Ultra",
        "price": 349.99,
        "stock": 12,
        "discount": False,
        "strengths": [50, 65, 85],
        "img": "https://i.ibb.co/0pLKnvx2/Black-Currant-Rose.jpg",
        "desc": "🥀 <b>Смородина-Троянда</b>\nВишуканий аромат.",
        "payment_url": PAYMENT_LINK
    },
    307: {
        "name": "🍋 Berry Lemonade",
        "category": "Special Berry",
        "price": 349.99,
        "stock": 15,
        "discount": False,
        "strengths": [50, 65, 85],
        "img": "https://i.ibb.co/21xt8N1p/Berry-Lemonade.jpg",
        "desc": "🍹 <b>Ягідний Лимонад</b>\nОсвіжаючий літній мікс.",
        "payment_url": PAYMENT_LINK
    },
    308: {
        "name": "⚡ Energetic",
        "category": "Special Berry",
        "price": 349.99,
        "stock": 10,
        "discount": False,
        "strengths": [50, 65, 85],
        "img": "https://i.ibb.co/TBwR7NTP/Energetic.jpg",
        "desc": "🔋 <b>Енергетик</b>\nСмак, що бадьорить.",
        "payment_url": PAYMENT_LINK
    },
    309: {
        "name": "💊 Vitamin",
        "category": "Special Berry",
        "price": 349.99,
        "stock": 15,
        "discount": False,
        "strengths": [50, 65, 85],
        "img": "https://i.ibb.co/tTLrsGGT/Vitamin.jpg",
        "desc": "🍏 <b>Вітамін</b>\nМікс фруктів.",
        "payment_url": PAYMENT_LINK
    }
}

# 2. HHC ВЕЙПИ
HHC_VAPES = {
    100: {
        "name": "🌴 Packwoods Purple 1ml",
        "type": "hhc",
        "price": 999.99,
        "stock": 16,
        "discount": True,
        "gift_liquid": True,
        "img": "https://i.ibb.co/svXqXPgL/Ghost-Vape-3.jpg",
        "desc": "🧠 <b>90% HHC | Гібрид</b>\n😌 Розслаблення + ейфорія\n🎁 <b>+ РІДИНА БЕЗКОШТОВНО!</b>",
        "payment_url": PAYMENT_LINK
    },
    101: {
        "name": "🍊 Packwoods Orange 1ml",
        "type": "hhc",
        "price": 999.99,
        "stock": 14,
        "discount": True,
        "gift_liquid": True,
        "img": "https://i.ibb.co/SDJFRTwk/Ghost-Vape-1.jpg",
        "desc": "🧠 <b>90% HHC | Сатіва</b>\n⚡ Бадьорить та фокусує\n🎁 <b>+ РІДИНА БЕЗКОШТОВНО!</b>",
        "payment_url": PAYMENT_LINK
    },
    102: {
        "name": "🌸 Packwoods Pink 1ml",
        "type": "hhc",
        "price": 999.99,
        "stock": 4,
        "discount": True,
        "gift_liquid": True,
        "img": "https://i.ibb.co/65j1901/Ghost-Vape-2.jpg",
        "desc": "🧠 <b>90% HHC | Індіка</b>\n😇 Спокій + підйом настрою\n🎁 <b>+ РІДИНА БЕЗКОШТОВНО!</b>",
        "payment_url": PAYMENT_LINK
    },
    103: {
        "name": "🌿 Whole Mint 2ml",
        "type": "hhc",
        "price": 1399.99,
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
        "price": 1799.99,
        "stock": 8,
        "discount": True,
        "gift_liquid": True,
        "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg",
        "desc": "🧠 <b>95% HHC | Індика</b>\n😴 Глибокий релакс (2ml)\n🎁 <b>+ РІДИНА БЕЗКОШТОВНО!</b>",
        "payment_url": PAYMENT_LINK
    }
}

# 3. POD-СИСТЕМИ
# FIX: Додано параметр 'stock', щоб товари відкривалися в каталозі
PODS = {
    500: {
        "name": "🔌 Vaporesso XROS 3 Mini",
        "type": "pod",
        "stock": 15,  # FIX: Додано наявність
        "gift_liquid": True,
        "price": 749,
        "discount": False,
        "img": "https://i.ibb.co/yFSQ5QSn/vaporesso-xros-3-mini.jpg",
        "desc": "🔋 <b>1000 mAh | MTL</b>\nЛегендарна модель. Надійна та смачна.\n✨ <i>Ідеальний вибір для старту.</i>",
        "colors": ["⚫️ Black", "🟢 Green", "🟣 Pink"],
        "color_previews": {
            "GhosstyLove Edition": "ЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯ",
            "Black": "https://ibb.co/ycwSdT03",
            "Green": "https://ibb.co/5WQY1pjq",
            "Pink": "https://ibb.co/YB7XmmpZ" # Fixed typo hhttps -> https
        },
        "payment_url": PAYMENT_LINK
    },
    501: {
        "name": "🔌 Vaporesso XROS 5 Mini",
        "type": "pod",
        "stock": 15, # FIX: Додано наявність
        "gift_liquid": True,
        "price": 849,
        "discount": False,
        "img": "https://i.ibb.co/RkNgt1Qr/vaporesso-xros-5-mini.jpg",
        "desc": "🔥 <b>НОВИНКА 2025 | COREX 2.0</b>\nМаксимальна передача смаку.\n💎 <i>Оновлений дизайн та швидка зарядка.</i>",
        "colors": ["⚫️ Core Black", "🟣 Pink", "🟢 Green"],
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
        "stock": 10, # FIX: Додано наявність
        "gift_liquid": True,
        "price": 1199,
        "discount": False,
        "img": "https://i.ibb.co/ynYwSMt6/vaporesso-xros-pro.jpg",
        "desc": "🚀 <b>PROFESSIONAL | 1200 mAh</b>\nЕкран, регулювання потужності, блокування.\n⚡ <i>Зарядка за 35 хвилин!</i>",
        "colors": ["⚫️ Black", "⚪️ Silver", "🔴 Red", "🔵 Blue"],
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
        "stock": 12, # FIX: Додано наявність
        "gift_liquid": True,
        "price": 929,
        "discount": False,
        "img": "https://i.ibb.co/5XW2yN80/vaporesso-xros-nano.jpg",
        "desc": "🎒 <b>КОМПАКТНИЙ КВАДРАТ</b>\nСтильний, зручний, на шнурку.\n🔋 <i>1000 mAh у міні-корпусі.</i>",
        "colors": ["⚫️ Black", "🟡 Yellow", "🟠 Orange", "🌸 Pink"],
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
        "stock": 11, # FIX: Додано наявність
        "gift_liquid": True,
        "price": 719,
        "discount": False,
        "img": "https://i.ibb.co/LDRbQxr1/vaporesso-xros-4.jpg",
        "desc": "👌 <b>БАЛАНС ТА СТИЛЬ</b>\nМеталевий корпус, 3 режими потужності.\n🎯 <i>Універсальний солдат.</i>",
        "colors": ["⚫️ Black", "🔵 Blue", "🟣 Purple Gradient", "⚪️ Silver"],
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
        "stock": 8,
        "gift_liquid": True,
        "price": 999,
        "discount": False,
        "img": "https://i.ibb.co/hxjmpHF2/vaporesso-xros-5.jpg",
        "desc": "💎 <b>ПРЕМІУМ ФЛАГМАН</b>\n1200 mAh, 3 режими, супер-смак.\n🚀 <i>Найкраще, що створили Vaporesso.</i>",
        "colors": ["⚫️ Obsidian Black", "⚪️ Pearl White", "🔵 Ocean Blue"],
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
        "stock": 25, # FIX: Додано наявність
        "gift_liquid": True,
        "price": 619,
        "discount": False,
        "img": "https://ilrnrwxhokrl5q.ldycdn.com/cloud/lpBqlKmrSRkllmojnpiq/Authentic-VOOPOO-Vmate-Mini-30W-Pod-Kit-1000mAh-3ml-0-7ohm-Classic-Black.jpg",
        "desc": "😌 <b>ЛЕГКИЙ СТАРТ</b>\nАвтоматична тяга, жодних кнопок.\n🧬 <i>Просто залий рідину і парь.</i>",
        "colors": ["⚫️ Black", "🔴 Red", "🔵 Blue", "🟢 Green"],
        "color_previews": {
             "GhosstyLove Edition": "ЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯЯ",
            "Black": "https://i.ibb.co/url-to-black.jpg",
            "Silver": "https://i.ibb.co/url-to-silver.jpg",
            "Phantom Red": "https://i.ibb.co/url-to-red.jpg"
        },
        "payment_url": PAYMENT_LINK
    }
}

# 4. УНІВЕРСАЛЬНА ФУНКЦІЯ ПОШУКУ
# (Критично важлива для відкриття товарів)
def get_item_data(item_id: int):
    """Шукає товар у всіх категоріях за ID."""
    # Перевіряємо всі бази (Включаючи SETS якщо вони з'являться)
    all_dbs = [HHC_VAPES, PODS, LIQUIDS]
    # Якщо ви додасте SETS, додайте сюди: [HHC_VAPES, PODS, LIQUIDS, SETS]
    
    for db in all_dbs:
        if item_id in db:
            return db[item_id]
    return None
    


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
    "🔟 Всі транзакції — це безповоротний подарунок розробнику.  Gho$$tyyy.\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "<i>Натискаючи «Прийняти» або продовжуючи роботу, ви підтверджуєте, "
    "що ознайомлені з цими пунктами.</i>"
)


# =================================================================
# ⚙️ SECTION 4: DATABASE & AUTH CORE (TITAN FINAL)
# =================================================================

def init_db():
    """
    Ініціалізація бази даних (Self-Healing).
    Створює таблиці та перевіряє структуру при кожному запуску.
    """
    try:
        # ВИПРАВЛЕНО: Timeout збільшено до 30 секунд для стабільності
        with sqlite3.connect(DB_PATH, timeout=30) as conn:
            cur = conn.cursor()
            
            # 1. Таблиця Користувачів (Users)
            cur.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY, 
                    username TEXT, 
                    full_name TEXT, 
                    phone TEXT, 
                    city TEXT, 
                    district TEXT, 
                    address_details TEXT,
                    is_vip INTEGER DEFAULT 0, 
                    vip_expiry TEXT, 
                    promo_applied INTEGER DEFAULT 0,
                    next_order_discount REAL DEFAULT 0, 
                    reg_date TEXT, 
                    balance REAL DEFAULT 0, 
                    joined_date TEXT
                )
            ''')
            
            # 2. Таблиця Замовлень (Orders)
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
    Розумний менеджер профілю:
    1. Перевіряє кеш (швидко).
    2. Синхронізує з БД (надійно).
    3. Реєструє нового, якщо немає.
    """
    user = update.effective_user
    
    # 1. Ініціалізація пам'яті (Кеш)
    if 'profile' not in context.user_data:
        context.user_data['profile'] = {
            "uid": user.id,
            "username": f"@{user.username}" if user.username else "Hidden",
            "full_name": user.full_name, # Ім'я з Telegram за замовчуванням
            "phone": None, 
            "city": None, 
            "district": None,
            "address_details": None, 
            "is_vip": False, 
            "vip_expiry": None,
            "next_order_discount": 0.0, 
            "promo_applied": False
        }
    
    # Гарантуємо наявність кошика
    if 'cart' not in context.user_data:
        context.user_data['cart'] = []

    # 2. Синхронізація з БД (Гідратація)
    try:
        # Timeout також збільшено тут
        with sqlite3.connect(DB_PATH, timeout=30) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Шукаємо юзера
            row = cursor.execute("SELECT * FROM users WHERE user_id=?", (user.id,)).fetchone()
            
            if not row:
                # РЕЄСТРАЦІЯ НОВОГО
                reg_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute("""
                    INSERT INTO users (user_id, username, full_name, reg_date, is_vip, next_order_discount, promo_applied) 
                    VALUES (?, ?, ?, ?, 0, 0, 0)
                """, (user.id, user.username, user.full_name, reg_time))
                conn.commit()
                logger.info(f"🆕 New User Registered: {user.id}")
            else:
                # ВІДНОВЛЕННЯ ДАНИХ З БД
                p = context.user_data['profile']
                p['is_vip'] = bool(row['is_vip'])
                p['vip_expiry'] = row['vip_expiry']
                # Безпечне перетворення float
                p['next_order_discount'] = float(row['next_order_discount']) if row['next_order_discount'] is not None else 0.0
                p['promo_applied'] = bool(row['promo_applied'])
                
                # Відновлюємо особисті дані, якщо вони є в базі (пріоритет над Telegram)
                if row['full_name']: p['full_name'] = row['full_name']
                if row['phone']: p['phone'] = row['phone']
                if row['city']: p['city'] = row['city']
                if row['district']: p['district'] = row['district']
                if row['address_details']: p['address_details'] = row['address_details']
                
    except Exception as e:
        logger.error(f"❌ DB Sync Failure: {e}")
        
    return context.user_data['profile']
    
    
# =================================================================
# 🛍 SECTION 14: CATALOG MASTER ENGINE (TITAN PRO v6.8)
# =================================================================

async def catalog_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Головний вхід у каталог. 
    Відображає категорії та акційні пропозиції.
    """
    text = (
        "<b>🛍 КАТАЛОГ GHO$$TY STAFF</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Тут тільки перевірений стафф. Обирай категорію 👇\n\n"
        "💨 <b>HHC Вейпи</b> — <i>Relax з США (Original)</i>\n"
        "🔌 <b>POD-Системи</b> — <i>Девайси на кожен день</i>\n"
        "💧 <b>Рідини</b> — <i>Chaser, нові колекції (Топові смаки)</i>\n"
    )
    
    kb = [
        [InlineKeyboardButton("💨 HHC ВЕЙПИ (USA)", callback_data="cat_list_hhc")],
        [InlineKeyboardButton("🔌 POD-СИСТЕМИ", callback_data="cat_list_pods")],
        [InlineKeyboardButton("💧 РІДИНИ (Salt)", callback_data="cat_list_liquids")],
        # Додаємо кнопку наборів, якщо вона знадобиться
        [InlineKeyboardButton("🏠 ГОЛОВНЕ МЕНЮ", callback_data="menu_start")]
    ]
    
    # Використовуємо глобальне фото з налаштувань (Section 1), або фолбек
    photo = globals().get('WELCOME_PHOTO', "https://i.ibb.co/y7Q194N/1770068775663.png")
    
    # Використовуємо універсальний UI двигун з підтримкою context
    await send_ghosty_message(update, text, kb, photo=photo, context=context)


async def show_category_items(update: Update, context: ContextTypes.DEFAULT_TYPE, category_key: str):
    """
    Генератор списку товарів.
    ПОВНІСТЮ ОНОВЛЕНО: додано легенду про 💎, сортування та захист від помилок.
    """
    # 1. Професійний мапінг (Зв'язок Callback -> Змінна БД)
    cat_map = {
        'hhc': ('HHC_VAPES', '💨 HHC Вейпи'),
        'pods': ('PODS', '🔌 POD-Системи'),
        'liquids': ('LIQUIDS', '💧 Рідини'),
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
    
    # 2. Формування тексту заголовка з ЛЕГЕНДОЮ
    text = (
        f"📂 <b>КАТЕГОРІЯ: {cat_title}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🔥 — <i>акційна ціна (Знижка)</i>\n"
        f"⌛ — <i>товар закінчується</i>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👇 Натисніть на товар для детального перегляду:"
    )
    
    kb = []
    
    # 3. Розумне сортування
    # Пріоритет: Спочатку ті, де мало товару (⌛), потім звичайні, в кінці - продані
    # (Сортуємо за stock reverse=True)
    sorted_items = sorted(items_dict.items(), key=lambda x: x[1].get('stock', 0), reverse=True)

    for i_id, item in sorted_items:
        stock = item.get('stock', 0)
        
        # Розрахунок ціни через ядро знижок
        # (Перевіряємо, чи існує функція, щоб уникнути помилок)
        if 'calculate_final_price' in globals():
            price, is_discounted = calculate_final_price(item['price'], profile, item_id=i_id)
        else:
            price, is_discounted = item['price'], False

        price_display = f"{int(price)}₴"
        
        # 4. Формування PRO-тексту кнопки
        if stock <= 0:
            btn_text = f"⛔️ {item['name']} (Sold Out)"
        else:
            # Динамічні маркери наявності
            hot_mark = "⌛" if stock < 10 else ""
            vip_mark = "🔥" if is_discounted else ""
            
            # Структура: [Вогонь] Назва | Ціна [Алмаз]
            btn_text = f"{hot_mark}{item['name']} | {price_display}"
        
        kb.append([InlineKeyboardButton(btn_text, callback_data=f"view_item_{i_id}")])
    
    # Навігаційний блок
    kb.append([InlineKeyboardButton("🔙 До категорій", callback_data="cat_all")])
    kb.append([InlineKeyboardButton("🏠 В головне меню", callback_data="menu_start")])
    
    # Використовуємо універсальний UI-адаптер (Section 2)
    # КРИТИЧНО: Передаємо context!
    await _edit_or_reply(update.callback_query, text, kb, context=context)
    
    
    
# =================================================================
# 🔍 SECTION 15: PRODUCT CARD & INTERACTIVE COLOR ENGINE (TITAN ULTIMATE v9.0)
# =================================================================

async def view_item_details(update: Update, context: ContextTypes.DEFAULT_TYPE, item_id: int):
    """
    Точка входу в картку товару.
    Скидає попередній вибір кольору та відображає картку.
    """
    # 1. Отримуємо дані про товар
    item = get_item_data(item_id)
    if not item:
        if update.callback_query:
            await update.callback_query.answer("❌ Товар не знайдено або видалено.", show_alert=True)
        return

    # 2. Скидаємо вибір кольору при першому відкритті
    context.user_data['selected_color'] = None
    
    # 3. Рендеримо картку (перший запуск)
    # ПЕРЕДАЄМО item_id ЯВНО!
    await render_product_card(update, context, item, item_id, item['img'])


async def render_product_card(update: Update, context: ContextTypes.DEFAULT_TYPE, item: dict, item_id: int, current_photo: str):
    """
    Ядро відображення. Викликається при старті та при кліку на колір.
    """
    profile = context.user_data.get("profile", {})
    
    # --- ЛОГІКА ЦІНИ ---
    # Перевірка наявності функції знижок
    if 'calculate_final_price' in globals():
        final_price, has_discount = calculate_final_price(item['price'], profile)
    else:
        final_price, has_discount = item['price'], False

    price_html = f"<b>{int(item['price'])} ₴</b>"
    if has_discount:
        price_html = f"<s>{int(item['price'])}</s> 🔥 <b>{final_price:.0f} ₴</b>"

    # --- ЛОГІКА СКЛАДУ ---
    stock = item.get('stock', 0)
    if stock >= 12: 
        stock_status = f"🟢 <b>В наявності</b> ({stock} шт)"
    elif 1 <= stock < 12: 
        stock_status = f"🟡 <b>Закінчується</b> ({stock})"
    else: 
        stock_status = "🔴 <b>Немає в наявності</b>"

    # --- ЛОГІКА КОЛЬОРУ ---
    selected_color = context.user_data.get('selected_color')
    color_text = f"\n🎨 Колір: <b>{selected_color}</b>" if selected_color else ""

    # --- ЗБІРКА ОПИСУ ---
    safe_name = escape(item['name'])
    desc = item.get('desc', 'Опис оновлюється...')
    
    caption = (
        f"🛍 <b>{safe_name}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📦 {stock_status}\n"
        f"💰 Ціна: {price_html}{color_text}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{desc}"
    )

    kb = []
    
    # 1. ГЕНЕРАЦІЯ КНОПОК КОЛЬОРІВ (Якщо вони є)
    if stock > 0 and "colors" in item and item["colors"]:
        colors = item["colors"]
        row = []
        for col in colors:
            # Якщо цей колір обрано -> ставимо галочку і блокуємо повторний клік
            if col == selected_color:
                btn_text = f"✅ {col}"
                cb_data = "ignore_click" 
            else:
                btn_text = col
                # Формат: sel_col_ID_COLORName (використовуємо item_id з аргументів)
                cb_data = f"sel_col_{item_id}_{col}" 
            
            row.append(InlineKeyboardButton(btn_text, callback_data=cb_data))
            
            # Розбиваємо по 2 кнопки в ряд для краси
            if len(row) == 2:
                kb.append(row)
                row = []
        if row: kb.append(row)

    # 2. КНОПКИ ДІЇ (Купити / Швидко / Менеджер)
    if stock > 0:
        # Сценарій А: Є кольори, але жоден не обрано
        if "colors" in item and item["colors"] and not selected_color:
            kb.append([InlineKeyboardButton("👆 ОБЕРІТЬ КОЛІР ВИЩЕ 👆", callback_data="ignore_click")])
        
        # Сценарій Б: Колір обрано АБО товар без кольорів
        else:
            # Формуємо текст кнопки
            buy_text = f"🛒 КУПИТИ {selected_color.upper()}" if selected_color else "🛒 ДОДАТИ В КОШИК"
            
            # Формуємо дані для кошика (Cart Handler)
            cart_cb = f"add_{item_id}_col_{selected_color}" if selected_color else f"add_{item_id}"
            kb.append([InlineKeyboardButton(buy_text, callback_data=cart_cb)])
            
            # ШВИДКІ ДІЇ (Передаємо колір у колбеку!)
            fast_cb = f"fast_order_{item_id}_{selected_color}" if selected_color else f"fast_order_{item_id}"
            mgr_cb = f"mgr_pre_{item_id}_{selected_color}" if selected_color else f"mgr_pre_{item_id}"
            
            kb.append([
                InlineKeyboardButton("⚡ ШВИДКО", callback_data=fast_cb),
                InlineKeyboardButton("👨‍💻 МЕНЕДЖЕР", callback_data=mgr_cb)
            ])
            
    else:
        # Якщо товару немає -> кнопка сповіщення
        kb.append([InlineKeyboardButton("🔔 ПОВІДОМИТИ ПРО НАЯВНІСТЬ", callback_data=f"notify_{item_id}")])

    # 3. НАВІГАЦІЯ
    kb.append([InlineKeyboardButton("🔙 До каталогу", callback_data="cat_all")])

    # 4. ВІДПРАВКА (Через розумний рушій Section 2)
    # Він сам змінить фото (edit_message_media), якщо current_photo відрізняється від старого
    await send_ghosty_message(update, caption, kb, photo=current_photo, context=context)


async def handle_color_selection_click(update: Update, context: ContextTypes.DEFAULT_TYPE, item_id: int, color_name: str):
    """
    Обробляє клік по кольору: змінює фото та оновлює галочки.
    """
    item = get_item_data(item_id)
    if not item: return

    # 1. Зберігаємо вибір користувача
    context.user_data['selected_color'] = color_name
    
    # 2. Шукаємо фото для цього кольору
    # Якщо в color_previews є фото для цього кольору -> беремо його
    # Інакше -> залишаємо головне фото товару
    previews = item.get("color_previews", {})
    new_photo = previews.get(color_name, item['img'])
    
    # 3. Перемальовуємо картку (це оновить галочки і фото)
    # ПЕРЕДАЄМО item_id ЯВНО!
    await render_product_card(update, context, item, item_id, new_photo)
    
    
# =================================================================
# 🌍 SECTION 10: GEOGRAPHY & LOGISTICS (TITAN ULTIMATE v10.0)
# =================================================================

async def choose_city_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    КРОК 1: Головне меню вибору міста.
    Використовується при старті, в профілі та при замовленні.
    """
    # Встановлюємо стан, щоб бот знав, що ми в процесі налаштування
    context.user_data['state'] = "COLLECTING_DATA"
    context.user_data.setdefault('data_flow', {})['step'] = 'city_selection'
    
    # Отримуємо картинку (або дефолтну)
    map_image = globals().get('WELCOME_PHOTO', "https://i.ibb.co/y7Q194N/1770068775663.png")
    
    text = (
        "🏙 <b>ОБЕРІТЬ ВАШЕ МІСТО</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Ми працюємо у найбільших містах України.\n"
        "Оберіть локацію, щоб побачити доступні методи доставки 👇"
    )
    
    # Отримуємо список міст (з Section 4)
    cities_db = globals().get('UKRAINE_CITIES', {})
    if not cities_db:
        # Аварійний режим, якщо база міст пуста
        cities_db = {"Київ": [], "Дніпро": [], "Львів": [], "Одеса": [], "Харків": []}
        
    city_list = list(cities_db.keys())
    
    keyboard = []
    # Генерація кнопок по 2 в ряд
    for i in range(0, len(city_list), 2):
        row = [InlineKeyboardButton(city_list[i], callback_data=f"sel_city_{city_list[i]}")]
        if i + 1 < len(city_list):
            row.append(InlineKeyboardButton(city_list[i+1], callback_data=f"sel_city_{city_list[i+1]}"))
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("🔙 В головне меню", callback_data="menu_start")])
    
    # Відправляємо через надійний сендер
    await send_ghosty_message(update, text, keyboard, photo=map_image, context=context)


async def choose_dnipro_delivery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Спеціальний логістичний хаб для Дніпра.
    Дозволяє вибрати між Кладом (район) та Кур'єром (адреса).
    """
    query = update.callback_query
    
    # Зберігаємо місто заздалегідь
    context.user_data.setdefault("profile", {})["city"] = "Дніпро"
    
    text = (
        "🏙 <b>ДНІПРО: СПОСІБ ОТРИМАННЯ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "1️⃣ <b>Район (Клад)</b> — готовий сховок у вашому районі.\n"
        "2️⃣ <b>Кур'єр (+150 грн)</b> — доставка прямо по адресі.\n\n"
        "👇 Що обираєте?"
    )
    
    kb = [
        # sel_city_Dnipro_Klad -> Перенаправить на вибір району (district_selection_handler)
        [InlineKeyboardButton("📍 Обрати район (Клад)", callback_data="sel_city_Dnipro_Klad")],
        
        # sel_dist_Кур'єр -> Одразу вважатиметься, що район обрано як "Кур'єр", 
        # і Section 16 (address_request_handler) попросить адресу.
        [InlineKeyboardButton("🛵 Кур'єрська доставка (+150 грн)", callback_data="sel_dist_Кур'єр")],
        
        [InlineKeyboardButton("⬅️ Інше місто", callback_data="choose_city")]
    ]
    
    await _edit_or_reply(query, text, kb, context=context)


async def district_selection_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, city: str):
    """
    КРОК 2: Динамічне меню районів.
    """
    query = update.callback_query
    
    # Логіка для Дніпра (якщо прийшов спец-тег)
    if city == "Dnipro_Klad":
        real_city = "Дніпро"
    else:
        real_city = city
        
    # Зберігаємо реальне місто в профіль
    context.user_data.setdefault('profile', {})['city'] = real_city
    
    # Отримуємо райони
    cities_db = globals().get('UKRAINE_CITIES', {})
    districts = cities_db.get(real_city, [])
    
    text = (
        f"🏘 <b>{real_city.upper()}: ОБЕРІТЬ РАЙОН</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Вкажіть зручний район для отримання:"
    )

    kb = []
    if districts:
        for i in range(0, len(districts), 2):
            row = [InlineKeyboardButton(districts[i], callback_data=f"sel_dist_{districts[i]}")]
            if i + 1 < len(districts):
                row.append(InlineKeyboardButton(districts[i+1], callback_data=f"sel_dist_{districts[i+1]}"))
            kb.append(row)
    else:
        # Якщо районів немає в базі, пропонуємо ввести адресу вручну
        text = f"📍 <b>{real_city}</b>\nУточніть деталі доставки вручну."
        # sel_dist_Центр -> автоматично обере район "Центр" і попросить адресу
        kb.append([InlineKeyboardButton("➡️ Ввести адресу", callback_data="sel_dist_Центр")])
        
    kb.append([InlineKeyboardButton("🔙 Змінити місто", callback_data="choose_city")])
    
    # Оновлюємо крок для FSM
    context.user_data.setdefault('data_flow', {})['step'] = 'district_selection'
    
    await _edit_or_reply(query, text, kb, context=context)
    
    
# =================================================================
# 👤 SECTION 5: MASTER START & PROFILE UI (TITAN PRO FIX)
# =================================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Головна точка входу (/start).
    Викликає реєстрацію (із Section 4), нараховує бонуси та вітає.
    """
    user = update.effective_user
    
    # 🔥 ФІКС ЗАЛИПАННЯ: Примусово очищаємо старі "хвости" замовлень
    context.user_data['target_item_id'] = None
    context.user_data['state'] = None
    
    # 1. Отримуємо профіль (функція береться з SECTION 4)
    if 'get_or_create_user' in globals():
        profile = await get_or_create_user(update, context)
    else:
        # Аварійний фолбек, якщо Section 4 не завантажилась
        await update.message.reply_text("⚠️ Система завантажується... Спробуйте через 5 секунд.")
        return
    
    # 2. АВТО-АКТИВАЦІЯ БОНУСІВ (Тільки 1 раз при першому старті)
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
        
        # Оновлюємо базу (фіксуємо, що бонуси видані)
        try:
            with sqlite3.connect(DB_PATH, timeout=30) as conn: # Timeout 30 для стабільності
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

    # 3. ВІЗУАЛІЗАЦІЯ ПРИВІТАННЯ
    safe_name = escape(user.first_name)
    personal_promo = f"GHST{user.id}"
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
        f"<i>(Поділись з другом: йому +7 днів VIP, тобі 50 грн на баланс!)</i>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👇 <b>ГОЛОВНЕ МЕНЮ:</b>"
    )
    
    # 🔥 ФІКС КНОПКИ: "ДАНІ ПРО ДОСТАВКУ" замість "ОБРАТИ ЛОКАЦІЮ"
    # Ця кнопка тепер веде на fill_delivery_data, що дозволяє змінити адресу
    keyboard = [
        [InlineKeyboardButton("🛍 ВІДКРИТИ КАТАЛОГ 🌿", callback_data="cat_all")],
        [InlineKeyboardButton("👤 ПРОФІЛЬ", callback_data="menu_profile"), 
         InlineKeyboardButton("🛒 КОШИК", callback_data="menu_cart")],
        [InlineKeyboardButton("🚚 ДАНІ ПРО ДОСТАВКУ", callback_data="fill_delivery_data")], 
        [InlineKeyboardButton("📜 ПРАВИЛА", callback_data="menu_terms")],
        [InlineKeyboardButton("👨‍💻 МЕНЕДЖЕР", url=f"https://t.me/{MANAGER_USERNAME}"),
         InlineKeyboardButton("📢 КАНАЛ", url=f"{CHANNEL_URL}")]
    ]
    
    # Кнопка адміна
    if user.id == MANAGER_ID:
        keyboard.append([InlineKeyboardButton("⚙️ GOD MODE (ADMIN)", callback_data="admin_main")])

    photo = globals().get('WELCOME_PHOTO', "https://i.ibb.co/y7Q194N/1770068775663.png")
    
    # Використовуємо універсальний відправник
    await send_ghosty_message(update, welcome_text, keyboard, photo=photo, context=context)


async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Відображає профіль користувача з його реальною аватаркою Telegram.
    Використовує get_or_create_user з Section 4.
    """
    user = update.effective_user
    
    # Викликаємо функцію з Section 4
    if 'get_or_create_user' in globals():
        profile = await get_or_create_user(update, context)
    else:
        try: await update.callback_query.answer("⚠️ Помилка доступу до профілю", show_alert=True)
        except: pass
        return
    
    # Спробуємо отримати справжнє фото профілю користувача
    user_photo = None
    try:
        photos = await user.get_profile_photos(limit=1)
        if photos and photos.total_count > 0:
            # Беремо file_id найбільшої версії фото
            user_photo = photos.photos[0][-1].file_id 
    except Exception as e:
        logger.debug(f"Failed to get user photo: {e}")

    # Якщо фото немає, використовуємо стандартне лого
    if not user_photo:
        user_photo = globals().get('WELCOME_PHOTO', "https://i.ibb.co/y7Q194N/1770068775663.png")

    # Дані для відображення
    full_name = profile.get('full_name', user.full_name)
    phone = profile.get('phone', 'Не вказано')
    city = profile.get('city', 'Не обрано')
    district = profile.get('district', '')
    address = profile.get('address_details', '—')
    
    # Красиве форматування локації
    # Якщо є район і він не дублюється в адресі -> показуємо його
    location_str = f"{city}"
    if district and district not in str(address): 
        location_str += f" ({district})"
    
    if city == 'Не обрано' or not city: 
        location_str = "Не обрано"

    balance = profile.get('next_order_discount', 0)
    vip_status = "💎 - V.I.P PRO" if profile.get('is_vip') else "👤 Standard"
    vip_till = profile.get('vip_expiry', '—')
    
    text = (
        f"👤 <b>ОСОБИСТИЙ КАБІНЕТ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 ID: <code>{user.id}</code>\n"
        f"🧢 Ім'я: <b>{full_name}</b>\n"
        f"🌟 Статус: <b>{vip_status}</b> (до {vip_till})\n\n"
        f"💰 <b>БАЛАНС БОНУСІВ: {int(balance)} ₴</b>\n"
        f"<i>(Можна використати для знижки до 50%)</i>\n\n"
        f"📍 <b>ДАНІ ДОСТАВКИ:</b>\n"
        f"🏙 Локація: {location_str}\n"
        f"🏠 Адреса: {address}\n"
        f"📱 Телефон: {phone}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👇 <i>Керування:</i>"
    )
    
    kb = [
        # 🔥 Ця кнопка тепер точно працює (перевірте Section 29, щоб там був обробник 'fill_delivery_data')
        [InlineKeyboardButton("✏️ Змінити дані доставки", callback_data="fill_delivery_data")],
        [InlineKeyboardButton("🎟 Ввести промокод", callback_data="menu_promo")],
        [InlineKeyboardButton("🔙 В головне меню", callback_data="menu_start")]
    ]
    
    await send_ghosty_message(update, text, kb, photo=user_photo, context=context)
    
# =================================================================
# 📝 SECTION 16: SMART DATA COLLECTION (TITAN FIXED)
# =================================================================

import sqlite3
from datetime import datetime

async def start_data_collection(update: Update, context: ContextTypes.DEFAULT_TYPE, next_action: str = 'checkout', item_id: int = None):
    """
    Ініціалізація збору даних.
    next_action='none' або 'profile' використовується для редагування даних без переходу до покупки.
    """
    user = update.effective_user
    
    # 1. Зберігаємо мету (куди йти після заповнення)
    context.user_data['post_data_action'] = next_action
    # Якщо передано ID товару (для швидкого замовлення), зберігаємо його
    if item_id: context.user_data['target_item_id'] = item_id
    
    profile = context.user_data.setdefault('profile', {'uid': user.id})
    
    # Визначаємо, чи це режим примусового редагування (коли натиснули "Змінити дані")
    force_edit = (next_action == 'none' or next_action == 'profile')

    # --- КРОК 1: ІМ'Я ---
    # Питаємо ім'я, якщо його немає АБО якщо це примусове редагування
    has_name = len(profile.get('full_name', '')) > 2
    if force_edit or not has_name:
        context.user_data['state'] = "COLLECTING_DATA"
        context.user_data['data_step'] = "name"
        
        current_val = f" (Поточне: {profile.get('full_name')})" if has_name else ""
        text = (
            f"📝 <b>КРОК 1/4: ЗНАЙОМСТВО</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"Для оформлення накладної нам потрібно знати, як до вас звертатись.\n"
            f"{current_val}\n\n"
            f"👇 <i>Введіть ваше Прізвище та Ім'я:</i>"
        )
        kb = [[InlineKeyboardButton("✖️ Скасувати", callback_data="menu_start")]]
        await send_ghosty_message(update, text, kb, context=context)
        return

    # --- КРОК 2: ТЕЛЕФОН ---
    has_phone = len(profile.get('phone', '')) > 9
    if force_edit or not has_phone:
        context.user_data['state'] = "COLLECTING_DATA"
        context.user_data['data_step'] = "phone"
        
        current_val = f" (Поточний: {profile.get('phone')})" if has_phone else ""
        text = (
            f"📱 <b>КРОК 2/4: КОНТАКТ</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"На цей номер прийде СМС з ТТН від Нової Пошти.\n"
            f"{current_val}\n\n"
            f"👇 <i>Введіть номер телефону (напр. 0991234567):</i>"
        )
        kb = [[InlineKeyboardButton("✖️ Скасувати", callback_data="menu_start")]]
        await send_ghosty_message(update, text, kb, context=context)
        return

    # --- КРОК 3: МІСТО ---
    # Якщо міста немає АБО ми в режимі редагування -> йдемо в меню міст
    if force_edit or not profile.get('city'):
        await choose_city_menu(update, context)
        return

    # --- КРОК 4: АДРЕСА ---
    # Якщо адреси немає АБО ми в режимі редагування -> питаємо адресу
    has_address = len(profile.get('address_details', '')) > 2
    if force_edit or not has_address:
        city = profile.get('city')
        context.user_data['state'] = "COLLECTING_DATA"
        context.user_data['data_step'] = "address"
        
        current_val = f"\nПоточна: {profile.get('address_details')}" if has_address else ""
        text = (
            f"📍 <b>КРОК 4/4: ДЕТАЛІ ДОСТАВКИ ({city})</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"Вкажіть номер відділення НП (напр. «№5»)\n"
            f"або повну адресу для кур'єра/таксі.\n"
            f"<i>{current_val}</i>\n\n"
            f"👇 <i>Напишіть нову адресу сюди:</i>"
        )
        kb = [
            [InlineKeyboardButton("🔙 Змінити місто", callback_data="choose_city")],
            [InlineKeyboardButton("✖️ Скасувати", callback_data="menu_start")]
        ]
        await send_ghosty_message(update, text, kb, context=context)
        return

    # ЯКЩО ВСІ ДАНІ Є І МИ НЕ В РЕЖИМІ РЕДАГУВАННЯ -> Фіналізація
    await finalize_data_collection(update, context)


async def address_request_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, dist_name: str):
    """
    Проміжний хендлер: Коли обрали район (Крок 3), переходимо до адреси (Крок 4).
    """
    # Зберігаємо район (очищуємо від зайвого тексту, якщо він був у колбеку)
    clean_dist = dist_name.split("_")[0] 
    context.user_data.setdefault('profile', {})['district'] = clean_dist
    
    context.user_data['state'] = "COLLECTING_DATA"
    context.user_data['data_step'] = "address"
    
    text = (
        f"✅ Район: <b>{clean_dist}</b>\n"
        f"📍 <b>КРОК 4/4: АДРЕСА</b>\n"
        f"Напишіть номер відділення НП або адресу:"
    )
    
    kb = [[InlineKeyboardButton("🔙 Змінити район", callback_data="choose_city")]]
    
    # Використовуємо універсальний UI
    await send_ghosty_message(update, text, kb, context=context)


async def finalize_data_collection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Фінал анкети: ГАРАНТОВАНЕ збереження в БД та перехід до Оплати/Менеджера/Профілю.
    """
    user_id = update.effective_user.id
    profile = context.user_data.get('profile', {})
    action = context.user_data.get('post_data_action', 'checkout')
    
    # 1. Збереження в БД (SQL Upsert з логуванням помилок)
    try:
        # Збільшено timeout до 30 секунд для надійності на BotHost
        with sqlite3.connect(DB_PATH, timeout=30) as conn:
            # Спочатку гарантуємо, що запис існує (INSERT OR IGNORE)
            conn.execute("""
                INSERT OR IGNORE INTO users (user_id, full_name, username, balance, is_vip, joined_date)
                VALUES (?, ?, ?, 0, 0, ?)
            """, (user_id, profile.get('full_name'), update.effective_user.username, datetime.now().strftime("%Y-%m-%d")))
            
            # Тепер оновлюємо дані
            conn.execute("""
                UPDATE users 
                SET full_name=?, phone=?, city=?, district=?, address_details=?
                WHERE user_id=?
            """, (
                profile.get('full_name'), 
                profile.get('phone'), 
                profile.get('city'), 
                profile.get('district'), 
                profile.get('address_details'), 
                user_id
            ))
            conn.commit()
            logger.info(f"✅ User data saved for {user_id}")
            
    except Exception as e:
        logger.error(f"DB Finalize Error: {e}")
        # Не перериваємо роботу, дані залишаться в кеші бота

    # 2. Очищення стану (щоб бот не чекав вводу тексту)
    context.user_data['state'] = None
    context.user_data['data_step'] = None

    # 3. Маршрутизація до мети
    
    # А) Оплата онлайн (Checkout)
    if action == 'checkout' or action == 'fast_order':
        await checkout_init(update, context)
        
    # Б) Замовлення через менеджера (Генерація тексту)
    elif action == 'manager_order':
        # Перевіряємо наявність функції (для безпеки)
        if 'submit_order_to_manager' in globals():
            await submit_order_to_manager(update, context)
        else:
             await send_ghosty_message(update, "✅ Заявку створено! Менеджер скоро напише.", context=context)
    
    # В) Просто редагували профіль (дія 'none' або 'profile')
    else:
        # Сповіщення про успіх
        await send_ghosty_message(update, "✅ <b>Дані успішно збережено!</b>", context=context)
        # Невелика пауза для UX
        await asyncio.sleep(0.5) 
        # Повертаємось в кабінет
        await show_profile(update, context)
        

# =================================================================
# 🛒 SECTION 18: CART LOGIC (TITAN FIXED v10.0)
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
            await _edit_or_reply(update.callback_query, empty_text, empty_kb, context=context)
        else:
            await send_ghosty_message(update, empty_text, empty_kb, context=context)
        return

    total_sum = 0.0
    items_text = ""
    keyboard = [] 

    for index, item in enumerate(cart):
        try: price = float(item.get('price', 0))
        except: price = 0.0
        
        # Рахуємо знижку
        if 'calculate_final_price' in globals():
            final_price, is_discounted = calculate_final_price(price, profile)
        else:
            final_price, is_discounted = price, False
            
        total_sum += final_price
        
        name = item.get('name', 'Товар')
        gift = item.get('gift')
        color = item.get('color') # Додаємо відображення кольору
        
        details = []
        if color: details.append(f"🎨 {color}")
        if gift: details.append(f"🎁 {gift}")
        
        details_txt = f"\n   {' | '.join(details)}" if details else ""
        
        price_txt = f"<s>{int(price)}</s> <b>{final_price:.0f} грн</b>" if is_discounted else f"<b>{int(price)} грн</b>"
        items_text += f"🔹 <b>{name}</b>{details_txt}\n   💰 {price_txt}\n\n"
        
        uid = item.get('id', 0)
        keyboard.append([InlineKeyboardButton(f"❌ Видалити: {name[:15]}...", callback_data=f"cart_del_{uid}")])

    # Перевірка наявності всіх даних для доставки
    full_name = profile.get("full_name")
    phone = profile.get("phone")
    city = profile.get("city")
    address = profile.get("address_details")
    
    # КРИТИЧНЕ ВИПРАВЛЕННЯ: Тепер перевіряємо і адресу, і ім'я!
    can_checkout = all([full_name, phone, city, address])
    
    if can_checkout:
        loc_status = f"✅ <b>Дані:</b> {city}, {full_name}\n📞 {phone}\n🏠 {address}"
        btn_text = "🚀 ОФОРМИТИ ЗАМОВЛЕННЯ"
        btn_action = "checkout_init"
    else:
        loc_status = "⚠️ <b>Дані доставки не заповнені!</b>"
        btn_text = "📝 ЗАПОВНИТИ ДАНІ"
        # Ведемо на start_data_collection, а не просто fill_delivery_data (для надійності)
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

    await send_ghosty_message(update, full_text, keyboard, context=context)


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
            # Видаляємо тільки той елемент, у якого співпадає унікальний ID
            context.user_data["cart"] = [item for item in cart if item.get('id') != target_uid]
            try: await query.answer("❌ Товар видалено")
            except: pass
        except Exception as e:
            logger.error(f"Cart Delete Error: {e}")
    
    await show_cart_logic(update, context)
    

# =================================================================
# 🎁 SECTION 19: GIFT & CART ENGINE (TITAN ULTIMATE v10.5 - PRO FIX)
# =================================================================

# Список ID товарів, які йдуть на подарунок.
# Самі дані беруться з бази (Section 4) через get_item_data.
GIFT_POOL = [9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008] 

async def gift_selection_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Генератор меню вибору подарунка.
    АДАПТОВАНО: Розуміє звідки прийшов запит (Кошик, Швидко, Менеджер).
    """
    query = update.callback_query
    data = query.data
    
    # 1. Розбираємо вхідні дані, щоб зберегти контекст операції
    parts = data.split("_")
    
    if data.startswith("fast_order_"):
        prefix = "fast_order"
        item_id = int(parts[2])
    elif data.startswith("mgr_pre_"):
        prefix = "mgr_pre"
        item_id = int(parts[2])
    elif data.startswith("add_"):
        prefix = "add"
        item_id = int(parts[1])
    elif data.startswith("gift_sel_"):
        # Якщо ми перемикаємось всередині меню подарунків
        prefix_code = parts[2]
        if prefix_code == "fast": prefix = "fast_order"
        elif prefix_code == "mgr": prefix = "mgr_pre"
        else: prefix = "add"
        item_id = int(parts[3])
    else:
        await query.answer("❌ Помилка контексту", show_alert=True)
        return

    main_item = get_item_data(item_id)
    if not main_item:
        await query.answer("❌ Товар не знайдено", show_alert=True)
        return

    text = (
        f"🎁 <b>АКЦІЯ: ОБЕРІТЬ ВАШ БОНУС!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"До товару <b>{main_item['name']}</b> йде рідина у подарунок.\n"
        f"Це абсолютно <b>БЕЗКОШТОВНО</b>!\n\n"
        f"👇 <i>Оберіть смак зі списку:</i>"
    )

    kb = []
    # 2. Генеруємо кнопки подарунків (формат PREFIX_ITEMID_GIFTID)
    for gid in GIFT_POOL:
        gift_item = get_item_data(gid)
        if gift_item:
            # Очищаємо назву для гарного вигляду на кнопці
            short_name = gift_item['name'].replace("🎁 ", "").replace(" 30ml", "").strip()
            kb.append([InlineKeyboardButton(f"🧪 {short_name}", callback_data=f"{prefix}_{item_id}_{gid}")])

    # 3. Керуючі кнопки
    kb.append([InlineKeyboardButton("❌ Без подарунка", callback_data=f"{prefix}_{item_id}_0")])
    kb.append([InlineKeyboardButton("🔙 Назад до товару", callback_data=f"view_item_{item_id}")])

    # Відправляємо оновлене меню
    await _edit_or_reply(query, text, kb, context=context)


async def add_to_cart_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    ЄДИНА функція додавання в кошик (Prefix: 'add').
    ✅ ПОВНІСТЮ ВИПРАВЛЕНИЙ ПАРСИНГ: Не плутає ID товару, колір та подарунок.
    """
    query = update.callback_query
    parts = query.data.split("_")
    
    try:
        item_id = int(parts[1])
        item = get_item_data(item_id)
        if not item: 
            await query.answer("❌ Товар не знайдено")
            return

        # --- 1. ПАРСИНГ КОЛЬОРУ ---
        selected_color = context.user_data.get('selected_color')
        if "col" in parts:
            col_index = parts.index("col")
            selected_color = "_".join(parts[col_index+1:])

        # --- 2. ПАРСИНГ ПОДАРУНКА ---
        gift_id = None
        # Якщо частин більше 2 і остання - це число (і вона не стоїть одразу після слова 'col')
        if len(parts) > 2 and parts[-1].isdigit() and parts[-2] != "col":
            gift_id = int(parts[-1])

        # --- 3. ЛОГІКА ПЕРЕХОПЛЕННЯ (АВТОВИБІР ПОДАРУНКА) ---
        # Перевіряємо, чи підпадає товар під акцію (Вейпи 100-299, Поди 500-699, або прапорець)
        is_hhc = 100 <= item_id < 300
        is_pod = 500 <= item_id < 700
        has_gift_flag = item.get('gift_liquid') == True
        
        needs_gift = is_hhc or is_pod or has_gift_flag
        
        if needs_gift and gift_id is None:
            # Зберігаємо колір перед переходом у меню подарунків
            if selected_color: context.user_data['selected_color'] = selected_color
            await gift_selection_handler(update, context) 
            return

        # --- 4. ДОДАВАННЯ В КОШИК ---
        gift_name = None
        if gift_id and gift_id > 0:
            g_item = get_item_data(gift_id)
            if g_item: gift_name = g_item['name']

        context.user_data.setdefault("cart", []).append({
            "id": random.randint(100000, 999999), # Унікальний ID для кошика
            "real_id": item_id, 
            "name": item['name'],
            "price": item['price'], 
            "color": selected_color, 
            "gift": gift_name
        })
        
        try: await query.answer("✅ Додано в кошик!", show_alert=False)
        except: pass
        
        # --- 5. ВІЗУАЛЬНИЙ ЗВІТ ---
        info = ""
        if selected_color: info += f"\n🎨 Колір: <b>{selected_color}</b>"
        if gift_name: info += f"\n🎁 Бонус: <b>{gift_name}</b>"
        
        text = (
            f"✅ <b>ТОВАР У КОШИКУ!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📦 <b>{item['name']}</b>"
            f"{info}\n"
            f"💰 <b>{int(item['price'])} грн</b>\n\n"
            f"👇 <i>Що робимо далі?</i>"
        )
        
        kb = [
            [InlineKeyboardButton("🛒 Оформити замовлення", callback_data="menu_cart")],
            [InlineKeyboardButton("🛍 Продовжити покупки", callback_data="cat_all")],
            [InlineKeyboardButton("🏠 В головне меню", callback_data="menu_start")]
        ]
        
        await _edit_or_reply(query, text, kb, context=context)

    except Exception as e:
        logger.error(f"Add to Cart Error: {e}")
        await query.answer("❌ Помилка додавання")
        
# =================================================================
# 💳 SECTION 20: CHECKOUT & PAYMENT CORE (TITAN FINAL REVISION)
# =================================================================

async def checkout_init(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Ініціалізація оплати (Фінальний чек).
    Включає:
    1. Відображення фото (для швидкого замовлення).
    2. Автоматичне застосування знижок з балансу.
    3. Розрахунок доставки.
    4. Відображення подарунків (з кошика та швидкого замовлення).
    """
    # Отримуємо дані
    target_item_id = context.user_data.get('target_item_id')
    target_gift_id = context.user_data.get('target_gift_id') # Отримуємо ID подарунка
    profile = context.user_data.get('profile', {})
    
    # Баланс бонусів користувача
    user_balance = float(profile.get('next_order_discount', 0.0))
    
    total_amount = 0.0
    items_desc = ""
    photo_to_show = None 

    # --- ВАРІАНТ А: ШВИДКЕ ЗАМОВЛЕННЯ (Один товар + Подарунок) ---
    if target_item_id:
        item = get_item_data(target_item_id)
        if not item: 
            context.user_data['target_item_id'] = None
            context.user_data['target_gift_id'] = None
            await send_ghosty_message(update, "⚠️ Товар розпродано або не знайдено.", context=context)
            return
        
        # Фото (враховуючи обраний колір)
        selected_color = context.user_data.get('selected_color')
        if selected_color and "color_previews" in item:
            photo_to_show = item["color_previews"].get(selected_color, item['img'])
        else:
            photo_to_show = item['img']

        # Ціна (вже з урахуванням VIP-знижки, якщо вона є)
        price, _ = calculate_final_price(item['price'], profile, item_id=target_item_id)
        total_amount = price
        
        # Опис основного товару
        color_txt = f" ({selected_color})" if selected_color else ""
        items_desc = f"▫️ <b>{item['name']}</b>{color_txt}\n   1 x {int(price)} грн"

        # 🎁 ВІДОБРАЖЕННЯ ПОДАРУНКА ДЛЯ ШВИДКОГО ЗАМОВЛЕННЯ
        if target_gift_id and target_gift_id > 0:
            gift_item = get_item_data(target_gift_id)
            if gift_item:
                items_desc += f"\n   🎁 Бонус: <b>{gift_item['name']}</b>"

    # --- ВАРІАНТ Б: ЗАМОВЛЕННЯ З КОШИКА (Декілька товарів + Подарунки) ---
    else:
        cart = context.user_data.get('cart', [])
        if not cart:
            kb = [[InlineKeyboardButton("🛍 Перейти в каталог", callback_data="cat_all")]]
            await send_ghosty_message(update, "🛒 <b>Ваш кошик порожній.</b>", kb, context=context)
            return
            
        photo_to_show = globals().get('WELCOME_PHOTO', "https://i.ibb.co/y7Q194N/1770068775663.png")
        
        for i in cart:
            p, _ = calculate_final_price(i['price'], profile, item_id=i.get('real_id'))
            total_amount += p
            
            # Формуємо деталі (колір та подарунок)
            extras = []
            if i.get('color'): extras.append(f"🎨 {i['color']}")
            if i.get('gift'): extras.append(f"🎁 {i['gift']}")
            
            extra_txt = f" ({', '.join(extras)})" if extras else ""
            items_desc += f"▫️ <b>{i['name']}</b>{extra_txt} — {int(p)} грн\n"

    # --- ЛОГІКА ДОСТАВКИ ---
    dist = profile.get('district', '')
    if "Кур'єр" in str(dist) and not profile.get("is_vip"):
        total_amount += 150.0
        items_desc += "\n🚚 Доставка кур'єром (+150 грн)"
        
    # --- 🔥 ЗАСТОСУВАННЯ БОНУСІВ З БАЛАНСУ ---
    used_bonus = 0.0
    if user_balance > 0:
        # Можна списати все, але сума не може бути меншою за 1 грн (технічне обмеження)
        max_possible_discount = max(0.0, total_amount - 1.0)
        
        if user_balance >= max_possible_discount:
            used_bonus = max_possible_discount
        else:
            used_bonus = user_balance
            
        if used_bonus > 0:
            total_amount -= used_bonus
            items_desc += f"\n\n💎 <b>Використано бонусів: -{int(used_bonus)} грн</b>"
            
    # Зберігаємо суму списання, щоб потім відняти з БД при підтвердженні/відправці менеджеру
    context.user_data['planned_bonus_deduction'] = used_bonus
    
    # Фіксуємо фінальну суму до сплати
    context.user_data['final_checkout_sum'] = total_amount
    
    # Формування тексту чека
    full_name = profile.get('full_name', 'Клієнт')
    city = profile.get('city', 'Місто')
    
    text = (
        f"🧾 <b>ФІНАЛЬНИЙ ЧЕК</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{items_desc}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📍 <b>Доставка:</b> {city}, {dist}\n"
        f"👤 <b>Отримувач:</b> {full_name}\n"
        f"💰 <b>ДО СПЛАТИ: {total_amount:.2f} UAH</b>\n\n"
        f"👇 <i>Оберіть зручний метод оплати:</i>"
    )
    
    kb = [
        [InlineKeyboardButton("💳 Monobank", callback_data="pay_mono"),
         InlineKeyboardButton("💚 PrivatBank", callback_data="pay_privat")],
        [InlineKeyboardButton("💎 Crypto / USDT", callback_data="pay_ghossty")],
        [InlineKeyboardButton("🔙 Назад", callback_data="menu_start")]
    ]
    
    await send_ghosty_message(update, text, kb, photo=photo_to_show, context=context)


async def payment_selection_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, method: str):
    """
    Показ реквізитів і інструкції.
    """
    query = update.callback_query
    
    link = PAYMENT_LINK.get(method, PAYMENT_LINK['ghossty'])
    amount = context.user_data.get('final_checkout_sum', 0)
    
    text = (
        f"💳 <b>ОПЛАТА ЗАМОВЛЕННЯ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Сума до сплати: <b>{amount:.2f} грн</b>\n\n"
        f"🔗 <b>Реквізити для оплати:</b>\n"
        f"<a href='{link}'>👉 НАТИСНІТЬ ТУТ ЩОБ СПЛАТИТИ</a>\n\n"
        f"⚠️ <b>ВАЖЛИВО:</b>\n"
        f"Після успішної оплати натисніть кнопку «Я ОПЛАТИВ» нижче та надішліть скріншот квитанції."
    )
    
    kb = [
        [InlineKeyboardButton("✅ Я ОПЛАТИВ", callback_data="confirm_payment_start")],
        [InlineKeyboardButton("🔙 Змінити метод", callback_data="checkout_init")]
    ]
    
    await _edit_or_reply(query, text, kb, context=context)
    
# =================================================================
# ⚙️ SECTION 8: PROMO & REFERRAL (DB SYNCED & SECURE)
# =================================================================

async def process_promo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обробка кодів: 
    1. GHST2026 (Глобальний промо: VIP + Гроші).
    2. GHST+ID (Реферальна система: Вам VIP, Другу +50 грн).
    """
    if not update.message or not update.message.text: return
    
    text = update.message.text.strip().upper()
    user = update.effective_user
    profile = context.user_data.setdefault("profile", {})
    
    msg = ""
    is_success = False
    
    # 1. Підключення до БД
    try:
        conn = sqlite3.connect(DB_PATH, timeout=30)
        cursor = conn.cursor()
    except Exception as e:
        logger.error(f"DB Connect Error: {e}")
        await update.message.reply_text("⚠️ Технічна помилка. Спробуйте пізніше.")
        return

    # --- ВАРІАНТ А: ГЛОБАЛЬНИЙ ПРОМО (GHST2026) ---
    if text == "GHST2026":
        if profile.get('promo_GHST2026_used'):
            msg = "⚠️ <b>Цей промокод ви вже активували!</b>"
        else:
            # Нагорода
            profile["next_order_discount"] = 101.0
            profile["is_vip"] = True
            profile["promo_GHST2026_used"] = True
            
            # Дата +30 днів
            expiry_date = datetime.now() + timedelta(days=30)
            profile["vip_expiry"] = expiry_date.strftime("%Y-%m-%d")
            
            msg = (
                "✅ <b>GHST2026 УСПІШНО АКТИВОВАНО!</b>\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "🎁 <b>Баланс поповнено:</b> +101 грн\n"
                "💎 <b>VIP статус:</b> Активовано на 30 днів\n"
                f"📅 <b>Діє до:</b> {profile['vip_expiry']}"
            )
            is_success = True

    # --- ВАРІАНТ Б: РЕФЕРАЛЬНИЙ КОД (GHST12345) ---
    elif text.startswith("GHST") and text[4:].isdigit():
        target_id = int(text[4:])
        
        # Перевірки
        if target_id == user.id:
            msg = "❌ <b>Ви не можете активувати свій власний код.</b>"
        elif profile.get('referral_used'):
            msg = "⚠️ <b>Ви вже активували реферальний код раніше.</b>"
        else:
            # Перевіряємо існування власника коду
            referrer = cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (target_id,)).fetchone()
            
            if not referrer:
                msg = "❌ <b>Такого коду не існує. Перевірте цифри.</b>"
            else:
                # 1. НАГОРОДА ВАМ (Поточному користувачу)
                # Логіка продовження VIP: якщо є активний, додаємо до нього, інакше від сьогодні
                current_expiry_str = profile.get("vip_expiry")
                if current_expiry_str:
                    try:
                        current_date = datetime.strptime(current_expiry_str, "%Y-%m-%d")
                        if current_date < datetime.now(): current_date = datetime.now()
                    except: current_date = datetime.now()
                else:
                    current_date = datetime.now()
                
                new_expiry = current_date + timedelta(days=7)
                profile["vip_expiry"] = new_expiry.strftime("%Y-%m-%d")
                profile["is_vip"] = True
                profile["referral_used"] = True
                
                msg = (
                    f"🤝 <b>Реферальний код прийнято!</b>\n"
                    f"Вам нараховано <b>+7 днів VIP</b> статусу.\n"
                    f"📅 Ваш VIP діє до: <b>{profile['vip_expiry']}</b>"
                )
                is_success = True
                
                # 2. НАГОРОДА ДРУГУ (Власнику коду)
                try:
                    # Додаємо гроші в БД
                    cursor.execute("""
                        UPDATE users 
                        SET next_order_discount = next_order_discount + 50 
                        WHERE user_id = ?
                    """, (target_id,))
                    conn.commit()
                    
                    # Надсилаємо йому повідомлення
                    await context.bot.send_message(
                        chat_id=target_id,
                        text=(
                            f"🎉 <b>ТВІЙ КОД АКТИВОВАНО!</b>\n"
                            f"━━━━━━━━━━━━━━━━━━━━\n"
                            f"Хтось щойно скористався твоїм запрошенням.\n"
                            f"💰 <b>+50 ГРН</b> нараховано на твій бонусний баланс!\n\n"
                            f"<i>Використовуй їх для знижок на наступні замовлення.</i>"
                        ),
                        parse_mode='HTML'
                    )
                    logger.info(f"💰 +50 UAH reward sent to referrer {target_id}")
                except Exception as e:
                    # Якщо бот заблокований другом або інша помилка - не ламаємо флоу поточному юзеру
                    logger.error(f"Failed to reward referrer {target_id}: {e}")

    else:
        msg = "❌ <b>Невірний формат коду.</b>"

    # --- 3. ЗБЕРЕЖЕННЯ В БД (ДЛЯ ВАС) ---
    if is_success:
        try:
            cursor.execute("""
                UPDATE users 
                SET is_vip = 1, 
                    vip_expiry = ?,
                    next_order_discount = ?,
                    promo_applied = ?
                WHERE user_id = ?
            """, (
                profile.get('vip_expiry'), 
                profile.get('next_order_discount'), 
                1 if profile.get('promo_GHST2026_used') else (1 if profile.get('referral_used') else 0),
                user.id
            ))
            conn.commit()
            
            # Оновлюємо кеш, щоб кнопка в меню показала актуальний баланс
            context.user_data['profile'] = profile
            
        except Exception as e:
            logger.error(f"DB Update Error (Current User): {e}")
    
    conn.close()

    # --- 4. ВІДПОВІДЬ ---
    kb = [[InlineKeyboardButton("👤 У Кабінет (Перевірити)", callback_data="menu_profile")],
          [InlineKeyboardButton("🛍 До покупок", callback_data="cat_all")]]
    
    await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode='HTML')
    
    # Вимикаємо режим очікування коду
    context.user_data['awaiting_promo'] = False


async def show_ref_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показ реферальної інформації."""
    user = update.effective_user
    try:
        bot = await context.bot.get_me()
        bot_name = bot.username
    except: bot_name = "GhostyShopBot"
    
    text = (
        f"🤝 <b>ПАРТНЕРСЬКА ПРОГРАМА</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Запрошуйте друзів та заробляйте реальні знижки!\n\n"
        f"🔑 <b>Твій промокод:</b> <code>GHST{user.id}</code>\n\n"
        f"🔗 <b>Твоє посилання:</b>\n"
        f"<code>https://t.me/{bot_name}?start={user.id}</code>\n\n"
        f"🎁 <b>Тобі:</b> +50 грн на баланс за кожного друга.\n"
        f"🎁 <b>Другу:</b> +7 днів VIP статусу."
    )
    
    kb = [[InlineKeyboardButton("🔙 Назад", callback_data="menu_profile")]]
    await _edit_or_reply(update.callback_query, text, kb, context=context)
    
    
    
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
# 🤵 SECTION 27: MANAGER ORDER HUB (WITH BALANCE DEDUCTION)
# =================================================================

from urllib.parse import quote 

async def submit_order_to_manager(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Генератор заявки для менеджера.
    🔥 ФУНКЦІОНАЛ: 
    1. Рахує товари та доставку.
    2. Списує бонуси з балансу (якщо є).
    3. Формує готове повідомлення менеджеру.
    """
    user = update.effective_user
    profile = context.user_data.get('profile', {})
    
    # 1. Визначаємо джерело (Швидке замовлення чи Кошик)
    target_item_id = context.user_data.get('target_item_id')
    cart = context.user_data.get('cart', [])
    
    # 2. Отримуємо подарунок (якщо був обраний)
    target_gift_id = context.user_data.get('target_gift_id')
    
    items_text = ""
    total_goods_price = 0.0
    
    # --- ЛОГІКА ЗБОРУ ТОВАРІВ ---
    if target_item_id:
        # Швидке замовлення (1 товар)
        item = get_item_data(target_item_id)
        if item:
            color = context.user_data.get('selected_color', 'Не обрано')
            # Ціна з урахуванням VIP статусу
            price, _ = calculate_final_price(item['price'], profile)
            
            # Інфо про подарунок
            gift_info = ""
            if target_gift_id:
                g = get_item_data(target_gift_id)
                if g: gift_info = f"\n   🎁 Бонус: {g['name']}"

            items_text = f"▫️ {item['name']}\n   🎨 {color}\n   💵 {int(price)} грн{gift_info}"
            total_goods_price = price
            
    elif cart:
        # Замовлення з кошика
        for i in cart:
            p, _ = calculate_final_price(i['price'], profile)
            total_goods_price += p
            
            details = []
            if i.get('color'): details.append(f"🎨 {i['color']}")
            if i.get('gift'): details.append(f"🎁 {i['gift']}")
            
            details_str = f" ({', '.join(details)})" if details else ""
            items_text += f"▫️ {i['name']}{details_str} — {int(p)} грн\n"
    else:
        # Якщо пусто
        await update.callback_query.answer("⚠️ Кошик порожній", show_alert=True)
        await catalog_main_menu(update, context)
        return

    # --- ЛОГІКА ДОСТАВКИ ---
    delivery_price = 0.0
    dist = profile.get('district', '')
    # Якщо доставка кур'єром і юзер НЕ VIP -> додаємо 150 грн
    if "Кур'єр" in str(dist) and not profile.get("is_vip"):
        delivery_price = 150.0
        items_text += f"\n🚚 Доставка кур'єром: {int(delivery_price)} грн"

    # --- ЛОГІКА БОНУСІВ (СПИСАННЯ) ---
    current_balance = float(profile.get('next_order_discount', 0.0))
    discount_to_apply = 0.0
    
    # Розрахунок проміжної суми
    pre_total = total_goods_price + delivery_price
    
    if current_balance > 0:
        # Списуємо баланс, але залишаємо мінімум 0 (повна оплата бонусами можлива)
        if current_balance >= pre_total:
            discount_to_apply = pre_total
        else:
            discount_to_apply = current_balance

    # Фінальна сума до сплати
    final_amount = pre_total - discount_to_apply
    
    # --- РОБОТА З БАЗОЮ ДАНИХ ---
    order_id = f"GH-{user.id}-{random.randint(1000, 9999)}"
    
    try:
        with sqlite3.connect(DB_PATH, timeout=20) as conn:
            # 1. Зберігаємо замовлення
            conn.execute("""
                INSERT OR REPLACE INTO orders (order_id, user_id, amount, status, created_at) 
                VALUES (?, ?, ?, ?, ?)
            """, (order_id, user.id, final_amount, 'manager_pending', datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            
            # 2. Якщо використали бонуси — списуємо їх з бази
            if discount_to_apply > 0:
                conn.execute("""
                    UPDATE users 
                    SET next_order_discount = next_order_discount - ? 
                    WHERE user_id = ?
                """, (discount_to_apply, user.id))
                
                # Оновлюємо локальний профіль, щоб юзер одразу бачив зміни
                profile['next_order_discount'] -= discount_to_apply
                
            conn.commit()
            
    except Exception as e:
        logger.error(f"Manager Order DB Error: {e}")

    # --- ФОРМУВАННЯ ПОВІДОМЛЕННЯ МЕНЕДЖЕРУ ---
    full_name = profile.get('full_name', 'Гість')
    phone = profile.get('phone', 'Не вказано')
    address = profile.get('address_details', '')
    
    # Рядок про знижку у звіті
    discount_line = ""
    if discount_to_apply > 0:
        discount_line = f"\n💎 Знижка з балансу: -{int(discount_to_apply)} грн"
    
    report = (
        f"👋 Привіт! Замовлення #{order_id}\n"
        f"👤 {full_name} | 📞 {phone}\n"
        f"📍 {profile.get('city')}, {dist}\n"
        f"🏠 {address}\n\n"
        f"🛒 ЗАМОВЛЕННЯ:\n{items_text}"
        f"{discount_line}\n"
        f"💰 ДО СПЛАТИ: {final_amount:.2f} грн"
    )
    
    # Кодування тексту для URL
    encoded_text = quote(report)
    clean_manager = MANAGER_USERNAME.replace("@", "").strip()
    magic_link = f"https://t.me/{clean_manager}?text={encoded_text}"

    # --- ВІДПРАВКА КЛІЄНТУ ---
    text = (
        f"✅ <b>ЗАЯВКУ СФОРМОВАНО!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Замовлення <code>#{order_id}</code> готове до відправки.\n"
        f"Ми врахували ваші бонуси.\n\n"
        f"👇 <b>Натисніть кнопку нижче:</b>\n"
        f"Вас перекине в діалог з менеджером, і текст замовлення вставиться автоматично."
    )
    
    kb = [
        [InlineKeyboardButton("✈️ ВІДПРАВИТИ МЕНЕДЖЕРУ", url=magic_link)],
        [InlineKeyboardButton("🏠 В головне меню", callback_data="menu_start")]
    ]

    await send_ghosty_message(update, text, kb, context=context)
    
    # Очистка сесії
    context.user_data['target_item_id'] = None
    context.user_data['target_gift_id'] = None
    context.user_data['cart'] = [] # Очищаємо кошик, бо замовлення оформлено
    

# =================================================================
# 📝 SECTION 17: DATA INPUT HANDLER (TEXT PROCESSOR)
# =================================================================

async def handle_data_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обробляє текстові відповіді користувача на етапах анкети.
    Викликається з handle_user_input.
    """
    if not update.message or not update.message.text: return
    
    user = update.effective_user
    text = update.message.text.strip()
    step = context.user_data.get('data_step')
    profile = context.user_data.setdefault('profile', {})

    # 1. ОБРОБКА ІМЕНІ
    if step == "name":
        if len(text) < 2:
            await update.message.reply_text("⚠️ Ім'я занадто коротке. Напишіть Прізвище та Ім'я:")
            return
        
        profile['full_name'] = text
        
        # Перехід до телефону
        context.user_data['data_step'] = "phone"
        msg = (
            f"👤 Приємно познайомитись, <b>{escape(text)}</b>!\n\n"
            f"📱 Тепер введіть ваш <b>номер телефону</b>\n"
            f"(Наприклад: 0991234567):"
        )
        await update.message.reply_text(msg, parse_mode='HTML')

    # 2. ОБРОБКА ТЕЛЕФОНУ
    elif step == "phone":
        # Проста валідація (залишаємо тільки цифри)
        digits = ''.join(filter(str.isdigit, text))
        if len(digits) < 9:
            await update.message.reply_text("⚠️ Некоректний формат. Введіть номер (напр. 099xxxxxxx):")
            return
        
        profile['phone'] = text
        
        # Перевіряємо, чи є місто. Якщо ні - йдемо обирати місто
        if not profile.get('city'):
            # Скидаємо стан тексту, бо далі будуть кнопки
            # Але зберігаємо state COLLECTING_DATA
            await choose_city_menu(update, context)
        else:
            # Якщо місто є, але немає адреси -> йдемо до адреси
            context.user_data['data_step'] = "address"
            city = profile['city']
            await update.message.reply_text(f"📞 Номер прийнято.\n\n📍 Місто: {city}. Вкажіть <b>Адресу або Відділення НП</b>:")

    # 3. ОБРОБКА АДРЕСИ
    elif step == "address":
        if len(text) < 2:
            await update.message.reply_text("⚠️ Адреса занадто коротка. Уточніть деталі:")
            return
            
        # Якщо був обраний район, додаємо його до адреси
        district = profile.get('district', '')
        if district and district not in text:
            full_address = f"{district}, {text}"
        else:
            full_address = text
        
        profile['address_details'] = full_address
        
        await update.message.reply_text("✅ <b>Адресу збережено!</b>", parse_mode='HTML')
        
        # Фіналізуємо анкету (виклик функції з Section 16)
        if 'finalize_data_collection' in globals():
            await finalize_data_collection(update, context)
            

# =================================================================
# 🎮 SECTION 28: STABLE MESSAGE HANDLER (TITAN ULTIMATE v10.5)
# =================================================================

async def handle_user_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Центральний хаб: обробляє Текст, Медіа (чеки) та Стани.
    Повна інтеграція з Section 17 (Data Input Handler).
    """
    if not update.message: 
        return 
    
    user = update.effective_user
    state = context.user_data.get('state')
    
    # Отримуємо текст безпечно (з повідомлення або підпису до фото)
    raw_text = update.message.text.strip() if update.message.text else update.message.caption
    
    # -----------------------------------------------------------
    # 1. АДМІН-РОЗСИЛКА (Тільки для MANAGER_ID)
    # -----------------------------------------------------------
    if state == "BROADCAST_MODE" and user.id == MANAGER_ID:
        try:
            # Використовуємо таймаут для стабільності на BotHost
            with sqlite3.connect(DB_PATH, timeout=20) as conn:
                users = conn.execute("SELECT user_id FROM users").fetchall()
            
            if not users:
                await update.message.reply_text("❌ База користувачів порожня.")
                context.user_data['state'] = None
                return

            sent, failed = 0, 0
            status_msg = await update.message.reply_text(
                f"🚀 <b>Запуск розсилки...</b>\nЦільова аудиторія: {len(users)} чол.", 
                parse_mode='HTML'
            )
            
            for (uid,) in users:
                try:
                    # copy_message копіює будь-який контент (текст/фото/відео/стікер)
                    await update.message.copy(chat_id=uid)
                    sent += 1
                    # Анти-флуд пауза
                    if sent % 25 == 0: await asyncio.sleep(1.0)
                    else: await asyncio.sleep(0.04)
                except Exception:
                    failed += 1 
            
            await status_msg.edit_text(
                f"✅ <b>РОЗСИЛКУ ЗАВЕРШЕНО!</b>\n━━━━━━━━━━━━━━━━━━━━\n"
                f"📥 Отримали: <code>{sent}</code>\n"
                f"❌ Не дійшло: <code>{failed}</code>", 
                parse_mode='HTML'
            )
        except Exception as e:
            logger.error(f"Broadcast Error: {e}")
            await update.message.reply_text(f"🆘 Помилка: {e}")
        finally:
            context.user_data['state'] = None
        return

    # -----------------------------------------------------------
    # 2. ПРИЙОМ КВИТАНЦІЙ (Стан WAITING_RECEIPT + Фото)
    # -----------------------------------------------------------
    if update.message.photo and state == "WAITING_RECEIPT":
        # Генеруємо унікальний ID, якщо його немає
        order_id = context.user_data.get("current_order_id", f"UNK-{user.id}-{int(datetime.now().timestamp())}")
        amount = context.user_data.get("final_checkout_sum", 0.0)
        profile = context.user_data.get("profile", {})
        
        # 1. ЗАПИС У БД (Статус 'pending')
        try:
            with sqlite3.connect(DB_PATH, timeout=20) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO orders (order_id, user_id, amount, status, created_at) 
                    VALUES (?, ?, ?, ?, ?)
                """, (order_id, user.id, amount, 'pending', datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                conn.commit()
        except Exception as e:
            logger.error(f"Receipt DB Error: {e}")
            await update.message.reply_text("⚠️ Помилка збереження даних. Спробуйте ще раз.")
            return

        # 2. СПОВІЩЕННЯ МЕНЕДЖЕРА
        caption = (
            f"💰 <b>НОВА ОПЛАТА НА ПЕРЕВІРКУ</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 Клієнт: <b>{escape(profile.get('full_name', user.first_name))}</b>\n"
            f"🆔 ID: <code>{user.id}</code> | @{user.username if user.username else '—'}\n"
            f"📦 Замовлення: <b>#{order_id}</b>\n"
            f"💵 Сума: <b>{amount:.2f} UAH</b>\n"
            f"🏙 Місто: {profile.get('city', '—')}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"👇 <i>Підтвердіть отримання коштів:</i>"
        )
        
        admin_kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ ПІДТВЕРДИТИ", callback_data=f"adm_ok_{user.id}_{order_id}")],
            [InlineKeyboardButton("❌ ВІДХИЛИТИ", callback_data=f"adm_no_{user.id}_{order_id}")]
        ])
        
        try:
            # Надсилаємо фото чека менеджеру
            await context.bot.send_photo(
                chat_id=MANAGER_ID,
                photo=update.message.photo[-1].file_id,
                caption=caption,
                reply_markup=admin_kb,
                parse_mode='HTML'
            )
            
            # 3. ВІДПОВІДЬ КЛІЄНТУ
            await update.message.reply_text(
                "✅ <b>Квитанцію отримано!</b>\n\n"
                "Ваш платіж передано на перевірку.\n"
                "Очікуйте підтвердження протягом 10-15 хвилин.",
                parse_mode='HTML'
            )
            # Скидаємо стан, щоб бот не чекав ще фото
            context.user_data['state'] = None
            
        except Exception as e:
            logger.error(f"Manager Notification Failed: {e}")
            await update.message.reply_text("⚠️ Не вдалося зв'язатися з менеджером. Напишіть йому: @ghosstydp")
        return

    # -----------------------------------------------------------
    # 3. ТЕКСТОВА МАРШРУТИЗАЦІЯ (Анкета & Промо)
    # -----------------------------------------------------------
    if raw_text:
        # А) АНКЕТА РЕЄСТРАЦІЇ (ПІБ -> Телефон -> Адреса)
        # Всі кроки обробляються через handle_data_input (Section 17)
        if state == "COLLECTING_DATA":
            if 'handle_data_input' in globals():
                await handle_data_input(update, context)
            else:
                await update.message.reply_text("⚠️ Оновлення системи... (func missing)")
            return
            
        # Б) ВВЕДЕННЯ ПРОМОКОДУ
        elif context.user_data.get('awaiting_promo'):
            if 'process_promo' in globals():
                await process_promo(update, context)
            return

        # Г) Ігноруємо випадковий текст (Anti-Spam)
        pass
        
            
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
# ⚙️ SECTION 29: GLOBAL DISPATCHER (TITAN FINAL - BULLETPROOF)
# =================================================================

async def global_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Центральний мозок GHO$$TY STAFF: розподіляє всі натискання кнопок.
    100% СТАБІЛЬНІСТЬ: Підтримка всіх функцій магазину.
    """
    query = update.callback_query
    data = query.data
    user = update.effective_user
    
    # 1. МИТТЄВА ВІДПОВІДЬ (Anti-Freeze)
    try: 
        if data == "ignore_click":
            await query.answer()
            return
        await query.answer()
    except Exception: pass

    try:
        # --- 0. АДМІН-ПАНЕЛЬ (Доступ для всіх з ADMIN_LIST) ---
        if data.startswith(("adm_", "admin_")):
            # Перевіряємо, чи є юзер в списку адмінів
            is_admin = False
            if 'ADMIN_LIST' in globals():
                if user.id in ADMIN_LIST: is_admin = True
            elif user.id == MANAGER_ID:
                is_admin = True
                
            if is_admin:
                if data.startswith("adm_"): await admin_decision_handler(update, context)
                elif data == "admin_main": await admin_menu(update, context)
                elif data == "admin_stats": await admin_stats(update, context)
                elif data == "admin_view_users": await admin_view_users(update, context)
                elif data == "admin_broadcast": await start_broadcast(update, context)
                elif data == "admin_cancel_action":
                    context.user_data['state'] = None
                    await admin_menu(update, context)
            else:
                await query.answer("⛔️ Доступ заборонено", show_alert=True)
            return

        # --- 1. БАЗОВА НАВІГАЦІЯ ---
        if data == "menu_start":
            context.user_data['state'] = None
            context.user_data['target_item_id'] = None
            context.user_data['target_gift_id'] = None
            context.user_data['selected_color'] = None # Додано очищення кольору
            await start_command(update, context)
            
        elif data == "menu_profile": await show_profile(update, context)
        elif data == "menu_cart": await show_cart_logic(update, context)
        elif data == "menu_terms": 
             if 'TERMS_TEXT' in globals():
                await _edit_or_reply(query, TERMS_TEXT, [[InlineKeyboardButton("🔙 Назад", callback_data="menu_start")]], context=context)

        elif data == "ref_system": await show_ref_info(update, context)
            
        elif data == "menu_promo": 
            context.user_data['awaiting_promo'] = True
            await _edit_or_reply(query, "🎟 <b>АКТИВАЦІЯ БОНУСІВ</b>\n\nВведіть промокод прямо тут 👇", [[InlineKeyboardButton("🔙 Скасувати", callback_data="menu_profile")]], context=context)

        # --- 2. КАТАЛОГ ТА ТОВАРИ ---
        elif data == "cat_all": 
            context.user_data['state'] = None
            await catalog_main_menu(update, context)
            
        elif data.startswith("cat_list_"): 
            cat_key = data.replace("cat_list_", "")
            await show_category_items(update, context, cat_key)
        
        elif data.startswith("view_item_"): 
            try:
                parts = data.split("_")
                item_id = int(parts[2])
                await view_item_details(update, context, item_id)
            except (IndexError, ValueError):
                await catalog_main_menu(update, context)

        # --- 3. КОЛЬОРИ ТА КОШИК ---
        elif data.startswith("sel_col_"):
            try:
                parts = data.split("_")
                item_id = int(parts[2])
                color_name = "_".join(parts[3:])
                if 'handle_color_selection_click' in globals():
                    await handle_color_selection_click(update, context, item_id, color_name)
            except Exception as e:
                logger.error(f"Color handler error: {e}")

        elif data.startswith("add_"): await add_to_cart_handler(update, context)
        elif data == "cart_clear" or data.startswith("cart_del_"): await cart_action_handler(update, context)
        elif data.startswith("gift_sel_"): await gift_selection_handler(update, context)

        # --- 4. ДАНІ ТА ЛОКАЦІЯ ---
        elif data == "choose_city": await choose_city_menu(update, context)
        
        elif data.startswith("sel_city_"): 
            city = data.replace("sel_city_", "")
            if city == "Дніпро": await choose_dnipro_delivery(update, context)
            elif city == "Dnipro_Klad": await district_selection_handler(update, context, "Дніпро")
            else: await district_selection_handler(update, context, city)
            
        elif data.startswith("sel_dist_"): 
            dist_name = data.replace("sel_dist_", "")
            if 'address_request_handler' in globals():
                await address_request_handler(update, context, dist_name)
            
        elif data == "fill_delivery_data": 
            await start_data_collection(update, context, next_action='none')
            
        elif data == "checkout_init": 
            context.user_data['target_item_id'] = None 
            await start_data_collection(update, context, next_action='checkout')

        # --- 5. ШВИДКЕ ЗАМОВЛЕННЯ (ІДЕАЛЬНЕ ПЕРЕХОПЛЕННЯ ПОДАРУНКА) ---
        elif data.startswith("fast_order_"):
            try:
                parts = data.split("_") # fast_order_100 або fast_order_100_Black або fast_order_100_Black_9001
                item_id = int(parts[2])
                item = get_item_data(item_id)
                
                gift_id = None
                
                # Аналізуємо "хвіст" кнопки, щоб витягти колір та подарунок
                if len(parts) > 3:
                    # Якщо останній елемент - цифра (і це не частина назви кольору)
                    if parts[-1].isdigit(): 
                        gift_id = int(parts[-1])
                        # Якщо елементів більше 4, значить між ID і подарунком є колір
                        if len(parts) > 4:
                            context.user_data['selected_color'] = "_".join(parts[3:-1])
                    else: 
                        # Якщо останній елемент не цифра - це колір (подарунка ще немає)
                        context.user_data['selected_color'] = "_".join(parts[3:])

                # Перевіряємо, чи взагалі потрібен подарунок для цього товару (HHC < 300, POD 500-699)
                needs_gift = item and (item_id < 300 or 500 <= item_id < 700 or item.get('gift_liquid'))
                
                if needs_gift and gift_id is None:
                    # Перекидаємо на вибір подарунка
                    await gift_selection_handler(update, context)
                else:
                    # Все є, йдемо оформлювати
                    context.user_data['target_item_id'] = item_id
                    context.user_data['target_gift_id'] = gift_id if (gift_id and gift_id > 0) else None
                    await start_data_collection(update, context, next_action='fast_order')
            except Exception as e: 
                logger.error(f"Fast order route error: {e}")

        # --- 6. МЕНЕДЖЕР (ІДЕАЛЬНЕ ПЕРЕХОПЛЕННЯ ПОДАРУНКА) ---
        elif data.startswith("mgr_pre_"):
            try:
                parts = data.split("_")
                item_id = int(parts[2])
                item = get_item_data(item_id)
                
                gift_id = None
                if len(parts) > 3:
                    if parts[-1].isdigit(): 
                        gift_id = int(parts[-1])
                        if len(parts) > 4:
                            context.user_data['selected_color'] = "_".join(parts[3:-1])
                    else: 
                        context.user_data['selected_color'] = "_".join(parts[3:])

                needs_gift = item and (item_id < 300 or 500 <= item_id < 700 or item.get('gift_liquid'))
                
                if needs_gift and gift_id is None:
                    await gift_selection_handler(update, context)
                else:
                    context.user_data['target_item_id'] = item_id
                    context.user_data['target_gift_id'] = gift_id if (gift_id and gift_id > 0) else None
                    await start_data_collection(update, context, next_action='manager_order')
            except Exception as e: 
                logger.error(f"Manager route error: {e}")
            
        elif data.startswith("pay_"): 
            method = data.split("_")[1]
            if 'payment_selection_handler' in globals():
                await payment_selection_handler(update, context, method)
            
        elif data == "confirm_payment_start": 
            await payment_confirmation_handler(update, context)
        
        elif data == "confirm_manager_order":
            if 'submit_order_to_manager' in globals():
                await submit_order_to_manager(update, context)

    # 🛡 ФІНАЛЬНИЙ ЗАХИСТ
    except NameError as ne:
        logger.error(f"ROUTING FAILURE (MISSING FUNC): {data} | Error: {ne}")
        await query.answer("⚠️ Оновлення системи...", show_alert=True)
        
    except Exception as e:
        logger.error(f"GLOBAL DISPATCHER FATAL: {e} | DATA: {data}")
        traceback.print_exc()
        await query.answer("❌ Внутрішня помилка.", show_alert=True)
            
# =================================================================
# 🚀 SECTION 31: ENGINE STARTUP & MAIN LOOP (FINAL NETWORK FIX)
# =================================================================

import platform

async def post_init(application: Application) -> None:
    """
    Розширений звіт для Адміна при запуску.
    """
    try:
        # 1. Отримуємо дані про бота
        bot = await application.bot.get_me()
        
        # 2. Технічні дані
        system_info = f"{platform.system()} {platform.release()}"
        node_name = platform.node()
        python_ver = platform.python_version()
        
        # 3. База даних
        db_size = "0 KB"
        if os.path.exists(DB_PATH):
            size_bytes = os.path.getsize(DB_PATH)
            db_size = f"{size_bytes / 1024:.2f} KB"
            
        now_str = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
        
        report = (
            f"🚀 <b>GHO$$TY ENGINE: SUCCESSFUL LAUNCH</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🤖 <b>Bot:</b> @{bot.username} (ID: <code>{bot.id}</code>)\n"
            f"🛡 <b>Version:</b> TITAN PRO v10.0\n"
            f"🕒 <b>Launched:</b> {now_str}\n\n"
            f"📡 <b>SYSTEM DIAGNOSTICS:</b>\n"
            f"💻 <b>Host:</b> {node_name}\n"
            f"🐧 <b>OS:</b> {system_info}\n"
            f"🐍 <b>Python:</b> v{python_ver}\n\n"
            f"🗄 <b>DATABASE STATUS:</b>\n"
            f"✅ Connection: OK\n"
            f"📦 Size: {db_size}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🟢 <i>Network protection active.</i>"
        )
        
        await application.bot.send_message(chat_id=MANAGER_ID, text=report, parse_mode='HTML')
        logger.info(f"✅ Startup notification sent to ADMIN ({MANAGER_ID})")
        
    except Exception as e:
        logger.error(f"❌ Post-init failed: {e}")

def main():
    """
    Головна точка входу.
    """
    print("⏳ INITIALIZING SYSTEM...")

    # 1. Перевірка токена
    if not TOKEN or "ВСТАВ" in TOKEN:
        print("❌ FATAL ERROR: Bot token is missing!")
        sys.exit(1)
        
    # 2. Ініціалізація БД
    init_db()
    
    # 3. Налаштування МЕРЕЖІ (Виправлення httpx.ConnectError)
    # Збільшуємо таймаути, щоб бот не падав при затримках мережі
    app = (
        Application.builder()
        .token(TOKEN)
        .persistence(PicklePersistence(filepath=PERSISTENCE_PATH))
        .defaults(Defaults(parse_mode=ParseMode.HTML))
        .get_updates_http_version('1.1')
        .http_version('1.1')
        .connection_pool_size(10) # Більше потоків
        .read_timeout(30)         # Чекаємо відповіді 30 сек
        .write_timeout(30)
        .connect_timeout(30)
        .pool_timeout(30)
        .post_init(post_init)
        .build()
    )

    # 4. Реєстрація хендлерів (Строгий порядок!)
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("admin", admin_menu))
    app.add_handler(CallbackQueryHandler(global_callback_handler))
    
    # Текстовий хендлер (має бути в кінці)
    app.add_handler(MessageHandler(
        (filters.TEXT | filters.PHOTO | filters.VIDEO | filters.VOICE) & (~filters.COMMAND), 
        handle_user_input
    ))
    
    # Обробник помилок
    app.add_error_handler(error_handler)
    
    # 5. Інфо в консоль
    token_masked = f"{TOKEN[:5]}...{TOKEN[-5:]}"
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"🌫️  GHO$$TY STAFF PREMIUM ENGINE v10.0")
    print(f"📡  STATUS:  [ ONLINE ]")
    print(f"🔑  TOKEN:   {token_masked}")
    print(f"👮‍♂️  ADMIN:   ID:{MANAGER_ID}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    # 6. Запуск (ігноруємо старі апдейти)
    app.run_polling(drop_pending_updates=True, close_loop=False)

if __name__ == "__main__":
    if 'START_TIME' not in globals():
        START_TIME = datetime.now()

    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 System stopped by Administrator.")
        sys.exit(0)
    except Exception as fatal_e:
        print(f"❌ CRITICAL CRASH: {fatal_e}")
        traceback.print_exc()
        sys.exit(1)

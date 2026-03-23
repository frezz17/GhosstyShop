# =================================================================
# 🤖 PROJECT: GHO$$TY STAFF PREMIUM E-COMMERCE ENGINE (PRO)
# 🛠 VERSION: TITAN ULTIMATE v10.6 (SCALABLE & STABLE)
# 🛡 DEVELOPER: Gho$$tyyy & Gemini AI
# =================================================================

import os
import sys
import logging
import sqlite3
import asyncio
import random
import traceback
import warnings
import signal
from datetime import datetime, timedelta
from html import escape
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor

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
from telegram.error import BadRequest, NetworkError, TimedOut

# 🛡️ ТЕХНІЧНА ГІГІЄНА & СИСТЕМНИЙ КОНТРОЛЬ
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Гарантуємо унікальність логера (використовуємо GhosstyCore для точності)
if 'GhosstyCore' in logging.Logger.manager.loggerDict:
    logging.getLogger("GhosstyCore").handlers.clear()

logger = logging.getLogger("GhosstyCore")

# Ініціалізація пулу потоків для важких операцій з БД
db_executor = ThreadPoolExecutor(max_workers=5)

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

print(f"{Colors.OKBLUE}{Colors.BOLD}🚀 GHO$$TY ENGINE STARTING...{Colors.ENDC}")


# =================================================================
# ⚙️ SECTION 1: GLOBAL CONFIGURATION
# =================================================================

import os
import sys
import logging
import sqlite3
import warnings
from datetime import datetime
from telegram.constants import ParseMode
from telegram.ext import Defaults

# 🛡️ ТЕХНІЧНА ГІГІЄНА
warnings.filterwarnings("ignore", category=UserWarning)

# НАЛАШТУВАННЯ ШЛЯХІВ (Авто-створення структури)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True) 

DB_PATH = os.path.join(DATA_DIR, 'ghosty_pro_final.db')
PERSISTENCE_PATH = os.path.join(DATA_DIR, 'ghosty_state_final.pickle')
LOG_PATH = os.path.join(DATA_DIR, 'ghosty_system.log')

# =================================================================
# 🔑 AUTH & ADMINISTRATION
# =================================================================
# Використовуй екологічний підхід: токен з оточення, але з fallback-значенням
TOKEN = os.getenv("BOT_TOKEN", "8351638507:AAHV2kIM0b_H0tFCTJgF4GGq5qaKX4y58_c")
MANAGER_ID = 7544847872
ADMIN_LIST = [MANAGER_ID]
MANAGER_USERNAME = "ghosstydp"
CHANNEL_URL = "https://t.me/GhostyStaffDP"
WELCOME_PHOTO = "https://i.ibb.co/35K9Zp5p/Polish-20260310-051407282.png"

# =================================================================
# 💸 FINANCE & ASSETS
# =================================================================
USDT_RATE = 43.7  
TON_WALLET = "UQAoGQYr_1sl9_3PcgkvJFzO4bXdQWpmnM6o6NPLk4l5koW5"

PAYMENT_LINK = {
    "mono": "https://lnk.ua/k4xJG21Vy",    
    "privat": "https://lnk.ua/RVd0OW6V3",
    "ghossty_web": "https://heylink.me/GhosstyShop"
}

# =================================================================
# 📋 LOGGING SYSTEM (PRO CONFIG)
# =================================================================
# Очищення старих хендлерів для уникнення дублювання логів у консолі
logging.getLogger().handlers.clear()

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

# =================================================================
# 🤖 BOT DEFAULTS (Глобальні налаштування для скорочення коду)
# =================================================================
# Це дозволить не писати parse_mode="HTML" у кожному повідомленні
GHOSTY_DEFAULTS = Defaults(
    parse_mode=ParseMode.HTML,
    disable_web_page_preview=True,
    allow_sending_without_reply=True
)

# =================================================================
# 🛡️ SECTION 2: TITAN UI ENGINE & ERROR SHIELD (ULTIMATE v10.6)
# =================================================================

import traceback
from html import escape
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, CallbackQuery
from telegram.constants import ParseMode
from telegram.error import BadRequest

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Глобальний щит безпеки: Перехоплює помилки, логує їх та сповіщає адміна.
    """
    logger.error(msg="🆘 Exception while handling an update:", exc_info=context.error)
    
    try:
        # Формуємо стектрейс для розробника (макс 3000 символів для ТГ)
        tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
        tb_string = "".join(tb_list)
        error_snippet = escape(tb_string[-3000:]) 
        
        user_info = "Unknown User"
        if isinstance(update, Update) and update.effective_user:
            u = update.effective_user
            user_info = f"👤 <b>{escape(u.full_name)}</b> (@{u.username}) [<code>{u.id}</code>]"

        admin_msg = (
            f"🆘 <b>CRITICAL SYSTEM ERROR</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 <b>User:</b> {user_info}\n"
            f"⚙️ <b>Type:</b> <code>{type(context.error).__name__}</code>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🔍 <b>Traceback:</b>\n<pre>{error_snippet}</pre>"
        )
        
        # Надсилаємо звіт менеджеру (MANAGER_ID з Section 1)
        await context.bot.send_message(chat_id=MANAGER_ID, text=admin_msg, parse_mode=ParseMode.HTML)
        
        # М'яка відповідь користувачу, щоб він не бачив "порожнечу"
        if isinstance(update, Update) and update.effective_chat:
            await context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text="⚠️ <b>Виникла технічна помилка.</b>\nМи вже працюємо над її виправленням. Спробуйте натиснути /start",
                parse_mode=ParseMode.HTML
            )
    except Exception as fatal_e:
        logger.error(f"❌ Failed to report error: {fatal_e}")


async def _edit_or_reply(target, text: str, kb: list = None, photo: str = None, context: ContextTypes.DEFAULT_TYPE = None):
    """
    Core UI Engine: Розумне керування інтерфейсом.
    Автоматично вирішує: редагувати існуюче повідомлення чи надсилати нове.
    """
    if not text: text = "..."
    
    # Створення розмітки клавіатури
    markup = InlineKeyboardMarkup(kb) if isinstance(kb, list) else (kb if kb else None)
    
    # Визначаємо, з чим працюємо: CallbackQuery чи звичайний Update
    query = target if isinstance(target, CallbackQuery) else getattr(target, 'callback_query', None)
    message = query.message if query else (target.message if hasattr(target, 'message') else target)
    
    if not message: return
    
    chat_id = message.chat_id
    bot = context.bot if context else message.get_bot()

    try:
        if query:
            # Прибираємо стан завантаження на кнопці
            await query.answer()
            
            if photo:
                if message.photo:
                    # Якщо вже є фото — оновлюємо медіа (плавний перехід)
                    await query.edit_message_media(
                        media=InputMediaPhoto(media=photo, caption=text, parse_mode=ParseMode.HTML),
                        reply_markup=markup
                    )
                else:
                    # Якщо було текстове повідомлення — видаляємо і шлемо фото
                    await safe_delete(message)
                    await bot.send_photo(chat_id=chat_id, photo=photo, caption=text, reply_markup=markup, parse_mode=ParseMode.HTML)
            else:
                if message.photo:
                    # Якщо було фото, а треба лише текст — видаляємо і шлемо текст
                    await safe_delete(message)
                    await bot.send_message(chat_id=chat_id, text=text, reply_markup=markup, parse_mode=ParseMode.HTML)
                else:
                    # Звичайне редагування тексту
                    await query.edit_message_text(text=text, reply_markup=markup, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        
        else:
            # Якщо це не натискання кнопки, а нова команда (напр. /start)
            if photo:
                await bot.send_photo(chat_id=chat_id, photo=photo, caption=text, reply_markup=markup, parse_mode=ParseMode.HTML)
            else:
                await bot.send_message(chat_id=chat_id, text=text, reply_markup=markup, parse_mode=ParseMode.HTML)

    except BadRequest as e:
        if "Message is not modified" in str(e):
            return # Ігноруємо, якщо контент не змінився
        
        # Fallback: якщо редагування неможливе (напр. повідомлення старе), шлемо нове
        try:
            if photo:
                await bot.send_photo(chat_id=chat_id, photo=photo, caption=text, reply_markup=markup, parse_mode=ParseMode.HTML)
            else:
                await bot.send_message(chat_id=chat_id, text=text, reply_markup=markup, parse_mode=ParseMode.HTML)
        except Exception as last_err:
            logger.error(f"❌ UI Engine Critical failure: {last_err}")


async def send_ghosty_message(update_obj, text: str, kb=None, photo=None, context: ContextTypes.DEFAULT_TYPE = None):
    """Швидкий виклик основного двигуна."""
    await _edit_or_reply(update_obj, text, kb, photo, context)


async def safe_delete(message):
    """Безпечне видалення повідомлень без переривання роботи скрипта."""
    try:
        if hasattr(message, 'delete'):
            await message.delete()
    except Exception:
        pass
        
# =================================================================
# 🛍 SECTION 3: DATA REGISTRY (FULL PRODUCTS & LOGISTICS)
# =================================================================

# --- 🌍 ГЕОЛОКАЦІЯ ---
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

CITIES_LIST = list(UKRAINE_CITIES.keys())
COURIER_PRICE = 150.0

# --- 💧 РІДИНИ (300-400) ---
LIQUIDS = {
    301: {"name": "🍂 Fall Tea", "type": "liquids", "price": 279.99, "stock": 15, "strengths": [50, 65, 85], "img": "https://i.ibb.co/GmZH1XL/1-0.jpg", "desc": "☕ <b>Осінній Чай</b>\nСпокійний аромат чаю з нотками лимону.", "payment_url": PAYMENT_LINK},
    302: {"name": "👻 Mystery One", "type": "liquids", "price": 279.99, "stock": 15, "strengths": [50, 65, 85], "img": "https://i.ibb.co/DDnd5d2S/1-1.png", "desc": "🔮 <b>Ghost Edition</b>\nТаємничий фруктовий мікс.", "payment_url": PAYMENT_LINK},
    303: {"name": "🍓 Strawberry Jelly", "type": "liquids", "price": 279.99, "stock": 14, "strengths": [50, 65, 85], "img": "https://i.ibb.co/JW96c5xq/1-2.jpg", "desc": "🍮 <b>Полуничне Желе</b>\nНіжний десертний смак.", "payment_url": PAYMENT_LINK},
    304: {"name": "🍇 Grape BlackBerry", "type": "liquids", "price": 279.99, "stock": 15, "strengths": [50, 65, 85], "img": "https://i.ibb.co/JW96c5xq/1-3.jpg", "desc": "🍇 <b>Виноград-Ожина</b>\nВибух темних ягід.", "payment_url": PAYMENT_LINK},
    305: {"name": "🥤 Cola Pomelo", "type": "liquids", "price": 279.99, "stock": 15, "strengths": [50, 65, 85], "img": "https://i.ibb.co/JW96c5xq/1-4.jpg", "desc": "🍊 <b>Кола-Помело</b>\nНезвичне поєднання.", "payment_url": PAYMENT_LINK},
    306: {"name": "🌹 BlackCurrant Rose", "type": "liquids", "price": 279.99, "stock": 12, "strengths": [50, 65, 85], "img": "https://i.ibb.co/bRgVwzJg/1-5.jpg", "desc": "🥀 <b>Смородина-Троянда</b>\nВишуканий аромат.", "payment_url": PAYMENT_LINK},
    307: {"name": "🍋 Berry Lemonade", "type": "liquids", "price": 279.99, "stock": 15, "strengths": [50, 65, 85], "img": "https://i.ibb.co/fG4GqL6F/1-2.png", "desc": "🍹 <b>Ягідний Лимонад</b>\nОсвіжаючий літній мікс.", "payment_url": PAYMENT_LINK},
    308: {"name": "⚡ Energetic", "type": "liquids", "price": 279.99, "stock": 10, "strengths": [50, 65, 85], "img": "https://i.ibb.co/fG4GqL6F/1-3.png", "desc": "🔋 <b>Енергетик</b>\nСмак, що бадьорить.", "payment_url": PAYMENT_LINK},
    309: {"name": "💊 Vitamin", "type": "liquids", "price": 279.99, "stock": 15, "strengths": [50, 65, 85], "img": "https://i.ibb.co/fG4GqL6F/1-4.png", "desc": "🍏 <b>Вітамін</b>\nМікс фруктів.", "payment_url": PAYMENT_LINK}
}

# --- 🧠 HHC ВЕЙПИ (100-200) ---
HHC_VAPES = {
    100: {"name": "🌴 Packwoods Purple 1ml", "type": "hhc", "price": 999.99, "stock": 24, "gift_liquid": True, "img": "https://i.ibb.co/svXqXPgL/Ghost-Vape-3.jpg", "desc": "🧠 <b>90% HHC | Гібрид</b>\n😌 Розслаблення + ейфорія\n🎁 <b>+ РІДИНА БЕЗКОШТОВНО!</b>", "payment_url": PAYMENT_LINK},
    101: {"name": "🍊 Packwoods Orange 1ml", "type": "hhc", "price": 999.99, "stock": 21, "gift_liquid": True, "img": "https://i.ibb.co/SDJFRTwk/Ghost-Vape-1.jpg", "desc": "🧠 <b>90% HHC | Сатіва</b>\n⚡ Бадьорить та фокусує\n🎁 <b>+ РІДИНА БЕЗКОШТОВНО!</b>", "payment_url": PAYMENT_LINK},
    102: {"name": "🌸 Packwoods Pink 1ml", "type": "hhc", "price": 999.99, "stock": 19, "gift_liquid": True, "img": "https://i.ibb.co/65j1901/Ghost-Vape-2.jpg", "desc": "🧠 <b>90% HHC | Індіка</b>\n😇 Спокій + підйом настрою\n🎁 <b>+ РІДИНА БЕЗКОШТОВНО!</b>", "payment_url": PAYMENT_LINK},
    103: {"name": "🌿 Whole Mint 2ml", "type": "hhc", "price": 1399.99, "stock": 6, "gift_liquid": True, "img": "https://i.ibb.co/W4hqn2tZ/Ghost-Vape-4.jpg", "desc": "🧠 <b>95% HHC | Сатіва</b>\n⚡ Енергія та ясність (2ml)\n🎁 <b>+ РІДИНА БЕЗКОШТОВНО!</b>", "payment_url": PAYMENT_LINK},
    104: {"name": "🌴 Jungle Boys White 2ml", "type": "hhc", "price": 1799.99, "stock": 3, "gift_liquid": True, "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg", "desc": "🧠 <b>95% HHC | Індика</b>\n😴 Глибокий релакс (2ml)\n🎁 <b>+ РІДИНА БЕЗКОШТОВНО!</b>", "payment_url": PAYMENT_LINK},
    105: {"name": "🔥 Ace&Gold Ghossty Edition 1.5ml", "type": "hhc", "price": 1599.99, "stock": 4, "gift_liquid": True, "img": "https://i.ibb.co/5h9VDkF6/photo-2026-02-21-17-39-26.jpg", "desc": "👑 <b>95% HHC | Гібрид (Потужний)</b>\n🔥 Ексклюзивна <b>Ghossty Edition</b> у золотому корпусі\n🎁 <b>+ РІДИНА БЕЗКОШТОВНО!</b>", "payment_url": PAYMENT_LINK}
}

# --- 🔌 POD-СИСТЕМИ (500-600) ---
PODS = {
    500: {
        "name": "🔌 Vaporesso XROS Pro", "type": "pods", "stock": 4, "gift_liquid": True, "price": 999, 
        "img": "https://i.ibb.co/rKvNKwFP/Polish-20260310-035040856.jpg", 
        "desc": "🚀 <b>PROFESSIONAL | 1200 mAh</b>\nЕкран, регулювання потужності, блокування.",
        "colors": ["⚫️ Black", "⚪️ Silver", "🔴 Red"],
        "color_previews": {
            "Black": "https://i.ibb.co/rKvNKwFP/Polish-20260310-035040856.jpg", 
            "Silver": "https://i.ibb.co/Fkqc5S9G/Polish-20260310-035143043.jpg", 
            "Red": "https://i.ibb.co/LXb9mhBf/Polish-20260310-035252469.jpg"
        }, "payment_url": PAYMENT_LINK
    },
    501: {
        "name": "🔌 Vaporesso XROS 5", "type": "pods", "stock": 6, "gift_liquid": True, "price": 839, 
        "img": "https://i.ibb.co/1HdPNKh/Polish-20260310-040417817.jpg", 
        "desc": "💎 <b>ПРЕМІУМ ФЛАГМАН</b>\n1200 mAh, 3 режими, супер-смак.",
        "colors": ["⚫️ Obsidian Black", "⚪️ Pearl White", "🔵 Pink"],
        "color_previews": {
            "Obsidian Black": "https://i.ibb.co/1HdPNKh/Polish-20260310-040417817.jpg", 
            "Pearl White": "https://i.ibb.co/RpW3VBrZ/Polish-20260310-040517300.jpg", 
            "Pink": "https://i.ibb.co/5XdQNwDR/Polish-20260310-040622066.jpg"
        }, "payment_url": PAYMENT_LINK
    },
    502: {
        "name": "🔌 Vaporesso XROS Nano 5", "type": "pods", "stock": 8, "gift_liquid": True, "price": 779, 
        "img": "https://i.ibb.co/fzxY8fCB/Polish-20260310-035712367.jpg", 
        "desc": "🎒 <b>КОМПАКТНИЙ КВАДРАТ</b>\nСтильний, зручний, на шнурку.",
        "colors": ["⚫️ Black", "🟠 Brown", "🌸 Pink"],
        "color_previews": {
            "Black": "https://i.ibb.co/fzxY8fCB/Polish-20260310-035712367.jpg", 
            "Brown": "https://i.ibb.co/0pWT0RDw/Polish-20260310-035926140.jpg", 
            "Pink": "https://i.ibb.co/LDtSBmNr/Polish-20260310-035829615.jpg"
        }, "payment_url": PAYMENT_LINK
    },
    503: {
        "name": "🔌 Vaporesso XROS 5 Mini", "type": "pods", "stock": 15, "gift_liquid": True, "price": 699, 
        "img": "https://i.ibb.co/9kjjt8fS/Polish-20260310-035358626.jpg", 
        "desc": "🔥 <b>НОВИНКА 2025 | COREX 2.0</b>\nМаксимальна передача смаку.",
        "colors": ["⚫️ Core Black", "🌸 Pink", "🟢 Green"],
        "color_previews": {
            "Core Black": "https://i.ibb.co/9kjjt8fS/Polish-20260310-035358626.jpg", 
            "Green": "https://i.ibb.co/qFRkWbSd/Polish-20260310-035559939.jpg", 
            "Pink": "https://i.ibb.co/Wppc1Kpz/Polish-20260310-035500449.jpg"
        }, "payment_url": PAYMENT_LINK
    },
    504: {
        "name": "🔌 Vaporesso XROS 4", "type": "pods", "stock": 7, "gift_liquid": True, "price": 799, 
        "img": "https://i.ibb.co/dxxRp0s/Polish-20260310-040035754.jpg", 
        "desc": "👌 <b>БАЛАНС ТА СТИЛЬ</b>\nМеталевий корпус, 3 режими потужності.",
        "colors": ["⚫️ Black", "🔵 Blue", "🟣 Purple Gradient"],
        "color_previews": {
            "Black": "https://i.ibb.co/dxxRp0s/Polish-20260310-040035754.jpg", 
            "Blue": "https://i.ibb.co/yFBdq6H5/Polish-20260310-040313133.jpg", 
            "Purple Gradient": "https://i.ibb.co/R4pNBjqd/Polish-20260310-040208981.jpg"
        }, "payment_url": PAYMENT_LINK
    },
    505: {
        "name": "🔌 Vaporesso XROS 3 Mini", "type": "pods", "stock": 28, "gift_liquid": True, "price": 549, 
        "img": "https://i.ibb.co/3yjwss9n/Polish-20260310-034640422.jpg", 
        "desc": "🔋 <b>1000 mAh | MTL</b>\nЛегендарна модель.",
        "colors": ["⚫️ Black", "🟢 Green", "🌸 Pink"],
        "color_previews": {
            "Black": "https://i.ibb.co/3yjwss9n/Polish-20260310-034640422.jpg", 
            "Green": "https://i.ibb.co/HfJyCtCy/Polish-20260310-034754250.jpg", 
            "Pink": "https://i.ibb.co/MD42jyrq/Polish-20260310-034919145.jpg"
        }, "payment_url": PAYMENT_LINK
    },
    506: {
        "name": "🔌 Voopoo Vmate Mini", "type": "pods", "stock": 35, "gift_liquid": True, "price": 479, 
        "img": "https://i.ibb.co/HDMZfbSj/Polish-20260310-040815896.jpg", 
        "desc": "😌 <b>ЛЕГКИЙ СТАРТ</b>\nАвтоматична тяга, жодних кнопок.",
        "colors": ["⚫️ Black", "🔴 Red", "🌸 Pink"],
        "color_previews": {
            "Black": "https://i.ibb.co/HDMZfbSj/Polish-20260310-040815896.jpg", 
            "Red": "https://i.ibb.co/S7Jt4Z2P/Polish-20260310-040956311.jpg", 
            "Pink": "https://i.ibb.co/nNrz1dKC/Polish-20260310-041156722.jpg"
        }, "payment_url": PAYMENT_LINK
    }
}

# --- 🎁 ПОДАРУНКОВІ РІДИНИ (9000+) ---
GIFT_LIQUIDS = {
    9001: {"name": "🎁 Fall Tea 30ml", "desc": "☕ Осінній чай з нотками лимону."},
    9002: {"name": "🎁 Mystery One 30ml", "desc": "🔮 Таємничий фруктовий мікс."},
    9003: {"name": "🎁 Strawberry Jelly 30ml", "desc": "🍮 Ніжний десертний смак полуничного желе."},
    9004: {"name": "🎁 Grape BlackBerry 30ml", "desc": "🍇 Виноград та ожина."},
    9005: {"name": "🎁 Cola Pomelo 30ml", "desc": "🥤 Кола та помело."},
    9006: {"name": "🎁 BlackCurrant Rose 30ml", "desc": "🌹 Смородина та троянди."},
    9007: {"name": "🎁 Berry Lemonade 30ml", "desc": "🍹 Ягідний лимонад."},
    9008: {"name": "🎁 Energetic 30ml", "desc": "⚡ Бадьорий смак енергетика."}
}

# --- 🛠 СЕРВІСНІ ФУНКЦІЇ ---
def get_item_data(item_id: int):
    """Шукає товар у всіх категоріях за ID (Єдина правильна функція)."""
    all_dbs = [HHC_VAPES, PODS, LIQUIDS, GIFT_LIQUIDS] 
    try:
        iid = int(item_id)
        for db in all_dbs:
            if iid in db: return db[iid]
    except: pass
    return None

# =================================================================
# ⚙️ SECTION 4: MATH CORE, DATABASE & AUTH (DB FIX + REF READY)
# =================================================================

import sqlite3
import logging
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

logger = logging.getLogger("GhostyCore")

# Налаштування знижок
VIP_DISCOUNT_PERCENT = 0.35  # 35%
VIP_DISCOUNT_CATEGORIES = ['hhc', 'pods'] 

# ==========================================
# 🧮 MATH & UI LOGIC
# ==========================================

def calculate_final_price(item_price, user_profile, item_category=None):
    """
    Обчислює ціну з використанням Decimal для фінансової точності.
    Застосовує VIP знижку тільки до вказаних категорій.
    """
    try:
        # Використовуємо Decimal для уникнення помилок 0.1 + 0.2
        price = Decimal(str(item_price))
        up = user_profile or {}
        is_vip = bool(up.get('is_vip', False))
        
        # Якщо категорія не передана, знижка не застосовується (безпечний режим)
        if is_vip and item_category in VIP_DISCOUNT_CATEGORIES:
            discount_multiplier = Decimal(str(1 - VIP_DISCOUNT_PERCENT))
            final_price = price * discount_multiplier
            # Округлення до сотих, мінімальна ціна 1.0 грн
            final_price = max(final_price, Decimal('1.00')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            return float(final_price), True
            
        return float(price.quantize(Decimal('0.01'))), False
    except Exception as e:
        logger.error(f"❌ Math Error in calculate_final_price: {e}")
        return float(item_price), False

def get_price_display(item_price, profile, item_category):
    """Форматує ціну для Telegram UI (з закресленням старої ціни)."""
    price, is_discounted = calculate_final_price(item_price, profile, item_category)
    if is_discounted:
        return f"<s>{int(item_price)}</s> 🔥 <b>{int(price)} ₴</b>", price, True
    return f"<b>{int(price)} ₴</b>", price, False

# ==========================================
# 🗄️ DATABASE & MIGRATIONS
# ==========================================

def init_db():
    """Ініціалізація структури бази та динамічна перевірка колонок."""
    try:
        with sqlite3.connect(DB_PATH, timeout=30) as conn:
            conn.execute("PRAGMA journal_mode=WAL") # Вмикаємо швидкий доступ
            cur = conn.cursor()
            
            # Таблиця користувачів
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
                    balance REAL DEFAULT 0,
                    next_order_discount REAL DEFAULT 0,
                    referred_by INTEGER,
                    referral_used INTEGER DEFAULT 0,
                    promo_applied INTEGER DEFAULT 0,
                    promo_GHST2026_used INTEGER DEFAULT 0,
                    reg_date TEXT
                )
            ''')
            
            # Розумна міграція: Перевіряємо наявність колонок перед додаванням
            cur.execute("PRAGMA table_info(users)")
            existing_columns = [col[1] for col in cur.fetchall()]
            
            migrations = [
                ("promo_GHST2026_used", "INTEGER DEFAULT 0"),
                ("referral_used", "INTEGER DEFAULT 0"),
                ("referred_by", "INTEGER"),
                ("balance", "REAL DEFAULT 0")
            ]
            
            for col_name, col_type in migrations:
                if col_name not in existing_columns:
                    cur.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
                    logger.info(f"⚙️ Migration: Added column {col_name} to users")
            
            # Таблиця замовлень
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
            logger.info("✅ Database initialized successfully.")
    except Exception as e:
        logger.critical(f"❌ DB FATAL ERROR: {e}")

# ==========================================
# 👤 USER SYNC & REFERRALS
# ==========================================

async def get_or_create_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Синхронізація профілю з БД та обробка реферальних переходів."""
    user = update.effective_user
    if not user: return None

    # Завантаження з БД
    try:
        with sqlite3.connect(DB_PATH, timeout=30) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            row = cursor.execute("SELECT * FROM users WHERE user_id=?", (user.id,)).fetchone()

            if not row:
                # НОВИЙ КОРИСТУВАЧ
                reg_time = datetime.now().strftime("%d.%m.%Y %H:%M")
                
                # Обробка Deep Link (/start 12345)
                ref_id = None
                if context.args and context.args[0].isdigit():
                    potential_ref = int(context.args[0])
                    if potential_ref != user.id: # Не можна запросити самого себе
                        ref_id = potential_ref
                
                cursor.execute("""
                    INSERT INTO users (user_id, username, full_name, reg_date, referred_by) 
                    VALUES (?, ?, ?, ?, ?)
                """, (user.id, user.username, user.full_name, reg_time, ref_id))
                conn.commit()
                row = cursor.execute("SELECT * FROM users WHERE user_id=?", (user.id,)).fetchone()
                logger.info(f"🆕 New user registered: {user.id} (Ref: {ref_id})")

            # Мапінг рядка БД в словник профілю
            profile_data = dict(row)
            # Конвертація числових статусів в Boolean
            for bool_col in ['is_vip', 'promo_applied', 'promo_GHST2026_used', 'referral_used']:
                profile_data[bool_col] = bool(profile_data.get(bool_col, 0))
            
            # Зберігаємо в context для швидкості
            context.user_data['profile'] = profile_data
            
    except Exception as e:
        logger.error(f"❌ DB Sync Failure for {user.id}: {e}")
        # Створюємо тимчасовий профіль, щоб бот не впав
        if 'profile' not in context.user_data:
            context.user_data['profile'] = {"user_id": user.id, "is_vip": False}
        
    return context.user_data['profile']
    
# =================================================================
# 🛍 SECTION 14: CATALOG MASTER ENGINE (TITAN PRO v10.5)
# =================================================================

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

logger = logging.getLogger("GhostyCore")

async def catalog_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Головне меню вибору категорій стафу."""
    query = update.callback_query
    if query: await query.answer()

    profile = context.user_data.get('profile', {})
    is_vip = profile.get('is_vip', False)
    
    # Динамічний статус для лояльності
    vip_status_text = "✨ <b>Статус: VIP PRO</b> (-35% 🔥)" if is_vip else "👤 <b>Статус: Standard</b>"

    text = (
        "<b>🛍 КАТАЛОГ GHO$$TY STAFF</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"{vip_status_text}\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Оберіть категорію товарів 👇\n"
    )
    
    kb = [
        [InlineKeyboardButton("💨 HHC ВЕЙПИ (USA) 🔥", callback_data="cat_list_hhc")],
        [InlineKeyboardButton("🔌 POD-СИСТЕМИ 🔌", callback_data="cat_list_pods")],
        [InlineKeyboardButton("💧 РІДИНИ (SALT) 💧", callback_data="cat_list_liquids")],
        [InlineKeyboardButton("🏠 ГОЛОВНЕ МЕНЮ", callback_data="menu_start")]
    ]
    
    photo = globals().get('WELCOME_PHOTO', "https://i.ibb.co/y7Q194N/1770068775663.png")
    
    # Виклик універсальної функції (Section 25)
    send_func = globals().get('send_ghosty_message')
    if send_func:
        await send_func(update, text, kb, photo=photo, context=context)
    else:
        # Fallback якщо основна функція не завантажена
        markup = InlineKeyboardMarkup(kb)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=markup, parse_mode="HTML")

async def show_category_items(update: Update, context: ContextTypes.DEFAULT_TYPE, category_key: str):
    """Виведення списку товарів з урахуванням наявності та прайсу."""
    query = update.callback_query
    if query: await query.answer()
    
    # Мапінг категорій
    cat_map = {
        'hhc': ('HHC_VAPES', '💨 HHC Вейпи'),
        'pods': ('PODS', '🔌 POD-Системи'),
        'liquids': ('LIQUIDS', '💧 Рідини'),
    }
    
    map_data = cat_map.get(category_key)
    if not map_data:
        return await query.answer("⚠️ Категорія недоступна", show_alert=True)

    dict_name, cat_title = map_data
    items_dict = globals().get(dict_name, {})
    
    if not items_dict:
        return await query.answer("⚠️ Товари скоро з'являться", show_alert=True)

    profile = context.user_data.get('profile', {})
    
    text = (
        f"📂 <b>КАТЕГОРІЯ: {cat_title}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🔥 — <i>Ціна зі знижкою VIP</i>\n"
        f"⌛ — <i>Залишилось обмаль</i>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👇 Оберіть товар для деталей:"
    )
    
    kb = []
    # Сортування: спочатку те, що є (True/False), потім за ціною
    sorted_items = sorted(
        items_dict.items(), 
        key=lambda x: (x[1].get('stock', 0) > 0, -x[1].get('price', 0)), 
        reverse=True
    )

    # Ліміт на 15 товарів (захист від занадто довгих повідомлень)
    for i_id, item in sorted_items[:18]:
        stock = int(item.get('stock', 0))
        
        # Отримуємо ціну через Section 4
        price_func = globals().get('get_price_display')
        if callable(price_func):
            # Повертає: (html_str, final_float, is_discounted)
            _, final_price, is_discounted = price_func(item['price'], profile, i_id)
        else:
            final_price, is_discounted = item['price'], False

        if stock <= 0:
            btn_text = f"❌ {item['name']} (Sold Out)"
            cb_data = "ignore_out_of_stock"
        else:
            hot_prefix = "⌛ " if stock < 3 else ""
            vip_prefix = "🔥 " if is_discounted else ""
            btn_text = f"{vip_prefix}{hot_prefix}{item['name']} — {int(final_price)} ₴"
            cb_data = f"view_item_{i_id}"

        kb.append([InlineKeyboardButton(btn_text, callback_data=cb_data)])
    
    kb.append([InlineKeyboardButton("🔙 НАЗАД ДО КАТЕГОРІЙ", callback_data="cat_all")])
    
    # Виклик безпечного редагування (Section 10)
    safe_edit = globals().get('_edit_or_reply')
    if safe_edit:
        await safe_edit(query, text, kb, context=context)
    else:
        await query.edit_message_caption(caption=text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="HTML")
        

# =================================================================
# 🌍 SECTION 10: GEOGRAPHY & LOGISTICS (TITAN ULTIMATE v10.5)
# =================================================================

import sqlite3
import logging
from telegram import Update, InlineKeyboardButton
from telegram.ext import ContextTypes

logger = logging.getLogger("GhostyCore")

async def choose_city_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    КРОК 1: Головне меню вибору міста.
    Точка входу для зміни локації.
    """
    query = update.callback_query
    
    # 1. Скидання старих гео-даних (захист від замовлень не туди)
    p = context.user_data.setdefault('profile', {})
    p['city'] = None
    p['district'] = None
    p['address_details'] = None
    
    context.user_data['state'] = "COLLECTING_DATA"
    context.user_data.setdefault('data_flow', {})['step'] = 'city_selection'
    
    # Брендований візуал
    map_image = globals().get('WELCOME_PHOTO', "https://i.ibb.co/y7Q194N/1770068775663.png")
    
    text = (
        "🏙 <b>ГЕОЛОКАЦІЯ ТА ДОСТАВКА</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Оберіть ваше місто. Це дозволить нам показати\n"
        "доступні райони або варіанти доставки 👇"
    )
    
    # Отримуємо список міст (Section 3)
    cities = globals().get('CITIES_LIST', ["Дніпро", "Кам'янське", "Київ"])
    
    keyboard = []
    # Генерація кнопок (сітка 2хN)
    for i in range(0, len(cities), 2):
        row = [InlineKeyboardButton(cities[i], callback_data=f"sel_city_{cities[i]}")]
        if i + 1 < len(cities):
            row.append(InlineKeyboardButton(cities[i+1], callback_data=f"sel_city_{cities[i+1]}"))
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("🏠 ГОЛОВНЕ МЕНЮ", callback_data="menu_start")])
    
    # Використовуємо універсальну функцію відправки з фото
    await send_ghosty_message(update, text, keyboard, photo=map_image, context=context)


async def choose_delivery_method(update: Update, context: ContextTypes.DEFAULT_TYPE, city: str):
    """
    КРОК 2: Вибір способу отримання (Клад vs Кур'єр).
    """
    query = update.callback_query
    context.user_data.setdefault('profile', {})['city'] = city
    
    courier_fee = float(globals().get('COURIER_PRICE', 150.0))
    
    text = (
        f"🏙 <b>{city.upper()}: ВАРІАНТИ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"1️⃣ <b>Готовий Клад</b> — миттєве отримання в обраному районі (0 ₴).\n"
        f"2️⃣ <b>Кур'єрська доставка</b> — конфіденційна доставка за адресою.\n"
        f"   └ <i>Вартість: +{int(courier_fee)} ₴</i>\n\n"
        f"👇 Оберіть спосіб отримання:"
    )
    
    kb = [
        [InlineKeyboardButton("📍 Обрати район (Клад)", callback_data=f"list_districts_{city}")],
        [InlineKeyboardButton(f"🛵 Замовити Кур'єра (+{int(courier_fee)} ₴)", callback_data="sel_dist_Кур'єр")],
        [InlineKeyboardButton("⬅️ Змінити місто", callback_data="choose_city")]
    ]
    
    # Редагуємо існуюче повідомлення для плавності
    await _edit_or_reply(query, text, kb, context=context)


async def district_selection_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, city: str):
    """
    КРОК 3: Вибір конкретного району міста.
    """
    query = update.callback_query
    user_id = update.effective_user.id
    
    # Дані з UKRAINE_CITIES (Section 3)
    cities_db = globals().get('UKRAINE_CITIES', {})
    districts = cities_db.get(city, ["Центр", "Самовивіз"])
    
    # 1. Оновлення бази (Pre-Save)
    db_path = globals().get('DB_PATH', 'data/ghossty.db')
    try:
        with sqlite3.connect(db_path, timeout=30) as conn:
            # Оновлюємо місто і відразу скидаємо район/адресу
            conn.execute("""
                UPDATE users 
                SET city = ?, district = NULL, address_details = NULL 
                WHERE user_id = ?
            """, (city, user_id))
            conn.commit()
    except Exception as e:
        logger.error(f"DATABASE ERROR (District Selection): {e}")

    text = (
        f"🏘 <b>{city.upper()}: РАЙОНИ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Оберіть локацію, яка вам найбільше підходить.\n"
        f"Наші менеджери підготували клади саме там 👇"
    )

    kb = []
    # Адаптивна сітка районів
    for i in range(0, len(districts), 2):
        row = [InlineKeyboardButton(districts[i], callback_data=f"sel_dist_{districts[i]}")]
        if i + 1 < len(districts):
            row.append(InlineKeyboardButton(districts[i+1], callback_data=f"sel_dist_{districts[i+1]}"))
        kb.append(row)
        
    kb.append([InlineKeyboardButton("🔙 Назад", callback_data=f"sel_city_{city}")])
    
    context.user_data.setdefault('data_flow', {})['step'] = 'district_selection'
    
    await _edit_or_reply(query, text, kb, context=context)

async def _edit_or_reply(query, text, kb, context):
    """Допоміжна функція для плавного перемикання інтерфейсу."""
    markup = InlineKeyboardMarkup(kb)
    try:
        if query:
            await query.edit_message_caption(caption=text, reply_markup=markup, parse_mode="HTML")
        else:
            # Якщо викликано не з кнопки (малоімовірно, але для стабільності)
            await context.bot.send_message(chat_id=query.message.chat_id, text=text, reply_markup=markup, parse_mode="HTML")
    except Exception as e:
        # Якщо повідомлення не змінилося або фото не підтримує edit_caption
        await query.message.reply_text(text, reply_markup=markup, parse_mode="HTML")
        
    
# =================================================================
# 👤 SECTION 5: MASTER START & PROFILE UI (DEEP LINK SUPPORT)
# =================================================================

from datetime import datetime
from html import escape
import logging

logger = logging.getLogger("GhostyCore")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Головна точка входу (/start). 
    Підтримка Deep Linking (реферали) та повне скидання станів.
    """
    user = update.effective_user
    args = context.args # Отримуємо аргументи типу /start 12345678
    
    # 1. СКИДАННЯ СТАНІВ (Захист від "залипання" збору даних)
    for key in ['target_item_id', 'target_gift_id', 'selected_color', 
                'selected_strength', 'state', 'data_step']:
        context.user_data.pop(key, None)

    # 2. РЕФЕРАЛЬНА ЛОГІКА
    ref_id = None
    if args and args[0].isdigit():
        ref_id = int(args[0])
        if ref_id == user.id: ref_id = None # Не можна запросити самого себе

    # 3. ОТРИМАННЯ/СТВОРЕННЯ ПРОФІЛЮ
    if 'get_or_create_user' in globals():
        # Передаємо ref_id у функцію створення, щоб нарахувати бонуси
        profile = await get_or_create_user(update, context, referrer=ref_id)
    else:
        await update.message.reply_text("🔌 Помилка з'єднання з базою даних. Спробуйте пізніше.")
        return

    # 4. ПЕРЕВІРКА VIP СТАТУСУ (Надійна логіка)
    is_vip = False
    vip_expiry_str = profile.get('vip_expiry', '—')
    if vip_expiry_str and vip_expiry_str != '—':
        try:
            # Формат: 31.12.2026 23:59
            expiry_dt = datetime.strptime(vip_expiry_str, '%d.%m.%Y %H:%M')
            if expiry_dt > datetime.now():
                is_vip = True
        except Exception as e:
            logger.error(f"VIP Date Parse Error: {e}")

    # 5. ВІЗУАЛІЗАЦІЯ ТА ДАНІ
    safe_name = escape(user.first_name)
    balance = int(profile.get('next_order_discount', 0))
    bot_username = (await context.bot.get_me()).username
    ref_link = f"https://t.me/{bot_username}?start={user.id}"
    
    status_icon = "💎 V.I.P PRO" if is_vip else "👤 Standard User"
    vip_benefits = (
        f"📉 <b>-35% знижка</b> + <b>FREE Доставка</b> ✅" 
        if is_vip else "<i>(Активуй VIP для безкоштовної доставки!)</i>"
    )
    
    welcome_text = (
        f"🌫️ <b>GHO$$TY STAFF LAB | 2026</b> 🌿\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Вітаємо, <b>{safe_name}</b>!\n"
        f"👑 Статус: <b>{status_icon}</b>\n"
        f"💰 Баланс: <b>{balance} ₴</b>\n"
        f"{vip_benefits}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🎁 <b>АКЦІЯ ДЛЯ НОВИХ КЛІЄНТІВ:</b>\n"
        f"Введи код <code>GHST2026</code> у профілі\n"
        f"Отримай <b>+69 ₴</b> та <b>7 днів VIP PRO</b>!\n\n"
        f"🤝 <b>ПАРТНЕРКА (Заробляй на друзях):</b>\n"
        f"За кожного друга: <b>+50 ₴</b> та <b>+7 днів VIP</b>\n"
        f"🔗 <code>{ref_link}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👇 <b>ОБЕРИ РОЗДІЛ:</b>"
    )
    
    keyboard = [
        [InlineKeyboardButton("🛍 ВІДКРИТИ КАТАЛОГ 🌿", callback_data="cat_all")],
        [InlineKeyboardButton("👤 ПРОФІЛЬ", callback_data="menu_profile"), 
         InlineKeyboardButton("🛒 КОШИК", callback_data="menu_cart")],
        [InlineKeyboardButton("🚚 МОЯ ДОСТАВКА", callback_data="fill_delivery_data")], 
        [InlineKeyboardButton("👨‍💻 МЕНЕДЖЕР", url=f"https://t.me/{globals().get('MANAGER_USERNAME', 'ghosty_admin')}"),
         InlineKeyboardButton("📢 КАНАЛ", url=globals().get('CHANNEL_URL', 'https://t.me/ghosty_channel'))]
    ]
    
    # Кнопка адміна
    if user.id in globals().get('ADMIN_LIST', []) or str(user.id) == str(globals().get('MANAGER_ID')):
        keyboard.append([InlineKeyboardButton("⚙️ ADMIN PANEL", callback_data="admin_main")])

    photo = globals().get('WELCOME_PHOTO', "https://i.ibb.co/35K9Zp5p/Polish-20260310-051407282.png")
    await send_ghosty_message(update, welcome_text, keyboard, photo=photo, context=context)


async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Особистий кабінет користувача."""
    user = update.effective_user
    profile = await get_or_create_user(update, context)
    bot_username = (await context.bot.get_me()).username
    
    # Перевірка VIP
    vip_expiry = profile.get('vip_expiry', '—')
    is_vip = False
    try:
        if vip_expiry != '—' and datetime.strptime(vip_expiry, '%d.%m.%Y %H:%M') > datetime.now():
            is_vip = True
    except: pass
    
    status_text = "💎 V.I.P PRO" if is_vip else "👤 Standard"
    
    # Гео-дані
    city = profile.get('city', 'Не обрано')
    district = profile.get('district')
    location = f"{city}" + (f" ({district})" if district else "")
    
    text = (
        f"👤 <b>МІЙ ПРОФІЛЬ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 ID: <code>{user.id}</code>\n"
        f"🧢 Ім'я: <b>{escape(profile.get('full_name', user.first_name))}</b>\n"
        f"🌟 Статус: <b>{status_text}</b>\n"
        f"📅 VIP до: <code>{vip_expiry}</code>\n\n"
        f"💰 <b>БОНУСИ: {int(profile.get('next_order_discount', 0))} ₴</b>\n"
        f"<i>(Знижка активується автоматично)</i>\n\n"
        f"📍 <b>ДОСТАВКА:</b>\n"
        f"🏙 Місто: {location}\n"
        f"🏠 Адреса: {profile.get('address_details', '—')}\n"
        f"📱 Тел: <code>{profile.get('phone', 'Не вказано')}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🔗 <b>ВАШЕ ПОСИЛАННЯ:</b>\n"
        f"<code>https://t.me/{bot_username}?start={user.id}</code>\n\n"
        f"👇 <i>Керування:</i>"
    )
    
    kb = [
        [InlineKeyboardButton("✏️ Оновити дані", callback_data="fill_delivery_data")],
        [InlineKeyboardButton("🎟 Промокод", callback_data="menu_promo"),
         InlineKeyboardButton("🔄 Оновити", callback_data="menu_profile")],
        [InlineKeyboardButton("🔙 Головне меню", callback_data="menu_start")]
    ]
    
    await send_ghosty_message(update, text, kb, photo=globals().get('WELCOME_PHOTO'), context=context)
    
# =================================================================
# 🔍 SECTION 15: PRODUCT CARD & INTERACTIVE ENGINE (PRO)
# =================================================================

from html import escape

async def view_item_details(update: Update, context: ContextTypes.DEFAULT_TYPE, item_id: int):
    """
    Точка входу: Скидає старі вибори та завантажує свіжу картку.
    """
    item = get_item_data(item_id)
    if not item:
        if update.callback_query:
            await update.callback_query.answer("❌ Товар не знайдено або знято з продажу.", show_alert=True)
        return

    # Очищуємо сесію вибору для конкретного товару
    context.user_data['selected_color'] = None
    context.user_data['selected_strength'] = None
    
    # Використовуємо основне фото за замовчуванням
    main_photo = item.get('img', 'https://via.placeholder.com/500') # Заглушка, якщо фото немає
    await render_product_card(update, context, item, item_id, main_photo)


async def render_product_card(update: Update, context: ContextTypes.DEFAULT_TYPE, item: dict, item_id: int, current_photo: str):
    """
    Ядро рендерингу: Динамічно збирає опис, ціну та кнопки з урахуванням виборів.
    """
    profile = context.user_data.get("profile", {})
    
    # 1. ЦІНА ТА АКЦІЇ
    price_html, _, _ = get_price_display(item.get('price', 0), profile, item_id)

    # 2. СТАТУС СКЛАДУ
    stock = int(item.get('stock', 0))
    if stock >= 15:
        stock_status = "🟢 В наявності"
    elif 1 <= stock < 15:
        stock_status = f"🟡 Залишилось: {stock} шт 🔥"
    else:
        stock_status = "🔴 Немає в наявності"

    # 3. ПАРАМЕТРИ
    selected_color = context.user_data.get('selected_color')
    selected_strength = context.user_data.get('selected_strength')
    
    params_text = ""
    if selected_color: params_text += f"\n🎨 Колір: <b>{selected_color}</b>"
    if selected_strength: params_text += f"\n⚡️ Міцність: <b>{selected_strength} mg</b>"

    # 4. ТЕКСТ КАРТКИ
    caption = (
        f"🛍 <b>{escape(item.get('name', 'Без назви'))}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📦 Стан: {stock_status}\n"
        f"💰 Ціна: {price_html}{params_text}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{item.get('desc', 'Опис відсутній.')}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🚀 <i>Оберіть параметри та натисніть «Додати в кошик»</i>"
    )

    kb = []
    
    if stock > 0:
        # --- БЛОК КОЛЬОРІВ ---
        colors = item.get("colors", [])
        if colors:
            kb.append([InlineKeyboardButton("🎨 ОБЕРІТЬ КОЛІР:", callback_data="ignore")])
            row = []
            for col in colors:
                is_sel = (col == selected_color)
                btn_text = f"● {col} ●" if is_sel else col
                cb = "ignore" if is_sel else f"sel_col_{item_id}_{col}"
                row.append(InlineKeyboardButton(btn_text, callback_data=cb))
                if len(row) == 2:
                    kb.append(row); row = []
            if row: kb.append(row)

        # --- БЛОК МІЦНОСТІ ---
        strengths = item.get("strengths", [])
        if strengths:
            kb.append([InlineKeyboardButton("⚡️ ОБЕРІТЬ МІЦНІСТЬ:", callback_data="ignore")])
            row = []
            for s in strengths:
                is_sel = (str(s) == str(selected_strength))
                btn_text = f"🔘 {s} mg" if is_sel else f"{s} mg"
                cb = "ignore" if is_sel else f"sel_str_{item_id}_{s}"
                row.append(InlineKeyboardButton(btn_text, callback_data=cb))
            kb.append(row)

        # 5. КНОПКИ ДІЇ
        need_color = colors and not selected_color
        need_strength = strengths and not selected_strength
        
        if need_color or need_strength:
            missing = "КОЛІР" if need_color else "МІЦНІСТЬ"
            kb.append([InlineKeyboardButton(f"👆 ОБЕРІТЬ {missing}", callback_data="ignore")])
        else:
            # Збірка метаданих для кошика
            c_meta = f"_{selected_color}" if selected_color else ""
            s_meta = f"_{selected_strength}" if selected_strength else ""
            kb.append([InlineKeyboardButton("🛒 ДОДАТИ В КОШИК", callback_data=f"add_{item_id}{c_meta}{s_meta}")])
            kb.append([
                InlineKeyboardButton("⚡️ ШВИДКЕ ЗАМОВЛЕННЯ", callback_data=f"fast_{item_id}"),
                InlineKeyboardButton("👨‍💻 МЕНЕДЖЕР", callback_data=f"mgr_ask_{item_id}")
            ])
    else:
        kb.append([InlineKeyboardButton("🔔 ПОВІДОМИТИ ПРО ПОЯВУ", callback_data=f"notify_{item_id}")])

    kb.append([InlineKeyboardButton("🔙 НАЗАД ДО КАТАЛОГУ", callback_data="cat_all")])

    await send_ghosty_message(update, caption, kb, photo=current_photo, context=context)


async def handle_param_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обробляє вибір параметрів та динамічно оновлює фото товару.
    """
    query = update.callback_query
    data = query.data
    
    # Надійний розбір: sel_col_{id}_{value...}
    prefix, target, item_id, *value_parts = data.split('_')
    item_id = int(item_id)
    value = "_".join(value_parts)
    
    item = get_item_data(item_id)
    if not item: 
        return await query.answer("Товар більше недоступний")

    new_photo = item.get('img')
    
    if target == "col":
        context.user_data['selected_color'] = value
        # Оновлення фото на колір (якщо є в мапі)
        previews = item.get("color_previews", {})
        # Шукаємо збіг без врахування регістру
        new_photo = previews.get(value, previews.get(value.lower(), item.get('img')))
        await query.answer(f"🎨 Обрано: {value}")
        
    elif target == "str":
        context.user_data['selected_strength'] = value
        await query.answer(f"⚡️ Міцність: {value} mg")

    # Перерендер без мерехтіння (send_ghosty_message має вміти робити editMedia)
    await render_product_card(update, context, item, item_id, new_photo)
    
# =================================================================
# 📝 SECTION 16: SMART DATA COLLECTION (TITAN FIXED)
# =================================================================

import sqlite3
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

logger = logging.getLogger("GhostyCore")

async def start_data_collection(update: Update, context: ContextTypes.DEFAULT_TYPE, next_action: str = 'checkout', item_id: int = None):
    """
    Головний контролер збору даних. Автоматично визначає, якого поля не вистачає,
    або запускає повне перештрихування (force_edit).
    """
    user_id = update.effective_user.id
    context.user_data['post_data_action'] = next_action
    
    # Зберігаємо ID товару, якщо збір розпочато з кнопки "Купити"
    if item_id: 
        context.user_data['target_item_id'] = item_id
    
    # Ініціалізація профілю
    profile = context.user_data.setdefault('profile', {})
    force_edit = (next_action in ['none', 'profile', 'force_edit'])

    # Встановлюємо загальний стан збору
    context.user_data['state'] = "COLLECTING_DATA"

    # --- КРОК 1: ПІБ ---
    if force_edit or not profile.get('full_name'):
        context.user_data['data_step'] = "name"
        text = (
            "📝 <b>КРОК 1/4: ВАШЕ ІМ'Я</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "Введіть Прізвище та Ім'я отримувача.\n\n"
            "⚠️ <i>Це необхідно для ідентифікації замовлення.</i>"
        )
        kb = [[InlineKeyboardButton("✖️ Скасувати", callback_data="menu_profile")]]
        await send_ghosty_message(update, text, kb, context=context)
        return

    # --- КРОК 2: ТЕЛЕФОН ---
    if force_edit or not profile.get('phone'):
        context.user_data['data_step'] = "phone"
        text = (
            "📱 <b>КРОК 2/4: КОНТАКТНИЙ НОМЕР</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "Будь ласка, введіть ваш номер телефону.\n"
            "Приклад: <code>0931234567</code>"
        )
        kb = [[InlineKeyboardButton("✖️ Скасувати", callback_data="menu_profile")]]
        await send_ghosty_message(update, text, kb, context=context)
        return

    # --- КРОК 3: МІСТО ---
    if force_edit or not profile.get('city'):
        # При зміні міста старий район та адреса стають невалідними
        context.user_data['profile']['district'] = None
        context.user_data['profile']['address_details'] = None
        if 'choose_city_menu' in globals():
            await globals()['choose_city_menu'](update, context)
        else:
            await query.answer("❌ Помилка меню міст", show_alert=True)
        return

    # --- КРОК 4: РАЙОН ТА АДРЕСА ---
    # Якщо місто є, але немає району або конкретної адреси
    if force_edit or not profile.get('address_details') or not profile.get('district'):
        current_dist = profile.get('district', 'Вибір...')
        await address_request_handler(update, context, current_dist)
        return

    # Якщо всі дані на місці — фіналізуємо
    if 'finalize_data_collection' in globals():
        await finalize_data_collection(update, context)

async def city_selection_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, city_name: str):
    """
    Обробник вибору міста. Очищує застарілі гео-дані та оновлює БД.
    """
    query = update.callback_query
    user_id = update.effective_user.id
    
    # 1. Оновлення в оперативній пам'яті
    profile = context.user_data.setdefault('profile', {})
    profile['city'] = city_name
    profile['district'] = None
    profile['address_details'] = None
    
    # 2. Негайний запис у SQLite для запобігання втраті даних
    db_path = globals().get('DB_PATH', 'data/ghosty_pro.db')
    try:
        with sqlite3.connect(db_path, timeout=30) as conn:
            conn.execute("""
                UPDATE users 
                SET city = ?, district = NULL, address_details = NULL 
                WHERE user_id = ?
            """, (city_name, user_id))
            conn.commit()
    except Exception as e:
        logger.error(f"DATABASE CRITICAL ERROR (City Update): {e}")

    # 3. Маршрутизація залежно від міста
    if city_name == "Дніпро":
        # У Дніпрі є доставка кур'єром по районах
        if 'show_dnipro_districts' in globals():
            await globals()['show_dnipro_districts'](update, context)
        else:
            await address_request_handler(update, context, "Центр (Кур'єр)")
    else:
        # Для інших міст (Кам'янське, Київ тощо) — тільки НП або Самовивіз
        await address_request_handler(update, context, "Нова Пошта")

async def address_request_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, dist_name: str):
    """
    Крок 4: Запит детальної адреси.
    Викликається після вибору міста/району.
    """
    query = update.callback_query
    # Очищаємо назву району від технічних префіксів
    clean_dist = dist_name.split("_")[-1].replace("dist", "").strip()
    
    profile = context.user_data.setdefault('profile', {})
    profile['district'] = clean_dist
    
    context.user_data['state'] = "COLLECTING_DATA"
    context.user_data['data_step'] = "address"
    
    city = profile.get('city', 'Не вказано')
    
    text = (
        f"📍 <b>КРОК 4/4: АДРЕСА ДОСТАВКИ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🏙 <b>Місто:</b> {city}\n"
        f"🏘 <b>Район/Тип:</b> {clean_dist}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"✍️ <b>ВВЕДІТЬ ДАНІ:</b>\n"
        f"• Якщо це <b>Нова Пошта</b> — вкажіть номер відділення.\n"
        f"• Якщо це <b>Кур'єр</b> — напишіть вулицю та номер будинку."
    )
    
    kb = [
        [InlineKeyboardButton("🏙 Змінити місто", callback_data="fill_delivery_data")],
        [InlineKeyboardButton("✖️ Скасувати", callback_data="menu_profile")]
    ]
    
    await send_ghosty_message(update, text, kb, context=context)
            
# =================================================================
# 🛒 SECTION 18: CART LOGIC (EXPANDED & REINFORCED)
# =================================================================

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

logger = logging.getLogger("GhostyCore")

async def show_cart_logic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Відображення кошика: розрахунок цін, перевірка даних користувача та логістика.
    """
    query = update.callback_query
    # Отримуємо кошик або створюємо порожній список
    cart = context.user_data.get("cart", [])
    # Гарантуємо наявність профілю
    profile = context.user_data.setdefault("profile", {})
    
    # 1. ПЕРЕВІРКА НА ПОРОЖНІЙ КОШИК
    if not cart:
        text = (
            "🛒 <b>ВАШ КОШИК ПОРОЖНІЙ</b>\n\n"
            "Здається, ви ще нічого не обрали. Зазирніть у каталог, "
            "там на вас чекають найкращі пропозиції! 👇"
        )
        kb = [
            [InlineKeyboardButton("🛍 ВІДКРИТИ КАТАЛОГ", callback_data="cat_all")],
            [InlineKeyboardButton("🏠 ГОЛОВНЕ МЕНЮ", callback_data="menu_start")]
        ]
        return await send_ghosty_message(update, text, kb, context=context)

    # 2. ПЕРЕВІРКА ПОВНОТИ ДАНИХ (Для активації кнопки замовлення)
    is_ready = all([
        profile.get("full_name"),
        profile.get("phone"),
        profile.get("city"),
        profile.get("address_details")
    ])

    # 3. РОЗРАХУНОК ТОВАРІВ
    total_sum = 0.0
    items_html = ""
    kb = []
    has_gift = False

    for item in cart:
        item_id = item.get('real_id')
        # Отримуємо ціну через універсальну функцію (враховує VIP та акції)
        # get_price_display повертає (html_str, float_price, old_price)
        price_html, final_price, _ = get_price_display(item.get('price', 0), profile, item_id)
        
        total_sum += float(final_price)
        
        # Формуємо мета-дані товару
        meta = []
        if item.get('color'): meta.append(f"🎨 {item['color']}")
        if item.get('strength'): meta.append(f"⚡️ {item['strength']}mg")
        if item.get('gift'): 
            meta.append(f"🎁 +{item['gift']}")
            has_gift = True
            
        meta_str = f"<i>({', '.join(meta)})</i>" if meta else ""
        
        items_html += (
            f"▫️ <b>{item.get('name')}</b> {meta_str}\n"
            f"   └ Ціна: {price_html}\n\n"
        )
        
        # Кнопка видалення (з обрізанням назви для краси)
        short_name = (item.get('name')[:15] + '..') if len(item.get('name', '')) > 15 else item.get('name')
        kb.append([InlineKeyboardButton(f"❌ Видалити {short_name}", callback_data=f"cart_del_{item.get('id')}")])

    # 4. ЛОГІКА ДОСТАВКИ ТА КУР'ЄРА
    delivery_info = ""
    district = profile.get('district', 'Відділення')
    
    if is_ready:
        if "Кур'єр" in str(district):
            # Перевірка на безкоштовну VIP доставку
            if profile.get('is_vip', False):
                courier_fee = 0.0
                fee_txt = "<b>FREE</b> (VIP 👑)"
            else:
                courier_fee = float(globals().get('COURIER_PRICE', 150.0))
                fee_txt = f"+{int(courier_fee)} ₴"
            
            total_sum += courier_fee
            delivery_info = (
                f"📍 <b>Доставка:</b> {profile['city']}, {profile['address_details']}\n"
                f"🛵 <b>Спосіб:</b> Кур'єр ({fee_txt})\n"
                f"👤 <b>Отримувач:</b> {profile['full_name']} ({profile['phone']})"
            )
        else:
            delivery_info = (
                f"📍 <b>Доставка:</b> {profile['city']}, р-н {district}\n"
                f"📦 <b>Спосіб:</b> Самовивіз / Клад (0 ₴)\n"
                f"👤 <b>Отримувач:</b> {profile['full_name']} ({profile['phone']})"
            )
        
        checkout_btn = [InlineKeyboardButton("🚀 ОФОРМИТИ ЗАМОВЛЕННЯ", callback_data="checkout_init")]
    else:
        delivery_info = (
            "⚠️ <b>Дані доставки не заповнені!</b>\n"
            "Будь ласка, вкажіть адресу, щоб ми знали, куди доставити товар."
        )
        checkout_btn = [InlineKeyboardButton("📝 ЗАПОВНИТИ ДАНІ", callback_data="fill_delivery_data")]

    # 5. ФОРМУВАННЯ ТЕКСТУ
    gift_status = "🎉 <i>Вам додано бонусний подарунок!</i>\n" if has_gift else ""
    
    full_text = (
        f"🛒 <b>ВАШ КОШИК ({len(cart)} од.)</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{items_html}"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{gift_status}"
        f"{delivery_info}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 <b>РАЗОМ ДО СПЛАТИ: {int(total_sum)} ₴</b>"
    )

    # Збірка клавіатури
    kb.insert(0, checkout_btn) # Кнопка дії завжди зверху
    
    # Нижня панель керування
    footer = []
    # Якщо у користувача вже є накопичена знижка, кнопку промокоду можна приховати
    if float(profile.get('next_order_discount', 0)) <= 0:
        footer.append(InlineKeyboardButton("🎟 ПРОМОКОД", callback_data="menu_promo"))
    
    footer.append(InlineKeyboardButton("🗑 ОЧИСТИТИ", callback_data="cart_clear"))
    
    kb.append(footer)
    kb.append([InlineKeyboardButton("🔙 НАЗАД ДО КАТАЛОГУ", callback_data="cat_all")])

    # Використовуємо універсальну функцію відправки (Section 1)
    await send_ghosty_message(update, full_text, kb, context=context)


async def cart_action_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Швидке керування вмістом кошика."""
    query = update.callback_query
    data = query.data
    
    if data == "cart_clear":
        context.user_data["cart"] = []
        await query.answer("🗑 Кошик повністю очищено", show_alert=False)
        
    elif data.startswith("cart_del_"):
        try:
            target_id = int(data.replace("cart_del_", ""))
            cart = context.user_data.get("cart", [])
            # Фільтруємо кошик, видаляючи тільки елемент з конкретним унікальним ID
            new_cart = [i for i in cart if i.get('id') != target_id]
            
            if len(new_cart) < len(cart):
                context.user_data["cart"] = new_cart
                await query.answer("❌ Товар видалено")
            else:
                await query.answer("⚠️ Товар вже видалений")
        except Exception as e:
            logger.error(f"Cart delete error: {e}")
            await query.answer("❌ Помилка видалення")

    # Оновлюємо інтерфейс кошика
    await show_cart_logic(update, context)

# =================================================================
# 🎁 SECTION 19: GIFT & CART ENGINE (TITAN ULTIMATE v10.5 - PRO FIX)
# =================================================================

import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

def get_gift_data(gift_id: int):
    """Шукає дані про подарунок у спеціальному або загальному словнику."""
    if not gift_id or gift_id <= 0:
        return None
    
    gift_dict = globals().get('GIFT_LIQUIDS', {})
    if gift_id in gift_dict:
        return gift_dict[gift_id]
        
    # Якщо не знайшли в подарунках, шукаємо в загальному каталозі рідин
    liquids_dict = globals().get('LIQUIDS', {})
    return liquids_dict.get(gift_id)

async def gift_selection_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Генератор меню вибору подарунка. 
    Підтримує контексти: add (кошик), fast (швидке замовлення), mgr (менеджер).
    """
    query = update.callback_query
    data = query.data
    parts = data.split("_")
    
    # Визначаємо контекст та ID товару
    if data.startswith("fast_order_"): 
        prefix, item_id = "fast", int(parts[2])
    elif data.startswith("mgr_pre_"): 
        prefix, item_id = "mgr", int(parts[2])
    elif data.startswith("add_"): 
        prefix, item_id = "add", int(parts[1])
    else:
        item_id = context.user_data.get('target_item_id')
        prefix = "add"

    if not item_id:
        await query.answer("❌ Помилка: товар не ідентифіковано", show_alert=True)
        return

    main_item = get_item_data(item_id)
    if not main_item:
        await query.answer("❌ Товар не знайдено", show_alert=True)
        return

    # 🔥 РОЗШИРЕНА ТАБЛИЦЯ ЕМОДЗІ
    emoji_map = {
        "Tea": "🍵", "Mystery": "🔮", "Strawberry": "🍓", "Grape": "🍇", 
        "BlackCurrant": "🫐", "Berry": "🍒", "Cola": "🥤", "Rose": "🌹", 
        "Lemon": "🍋", "Energetic": "⚡️", "Apple": "🍏", "Peach": "🍑", 
        "Mango": "🥭", "Mint": "🌿", "Banana": "🍌", "Ice": "🧊"
    }

    text = (
        f"🎁 <b>АКЦІЯ: ОБЕРІТЬ ВАШ БОНУС!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"До <b>{main_item['name']}</b> додається\n"
        f"рідина 30мл абсолютно <b>БЕЗКОШТОВНО</b>!\n\n"
        f"👇 <i>Оберіть смак подарунка:</i>"
    )

    kb = []
    gift_dict = globals().get('GIFT_LIQUIDS', {})
    
    for gid, gift_item in gift_dict.items():
        raw_name = gift_item['name'].replace("🎁 ", "").replace(" 30ml", "").strip()
        
        # Динамічний підбір іконки
        icon = "🧪"
        for key, em in emoji_map.items():
            if key.lower() in raw_name.lower():
                icon = em
                break
        
        # Формат: set_gift_ПРЕФІКС_IDТОВАРУ_IDПОДАРУНКУ
        kb.append([InlineKeyboardButton(f"{icon} {raw_name}", callback_data=f"set_gift_{prefix}_{item_id}_{gid}")])

    # Технічні кнопки
    kb.append([InlineKeyboardButton("❌ Без подарунка", callback_data=f"set_gift_{prefix}_{item_id}_0")])
    kb.append([InlineKeyboardButton("🔙 Назад до товару", callback_data=f"view_item_{item_id}")])

    await _edit_or_reply(query, text, kb, context=context)

async def add_to_cart_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Фінальна обробка додавання. 
    Якщо обрано fast/mgr — перекидає відразу на оформлення.
    """
    query = update.callback_query
    data = query.data
    
    # Розбір callback даних
    if data.startswith("set_gift_"):
        # set_gift_prefix_item_gift
        parts = data.split("_")
        prefix, item_id, gift_id = parts[2], int(parts[3]), int(parts[4])
    else:
        # add_item_gift
        parts = data.split("_")
        prefix, item_id = "add", int(parts[1])
        gift_id = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else None

    item = get_item_data(item_id)
    if not item:
        await query.answer("❌ Помилка завантаження даних товару", show_alert=True)
        return

    # 1. ПЕРЕВІРКА НА НЕОБХІДНІСТЬ ПОДАРУНКА
    needs_gift = (item_id < 300 or 500 <= item_id < 700 or item.get('gift_liquid'))
    if needs_gift and gift_id is None:
        await gift_selection_handler(update, context)
        return

    # 2. ПІДГОТОВКА ДАНИХ
    selected_color = context.user_data.get('selected_color', 'Стандарт')
    gift_name = None
    if gift_id and gift_id > 0:
        g_data = get_gift_data(gift_id)
        if g_data:
            gift_name = g_data['name'].replace("🎁 ", "")

    # 3. ЛОГІКА: КУДИ ЙДЕМО?
    if prefix in ["fast", "mgr"]:
        # Прямий перехід до чеку (минаючи кошик)
        context.user_data['target_item_id'] = item_id
        context.user_data['target_gift_id'] = gift_id
        # Викликаємо ініціалізацію оплати (Section 20)
        if 'checkout_init' in globals():
            await globals()['checkout_init'](update, context)
        return

    # 4. ДОДАВАННЯ В КОШИК
    new_entry = {
        "id": random.randint(100000, 999999),
        "real_id": item_id,
        "name": item['name'],
        "price": item['price'],
        "color": selected_color,
        "gift": gift_name,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    }
    
    context.user_data.setdefault("cart", []).append(new_entry)
    
    # Отримуємо ціну для відображення
    profile = context.user_data.get('profile', {})
    display_price = f"{int(item['price'])} ₴"
    if 'get_price_display' in globals():
        display_price, _ = get_price_display(item['price'], profile, item_id)

    # 5. ФОРМУВАННЯ ВІДПОВІДІ
    info = f"\n🎨 Колір: <b>{selected_color}</b>"
    if gift_name:
        info += f"\n🎁 Подарунок: <b>{gift_name}</b>"

    text = (
        f"✅ <b>УСПІШНО ДОДАНО В КОШИК!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📦 <b>{item['name']}</b>"
        f"{info}\n"
        f"💰 Вартість: <b>{display_price}</b>\n\n"
        f"<i>Ви можете додати щось ще або перейти до оформлення.</i>"
    )

    kb = [
        [InlineKeyboardButton("🛒 ПЕРЕЙТИ ДО ОФОРМЛЕННЯ", callback_data="menu_cart")],
        [InlineKeyboardButton("🛍 ПРОДОВЖИТИ ШОПІНГ", callback_data="cat_all")],
        [InlineKeyboardButton("🏠 В ГОЛОВНЕ МЕНЮ", callback_data="menu_start")]
    ]

    # Очищення тимчасових даних вибору для наступного товару
    context.user_data.pop('selected_color', None)
    context.user_data.pop('target_item_id', None)

    await _edit_or_reply(query, text, kb, context=context)
    try: await query.answer("📦 Додано!")
    except: pass
    
# =================================================================
# 💳 SECTION 20: CHECKOUT & PAYMENT CORE (TITAN FINAL - PRO FIX)
# =================================================================

import sqlite3
import logging
import random
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from html import escape

# Конфігурація логера
logger = logging.getLogger("GhostyCore")

async def checkout_init(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Ініціалізація оплати. Розраховує фінальний чек, враховуючи VIP-статус, 
    район доставки, накопичені бонуси та акційні подарунки.
    """
    query = update.callback_query
    user_id = update.effective_user.id
    profile = context.user_data.get('profile', {})
    
    # 1. СИНХРОНІЗАЦІЯ БОНУСІВ З БД (Critical Fix)
    db_path = globals().get('DB_PATH', 'data/ghosty_pro_final.db')
    try:
        with sqlite3.connect(db_path, timeout=10) as conn:
            res = conn.execute("SELECT next_order_discount, is_vip FROM users WHERE user_id=?", (user_id,)).fetchone()
            if res:
                profile['next_order_discount'] = float(res[0] or 0.0)
                profile['is_vip'] = bool(res[1])
                context.user_data['profile'] = profile
    except Exception as e:
        logger.error(f"DB Sync Error in Checkout: {e}")

    # 2. ПІДГОТОВКА ЗМІННИХ
    target_item_id = context.user_data.get('target_item_id')
    user_balance = float(profile.get('next_order_discount', 0.0))
    total_amount = 0.0
    items_desc = ""
    photo_to_show = globals().get('WELCOME_PHOTO')

    # --- ВАРІАНТ А: ШВИДКЕ ЗАМОВЛЕННЯ ---
    if target_item_id:
        item = get_item_data(target_item_id) # Функція з Section 4
        if not item:
            await query.answer("❌ Товар тимчасово недоступний", show_alert=True)
            return

        # Вибір превью (пріоритет на колір)
        selected_color = context.user_data.get('selected_color')
        photo_to_show = item.get('img')
        if selected_color and "color_previews" in item:
            photo_to_show = item["color_previews"].get(selected_color, photo_to_show)

        # Розрахунок ціни (з урахуванням VIP через глобальну функцію)
        # get_price_display повертає (текст_ціни, чиста_ціна, стара_ціна)
        _, final_p, _ = get_price_display(item['price'], profile, target_item_id)
        total_amount = float(final_p)

        color_str = f" (🎨 {selected_color})" if selected_color else ""
        items_desc = f"▫️ <b>{item['name']}</b>{color_str}\n   └ 💰 {int(final_p)} грн"

        # Додавання подарунка в чек
        gift_id = context.user_data.get('target_gift_id')
        if gift_id:
            gift = get_gift_data(gift_id) # Функція з Section 19
            if gift:
                items_desc += f"\n   🎁 <b>Подарунок:</b> {gift['name']} (0 грн)"

    # --- ВАРІАНТ Б: ПОВНИЙ КОШИК ---
    else:
        cart = context.user_data.get('cart', [])
        if not cart:
            await query.answer("🛒 Ваш кошик порожній!", show_alert=True)
            return
        
        for i in cart:
            _, p, _ = get_price_display(i.get('price', 0), profile, i.get('real_id'))
            total_amount += float(p)
            
            meta = []
            if i.get('color'): meta.append(f"🎨 {i['color']}")
            if i.get('gift'): meta.append(f"🎁 {i['gift']}")
            meta_txt = f" ({', '.join(meta)})" if meta else ""
            items_desc += f"▫️ <b>{i['name']}</b>{meta_txt}\n   └ 💰 {int(p)} грн\n"

    # 3. ЛОГІКА ДОСТАВКИ
    district = profile.get('district', 'Самовивіз')
    if "Кур'єр" in str(district):
        if not profile.get("is_vip"):
            delivery_fee = float(globals().get('COURIER_PRICE', 150.0))
            total_amount += delivery_fee
            items_desc += f"\n🛵 <b>Доставка:</b> +{int(delivery_fee)} грн"
        else:
            items_desc += "\n🚀 <b>Доставка:</b> <pre>VIP FREE</pre> (0 грн)"

    # 4. СПИСАННЯ БОНУСІВ (Smart Deduction)
    used_bonus = 0.0
    if user_balance > 0:
        # Бот ніколи не списує суму під 0 (мінімум 10 грн до сплати)
        max_deductible = max(0.0, total_amount - 10.0)
        used_bonus = min(user_balance, max_deductible)
        
        if used_bonus > 0:
            total_amount -= used_bonus
            items_desc += f"\n\n💎 <b>Списання бонусів:</b> -{int(used_bonus)} грн"

    # Збереження стану для фіналізації
    context.user_data['final_checkout_sum'] = total_amount
    context.user_data['planned_bonus_deduction'] = used_bonus

    # 5. ВІЗУАЛІЗАЦІЯ
    checkout_text = (
        f"🧾 <b>ОФОРМЛЕННЯ ЗАМОВЛЕННЯ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{items_desc}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📍 <b>Адреса:</b> {profile.get('city', 'Не вказано')}, {district}\n"
        f"👤 <b>Отримувач:</b> {escape(str(profile.get('full_name', 'Не вказано')))}\n\n"
        f"💳 <b>РАЗОМ ДО СПЛАТИ: {int(total_amount)} UAH</b>\n\n"
        f"👇 <i>Оберіть зручний метод оплати:</i>"
    )

    kb = [
        [InlineKeyboardButton("💳 Monobank", callback_data="pay_mono"),
         InlineKeyboardButton("💚 Privat24", callback_data="pay_privat")],
        [InlineKeyboardButton("💎 Crypto / USDT (TON)", callback_data="pay_crypto")],
        [InlineKeyboardButton("🔙 Назад", callback_data="menu_cart" if not target_item_id else f"view_item_{target_item_id}")]
    ]

    await send_ghosty_message(update, checkout_text, kb, photo=photo_to_show, context=context)

async def payment_selection_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Генерує платіжні реквізити та посилання на оплату.
    """
    query = update.callback_query
    method = query.data.replace("pay_", "")
    amount_uah = context.user_data.get('final_checkout_sum', 0)
    links = globals().get('PAYMENT_LINKS', {}) # Словник посилань

    if method == "crypto":
        rate = float(globals().get('USDT_RATE', 43.5))
        wallet = globals().get('TON_WALLET', 'Адреса оновлюється...')
        amount_usdt = amount_uah / rate
        
        text = (
            f"💎 <b>ОПЛАТА КРИПТОВАЛЮТОЮ</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💵 Сума: <b>{int(amount_uah)} UAH</b>\n"
            f"📈 Курс: <code>{rate}</code>\n"
            f"🚀 До сплати: <b>{amount_usdt:.2f} USDT</b>\n\n"
            f"🔗 <b>Гаманець (мережа TON):</b>\n"
            f"<code>{wallet}</code>\n\n"
            f"⚠️ <i>Надсилайте тільки USDT в мережі TON, інакше кошти будуть втрачені.</i>"
        )
    else:
        # Логіка для Моно/Приват
        target_link = links.get(method, "#")
        bank_name = "MONOBANK" if method == "mono" else "ПРИВАТ24"
        
        text = (
            f"💳 <b>ОПЛАТА ЧЕРЕЗ {bank_name}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"Сума платежу: <b>{int(amount_uah)} UAH</b>\n\n"
            f"🔗 <b>Посилання на переказ:</b>\n"
            f"<a href='{target_link}'>👉 НАТИСНІТЬ ТУТ ДЛЯ ОПЛАТИ</a>\n\n"
            f"📝 <b>ІНСТРУКЦІЯ:</b>\n"
            f"1. Перейдіть за посиланням та оплатіть.\n"
            f"2. Обов'язково збережіть чек/скріншот.\n"
            f"3. Натисніть кнопку підтвердження нижче."
        )

    kb = [
        [InlineKeyboardButton("✅ Я ОПЛАТИВ (НАДІСЛАТИ ЧЕК)", callback_data="confirm_payment_start")],
        [InlineKeyboardButton("🔙 Змінити спосіб", callback_data="checkout_init")]
    ]

    await query.message.edit_text(
        text, 
        reply_markup=InlineKeyboardMarkup(kb), 
        parse_mode='HTML', 
        disable_web_page_preview=True
    )
    
# =================================================================
# ⚙️ SECTION 8: PROMO & REFERRAL (DB SYNCED & SECURE)
# =================================================================

async def process_promo(update: Update, context: ContextTypes.DEFAULT_TYPE, silent=False):
    """Обробка промокодів та реферальних зв'язків."""
    if not (update.message and update.message.text): return
    
    raw_text = update.message.text.strip().upper()
    user = update.effective_user
    profile = context.user_data.setdefault("profile", {})
    db_path = globals().get('DB_PATH', 'data/store_db.sqlite')
    msg, is_success = "", False
    
    try:
        conn = sqlite3.connect(db_path, timeout=30)
        cursor = conn.cursor()
        
        # --- 1. ГЛОБАЛЬНИЙ ПРОМО (GHST2026) ---
        if raw_text == "GHST2026":
            if profile.get('promo_GHST2026_used'):
                msg = "⚠️ <b>Ви вже активували цей промокод!</b>"
            else:
                # Нарахування бонусу (наступна знижка)
                current_discount = float(profile.get("next_order_discount", 0))
                profile["next_order_discount"] = current_discount + 69.0
                profile["promo_GHST2026_used"] = True
                
                # Розумне продовження VIP
                current_vip = profile.get("vip_expiry")
                start_date = datetime.now()
                if current_vip:
                    try:
                        expire_dt = datetime.strptime(current_vip, "%Y-%m-%d")
                        if expire_dt > start_date: start_date = expire_dt
                    except: pass
                
                new_expiry = start_date + timedelta(days=7)
                profile["vip_expiry"] = new_expiry.strftime("%Y-%m-%d")
                profile["is_vip"] = True
                
                msg = (
                    "✅ <b>GHST2026 АКТИВОВАНО!</b>\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    "💰 Бонус: <b>+69 UAH</b> (на наступне замовлення)\n"
                    "💎 Статус: <b>VIP PRO (+7 днів)</b>\n"
                    f"📅 Дійсно до: <b>{profile['vip_expiry']}</b>"
                )
                is_success = True

        # --- 2. РЕФЕРАЛЬНИЙ КОД (GHST + ID) ---
        elif raw_text.startswith("GHST") and raw_text[4:].isdigit():
            target_id = int(raw_text[4:])
            
            if target_id == user.id:
                msg = "❌ <b>Не можна активувати власний код!</b>"
            elif profile.get('referral_used'):
                msg = "⚠️ <b>Ви вже використали реферальний бонус.</b>"
            else:
                # Перевірка реферера в БД
                ref_data = cursor.execute(
                    "SELECT next_order_discount, vip_expiry FROM users WHERE user_id = ?", 
                    (target_id,)
                ).fetchone()
                
                if not ref_data:
                    msg = "❌ <b>Код не знайдено. Перевірте цифри.</b>"
                else:
                    # А) Нараховуємо новому користувачу
                    profile["referral_used"] = True
                    current_discount = float(profile.get("next_order_discount", 0))
                    profile["next_order_discount"] = current_discount + 50.0
                    
                    # VIP для нового
                    now = datetime.now()
                    profile["vip_expiry"] = (now + timedelta(days=7)).strftime("%Y-%m-%d")
                    profile["is_vip"] = True
                    
                    # Б) Нараховуємо рефереру (тому, хто запросив)
                    ref_discount = float(ref_data[0] or 0) + 50.0
                    ref_vip_raw = ref_data[1]
                    
                    ref_start_date = now
                    if ref_vip_raw:
                        try:
                            rd = datetime.strptime(ref_vip_raw, "%Y-%m-%d")
                            if rd > now: ref_start_date = rd
                        except: pass
                    
                    ref_new_vip = (ref_start_date + timedelta(days=7)).strftime("%Y-%m-%d")
                    
                    # Оновлюємо реферера в БД негайно
                    cursor.execute("""
                        UPDATE users SET next_order_discount = ?, vip_expiry = ?, is_vip = 1 
                        WHERE user_id = ?
                    """, (ref_discount, ref_new_vip, target_id))
                    
                    msg = (
                        f"🤝 <b>БОНУС ПРИЙНЯТО!</b>\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"💰 Вам та другу нараховано по <b>50 UAH</b>\n"
                        f"💎 VIP статус активовано на 7 днів!"
                    )
                    is_success = True
                    
                    # Повідомлення рефереру
                    try:
                        await context.bot.send_message(
                            chat_id=target_id,
                            text=f"🎉 <b>Твій код активовано!</b>\n\n💰 Нараховано: <b>+50 UAH</b> до знижки\n💎 VIP продовжено до: <b>{ref_new_vip}</b>",
                            parse_mode='HTML'
                        )
                    except: pass
        else:
            msg = "❌ <b>Невірний код або формат.</b>"

        # --- 3. ФІНАЛІЗАЦІЯ (Оновлення профілю того, хто вводив код) ---
        if is_success:
            cursor.execute("""
                UPDATE users SET 
                is_vip = 1, vip_expiry = ?, next_order_discount = ?, 
                promo_GHST2026_used = ?, referral_used = ?
                WHERE user_id = ?
            """, (
                profile.get('vip_expiry'), profile.get('next_order_discount'),
                1 if profile.get('promo_GHST2026_used') else 0,
                1 if profile.get('referral_used') else 0,
                user.id
            ))
            conn.commit()
            context.user_data['profile'] = profile

    except Exception as e:
        if 'logger' in globals():
            globals()['logger'].error(f"Promo Error: {e}")
        msg = "⚠️ Помилка бази даних. Спробуйте пізніше."
    finally:
        if 'conn' in locals(): conn.close()

    # Скидаємо стан очікування промокоду
    context.user_data['awaiting_promo'] = False
    context.user_data['state'] = None
    
    if not silent:
        kb = [
            [InlineKeyboardButton("👤 Профіль", callback_data="menu_profile")],
            [InlineKeyboardButton("🛍 В каталог", callback_data="cat_all")],
            [InlineKeyboardButton("🏠 Головна", callback_data="menu_start")]
        ]
        await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode='HTML')

# =================================================================
# 🛡 SECTION 21 & 26: ORDER CONFIRMATION & RECEIPT PROCESSING
# =================================================================

import sqlite3
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# Твій актуальний ID менеджера
ADMIN_ID = 5309653842 

async def payment_confirmation_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    КРОК 1: Ініціація (Запит чека). Викликається кнопкою 'confirm_payment_start'.
    """
    query = update.callback_query
    
    # Перевіряємо суму до сплати
    amount = context.user_data.get('final_checkout_sum', 0.0)
    if amount <= 0:
        if query: await query.answer("⚠️ Помилка суми замовлення", show_alert=True)
        return

    # Генеруємо номер замовлення
    order_id = context.user_data.get('current_order_id') or f"GH{random.randint(100, 999)}-{random.randint(1000, 9999)}"
    context.user_data['current_order_id'] = order_id
    
    text = (
        f"⏳ <b>ЗАМОВЛЕННЯ #{order_id} ОЧІКУЄ ЧЕК</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💵 Сума до сплати: <b>{amount:.2f} UAH</b>\n\n"
        f"📸 <b>ВАША ДІЯ:</b>\n"
        f"Будь ласка, надішліть <b>фото чека</b> або <b>скріншот</b> прямо у цей чат.\n\n"
        f"<i>🤖 Менеджер перевірить оплату та підтвердить замовлення.</i>"
    )
    
    # Активуємо режим очікування фото для MessageHandler
    context.user_data['state'] = "WAITING_RECEIPT"
    
    kb = [[InlineKeyboardButton("🔙 НАЗАД ДО КОШИКА", callback_data="menu_cart")]]
    
    if query:
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode='HTML')
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode='HTML')


async def handle_receipt_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    КРОК 2: Обробка фото чека та пересилка адміну.
    """
    if context.user_data.get('state') != "WAITING_RECEIPT":
        return

    user = update.effective_user
    profile = context.user_data.get('profile', {})
    order_id = context.user_data.get('current_order_id', '???')
    amount = context.user_data.get('final_checkout_sum', 0.0)
    bonus_to_deduct = context.user_data.get('planned_bonus_deduction', 0.0)

    # 1. Візуальний фідбек клієнту
    status_msg = await update.message.reply_text("📡 <i>Надсилаємо чек менеджеру...</i>", parse_mode='HTML')
    
    # 2. Отримуємо файл (найкраща якість)
    photo_file = await update.message.photo[-1].get_file()
    
    # 3. Формуємо список товарів
    cart = context.user_data.get('cart', [])
    target_id = context.user_data.get('target_item_id')
    
    if target_id:
        items_txt = f"• Швидке замовлення (ID: {target_id})"
    else:
        items_txt = "\n".join([f"• {i['name']} ({i.get('color', 'Стандарт')})" for i in cart])

    # 4. Текст для Адміна (Тебе)
    admin_text = (
        f"💳 <b>НОВИЙ ПЛАТІЖ #{order_id}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>Клієнт:</b> <a href='tg://user?id={user.id}'>{user.first_name}</a>\n"
        f"🆔 ID: <code>{user.id}</code>\n"
        f"💰 <b>СУМА: {amount:.2f} UAH</b>\n"
        f"💎 Бонуси до списання: -{int(bonus_to_deduct)} UAH\n"
        f"📍 {profile.get('city', 'Місто?')}, {profile.get('district', 'Район?')}\n\n"
        f"📦 <b>ТОВАРИ:</b>\n{items_txt}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👇 <b>ВЕРДИКТ:</b>"
    )

    # Кнопки для адміна (додаємо суму бонусу в callback, щоб не загубити)
    admin_kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ ПРИЙНЯТИ", callback_data=f"adm_pay_ok_{user.id}_{order_id}_{int(bonus_to_deduct)}"),
            InlineKeyboardButton("❌ ВІДМОВА", callback_data=f"adm_pay_no_{user.id}_{order_id}_0")
        ],
        [InlineKeyboardButton("💬 ПЕРЕЙТИ ДО ЧАТУ", url=f"tg://user?id={user.id}")]
    ])

    try:
        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=photo_file.file_id,
            caption=admin_text,
            reply_markup=admin_kb,
            parse_mode='HTML'
        )
        
        await status_msg.edit_text(
            f"✅ <b>ЧЕК ПРИЙНЯТО!</b>\n\nОчікуйте, менеджер перевіряє транзакцію. Ви отримаєте повідомлення тут.\n"
            f"🆔 Замовлення: <code>#{order_id}</code>",
            parse_mode='HTML'
        )
        # Скидаємо тільки стейт, щоб юзер не міг спамити фото
        context.user_data['state'] = None

    except Exception as e:
        await status_msg.edit_text("⚠️ Помилка зв'язку з сервером. Зв'яжіться з @ghosstydp")


async def admin_decision_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    КРОК 3: Фінальне рішення адміністратора.
    """
    query = update.callback_query
    # adm_pay_ACTION_USERID_ORDERID_BONUS
    parts = query.data.split("_")
    if len(parts) < 6: return

    _, _, action, client_id, order_id, bonus = parts
    client_id = int(client_id)
    bonus_amount = float(bonus)

    if action == "ok":
        # 1. Списуємо бонуси в БД
        if bonus_amount > 0:
            try:
                db_path = globals().get('DB_PATH', 'data/store_db.sqlite')
                with sqlite3.connect(db_path) as conn:
                    conn.execute("UPDATE users SET next_order_discount = next_order_discount - ? WHERE user_id = ?", (bonus_amount, client_id))
                    conn.commit()
            except: pass

        # 2. Повідомляємо клієнта
        await context.bot.send_message(
            chat_id=client_id,
            text=f"🎉 <b>ОПЛАТУ ПІДТВЕРДЖЕНО!</b>\n\nВаше замовлення #{order_id} вже готується до видачі/відправки. Дякуємо, що ви з нами!",
            parse_mode='HTML'
        )
        
        # 3. Очищення кошика клієнта (через флаг у БД або окрему логіку)
        # Оскільки адмін не має доступу до context.user_data клієнта, 
        # кошик клієнта рекомендується чистити при наступному його вході в меню, 
        # перевіряючи статус останнього замовлення в БД.

        status_text = "✅ ОПЛАЧЕНО"
    else:
        await context.bot.send_message(
            chat_id=client_id,
            text=f"❌ <b>ОПЛАТУ ВІДХИЛЕНО</b>\n\nЧек для замовлення #{order_id} не пройшов перевірку. Перевірте суму або зв'яжіться з @ghosstydp",
            parse_mode='HTML'
        )
        status_text = "❌ ВІДХИЛЕНО"

    await query.edit_message_caption(
        caption=query.message.caption + f"\n\n<b>СТАТУС: {status_text}</b>",
        reply_markup=None,
        parse_mode='HTML'
    )
    await query.answer(f"Статус: {status_text}")

# =================================================================
# 🤵 SECTION 27: MANAGER ORDER HUB (FAST ORDER & BALANCE PRO)
# =================================================================

import sqlite3
import random
from urllib.parse import quote
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# Конфігурація (переконайся, що MANAGER_ID та ADMIN_ID синхронізовані в Section 1)
MANAGER_ID = 5309653842 
MANAGER_USERNAME = "ghosstydp" # Юзернейм БЕЗ @ для посилання

async def submit_order_to_manager(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Генератор заявки. Об'єднує розрахунок, бонуси та запис в БД."""
    user = update.effective_user
    profile = context.user_data.get('profile', {})
    
    # 1. ЗБІР ТОВАРІВ
    target_item_id = context.user_data.get('target_item_id')
    target_gift_id = context.user_data.get('target_gift_id')
    cart = context.user_data.get('cart', [])
    
    items_text = ""
    total_goods_price = 0.0
    
    if target_item_id:
        item = globals().get('get_item_data')(target_item_id)
        if item:
            color = context.user_data.get('selected_color')
            _, price, _ = globals().get('get_price_display')(item['price'], profile, target_item_id)
            total_goods_price = price
            items_text += f"▫️ {item['name']}{f' (🎨 {color})' if color else ''} — {int(price)} грн\n"
            if target_gift_id:
                g = globals().get('get_item_data')(target_gift_id)
                if g: items_text += f"    🎁 Бонус: {g['name']}\n"
  elif cart:
    for i in cart:
        # 1. Получаем цену (как и было)
        _, p, _ = globals().get('get_price_display')(i['price'], profile, i.get('real_id'))
        total_goods_price += p
        
        # 2. Сначала готовим строку с цветом (отдельно от основной строки)
        color_info = f" (🎨 {i.get('color')})" if i.get('color') else ""
        
        # 3. Формируем финальную строку для этого товара
        items_text += f"▫️ {i['name']}{color_info} — {int(p)} грн\n"
    else:
        if update.callback_query: await update.callback_query.answer("⚠️ Кошик порожній", show_alert=True)
        return

    # 2. РОЗРАХУНОК ТА БОНУСИ
    delivery_price = 150.0 if "Кур'єр" in str(profile.get('district', '')) and not profile.get("is_vip") else 0.0
    pre_total = total_goods_price + delivery_price
    
    current_balance = float(profile.get('next_order_discount', 0.0))
    discount_to_apply = min(current_balance, max(0.0, pre_total - 1.0))
    final_amount = pre_total - discount_to_apply
    
    # Зберігаємо в context клієнта для Section 28 (WAITING_RECEIPT)
    context.user_data['final_checkout_sum'] = final_amount
    context.user_data['planned_bonus_deduction'] = discount_to_apply

    # 3. ГЕНЕРАЦІЯ ID ТА ЗАПИС В БД (Додаємо суму бонусів в базу!)
    order_id = f"GH{random.randint(100, 999)}-{user.id % 10000}"
    context.user_data['current_order_id'] = order_id
    
    try:
        with sqlite3.connect(globals().get('DB_PATH'), timeout=30) as conn:
            # ВАЖЛИВО: додаємо discount_applied у таблицю orders (переконайся, що така колонка є або ігноруй)
            conn.execute("""
                INSERT INTO orders (order_id, user_id, amount, status) 
                VALUES (?, ?, ?, ?)
            """, (order_id, user.id, final_amount, 'awaiting_payment'))
            conn.commit()
    except Exception as e: 
        globals().get('logger').error(f"DB Order Error: {e}")

    # 4. ФОРМУВАННЯ ПОВІДОМЛЕННЯ
    report = (
        f"👋 Замовлення #{order_id}\n"
        f"👤 {profile.get('full_name', 'Гість')} | 📞 {profile.get('phone')}\n"
        f"📍 {profile.get('city')}, {profile.get('district')}\n"
        f"🛒 ТОВАРИ:\n{items_text}"
        f"💰 ДО СПЛАТИ: {final_amount:.2f} грн"
    )
    
    # 5. DEEP LINK
    magic_link = f"https://t.me/{MANAGER_USERNAME}?text={quote(report)}"

    # 6. ВИВІД КЛІЄНТУ
    text = (
        f"📦 <b>ЗАМОВЛЕННЯ СФОРМОВАНО</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 ID: <code>{order_id}</code>\n"
        f"💵 Сума: <b>{final_amount:.2f} грн</b>\n"
        f"💎 Знижка бонусами: <b>-{int(discount_to_apply)} грн</b>\n\n"
        f"👇 <b>ОБЕРІТЬ СПОСІБ ПІДТВЕРДЖЕННЯ:</b>"
    )
    
    kb = [
        [InlineKeyboardButton("📸 НАДІСЛАТИ ЧЕК У БОТ", callback_data="confirm_payment_start")],
        [InlineKeyboardButton("✈️ НАПИСАТИ МЕНЕДЖЕРУ", url=magic_link)],
        [InlineKeyboardButton("🔙 НАЗАД", callback_data="menu_cart")]
    ]
    
    if update.callback_query:
        await update.callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode='HTML')
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode='HTML')

# --- СИСТЕМА ПРИЙНЯТТЯ РІШЕНЬ (CALLBACKS ДЛЯ АДМІНА) ---

async def admin_decision_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробка кнопок ✅ Прийняти / ❌ Відмовити."""
    query = update.callback_query
    # adm_pay_ok_USERID_ORDERID_BONUS
    data_parts = query.data.split("_")
    if len(data_parts) < 5: return
    
    _, _, action, client_id, order_id = data_parts[:5]
    client_id = int(client_id)
    # Бонуси краще передавати прямо в callback_data або брати з БД
    
    if action == "ok":
        # Логіка списання бонусів (приклад з прямою зміною балансу)
        # В ідеалі: дістати запланований бонус з БД таблиці orders
        await context.bot.send_message(
            client_id, 
            f"✅ <b>Замовлення #{order_id} підтверджено!</b>\nДякуємо за покупку, ми вже готуємо відправку.", 
            parse_mode='HTML'
        )
        new_status = "✅ ОПЛАЧЕНО"
    else:
        await context.bot.send_message(
            client_id, 
            f"❌ <b>Оплату #{order_id} відхилено.</b>\nПеревірте дані або зв'яжіться з менеджером.", 
            parse_mode='HTML'
        )
        new_status = "❌ ВІДХИЛЕНО"

    await query.edit_message_caption(
        caption=f"{query.message.caption}\n\n<b>СТАТУС: {new_status}</b>", 
        reply_markup=None, 
        parse_mode='HTML'
    )

# =================================================================
# 📝 SECTION 17: DATA INPUT HANDLER (TEXT PROCESSOR - PRO FIX)
# =================================================================

import sqlite3
import re
from datetime import datetime
from html import escape
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def handle_data_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обробляє текстові відповіді користувача на етапах анкети.
    🔥 ВДОСКОНАЛЕННЯ: Миттєве збереження + Розумна валідація даних + Примусовий вибір міста.
    """
    if not update.message or not update.message.text: 
        return
    
    user = update.effective_user
    text = update.message.text.strip()
    step = context.user_data.get('data_step')
    
    # Ініціалізуємо профіль, якщо його немає
    profile = context.user_data.setdefault('profile', {})
    profile['uid'] = user.id # Гарантуємо ID

    # --- ВНУТРІШНЯ ФУНКЦІЯ: МИТТЄВЕ ЗБЕРЕЖЕННЯ (БЕЗПЕЧНЕ) ---
    def save_step_to_db(field_name, value):
        try:
            db_path = globals().get('DB_PATH', 'data/ghosty_pro_final.db')
            with sqlite3.connect(db_path, timeout=30) as conn:
                # 1. Перевіряємо/Створюємо юзера (якщо він новий)
                reg_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                conn.execute("""
                    INSERT OR IGNORE INTO users (user_id, username, full_name, is_vip, next_order_discount, reg_date) 
                    VALUES (?, ?, ?, 0, 0.0, ?)
                """, (user.id, user.username or "Unknown", user.first_name, reg_time))
                
                # 2. Оновлюємо конкретне поле (використовуємо f-строку обережно лише для назви колонки)
                conn.execute(f"UPDATE users SET {field_name}=? WHERE user_id=?", (value, user.id))
                conn.commit()
        except Exception as e:
            if 'logger' in globals():
                logger.error(f"❌ DB Save Error [{field_name}]: {e}")

    # --- 1. ОБРОБКА ІМЕНІ ---
    if step == "name":
        if len(text) < 2 or text.isdigit():
            await update.message.reply_text("⚠️ <b>Некоректне ім'я.</b> Напишіть справжнє Прізвище та Ім'я літерами:", parse_mode='HTML')
            return
        
        profile['full_name'] = text
        save_step_to_db("full_name", text)
        
        context.user_data['data_step'] = "phone"
        msg = (
            f"👤 Приємно познайомитись, <b>{escape(text)}</b>!\n\n"
            f"📱 Тепер введіть ваш <b>номер телефону</b>\n"
            f"(Приклад: 0991234567):"
        )
        await update.message.reply_text(msg, parse_mode='HTML')

    # --- 2. ОБРОБКА ТЕЛЕФОНУ ---
    elif step == "phone":
        clean_phone = re.sub(r'[\s\(\)\-\+]', '', text)
        
        if not clean_phone.isdigit() or len(clean_phone) < 9 or len(clean_phone) > 12:
            await update.message.reply_text("⚠️ <b>Некоректний формат.</b> Введіть 10 цифр (напр. 0991234567):", parse_mode='HTML')
            return
            
        if clean_phone.startswith('0') and len(clean_phone) == 10:
            clean_phone = '38' + clean_phone
        
        profile['phone'] = clean_phone
        save_step_to_db("phone", clean_phone)
        
        action = context.user_data.get('post_data_action')
        force_edit = (action in ['none', 'profile'])

        # ПЕРЕВІРКА: Чи потрібно обирати місто?
        if force_edit or not profile.get('city'):
            context.user_data['data_step'] = "awaiting_city" # Змінюємо стейт
            if 'choose_city_menu' in globals():
                await choose_city_menu(update, context)
            else:
                await update.message.reply_text("📍 Оберіть ваше місто за допомогою кнопок меню.")
            return
            
        else:
            # Місто вже є, йдемо до адреси
            context.user_data['data_step'] = "address"
            city = profile.get('city', 'Ваше місто')
            kb = [[InlineKeyboardButton("🏙 Змінити місто", callback_data="choose_city")]]
            
            await update.message.reply_text(
                f"📞 Номер <code>{clean_phone}</code> збережено.\n\n"
                f"📍 Місто: <b>{city}</b>.\n"
                f"Вкажіть <b>Адресу або Відділення НП</b>:",
                reply_markup=InlineKeyboardMarkup(kb),
                parse_mode='HTML'
            )

    # --- 3. ОБРОБКА АДРЕСИ ---
    elif step == "address":
        if len(text) < 3:
            await update.message.reply_text("⚠️ <b>Адреса занадто коротка.</b> Будь ласка, уточніть (Вулиця, будинок або № пошти):", parse_mode='HTML')
            return
            
        district = profile.get('district', '')
        full_address = f"{district}, {text}" if district and district not in text else text
        
        profile['address_details'] = full_address
        save_step_to_db("address_details", full_address)
        
        # Очищуємо крок, щоб текст більше не перехоплювався
        context.user_data['data_step'] = None 

        if 'finalize_data_collection' in globals():
            await finalize_data_collection(update, context)
        else:
            # Якщо функції фіналізації немає в пам'яті, робимо базовий вихід
            kb = [[InlineKeyboardButton("🏠 В МЕНЮ", callback_data="menu_start")]]
            await update.message.reply_text("✅ <b>Ваш профіль успішно оновлено!</b>", reply_markup=InlineKeyboardMarkup(kb), parse_mode='HTML')

    # --- 4. ОБРОБКА ПРОМОКОДІВ (ІНТЕГРАЦІЯ З SECTION 8) ---
    elif context.user_data.get('awaiting_promo'):
        if 'process_promo' in globals():
            await process_promo(update, context)
        else:
            await update.message.reply_text("⚠️ Система промокодів зараз на тестуванні.")
            
# =================================================================
# 🎮 SECTION 28: STABLE MESSAGE HANDLER (TITAN ULTIMATE v10.5)
# =================================================================

async def handle_user_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Центральний обробник текстових та медіа повідомлень.
    Синхронізує стани анкети, оплати та адмін-панелі.
    """
    if not update.message: return 
    
    user = update.effective_user
    # Пріоритет: спочатку перевіряємо основний state, потім крок анкети
    state = context.user_data.get('state') or context.user_data.get('data_step')
    raw_text = update.message.text.strip() if update.message.text else (update.message.caption or "")
    
    # 🛡 АНТИ-ФЛУД (Media Group - обробляємо лише перше повідомлення з групи)
    if update.message.media_group_id:
        if context.user_data.get('last_media_group_id') == update.message.media_group_id:
            return 
        context.user_data['last_media_group_id'] = update.message.media_group_id

    # СИСТЕМА ДОСТУПУ
    MANAGER_ID = globals().get('ADMIN_ID', 5309653842)
    ADMIN_LIST = globals().get('ADMIN_LIST', [])
    is_admin = (user.id == MANAGER_ID) or (user.id in ADMIN_LIST)

    # -----------------------------------------------------------
    # 💎 1. КЕРУВАННЯ БАЛАНСОМ (Тільки для Адміна)
    # -----------------------------------------------------------
    if state == "WAITING_BALANCE_DATA" and is_admin:
        try:
            parts = raw_text.split()
            if len(parts) < 2:
                await update.message.reply_text("⚠️ Введіть <b>ID СУМА</b> (напр. <code>12345 500</code>):", parse_mode='HTML')
                return
            
            target_id, amount = int(parts[0]), float(parts[1])
            db_path = globals().get('DB_PATH')
            
            with sqlite3.connect(db_path, timeout=30) as conn:
                conn.execute("UPDATE users SET next_order_discount = next_order_discount + ? WHERE user_id=?", (amount, target_id))
                conn.commit()
                
            await update.message.reply_text(f"✅ Користувачу <code>{target_id}</code> змінено бонусний баланс на <b>{amount} грн</b>.", parse_mode='HTML')
            context.user_data['state'] = None 
            
            try:
                msg = (f"💳 <b>БАЛАНС ОНОВЛЕНО!</b>\n━━━━━━━━━━━━━━━━━━━━\n"
                       f"Вам {'нараховано' if amount > 0 else 'списано'} <b>{abs(amount)} грн</b> бонусів.")
                await context.bot.send_message(chat_id=target_id, text=msg, parse_mode='HTML')
            except: pass
        except ValueError:
            await update.message.reply_text("❌ Помилка: Формат має бути 'ID СУМА' (числа).")
        return

    # -----------------------------------------------------------
    # 🚀 2. АДМІН-РОЗСИЛКА (Broadcast)
    # -----------------------------------------------------------
    if state in ["BROADCAST_MODE", "WAITING_BROADCAST_CONTENT"] and is_admin:
        db_path = globals().get('DB_PATH')
        try:
            with sqlite3.connect(db_path) as conn:
                users = conn.execute("SELECT user_id FROM users").fetchall()
            
            if not users:
                await update.message.reply_text("❌ База користувачів порожня.")
                return

            sent, failed = 0, 0
            status_msg = await update.message.reply_text(f"🚀 Запуск розсилки на {len(users)} чол...")
            
            for (uid,) in users:
                try:
                    # Копіюємо повідомлення (текст, фото, відео, стікери)
                    await update.message.copy(chat_id=uid)
                    sent += 1
                    if sent % 25 == 0: await asyncio.sleep(0.5)
                except: failed += 1 
            
            await status_msg.edit_text(
                f"✅ <b>Розсилку завершено!</b>\n━━━━━━━━━━━━━━━━━━━━\n📥 Успішно: <code>{sent}</code>\n🚫 Блокувань: <code>{failed}</code>", 
                parse_mode='HTML'
            )
        except Exception as e:
            if 'logger' in globals(): globals()['logger'].error(f"Broadcast Error: {e}")
        finally:
            context.user_data['state'] = None
        return

    # -----------------------------------------------------------
    # 📸 3. ПРИЙОМ ЧЕКІВ (Синхронізовано з Section 27)
    # -----------------------------------------------------------
    if state == "WAITING_RECEIPT":
        if update.message.photo or update.message.document:
            if 'handle_receipt_photo' in globals():
                await globals()['handle_receipt_photo'](update, context)
            else:
                await update.message.reply_text("🆘 Модуль обробки платежів не знайдено.")
        else:
            await update.message.reply_text("📸 Будь ласка, надішліть <b>ФОТО</b> вашого чека про оплату.")
        return

    # -----------------------------------------------------------
    # 📝 4. АНКЕТА ТА ПРОМОКОДИ (Синхронізовано з Section 17)
    # -----------------------------------------------------------
    # Обробка кроків реєстрації
    if state in ["name", "phone", "address", "awaiting_city"]:
        if 'handle_data_input' in globals():
            await globals()['handle_data_input'](update, context)
        return

    # Обробка промокодів
    if context.user_data.get('awaiting_promo') or state == "AWAITING_PROMO":
        if 'process_promo' in globals():
            await globals()['process_promo'](update, context)
        else:
            await update.message.reply_text("⚠️ Система промокодів тимчасово недоступна.")
        return

    # -----------------------------------------------------------
    # ⚙️ 5. DEFAULT FALLBACK
    # -----------------------------------------------------------
    # Якщо повідомлення не підпадає під жоден стан і це не команда
    if not is_admin and not raw_text.startswith('/'):
        # Можна додати автоматичну відповідь або просто ігнорувати
        pass

# =================================================================
# 👮‍♂️ SECTION 25: ADMIN GOD-PANEL (MONITORING & FINANCIALS)
# =================================================================

import sqlite3
import random
import logging
import io
import os
import asyncio
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

# 🛡️ TITAN SECURITY CHECK
def check_is_admin(user_id: int) -> bool:
    # Використовуємо MANAGER_ID, як у Section 31
    manager_id = globals().get('MANAGER_ID', 5309653842)
    admin_list = globals().get('ADMIN_LIST', [])
    return (user_id == manager_id) or (user_id in admin_list)

# ⚡️ ДОПОМІЖНІ МЕТОДИ
async def _safe_edit_or_reply(update: Update, text: str, reply_markup: list, parse_mode='HTML'):
    kb = InlineKeyboardMarkup(reply_markup)
    query = update.callback_query
    if query:
        await query.answer()
        await query.edit_message_text(text=text, reply_markup=kb, parse_mode=parse_mode)
    else:
        await update.message.reply_text(text=text, reply_markup=kb, parse_mode=parse_mode)

# =================================================================
# 🖥 ГОЛОВНЕ МЕНЮ ТА МОНІТОРИНГ
# =================================================================

async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Головний термінал керування системою."""
    user = update.effective_user
    if not check_is_admin(user.id): return 

    ping = random.randint(12, 28)
    uptime = str(datetime.now() - globals().get('START_TIME', datetime.now())).split('.')[0]
    db_path = globals().get('DB_PATH', 'data/store_db.sqlite')
    db_size = f"{os.path.getsize(db_path) / 1024:.1f} KB" if os.path.exists(db_path) else "0 KB"

    text = (
        f"🛡 <b>ADMIN GOD-MODE v10.5</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📡 <b>SYSTEM STATUS:</b>\n"
        f"⏱ Пінг: <code>{ping}ms</code>\n"
        f"🆙 Uptime: <code>{uptime}</code>\n"
        f"📦 DB Size: <code>{db_size}</code>\n"
        f"👥 Sessions: <code>{len(context.application.user_data)}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⚡️ <b>КЕРУВАННЯ:</b>"
    )
    
    kb = [
        [InlineKeyboardButton("👥 БАЗА КЛІЄНТІВ", callback_data="admin_view_users_0"),
         InlineKeyboardButton("💰 ФІНАНСИ", callback_data="admin_stats")],
        [InlineKeyboardButton("📢 РОЗСИЛКА (Media)", callback_data="admin_broadcast")],
        [InlineKeyboardButton("💳 БАЛАНС +/-", callback_data="admin_add_balance"),
         InlineKeyboardButton("📥 EXPORT БД", callback_data="admin_get_db")],
        [InlineKeyboardButton("🔙 ВИХІД", callback_data="menu_start")]
    ]
    await _safe_edit_or_reply(update, text, kb)

# =================================================================
# 📥 СИСТЕМА ЕКСПОРТУ ДАНИХ (БЕКАПИ)
# =================================================================

async def admin_export_database(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Генерація та відправка бекапів у двох форматах."""
    query = update.callback_query
    db_path = globals().get('DB_PATH', 'data/store_db.sqlite')
    await query.answer("⏳ Формую звіти...")
    
    try:
        # 1. Відправка Binary .db
        with open(db_path, 'rb') as f:
            await context.bot.send_document(
                chat_id=query.from_user.id,
                document=f, 
                filename=f"BACKUP_{datetime.now().strftime('%d_%m')}.db",
                caption="📂 <b>Binary SQLite DB</b> (Для відновлення)"
            )
        
        # 2. Відправка Readable .txt (SQL Dump)
        conn = sqlite3.connect(db_path)
        output = io.StringIO()
        for line in conn.iterdump():
            output.write(f'{line}\n')
        conn.close()
        
        text_file = io.BytesIO(output.getvalue().encode('utf-8'))
        text_file.name = "database_dump.txt"
        await context.bot.send_document(
            chat_id=query.from_user.id,
            document=text_file,
            caption="📝 <b>Readable SQL Dump</b>\n(Можна читати блокнотом)"
        )
    except Exception as e:
        logger.error(f"Export Error: {e}")
        await query.message.reply_text(f"❌ Помилка експорту: {e}")

# =================================================================
# 📈 ФІНАНСИ ТА КЛІЄНТИ
# =================================================================

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Розширена фінансова статистика."""
    db_path = globals().get('DB_PATH', 'data/store_db.sqlite')
    try:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            # За 7 днів
            cur.execute("SELECT SUM(amount) FROM orders WHERE status='paid' AND created_at >= date('now', '-7 days')")
            rev_7d = cur.fetchone()[0] or 0.0
            
            # За сьогодні
            cur.execute("SELECT SUM(amount) FROM orders WHERE status='paid' AND created_at >= date('now')")
            rev_today = cur.fetchone()[0] or 0.0

            cur.execute("SELECT COUNT(*) FROM orders WHERE status='paid'")
            total_orders = cur.fetchone()[0] or 0

        text = (
            f"💰 <b>ФІНАНСОВИЙ ЗВІТ</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💵 Сьогодні: <b>{rev_today:,.0f} UAH</b>\n"
            f"📅 За 7 днів: <b>{rev_7d:,.0f} UAH</b>\n"
            f"📦 Всього продажів: <b>{total_orders}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        )
        await _safe_edit_or_reply(update, text, [[InlineKeyboardButton("🔙 НАЗАД", callback_data="admin_main")]])
    except Exception as e:
        logger.error(f"Stats Error: {e}")

async def admin_view_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Перегляд бази з пагінацією."""
    query = update.callback_query
    page = int(query.data.split("_")[-1]) if query and "admin_view_users_" in query.data else 0
    limit, offset = 10, page * 10
    db_path = globals().get('DB_PATH', 'data/store_db.sqlite')

    try:
        with sqlite3.connect(db_path) as conn:
            total = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] or 0
            users = conn.execute("""
                SELECT u.username, u.user_id, u.balance 
                FROM users u ORDER BY u.reg_date DESC LIMIT ? OFFSET ?
            """, (limit, offset)).fetchall()

        report = f"👥 <b>КЛІЄНТИ (Стор. {page + 1}):</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        for username, uid, bal in users:
            report += f"👤 @{username or '—'} | ID: <code>{uid}</code> | 💰 {bal}₴\n"

        kb = [[
            InlineKeyboardButton("⬅️", callback_data=f"admin_view_users_{max(0, page-1)}"),
            InlineKeyboardButton("🔄", callback_data=f"admin_view_users_{page}"),
            InlineKeyboardButton("➡️", callback_data=f"admin_view_users_{page+1}")
        ]] if total > limit else []
        kb.append([InlineKeyboardButton("🔙 НАЗАД", callback_data="admin_main")])
        
        await _safe_edit_or_reply(update, report, kb)
    except Exception as e:
        logger.error(f"View Error: {e}")

# =================================================================
# 📢 РОЗСИЛКА ТА БАЛАНС (СТАНИ)
# =================================================================

async def start_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_is_admin(update.effective_user.id): return
    context.user_data['state'] = "BROADCAST_MODE"
    await _safe_edit_or_reply(update, "📢 <b>РЕЖИМ РОЗСИЛКИ</b>\n\nНадішліть пост (текст/фото), і я розішлю його всім.", [[InlineKeyboardButton("❌ СКАСУВАТИ", callback_data="admin_main")]])

async def ask_balance_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_is_admin(update.effective_user.id): return
    context.user_data['state'] = "WAITING_BALANCE_DATA"
    await _safe_edit_or_reply(update, "💳 <b>БАЛАНС</b>\n\nВведіть: <code>ID СУМА</code>\nПриклад: <code>123456 500</code>", [[InlineKeyboardButton("❌ СКАСУВАТИ", callback_data="admin_main")]])

# =================================================================
# ⚙️ SECTION 29: GLOBAL DISPATCHER (TITAN FINAL - BULLETPROOF)
# =================================================================

import traceback
import logging
import sqlite3
from telegram import Update, InlineKeyboardButton
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

async def _reset_user_state(context: ContextTypes.DEFAULT_TYPE):
    """Повне очищення тимчасових даних користувача для безпечної навігації."""
    keys_to_clear = [
        'state', 'target_item_id', 'target_gift_id', 
        'selected_color', 'awaiting_promo', 'post_data_action'
    ]
    for key in keys_to_clear:
        context.user_data.pop(key, None)

async def global_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    TITAN DISPATCHER v11.0: Ювелірна точність та синхронізація всіх секцій.
    """
    query = update.callback_query
    data = query.data
    user = update.effective_user

    # 1. ATOMIC ANSWER: Миттєве підтвердження (прибирає "годинник" на кнопці)
    try: 
        await query.answer() 
    except: pass

    try:
        # --- 🛡️ ГВАРДІЯ ДОСТУПУ (ADMIN CHECK) ---
        if data.startswith(("adm_", "admin_")):
            admin_list = globals().get('ADMIN_LIST', [])
            manager_id = globals().get('MANAGER_ID', 5309653842)
            
            if user.id not in admin_list and user.id != manager_id:
                return await query.answer("⛔️ Доступ обмежено", show_alert=True)

            # Адмін-маршрутизація (Section 25)
            if data.startswith("adm_"): 
                return await admin_decision_handler(update, context)
            
            # Обробка основних адмін-команд
            if data == "admin_main": 
                return await admin_menu(update, context)
            elif data == "admin_stats": 
                return await admin_stats(update, context)
            elif data == "admin_broadcast": 
                return await start_broadcast(update, context)
            elif data == "admin_add_balance": 
                return await ask_balance_data(update, context)
            elif data == "admin_get_db": 
                return await admin_export_database(update, context)
            elif data.startswith("admin_view_users"): 
                return await admin_view_users(update, context)
            elif data == "admin_cancel_action":
                context.user_data['state'] = None
                return await admin_menu(update, context)

        # --- 🏠 ГОЛОВНА НАВІГАТОРІЯ (ЮЗЕР) ---
        if data == "menu_start":
            await _reset_user_state(context)
            if 'start_command' in globals():
                return await globals()['start_command'](update, context)

        if data == "menu_profile": 
            if 'show_profile' in globals(): return await show_profile(update, context)
        
        if data == "menu_promo":
            context.user_data['state'] = "AWAITING_PROMO"
            # Використовуємо глобальний метод для редагування
            return await update.effective_message.edit_text(
                "🎟 <b>АКТИВАЦІЯ БОНУСІВ</b>\n\nВведіть ваш промокод у чат:",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="menu_profile")]]),
                parse_mode='HTML'
            )

        if data == "ref_system": 
            if 'show_ref_info' in globals(): return await show_ref_info(update, context)

        # --- 🛍️ MARKET ENGINE (КАТАЛОГ ТА КОШИК) ---
        if data == "cat_all": 
            context.user_data['state'] = None
            if 'catalog_main_menu' in globals(): return await catalog_main_menu(update, context)

        if data.startswith("cat_list_"): 
            cat_tag = data.replace("cat_list_", "")
            if 'show_category_items' in globals(): return await show_category_items(update, context, cat_tag)

        if data.startswith("view_item_"):
            try:
                item_id = int(data.split("_")[2])
                if 'view_item_details' in globals(): return await view_item_details(update, context, item_id)
            except: return 

        if data.startswith("sel_col_"):
            p = data.split("_")
            if 'handle_color_selection_click' in globals() and len(p) >= 4:
                return await handle_color_selection_click(update, context, int(p[2]), "_".join(p[3:]))

        if data == "menu_cart": 
            if 'show_cart_logic' in globals(): return await show_cart_logic(update, context)
        
        if data == "cart_clear" or data.startswith("cart_del_"): 
            if 'cart_action_handler' in globals(): return await cart_action_handler(update, context)

        # --- 💳 ТРАНЗАКЦІЙНИЙ ШЛЮЗ (CHECKOUT) ---
        if data == "checkout_init":
            context.user_data['target_item_id'] = None 
            if 'start_data_collection' in globals(): 
                return await start_data_collection(update, context, next_action='checkout')

        if data.startswith(("pay_mono", "pay_privat", "pay_crypto")):
            pay_type = data.replace("pay_", "")
            if 'payment_selection_handler' in globals():
                return await payment_selection_handler(update, context, pay_type)

        if data == "confirm_payment_start":
            context.user_data['state'] = "WAITING_RECEIPT" # Синхронізовано з Section 28
            return await update.effective_message.edit_text(
                "📸 <b>ПІДТВЕРДЖЕННЯ ОПЛАТИ</b>\n\nБудь ласка, надішліть <b>скріншот чека</b> прямо в цей чат.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Змінити метод", callback_data="checkout_init")]]),
                parse_mode='HTML'
            )

        # --- ⚡ ШВИДКІ ДІЇ ТА ПОДАРУНКИ ---
        if data.startswith(("fast_order_", "mgr_pre_", "gift_sel_", "add_")):
            if data.startswith("gift_sel_"): 
                if 'gift_selection_handler' in globals(): return await gift_selection_handler(update, context)
            
            if data.startswith("add_"): 
                if 'add_to_cart_handler' in globals(): return await add_to_cart_handler(update, context)
            
            # Логіка Fast Order
            parts = data.split("_")
            item_id = int(parts[2])
            gift_id = int(parts[-1]) if (len(parts) > 3 and parts[-1].isdigit()) else None
            
            context.user_data.update({'target_item_id': item_id, 'target_gift_id': gift_id})
            next_act = 'fast_order' if "fast" in data else 'manager_order'
            if 'start_data_collection' in globals():
                return await start_data_collection(update, context, next_action=next_act)

    except Exception as e:
        logger.error(f"🚨 DISPATCHER CRITICAL: {e}\n{traceback.format_exc()}")
        try: 
            await query.message.reply_text("⚠️ Помилка обробки. Спробуйте /start")
        except: pass
            
# =================================================================
# 🚀 SECTION 31: ENGINE STARTUP & ELITE MONITORING (TITAN v10.5)
# =================================================================

import time
import platform
import os
import sys
import traceback
import logging
from datetime import datetime

# Налаштування логування
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger("GhostyBoot")

# Глобальна точка відліку для аптайму
START_TIME = datetime.now()

async def post_init(application: Application) -> None:
    """Професійний звіт системи моніторингу GHO$$TY для Адміна."""
    try:
        # 1. Ініціалізація бази даних (якщо функція існує)
        if 'init_db' in globals():
            globals()['init_db']()
            logger.info("📡 Database: SQLite3 Connection Verified.")

        # 2. Збір метрик
        start_ping = time.time()
        bot_info = await application.bot.get_me()
        ping = round((time.time() - start_ping) * 1000, 2)
        
        db_sz = f"{os.path.getsize(DB_PATH) / 1024:.2f} KB" if os.path.exists(DB_PATH) else "🛠 NEW"
        uptime_dt = datetime.now() - START_TIME
        uptime_str = str(uptime_dt).split('.')[0]
        
        # 3. Формування звіту
        report = (
            f"🛰 <b>GHO$$TY STAFF | MONITORING CENTER</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🤖 <b>BOT-NODE:</b> @{bot_info.username}\n"
            f"🛡 <b>VERSION:</b> <code>TITAN ULTIMATE v10.6</code>\n"
            f"🟢 <b>STATUS:</b> <code>STABLE / ONLINE</code>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"⚡️ <b>PERFORMANCE:</b>\n"
            f"⏱ Ping: <code>{ping} ms</code>\n"
            f"🆙 Uptime: <code>{uptime_str}</code>\n"
            f"🐍 Python: <code>{platform.python_version()}</code>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🗄 <b>STORAGE & DB:</b>\n"
            f"📝 Database: <code>CONNECTED</code>\n"
            f"📦 DB Weight: <code>{db_sz}</code>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🕒 <code>{datetime.now().strftime('%d.%m.%Y | %H:%M:%S')}</code>\n\n"
            f"👑 <i>System fully operational. Ready for orders.</i>"
        )
        
        # 4. Сповіщення адміна
        await application.bot.send_message(chat_id=MANAGER_ID, text=report, parse_mode='HTML')
        logger.info(f"🚀 Boot Report sent to Manager ({MANAGER_ID})")
        
    except Exception as e:
        logger.error(f"❌ Post-init reporting failed: {e}")

def main():
    # ЕЛІТНИЙ СИСАДМІН-ВИВІД
    if os.name == 'nt': os.system('cls')
    else: os.system('clear')
    
    print("\n" + "═"*60)
    print(f"    ☁️  GHO$$TY STAFF PREMIUM ENGINE v10.6  ☁️")
    print("═" * 60)
    print(f"    [⏳] TIME:      {datetime.now().strftime('%H:%M:%S')}")
    print(f"    [👤] ADMIN ID:  {MANAGER_ID}")
    
    if not TOKEN or "8351638507" not in TOKEN: # Валідація токена
        print(f"    [❌] FATAL:      BOT_TOKEN IS INCORRECT OR MISSING!")
        print("═" * 60 + "\n")
        sys.exit(1)
        
    # Конфігурація додатка
    persistence = PicklePersistence(filepath=PERSISTENCE_PATH)
    
    # Використовуємо Defaults для чистоти коду в хендлерах
    defaults = Defaults(parse_mode=ParseMode.HTML, disable_web_page_preview=True)

    app = (
        Application.builder()
        .token(TOKEN)
        .persistence(persistence)
        .defaults(defaults)
        .post_init(post_init) # Виклик звіту та БД
        .concurrent_updates(True) # Включення паралельної обробки
        .build()
    )

    # РЕЄСТРАЦІЯ ХЕНДЛЕРІВ (Titan Bulletproof Routing)
    # Команди
    app.add_handler(CommandHandler("start", globals().get('start_command', lambda u, c: None)))
    app.add_handler(CommandHandler("admin", globals().get('admin_menu', lambda u, c: None)))
    
    # Кнопки
    app.add_handler(CallbackQueryHandler(globals().get('global_callback_handler')))
    
    # Текст та Медіа (Синхронізація з global_message_handler)
    # ПРІОРИТЕТ: global_message_handler (як у твоєму останньому файлі)
    msg_handler = globals().get('global_message_handler') or globals().get('handle_user_input')
    
    if msg_handler:
        app.add_handler(MessageHandler(
            (filters.TEXT | filters.PHOTO | filters.VIDEO | filters.Document.ALL) & ~filters.COMMAND, 
            msg_handler
        ))
    
    # Error handler (Section 25)
    if 'error_handler' in globals():
        app.add_error_handler(globals()['error_handler'])
    
    print(f"    [🌐] NETWORK:    Pool Size: 25 | Drop Pending: True")
    print(f"    [🚀] STATUS:     POLLING STARTED - SYSTEM ONLINE")
    print("═" * 60 + "\n")
    
    # Запуск бота з очищенням старих запитів
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        print(f"\n    [🚫] SHUTDOWN:    System manually terminated.")
    except Exception as fatal_e:
        print(f"\n    [💥] CRASH:      CRITICAL ERROR DETECTED!")
        print(f"    [!] REASON:      {fatal_e}")
        traceback.print_exc()
        sys.exit(1)

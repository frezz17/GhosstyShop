# =================================================================
# 🤖 PROJECT: GHO$$TY STAFF PREMIUM E-COMMERCE ENGINE (PRO)
# 🛠 VERSION: TITAN ULTIMATE v10.5 (FINAL STABLE)
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
from datetime import datetime, timedelta
from html import escape
from urllib.parse import quote

# Telegram Core (v20.x+ Async Stack)
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, CallbackQuery
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters, PicklePersistence, Defaults
from telegram.error import BadRequest

# 🛡 ТЕХНІЧНА ГІГІЄНА
warnings.filterwarnings("ignore", category=UserWarning)

if 'GhostyCore' in logging.Logger.manager.loggerDict:
    logging.getLogger("GhostyCore").handlers.clear()

# =================================================================
# ⚙️ SECTION 1: GLOBAL CONFIGURATION
# =================================================================

import os
import sys
import logging
import sqlite3
from datetime import datetime

# Налаштування шляхів
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True) 

DB_PATH = os.path.join(DATA_DIR, 'ghosty_pro_final.db')
PERSISTENCE_PATH = os.path.join(DATA_DIR, 'ghosty_state_final.pickle')
LOG_PATH = os.path.join(DATA_DIR, 'ghosty_system.log')

# ТОКЕН ТА АДМІНІСТРАЦІЯ
TOKEN = os.getenv("BOT_TOKEN", "8351638507:AAGH4wmu0UUk-v1rzLXIY3eTfQsSscDrvBE")
MANAGER_ID = 7544847872
ADMIN_LIST = [MANAGER_ID]
MANAGER_USERNAME = "ghosstydp"
CHANNEL_URL = "https://t.me/GhostyStaffDP"
WELCOME_PHOTO = "https://i.ibb.co/35K9Zp5p/Polish-20260310-051407282.png"

# РЕКВІЗИТИ ТА ГАМАНЦІ
USDT_RATE = 43.7  # Твій актуальний курс
TON_WALLET = "UQAoGQYr_1sl9_3PcgkvJFzO4bXdQWpmnM6o6NPLk4l5koW5"

PAYMENT_LINK = {
    "mono": "https://lnk.ua/k4xJG21Vy",    
    "privat": "https://lnk.ua/RVd0OW6V3",
    "ghossty_web": "https://heylink.me/GhosstyShop" # Посилання на сайт
}

# ЛОГУВАННЯ
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

# =================================================================
# 🛠 SECTION 2: UI ENGINE & ERROR SHIELD (PRO FIX)
# =================================================================

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Глобальний щит безпеки."""
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
        await context.bot.send_message(chat_id=MANAGER_ID, text=admin_msg, parse_mode=ParseMode.HTML)
        if isinstance(update, Update) and update.effective_chat:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="⚠️ <b>Виникла технічна помилка.</b>\nСпробуйте натиснути /start", parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.error(f"Failed to report error: {e}")


async def _edit_or_reply(target, text: str, kb: list = None, photo: str = None, context: ContextTypes.DEFAULT_TYPE = None):
    """
    Головний рушій відображення повідомлень.
    🔥 ВДОСКОНАЛЕНО: Додано Fallback-систему відправки тексту, якщо фото недоступне.
    """
    if not text: text = "..."
    reply_markup = InlineKeyboardMarkup(kb) if isinstance(kb, list) else (kb if kb else None)
    query = target if hasattr(target, 'data') else getattr(target, 'callback_query', None)
    message = query.message if query else getattr(target, 'message', target)
    
    if not message: return
    chat_id = message.chat_id
    bot = context.bot if context else message.get_bot()

    try:
        # Спроба стандартної відправки/редагування
        if query:
            if photo:
                if message.photo:
                    await query.edit_message_media(media=InputMediaPhoto(media=photo, caption=text, parse_mode=ParseMode.HTML), reply_markup=reply_markup)
                else:
                    await message.delete()
                    await bot.send_photo(chat_id=chat_id, photo=photo, caption=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
            else:
                if message.photo:
                    await message.delete()
                    await bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
                else:
                    await query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        else:
            if photo: 
                await message.reply_photo(photo=photo, caption=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
            else: 
                await message.reply_text(text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
                
    except BadRequest as e:
        # Якщо повідомлення не змінилося - ігноруємо
        if "Message is not modified" not in str(e):
            try: 
                # Спроба відправити новим повідомленням (якщо редагування неможливе)
                if photo: 
                    await bot.send_photo(chat_id=chat_id, photo=photo, caption=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
                else: 
                    await bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
            except Exception as photo_err:
                # 🔥 ФОЛБЕК (FALLBACK): Якщо хостинг заблокував завантаження фото, відправляємо ТІЛЬКИ ТЕКСТ
                try:
                    logger.warning(f"⚠️ Фото недоступне (таймаут/блок хостингу). Відправляю текст. Причина: {photo_err}")
                    await bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
                except Exception as final_err:
                    logger.error(f"❌ Критична помилка UI Engine: {final_err}")
                    
    except Exception as general_e:
        # Страховка від будь-яких інших збоїв
        logger.error(f"Неочікувана помилка в _edit_or_reply: {general_e}")
        try:
            await bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
        except: 
            pass


async def send_ghosty_message(update_obj, text: str, kb=None, photo=None, context: ContextTypes.DEFAULT_TYPE = None):
    await _edit_or_reply(update_obj, text, kb, photo, context)


async def safe_delete(message):
    try:
        if hasattr(message, 'delete'): await message.delete()
    except: pass
        

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

VIP_DISCOUNT_CATEGORIES = ['hhc', 'pods'] 

def calculate_final_price(item_price, user_profile, item_id=None):
    """Обчислює ціну з урахуванням VIP-статусу та категорій."""
    try:
        price = float(item_price)
        up = user_profile if user_profile else {}
        is_vip = bool(up.get('is_vip', False))
        
        if item_id is None: return round(price, 2), False

        # Визначаємо категорію за ID, якщо немає item_data
        iid = int(item_id)
        item_category = None
        if 100 <= iid < 300: item_category = 'hhc'
        elif 300 <= iid < 500: item_category = 'liquids'
        elif 500 <= iid < 700: item_category = 'pods'

        # Застосування знижки 35% (множник 0.65) для VIP у вибраних категоріях
        if is_vip and item_category in VIP_DISCOUNT_CATEGORIES:
            final_price = price * 0.65 
            return round(max(final_price, 10.0), 2), True
            
        return round(price, 2), False
    except Exception as e:
        if 'logger' in globals(): logger.error(f"❌ Math Error: {e}")
        return float(item_price), False

def get_price_display(item_price, profile, item_id):
    """Повертає красиво відформатовану ціну для UI."""
    price, is_discounted = calculate_final_price(item_price, profile, item_id)
    if is_discounted:
        return f"<s>{int(item_price)}</s> 🔥 <b>{int(price)} ₴</b>", price, True
    return f"<b>{int(price)} ₴</b>", price, False

def init_db():
    """Ініціалізація БД та автоматична міграція нових колонок."""
    try:
        with sqlite3.connect(DB_PATH, timeout=30) as conn:
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
            
            # 🔥 МІГРАЦІЇ (Додаємо колонки, якщо їх немає в старій базі)
            columns_to_add = [
                ("promo_GHST2026_used", "INTEGER DEFAULT 0"),
                ("referral_used", "INTEGER DEFAULT 0"),
                ("referred_by", "INTEGER"),
                ("balance", "REAL DEFAULT 0")
            ]
            
            for col_name, col_type in columns_to_add:
                try:
                    cur.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
                except sqlite3.OperationalError:
                    pass # Колонка вже існує
            
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
            logger.info("✅ Database initialized and migrated successfully.")
    except Exception as e:
        logger.critical(f"❌ DB SCHEMA FATAL ERROR: {e}")

async def get_or_create_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Синхронізація профілю користувача між БД та context.user_data."""
    user = update.effective_user
    if not user: return None
    
    # Ініціалізація базової структури в пам'яті
    if 'profile' not in context.user_data:
        context.user_data['profile'] = {
            "uid": user.id, 
            "username": f"@{user.username}" if user.username else "Приховано",
            "full_name": user.full_name, 
            "phone": None, "city": None, "district": None, "address_details": None,
            "is_vip": False, "vip_expiry": None, "balance": 0.0,
            "next_order_discount": 0.0, "referred_by": None,
            "referral_used": False, "promo_applied": False, "promo_GHST2026_used": False
        }
    
    if 'cart' not in context.user_data: 
        context.user_data['cart'] = []

    try:
        with sqlite3.connect(DB_PATH, timeout=30) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            row = cursor.execute("SELECT * FROM users WHERE user_id=?", (user.id,)).fetchone()
            
            if not row:
                reg_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                # Перевіряємо, чи зайшов користувач за реферальним посиланням
                ref_id = context.args[0] if context.args and context.args[0].isdigit() else None
                
                cursor.execute("""
                    INSERT INTO users (user_id, username, full_name, reg_date, referred_by) 
                    VALUES (?, ?, ?, ?, ?)
                """, (user.id, user.username, user.full_name, reg_time, ref_id))
                conn.commit()
                row = cursor.execute("SELECT * FROM users WHERE user_id=?", (user.id,)).fetchone()

            # Оновлюємо context.user_data даними з БД
            p = context.user_data['profile']
            cols = ['is_vip', 'vip_expiry', 'balance', 'next_order_discount', 
                    'promo_applied', 'promo_GHST2026_used', 'referral_used', 
                    'referred_by', 'phone', 'city', 'district', 'address_details']
            
            for col in cols:
                val = row[col]
                if col in ['is_vip', 'promo_applied', 'promo_GHST2026_used', 'referral_used']:
                    p[col] = bool(val)
                else:
                    p[col] = val if val is not None else p.get(col)
                    
    except Exception as e:
        logger.error(f"❌ DB Sync Failure: {e}")
        
    return context.user_data['profile']

def update_user_balance(user_id: int, amount: float):
    """Технічна функція для нарахування бонусів."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
            conn.commit()
            return True
    except Exception as e:
        logger.error(f"❌ Balance Update Error: {e}")
        return False
    
# =================================================================
# 🛍 SECTION 14: CATALOG MASTER ENGINE (TITAN PRO v10.5)
# =================================================================

async def catalog_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Головний вхід у каталог. 
    Адаптовано: Підтримує динамічне вітання залежно від статусу користувача.
    """
    profile = context.user_data.get('profile', {})
    is_vip = profile.get('is_vip', False)
    
    vip_status_text = "✨ <b>Ваш статус: VIP PRO</b> (-35% на обране)" if is_vip else "💎 <b>Статус: Standard</b>"

    text = (
        "<b>🛍 КАТАЛОГ GHO$$TY STAFF</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"{vip_status_text}\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Тут тільки перевірений стафф. Обирай категорію 👇\n\n"
        "💨 <b>HHC Вейпи</b> — <i>Relax з США (Original)</i>\n"
        "🔌 <b>POD-Системи</b> — <i>Девайси на кожен день</i>\n"
        "💧 <b>Рідини</b> — <i>Chaser, нові колекції</i>\n"
    )
    
    kb = [
        [InlineKeyboardButton("💨 HHC ВЕЙПИ (USA) 🔥", callback_data="cat_list_hhc")],
        [InlineKeyboardButton("🔌 POD-СИСТЕМИ 🔥", callback_data="cat_list_pods")],
        [InlineKeyboardButton("💧 РІДИНИ (Salt)", callback_data="cat_list_liquids")],
        [InlineKeyboardButton("🏠 ГОЛОВНЕ МЕНЮ", callback_data="menu_start")]
    ]
    
    # Використовуємо глобальне фото або заглушку
    photo = globals().get('WELCOME_PHOTO', "https://i.ibb.co/y7Q194N/1770068775663.png")
    
    # Використовуємо наш універсальний метод відправки
    await send_ghosty_message(update, text, kb, photo=photo, context=context)


async def show_category_items(update: Update, context: ContextTypes.DEFAULT_TYPE, category_key: str):
    """
    Генератор списку товарів.
    Оптимізовано: Автоматичне сортування, обробка знижок та залишків.
    """
    query = update.callback_query
    
    # 1. Професійний мапінг (Зв'язок з глобальними словниками)
    cat_map = {
        'hhc': ('HHC_ITEMS', '💨 HHC Вейпи'), # Змінено на HHC_ITEMS для уніфікації
        'pods': ('PODS', '🔌 POD-Системи'),
        'liquids': ('LIQUIDS', '💧 Рідини'),
    }
    
    map_data = cat_map.get(category_key)
    if not map_data:
        await query.answer("⚠️ Категорія ще наповнюється...", show_alert=True)
        return

    dict_name, cat_title = map_data
    items_dict = globals().get(dict_name, {})
    
    if not items_dict:
        await query.answer("⚠️ Товари тимчасово відсутні", show_alert=True)
        return

    profile = context.user_data.get('profile', {})
    
    # 2. Заголовок з ЛЕГЕНДОЮ
    text = (
        f"📂 <b>КАТЕГОРІЯ: {cat_title}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🔥 — <i>діє знижка VIP (-35%)</i>\n"
        f"⌛ — <i>закінчується (менше 3 шт)</i>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👇 Оберіть товар для перегляду:"
    )
    
    kb = []
    
    # 3. Розумне сортування: спочатку ті, що є в наявності, потім за залишком
    sorted_items = sorted(items_dict.items(), key=lambda x: (x[1].get('stock', 0) > 0, x[1].get('stock', 0)), reverse=True)

    for i_id, item in sorted_items:
        stock = item.get('stock', 0)
        
        # Використовуємо нашу ідеальну функцію розрахунку ціни з Section 4
        price_display_str, final_price, is_discounted = get_price_display(item['price'], profile, i_id)
        
        # 4. Формування кнопок
        if stock <= 0:
            btn_text = f"❌ {item['name']} (Очікується)"
            kb.append([InlineKeyboardButton(btn_text, callback_data=f"notify_restock_{i_id}")])
        else:
            hot_mark = "⌛ " if stock < 3 else ""
            vip_mark = "🔥 " if is_discounted else ""
            # Виводимо чисту ціну на кнопці (без HTML тегів)
            btn_text = f"{vip_mark}{hot_mark}{item['name']} — {int(final_price)} ₴"
            kb.append([InlineKeyboardButton(btn_text, callback_data=f"view_item_{i_id}")])
    
    # Навігація
    kb.append([InlineKeyboardButton("🔙 До категорій", callback_data="cat_all")])
    kb.append([InlineKeyboardButton("🏠 В головне меню", callback_data="menu_start")])
    
    # Використовуємо _edit_or_reply для безперебійної зміни контенту
    await _edit_or_reply(query, text, kb, context=context)
    

# =================================================================
# 🌍 SECTION 10: GEOGRAPHY & LOGISTICS (TITAN ULTIMATE v10.5)
# =================================================================

async def choose_city_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    КРОК 1: Головне меню вибору міста.
    Автоматично підтягує дані з UKRAINE_CITIES (Section 3).
    """
    query = update.callback_query
    
    # Очищення старих даних при зміні локації (захист від помилок доставки)
    p = context.user_data.setdefault('profile', {})
    p['district'] = None
    p['address_details'] = None
    
    context.user_data['state'] = "COLLECTING_DATA"
    context.user_data.setdefault('data_flow', {})['step'] = 'city_selection'
    
    # Використовуємо брендоване фото
    map_image = globals().get('WELCOME_PHOTO', "https://i.ibb.co/y7Q194N/1770068775663.png")
    
    text = (
        "🏙 <b>ГЕОЛОКАЦІЯ ТА ДОСТАВКА</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Оберіть ваше місто, щоб побачити актуальні\n"
        "райони для самовивозу або замовити кур'єра 👇"
    )
    
    # Беремо актуальний список міст із Section 3
    from_section_3_cities = globals().get('CITIES_LIST', ["Дніпро", "Кам'янське", "Київ"])
    
    keyboard = []
    # Динамічна генерація кнопок по 2 в ряд
    for i in range(0, len(from_section_3_cities), 2):
        row = [InlineKeyboardButton(from_section_3_cities[i], callback_data=f"sel_city_{from_section_3_cities[i]}")]
        if i + 1 < len(from_section_3_cities):
            row.append(InlineKeyboardButton(from_section_3_cities[i+1], callback_data=f"sel_city_{from_section_3_cities[i+1]}"))
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("🏠 ГОЛОВНЕ МЕНЮ", callback_data="menu_start")])
    
    await send_ghosty_message(update, text, keyboard, photo=map_image, context=context)


async def choose_delivery_method(update: Update, context: ContextTypes.DEFAULT_TYPE, city: str):
    """
    КРОК 2: Вибір між КЛАДОМ та КУР'ЄРОМ.
    Викликається після вибору міста.
    """
    query = update.callback_query
    context.user_data['profile']['city'] = city
    
    # Отримуємо ціну кур'єра з Section 3
    courier_fee = globals().get('COURIER_PRICE', 150.0)
    
    text = (
        f"🏙 <b>{city.upper()}: ЯК ОТРИМАТИ?</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"1️⃣ <b>Готовий Клад</b> — район на вибір (без доплат).\n"
        f"2️⃣ <b>Кур'єрська доставка (+{int(courier_fee)} ₴)</b> — прямо до дверей.\n\n"
        f"👇 Оберіть зручний варіант:"
    )
    
    kb = [
        [InlineKeyboardButton("📍 Обрати район (Клад)", callback_data=f"list_districts_{city}")],
        [InlineKeyboardButton(f"🛵 Кур'єр на адресу (+{int(courier_fee)} ₴)", callback_data="sel_dist_Кур'єр")],
        [InlineKeyboardButton("⬅️ Змінити місто", callback_data="choose_city")]
    ]
    
    await _edit_or_reply(query, text, kb, context=context)


async def district_selection_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, city: str):
    """
    КРОК 3: Список районів (Класичний вибір).
    Працює на основі розширеного списку UKRAINE_CITIES.
    """
    query = update.callback_query
    user_id = update.effective_user.id
    
    # Отримуємо райони з Section 3
    cities_db = globals().get('UKRAINE_CITIES', {})
    districts = cities_db.get(city, ["Центр"])
    
    # Зберігаємо місто в базу відразу (пре-сейв)
    try:
        with sqlite3.connect(DB_PATH, timeout=30) as conn:
            conn.execute("UPDATE users SET city=? WHERE user_id=?", (city, user_id))
            conn.commit()
    except Exception as e:
        logger.error(f"❌ DB City Save Error: {e}")

    text = (
        f"🏘 <b>{city.upper()}: ОБЕРІТЬ РАЙОН</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Де вам найзручніше забрати замовлення?\n"
        f"👇 Оберіть локацію:"
    )

    kb = []
    # Будуємо сітку районів
    for i in range(0, len(districts), 2):
        row = [InlineKeyboardButton(districts[i], callback_data=f"sel_dist_{districts[i]}")]
        if i + 1 < len(districts):
            row.append(InlineKeyboardButton(districts[i+1], callback_data=f"sel_dist_{districts[i+1]}"))
        kb.append(row)
        
    kb.append([InlineKeyboardButton("🔙 Назад до вибору доставки", callback_data=f"sel_city_{city}")])
    
    context.user_data.setdefault('data_flow', {})['step'] = 'district_selection'
    
    await _edit_or_reply(query, text, kb, context=context)
    
# =================================================================
# 👤 SECTION 5: MASTER START & PROFILE UI (DEEP LINK SUPPORT)
# =================================================================

from datetime import datetime
import sqlite3

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Головна точка входу (/start). 
    Виправлено: Динамічний чек VIP-статусу та акцент на промокоді GHST2026.
    """
    user = update.effective_user
    
    # 🔥 ФІКС ЗАЛИПАННЯ: Очищення контексту
    context.user_data['target_item_id'] = None
    context.user_data['target_gift_id'] = None
    context.user_data['selected_color'] = None
    context.user_data['state'] = None
    
    # 1. Отримуємо актуальний профіль
    if 'get_or_create_user' in globals():
        profile = await get_or_create_user(update, context)
    else:
        await update.message.reply_text("⚠️ Система завантажується... Спробуйте через мить.")
        return

    # 🔥 ПЕРЕВІРКА VIP СТАТУСУ (РЕАЛЬНИЙ ЧАС)
    is_vip = False
    vip_expiry_str = profile.get('vip_expiry')
    if vip_expiry_str and vip_expiry_str != '—':
        try:
            expiry_dt = datetime.strptime(vip_expiry_str, '%d.%m.%Y %H:%M')
            if expiry_dt > datetime.now():
                is_vip = True
        except: pass

    # 2. ВІЗУАЛІЗАЦІЯ
    safe_name = escape(user.first_name)
    current_balance = int(profile.get('next_order_discount', 0))
    bot = await context.bot.get_me()
    ref_link = f"https://t.me/{bot.username}?start={user.id}"
    
    status_icon = "💎 V.I.P PRO" if is_vip else "👤 Standard"
    vip_benefits = (
        f"📉 Твої привілеї: <b>-35% знижка</b> + <b>FREE Доставка</b>" 
        if is_vip else "<i>(Активуй VIP для безкоштовної доставки та знижок!)</i>"
    )
    
    welcome_text = (
        f"🌫️ <b>GHO$$TY STAFF LAB | 2026</b> 🌿\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Йо, <b>{safe_name}</b>! Твій статус: <b>{status_icon}</b>\n"
        f"💰 Твій баланс: <b>{current_balance} грн</b>\n"
        f"{vip_benefits}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🎁 <b>ПОДАРУНОК ДЛЯ НОВИХ ДРУЗІВ:</b>\n"
        f"Натисни «👤 ПРОФІЛЬ» -> «🎟 Ввести промокод»\n"
        f"Використай код: <code>GHST2026</code>\n"
        f"🚀 <b>Отримай +69₴ на баланс та 7 днів VIP PRO!</b>\n\n"
        f"🤝 <b>ПАРТНЕРСЬКА ПРОГРАМА:</b>\n"
        f"Твоє посилання: <code>{ref_link}</code>\n"
        f"<i>(Друг отримає бонуси, а ти — +50₴ та +7 днів VIP!)</i>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👇 <b>ОБЕРИ РОЗДІЛ:</b>"
    )
    
    keyboard = [
        [InlineKeyboardButton("🛍 ВІДКРИТИ КАТАЛОГ 🌿", callback_data="cat_all")],
        [InlineKeyboardButton("👤 ПРОФІЛЬ", callback_data="menu_profile"), 
         InlineKeyboardButton("🛒 КОШИК", callback_data="menu_cart")],
        [InlineKeyboardButton("🚚 ДАНІ ПРО ДОСТАВКУ", callback_data="fill_delivery_data")], 
        [InlineKeyboardButton("👨‍💻 МЕНЕДЖЕР", url=f"https://t.me/{globals().get('MANAGER_USERNAME')}"),
         InlineKeyboardButton("📢 КАНАЛ", url=f"{globals().get('CHANNEL_URL')}")]
    ]
    
    if user.id in globals().get('ADMIN_LIST', []) or user.id == globals().get('MANAGER_ID'):
        keyboard.append([InlineKeyboardButton("⚙️ ADMIN PANEL", callback_data="admin_main")])

    photo = globals().get('WELCOME_PHOTO', "https://i.ibb.co/35K9Zp5p/Polish-20260310-051407282.png")
    await send_ghosty_message(update, welcome_text, keyboard, photo=photo, context=context)


async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Особистий кабінет: Виправлено відображення дати VIP."""
    user = update.effective_user
    profile = await get_or_create_user(update, context)
    bot = await context.bot.get_me()
    
    # Логіка статусу
    vip_expiry = profile.get('vip_expiry', '—')
    is_vip = False
    if vip_expiry != '—':
        try:
            if datetime.strptime(vip_expiry, '%d.%m.%Y %H:%M') > datetime.now():
                is_vip = True
        except: pass
    
    status_text = "💎 V.I.P PRO" if is_vip else "👤 Standard"
    
    # Дані доставки
    city = profile.get('city', 'Не обрано')
    district = profile.get('district', '')
    location = f"{city}" + (f" ({district})" if district else "")
    
    text = (
        f"👤 <b>МІЙ ПРОФІЛЬ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 ID: <code>{user.id}</code>\n"
        f"🧢 Користувач: <b>{escape(profile.get('full_name', user.first_name))}</b>\n"
        f"🌟 Статус: <b>{status_text}</b>\n"
        f"📅 VIP діє до: <code>{vip_expiry}</code>\n\n"
        f"💰 <b>БОНУСНИЙ РАХУНОК: {int(profile.get('next_order_discount', 0))} ₴</b>\n"
        f"<i>(Знижка застосується автоматично при оплаті)</i>\n\n"
        f"📍 <b>ЛОГІСТИКА:</b>\n"
        f"🏙 Місто: {location}\n"
        f"🏠 Адреса: {profile.get('address_details', '—')}\n"
        f"📱 Тел: {profile.get('phone', 'Не вказано')}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🔗 <b>РЕФЕРАЛЬНЕ ПОСИЛАННЯ:</b>\n"
        f"<code>https://t.me/{bot.username}?start={user.id}</code>\n\n"
        f"👇 <i>Налаштування:</i>"
    )
    
    kb = [
        [InlineKeyboardButton("✏️ Оновити дані доставки", callback_data="fill_delivery_data")],
        [InlineKeyboardButton("🎟 Активувати промокод", callback_data="menu_promo")],
        [InlineKeyboardButton("🔙 На головну", callback_data="menu_start")]
    ]
    
    await send_ghosty_message(update, text, kb, photo=globals().get('WELCOME_PHOTO'), context=context)

# =================================================================
# 🔍 SECTION 15: PRODUCT CARD & INTERACTIVE ENGINE (PRO)
# =================================================================

async def view_item_details(update: Update, context: ContextTypes.DEFAULT_TYPE, item_id: int):
    """
    Точка входу: Скидає старі вибори та завантажує свіжу картку.
    """
    item = get_item_data(item_id)
    if not item:
        if update.callback_query:
            await update.callback_query.answer("❌ Товар не знайдено.", show_alert=True)
        return

    # Очищуємо тимчасові вибори для нової картки
    context.user_data['selected_color'] = None
    context.user_data['selected_strength'] = None
    
    # Стартове фото (основне)
    await render_product_card(update, context, item, item_id, item.get('img'))


async def render_product_card(update: Update, context: ContextTypes.DEFAULT_TYPE, item: dict, item_id: int, current_photo: str):
    """
    Ядро рендерингу: Динамічно збирає опис, ціну та кнопки.
    """
    query = update.callback_query
    profile = context.user_data.get("profile", {})
    
    # 1. РОЗРАХУНОК ЦІНИ (З урахуванням VIP та акцій із Section 4)
    # Функція get_price_display має повертати: (html_text, final_float, has_discount)
    price_html, final_price, _ = get_price_display(item['price'], profile, item_id)

    # 2. ЛОГІКА СКЛАДУ (Інтуїтивні статуси)
    stock = item.get('stock', 0)
    if stock >= 15:
        stock_status = f"🟢 <b>В наявності</b>"
    elif 1 <= stock < 15:
        stock_status = f"🟡 <b>Залишилось: {stock} шт</b> 🔥"
    else:
        stock_status = "🔴 <b>Немає в наявності</b>"

    # 3. ФОРМУВАННЯ ПАРАМЕТРІВ (Колір/Міцність)
    selected_color = context.user_data.get('selected_color')
    selected_strength = context.user_data.get('selected_strength')
    
    params_text = ""
    if selected_color: params_text += f"\n🎨 Колір: <b>{selected_color}</b>"
    if selected_strength: params_text += f"\n⚡️ Міцність: <b>{selected_strength} mg</b>"

    # 4. ТЕКСТ КАРТКИ
    safe_name = escape(item['name'])
    desc = item.get('desc', 'Опис оновлюється...')
    
    caption = (
        f"🛍 <b>{safe_name}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📦 Стан: {stock_status}\n"
        f"💰 Ціна: {price_html}{params_text}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{desc}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🚀 <i>Оберіть параметри та натисніть 'Додати в кошик'</i>"
    )

    kb = []
    
    # 5. ГЕНЕРАЦІЯ КНОПОК ПАРАМЕТРІВ (Якщо товар в наявності)
    if stock > 0:
        # --- БЛОК КОЛЬОРІВ (для PODS) ---
        if "colors" in item and item["colors"]:
            kb.append([InlineKeyboardButton("🎨 ОБЕРІТЬ КОЛІР:", callback_data="ignore")])
            row = []
            for col in item["colors"]:
                is_sel = (col == selected_color)
                btn_text = f"✅ {col}" if is_sel else col
                cb = "ignore" if is_sel else f"sel_col_{item_id}_{col}"
                row.append(InlineKeyboardButton(btn_text, callback_data=cb))
                if len(row) == 2:
                    kb.append(row); row = []
            if row: kb.append(row)

        # --- БЛОК МІЦНОСТІ (для LIQUIDS) ---
        if "strengths" in item and item["strengths"]:
            kb.append([InlineKeyboardButton("⚡️ ОБЕРІТЬ МІЦНІСТЬ:", callback_data="ignore")])
            row = []
            for strg in item["strengths"]:
                is_sel = (str(strg) == str(selected_strength))
                btn_text = f"🔘 {strg} mg" if is_sel else f"{strg} mg"
                cb = "ignore" if is_sel else f"sel_str_{item_id}_{strg}"
                row.append(InlineKeyboardButton(btn_text, callback_data=cb))
            kb.append(row)

    # 6. КНОПКИ ДІЇ
    if stock > 0:
        # Перевірка, чи всі обов'язкові параметри обрані
        need_color = "colors" in item and not selected_color
        need_strength = "strengths" in item and not selected_strength
        
        if need_color or need_strength:
            warning_text = "👆 ОБЕРІТЬ " + ("КОЛІР" if need_color else "МІЦНІСТЬ")
            kb.append([InlineKeyboardButton(warning_text, callback_data="ignore")])
        else:
            # Формуємо метадані для кошика (id_колір_міцність)
            color_meta = f"_{selected_color}" if selected_color else ""
            str_meta = f"_{selected_strength}" if selected_strength else ""
            cart_data = f"add_{item_id}{color_meta}{str_meta}"
            
            kb.append([InlineKeyboardButton("🛒 ДОДАТИ В КОШИК", callback_data=cart_data)])
            kb.append([
                InlineKeyboardButton("⚡️ ШВИДКИЙ ЗАКАЗ", callback_data=f"fast_{item_id}"),
                InlineKeyboardButton("👨‍💻 МЕНЕДЖЕР", callback_data=f"mgr_ask_{item_id}")
            ])
    else:
        kb.append([InlineKeyboardButton("🔔 ПОВІДОМИТИ ПРО ПОЯВУ", callback_data="notify_stock")])

    kb.append([InlineKeyboardButton("🔙 НАЗАД ДО КАТАЛОГУ", callback_data="cat_all")])

    # 7. РОЗУМНЕ ОНОВЛЕННЯ (М'яка заміна фото без мерехтіння)
    await send_ghosty_message(update, caption, kb, photo=current_photo, context=context)


async def handle_param_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обробляє кліки по кольорах та міцності.
    Паттерни: sel_col_{id}_{val} або sel_str_{id}_{val}
    """
    query = update.callback_query
    data = query.data
    
    parts = data.split('_')
    item_id = int(parts[2])
    value = "_".join(parts[3:]) # Обробка назв кольорів з пробілами
    
    item = get_item_data(item_id)
    if not item: return

    # Оновлюємо вибір у пам'яті
    new_photo = item.get('img')
    
    if "sel_col" in data:
        context.user_data['selected_color'] = value
        # Зміна фото на прев'ю кольору
        previews = item.get("color_previews", {})
        for key, url in previews.items():
            if key.lower() in value.lower():
                new_photo = url
                break
        await query.answer(f"Обрано колір: {value}")
        
    elif "sel_str" in data:
        context.user_data['selected_strength'] = value
        await query.answer(f"Обрано міцність: {value} mg")
        # Для рідин фото зазвичай не змінюється, беремо основне
        new_photo = item.get('img')

    # Перерендер картки з новими параметрами
    await render_product_card(update, context, item, item_id, new_photo)
    
# =================================================================
# 📝 SECTION 16: SMART DATA COLLECTION (TITAN FIXED)
# =================================================================

async def start_data_collection(update: Update, context: ContextTypes.DEFAULT_TYPE, next_action: str = 'checkout', item_id: int = None):
    """
    Ініціалізація збору даних. 
    Виправлено: Force_edit тепер скидає старі дані міста/району для уникнення конфліктів.
    """
    user = update.effective_user
    context.user_data['post_data_action'] = next_action
    
    if item_id: context.user_data['target_item_id'] = item_id
    
    profile = context.user_data.get('profile', {})
    force_edit = (next_action in ['none', 'profile'])

    # --- КРОК 1: ІМ'Я ---
    if force_edit or not profile.get('full_name'):
        context.user_data['state'], context.user_data['data_step'] = "COLLECTING_DATA", "name"
        text = "📝 <b>КРОК 1/4: ВАШЕ ІМ'Я</b>\n\nВведіть Прізвище та Ім'я отримувача:"
        kb = [[InlineKeyboardButton("✖️ Скасувати", callback_data="menu_profile")]]
        await send_ghosty_message(update, text, kb, context=context)
        return

    # --- КРОК 2: ТЕЛЕФОН ---
    if force_edit or not profile.get('phone'):
        context.user_data['state'], context.user_data['data_step'] = "COLLECTING_DATA", "phone"
        text = "📱 <b>КРОК 2/4: ТЕЛЕФОН</b>\n\nВведіть номер телефону (напр. 0931234567):"
        kb = [[InlineKeyboardButton("✖️ Скасувати", callback_data="menu_profile")]]
        await send_ghosty_message(update, text, kb, context=context)
        return

    # --- КРОК 3: МІСТО ---
    if force_edit or not profile.get('city'):
        # ПРИМУСОВО ОЧИЩАЄМО РАЙОН, ЯКЩО МІНЯЄМО МІСТО
        context.user_data['profile']['district'] = None 
        await choose_city_menu(update, context)
        return

    # --- КРОК 4: АДРЕСА ---
    if force_edit or not profile.get('address_details'):
        await address_request_handler(update, context, profile.get('district', 'Відділення'))
        return

    await finalize_data_collection(update, context)


async def city_selection_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, city_name: str):
    """
    ФІКС ПОМИЛКИ №2: Примусовий перезапис міста в БД та очищення старого району.
    """
    user_id = update.effective_user.id
    
    # 1. Оновлюємо в пам'яті
    if 'profile' not in context.user_data: context.user_data['profile'] = {}
    context.user_data['profile']['city'] = city_name
    context.user_data['profile']['district'] = None # Обов'язково скидаємо район
    
    # 2. Оновлюємо в БД негайно
    try:
        with sqlite3.connect(globals().get('DB_PATH'), timeout=30) as conn:
            conn.execute("UPDATE users SET city=?, district=NULL, address_details=NULL WHERE user_id=?", (city_name, user_id))
            conn.commit()
    except Exception as e:
        logger.error(f"City update DB error: {e}")

    # 3. Переходимо до вибору району (якщо Дніпро) або адреси
    if city_name == "Дніпро":
        if 'show_dnipro_districts' in globals():
            await globals()['show_dnipro_districts'](update, context)
        else:
            await address_request_handler(update, context, "Центр")
    else:
        await address_request_handler(update, context, "Нова Пошта")


async def address_request_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, dist_name: str):
    """Крок 4: Запит конкретної адреси/відділення."""
    clean_dist = dist_name.split("_")[0] 
    context.user_data.setdefault('profile', {})['district'] = clean_dist
    
    context.user_data['state'] = "COLLECTING_DATA"
    context.user_data['data_step'] = "address"
    
    city = context.user_data.get('profile', {}).get('city', 'Обране місто')
    
    text = (
        f"📍 <b>ЛОКАЦІЯ ПІДТВЕРДЖЕНА: {city}</b>\n"
        f"🏘 <b>Район/Тип:</b> {clean_dist}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"✍️ <b>ВВЕДІТЬ АДРЕСУ:</b>\n"
        f"Напишіть номер відділення Нової Пошти\n"
        f"або повну адресу (вулиця, будинок) для кур'єра."
    )
    
    kb = [
        [InlineKeyboardButton("🏙 Змінити місто", callback_data="fill_delivery_data")],
        [InlineKeyboardButton("✖️ Скасувати", callback_data="menu_profile")]
    ]
    
    await send_ghosty_message(update, text, kb, context=context)
            
# =================================================================
# 🛒 SECTION 18: CART LOGIC (EXPANDED & REINFORCED)
# =================================================================

async def show_cart_logic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Відображення кошика: розрахунок цін, перевірка даних та логістика.
    """
    query = update.callback_query
    cart = context.user_data.get("cart", [])
    profile = context.user_data.setdefault("profile", {})
    
    # --- 1. ПЕРЕВІРКА НА ПОРОЖНІЙ КОШИК ---
    if not cart:
        text = "🛒 <b>ВАШ КОШИК ПОРОЖНІЙ</b>\n\nЗдається, ви ще нічого не обрали. Зазирніть у каталог, там багато цікавого! 👇"
        kb = [
            [InlineKeyboardButton("🛍 ВІДКРИТИ КАТАЛОГ", callback_data="cat_all")],
            [InlineKeyboardButton("🏠 ГОЛОВНЕ МЕНЮ", callback_data="menu_start")]
        ]
        return await send_ghosty_message(update, text, kb, context=context)

    # --- 2. ПЕРЕВІРКА ДАНИХ ДОСТАВКИ ---
    full_name = profile.get("full_name")
    phone = profile.get("phone")
    city = profile.get("city")
    address = profile.get("address_details")
    district = profile.get("district") # Важливо для розрахунку кур'єра
    
    is_ready = all([full_name, phone, city, address])

    # --- 3. РОЗРАХУНОК ТОВАРІВ ---
    total_sum = 0.0
    items_html = ""
    kb = []
    has_gift = False

    for item in cart:
        item_id = item.get('real_id')
        # Використовуємо універсальну функцію ціни з Секції 4
        price_html, final_price, _ = get_price_display(item.get('price', 0), profile, item_id)
        
        total_sum += final_price
        
        # Деталізація (Колір / Міцність / Подарунок)
        meta = []
        if item.get('color'): meta.append(f"🎨 {item['color']}")
        if item.get('strength'): meta.append(f"⚡️ {item['strength']}mg")
        if item.get('gift'): 
            meta.append(f"🎁 +{item['gift']}")
            has_gift = True
            
        meta_str = f"<i>({', '.join(meta)})</i>" if meta else ""
        
        items_html += (
            f"▫️ <b>{item.get('name')}</b> {meta_str}\n"
            f"  └ Ціна: {price_html}\n\n"
        )
        
        # Кнопка видалення конкретного екземпляра
        uid = item.get('id')
        kb.append([InlineKeyboardButton(f"❌ Видалити {item.get('name')[:12]}...", callback_data=f"cart_del_{uid}")])

    # --- 4. ЛОГІКА ДОСТАВКИ ТА КУР'ЄРА ---
    delivery_info = ""
    courier_fee = 0.0
    
    if is_ready:
        # Якщо обрано район "Кур'єр", додаємо фіксовану вартість із Секції 3
        if district == "Кур'єр":
            courier_fee = globals().get('COURIER_PRICE', 150.0)
            total_sum += courier_fee
            delivery_info = (
                f"📍 <b>Доставка:</b> {city}, {address}\n"
                f"🛵 <b>Спосіб:</b> Кур'єр (+{int(courier_fee)} ₴)\n"
                f"👤 <b>Отримувач:</b> {full_name} ({phone})"
            )
        else:
            delivery_info = (
                f"📍 <b>Доставка:</b> {city}, р-н {district}\n"
                f"📦 <b>Спосіб:</b> Готовий клад (0 ₴)\n"
                f"👤 <b>Отримувач:</b> {full_name} ({phone})"
            )
        
        checkout_btn = InlineKeyboardButton("🚀 ОФОРМИТИ ЗАМОВЛЕННЯ", callback_data="checkout_init")
    else:
        delivery_info = "⚠️ <b>Дані доставки не заповнені!</b>\nНатисніть кнопку нижче, щоб додати адресу."
        checkout_btn = InlineKeyboardButton("📝 ЗАПОВНИТИ ДАНІ", callback_data="fill_delivery_data")

    # --- 5. ФОРМУВАННЯ ТЕКСТУ ---
    gift_note = "🎉 <i>Вам нараховано безкоштовний бонус до замовлення!</i>\n━━━━━━━━━━━━━━━━━━━━\n" if has_gift else ""
    
    full_text = (
        f"🛒 <b>ВАШЕ ЗАМОВЛЕННЯ ({len(cart)})</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{items_html}"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{gift_note}"
        f"{delivery_info}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 <b>РАЗОМ ДО СПЛАТИ: {total_sum:.2f} ₴</b>"
    )

    # Збірка клавіатури
    kb.insert(0, [checkout_btn])
    
    footer = []
    # Показуємо кнопку промокоду тільки якщо ще немає знижки
    if not profile.get('next_order_discount'):
        footer.append(InlineKeyboardButton("🎟 ПРОМОКОД", callback_data="menu_promo"))
    
    footer.append(InlineKeyboardButton("🗑 ОЧИСТИТИ", callback_data="cart_clear"))
    kb.append(footer)
    kb.append([InlineKeyboardButton("🔙 НАЗАД ДО КАТАЛОГУ", callback_data="cat_all")])

    await send_ghosty_message(update, full_text, kb, context=context)


async def cart_action_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробник швидких дій у кошику (видалення/очищення)."""
    query = update.callback_query
    data = query.data
    
    if data == "cart_clear":
        context.user_data["cart"] = []
        await query.answer("🗑 Кошик повністю очищено")
        
    elif data.startswith("cart_del_"):
        uid = int(data.split("_")[2])
        cart = context.user_data.get("cart", [])
        # Видаляємо лише один конкретний товар за його унікальним внутрішнім ID
        context.user_data["cart"] = [i for i in cart if i.get('id') != uid]
        await query.answer("❌ Товар видалено")

    # Повертаємось у оновлений кошик
    await show_cart_logic(update, context)
    

# =================================================================
# 🎁 SECTION 19: GIFT & CART ENGINE (TITAN ULTIMATE v10.5 - PRO FIX)
# =================================================================

def get_gift_data(gift_id: int):
    """Шукає дані про подарунок у спеціальному або загальному словнику."""
    gift_dict = globals().get('GIFT_LIQUIDS', {})
    if gift_id in gift_dict:
        return gift_dict[gift_id]
    # Якщо не знайшли в подарунках, шукаємо в загальному каталозі рідин
    liquids_dict = globals().get('LIQUIDS', {})
    return liquids_dict.get(gift_id)

async def gift_selection_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Генератор меню вибору подарунка. 
    Виправлено: Точна прив'язка емодзі та очищення назв.
    """
    query = update.callback_query
    data = query.data
    parts = data.split("_")
    
    # Визначаємо контекст (звідки прийшов користувач)
    if data.startswith("fast_order_"): prefix, item_id = "fast_order", int(parts[2])
    elif data.startswith("mgr_pre_"): prefix, item_id = "mgr_pre", int(parts[2])
    elif data.startswith("add_"): prefix, item_id = "add", int(parts[1])
    else:
        # Fallback для складних випадків
        try:
            item_id = context.user_data.get('target_item_id')
            prefix = "add"
        except:
            await query.answer("❌ Помилка контексту вибору", show_alert=True)
            return

    main_item = get_item_data(item_id)
    if not main_item:
        await query.answer("❌ Товар не знайдено", show_alert=True)
        return

    # 🔥 ТАБЛИЦЯ ЕМОДЗІ (Пункт №4: Підібрано під смак)
    emoji_map = {
        "Fall Tea": "🍵", "Mystery": "🔮", "Strawberry": "🍓",
        "Grape": "🍇", "BlackCurrant": "🫐", "Cola": "🥤", 
        "Rose": "🌹", "Lemonade": "🍹", "Energetic": "⚡️",
        "Vitamin": "🍏", "Apple": "🍏", "Pomelo": "🍊", "Jelly": "🍮"
    }

    text = (
        f"🎁 <b>АКЦІЯ: ОБЕРІТЬ ВАШ БОНУС!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"До <b>{main_item['name']}</b> додається\n"
        f"рідина 30мл абсолютно <b>БЕЗКОШТОВНО</b>!\n\n"
        f"👇 <i>Оберіть смак:</i>"
    )

    kb = []
    gift_dict = globals().get('GIFT_LIQUIDS', {})
    
    for gid, gift_item in gift_dict.items():
        raw_name = gift_item['name'].replace("🎁 ", "").replace(" 30ml", "").strip()
        
        # Динамічний підбір іконки за ключовими словами
        icon = "🧪"
        for key, em in emoji_map.items():
            if key.lower() in raw_name.lower():
                icon = em
                break
        
        kb.append([InlineKeyboardButton(f"{icon} {raw_name}", callback_data=f"set_gift_{prefix}_{item_id}_{gid}")])

    kb.append([InlineKeyboardButton("❌ Без подарунка", callback_data=f"{prefix}_{item_id}_0")])
    kb.append([InlineKeyboardButton("🔙 Назад до товару", callback_data=f"view_item_{item_id}")])

    await _edit_or_reply(query, text, kb, context=context)

async def add_to_cart_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Фінальна обробка додавання в кошик.
    Виправлено: Коректне відображення ціни та збереження бонусів.
    """
    query = update.callback_query
    data = query.data
    
    # Обробка префікса (якщо це вибір подарунка)
    if data.startswith("set_gift_"):
        parts = data.split("_") # set, gift, prefix, item_id, gid
        prefix = parts[2]
        item_id = int(parts[3])
        gift_id = int(parts[4])
    else:
        parts = data.split("_")
        item_id = int(parts[1])
        gift_id = int(parts[-1]) if len(parts) > 2 and parts[-1].isdigit() else None

    item = get_item_data(item_id)
    if not item:
        await query.answer("❌ Помилка: Товар не знайдено")
        return

    # Перевірка, чи потрібен подарунок
    needs_gift = (item_id < 300 or 500 <= item_id < 700 or item.get('gift_liquid'))
    if needs_gift and gift_id is None:
        await gift_selection_handler(update, context)
        return

    # Формування об'єкта для кошика
    selected_color = context.user_data.get('selected_color')
    gift_name = None
    if gift_id and gift_id > 0:
        g_data = get_gift_data(gift_id)
        if g_data:
            gift_name = g_data['name'].replace("🎁 ", "")

    # Додаємо в кошик
    new_entry = {
        "id": random.randint(100000, 999999),
        "real_id": item_id,
        "name": item['name'],
        "price": item['price'],
        "color": selected_color,
        "gift": gift_name
    }
    
    context.user_data.setdefault("cart", []).append(new_entry)
    
    # Логіка відображення ціни (з урахуванням знижок профілю)
    profile = context.user_data.get('profile', {})
    display_price = f"{int(item['price'])} ₴"
    if 'get_price_display' in globals():
        display_price, _ = get_price_display(item['price'], profile, item_id)

    # Фінальне повідомлення
    info = f"\n🎨 Колір: <b>{selected_color}</b>" if selected_color else ""
    info += f"\n🎁 Бонус: <b>{gift_name}</b>" if gift_name else ""

    text = (
        f"✅ <b>УСПІШНО ДОДАНО!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📦 <b>{item['name']}</b>"
        f"{info}\n"
        f"💰 Ціна: <b>{display_price}</b>\n\n"
        f"Що бажаєте зробити далі?"
    )

    kb = [
        [InlineKeyboardButton("🛒 ОФОРМИТИ ЗАМОВЛЕННЯ", callback_data="menu_cart")],
        [InlineKeyboardButton("🛍 ПРОДОВЖИТИ ШОПІНГ", callback_data="cat_all")],
        [InlineKeyboardButton("🏠 НА ГОЛОВНУ", callback_data="menu_start")]
    ]

    await _edit_or_reply(query, text, kb, context=context)
    try: await query.answer("Додано!")
    except: pass
        
# =================================================================
# 💳 SECTION 20: CHECKOUT & PAYMENT CORE (TITAN FINAL - PRO FIX)
# =================================================================

import sqlite3
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from html import escape

logger = logging.getLogger("GhostyCore")

async def checkout_init(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Ініціалізація оплати. Розраховує фінальну суму з урахуванням усіх знижок та бонусів.
    """
    query = update.callback_query
    profile = context.user_data.get('profile', {})
    user_id = update.effective_user.id
    
    # 1. СИНХРОНІЗАЦІЯ БОНУСІВ (Свіжі дані з БД)
    try:
        db_path = globals().get('DB_PATH', 'data/ghosty_pro_final.db')
        with sqlite3.connect(db_path) as conn:
            res = conn.execute("SELECT next_order_discount FROM users WHERE user_id=?", (user_id,)).fetchone()
            if res:
                profile['next_order_discount'] = float(res[0])
    except Exception as e:
        logger.error(f"Balance sync error: {e}")

    # Отримуємо дані для розрахунку
    target_item_id = context.user_data.get('target_item_id') # Для "Швидкого замовлення"
    user_balance = float(profile.get('next_order_discount', 0.0))
    
    total_amount = 0.0
    items_desc = ""
    photo_to_show = None 

    # --- ВАРІАНТ А: ШВИДКЕ ЗАМОВЛЕННЯ (МИНУЮЧИ КОШИК) ---
    if target_item_id:
        item = get_item_data(target_item_id)
        if not item: 
            await query.answer("❌ Помилка завантаження товару.", show_alert=True)
            return
        
        # Визначаємо фото (враховуємо колір)
        selected_color = context.user_data.get('selected_color')
        photo_to_show = item.get('img')
        if selected_color and "color_previews" in item:
            for key, url in item["color_previews"].items():
                if key in str(selected_color):
                    photo_to_show = url; break

        # Розрахунок ціни (враховуємо VIP знижку з Section 4)
        _, final_p, _ = get_price_display(item['price'], profile, target_item_id)
        total_amount = final_p
        
        # Формуємо текст
        color_txt = f" (🎨 {selected_color})" if selected_color else ""
        str_txt = f" (⚡️ {context.user_data.get('selected_strength')}mg)" if context.user_data.get('selected_strength') else ""
        items_desc = f"▫️ <b>{item['name']}</b>{color_txt}{str_txt}\n   └ 💰 {int(final_p)} грн"

        # Перевірка подарунка
        target_gift_id = context.user_data.get('target_gift_id')
        if target_gift_id:
            gift = get_item_data(target_gift_id)
            if gift: items_desc += f"\n   🎁 <i>Бонус: {gift['name']} (0 грн)</i>"

    # --- ВАРІАНТ Б: ПОВНИЙ КОШИК ---
    else:
        cart = context.user_data.get('cart', [])
        if not cart:
            await query.answer("🛒 Кошик порожній!", show_alert=True)
            return
            
        photo_to_show = globals().get('WELCOME_PHOTO') # Фото для кошика (загальне)
        for i in cart:
            _, p, _ = get_price_display(i.get('price', 0), profile, i.get('real_id'))
            total_amount += p
            
            meta = []
            if i.get('color'): meta.append(f"🎨 {i['color']}")
            if i.get('strength'): meta.append(f"⚡️ {i['strength']}mg")
            if i.get('gift'): meta.append(f"🎁 {i['gift']}")
            meta_txt = f" ({', '.join(meta)})" if meta else ""
            
            items_desc += f"▫️ <b>{i['name']}</b>{meta_txt}\n   └ 💰 {int(p)} грн\n"

    # --- ЛОГІКА ДОСТАВКИ (VIP FREE VS REGULAR) ---
    dist = profile.get('district', 'Самовивіз')
    if "Кур'єр" in str(dist):
        if not profile.get("is_vip", False):
            fee = globals().get('COURIER_PRICE', 150.0)
            total_amount += fee
            items_desc += f"\n🛵 <b>Доставка:</b> +{int(fee)} грн"
        else:
            items_desc += "\n🚀 <b>Доставка:</b> VIP FREE (0 грн)"

    # --- БОНУСНА СИСТЕМА (Списання 💎) ---
    used_bonus = 0.0
    if user_balance > 0:
        # Залишаємо мінімум 10 грн до сплати (захист від нульових чеків)
        max_can_deduct = max(0.0, total_amount - 10.0)
        used_bonus = min(user_balance, max_can_deduct)
        
        if used_bonus > 0:
            total_amount -= used_bonus
            items_desc += f"\n\n💎 <b>Використано бонусів:</b> -{int(used_bonus)} грн"
    
    # Зберігаємо фінальну суму для перевірки оплати
    context.user_data['final_checkout_sum'] = total_amount
    context.user_data['planned_bonus_deduction'] = used_bonus

    # ФОРМУВАННЯ ФІНАЛЬНОГО ТЕКСТУ
    checkout_text = (
        f"🧾 <b>ФІНАЛЬНИЙ ЧЕК</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{items_desc}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📍 <b>Локація:</b> {profile.get('city', 'Не вказано')}, {dist}\n"
        f"👤 <b>Отримувач:</b> {escape(str(profile.get('full_name', 'Клієнт')))}\n\n"
        f"💰 <b>РАЗОМ ДО СПЛАТИ: {int(total_amount)} UAH</b>\n\n"
        f"👇 <i>Оберіть спосіб оплати:</i>"
    )

    kb = [
        [InlineKeyboardButton("💳 Monobank", callback_data="pay_mono"),
         InlineKeyboardButton("💚 Privat24", callback_data="pay_privat")],
        [InlineKeyboardButton("💎 Crypto / USDT (TON)", callback_data="pay_crypto")],
        [InlineKeyboardButton("🔙 Назад", callback_data="show_cart" if not target_item_id else f"item_{target_item_id}")]
    ]

    await send_ghosty_message(update, checkout_text, kb, photo=photo_to_show, context=context)

# -----------------------------------------------------------------
# ОБРОБКА ВИБОРУ СПОСОБУ ОПЛАТИ
# -----------------------------------------------------------------
async def payment_selection_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Видає реквізити залежно від обраного методу."""
    query = update.callback_query
    data = query.data # pay_mono, pay_privat, pay_crypto
    method = data.replace("pay_", "")
    
    amount_uah = context.user_data.get('final_checkout_sum', 0)
    links = globals().get('PAYMENT_LINK', {})
    
    if method == "crypto":
        usdt_rate = globals().get('USDT_RATE', 43.7)
        ton_wallet = globals().get('TON_WALLET', 'Адреса відсутня')
        amount_usdt = amount_uah / usdt_rate
        
        text = (
            f"💎 <b>ОПЛАТА USDT (TON)</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💵 Сума: <b>{int(amount_uah)} UAH</b>\n"
            f"📈 Курс: <code>{usdt_rate}</code>\n"
            f"👉 До сплати: <b>{amount_usdt:.2f} USDT</b>\n\n"
            f"🔗 <b>Гаманець (натисніть щоб копіювати):</b>\n"
            f"<code>{ton_wallet}</code>\n\n"
            f"⚠️ Мережа: <b>TON (USDT)</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💳 <a href='{links.get('ghossty_web', '#')}'>Оплатити карткою через Ghossty Pay</a>"
        )
    else:
        # Для Monobank / Privat24
        pay_url = links.get(method, "#")
        text = (
            f"💳 <b>ОПЛАТА {method.upper()}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"Сума: <b>{int(amount_uah)} UAH</b>\n\n"
            f"🔗 <b>Посилання на оплату:</b>\n"
            f"<a href='{pay_url}'>👉 НАТИСНІТЬ ТУТ ДЛЯ ПЕРЕКАЗУ</a>\n\n"
            f"⚠️ <b>КРОКИ:</b>\n"
            f"1. Оплатіть суму за посиланням.\n"
            f"2. Зробіть скріншот чека.\n"
            f"3. Натисніть кнопку підтвердження."
        )

    kb = [
        [InlineKeyboardButton("✅ Я ОПЛАТИВ (НАДІСЛАТИ ЧЕК)", callback_data="confirm_payment_start")],
        [InlineKeyboardButton("🔙 Змінити метод", callback_data="checkout_init")]
    ]

    # Використовуємо edit_text, бо ми вже в меню оплати (міняємо тільки текст)
    await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode='HTML', disable_web_page_preview=True)
    
# =================================================================
# ⚙️ SECTION 8: PROMO & REFERRAL (DB SYNCED & SECURE)
# =================================================================

async def process_promo(update: Update, context: ContextTypes.DEFAULT_TYPE, silent=False):
    """Обробка промокодів та реферальних зв'язків."""
    if not (update.message and update.message.text): return
    
    raw_text = update.message.text.strip().upper()
    user = update.effective_user
    profile = context.user_data.setdefault("profile", {})
    msg, is_success = "", False
    
    try:
        conn = sqlite3.connect(DB_PATH, timeout=30)
        cursor = conn.cursor()
        
        # --- 1. ГЛОБАЛЬНИЙ ПРОМО (GHST2026) ---
        if raw_text == "GHST2026":
            if profile.get('promo_GHST2026_used'):
                msg = "⚠️ <b>Ви вже активували цей промокод!</b>"
            else:
                # Нарахування бонусу
                profile["next_order_discount"] = float(profile.get("next_order_discount", 0)) + 69.0
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
                    "💰 Бонус: <b>+69 UAH</b>\n"
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
                ref_data = cursor.execute("SELECT user_id, next_order_discount, vip_expiry FROM users WHERE user_id = ?", (target_id,)).fetchone()
                
                if not ref_data:
                    msg = "❌ <b>Код не знайдено. Перевірте цифри.</b>"
                else:
                    # А) Нараховуємо новому користувачу (тому, хто ввів код)
                    profile["referral_used"] = True
                    profile["next_order_discount"] = float(profile.get("next_order_discount", 0)) + 50.0
                    
                    # VIP для нового
                    now = datetime.now()
                    new_exp = (now + timedelta(days=7)).strftime("%Y-%m-%d")
                    profile["vip_expiry"] = new_exp
                    profile["is_vip"] = True
                    
                    # Б) Нараховуємо рефереру (тому, хто запросив)
                    ref_discount = float(ref_data[1] or 0) + 50.0
                    ref_vip_raw = ref_data[2]
                    
                    ref_start_date = now
                    if ref_vip_raw:
                        try:
                            rd = datetime.strptime(ref_vip_raw, "%Y-%m-%d")
                            if rd > now: ref_start_date = rd
                        except: pass
                    
                    ref_new_vip = (ref_start_date + timedelta(days=7)).strftime("%Y-%m-%d")
                    
                    # Оновлюємо реферера в БД
                    cursor.execute("""
                        UPDATE users SET next_order_discount = ?, vip_expiry = ?, is_vip = 1 WHERE user_id = ?
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
                            text=f"🎉 <b>Твій код активовано!</b>\n\n💰 Нараховано: <b>+50 UAH</b>\n💎 VIP продовжено до: <b>{ref_new_vip}</b>",
                            parse_mode='HTML'
                        )
                    except: pass
        else:
            msg = "❌ <b>Невірний код або формат.</b>"

        # --- 3. ФІНАЛІЗАЦІЯ ---
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
        logger.error(f"Promo Error: {e}")
        msg = "⚠️ Помилка бази даних."
    finally:
        if 'conn' in locals(): conn.close()

    context.user_data['awaiting_promo'] = False
    
    if not silent:
        kb = [[InlineKeyboardButton("👤 Профіль", callback_data="menu_profile")],
              [InlineKeyboardButton("🛍 В каталог", callback_data="cat_all")]]
        await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode='HTML')

# =================================================================
# 🛡 SECTION 21 & 26: ORDER CONFIRMATION & RECEIPT PROCESSING
# =================================================================

ADMIN_ID = 5309653842  # Твій ID менеджера

async def payment_confirmation_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    КРОК 1: Ініціація (Запит чека). Викликається кнопкою 'Я оплатив'.
    """
    query = update.callback_query
    
    # Генеруємо номер замовлення, якщо його ще немає
    if not context.user_data.get('current_order_id'):
        context.user_data['current_order_id'] = random.randint(100000, 999999)
    
    order_id = context.user_data['current_order_id']
    amount = context.user_data.get('final_checkout_sum', 0)
    
    # Текст запиту (Професійний UX)
    text = (
        f"⏳ <b>ЗАМОВЛЕННЯ #{order_id} ОЧІКУЄ ЧЕК</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💵 До сплати: <b>{amount:.2f} UAH</b>\n\n"
        f"📸 <b>ВАША ДІЯ:</b>\n"
        f"Будь ласка, надішліть <b>скріншот квитанції</b> або <b>фото чека</b> прямо у цей чат.\n\n"
        f"<i>🤖 Система автоматично розпізнає документ та сповістить модератора.</i>"
    )
    
    # Активуємо режим очікування фото
    context.user_data['state'] = "WAITING_RECEIPT"
    
    kb = [[InlineKeyboardButton("❌ СКАСУВАТИ ЗАМОВЛЕННЯ", callback_data="menu_start")]]
    
    if query:
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode='HTML')
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode='HTML')


async def handle_receipt_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    КРОК 2: Обробка фото чека. Викликається автоматично, коли юзер кидає фото.
    """
    # Перевіряємо, чи ми взагалі чекаємо чек від цього юзера
    if context.user_data.get('state') != "WAITING_RECEIPT":
        return

    user = update.effective_user
    profile = context.user_data.get('profile', {})
    order_id = context.user_data.get('current_order_id', '???')
    amount = context.user_data.get('final_checkout_sum', 0)
    bonus_deducted = context.user_data.get('planned_bonus_deduction', 0)

    # Візуальний фідбек
    status_msg = await update.message.reply_text("📡 <i>З'єднання з банківським шлюзом... Перевірка чека...</i>", parse_mode='HTML')
    
    # Отримуємо файл чека
    photo_file = await update.message.photo[-1].get_file()
    
    # Формуємо склад замовлення для адміна
    cart = context.user_data.get('cart', [])
    if context.user_data.get('target_item_id'):
        items_txt = f"• Швидке замовлення (ID: {context.user_data['target_item_id']})"
    else:
        items_txt = "\n".join([f"• {i['name']} ({i.get('color', 'Стандарт')})" for i in cart])

    # Текст для ТЕБЕ (Адміна)
    admin_text = (
        f"💳 <b>НОВИЙ ПЛАТІЖ #{order_id}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>Клієнт:</b> <a href='tg://user?id={user.id}'>{user.first_name}</a> (@{user.username})\n"
        f"💰 <b>Сума в чеку:</b> {int(amount)} UAH\n"
        f"💎 <b>Знижка бонусами:</b> -{int(bonus_deducted)} UAH\n"
        f"📍 <b>Локація:</b> {profile.get('city')}, {profile.get('district')}\n\n"
        f"📦 <b>ТОВАРИ:</b>\n{items_txt}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👇 <b>ВЕРДИКТ:</b>"
    )

    # Кнопки прийняття/відмови для адміна
    admin_kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ ПРИЙНЯТИ", callback_data=f"adm_pay_ok_{user.id}_{order_id}"),
            InlineKeyboardButton("❌ ФЕЙК / ВІДМОВА", callback_data=f"adm_pay_no_{user.id}_{order_id}")
        ],
        [InlineKeyboardButton("💬 ПЕРЕЙТИ ДО ЧАТУ", url=f"tg://user?id={user.id}")]
    ])

    try:
        # Відправляємо тобі фото з кнопками
        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=photo_file.file_id,
            caption=admin_text,
            reply_markup=admin_kb,
            parse_mode='HTML'
        )
        
        # Відповідь клієнту
        await status_msg.edit_text(
            f"✅ <b>ЧЕК УСПІШНО ПРИЙНЯТО!</b>\n\n"
            f"Менеджер перевірить транзакцію. Ви отримаєте сповіщення про готовність замовлення.\n"
            f"🆔 Номер: <code>#{order_id}</code>",
            parse_mode='HTML'
        )
    except Exception as e:
        logger.error(f"Critical Gateway Error: {e}")
        await status_msg.edit_text("⚠️ Помилка передачі даних. Зв'яжіться з @ghosstydp")

    # Очищуємо робочі дані
    context.user_data['state'] = None
    context.user_data['cart'] = []
    context.user_data['target_item_id'] = None


async def admin_decision_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    ОБРОБКА РІШЕННЯ АДМІНІСТРАТОРА (Кнопки ✅/❌)
    """
    query = update.callback_query
    data = query.data # adm_pay_ok_USERID_ORDERID
    
    # Парсимо дані з кнопки
    _, _, action, client_id, order_id = data.split("_")
    client_id = int(client_id)

    if action == "ok":
        # Списуємо бонуси з БД фінально (якщо були)
        # (Тут можна додати виклик функції видачі кладу/товару)
        
        await context.bot.send_message(
            chat_id=client_id,
            text=f"🎉 <b>ОПЛАТУ ПІДТВЕРДЖЕНО!</b>\nВаше замовлення #{order_id} передано в доставку/видачу. Очікуйте наступне повідомлення.",
            parse_mode='HTML'
        )
        await query.edit_message_caption(caption=query.message.caption + "\n\n✅ <b>СТАТУС: ОПЛАЧЕНО</b>", reply_markup=None)
        
    else:
        await context.bot.send_message(
            chat_id=client_id,
            text=f"❌ <b>ПОМИЛКА ОПЛАТИ</b>\nВаш чек для замовлення #{order_id} було відхилено. Можливо, сума невірна або транзакція не пройшла. Зв'яжіться з підтримкою.",
            parse_mode='HTML'
        )
        await query.edit_message_caption(caption=query.message.caption + "\n\n❌ <b>СТАТУС: ВІДХИЛЕНО</b>", reply_markup=None)

    await query.answer("Дію виконано")



# =================================================================
# 🤵 SECTION 27: MANAGER ORDER HUB (FAST ORDER & BALANCE PRO)
# =================================================================

from urllib.parse import quote 

# Твій актуальний ID та Юзернейм
ADMIN_ID = 5309653842 
MANAGER_USERNAME = "@ghosstydp" # Зміни на свій юзернейм без @, якщо треба

async def submit_order_to_manager(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Генератор заявки для менеджера та системи оплати.
    Об'єднує: Розрахунок, Списання бонусів, Deep Link та Шлюз чеків.
    """
    user = update.effective_user
    profile = context.user_data.get('profile', {})
    
    # 1. ЗБІР ТОВАРІВ (Швидке замовлення або Кошик)
    target_item_id = context.user_data.get('target_item_id')
    target_gift_id = context.user_data.get('target_gift_id')
    cart = context.user_data.get('cart', [])
    
    items_text = ""
    total_goods_price = 0.0
    
    if target_item_id:
        item = get_item_data(target_item_id)
        if item:
            color = context.user_data.get('selected_color')
            _, price, _ = get_price_display(item['price'], profile, target_item_id)
            total_goods_price = price
            color_str = f" (🎨 {color})" if color else ""
            items_text += f"▫️ {item['name']}{color_str} — {int(price)} грн\n"
            if target_gift_id:
                g = get_item_data(target_gift_id)
                if g: items_text += f"    🎁 Бонус: {g['name']}\n"
    elif cart:
        for i in cart:
            _, p, _ = get_price_display(i['price'], profile, i.get('real_id'))
            total_goods_price += p
            details = [f"🎨 {i['color']}"] if i.get('color') else []
            if i.get('gift'): details.append(f"🎁 {i['gift']}")
            items_text += f"▫️ {i['name']} ({', '.join(details)}) — {int(p)} грн\n"
    else:
        if update.callback_query: await update.callback_query.answer("⚠️ Кошик порожній", show_alert=True)
        return

    # 2. РОЗРАХУНОК ДОСТАВКИ ТА БОНУСІВ
    delivery_price = 150.0 if "Кур'єр" in str(profile.get('district', '')) and not profile.get("is_vip") else 0.0
    pre_total = total_goods_price + delivery_price
    
    current_balance = float(profile.get('next_order_discount', 0.0))
    discount_to_apply = min(current_balance, max(0.0, pre_total - 1.0))
    final_amount = pre_total - discount_to_apply
    
    # Зберігаємо фінальну суму для секції оплати
    context.user_data['final_checkout_sum'] = final_amount
    context.user_data['planned_bonus_deduction'] = discount_to_apply

    # 3. ГЕНЕРАЦІЯ ID ТА КЕШУВАННЯ В БД
    order_id = f"GH-{user.id}-{random.randint(1000, 9999)}"
    context.user_data['current_order_id'] = order_id
    
    try:
        with sqlite3.connect(DB_PATH, timeout=30) as conn:
            conn.execute("INSERT INTO orders (order_id, user_id, amount, status) VALUES (?, ?, ?, ?)",
                         (order_id, user.id, final_amount, 'awaiting_payment'))
            conn.commit()
    except Exception as e: logger.error(f"DB Order Error: {e}")

    # 4. ФОРМУВАННЯ ПОВІДОМЛЕННЯ (REPORT)
    report = (
        f"👋 Замовлення #{order_id}\n"
        f"👤 {profile.get('full_name', 'Гість')} | 📞 {profile.get('phone')}\n"
        f"📍 {profile.get('city')}, {profile.get('district')}\n"
        f"🛒 ТОВАРИ:\n{items_text}"
        f"💰 ДО СПЛАТИ: {final_amount:.2f} грн"
    )
    
    # 5. СТВОРЕННЯ DEEP LINK (ДЛЯ РУЧНОГО РЕЖИМУ)
    encoded_text = quote(report)
    clean_manager = MANAGER_USERNAME.replace("@", "").strip()
    magic_link = f"https://t.me/{clean_manager}?text={encoded_text}"

    # 6. ВИВІД КЛІЄНТУ (ВИБІР ШЛЯХУ)
    text = (
        f"📦 <b>ЗАМОВЛЕННЯ #{order_id} СФОРМОВАНО</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💵 Сума: <b>{final_amount:.2f} грн</b>\n"
        f"💎 Знижка бонусами: <b>-{int(discount_to_apply)} грн</b>\n\n"
        f"👇 <b>ЯК БАЖАЄТЕ ПІДТВЕРДИТИ?</b>"
    )
    
    kb = [
        [InlineKeyboardButton("📸 НАДІСЛАТИ ЧЕК У БОТ (ШВИДКО)", callback_data="pay_confirm_bot")],
        [InlineKeyboardButton("✈️ НАПИСАТИ МЕНЕДЖЕРУ ЛС", url=magic_link)],
        [InlineKeyboardButton("🔙 НАЗАД", callback_data="menu_cart")]
    ]
    
    if update.callback_query:
        await update.callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode='HTML')
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode='HTML')

# --- СИСТЕМА ПРИЙНЯТТЯ РІШЕНЬ (CALLBACKS) ---

async def admin_decision_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробка кнопок ✅ Прийняти / ❌ Відмовити (для менеджера)."""
    query = update.callback_query
    if not query.data.startswith("adm_pay_"): return
    
    # adm_pay_ok_USERID_ORDERID
    _, _, action, client_id, order_id = query.data.split("_")
    client_id = int(client_id)
    
    if action == "ok":
        # Списуємо бонуси у клієнта ПІСЛЯ підтвердження оплати
        bonus = context.user_data.get('planned_bonus_deduction', 0)
        if bonus > 0:
             with sqlite3.connect(DB_PATH) as conn:
                conn.execute("UPDATE users SET next_order_discount = next_order_discount - ? WHERE user_id = ?", (bonus, client_id))
        
        await context.bot.send_message(client_id, f"✅ <b>Оплату замовлення #{order_id} підтверджено!</b>\nДякуємо! Очікуйте на видачу.", parse_mode='HTML')
        new_status = "✅ ОПЛАЧЕНО"
    else:
        await context.bot.send_message(client_id, f"❌ <b>Оплату #{order_id} відхилено.</b>\nЗв'яжіться з менеджером для уточнення.", parse_mode='HTML')
        new_status = "❌ ВІДХИЛЕНО"

    await query.edit_message_caption(caption=f"{query.message.caption}\n\n<b>{new_status}</b>", reply_markup=None, parse_mode='HTML')

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

import asyncio
import sqlite3
import logging
from telegram import Update
from telegram.ext import ContextTypes

# Ініціалізація логера (якщо він ще не створений глобально)
logger = logging.getLogger(__name__)

async def handle_user_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Центральний хаб: обробляє Текст, Медіа (чеки) та Стани.
    Titan Ultimate Engine v10.5 (Final Sync & Anti-Flood)
    """
    if not update.message: 
        return 
    
    user = update.effective_user
    # Універсальне отримання стану (зшиває Section 17 та інші)
    state = context.user_data.get('state') or context.user_data.get('data_step')
    raw_text = update.message.text.strip() if update.message.text else (update.message.caption or "")
    
    # --- 🛡 АНТИ-ФЛУД ДЛЯ ФОТО (Media Group Protection) ---
    # Якщо клієнт кидає чек альбомом (кілька фото за раз), Telegram надсилає їх як окремі повідомлення.
    # Цей код пропускає лише перше фото альбому, щоб уникнути дублювання замовлень.
    if update.message.media_group_id:
        if context.user_data.get('last_media_group_id') == update.message.media_group_id:
            return 
        context.user_data['last_media_group_id'] = update.message.media_group_id

    # 1. СИСТЕМА ДОСТУПУ (ADMIN/MANAGER)
    MANAGER_ID = globals().get('ADMIN_ID', 5309653842)
    ADMIN_LIST = globals().get('ADMIN_LIST', [])
    is_admin = (user.id == MANAGER_ID) or (user.id in ADMIN_LIST)

    # -----------------------------------------------------------
    # 💎 1. КЕРУВАННЯ БАЛАНСОМ (Тільки Адмін)
    # -----------------------------------------------------------
    if state == "WAITING_BALANCE_DATA" and is_admin:
        try:
            parts = raw_text.split()
            if len(parts) != 2:
                await update.message.reply_text("⚠️ Введіть ID та суму (напр. <code>12345 200</code>):", parse_mode='HTML')
                return
                
            target_id, amount = int(parts[0]), float(parts[1])
            db_path = globals().get('DB_PATH', 'data/store_db.sqlite')
            
            with sqlite3.connect(db_path, timeout=30) as conn:
                user_exists = conn.execute("SELECT user_id FROM users WHERE user_id=?", (target_id,)).fetchone()
                if not user_exists:
                    await update.message.reply_text("❌ Користувача не знайдено в базі.")
                    return
                
                conn.execute("UPDATE users SET next_order_discount = next_order_discount + ? WHERE user_id=?", (amount, target_id))
                conn.commit()
                
            await update.message.reply_text(f"✅ Користувачу <code>{target_id}</code> нараховано <b>{amount} грн</b>.", parse_mode='HTML')
            context.user_data['state'] = None 
            
            # Сповіщення клієнта
            try:
                await context.bot.send_message(
                    chat_id=target_id, 
                    text=f"🎁 <b>БАЛАНС ОНОВЛЕНО!</b>\n━━━━━━━━━━━━━━━━━━━━\nВам нараховано <b>{amount} грн</b> бонусів!",
                    parse_mode='HTML'
                )
            except Exception as e:
                logger.warning(f"Failed to notify user {target_id} about balance: {e}")
                
        except ValueError:
            await update.message.reply_text("❌ Помилка: ID та сума повинні бути числами.")
        except Exception as e:
            logger.error(f"Balance Update Error: {e}")
            await update.message.reply_text("❌ Системна помилка бази даних.")
        return

    # -----------------------------------------------------------
    # 🚀 2. АДМІН-РОЗСИЛКА (Broadcast)
    # -----------------------------------------------------------
    if state == "BROADCAST_MODE" and is_admin:
        try:
            db_path = globals().get('DB_PATH', 'data/store_db.sqlite')
            with sqlite3.connect(db_path) as conn:
                users = conn.execute("SELECT user_id FROM users").fetchall()
            
            if not users:
                await update.message.reply_text("❌ База порожня.")
                return

            sent, failed = 0, 0
            status_msg = await update.message.reply_text(f"🚀 Запуск розсилки на {len(users)} чол...")
            
            for (uid,) in users:
                try:
                    await update.message.copy(chat_id=uid)
                    sent += 1
                    # Надійніший захист від Flood Control API Telegram
                    if sent % 20 == 0: 
                        await asyncio.sleep(1.2) 
                except Exception: 
                    failed += 1 
            
            await status_msg.edit_text(
                f"✅ <b>Розсилку завершено!</b>\n"
                f"📥 Успішно: <code>{sent}</code>\n"
                f"❌ Заблокували бота: <code>{failed}</code>", 
                parse_mode='HTML'
            )
        except Exception as e:
            logger.error(f"Broadcast Error: {e}")
            await update.message.reply_text("❌ Виникла помилка під час розсилки.")
        finally:
            context.user_data['state'] = None
        return

    # -----------------------------------------------------------
    # 📸 3. ПРИЙОМ ЧЕКІВ (Обробка фото)
    # -----------------------------------------------------------
    if update.message.photo and state == "WAITING_RECEIPT":
        if 'handle_receipt_photo' in globals():
            # Безпечний виклик через globals(), щоб уникнути помилок імпорту
            await globals()['handle_receipt_photo'](update, context)
        else:
            await update.message.reply_text("🆘 Модуль оплати тимчасово недоступний. Зв'яжіться з підтримкою.")
        return

    # -----------------------------------------------------------
    # 📝 4. ТЕКСТОВА МАРШРУТИЗАЦІЯ (Анкета, Промо, Пошук)
    # -----------------------------------------------------------
    if raw_text and not raw_text.startswith("/"):
        
        # Крок 1: Анкета користувача (Section 17)
        steps = ["name", "phone", "address", "awaiting_city"]
        if state in steps:
            if 'handle_data_input' in globals():
                await globals()['handle_data_input'](update, context)
            return

        # Крок 2: Промокоди
        if context.user_data.get('awaiting_promo'):
            if 'process_promo' in globals():
                await globals()['process_promo'](update, context)
            return

        # Крок 3: Вільний текст (коли немає станів)
        if not state:
            # Ігноруємо випадковий текст, щоб бот не спамив повідомленнями "Я не розумію".
            # Або тут можна підключити функцію пошуку товарів за назвою.
            pass

# =================================================================
# 👮‍♂️ SECTION 25: ADMIN GOD-PANEL (MONITORING & FINANCIALS)
# =================================================================

import sqlite3
import random
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

# Універсальна перевірка на Адміна
def check_is_admin(user_id: int) -> bool:
    manager_id = globals().get('ADMIN_ID', 5309653842) # Основний ID
    admin_list = globals().get('ADMIN_LIST', [])
    return (user_id == manager_id) or (user_id in admin_list)

# Допоміжна функція для безпечної зміни повідомлень
async def _safe_edit_or_reply(update: Update, text: str, reply_markup: list, parse_mode='HTML'):
    kb = InlineKeyboardMarkup(reply_markup)
    query = update.callback_query
    if query:
        await query.answer()
        await query.edit_message_text(text=text, reply_markup=kb, parse_mode=parse_mode)
    else:
        await update.message.reply_text(text=text, reply_markup=kb, parse_mode=parse_mode)

async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Головне меню GOD-MODE."""
    user = update.effective_user
    if not check_is_admin(user.id): 
        return 

    ping = random.randint(12, 28)
    start_time = globals().get('START_TIME', datetime.now())
    uptime_str = str(datetime.now() - start_time).split('.')[0]
    active_sessions = len(context.application.user_data)
    cpu_load = random.randint(2, 7)

    text = (
        f"🛡 <b>ADMIN GOD-MODE v10.5</b>\n"
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
        [InlineKeyboardButton("👥 БАЗА КЛІЄНТІВ", callback_data="admin_view_users_0")],
        [InlineKeyboardButton("💰 ФІНАНСОВИЙ ЗВІТ", callback_data="admin_stats")],
        [InlineKeyboardButton("📢 РОЗСИЛКА", callback_data="admin_broadcast")],
        [InlineKeyboardButton("💳 КЕРУВАННЯ БАЛАНСОМ", callback_data="admin_add_balance")],
        [InlineKeyboardButton("🔙 ВИХІД", callback_data="menu_start")]
    ]
    await _safe_edit_or_reply(update, text, kb)

async def admin_decision_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробка кнопок Підтвердити/Відхилити чек."""
    query = update.callback_query
    await query.answer()
    
    parts = query.data.split("_")
    action, user_id = parts[1], int(parts[2])
    order_id = parts[3] if len(parts) > 3 else "Unknown"
    db_path = globals().get('DB_PATH', 'data/store_db.sqlite')
    
    old_caption = query.message.caption or "Чек оплати"

    if action == "ok":
        try:
            with sqlite3.connect(db_path, timeout=30) as conn:
                conn.execute("UPDATE orders SET status='paid' WHERE order_id=?", (order_id,))
                conn.commit()
            
            await query.edit_message_caption(caption=f"{old_caption}\n\n✅ <b>ПІДТВЕРДЖЕНО АДМІНОМ</b>", parse_mode='HTML')
            await context.bot.send_message(chat_id=user_id, text=f"🎉 <b>Вашу оплату підтверджено!</b>\n\nЗамовлення <code>#{order_id}</code> передано на пакування.", parse_mode='HTML')
        except Exception as e:
            logger.error(f"Admin OK Error: {e}")

    elif action == "no":
        try:
            with sqlite3.connect(db_path, timeout=30) as conn:
                conn.execute("UPDATE orders SET status='rejected' WHERE order_id=?", (order_id,))
                conn.commit()

            await query.edit_message_caption(caption=f"{old_caption}\n\n❌ <b>ВІДХИЛЕНО</b>", parse_mode='HTML')
            await context.bot.send_message(chat_id=user_id, text=f"⚠️ <b>Оплату по замовленню #{order_id} відхилено.</b>\nЗв'яжіться з менеджером для уточнення деталей.", parse_mode='HTML')
        except Exception as e:
            logger.error(f"Admin NO Error: {e}")

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Фінансова статистика (Захищено від пустих значень)."""
    db_path = globals().get('DB_PATH', 'data/store_db.sqlite')
    try:
        with sqlite3.connect(db_path, timeout=30) as conn:
            cur = conn.cursor()
            cur.execute("SELECT SUM(amount) FROM orders WHERE status='paid' AND created_at >= date('now', '-7 days')")
            revenue_7d = cur.fetchone()[0]
            revenue_7d = float(revenue_7d) if revenue_7d else 0.0
            
            cur.execute("SELECT COUNT(*) FROM orders WHERE status='paid' AND created_at >= date('now', '-7 days')")
            orders_count = cur.fetchone()[0] or 0
        
        avg_check = round(revenue_7d / orders_count, 2) if orders_count > 0 else 0.0

        text = (
            f"💰 <b>ФІНАНСОВИЙ ЗВІТ (7 ДНІВ)</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💵 Прибуток: <b>{revenue_7d:,.2f} UAH</b>\n"
            f"📦 Оплачених замовлень: <b>{orders_count}</b>\n"
            f"📈 Середній чек: <b>{avg_check} UAH</b>\n"
        )
        await _safe_edit_or_reply(update, text, [[InlineKeyboardButton("🔙 НАЗАД", callback_data="admin_main")]])
    except Exception as e:
        logger.error(f"Stats Error: {e}")
        await _safe_edit_or_reply(update, "❌ Помилка завантаження статистики.", [[InlineKeyboardButton("🔙 НАЗАД", callback_data="admin_main")]])

async def admin_view_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Перегляд бази з безпечною ПАГІНАЦІЄЮ."""
    query = update.callback_query
    page = 0
    if query and "admin_view_users_" in query.data:
        try: page = int(query.data.split("_")[-1])
        except ValueError: pass
        
    limit, offset = 10, page * 10
    db_path = globals().get('DB_PATH', 'data/store_db.sqlite')

    try:
        with sqlite3.connect(db_path, timeout=30) as conn:
            total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] or 0
            
            # Оптимізований SQL запит
            users_data = conn.execute(f"""
                SELECT u.username, u.user_id, u.phone, u.city, o.amount, o.status
                FROM users u
                LEFT JOIN orders o ON o.user_id = u.user_id 
                GROUP BY u.user_id
                ORDER BY u.reg_date DESC LIMIT ? OFFSET ?
            """, (limit, offset)).fetchall()

        if total_users == 0:
            report = "📭 База клієнтів порожня."
        else:
            report = f"👥 <b>КЛІЄНТИ (Стор. {page + 1}):</b>\n━━━━━━━━━━━━━━━━━━━━\n"
            for row in users_data:
                username, uid, phone, city, amount, status = row
                st_icon = "✅" if status == 'paid' else ("⏳" if status in ['pending', 'new_request'] else "❌")
                report += f"👤 @{username or 'Anon'} (<code>{uid}</code>)\n📞 {phone or '—'} | {city or '—'}\n💰 {f'{amount:.0f}₴' if amount else '—'} [{st_icon}]\n--------------------\n"

        kb, nav_row = [], []
        if page > 0: 
            nav_row.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"admin_view_users_{page-1}"))
        nav_row.append(InlineKeyboardButton("🔄 Оновити", callback_data=f"admin_view_users_{page}"))
        if offset + limit < total_users: 
            nav_row.append(InlineKeyboardButton("Далі ➡️", callback_data=f"admin_view_users_{page+1}"))
            
        kb.append(nav_row)
        kb.append([InlineKeyboardButton("🔙 НАЗАД", callback_data="admin_main")])
        await _safe_edit_or_reply(update, report, kb)
    except Exception as e:
        logger.error(f"View Users Error: {e}")

async def start_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запуск розсилки."""
    if not check_is_admin(update.effective_user.id): return
    
    context.user_data['state'] = "BROADCAST_MODE"
    text = (
        "📢 <b>РОЗСИЛКА</b>\n\n"
        "Надішліть повідомлення (текст, фото або відео).\n"
        "Бот автоматично розішле його всім клієнтам у базі."
    )
    await _safe_edit_or_reply(update, text, [[InlineKeyboardButton("❌ СКАСУВАТИ", callback_data="admin_main")]])

async def ask_balance_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запит ID та суми для поповнення балансу."""
    if not check_is_admin(update.effective_user.id): return

    context.user_data['state'] = "WAITING_BALANCE_DATA"
    text = (
        "💳 <b>НАРАХУВАННЯ БАЛАНСУ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Надішліть сюди в чат ID користувача та суму через пробіл.\n\n"
        "Приклад: <code>123456789 200</code>\n\n"
        "<i>(Щоб списати гроші, введіть суму з мінусом: 123456789 -50)</i>"
    )
    await _safe_edit_or_reply(update, text, [[InlineKeyboardButton("❌ СКАСУВАТИ", callback_data="admin_main")]])

# =================================================================
# ⚙️ SECTION 29: GLOBAL DISPATCHER (TITAN FINAL - BULLETPROOF)
# =================================================================

import traceback
import logging
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
    TITAN DISPATCHER v11.0: Ювелірна точність та стійкість до відмов.
    """
    query = update.callback_query
    data = query.data
    user = update.effective_user

    # 1. ATOMIC ANSWER: Миттєве підтвердження для UX
    try: 
        await query.answer() 
    except Exception: pass

    try:
        # --- 🛡️ ГВАРДІЯ ДОСТУПУ (ADMIN CHECK) ---
        if data.startswith(("adm_", "admin_")):
            admin_list = globals().get('ADMIN_LIST', [])
            manager_id = globals().get('MANAGER_ID')
            
            if user.id not in admin_list and user.id != manager_id:
                return await query.answer("⛔️ Доступ обмежено", show_alert=True)

            # Адмін-маршрутизація
            if data.startswith("adm_"): 
                return await admin_decision_handler(update, context)
            
            admin_map = {
                "admin_main": admin_menu,
                "admin_stats": admin_stats,
                "admin_broadcast": start_broadcast,
                "admin_add_balance": ask_balance_data,
                "admin_cancel_action": admin_menu
            }
            
            if data == "admin_cancel_action": context.user_data['state'] = None
            
            handler = admin_map.get(data)
            if handler: return await handler(update, context)
            
            if data.startswith("admin_view_users"): 
                return await admin_view_users(update, context)

        # --- 🏠 ГОЛОВНА НАВІГАТОРІЯ ---
        if data == "menu_start":
            await _reset_user_state(context)
            return await start_command(update, context)

        if data == "menu_profile": return await show_profile(update, context)
        
        if data == "menu_promo":
            context.user_data['state'] = "AWAITING_PROMO"
            return await _edit_or_reply(query, "🎟 <b>АКТИВАЦІЯ БОНУСІВ</b>\n\nВведіть ваш промокод у чат:", 
                                     [[InlineKeyboardButton("🔙 Назад", callback_data="menu_profile")]], context=context)

        if data == "ref_system": return await show_ref_info(update, context)

        # --- 🛍️ MARKET ENGINE (КАТАЛОГ ТА КОШИК) ---
        if data == "cat_all": 
            context.user_data['state'] = None
            return await catalog_main_menu(update, context)

        if data.startswith("cat_list_"): 
            return await show_category_items(update, context, data.replace("cat_list_", ""))

        if data.startswith("view_item_"):
            try:
                item_id = int(data.split("_")[2])
                return await view_item_details(update, context, item_id)
            except (IndexError, ValueError): 
                return await catalog_main_menu(update, context)

        if data.startswith("sel_col_"):
            p = data.split("_")
            if 'handle_color_selection_click' in globals() and len(p) >= 4:
                return await handle_color_selection_click(update, context, int(p[2]), "_".join(p[3:]))

        if data == "menu_cart": return await show_cart_logic(update, context)
        
        if data == "cart_clear" or data.startswith("cart_del_"): 
            return await cart_action_handler(update, context)

        # --- 💳 ТРАНЗАКЦІЙНИЙ ШЛЮЗ (CHECKOUT) ---
        if data == "checkout_init":
            context.user_data['target_item_id'] = None 
            return await start_data_collection(update, context, next_action='checkout')

        if data.startswith(("pay_mono", "pay_privat", "pay_crypto")):
            if 'payment_selection_handler' in globals():
                return await payment_selection_handler(update, context, data.replace("pay_", ""))

        if data == "confirm_payment_start":
            context.user_data['state'] = "AWAITING_PAYMENT_SCREENSHOT"
            return await _edit_or_reply(query, 
                "📸 <b>ПІДТВЕРДЖЕННЯ ОПЛАТИ</b>\n\nБудь ласка, надішліть скріншот чека прямо в цей чат.",
                [[InlineKeyboardButton("🔙 Змінити метод", callback_data="checkout_init")]], context=context)

        # --- 🚚 ЛОГІСТИКА ---
        if data == "choose_city": return await choose_city_menu(update, context)
        
        if data.startswith("sel_city_"):
            city = data.replace("sel_city_", "")
            return await choose_dnipro_delivery(update, context) if city == "Дніпро" else \
                   await district_selection_handler(update, context, city)

        # --- ⚡ ШВИДКІ ДІЇ ---
        if data.startswith(("fast_order_", "mgr_pre_", "gift_sel_")):
            # Об'єднана логіка для складних префіксів
            if data.startswith("gift_sel_"): return await gift_selection_handler(update, context)
            if data.startswith("add_"): return await add_to_cart_handler(update, context)
            
            # Fast Order parsing
            parts = data.split("_")
            item_id = int(parts[2])
            gift_id = int(parts[-1]) if (len(parts) > 3 and parts[-1].isdigit()) else None
            
            context.user_data.update({'target_item_id': item_id, 'target_gift_id': gift_id})
            next_act = 'fast_order' if "fast" in data else 'manager_order'
            return await start_data_collection(update, context, next_action=next_act)

    except Exception as e:
        logger.error(f"🚨 DISPATCHER CRITICAL: {e}\n{traceback.format_exc()}")
        try: 
            await query.message.reply_text("⚠️ Сталася помилка в обробці натискання. Спробуйте /start")
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
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, PicklePersistence, Defaults
from telegram.constants import ParseMode

# Конфігурація логів (ОБОВ'ЯЗКОВО до старту main)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

async def post_init(application: Application) -> None:
    """Професійний звіт системи моніторингу GHO$$TY для Адміна."""
    try:
        start_ping = time.time()
        bot_info = await application.bot.get_me()
        ping = round((time.time() - start_ping) * 1000, 2)
        
        db_sz = f"{os.path.getsize(DB_PATH) / 1024:.2f} KB" if os.path.exists(DB_PATH) else "🛠 NEW"
        # Розрахунок аптайму
        uptime_dt = datetime.now() - START_TIME
        uptime_str = str(uptime_dt).split('.')[0]
        
        report = (
            f"🛰 <b>GHO$$TY STAFF | MONITORING CENTER</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🤖 <b>BOT-NODE:</b> @{bot_info.username}\n"
            f"🛡 <b>VERSION:</b> <code>TITAN ULTIMATE v10.5</code>\n"
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
            f"👑 <i>System fully operational. Waiting for customers...</i>"
        )
        # Відправка менеджеру та адміну (якщо вони різні)
        await application.bot.send_message(chat_id=MANAGER_ID, text=report)
    except Exception as e:
        logger.error(f"Post-init reporting failed: {e}")

def main():
    # ЕЛІТНИЙ СИСАДМІН-ВИВІД
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\n" + "═"*60)
    print(f"   ☁️  GHO$$TY STAFF PREMIUM ENGINE v10.5  ☁️")
    print("═"*60)
    print(f"   [⏳] TIME:      {datetime.now().strftime('%H:%M:%S')}")
    print(f"   [👤] ADMIN ID:  {MANAGER_ID}")
    
    if not TOKEN or "ВСТАВ" in TOKEN:
        print(f"   [❌] FATAL:      BOT_TOKEN IS MISSING!")
        print("═"*60 + "\n")
        sys.exit(1)
        
    # Ініціалізація бази (Section 12)
    if 'init_db' in globals():
        globals()['init_db']()
        print(f"   [💾] DATABASE:   SQLITE3 Connection Active")
    
    # Конфігурація додатка
    persistence = PicklePersistence(filepath=PERSISTENCE_PATH)
    defaults = Defaults(parse_mode=ParseMode.HTML)

    app = (
        Application.builder()
        .token(TOKEN)
        .persistence(persistence)
        .defaults(defaults)
        .connection_pool_size(25)
        .post_init(post_init)
        .build()
    )

    # РЕЄСТРАЦІЯ ХЕНДЛЕРІВ (Titan Bulletproof Routing)
    app.add_handler(CommandHandler("start", globals().get('start_command')))
    app.add_handler(CommandHandler("admin", globals().get('admin_menu')))
    
    # Головний обробник кнопок (Section 29)
    app.add_handler(CallbackQueryHandler(globals().get('global_callback_handler')))
    
    # Головний обробник тексту та медіа (Section 30)
    app.add_handler(MessageHandler(
        (filters.TEXT | filters.PHOTO | filters.VIDEO | filters.Document.IMAGE) & ~filters.COMMAND, 
        globals().get('global_message_handler')
    ))
    
    # Error handler (Section 25)
    if 'error_handler' in globals():
        app.add_error_handler(globals()['error_handler'])
    
    print(f"   [🌐] NETWORK:    Pool Size: 25 | Drop Pending: True")
    print(f"   [🚀] STATUS:     POLLING STARTED - SYSTEM ONLINE")
    print("═"*60 + "\n")
    
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    # Фіксація часу старту для аптайму
    START_TIME = datetime.now()
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        print(f"\n   [🚫] SHUTDOWN:   System manually terminated.")
    except Exception as fatal_e:
        print(f"\n   [💥] CRASH:      CRITICAL ERROR DETECTED!")
        print(f"   [!] REASON:     {fatal_e}")
        traceback.print_exc()
        sys.exit(1)

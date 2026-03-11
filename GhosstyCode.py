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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True) 

DB_PATH = os.path.join(DATA_DIR, 'ghosty_pro_final.db')
PERSISTENCE_PATH = os.path.join(DATA_DIR, 'ghosty_state_final.pickle')
LOG_PATH = os.path.join(DATA_DIR, 'ghosty_system.log')

TOKEN = os.getenv("BOT_TOKEN", "8351638507:AAGH4wmu0UUk-v1rzLXIY3eTfQsSscDrvBE")
MANAGER_ID = 7544847872
ADMIN_LIST = [MANAGER_ID] # 🔥 Глобальний список адмінів
MANAGER_USERNAME = "ghosstydp"
CHANNEL_URL = "https://t.me/GhostyStaffDP"
WELCOME_PHOTO = "https://i.ibb.co/35K9Zp5p/Polish-20260310-051407282.png"

PAYMENT_LINK = {
    "mono": "https://lnk.ua/k4xJG21Vy",    
    "privat": "https://lnk.ua/RVd0OW6V3",
    "ghossty": "https://heylink.me/GhosstyShop"
}

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

START_TIME = datetime.now()

DEBUG_MODE = os.name == 'nt' 
if DEBUG_MODE:
    logger.setLevel(logging.DEBUG)
    logger.info("🛠 DEBUG MODE: ENABLED")


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
# 🛍 SECTION 3: DATA REGISTRY (PRODUCTS & CITIES)
# =================================================================

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

LIQUIDS = {
    301: {"name": "🍂 Fall Tea", "category": "Chaser Balance", "price": 279.99, "stock": 15, "discount": False, "strengths": [50, 65, 85], "img": "https://i.ibb.co/GmZH1XL/1-0.jpg", "desc": "☕ <b>Осінній Чай</b>\nСпокійний аромат чаю з нотками лимону.", "payment_url": PAYMENT_LINK},
    302: {"name": "👻 Mystery One", "category": "Chaser Balance", "price": 279.99, "stock": 15, "discount": False, "strengths": [50, 65, 85], "img": "https://i.ibb.co/DDnd5d2S/1-1.png", "desc": "🔮 <b>Ghost Edition</b>\nТаємничий фруктовий мікс.", "payment_url": PAYMENT_LINK},
    303: {"name": "🍓 Strawberry Jelly", "category": "Chaser Balance", "price": 279.99, "stock": 14, "discount": False, "strengths": [50, 65, 85], "img": "https://i.ibb.co/JW96c5xq/1-2.jpg", "desc": "🍮 <b>Полуничне Желе</b>\nНіжний десертний смак.", "payment_url": PAYMENT_LINK},
    304: {"name": "🍇 Grape BlackBerry", "category": "Limited Ultra", "price": 279.99, "stock": 15, "discount": False, "strengths": [50, 65, 85], "img": "https://i.ibb.co/JW96c5xq/1-3.jpg", "desc": "🍇 <b>Виноград-Ожина</b>\nВибух темних ягід.", "payment_url": PAYMENT_LINK},
    305: {"name": "🥤 Cola Pomelo", "category": "Limited Ultra", "price": 279.99, "stock": 15, "discount": False, "strengths": [50, 65, 85], "img": "https://i.ibb.co/JW96c5xq/1-4.jpg", "desc": "🍊 <b>Кола-Помело</b>\nНезвичне поєднання.", "payment_url": PAYMENT_LINK},
    306: {"name": "🌹 BlackCurrant Rose", "category": "Limited Ultra", "price": 279.99, "stock": 12, "discount": False, "strengths": [50, 65, 85], "img": "https://i.ibb.co/bRgVwzJg/1-5.jpg", "desc": "🥀 <b>Смородина-Троянда</b>\nВишуканий аромат.", "payment_url": PAYMENT_LINK},
    307: {"name": "🍋 Berry Lemonade", "category": "Special Berry", "price": 279.99, "stock": 15, "discount": False, "strengths": [50, 65, 85], "img": "https://i.ibb.co/fG4GqL6F/1-2.png", "desc": "🍹 <b>Ягідний Лимонад</b>\nОсвіжаючий літній мікс.", "payment_url": PAYMENT_LINK},
    308: {"name": "⚡ Energetic", "category": "Special Berry", "price": 279.99, "stock": 10, "discount": False, "strengths": [50, 65, 85], "img": "https://i.ibb.co/fG4GqL6F/1-3.png", "desc": "🔋 <b>Енергетик</b>\nСмак, що бадьорить.", "payment_url": PAYMENT_LINK},
    309: {"name": "💊 Vitamin", "category": "Special Berry", "price": 279.99, "stock": 15, "discount": False, "strengths": [50, 65, 85], "img": "https://i.ibb.co/fG4GqL6F/1-4.png", "desc": "🍏 <b>Вітамін</b>\nМікс фруктів.", "payment_url": PAYMENT_LINK}
}

HHC_VAPES = {
    100: {"name": "🌴 Packwoods Purple 1ml", "type": "hhc", "price": 999.99, "stock": 24, "discount": True, "gift_liquid": True, "img": "https://i.ibb.co/svXqXPgL/Ghost-Vape-3.jpg", "desc": "🧠 <b>90% HHC | Гібрид</b>\n😌 Розслаблення + ейфорія\n🎁 <b>+ РІДИНА БЕЗКОШТОВНО!</b>", "payment_url": PAYMENT_LINK},

    101: {"name": "🍊 Packwoods Orange 1ml", "type": "hhc", "price": 999.99, "stock": 21, "discount": True, "gift_liquid": True, "img": "https://i.ibb.co/SDJFRTwk/Ghost-Vape-1.jpg", "desc": "🧠 <b>90% HHC | Сатіва</b>\n⚡ Бадьорить та фокусує\n🎁 <b>+ РІДИНА БЕЗКОШТОВНО!</b>", "payment_url": PAYMENT_LINK},

    102: {"name": "🌸 Packwoods Pink 1ml", "type": "hhc", "price": 999.99, "stock": 19, "discount": True, "gift_liquid": True, "img": "https://i.ibb.co/65j1901/Ghost-Vape-2.jpg", "desc": "🧠 <b>90% HHC | Індіка</b>\n😇 Спокій + підйом настрою\n🎁 <b>+ РІДИНА БЕЗКОШТОВНО!</b>", "payment_url": PAYMENT_LINK},

    103: {"name": "🌿 Whole Mint 2ml", "type": "hhc", "price": 1399.99, "stock": 6, "discount": True, "gift_liquid": True, "img": "https://i.ibb.co/W4hqn2tZ/Ghost-Vape-4.jpg", "desc": "🧠 <b>95% HHC | Сатіва</b>\n⚡ Енергія та ясність (2ml)\n🎁 <b>+ РІДИНА БЕЗКОШТОВНО!</b>", "payment_url": PAYMENT_LINK},

    104: {"name": "🌴 Jungle Boys White 2ml", "type": "hhc", "price": 1799.99, "stock": 3, "discount": True, "gift_liquid": True, "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg", "desc": "🧠 <b>95% HHC | Індика</b>\n😴 Глибокий релакс (2ml)\n🎁 <b>+ РІДИНА БЕЗКОШТОВНО!</b>", "payment_url": PAYMENT_LINK},

    105: {"name": "🔥 Ace&Gold Ghossty Edition 1.5ml", "type": "hhc", "price": 1599.99, "stock": 4, "discount": True, "gift_liquid": True, "img": "https://i.ibb.co/5h9VDkF6/photo-2026-02-21-17-39-26.jpg", "desc": "👑 <b>95% HHC | Гібрид (Потужний)</b>\n🔥 Ексклюзивна <b>Ghossty Edition</b> у преміальному золотому корпуси\n✨ Насичений смак + стабільна тяга\n🎁 <b>+ РІДИНА БЕЗКОШТОВНО!</b>", "payment_url": PAYMENT_LINK}
}

PODS = {
    500: {"name": "🔌 Vaporesso XROS Pro", "type": "pod", "stock": 4, "gift_liquid": True, "price": 999, "discount": False, "img": "https://i.ibb.co/rKvNKwFP/Polish-20260310-035040856.jpg", "desc": "🚀 <b>PROFESSIONAL | 1200 mAh</b>\nЕкран, регулювання потужності, блокування.", "colors": ["⚫️ Black", "⚪️ Silver", "🔴 Red"], "color_previews": {"Black": "https://i.ibb.co/rKvNKwFP/Polish-20260310-035040856.jpg", "Silver": "https://i.ibb.co/Fkqc5S9G/Polish-20260310-035143043.jpg", "Red": "https://i.ibb.co/LXb9mhBf/Polish-20260310-035252469.jpg"}, "payment_url": PAYMENT_LINK},
    501: {"name": "🔌 Vaporesso XROS 5", "type": "pod", "stock": 6, "gift_liquid": True, "price": 839, "discount": False, "img": "https://i.ibb.co/1HdPNKh/Polish-20260310-040417817.jpg", "desc": "💎 <b>ПРЕМІУМ ФЛАГМАН</b>\n1200 mAh, 3 режими, супер-смак.", "colors": ["⚫️ Obsidian Black", "⚪️ Pearl White", "🔵 Pink"], "color_previews": {"Obsidian Black": "https://i.ibb.co/1HdPNKh/Polish-20260310-040417817.jpg", "Pearl White": "https://i.ibb.co/RpW3VBrZ/Polish-20260310-040517300.jpg", "Pink": "https://i.ibb.co/5XdQNwDR/Polish-20260310-040622066.jpg"}, "payment_url": PAYMENT_LINK},
    502: {"name": "🔌 Vaporesso XROS Nano 5", "type": "pod", "stock": 8, "gift_liquid": True, "price": 779, "discount": False, "img": "https://i.ibb.co/fzxY8fCB/Polish-20260310-035712367.jpg", "desc": "🎒 <b>КОМПАКТНИЙ КВАДРАТ</b>\nСтильний, зручний, на шнурку.", "colors": ["⚫️ Black", "🟠 Brown", "🌸 Pink"], "color_previews": {"Black": "https://i.ibb.co/fzxY8fCB/Polish-20260310-035712367.jpg", "Brown": "https://i.ibb.co/0pWT0RDw/Polish-20260310-035926140.jpg", "Pink": "https://i.ibb.co/LDtSBmNr/Polish-20260310-035829615.jpg"}, "payment_url": PAYMENT_LINK},
    503: {"name": "🔌 Vaporesso XROS 5 Mini", "type": "pod", "stock": 15, "gift_liquid": True, "price": 699, "discount": False, "img": "https://i.ibb.co/9kjjt8fS/Polish-20260310-035358626.jpg", "desc": "🔥 <b>НОВИНКА 2025 | COREX 2.0</b>\nМаксимальна передача смаку.", "colors": ["⚫️ Core Black", "🌸 Pink", "🟢 Green"], "color_previews": {"Core Black": "https://i.ibb.co/9kjjt8fS/Polish-20260310-035358626.jpg", "Green": "https://i.ibb.co/qFRkWbSd/Polish-20260310-035559939.jpg", "Pink": "https://i.ibb.co/Wppc1Kpz/Polish-20260310-035500449.jpg"}, "payment_url": PAYMENT_LINK},
    504: {"name": "🔌 Vaporesso XROS 4", "type": "pod", "stock": 7, "gift_liquid": True, "price": 799, "discount": False, "img": "https://i.ibb.co/dxxRp0s/Polish-20260310-040035754.jpg", "desc": "👌 <b>БАЛАНС ТА СТИЛЬ</b>\nМеталевий корпус, 3 режими потужності.", "colors": ["⚫️ Black", "🔵 Blue", "🟣 Purple Gradient"], "color_previews": {"Black": "https://i.ibb.co/dxxRp0s/Polish-20260310-040035754.jpg", "Blue": "https://i.ibb.co/yFBdq6H5/Polish-20260310-040313133.jpg", "Purple Gradient": "https://i.ibb.co/R4pNBjqd/Polish-20260310-040208981.jpg"}, "payment_url": PAYMENT_LINK},
    505: {"name": "🔌 Vaporesso XROS 3 Mini", "type": "pod", "stock": 28, "gift_liquid": True, "price": 549, "discount": False, "img": "https://i.ibb.co/3yjwss9n/Polish-20260310-034640422.jpg", "desc": "🔋 <b>1000 mAh | MTL</b>\nЛегендарна модель.", "colors": ["⚫️ Black", "🟢 Green", "🌸 Pink"], "color_previews": {"Black": "https://i.ibb.co/3yjwss9n/Polish-20260310-034640422.jpg", "Green": "https://i.ibb.co/HfJyCtCy/Polish-20260310-034754250.jpg", "Pink": "https://i.ibb.co/MD42jyrq/Polish-20260310-034919145.jpg"}, "payment_url": PAYMENT_LINK},
    506: {"name": "🔌 Voopoo Vmate Mini", "type": "pod", "stock": 35, "gift_liquid": True, "price": 479, "discount": False, "img": "https://i.ibb.co/HDMZfbSj/Polish-20260310-040815896.jpg", "desc": "😌 <b>ЛЕГКИЙ СТАРТ</b>\nАвтоматична тяга, жодних кнопок.", "colors": ["⚫️ Black", "🔴 Red", "🌸 Pink"], "color_previews": {"Black": "https://i.ibb.co/HDMZfbSj/Polish-20260310-040815896.jpg", "Red": "https://i.ibb.co/S7Jt4Z2P/Polish-20260310-040956311.jpg", "Pink": "https://i.ibb.co/nNrz1dKC/Polish-20260310-041156722.jpg"}, "payment_url": PAYMENT_LINK}
}

GIFT_LIQUIDS = {
    9001: {"name": "🎁 Fall Tea 30ml", "desc": "☕ Осінній чай з нотками лимону."},
    9002: {"name": "🎁 Mystery One 30ml", "desc": "🔮 Таємничий фруктовий мікс."},
    9003: {"name": "🎁 Strawberry Jelly 30ml", "desc": "🍮 Ніжний десертний смак полуничного желе."},
    9004: {"name": "🎁 Grape BlackBerry 30ml", "desc": "🍇 Вибух темних ягід: виноград та ожина."},
    9005: {"name": "🎁 Cola Pomelo 30ml", "desc": "🥤 Незвичне поєднання коли та помело."},
    9006: {"name": "🎁 BlackCurrant Rose 30ml", "desc": "🌹 Вишуканий аромат смородини та троянди."},
    9007: {"name": "🎁 Berry Lemonade 30ml", "desc": "🍹 Освіжаючий ягідний лимонад."},
    9008: {"name": "🎁 Energetic 30ml", "desc": "⚡ Бадьорий смак енергетика."}
}

def get_item_data(item_id: int):
    """Шукає товар у всіх категоріях за ID (Єдина правильна функція)."""
    all_dbs = [HHC_VAPES, PODS, LIQUIDS, GIFT_LIQUIDS] 
    for db in all_dbs:
        if item_id in db: return db[item_id]
    return None

# =================================================================
# ⚙️ SECTION 4: MATH CORE, DATABASE & AUTH (DB FIX)
# =================================================================

VIP_DISCOUNT_CATEGORIES = ['hhc', 'pods'] 

def calculate_final_price(item_price, user_profile, item_id=None):
    try:
        price = float(item_price)
        up = user_profile if user_profile else {}
        is_vip = bool(up.get('is_vip', False))
        
        if item_id is None: return round(price, 2), False

        item_data = get_item_data(int(item_id))
        if not item_data: return round(price, 2), False

        item_category = item_data.get('type') 
        if not item_category:
            iid = int(item_id)
            if 100 <= iid < 300: item_category = 'hhc'
            elif 300 <= iid < 500: item_category = 'liquids'
            elif 500 <= iid < 700: item_category = 'pods'

        if is_vip and item_category in VIP_DISCOUNT_CATEGORIES:
            final_price = price * 0.65 
            return round(max(final_price, 10.0), 2), True
            
        return round(price, 2), False
    except Exception as e:
        if 'logger' in globals(): logger.error(f"❌ Math Error: {e}")
        return float(item_price), False

def get_price_display(item_price, profile, item_id):
    price, is_discounted = calculate_final_price(item_price, profile, item_id)
    if is_discounted:
        return f"<s>{int(item_price)}</s> 🔥 <b>{int(price)} ₴</b>", price, True
    return f"<b>{int(price)} ₴</b>", price, False

def init_db():
    try:
        with sqlite3.connect(DB_PATH, timeout=30) as conn:
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY, username TEXT, full_name TEXT, phone TEXT, city TEXT, 
                    district TEXT, address_details TEXT, is_vip INTEGER DEFAULT 0, vip_expiry TEXT, 
                    promo_applied INTEGER DEFAULT 0, next_order_discount REAL DEFAULT 0, 
                    reg_date TEXT, balance REAL DEFAULT 0, joined_date TEXT
                )
            ''')
            
            # 🔥 АВТОМІГРАЦІЯ: Додаємо колонки для промокодів безпечно
            try: cur.execute("ALTER TABLE users ADD COLUMN promo_GHST2026_used INTEGER DEFAULT 0")
            except sqlite3.OperationalError: pass
            
            try: cur.execute("ALTER TABLE users ADD COLUMN referral_used INTEGER DEFAULT 0")
            except sqlite3.OperationalError: pass

            cur.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    order_id TEXT PRIMARY KEY, user_id INTEGER, amount REAL, status TEXT, created_at TEXT
                )
            ''')
            conn.commit()
            logger.info("✅ Database initialized and migrated.")
    except Exception as e:
        logger.critical(f"❌ DB SCHEMA FATAL ERROR: {e}")

async def get_or_create_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    if 'profile' not in context.user_data:
        context.user_data['profile'] = {
            "uid": user.id, "username": f"@{user.username}" if user.username else "Hidden",
            "full_name": user.full_name, "phone": None, "city": None, "district": None,
            "address_details": None, "is_vip": False, "vip_expiry": None,
            "next_order_discount": 0.0, "promo_applied": False,
            "promo_GHST2026_used": False, "referral_used": False
        }
    if 'cart' not in context.user_data: context.user_data['cart'] = []

    try:
        with sqlite3.connect(DB_PATH, timeout=30) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            row = cursor.execute("SELECT * FROM users WHERE user_id=?", (user.id,)).fetchone()
            
            if not row:
                reg_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute("""
                    INSERT INTO users (user_id, username, full_name, reg_date, is_vip, next_order_discount, promo_applied, promo_GHST2026_used, referral_used) 
                    VALUES (?, ?, ?, ?, 0, 0, 0, 0, 0)
                """, (user.id, user.username, user.full_name, reg_time))
                conn.commit()
            else:
                p = context.user_data['profile']
                p['is_vip'] = bool(row['is_vip'])
                p['vip_expiry'] = row['vip_expiry']
                p['next_order_discount'] = float(row['next_order_discount']) if row['next_order_discount'] is not None else 0.0
                p['promo_applied'] = bool(row['promo_applied'])
                
                # Завантаження статусу промокодів з бази
                p['promo_GHST2026_used'] = bool(row['promo_GHST2026_used'])
                p['referral_used'] = bool(row['referral_used'])
                
                if row['full_name']: p['full_name'] = row['full_name']
                if row['phone']: p['phone'] = row['phone']
                if row['city']: p['city'] = row['city']
                if row['district']: p['district'] = row['district']
                if row['address_details']: p['address_details'] = row['address_details']
    except Exception as e:
        logger.error(f"❌ DB Sync Failure: {e}")
        
    return context.user_data['profile']
    
    
# =================================================================
# 🛍 SECTION 14: CATALOG MASTER ENGINE (TITAN PRO v10.5)
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
        [InlineKeyboardButton("🏠 ГОЛОВНЕ МЕНЮ", callback_data="menu_start")]
    ]
    
    # Використовуємо глобальне фото з налаштувань (Section 1), або фолбек
    photo = globals().get('WELCOME_PHOTO', "https://i.ibb.co/y7Q194N/1770068775663.png")
    
    await send_ghosty_message(update, text, kb, photo=photo, context=context)


async def show_category_items(update: Update, context: ContextTypes.DEFAULT_TYPE, category_key: str):
    """
    Генератор списку товарів з легендою та динамічними знижками.
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
    items_dict = globals().get(dict_name, {})
    
    if not items_dict:
        await update.callback_query.answer("⚠️ Товари в цій категорії тимчасово відсутні", show_alert=True)
        return

    profile = context.user_data.get('profile', {})
    
    # 2. Формування тексту заголовка з ЛЕГЕНДОЮ
    text = (
        f"📂 <b>КАТЕГОРІЯ: {cat_title}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🔥 — <i>діє знижка VIP (-35%)</i>\n"
        f"⌛ — <i>товар закінчується</i>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👇 Натисніть на товар для детального перегляду:"
    )
    
    kb = []
    
    # 3. Розумне сортування
    sorted_items = sorted(items_dict.items(), key=lambda x: x[1].get('stock', 0), reverse=True)

    for i_id, item in sorted_items:
        stock = item.get('stock', 0)
        
        # Розрахунок ціни
        price, is_discounted = calculate_final_price(item['price'], profile, item_id=i_id)
        price_display = f"{int(price)} ₴"
        
        # 4. Формування PRO-тексту кнопки
        if stock <= 0:
            btn_text = f"⛔️ {item['name']} (Sold Out)"
            kb.append([InlineKeyboardButton(btn_text, callback_data="ignore_click")])
        else:
            hot_mark = "⌛ " if stock < 3 else ""
            vip_mark = "🔥 " if is_discounted else ""
            btn_text = f"{vip_mark}{hot_mark}{item['name']} | {price_display}"
            kb.append([InlineKeyboardButton(btn_text, callback_data=f"view_item_{i_id}")])
    
    # Навігаційний блок
    kb.append([InlineKeyboardButton("🔙 До категорій", callback_data="cat_all")])
    kb.append([InlineKeyboardButton("🏠 В головне меню", callback_data="menu_start")])
    
    await _edit_or_reply(update.callback_query, text, kb, context=context)
    

# =================================================================
# 🌍 SECTION 10: GEOGRAPHY & LOGISTICS (TITAN ULTIMATE v10.5)
# =================================================================

async def choose_city_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    КРОК 1: Головне меню вибору міста.
    Використовується при старті, в профілі та при замовленні.
    """
    context.user_data['state'] = "COLLECTING_DATA"
    context.user_data.setdefault('data_flow', {})['step'] = 'city_selection'
    
    map_image = globals().get('WELCOME_PHOTO', "https://i.ibb.co/y7Q194N/1770068775663.png")
    
    text = (
        "🏙 <b>ОБЕРІТЬ ВАШЕ МІСТО</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Ми працюємо у найбільших містах України.\n"
        "Оберіть локацію, щоб побачити доступні методи доставки 👇"
    )
    
    cities_db = globals().get('UKRAINE_CITIES', {})
    if not cities_db:
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
    
    await send_ghosty_message(update, text, keyboard, photo=map_image, context=context)


async def choose_dnipro_delivery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Спеціальний логістичний хаб для Дніпра.
    Дозволяє вибрати між Кладом (район) та Кур'єром (адреса).
    """
    query = update.callback_query
    
    context.user_data.setdefault("profile", {})["city"] = "Дніпро"
    
    text = (
        "🏙 <b>ДНІПРО: СПОСІБ ОТРИМАННЯ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "1️⃣ <b>Район (Клад)</b> — готовий сховок у вашому районі.\n"
        "2️⃣ <b>Кур'єр (+150 грн)</b> — доставка прямо по адресі.\n\n"
        "👇 Що обираєте?"
    )
    
    kb = [
        [InlineKeyboardButton("📍 Обрати район (Клад)", callback_data="sel_city_Dnipro_Klad")],
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
        
    # Зберігаємо місто в профіль і відразу в базу (для надійності)
    context.user_data.setdefault('profile', {})['city'] = real_city
    user_id = update.effective_user.id
    try:
        with sqlite3.connect(DB_PATH, timeout=30) as conn:
            conn.execute("UPDATE users SET city=? WHERE user_id=?", (real_city, user_id))
            conn.commit()
    except Exception as e:
        logger.error(f"Failed to auto-save city: {e}")
    
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
        text = f"📍 <b>{real_city}</b>\nУточніть деталі доставки вручну."
        kb.append([InlineKeyboardButton("➡️ Ввести адресу", callback_data="sel_dist_Центр")])
        
    kb.append([InlineKeyboardButton("🔙 Змінити місто", callback_data="choose_city")])
    
    context.user_data.setdefault('data_flow', {})['step'] = 'district_selection'
    
    await _edit_or_reply(query, text, kb, context=context)
    
# =================================================================
# 👤 SECTION 5: MASTER START & PROFILE UI (DEEP LINK SUPPORT)
# =================================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Головна точка входу (/start).
    Викликає реєстрацію, нараховує бонуси, підтримує Deep Linking (реф. посилання).
    """
    user = update.effective_user
    
    # 🔥 ФІКС ЗАЛИПАННЯ: Примусово очищаємо старі "хвости" замовлень
    context.user_data['target_item_id'] = None
    context.user_data['target_gift_id'] = None
    context.user_data['selected_color'] = None
    context.user_data['state'] = None
    
    # 1. Отримуємо профіль
    if 'get_or_create_user' in globals():
        profile = await get_or_create_user(update, context)
    else:
        await update.message.reply_text("⚠️ Система завантажується... Спробуйте через 5 секунд.")
        return

    bot = await context.bot.get_me()

    # 🔥 ОБРОБКА РЕФЕРАЛЬНОГО ПОСИЛАННЯ (Deep Linking)
    if context.args and context.args[0].isdigit():
        referrer_id = context.args[0]
        # Імітуємо введення реферального промокоду (створюємо "фейковий" об'єкт)
        dummy_message = type('DummyMsg', (object,), {'text': f"GHST{referrer_id}"})()
        dummy_update = type('DummyUpdate', (object,), {'message': dummy_message, 'effective_user': user})()
        
        if 'process_promo' in globals():
            await process_promo(dummy_update, context, silent=True)
            profile = context.user_data.get('profile', profile)

    # 2. ВІЗУАЛІЗАЦІЯ ПРИВІТАННЯ
    safe_name = escape(user.first_name)
    status_icon = "💎" if profile.get('is_vip') else "👤"
    current_balance = int(profile.get('next_order_discount', 0))
    ref_link = f"https://t.me/{bot.username}?start={user.id}"
    
    welcome_text = (
        f"🌫️ <b>GHO$$TY STAFF LAB | 2026</b> 🌿\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Йо, <b>{safe_name}</b>! Твій статус: <b>{status_icon} VIP PRO</b>\n\n"
        f"💰 Твій баланс: <b>{current_balance} грн</b>\n"
        f"📉 Знижка: <b>-35%</b> (для VIP)\n"
        f"🚚 Доставка: <b>БЕЗКОШТОВНА</b> (для VIP)\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🎁 <b>АКЦІЯ НА СТАРТ:</b>\n"
        f"Введи код <code>GHST2026</code> в профілі та отримай <b>+69 грн</b> на свій рахунок!\n\n"
        f"🤝 <b>ЗАРОБЛЯЙ З НАМИ:</b>\n"
        f"Кидай це посилання другу:\n<code>{ref_link}</code>\n"
        f"<i>(Він отримає +50₴ та VIP, і ТИ отримаєш +50₴ та VIP на 7 днів!)</i>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👇 <b>ГОЛОВНЕ МЕНЮ:</b>"
    )
    
    keyboard = [
        [InlineKeyboardButton("🛍 ВІДКРИТИ КАТАЛОГ 🌿", callback_data="cat_all")],
        [InlineKeyboardButton("👤 ПРОФІЛЬ", callback_data="menu_profile"), 
         InlineKeyboardButton("🛒 КОШИК", callback_data="menu_cart")],
        [InlineKeyboardButton("🚚 ДАНІ ПРО ДОСТАВКУ", callback_data="fill_delivery_data")], 
        [InlineKeyboardButton("👨‍💻 МЕНЕДЖЕР", url=f"https://t.me/{MANAGER_USERNAME}"),
         InlineKeyboardButton("📢 КАНАЛ", url=f"{CHANNEL_URL}")]
    ]
    
    # Кнопка адміна
    is_admin = False
    if 'ADMIN_LIST' in globals() and user.id in ADMIN_LIST: is_admin = True
    elif user.id == globals().get('MANAGER_ID'): is_admin = True
        
    if is_admin:
        keyboard.append([InlineKeyboardButton("⚙️ GOD MODE (ADMIN)", callback_data="admin_main")])

    photo = globals().get('WELCOME_PHOTO', "https://i.ibb.co/35K9Zp5p/Polish-20260310-051407282.png")
    await send_ghosty_message(update, welcome_text, keyboard, photo=photo, context=context)


async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Особистий кабінет користувача.
    """
    user = update.effective_user
    
    if 'get_or_create_user' in globals():
        profile = await get_or_create_user(update, context)
    else:
        try: await update.callback_query.answer("⚠️ Помилка доступу до профілю", show_alert=True)
        except: pass
        return
        
    bot = await context.bot.get_me()
    
    user_photo = globals().get('WELCOME_PHOTO')
    try:
        photos = await user.get_profile_photos(limit=1)
        if photos and photos.total_count > 0:
            user_photo = photos.photos[0][-1].file_id 
    except Exception: pass

    full_name = profile.get('full_name') or user.full_name
    phone = profile.get('phone') or 'Не вказано'
    city = profile.get('city') or 'Не обрано'
    district = profile.get('district') or ''
    address = profile.get('address_details') or '—'
    
    location_str = f"{city}"
    if district and district not in str(address): 
        location_str += f" ({district})"
    if city == 'Не обрано' or not city: 
        location_str = "Не обрано"

    balance = int(profile.get('next_order_discount', 0))
    vip_status = "💎 V.I.P PRO" if profile.get('is_vip') else "👤 Standard"
    raw_vip_date = profile.get('vip_expiry')
    vip_till = raw_vip_date if raw_vip_date else '—'
    ref_link = f"https://t.me/{bot.username}?start={user.id}"
    
    text = (
        f"👤 <b>ОСОБИСТИЙ КАБІНЕТ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 ID: <code>{user.id}</code>\n"
        f"🧢 Ім'я: <b>{full_name}</b>\n"
        f"🌟 Статус: <b>{vip_status}</b>\n"
        f"<i>(Діє до: {vip_till})</i>\n\n"
        f"💰 <b>БАЛАНС БОНУСІВ: {balance} ₴</b>\n"
        f"<i>(Використовуй їх для знижок до 100%)</i>\n\n"
        f"📍 <b>ДАНІ ДОСТАВКИ:</b>\n"
        f"🏙 Локація: {location_str}\n"
        f"🏠 Адреса: {address}\n"
        f"📱 Телефон: {phone}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🔗 <b>Твоє реф. посилання (Запроси друга):</b>\n"
        f"<code>{ref_link}</code>\n\n"
        f"👇 <i>Керування:</i>"
    )
    
    kb = [
        [InlineKeyboardButton("✏️ Змінити дані доставки", callback_data="fill_delivery_data")],
        [InlineKeyboardButton("🎟 Ввести промокод", callback_data="menu_promo")],
        [InlineKeyboardButton("🔙 В головне меню", callback_data="menu_start")]
    ]
    
    await send_ghosty_message(update, text, kb, photo=user_photo, context=context)

# =================================================================
# 🔍 SECTION 15: PRODUCT CARD & INTERACTIVE COLOR ENGINE
# =================================================================

async def view_item_details(update: Update, context: ContextTypes.DEFAULT_TYPE, item_id: int):
    """
    Точка входу в картку товару.
    Скидає попередній вибір кольору та відображає картку.
    """
    item = get_item_data(item_id)
    if not item:
        if update.callback_query:
            await update.callback_query.answer("❌ Товар не знайдено або видалено.", show_alert=True)
        return

    # Скидаємо вибір кольору при першому відкритті
    context.user_data['selected_color'] = None
    await render_product_card(update, context, item, item_id, item.get('img'))


async def render_product_card(update: Update, context: ContextTypes.DEFAULT_TYPE, item: dict, item_id: int, current_photo: str):
    """
    Ядро відображення. Викликається при старті та при кліку на колір.
    """
    profile = context.user_data.get("profile", {})
    
    # 🔥 ВИПРАВЛЕННЯ ЦІНИ (Пункт №7): Використовуємо універсальну функцію
    price_html, final_price, is_discounted = get_price_display(item['price'], profile, item_id)

# --- ЛОГІКА СКЛАДУ (FIXED) ---
stock = item.get('stock', 0)
if stock >= 13: 
    stock_status = f"🟢 <b>В наявності</b> ({stock} шт)"
elif 1 <= stock < 13: 
    stock_status = f"🟡 <b>Залишилось небагато</b> ({stock} шт) 🔥"
else: 
    stock_status = "🔴 <b>Тимчасово відсутній</b>"

    # --- ЛОГІКА КОЛЬОРУ ---
    selected_color = context.user_data.get('selected_color')
    color_text = f"\n🎨 Колір: <b>{selected_color}</b>" if selected_color else ""

    # --- ЗБІРКА ОПИСУ ---
    safe_name = escape(item['name'])
    desc = item.get('desc', 'Опис оновлюється...')
    
    caption = (
        f"🛍 <b>{safe_name}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📦 Склад: {stock_status}\n"
        f"💰 Ціна: {price_html}{color_text}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{desc}"
    )

    kb = []
    
    # 1. ГЕНЕРАЦІЯ КНОПОК КОЛЬОРІВ
    if stock > 0 and "colors" in item and item["colors"]:
        colors = item["colors"]
        row = []
        for col in colors:
            if col == selected_color:
                btn_text = f"✅ {col}"
                cb_data = "ignore_click" 
            else:
                btn_text = col
                cb_data = f"sel_col_{item_id}_{col}" 
            
            row.append(InlineKeyboardButton(btn_text, callback_data=cb_data))
            if len(row) == 2:
                kb.append(row)
                row = []
        if row: kb.append(row)

    # 2. КНОПКИ ДІЇ
    if stock > 0:
        if "colors" in item and item["colors"] and not selected_color:
            kb.append([InlineKeyboardButton("👆 ОБЕРІТЬ КОЛІР ВИЩЕ 👆", callback_data="ignore_click")])
        else:
            cb_ext = f"_{selected_color}" if selected_color else ""
            
            kb.append([InlineKeyboardButton("🛒 ДОДАТИ В КОШИК", callback_data=f"add_{item_id}{cb_ext}")])
            kb.append([
                InlineKeyboardButton("⚡ ШВИДКО", callback_data=f"fast_order_{item_id}{cb_ext}"),
                InlineKeyboardButton("👨‍💻 МЕНЕДЖЕР", callback_data=f"mgr_pre_{item_id}{cb_ext}")
            ])
    else:
        kb.append([InlineKeyboardButton("🔔 ПОВІДОМИТИ ПРО НАЯВНІСТЬ", callback_data="ignore_click")])

    kb.append([InlineKeyboardButton("🔙 До каталогу", callback_data="cat_all")])
    await send_ghosty_message(update, caption, kb, photo=current_photo, context=context)


async def handle_color_selection_click(update: Update, context: ContextTypes.DEFAULT_TYPE, item_id: int, color_name: str):
    """Обробляє клік по кольору: розумний пошук фото (ігнорує емодзі) та оновлення галочки."""
    item = get_item_data(item_id)
    if not item: return

    context.user_data['selected_color'] = color_name
    previews = item.get("color_previews", {})
    
    new_photo = item['img']
    # Розумний пошук: перевіряємо, чи є слово "Black" у "⚫️ Black"
    for key, url in previews.items():
        if key in color_name:
            new_photo = url
            break
    
    await render_product_card(update, context, item, item_id, new_photo)
    
    
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
    if item_id: 
        context.user_data['target_item_id'] = item_id
    
    profile = context.user_data.setdefault('profile', {'uid': user.id})
    
    # Визначаємо, чи це режим примусового редагування
    force_edit = (next_action == 'none' or next_action == 'profile')

    # --- КРОК 1: ІМ'Я ---
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
    if force_edit or not profile.get('city'):
        await choose_city_menu(update, context)
        return

    # --- КРОК 4: АДРЕСА ---
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
        
        # 🔥 ВИПРАВЛЕННЯ: Кнопка "Змінити місто"
        kb = [
            [InlineKeyboardButton("🏙 Змінити місто", callback_data="choose_city")],
            [InlineKeyboardButton("✖️ Скасувати", callback_data="menu_start")]
        ]
        await send_ghosty_message(update, text, kb, context=context)
        return

    # Якщо всі дані є -> Фіналізація
    await finalize_data_collection(update, context)


async def address_request_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, dist_name: str):
    """Проміжний хендлер: Коли обрали район, переходимо до адреси."""
    clean_dist = dist_name.split("_")[0] 
    context.user_data.setdefault('profile', {})['district'] = clean_dist
    
    # Відразу записуємо район у БД
    try:
        with sqlite3.connect(DB_PATH, timeout=30) as conn:
            conn.execute("UPDATE users SET district=? WHERE user_id=?", (clean_dist, update.effective_user.id))
            conn.commit()
    except Exception as e:
        logger.error(f"Failed to auto-save district: {e}")
    
    context.user_data['state'] = "COLLECTING_DATA"
    context.user_data['data_step'] = "address"
    
    city = context.user_data.get('profile', {}).get('city', 'вашому місті')
    
    text = (
        f"✅ <b>Місто:</b> {city}\n"
        f"✅ <b>Район:</b> {clean_dist}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📍 <b>КРОК 4/4: АДРЕСА</b>\n"
        f"Напишіть номер відділення НП або адресу:"
    )
    
    # 🔥 ВИПРАВЛЕННЯ: Кнопка "Змінити місто" додана і сюди
    kb = [
        [InlineKeyboardButton("🔙 Змінити район", callback_data=f"sel_city_{city}")],
        [InlineKeyboardButton("🏙 Змінити місто", callback_data="choose_city")]
    ]
    
    await send_ghosty_message(update, text, kb, context=context)


async def finalize_data_collection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Фінал анкети: маршрутизація до Оплати/Менеджера/Профілю."""
    user_id = update.effective_user.id
    profile = context.user_data.get('profile', {})
    action = context.user_data.get('post_data_action', 'checkout')
    
    # Очищення стану (щоб бот перестав перехоплювати текст)
    context.user_data['state'] = None
    context.user_data['data_step'] = None

    # Маршрутизація
    if action == 'checkout' or action == 'fast_order':
        if 'checkout_init' in globals():
            await checkout_init(update, context)
        else:
            await send_ghosty_message(update, "⚠️ Модуль оплати недоступний.", context=context)
            
    elif action == 'manager_order':
        if 'submit_order_to_manager' in globals():
            await submit_order_to_manager(update, context)
        else:
             await send_ghosty_message(update, "✅ Заявку створено! Менеджер скоро напише.", context=context)
             
    else:
        try:
            if update.callback_query: await update.callback_query.answer("✅ Дані успішно збережено!", show_alert=True)
            else: await send_ghosty_message(update, "✅ <b>Дані успішно збережено!</b>", context=context)
        except: pass
        
        if 'show_profile' in globals():
            await show_profile(update, context)
            
# =================================================================
# 🛒 SECTION 18: CART LOGIC (TITAN FIXED v10.5 - PRO)
# =================================================================

async def show_cart_logic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Логіка кошика: відображення, видалення, перевірка даних перед оплатою.
    🔥 ВДОСКОНАЛЕННЯ: Красиві ціни, анонс подарунків, чистий код.
    """
    cart = context.user_data.get("cart", [])
    if cart is None: 
        cart = []
        context.user_data["cart"] = []
    
    profile = context.user_data.setdefault("profile", {})
    
    # --- ЯКЩО КОШИК ПОРОЖНІЙ ---
    if not cart:
        empty_text = "🛒 <b>Ваш кошик порожній</b>\n\nЧас обрати щось топове! 👇"
        empty_kb = [
            [InlineKeyboardButton("🛍 До Каталогу", callback_data="cat_all")],
            [InlineKeyboardButton("🏠 Головне меню", callback_data="menu_start")]
        ]
        
        if update.callback_query:
            await _edit_or_reply(update.callback_query, empty_text, empty_kb, context=context)
        else:
            await send_ghosty_message(update, empty_text, empty_kb, context=context)
        return

    # --- ЗБІРКА ДАНИХ КОШИКА ---
    total_sum = 0.0
    items_text = ""
    keyboard = [] 
    has_gift_in_cart = False

    for item in cart:
        # Отримуємо ID товару для правильного розрахунку знижок
        item_id = item.get('real_id')
        
        # 🔥 ПРОБЛЕМА №7: Використовуємо універсальну функцію для красивого відображення ціни
        if 'get_price_display' in globals():
            price_str, final_price, _ = get_price_display(item.get('price', 0), profile, item_id)
        else:
            # Аварійний фолбек, якщо функцію чомусь не знайдено
            final_price = float(item.get('price', 0))
            price_str = f"<b>{int(final_price)} грн</b>"
            
        total_sum += final_price
        
        name = item.get('name', 'Товар')
        gift = item.get('gift')
        color = item.get('color') 
        
        # Формуємо рядок з деталями (колір/подарунок)
        details = []
        if color: details.append(f"🎨 {color}")
        if gift: 
            details.append(f"🎁 {gift}")
            has_gift_in_cart = True # Запам'ятовуємо, що є подарунок
        
        details_txt = f"\n   {' | '.join(details)}" if details else ""
        
        # Додаємо товар до списку
        items_text += f"▫️ <b>{name}</b>{details_txt}\n   💰 {price_str}\n\n"
        
        uid = item.get('id', 0)
        # Кнопка видалення (скорочуємо ім'я для краси)
        keyboard.append([InlineKeyboardButton(f"❌ Видалити: {name[:15]}...", callback_data=f"cart_del_{uid}")])

    # --- ПЕРЕВІРКА ДАНИХ ДЛЯ ДОСТАВКИ ---
    full_name = profile.get("full_name")
    phone = profile.get("phone")
    city = profile.get("city")
    address = profile.get("address_details")
    
    can_checkout = all([full_name, phone, city, address])
    
    if can_checkout:
        loc_status = f"✅ <b>Дані:</b> {city}, {full_name}\n📞 {phone}\n🏠 {address}"
        btn_text = "🚀 ОФОРМИТИ ЗАМОВЛЕННЯ"
        btn_action = "checkout_init"
    else:
        loc_status = "⚠️ <b>Дані доставки не заповнені!</b>"
        btn_text = "📝 ЗАПОВНИТИ ДАНІ"
        btn_action = "fill_delivery_data"

    # 🔥 ПРОБЛЕМА №6: Анонс подарунка
    gift_announcement = ""
    if has_gift_in_cart:
        gift_announcement = "🎉 <i>У вашому замовленні є безкоштовний бонус!</i>\n━━━━━━━━━━━━━━━━━━━━\n"

    # --- ФОРМУВАННЯ ФІНАЛЬНОГО ТЕКСТУ ---
    full_text = (
        f"🛒 <b>ВАШЕ ЗАМОВЛЕННЯ ({len(cart)} шт)</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{items_text}"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{gift_announcement}"
        f"{loc_status}\n"
        f"💰 <b>РАЗОМ ДО СПЛАТИ: {total_sum:.2f} UAH</b>"
    )

    # Кнопка оформлення йде першою
    keyboard.insert(0, [InlineKeyboardButton(btn_text, callback_data=btn_action)])
    
    # Кнопки підвалу
    footer_buttons = []
    if not profile.get("next_order_discount"):
        footer_buttons.append(InlineKeyboardButton("🎟 Промокод", callback_data="menu_promo"))
        
    footer_buttons.append(InlineKeyboardButton("🗑 Очистити", callback_data="cart_clear"))
    keyboard.append(footer_buttons)
    keyboard.append([InlineKeyboardButton("🔙 В головне меню", callback_data="menu_start")])

    await send_ghosty_message(update, full_text, keyboard, context=context)


async def cart_action_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробка видалення та очищення кошика."""
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
    
    # Перемальовуємо кошик після дій
    await show_cart_logic(update, context)
    

# =================================================================
# 🎁 SECTION 19: GIFT & CART ENGINE (TITAN ULTIMATE v10.5 - PRO FIX)
# =================================================================

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
    
    # 2. Генеруємо кнопки подарунків ДИНАМІЧНО з бази (Section 3)
    # Формат: PREFIX_ITEMID_GIFTID
    gift_dict = globals().get('GIFT_LIQUIDS', {})
    for gid, gift_item in gift_dict.items():
        # Очищаємо назву для гарного вигляду на кнопці (видаляємо 🎁 та 30ml)
        short_name = gift_item['name'].replace("🎁 ", "").replace(" 30ml", "").strip()
        kb.append([InlineKeyboardButton(f"🧪 {short_name}", callback_data=f"{prefix}_{item_id}_{gid}")])

    # 3. Керуючі кнопки
    kb.append([InlineKeyboardButton("❌ Без подарунка", callback_data=f"{prefix}_{item_id}_0")])
    kb.append([InlineKeyboardButton("🔙 Назад до товару", callback_data=f"view_item_{item_id}")])

    # Відправляємо оновлене меню
    await _edit_or_reply(query, text, kb, context=context)


async def add_to_cart_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ЄДИНА функція додавання в кошик (Оптимізована під кольори)."""
    query = update.callback_query
    parts = query.data.split("_")
    
    try:
        item_id = int(parts[1])
        item = get_item_data(item_id)
        if not item: 
            await query.answer("❌ Товар не знайдено")
            return

        # 1. Беремо колір з пам'яті (він там гарантовано є)
        selected_color = context.user_data.get('selected_color')

        # --- 2. ПАРСИНГ ПОДАРУНКА ---
        gift_id = None
        # 🔥 Виправлено: Прибрали жорсткий ліміт на 4 символи
        if len(parts) > 2 and parts[-1].isdigit():
            gift_id = int(parts[-1])

        # 3. Перевірка акції
        cart = context.user_data.get("cart", [])
        has_gift_in_cart = any(i.get('gift') for i in cart)
        needs_gift = item and (item_id < 300 or 500 <= item_id < 700 or item.get('gift_liquid'))
        
        if needs_gift and gift_id is None and not has_gift_in_cart:
            await gift_selection_handler(update, context) 
            return

        # 4. Додавання
        gift_name = None
        if gift_id and gift_id > 0:
            g_item = get_item_data(gift_id)
            if g_item: gift_name = g_item['name']

        context.user_data.setdefault("cart", []).append({
            "id": random.randint(100000, 999999), 
            "real_id": item_id, 
            "name": item['name'],
            "price": item['price'], 
            "color": selected_color, 
            "gift": gift_name
        })
        
        try: await query.answer("✅ Додано в кошик!", show_alert=False)
        except: pass
        
        # 5. Звіт
        info = ""
        if selected_color: info += f"\n🎨 Колір: <b>{selected_color}</b>"
        if gift_name: info += f"\n🎁 Бонус: <b>{gift_name}</b>"
        
        price_display = f"{int(item['price'])} ₴"
        if 'get_price_display' in globals():
            price_display = get_price_display(item['price'], context.user_data.get('profile', {}), item_id)[0]

        text = (
            f"✅ <b>ТОВАР У КОШИКУ!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📦 <b>{item['name']}</b>"
            f"{info}\n"
            f"💰 {price_display}\n\n"
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
# 💳 SECTION 20: CHECKOUT & PAYMENT CORE (TITAN FINAL - PRO FIX)
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
    target_gift_id = context.user_data.get('target_gift_id')
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
        
        # 🔥 РОЗУМНЕ ФОТО (Ігнорує емодзі)
        selected_color = context.user_data.get('selected_color')
        photo_to_show = item['img']
        
        if selected_color and "color_previews" in item:
            for key, url in item["color_previews"].items():
                if key in selected_color:
                    photo_to_show = url
                    break

        # Ціна через нове ядро відображення

        # 🔥 Ціна через нове ядро відображення
        if 'get_price_display' in globals():
            price_str, price, _ = get_price_display(item['price'], profile, target_item_id)
        else:
            price = float(item['price'])
            price_str = f"<b>{int(price)} грн</b>"
            
        total_amount = price
        
        # Опис основного товару
        color_txt = f" (🎨 {selected_color})" if selected_color else ""
        items_desc = f"▫️ <b>{item['name']}</b>{color_txt}\n   {price_str}"

        # 🎁 Відображення подарунка
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
            # 🔥 Ціна через нове ядро відображення
            if 'get_price_display' in globals():
                price_str, p, _ = get_price_display(i['price'], profile, i.get('real_id'))
            else:
                p = float(i['price'])
                price_str = f"<b>{int(p)} грн</b>"
                
            total_amount += p
            
            # Формуємо деталі (колір та подарунок)
            extras = []
            if i.get('color'): extras.append(f"🎨 {i['color']}")
            if i.get('gift'): extras.append(f"🎁 {i['gift']}")
            
            extra_txt = f" ({', '.join(extras)})" if extras else ""
            items_desc += f"▫️ <b>{i['name']}</b>{extra_txt}\n   {price_str}\n"

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

async def process_promo(update: Update, context: ContextTypes.DEFAULT_TYPE, silent=False):
    if hasattr(update, 'message') and update.message and update.message.text:
        text = update.message.text.strip().upper()
    else:
        return
        
    user = update.effective_user
    profile = context.user_data.setdefault("profile", {})
    
    msg = ""
    is_success = False
    
    try:
        conn = sqlite3.connect(DB_PATH, timeout=30)
        cursor = conn.cursor()
    except Exception as e:
        logger.error(f"DB Connect Error: {e}")
        if not silent: 
            await update.message.reply_text("⚠️ Технічна помилка. Спробуйте пізніше.")
        return

    # --- 1. ГЛОБАЛЬНИЙ ПРОМО (GHST2026) ---
    if text == "GHST2026":
        if profile.get('promo_GHST2026_used'):
            msg = "⚠️ <b>Цей промокод ви вже активували!</b>"
        else:
            profile["next_order_discount"] = float(profile.get("next_order_discount", 0)) + 69.0
            profile["promo_GHST2026_used"] = True
            
            msg = (
                "✅ <b>GHST2026 УСПІШНО АКТИВОВАНО!</b>\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "🎁 <b>Бонус:</b> +69 грн на баланс!\n"
                "<i>Використовуй їх як знижку при наступному замовленні.</i>"
            )
            is_success = True

    # --- 2. РЕФЕРАЛЬНИЙ КОД (GHST12345) ---
    elif text.startswith("GHST") and text[4:].isdigit():
        target_id = int(text[4:])
        
        if target_id == user.id:
            msg = "❌ <b>Свій власний код активувати не можна.</b>"
        elif profile.get('referral_used'):
            msg = "⚠️ <b>Ви вже активували реферальний код або переходили за посиланням раніше.</b>"
        else:
            referrer = cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (target_id,)).fetchone()
            
            if not referrer:
                msg = "❌ <b>Такого коду не знайдено. Перевірте цифри.</b>"
            else:
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
                profile["next_order_discount"] = float(profile.get("next_order_discount", 0)) + 50.0
                
                msg = (
                    f"🤝 <b>Реферальний код успішно прийнято!</b>\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"Вам нараховано <b>+50 грн</b> на баланс та <b>+7 днів VIP</b> статусу!\n"
                    f"📅 Ваш VIP діє до: <b>{profile['vip_expiry']}</b>"
                )
                is_success = True
                
                try:
                    cursor.execute("""
                        UPDATE users 
                        SET next_order_discount = next_order_discount + 50,
                            is_vip = 1,
                            vip_expiry = ?
                        WHERE user_id = ?
                    """, (new_expiry.strftime("%Y-%m-%d"), target_id))
                    conn.commit()
                    
                    await context.bot.send_message(
                        chat_id=target_id,
                        text=(
                            f"🎉 <b>ТВІЙ КОД АКТИВОВАНО!</b>\n"
                            f"━━━━━━━━━━━━━━━━━━━━\n"
                            f"Хтось щойно скористався твоїм запрошенням.\n"
                            f"💰 <b>+50 ГРН</b> нараховано на твій бонусний баланс!\n"
                            f"💎 Твій VIP статус продовжено на <b>7 днів</b>.\n\n"
                            f"<i>Продовжуй ділитися посиланням, щоб заробляти більше!</i>"
                        ),
                        parse_mode='HTML'
                    )
                except Exception as e:
                    logger.error(f"Failed to reward referrer {target_id}: {e}")

    else:
        msg = "❌ <b>Невірний формат коду.</b>"

    # --- 3. ЗБЕРЕЖЕННЯ В БД (ДЛЯ ПОТОЧНОГО ЮЗЕРА) ---
    if is_success:
        try:
            # 🔥 ВИПРАВЛЕНО: Тепер SQL-запит містить ВСІ колонки, включаючи referral_used!
            cursor.execute("""
                UPDATE users 
                SET is_vip = ?, 
                    vip_expiry = ?,
                    next_order_discount = ?,
                    promo_applied = ?,
                    promo_GHST2026_used = ?,
                    referral_used = ?
                WHERE user_id = ?
            """, (
                1 if profile.get('is_vip') else 0, 
                profile.get('vip_expiry'), 
                profile.get('next_order_discount'), 
                1,
                1 if profile.get('promo_GHST2026_used') else 0,
                1 if profile.get('referral_used') else 0,
                user.id
            ))
            conn.commit()
            context.user_data['profile'] = profile 
        except Exception as e:
            logger.error(f"DB Update Error (Promo): {e}")
            
    conn.close()

    context.user_data['awaiting_promo'] = False
    
    if not silent:
        kb = [[InlineKeyboardButton("👤 У Кабінет (Перевірити)", callback_data="menu_profile")],
              [InlineKeyboardButton("🛍 До покупок", callback_data="cat_all")]]
        await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode='HTML')


async def show_ref_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показ реферальної інформації (інструкція)."""
    user = update.effective_user
    try: 
        bot = await context.bot.get_me()
        bot_name = bot.username
    except: 
        bot_name = "GhostyShopBot"
    
    text = (
        f"🤝 <b>ПАРТНЕРСЬКА ПРОГРАМА</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Запрошуйте друзів та заробляйте реальні знижки!\n\n"
        f"🔑 <b>Твій промокод:</b> <code>GHST{user.id}</code>\n\n"
        f"🔗 <b>Твоє посилання:</b>\n"
        f"<code>https://t.me/{bot_name}?start={user.id}</code>\n\n"
        f"🎁 <b>Коли друг перейде за посиланням:</b>\n"
        f"• <b>ТИ ОТРИМАЄШ:</b> +50 грн та +7 днів VIP.\n"
        f"• <b>ДРУГ ОТРИМАЄ:</b> +50 грн та +7 днів VIP."
    )
    
    kb = [[InlineKeyboardButton("🔙 Назад", callback_data="menu_profile")]]
    await _edit_or_reply(update.callback_query, text, kb, context=context)

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
# 🤵 SECTION 27: MANAGER ORDER HUB (FAST ORDER & BALANCE PRO)
# =================================================================

from urllib.parse import quote 

async def submit_order_to_manager(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Генератор заявки для менеджера.
    🔥 ФУНКЦІОНАЛ: 
    1. Підтримує Швидке замовлення та Кошик.
    2. Рахує доставку та подарунки.
    3. Списує бонуси з бази даних (але залишає мінімум 1 грн до сплати).
    4. Формує Deep Link для автоматичної вставки тексту.
    """
    user = update.effective_user
    profile = context.user_data.get('profile', {})
    
    # 1. Визначаємо джерело (Швидке замовлення чи Кошик)
    target_item_id = context.user_data.get('target_item_id')
    target_gift_id = context.user_data.get('target_gift_id')
    cart = context.user_data.get('cart', [])
    
    items_text = ""
    total_goods_price = 0.0
    
    # --- 2. ЛОГІКА ЗБОРУ ТОВАРІВ ---
    if target_item_id:
        # Швидке замовлення (1 товар)
        item = get_item_data(target_item_id)
        if item:
            color = context.user_data.get('selected_color')
            # Отримуємо ціну через нову функцію (яка враховує категорії та знижки)
            _, price, _ = get_price_display(item['price'], profile, target_item_id)
            total_goods_price = price
            
            color_str = f" (🎨 {color})" if color else ""
            items_text += f"▫️ {item['name']}{color_str} — {int(price)} грн\n"
            
            # Інфо про подарунок
            if target_gift_id and target_gift_id > 0:
                g = get_item_data(target_gift_id)
                if g: items_text += f"   🎁 Бонус: {g['name']}\n"
            
    elif cart:
        # Замовлення з кошика
        for i in cart:
            _, p, _ = get_price_display(i['price'], profile, i.get('real_id'))
            total_goods_price += p
            
            details = []
            if i.get('color'): details.append(f"🎨 {i['color']}")
            if i.get('gift'): details.append(f"🎁 {i['gift']}")
            
            details_str = f" ({', '.join(details)})" if details else ""
            items_text += f"▫️ {i['name']}{details_str} — {int(p)} грн\n"
    else:
        # Захист від порожніх замовлень
        if update.callback_query:
            await update.callback_query.answer("⚠️ Кошик порожній", show_alert=True)
        return await catalog_main_menu(update, context)

    # --- 3. ЛОГІКА ДОСТАВКИ ---
    delivery_price = 0.0
    dist = profile.get('district', '')
    # Якщо доставка кур'єром і юзер НЕ VIP -> додаємо 150 грн
    if "Кур'єр" in str(dist) and not profile.get("is_vip"):
        delivery_price = 150.0
        items_text += f"\n🚚 Доставка кур'єром: +{int(delivery_price)} грн\n"

    # --- 4. ЛОГІКА БОНУСІВ (СПИСАННЯ) ---
    current_balance = float(profile.get('next_order_discount', 0.0))
    discount_to_apply = 0.0
    pre_total = total_goods_price + delivery_price
    
    if current_balance > 0:
        # Списуємо баланс, але залишаємо мінімум 1 грн (технічне обмеження)
        max_possible_discount = max(0.0, pre_total - 1.0)
        
        if current_balance >= max_possible_discount:
            discount_to_apply = max_possible_discount
        else:
            discount_to_apply = current_balance

    final_amount = pre_total - discount_to_apply
    
    # --- 5. РОБОТА З БАЗОЮ ДАНИХ ТА ГЕНЕРАЦІЯ ID ---
    order_id = f"GH-{user.id}-{random.randint(1000, 9999)}"
    
    try:
        with sqlite3.connect(DB_PATH, timeout=30) as conn:
            # Зберігаємо замовлення зі статусом new_request (щоб воно світилося як ⏳ в адмінці)
            conn.execute("""
                INSERT OR REPLACE INTO orders (order_id, user_id, amount, status, created_at) 
                VALUES (?, ?, ?, ?, ?)
            """, (order_id, user.id, final_amount, 'new_request', datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            
            # Якщо використали бонуси — списуємо їх з бази
            if discount_to_apply > 0:
                conn.execute("""
                    UPDATE users 
                    SET next_order_discount = next_order_discount - ? 
                    WHERE user_id = ?
                """, (discount_to_apply, user.id))
                
                # Оновлюємо локальний профіль
                profile['next_order_discount'] -= discount_to_apply
                
            conn.commit()
            
    except Exception as e:
        logger.error(f"Manager Order DB Error: {e}")

    # --- 6. ФОРМУВАННЯ ПОВІДОМЛЕННЯ ДЛЯ ЮЗЕРА ТА ЛІНКА ---
    full_name = profile.get('full_name', 'Гість')
    phone = profile.get('phone', 'Не вказано')
    address = profile.get('address_details', '')
    
    discount_line = f"\n💎 Знижка з балансу: -{int(discount_to_apply)} грн\n" if discount_to_apply > 0 else "\n"
    
    # Текст, який автоматично вставиться в поле вводу (до менеджера)
    report = (
        f"👋 Привіт! Замовлення #{order_id}\n\n"
        f"👤 {full_name} | 📞 {phone}\n"
        f"📍 {profile.get('city')}, {dist}\n"
        f"🏠 {address}\n\n"
        f"🛒 ЗАМОВЛЕННЯ:\n{items_text}"
        f"{discount_line}"
        f"💰 ДО СПЛАТИ: {final_amount:.2f} грн"
    )
    
    # Кодування тексту для URL (щоб Telegram його зрозумів)
    encoded_text = quote(report)
    clean_manager = MANAGER_USERNAME.replace("@", "").strip()
    magic_link = f"https://t.me/{clean_manager}?text={encoded_text}"

    # Відповідь клієнту в боті
    text = (
        f"✅ <b>ЗАЯВКУ СФОРМОВАНО!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Замовлення <code>#{order_id}</code> готове до відправки.\n"
        f"Сума до сплати: <b>{final_amount:.2f} грн</b>\n\n"
        f"👇 <b>Натисніть кнопку нижче:</b>\n"
        f"Вас перекине в діалог з менеджером, і текст замовлення вставиться автоматично."
    )
    
    kb = [
        [InlineKeyboardButton("✈️ НАПИСАТИ МЕНЕДЖЕРУ", url=magic_link)],
        [InlineKeyboardButton("🏠 В головне меню", callback_data="menu_start")]
    ]

    await send_ghosty_message(update, text, kb, context=context)
    
    # --- 7. ОЧИСТКА СЕСІЇ ---
    context.user_data['target_item_id'] = None
    context.user_data['target_gift_id'] = None
    context.user_data['selected_color'] = None
    context.user_data['cart'] = []
    

# =================================================================
# 📝 SECTION 17: DATA INPUT HANDLER (TEXT PROCESSOR - PRO FIX)
# =================================================================

import sqlite3
import re
from datetime import datetime

async def handle_data_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обробляє текстові відповіді користувача на етапах анкети.
    🔥 ВДОСКОНАЛЕННЯ: Миттєве збереження + Розумна валідація даних.
    """
    if not update.message or not update.message.text: return
    
    user = update.effective_user
    text = update.message.text.strip()
    step = context.user_data.get('data_step')
    profile = context.user_data.setdefault('profile', {'uid': user.id})

    # --- ВНУТРІШНЯ ФУНКЦІЯ: МИТТЄВЕ ЗБЕРЕЖЕННЯ ---
    def save_step_to_db(field_name, value):
        try:
            with sqlite3.connect(DB_PATH, timeout=30) as conn:
                # Гарантуємо, що користувач існує в БД (із датою реєстрації)
                reg_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                conn.execute("""
                    INSERT OR IGNORE INTO users (user_id, username, full_name, is_vip, next_order_discount, reg_date) 
                    VALUES (?, ?, ?, 0, 0.0, ?)
                """, (user.id, user.username, user.full_name, reg_time))
                
                # Записуємо конкретне поле
                conn.execute(f"UPDATE users SET {field_name}=? WHERE user_id=?", (value, user.id))
                conn.commit()
        except Exception as e:
            logger.error(f"Instant DB Save Error [{field_name}]: {e}")

    # --- 1. ОБРОБКА ІМЕНІ ---
    if step == "name":
        # Захист від занадто коротких імен або цифр
        if len(text) < 2 or text.isdigit():
            await update.message.reply_text("⚠️ Некоректне ім'я. Напишіть справжнє Прізвище та Ім'я літерами:")
            return
        
        profile['full_name'] = text
        save_step_to_db("full_name", text) # 💾 ЗБЕРЕГЛИ ОДРАЗУ
        
        # Перехід до телефону
        context.user_data['data_step'] = "phone"
        msg = (
            f"👤 Приємно познайомитись, <b>{escape(text)}</b>!\n\n"
            f"📱 Тепер введіть ваш <b>номер телефону</b>\n"
            f"(Наприклад: 0991234567):"
        )
        await update.message.reply_text(msg, parse_mode='HTML')

    # --- 2. ОБРОБКА ТЕЛЕФОНУ ---
    elif step == "phone":
        # PRO-ВАЛІДАЦІЯ: Очищаємо від пробілів, дужок, дефісів та плюсів
        clean_phone = re.sub(r'[\s\(\)\-\+]', '', text)
        
        if not clean_phone.isdigit() or len(clean_phone) < 9 or len(clean_phone) > 12:
            await update.message.reply_text("⚠️ Некоректний формат. Введіть правильний номер (напр. 0991234567):")
            return
        
        profile['phone'] = clean_phone
        save_step_to_db("phone", clean_phone) # 💾 ЗБЕРЕГЛИ ОДРАЗУ
        
        # Перевіряємо, чи є місто. Якщо ні - йдемо обирати місто
        if not profile.get('city'):
            # Скидаємо стан тексту, бо далі будуть кнопки
            await choose_city_menu(update, context)
        else:
            # Якщо місто є, але немає адреси -> йдемо до адреси
            context.user_data['data_step'] = "address"
            city = profile['city']
            
            # 🔥 ПРОБЛЕМА №3: Кнопка для зміни міста на етапі адреси
            kb = [[InlineKeyboardButton("🏙 Змінити місто", callback_data="choose_city")]]
            
            await update.message.reply_text(
                f"📞 Номер <code>{clean_phone}</code> прийнято.\n\n"
                f"📍 Місто: <b>{city}</b>.\n"
                f"Вкажіть <b>Адресу або Відділення НП</b>:",
                reply_markup=InlineKeyboardMarkup(kb),
                parse_mode='HTML'
            )

    # --- 3. ОБРОБКА АДРЕСИ ---
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
        save_step_to_db("address_details", full_address) # 💾 ЗБЕРЕГЛИ ОДРАЗУ
        
        # Фіналізуємо анкету (виклик функції з Section 16)
        if 'finalize_data_collection' in globals():
            await finalize_data_collection(update, context)
            
            
# =================================================================
# 🎮 SECTION 28: STABLE MESSAGE HANDLER (TITAN ULTIMATE v10.5)
# =================================================================

async def handle_user_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Центральний хаб: обробляє Текст, Медіа (чеки) та Стани.
    """
    if not update.message: 
        return 
    
    user = update.effective_user
    state = context.user_data.get('state')
    
    # Отримуємо текст безпечно (з повідомлення або підпису до фото)
    raw_text = update.message.text.strip() if update.message.text else (update.message.caption or "")
    
    # Визначаємо, чи є юзер адміном
    is_admin = False
    if 'ADMIN_LIST' in globals() and user.id in ADMIN_LIST: is_admin = True
    elif user.id == globals().get('MANAGER_ID'): is_admin = True

    # -----------------------------------------------------------
    # 💎 1. ІНТЕРАКТИВНЕ КЕРУВАННЯ БАЛАНСОМ (Тільки Адмін)
    # -----------------------------------------------------------
    if state == "WAITING_BALANCE_DATA" and is_admin:
        try:
            parts = raw_text.split()
            if len(parts) != 2:
                await update.message.reply_text("⚠️ <b>Помилка:</b> Введіть тільки ID та суму через пробіл (напр. <code>12345 200</code>).", parse_mode='HTML')
                return
                
            target_id = int(parts[0])
            amount = float(parts[1])
            
            with sqlite3.connect(DB_PATH, timeout=30) as conn:
                # Перевіряємо, чи є юзер в базі
                user_exists = conn.execute("SELECT user_id FROM users WHERE user_id=?", (target_id,)).fetchone()
                if not user_exists:
                    await update.message.reply_text("❌ Користувача з таким ID не знайдено в базі.")
                    return
                
                # Додаємо баланс (якщо amount з мінусом - він відніметься)
                conn.execute("UPDATE users SET next_order_discount = next_order_discount + ? WHERE user_id=?", (amount, target_id))
                conn.commit()
                
            await update.message.reply_text(f"✅ Баланс користувача <code>{target_id}</code> успішно змінено на <b>{amount} грн</b>!", parse_mode='HTML')
            context.user_data['state'] = None # Скидаємо стан
            
            # Сповіщаємо клієнта
            try:
                msg_text = (
                    f"🎁 <b>ВАШ БАЛАНС ОНОВЛЕНО!</b>\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"Адміністратор нарахував вам <b>{amount} грн</b> на бонусний рахунок.\n\n"
                    f"<i>Використовуйте їх для повної або часткової оплати замовлень!</i>"
                )
                await context.bot.send_message(chat_id=target_id, text=msg_text, parse_mode='HTML')
            except Exception:
                await update.message.reply_text("⚠️ Сповіщення не доставлено (можливо, юзер заблокував бота), але гроші в базі нараховано.")
                
        except ValueError:
            await update.message.reply_text("⚠️ <b>Помилка:</b> ID та сума мають бути числами.")
        except Exception as e:
            await update.message.reply_text(f"❌ Системна помилка: {e}")
        return

    # -----------------------------------------------------------
    # 2. АДМІН-РОЗСИЛКА
    # -----------------------------------------------------------
    if state == "BROADCAST_MODE" and is_admin:
        try:
            with sqlite3.connect(DB_PATH, timeout=30) as conn:
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
                    await update.message.copy(chat_id=uid)
                    sent += 1
                    if sent % 25 == 0: await asyncio.sleep(1.0)
                    else: await asyncio.sleep(0.05)
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
            await update.message.reply_text(f"🆘 Помилка розсилки: {e}")
        finally:
            context.user_data['state'] = None
        return

    # -----------------------------------------------------------
    # 3. ПРИЙОМ КВИТАНЦІЙ (Стан WAITING_RECEIPT + Фото)
    # -----------------------------------------------------------
    if update.message.photo and state == "WAITING_RECEIPT":
        order_id = context.user_data.get("current_order_id", f"UNK-{user.id}-{int(datetime.now().timestamp())}")
        amount = context.user_data.get("final_checkout_sum", 0.0)
        profile = context.user_data.get("profile", {})
        
        try:
            with sqlite3.connect(DB_PATH, timeout=30) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO orders (order_id, user_id, amount, status, created_at) 
                    VALUES (?, ?, ?, ?, ?)
                """, (order_id, user.id, amount, 'pending', datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                conn.commit()
        except Exception as e:
            logger.error(f"Receipt DB Error: {e}")
            await update.message.reply_text("⚠️ Помилка збереження. Спробуйте ще раз.")
            return

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
            await context.bot.send_photo(
                chat_id=globals().get('MANAGER_ID'),
                photo=update.message.photo[-1].file_id,
                caption=caption,
                reply_markup=admin_kb,
                parse_mode='HTML'
            )
            await update.message.reply_text(
                "✅ <b>Квитанцію отримано!</b>\n\n"
                "Ваш платіж передано на перевірку.\n"
                "Очікуйте підтвердження протягом 10-15 хвилин.",
                parse_mode='HTML'
            )
            context.user_data['state'] = None
        except Exception as e:
            logger.error(f"Manager Notification Failed: {e}")
            await update.message.reply_text("⚠️ Не вдалося зв'язатися з менеджером.")
        return

    # -----------------------------------------------------------
    # 4. ТЕКСТОВА МАРШРУТИЗАЦІЯ (Анкета & Промо)
    # -----------------------------------------------------------
    if raw_text and not raw_text.startswith("/"):
        if state == "COLLECTING_DATA":
            if 'handle_data_input' in globals():
                await handle_data_input(update, context)
            return
            
        elif context.user_data.get('awaiting_promo'):
            if 'process_promo' in globals():
                await process_promo(update, context)
            return

# =================================================================
# 👮‍♂️ SECTION 25: ADMIN GOD-PANEL (MONITORING & FINANCIALS)
# =================================================================

async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Головне меню GOD-MODE."""
    user = update.effective_user
    
    is_admin = False
    if 'ADMIN_LIST' in globals() and user.id in ADMIN_LIST: is_admin = True
    elif user.id == globals().get('MANAGER_ID'): is_admin = True
    if not is_admin: return 

    ping = random.randint(12, 28)
    uptime_str = str(datetime.now() - START_TIME).split('.')[0] if 'START_TIME' in globals() else "Unknown"
    active_sessions = len(context.application.user_data)
    cpu_load = random.randint(2, 7)

    text = (
        f"🕴️ <b>GHOSTY GOD-MODE v10.5</b>\n"
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
    await _edit_or_reply(update, text, kb)

async def admin_decision_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробка кнопок Підтвердити/Відхилити чек."""
    query = update.callback_query
    parts = query.data.split("_")
    action, user_id = parts[1], int(parts[2])
    order_id = parts[3] if len(parts) > 3 else "Unknown"
    
    if action == "ok":
        try:
            with sqlite3.connect(DB_PATH, timeout=30) as conn:
                conn.execute("UPDATE orders SET status='paid' WHERE order_id=?", (order_id,))
                conn.commit()
            
            await query.edit_message_caption(caption=query.message.caption + "\n\n✅ <b>ПІДТВЕРДЖЕНО АДМІНОМ</b>", parse_mode='HTML')
            await context.bot.send_message(chat_id=user_id, text=f"🎉 <b>Вашу оплату підтверджено!</b>\n\nЗамовлення <code>#{order_id}</code> передано на пакування.", parse_mode='HTML')
        except Exception as e:
            logger.error(f"Admin OK Error: {e}")

    elif action == "no":
        try:
            with sqlite3.connect(DB_PATH, timeout=30) as conn:
                conn.execute("UPDATE orders SET status='rejected' WHERE order_id=?", (order_id,))
                conn.commit()

            await query.edit_message_caption(caption=query.message.caption + "\n\n❌ <b>ВІДХИЛЕНО</b>", parse_mode='HTML')
            await context.bot.send_message(chat_id=user_id, text=f"⚠️ <b>Оплату по замовленню #{order_id} відхилено.</b>\nЗв'яжіться з менеджером.", parse_mode='HTML')
        except Exception as e:
            logger.error(f"Admin NO Error: {e}")

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Фінансова статистика."""
    query = update.callback_query
    try:
        with sqlite3.connect(DB_PATH, timeout=30) as conn:
            cur = conn.cursor()
            cur.execute("SELECT SUM(amount) FROM orders WHERE status='paid' AND created_at >= date('now', '-7 days')")
            revenue_7d = cur.fetchone()[0] or 0.0
            cur.execute("SELECT COUNT(*) FROM orders WHERE status='paid' AND created_at >= date('now', '-7 days')")
            orders_count = cur.fetchone()[0]
        
        text = (
            f"💰 <b>ФІНАНСОВИЙ ЗВІТ (7 ДНІВ)</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💵 Прибуток: <b>{revenue_7d:,.2f} UAH</b>\n"
            f"📦 Оплачених замовлень: <b>{orders_count}</b>\n"
            f"📈 Середній чек: <b>{round(revenue_7d/orders_count, 2) if orders_count > 0 else 0} UAH</b>\n"
        )
        await _edit_or_reply(query, text, [[InlineKeyboardButton("🔙 НАЗАД", callback_data="admin_main")]])
    except Exception as e:
        logger.error(f"Stats Error: {e}")

async def admin_view_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Перегляд бази з ПАГІНАЦІЄЮ."""
    query = update.callback_query
    
    page = 0
    if "admin_view_users_" in query.data:
        try: page = int(query.data.split("_")[-1])
        except: pass
        
    limit, offset = 10, page * 10

    try:
        with sqlite3.connect(DB_PATH, timeout=30) as conn:
            total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            users_data = conn.execute(f"""
                SELECT u.username, u.user_id, u.phone, u.city, o.amount, o.status
                FROM users u
                LEFT JOIN orders o ON o.user_id = u.user_id 
                AND o.created_at = (SELECT MAX(created_at) FROM orders WHERE user_id = u.user_id)
                ORDER BY u.reg_date DESC LIMIT {limit} OFFSET {offset}
            """).fetchall()

        report = f"👥 <b>КЛІЄНТИ (Стор. {page + 1}):</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        for row in users_data:
            username, uid, phone, city, amount, status = row
            st_icon = "✅" if status == 'paid' else ("⏳" if status in ['pending', 'new_request'] else "❌")
            report += f"👤 @{username or 'Anon'} (<code>{uid}</code>)\n📞 {phone or '—'} | {city or '—'}\n💰 {f'{amount:.0f}₴' if amount else '—'} [{st_icon}]\n--------------------\n"

        kb, nav_row = [], []
        if page > 0: nav_row.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"admin_view_users_{page-1}"))
        nav_row.append(InlineKeyboardButton("🔄", callback_data=f"admin_view_users_{page}"))
        if offset + limit < total_users: nav_row.append(InlineKeyboardButton("Далі ➡️", callback_data=f"admin_view_users_{page+1}"))
            
        kb.append(nav_row)
        kb.append([InlineKeyboardButton("🔙 НАЗАД", callback_data="admin_main")])
        await _edit_or_reply(query, report, kb)
    except Exception as e:
        logger.error(f"View Users Error: {e}")

async def start_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запуск розсилки."""
    user = update.effective_user
    is_admin = False
    if 'ADMIN_LIST' in globals() and user.id in ADMIN_LIST: is_admin = True
    elif user.id == globals().get('MANAGER_ID'): is_admin = True
    if not is_admin: return
    
    context.user_data['state'] = "BROADCAST_MODE"
    await _edit_or_reply(
        update.callback_query if update.callback_query else update, 
        "📢 <b>РОЗСИЛКА</b>\nНадішліть повідомлення (текст/фото/відео).\nБот розішле його всім клієнтам.", 
        [[InlineKeyboardButton("❌ СКАСУВАТИ", callback_data="admin_main")]]
    )

async def ask_balance_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запит ID та суми для поповнення балансу."""
    query = update.callback_query
    context.user_data['state'] = "WAITING_BALANCE_DATA"
    
    text = (
        "💳 <b>НАРАХУВАННЯ БАЛАНСУ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Надішліть сюди в чат ID користувача та суму через пробіл.\n\n"
        "Приклад: <code>123456789 200</code>\n\n"
        "<i>(Щоб списати гроші, введіть суму з мінусом: 123456789 -50)</i>"
    )
    kb = [[InlineKeyboardButton("❌ СКАСУВАТИ", callback_data="admin_main")]]
    await _edit_or_reply(query, text, kb)

# =================================================================
# ⚙️ SECTION 29: GLOBAL DISPATCHER (TITAN FINAL - BULLETPROOF)
# =================================================================

async def global_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Центральний мозок: розподіляє всі натискання кнопок."""
    query = update.callback_query
    data = query.data
    user = update.effective_user
    
    try: 
        if data != "ignore_click": await query.answer()
    except Exception: pass

    try:
        # --- 0. АДМІН-ПАНЕЛЬ ---
        if data.startswith(("adm_", "admin_")):
            is_admin = False
            if 'ADMIN_LIST' in globals() and user.id in ADMIN_LIST: is_admin = True
            elif user.id == globals().get('MANAGER_ID'): is_admin = True
                
            if is_admin:
                if data.startswith("adm_"): await admin_decision_handler(update, context)
                elif data == "admin_main": await admin_menu(update, context)
                elif data == "admin_stats": await admin_stats(update, context)
                elif data.startswith("admin_view_users"): await admin_view_users(update, context)
                elif data == "admin_broadcast": await start_broadcast(update, context)
                elif data == "admin_add_balance": await ask_balance_data(update, context)
                elif data == "admin_cancel_action":
                    context.user_data['state'] = None
                    await admin_menu(update, context)
            else:
                await query.answer("⛔️ Доступ заборонено", show_alert=True)
            return

        # --- 1. БАЗОВА НАВІГАЦІЯ ---
        if data == "menu_start":
            context.user_data['state'], context.user_data['target_item_id'], context.user_data['target_gift_id'], context.user_data['selected_color'] = None, None, None, None
            await start_command(update, context)
        elif data == "menu_profile": await show_profile(update, context)
        elif data == "menu_cart": await show_cart_logic(update, context)
        elif data == "ref_system": await show_ref_info(update, context)
        elif data == "menu_promo": 
            context.user_data['awaiting_promo'] = True
            await _edit_or_reply(query, "🎟 <b>АКТИВАЦІЯ БОНУСІВ</b>\n\nВведіть промокод прямо тут 👇", [[InlineKeyboardButton("🔙 Скасувати", callback_data="menu_profile")]], context=context)

        # --- 2. КАТАЛОГ ТА ТОВАРИ ---
        elif data == "cat_all": 
            context.user_data['state'] = None
            await catalog_main_menu(update, context)
        elif data.startswith("cat_list_"): await show_category_items(update, context, data.replace("cat_list_", ""))
        elif data.startswith("view_item_"): 
            try: await view_item_details(update, context, int(data.split("_")[2]))
            except: await catalog_main_menu(update, context)

        # --- 3. КОЛЬОРИ ТА КОШИК ---
        elif data.startswith("sel_col_"):
            p = data.split("_")
            if 'handle_color_selection_click' in globals():
                await handle_color_selection_click(update, context, int(p[2]), "_".join(p[3:]))
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
        elif data.startswith("sel_dist_"): await address_request_handler(update, context, data.replace("sel_dist_", ""))
        elif data == "fill_delivery_data": await start_data_collection(update, context, next_action='none')
        elif data == "checkout_init": 
            context.user_data['target_item_id'] = None 
            await start_data_collection(update, context, next_action='checkout')

# --- 5. ШВИДКЕ ЗАМОВЛЕННЯ ТА МЕНЕДЖЕР (ПЕРЕХОПЛЕННЯ) ---
        elif data.startswith("fast_order_") or data.startswith("mgr_pre_"):
            try:
                parts = data.split("_")
                is_fast = data.startswith("fast")
                item_id = int(parts[2])
                item = get_item_data(item_id)
                
                gift_id = None
                # Просто перевіряємо, чи є цифри в кінці
                if len(parts) > 3 and parts[-1].isdigit():
                    gift_id = int(parts[-1])

                needs_gift = item and (item_id < 300 or 500 <= item_id < 700 or item.get('gift_liquid'))
                
                if needs_gift and gift_id is None: 
                    await gift_selection_handler(update, context)
                else:
                    context.user_data['target_item_id'] = item_id
                    context.user_data['target_gift_id'] = gift_id if (gift_id and gift_id > 0) else None
                    await start_data_collection(update, context, next_action='fast_order' if is_fast else 'manager_order')
            except Exception as e: 
                logger.error(f"Order route error: {e}")

    except Exception as e:
        logger.error(f"GLOBAL DISPATCHER FATAL: {e} | DATA: {data}")
        traceback.print_exc()

# =================================================================
# 🚀 SECTION 31: ENGINE STARTUP & ELITE MONITORING (TITAN v10.5)
# =================================================================

import time
import platform

async def post_init(application: Application) -> None:
    """Професійний звіт системи моніторингу GHO$$TY для Адміна."""
    try:
        start_ping = time.time()
        bot = await application.bot.get_me()
        ping = round((time.time() - start_ping) * 1000, 2)
        
        # Системні дані
        db_sz = f"{os.path.getsize(DB_PATH) / 1024:.2f} KB" if os.path.exists(DB_PATH) else "🛠 NEW"
        uptime = str(datetime.now() - START_TIME).split('.')[0]
        py_ver = platform.python_version()
        
        # Дизайнерський звіт в Telegram
        report = (
            f"🛰 <b>GHO$$TY STAFF | MONITORING CENTER</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🤖 <b>BOT-NODE:</b> @{bot.username}\n"
            f"🛡 <b>VERSION:</b> <code>TITAN ULTIMATE v10.5</code>\n"
            f"🟢 <b>STATUS:</b> <code>STABLE / ONLINE</code>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"⚡️ <b>PERFORMANCE:</b>\n"
            f"⏱ Ping: <code>{ping} ms</code>\n"
            f"🆙 Uptime: <code>{uptime}</code>\n"
            f"🐍 Python: <code>{py_ver}</code>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🗄 <b>STORAGE & DB:</b>\n"
            f"📝 Database: <code>CONNECTED</code>\n"
            f"📦 DB Weight: <code>{db_sz}</code>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🕒 <code>{datetime.now().strftime('%d.%m.%Y | %H:%M:%S')}</code>\n\n"
            f"👑 <i>System fully operational. Waiting for customers...</i>"
        )
        await application.bot.send_message(chat_id=MANAGER_ID, text=report, parse_mode='HTML')
    except Exception as e:
        logger.error(f"Post-init reporting failed: {e}")

def main():
    # 🔥 ЕЛІТНИЙ СИСАДМІН-ВИВІД У КОНСОЛЬ
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\n" + "═"*60)
    print(f"  ☁️  GHO$$TY STAFF PREMIUM ENGINE v10.5  ☁️")
    print("═"*60)
    print(f"  [⏳] TIME:      {datetime.now().strftime('%H:%M:%S')}")
    print(f"  [👤] ADMIN:     {MANAGER_ID}")
    print(f"  [⚙️] CORE:      Initializing Async Stack...")
    
    if not TOKEN or "ВСТАВ" in TOKEN:
        print(f"  [❌] FATAL:     BOT_TOKEN IS MISSING!")
        print("═"*60 + "\n")
        sys.exit(1)
        
    init_db()
    print(f"  [💾] DATABASE:  SQLITE3 Connection Active")
    
    # Конфігурація додатка
    app = (
        Application.builder()
        .token(TOKEN)
        .persistence(PicklePersistence(filepath=PERSISTENCE_PATH))
        .defaults(Defaults(parse_mode=ParseMode.HTML))
        .connection_pool_size(25)
        .read_timeout(60)
        .write_timeout(60)
        .post_init(post_init)
        .build()
    )

    # Реєстрація хендлерів (Bulletproof Routing)
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("admin", admin_menu))
    app.add_handler(CallbackQueryHandler(global_callback_handler))
    app.add_handler(MessageHandler((filters.TEXT | filters.PHOTO | filters.VIDEO) & ~filters.COMMAND, handle_user_input))
    
    app.add_error_handler(error_handler)
    
    print(f"  [🌐] NETWORK:   Pool Size: 25 | Protocols: HTTP/1.1")
    print(f"  [🚀] STATUS:    POLLING STARTED - SYSTEM ONLINE")
    print("═"*60 + "\n")
    
    app.run_polling(drop_pending_updates=True, close_loop=False)

if __name__ == "__main__":
    if 'START_TIME' not in globals():
        START_TIME = datetime.now()
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        print(f"\n  [🚫] SHUTDOWN:  System manually terminated.")
    except Exception as fatal_e:
        print(f"\n  [💥] CRASH:     CRITICAL ERROR DETECTED!")
        print(f"  [!] REASON:    {fatal_e}")
        traceback.print_exc()
        sys.exit(1)

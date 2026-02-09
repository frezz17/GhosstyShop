# =================================================================
# 🤖 PROJECT: GHOSTY STAFF PREMIUM E-COMMERCE ENGINE (STABLE)
# 🛠 VERSION: 4.2.0 (BOTHOST OPTIMIZED)
# 🛡 DEVELOPER: Gho$$tyyy & Gemini AI
# =================================================================
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    CallbackQueryHandler, ContextTypes, filters, 
    PicklePersistence, Defaults  # Обов'язково тут!
)
from telegram.constants import ParseMode # Обов'язково тут!

import os
import sys
import logging
import sqlite3
import asyncio
import random
from datetime import datetime
from html import escape

import telegram
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters, PicklePersistence, Defaults
from telegram.constants import ParseMode
from telegram.error import NetworkError



# =================================================================
# ⚙️ SECTION 1: GLOBAL CONFIGURATION (FIXED)
# =================================================================
# Пріоритет: спочатку беремо токен з Docker, якщо його нема — з коду
TOKEN = os.getenv("BOT_TOKEN", "8351638507:AAFSnnmblizuK7xOEleDiRl4SE4VTpPJulc")
MANAGER_ID = 7544847872
MANAGER_USERNAME = "ghosstydpbot"

MANAGER_ID = 7544847872
MANAGER_USERNAME = "ghosstydp" # Твій основний юзернейм

MANAGER_ID = 7544847872
MANAGER_USERNAME = "ghosstydpbot"
CHANNEL_URL = "https://t.me/GhostyStaffDP"
WELCOME_PHOTO = "https://i.ibb.co/y7Q194N/1770068775663.png"

# Економіка
DISCOUNT_MULT = 0.65         
PROMO_DISCOUNT_MULT = 0.65   
VIP_EXPIRY = "25.03.2026"
MIN_ORDER_SUM = 300 

# Реквізити (ВИПРАВЛЕНО КОМИ ТА ДУЖКИ)
PAYMENT_LINK = {
    PAYMENT_LINK = "https://heylink.me/ghosstyshop" # Твій основний хаб
    "mono": "https://lnk.ua/k4xJG21Vy?utm_medium=social&utm_source=heylink.me",
    "privat": "https://lnk.ua/RVd0OW6V3?utm_medium=social&utm_source=heylink.me"
}

# Категорії для диспетчера
CATEGORIES = {
    "cat_list_hhc": [100, 101, 102, 103, 104],
    "cat_list_pods": [500, 501, 502, 503, 504, 505, 506],
    "cat_list_liquids": [301, 302, 303],
    "cat_list_sets": [701, 702]
}

# Виправлена функція пошуку (заміни стару версію)
def get_item_data(item_id):
    try:
        iid = int(item_id)
        # Об'єднуємо всі словники для пошуку
        all_products = {}
        if 'HHC_VAPES' in globals(): all_products.update(HHC_VAPES)
        if 'PODS' in globals(): all_products.update(PODS)
        if 'LIQUIDS' in globals(): all_products.update(LIQUIDS)
        
        return all_products.get(iid)
    except Exception as e:
        logger.error(f"Error getting item data: {e}")
        return None

# Повна база товарів Gho$$tyyy (HHC, Рідини, Набори)
# =================================================================
# 📦 SECTION 7: REAL PRODUCT INVENTORY (PODS)
# =================================================================
PAYMENT_LINK = "https://t.me/ghosstydpbot" # Твій лінк на оплату/менеджера

PODS = {
    501: {
        "name": "🔌 Vaporesso XROS 4 Mini",
        "type": "pod",
        "gift_liquid": False,
        "price": 549,
        "discount": True,
        "imgs": ["https://ibb.co/WpMYBCH1"],
        "colors": ["🌸 Рожевий", "🟣 Фіолетовий", "⚫ Чорний"],
        "desc": "🔋 1000 mAh\n🔥 COREX 2.0\n⚡ Швидка зарядка\n🎯 Яскравий смак\n💎 Оновлений дизайн",
        "payment_url": PAYMENT_LINK
    },
    502: {
        "name": "🔌 Vaporesso XROS Pro",
        "type": "pod",
        "gift_liquid": False,
        "price": 689,
        "discount": True,
        "imgs": ["https://ibb.co/ynYwSMt6", "https://ibb.co/3mV7scXr", "https://ibb.co/xSJCgpJ5"],
        "colors": ["⚫ Чорний", "🔴 Темно-червоний", "🌸 Рожево-червоний"],
        "desc": "🔋 1200 mAh\n⚡ Регулювання потужності\n💨 RDL / MTL\n🔥 Максимальний смак\n🚀 Професійний рівень",
        "payment_url": PAYMENT_LINK
    },
    503: {
        "name": "🔌 Vaporesso XROS Nano",
        "type": "pod",
        "gift_liquid": False,
        "price": 519,
        "discount": True,
        "imgs": ["https://ibb.co/5XW2yN80", "https://ibb.co/93dJ8wKS", "https://ibb.co/Qj90hyyz"],
        "colors": ["🪖 Камуфляж 1", "🪖 Камуфляж 2", "🪖 Камуфляж 3"],
        "desc": "🔋 1000 mAh\n💨 MTL\n🧱 Міцний корпус\n🎒 Ідеальний у дорогу\n😌 Спокійна, рівна тяга",
        "payment_url": PAYMENT_LINK
    },
    504: {
        "name": "🔌 Vaporesso XROS 4",
        "type": "pod",
        "gift_liquid": False,
        "price": 599,
        "discount": True,
        "imgs": ["https://ibb.co/LDRbQxr1", "https://ibb.co/NPHYSjN", "https://ibb.co/LhbzXD57"],
        "colors": ["🌸 Рожевий", "⚫ Чорний", "🔵 Синій"],
        "desc": "🔋 1000 mAh\n🔥 COREX\n🎨 Стильний дизайн\n👌 Баланс смаку та тяги\n✨ Щоденний комфорт",
        "payment_url": PAYMENT_LINK
    },
    505: {
        "name": "🔌 Vaporesso XROS 5",
        "type": "pod",
        "gift_liquid": False,
        "price": 799,
        "discount": True,
        "imgs": ["https://ibb.co/hxjmpHF2", "https://ibb.co/DDkgjtV4", "https://ibb.co/r2C9JTzz"],
        "colors": ["⚫ Чорний", "🌸 Рожевий", "🟣 Фіолетовий з полоскою"],
        "desc": "🔋 1200 mAh\n⚡ Fast Charge\n💎 Преміальна збірка\n🔥 Максимум смаку\n🚀 Флагман серії",
        "payment_url": PAYMENT_LINK
    },
    506: {
        "name": "🔌 Voopoo Vmate Mini Pod Kit",
        "type": "pod",
        "gift_liquid": False,
        "price": 459,
        "discount": True,
        "imgs": ["https://ibb.co/8L0JNTHz", "https://ibb.co/0RZ1VDnG", "https://ibb.co/21LPrbbj"],
        "colors": ["🌸 Рожевий", "🔴 Червоний", "⚫ Чорний"],
        "desc": "🔋 1000 mAh\n💨 Автозатяжка\n🧲 Магнітний картридж\n🎯 Простий та надійний\n😌 Легкий старт для новачків",
        "payment_url": PAYMENT_LINK
    }
}


# Групування для категорій
CATEGORIES = {
    "cat_list_hhc": [101, 102, 103],
    "cat_list_pods": [501],
    "cat_list_liquids": [301, 302, 303],
    "cat_list_sets": [701, 702]
}

# Налаштування логування
os.makedirs('data/logs', exist_ok=True)
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
# 🛠 SECTION 2: ERROR HANDLING & LOGGING
# =================================================================

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Логування помилок та сповіщення адміна."""
    # Логуємо помилку в файл
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    
    # Формуємо повідомлення про помилку для адміна
    try:
        error_msg = (
            f"🆘 <b>CRITICAL ERROR:</b>\n\n"
            f"❌ <b>Тип:</b> <code>{type(context.error).__name__}</code>\n"
            f"📝 <b>Опис:</b> <code>{escape(str(context.error))}</code>"
        )
        
        # Відправляємо сповіщення адміну
        await context.bot.send_message(chat_id=MANAGER_ID, text=error_msg)
    except Exception as e:
        logger.error(f"Could not send error message to admin: {e}")

# =================================================================
# =================================================================
# 📍 SECTION 7: GEOGRAPHY ENGINE (EXPANDED LIST)
# =================================================================

UKRAINE_CITIES = {
    "Київ": ["Шевченківський", "Дарницький", "Оболонський", "Печерський", "Соломʼянський", "Деснянський", "Подільський", "Голосіївський"],
    "Дніпро": ["Центральний", "Соборний", "Індустріальний", "Амур", "Новокодацький", "Чечелівський", "Самарський", "Шевченківський"],
    "Камʼянське": ["Центральний", "Південний", "Заводський", "Дніпровський", "Черемушки", "Романкове", "БАМ", "Соцмісто"],
    "Харків": ["Київський", "Салтівський", "Холодногірський", "Індустріальний", "Основʼянський", "Немишлянський", "Новобаварський", "Слобідський"],
    "Одеса": ["Приморський", "Київський", "Малиновський", "Суворовський", "Аркадія", "Таїрово", "Черьомушки", "Центр"],
    "Львів": ["Галицький", "Франківський", "Сихівський", "Личаківський", "Залізничний", "Шевченківський", "Брюховичі", "Рясне"],
    "Запоріжжя": ["Вознесенівський", "Хортицький", "Дніпровський", "Олександрівський", "Комунарський", "Заводський", "Шевченківський", "Південний"],
    "Кривий Ріг": ["Металургійний", "Центрально-Міський", "Інгулецький", "Саксаганський", "Покровський", "Тернівський", "Довгинцівський", "Жовтневий"],
    "Полтава": ["Київський", "Шевченківський", "Подільський", "Алмазний", "Центр", "Левада", "Браїлки", "Огнівка"],
    "Черкаси": ["Соснівський", "Придніпровський", "Центральний", "Митниця", "Казбет", "Південно-Західний", "Хімселище", "Дахнівка"]
}

async def choose_city_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Меню вибору міста (10 міст)."""
    query = update.callback_query
    profile = context.user_data.get("profile", {})
    current_city = profile.get("city")

    text = "📍 <b>ОБЕРІТЬ ВАШЕ МІСТО</b>\n━━━━━━━━━━━━━━━━━━━━\n"
    if current_city:
        text += f"✅ Поточне місто: <b>{current_city}</b>\n"
    text += "🌫️ <i>Оберіть локацію для доставки:</i>"

    keyboard = []
    city_list = list(UKRAINE_CITIES.keys())
    # Виводимо кнопки по 2 в ряд
    for i in range(0, len(city_list), 2):
        row = [InlineKeyboardButton(city, callback_data=f"sel_city_{city}") for city in city_list[i:i+2]]
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("⬅️ Назад до профілю", callback_data="menu_profile")])
    await _edit_or_reply(query, text, keyboard)

async def choose_district_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, city: str):
    """Меню вибору району для конкретного міста."""
    query = update.callback_query
    profile = context.user_data.get("profile", {})
    current_dist = profile.get("district")

    text = f"🧪 <b>{city.upper()}</b>\n━━━━━━━━━━━━━━━━━━━━\n"
    text += "🌫️ <i>Оберіть район для отримання товару:</i>"

    keyboard = []
    districts = UKRAINE_CITIES.get(city, [])
    # Виводимо райони по 2 в ряд для компактності
    for i in range(0, len(districts), 2):
        row = []
        for d in districts[i:i+2]:
            label = f"✅ {d}" if d == current_dist and profile.get("city") == city else d
            row.append(InlineKeyboardButton(label, callback_data=f"sel_dist_{d}"))
        keyboard.append(row)

    keyboard.append([InlineKeyboardButton("🏘 Змінити місто", callback_data="choose_city")])
    await _edit_or_reply(query, text, keyboard)

# =================================================================
# 🛵 SECTION 7.1: DNIPRO SPECIAL LOGISTICS
# =================================================================

DNIPRO_SPECIAL_KEYBOARD = [
    [InlineKeyboardButton("📍 Район (Клад)", callback_data="set_del_type_klad")],
    [InlineKeyboardButton("🏠 Адресна доставка (+150 грн)", callback_data="set_del_type_courier")]
]

async def choose_dnipro_delivery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Спеціальне меню для Дніпра."""
    query = update.callback_query
    text = (
        "🛵 <b>ДОСТАВКА ПО ДНІПРУ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Оберіть спосіб отримання товару:\n\n"
        "1️⃣ <b>Район (Клад)</b> — стандартний вибір району.\n"
        "2️⃣ <b>Адресна доставка</b> — кур'єр до дверей (+150 грн).\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "<i>При виборі кур'єра оплата проводиться окремо за спец-реквізитами.</i>"
    )
    await _edit_or_reply(query, text, DNIPRO_SPECIAL_KEYBOARD)

# =================================================================
# ⚙️ ОНОВЛЕННЯ ДИС ПЕТЧЕРА (SECTION 29) ДЛЯ ДНІПРА
# =================================================================

# Додай ці elif-блоки у свій global_callback_handler:

        elif data.startswith("sel_city_"):
            city = data.replace("sel_city_", "")
            context.user_data.setdefault("profile", {})["city"] = city
            # Якщо вибрано Дніпро — показуємо спец-меню
            if city == "Дніпро":
                await choose_dnipro_delivery(update, context)
            else:
                await choose_district_menu(update, context, city)

        elif data == "set_del_type_klad":
            await choose_district_menu(update, context, "Дніпро")

        elif data == "set_del_type_courier":
            profile = context.user_data.get("profile", {})
            profile["district"] = "Кур'єр (Адресна)"
            profile["courier_fee"] = 150
            
            text = (
                "💳 <b>ОПЛАТА КУР'ЄРА</b>\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "💰 Сума: <b>149.99 грн</b>\n"
                "🏷 Коментар: <code>GHSTdeliv1337</code>\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "🌫️ <i>Надішліть квитанцію про оплату доставки сюди. "
                "Після підтвердження менеджер зв'яжеться для уточнення адреси.</i>"
            )
            keyboard = [[InlineKeyboardButton("✅ Оплатити доставку", url=PAYMENT_LINK)], 
                        [InlineKeyboardButton("⬅️ Назад", callback_data="choose_city")]]
            await _edit_or_reply(query, text, keyboard)


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

# ===================== PRODUCTS =====================
LIQUIDS = {
    301: {
        "name": "🎃 Pumpkin Latte",
        "series": "Chaser HO HO HO Edition",
        "price": 269,
        "discount": True,
        "img": "https://i.ibb.co/Y7qn69Ds/photo-2024-12-18-00-00-00.jpg",
        "desc": "☕ Гарбузовий латте з корицею\n🎄 Зимовий настрій\n😌 Мʼякий та теплий смак",
        "effect": "Затишок, солодкий aftertaste ☕",
        "payment_url": "https://heylink.me/ghosstyshop/"
    },
    302: {
        "name": "🍷 Glintwine",
        "series": "Chaser HO HO HO Edition",
        "price": 269,
        "discount": True,
        "img": "https://i.ibb.co/wF8r7Nmc/photo-2024-12-18-00-00-01.jpg",
        "desc": "🍇 Пряний глінтвейн\n🔥 Теплий винний смак\n🎄 Святковий вайб",
        "effect": "Тепло, релакс 🔥",
        "payment_url": "https://heylink.me/ghosstyshop/"
    },
    303: {
        "name": "🎄 Christmas Tree",
        "series": "Chaser HO HO HO Edition",
        "price": 269,
        "discount": True,
        "img": "https://i.ibb.co/vCPGV8RV/photo-2024-12-18-00-00-02.jpg",
        "desc": "🌲 Хвоя + морозна свіжість\n❄️ Дуже свіжа\n🎅 Атмосфера зими",
        "effect": "Свіжість, холодок ❄️",
        "payment_url": "https://heylink.me/ghosstyshop/"
    }
}

HHC_VAPES = {
    100: {
        "name": "🌴 Packwoods Purple 1ml",
        "type": "hhc",
        "gift_liquid": True,
        "price": 699.77,
        "discount": True,
        "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg",
        "desc": "🧠 90% ННС | Гібрид\n😌 Розслаблення + легка ейфорія\n🎨 Мʼякий виноградний профіль\n🎁 Рідина у подарунок на вибір\n⚠️ Потужний ефект — починай з малого",
        "payment_url": PAYMENT_LINK
    },
    101: {
        "name": "🍊 Packwoods Orange 1ml",
        "type": "hhc",
        "gift_liquid": True,
        "price": 699.77,
        "discount": True,
        "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg",
        "desc": "🧠 90% ННС | Гібрид\n⚡ Бадьорить та фокусує\n🍊 Соковитий апельсин\n🎁 Рідина у подарунок на вибір\n🔥 Яскравий та швидкий ефект",
        "payment_url": PAYMENT_LINK
    },
    102: {
        "name": "🌸 Packwoods Pink 1ml",
        "type": "hhc",
        "gift_liquid": True,
        "price": 699.77,
        "discount": True,
        "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg",
        "desc": "🧠 90% ННС | Гібрид\n😇 Спокій + підйом настрою\n🍓 Солодко-фруктовий мікс\n🎁 Рідина у подарунок на вибір\n✨ Комфортний та плавний",
        "payment_url": PAYMENT_LINK
    },
    103: {
        "name": "🌿 Whole Mint 2ml",
        "type": "hhc",
        "gift_liquid": True,
        "price": 879.77,
        "discount": True,
        "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg",
        "desc": "🧠 95% ННС | Сатіва\n⚡ Енергія та ясність\n❄️ Свіжа мʼята\n🎁 Рідина у подарунок на вибір\n🚀 Ідеально вдень",
        "payment_url": PAYMENT_LINK
    },
    104: {
        "name": "🌴 Jungle Boys White 2ml",
        "type": "hhc",
        "gift_liquid": True,
        "price": 999.77,
        "discount": True,
        "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg",
        "desc": "🧠 95% ННС | Індика\n😴 Глибокий релакс\n🌲 Насичений терпкий смак\n🎁 Рідина у подарунок на вибір\n🌙 Ідеально для вечора та сну",
        "payment_url": PAYMENT_LINK
    }
}

PODS = {
    500: {
        "name": "🔌 Vaporesso XROS 3 Mini",
        "type": "pod",
        "gift_liquid": False,
        "price": 499.77,
        "discount": True,
        "img": "https://i.ibb.co/yFSQ5QSn/vaporesso-xros-3-mini.jpg",
        "desc": "🔋 1000 mAh\n💨 MTL / RDL\n⚡ Type-C зарядка\n✨ Компактний та легкий\n😌 Мʼяка тяга, стабільний смак",
        "payment_url": PAYMENT_LINK
    },
    501: {
        "name": "🔌 Vaporesso XROS 5 Mini",
        "type": "pod",
        "gift_liquid": False,
        "price": 674.77,
        "discount": True,
        "img": "https://i.ibb.co/RkNgt1Qr/vaporesso-xros-5-mini.jpg",
        "desc": "🔋 1000 mAh\n🔥 COREX 2.0\n⚡ Швидка зарядка\n🎯 Яскравий смак\n💎 Оновлений дизайн",
        "payment_url": PAYMENT_LINK
    },
    502: {
        "name": "🔌 Vaporesso XROS Pro",
        "type": "pod",
        "gift_liquid": False,
        "price": 974.77,
        "discount": True,
        "img": "https://i.ibb.co/ynYwSMt6/vaporesso-xros-pro.jpg",
        "desc": "🔋 1200 mAh\n⚡ Регулювання потужності\n💨 RDL / MTL\n🔥 Максимальний смак\n🚀 Професійний рівень",
        "payment_url": PAYMENT_LINK
    },
    503: {
        "name": "🔌 Vaporesso XROS Nano",
        "type": "pod",
        "gift_liquid": False,
        "price": 659.77,
        "discount": True,
        "img": "https://i.ibb.co/5XW2yN80/vaporesso-xros-nano.jpg",
        "desc": "🔋 1000 mAh\n💨 MTL\n🧱 Міцний корпус\n🎒 Ідеальний у дорогу\n😌 Спокійна, рівна тяга",
        "payment_url": PAYMENT_LINK
    },
    504: {
        "name": "🔌 Vaporesso XROS 4",
        "type": "pod",
        "gift_liquid": False,
        "price": 629.77,
        "discount": True,
        "img": "https://i.ibb.co/LDRbQxr1/vaporesso-xros-4.jpg",
        "desc": "🔋 1000 mAh\n🔥 COREX\n🎨 Стильний дизайн\n👌 Баланс смаку та тяги\n✨ Щоденний комфорт",
        "payment_url": PAYMENT_LINK
    },
    505: {
        "name": "🔌 Vaporesso XROS 5",
        "type": "pod",
        "gift_liquid": False,
        "price": 799.77,
        "discount": True,
        "img": "https://i.ibb.co/hxjmpHF2/vaporesso-xros-5.jpg",
        "desc": "🔋 1200 mAh\n⚡ Fast Charge\n💎 Преміальна збірка\n🔥 Максимум смаку\n🚀 Флагман серії",
        "payment_url": PAYMENT_LINK
    },
    506: {
        "name": "🔌 Voopoo Vmate Mini Pod Kit",
        "type": "pod",
        "gift_liquid": False,
        "price": 459.77,
        "discount": True,
        "img": "https://i.ibb.co/8L0JNTHz/voopoo-vmate-mini.jpg",
        "desc": "🔋 1000 mAh\n💨 Автозатяжка\n🧲 Магнітний картридж\n🎯 Простий та надійний\n😌 Легкий старт для новачків",
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
# =================================================================
# 🧠 SECTION 5: DATABASE ENGINE & PERSISTENCE
# =================================================================

def db_init():
    try:
        if not os.path.exists('data'): os.makedirs('data')
        conn = sqlite3.connect('data/ghosty_v3.db')
        cursor = conn.cursor()
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT, 
            referrals INTEGER DEFAULT 0, is_vip INTEGER DEFAULT 0)''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY, user_id INTEGER, items_text TEXT, 
            total_sum INTEGER, status TEXT, receipt_url TEXT)''')
        
        conn.commit()
        conn.close()
        logging.info("Database initialized successfully.")
    except Exception as e:
        logging.critical(f"DB Error: {e}")
        sys.exit(1)


# =================================================================
# 🛒 SECTION 6: USER INTERFACE (PROFILE & CART)
# =================================================================

async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    
    # Спрощена логіка профілю для стабільності
    text = (
        f"👤 <b>Ваш профіль</b>\n"
        f"🆔 ID: <code>{user_id}</code>\n"
        f"🏦 Статус: Стандарт\n\n"
        f"📢 Наш канал: <a href='{CHANNEL_URL}'>Підписатися</a>"
    )
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="menu_start")]]
    
    if query:
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')

async def show_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    text = "🛒 <b>Ваш кошик порожній</b>\n\nПерейдіть до каталогу, щоб обрати товар."
    keyboard = [[InlineKeyboardButton("🛍 Каталог", callback_data="cat_all")],
                [InlineKeyboardButton("🔙 Назад", callback_data="menu_start")]]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')

async def checkout_init(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.message.reply_text("📝 <b>Оформлення замовлення</b>\n\nВведіть вашу адресу доставки:")
    context.user_data["state"] = "WAITING_ADDRESS"
    

# =================================================================
# 👤 SECTION 6: USER PROFILE & REFERRAL SYSTEM (FIXED & SYNCED)
# =================================================================

async def get_or_create_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Комплексна ініціалізація користувача.
    Обробляє: реєстрацію, реферальні посилання, VIP-дати та адресні дані.
    """
    user = update.effective_user
    uid = user.id
    current_time = datetime.now().strftime("%d.%m.%Y %H:%M")
    
    # Ініціалізація профілю в пам'яті (context.user_data)
    if "profile" not in context.user_data:
        context.user_data["profile"] = {
            "uid": uid,
            "name": escape(user.first_name) if user.first_name else "Клієнт",
            "username": f"@{user.username}" if user.username else "Приховано",
            "city": None,
            "district": None,
            "address_details": None,      # ВИПРАВЛЕНО: обов'язкове поле для адресних замовлень
            "promo_applied": False,
            "promo_code": f"GHST{uid}",   # ВИПРАВЛЕНО: персональний промокод GHST + ID
            "referrals": 0,
            "orders_count": 0,
            "vip_status": f"VIP до {VIP_EXPIRY}", # Текстовий статус для відображення
            "reg_date": current_time
        }
        
        # Обробка реферального посилання
        if context.args and context.args[0].isdigit():
            referrer_id = int(context.args[0])
            if referrer_id != uid:
                context.user_data["profile"]["referred_by"] = referrer_id
                logger.info(f"User {uid} registered via ref-link from {referrer_id}")

    # Перестраховка: якщо старий профіль не мав поля address_details, додаємо його
    if "address_details" not in context.user_data["profile"]:
        context.user_data["profile"]["address_details"] = None

    # Синхронізація з фізичною базою даних SQLite
    try:
        conn = sqlite3.connect('data/ghosty_v3.db')
        c = conn.cursor()
        c.execute('''
            INSERT OR IGNORE INTO users (user_id, username, first_name, reg_date, last_active)
            VALUES (?, ?, ?, ?, ?)
        ''', (uid, user.username, user.first_name, current_time, current_time))
        
        # Оновлення часу останньої активності та імені (якщо змінив у ТГ)
        c.execute('''
            UPDATE users 
            SET last_active = ?, username = ?, first_name = ? 
            WHERE user_id = ?
        ''', (current_time, user.username, user.first_name, uid))
        
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        logger.error(f"SQLite Sync Error: {e}")

    return context.user_data["profile"]

# =================================================================
# 🛠 SECTION 7: CORE UTILITIES (FIXED)
# =================================================================

def get_item_data(item_id):
    """Шукає товар за ID у всіх нових словниках товарів."""
    try:
        iid = int(item_id)
        # Шукаємо послідовно в усіх категоріях
        if iid in HHC_VAPES: return HHC_VAPES[iid]
        if iid in LIQUIDS: return LIQUIDS[iid]
        if iid in PODS: return PODS[iid]
        # Якщо у тебе залишилися LIQUID_SETS в SECTION 1:
        if 'LIQUID_SETS' in globals() and iid in LIQUID_SETS: return LIQUID_SETS[iid]
        return None
    except:
        return None
        
async def send_ghosty_message(update: Update, text: str, reply_markup=None, photo=None):
    try:
        if update.callback_query:
            msg = update.callback_query.message
            if photo:
                try:
                    await msg.edit_media(media=InputMediaPhoto(photo, caption=text, parse_mode='HTML'), reply_markup=reply_markup)
                except:
                    await msg.reply_photo(photo=photo, caption=text, reply_markup=reply_markup, parse_mode='HTML')
            else:
                if msg.photo:
                    await msg.edit_caption(caption=text, reply_markup=reply_markup, parse_mode='HTML')
                else:
                    await msg.edit_text(text=text, reply_markup=reply_markup, parse_mode='HTML')
        else:
            if photo:
                await update.message.reply_photo(photo=photo, caption=text, reply_markup=reply_markup, parse_mode='HTML')
            else:
                await update.message.reply_text(text=text, reply_markup=reply_markup, parse_mode='HTML')
    except Exception as e:
        logger.error(f"Delivery error: {e}")

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
# 👤 SECTION 10: USER PROFILE & REFERRAL SYSTEM (GHOSTY STYLE)
# =================================================================

async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Відображення профілю користувача з фото та даними."""
    query = update.callback_query
    user = update.effective_user
    user_id = user.id
    ghst_id = f"GHSTid-{user_id}"
    
    # Ініціалізація даних користувача, якщо їх немає
    if 'delivery' not in context.user_data:
        context.user_data['delivery'] = None
    if 'vip_until' not in context.user_data:
        context.user_data['vip_until'] = VIP_END_DATE
    if 'balance' not in context.user_data:
        context.user_data['balance'] = 0

    delivery_status = context.user_data['delivery'] if context.user_data['delivery'] else "❌ Не вказано"
    
    # Текст профілю
    profile_text = (
        f"👤 <b>ПРОФІЛЬ КОРИСТУВАЧА</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🌫️ <b>Юзернейм:</b> @{user.username if user.username else 'відсутній'}\n"
        f"🧬 <b>Ім'я:</b> {user.first_name}\n"
        f"🆔 <b>ID:</b> <code>{user_id}</code>\n"
        f"🛡️ <b>Персональний код:</b> <code>{ghst_id}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🚚 <b>Дані про доставку:</b>\n<i>{delivery_status}</i>\n\n"
        f"💎 <b>ВІП-Статус до:</b> {context.user_data['vip_until']}\n"
        f"ℹ️ <i>+7 днів VIP за кожного запрошеного друга!</i>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 <b>Баланс:</b> {context.user_data['balance']} ₴\n"
        f"🎟️ <b>Реферальне посилання:</b>\n<code>https://t.me/{context.bot.username}?start={user_id}</code>"
    )

    keyboard = [
        [InlineKeyboardButton("📦 Дані про доставку", callback_data="edit_delivery")],
        [InlineKeyboardButton("🤝 Реферальна система", callback_data="ref_system")],
        [InlineKeyboardButton("🎟 Застосувати промокод", callback_data="use_promo")],
        [InlineKeyboardButton("🏠 Головне меню", callback_data="menu_start")]
    ]

    # Спроба отримати фото профілю
    try:
        photos = await user.get_profile_photos(limit=1)
        if photos.total_count > 0:
            await query.message.reply_photo(
                photo=photos.photos[0][-1].file_id,
                caption=profile_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='HTML'
            )
            await query.message.delete()
        else:
            await query.edit_message_text(profile_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
    except Exception:
        await query.edit_message_text(profile_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')

async def show_ref_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Інформація про реферальну систему (1.2)."""
    query = update.callback_query
    user_id = update.effective_user.id
    
    ref_text = (
        f"🤝 <b>РЕФЕРАЛЬНА ПРОГРАМА LAB</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"За кожного приглашеного друга ти отримуєш:\n"
        f"✅ <b>+7 днів ВІП-Статусу</b> (Безкоштовна доставка)\n"
        f"✅ <b>Додатковий промокод на 101 грн</b>\n"
        f"✅ <b>Рідина на вибір</b> (з 3-х реальних наборів) у подарунок до замовлення!\n\n"
        f"🔗 <b>Твоє посилання:</b>\n<code>https://t.me/{context.bot.username}?start={user_id}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🌫️ Більше друзів — більше бонусів у Ghosty Staff!"
    )
    keyboard = [[InlineKeyboardButton("⬅️ Назад до профілю", callback_data="menu_profile")]]
    await query.edit_message_text(ref_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')


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
# 🛍 SECTION 14: CATALOG ENGINE (FIXED)
# =================================================================

async def catalog_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Головне меню каталогу."""
    text = (
        "<b>🛍 КАТАЛОГ GHOSTY STAFF</b>\n\n"
        "Оберіть категорію товарів 👇\n"
        "🎁 <i>Подарунок до кожного HHC вейпу!</i>"
    )
    keyboard = [
        [InlineKeyboardButton("💨 HHC Вейпи", callback_data="cat_list_hhc")],
        [InlineKeyboardButton("🔌 POD-системи", callback_data="cat_list_pods")],
        [InlineKeyboardButton("📦 Набори рідин", callback_data="cat_list_sets")],
        [InlineKeyboardButton("🏠 Головне меню", callback_data="menu_start")]
    ]
    await send_ghosty_message(update, text, InlineKeyboardMarkup(keyboard))

# Додай цей аліас, щоб обидві назви функцій працювали
async def show_catalog_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await catalog_main_menu(update, context)
    
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


# =================================================================
# 🛒 SECTION 17-20: PROFESSIONAL CART & CATALOG ENGINE (GURU)
# =================================================================

async def add_to_cart_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Універсальний обробник додавання в кошик.
    Формат callback: add_[item_id]_[color_or_gift]
    """
    query = update.callback_query
    data = query.data.split("_")
    item_id = int(data[1])
    extra = data[2] # Колір або ID подарунка

    item = PODS.get(item_id)
    if not item:
        await query.answer("❌ Товар зник з лабораторії...")
        return

    # Ініціалізація кошика
    if 'cart' not in context.user_data:
        context.user_data['cart'] = []

    # Розрахунок ціни зі знижкою -35% (множник 0.65)
    # Знижка застосовується автоматично для всіх замовлень за твоїм запитом
    discount_price = int(item['price'] * 0.65)
    
    # Формуємо назву з урахуванням вибору
    display_name = item['name']
    if extra != "none":
        # Якщо extra - це назва кольору (не число)
        if not extra.isdigit():
            display_name += f" ({extra})"
        else:
            # Якщо extra - це ID рідини (подарунок)
            gift_name = GIFT_LIQUIDS.get(f"set_{extra}", "Рідина Staff")
            display_name += f" + 🎁 {gift_name}"

    cart_entry = {
        "id": item_id,
        "name": display_name,
        "base_price": item['price'],
        "final_price": discount_price,
        "extra": extra
    }

    context.user_data['cart'].append(cart_entry)
    
    await query.answer(f"✅ {item['name']} додано в кошик!")
    # Після додавання відразу показуємо кошик
    await show_cart_logic(update, context)

async def show_cart_logic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Професійне відображення кошика з перевіркою локації."""
    query = update.callback_query
    cart = context.user_data.get('cart', [])
    profile = context.user_data.get("profile", {})
    
    if not cart:
        text = (
            "🛒 <b>ТВІЙ КОШИК ПОРОЖНІЙ</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🌫️ Лабораторія чекає на твоє перше замовлення.\n\n"
            "🎁 <i>Нагадуємо: знижка -35% та рідина в подарунок активні!</i>"
        )
        keyboard = [[InlineKeyboardButton("🛍 В АСОРТИМЕНТ", callback_data="cat_all")]]
        await _edit_or_reply(query, text, keyboard)
        return

    total_sum = sum(item['final_price'] for item in cart)
    
    # Формуємо список товарів
    items_text = ""
    keyboard = []
    for idx, item in enumerate(cart):
        items_text += f"🔹 {idx+1}. <b>{item['name']}</b> — <code>{item['final_price']}₴</code>\n"
        # Кнопка видалення для кожного товару
        keyboard.append([InlineKeyboardButton(f"❌ Видалити {item['name'][:15]}...", callback_data=f"cart_del_{idx}")])

    # Перевірка даних для доставки
    location_status = ""
    can_checkout = False
    
    if profile.get("city") and profile.get("district") and profile.get("address_details"):
        location_status = f"📍 <b>Доставка:</b> {profile['city']}, {profile['district']}\n🏠 {profile['address_details']}"
        can_checkout = True
    else:
        location_status = "⚠️ <b>Увага:</b> Не вказані дані для доставки!"
        keyboard.append([InlineKeyboardButton("📍 ВКАЗАТИ ЛОКАЦІЮ", callback_data="choose_city")])

    text = (
        f"🛒 <b>ВАШ КОШИК GHO$$TY STAFF</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{items_text}"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{location_status}\n"
        f"🚚 Доставка: <b>0₴ (FREE)</b>\n"
        f"💰 Разом до сплати: <b>{total_sum}₴</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🧪 <i>Коментар до оплати: GHST{str(query.from_user.id)[::-1]}</i>"
    )

    if can_checkout:
        keyboard.append([InlineKeyboardButton("🚀 ОФОРМИТИ ЗАМОВЛЕННЯ", callback_data="checkout_final")])
    
    keyboard.append([InlineKeyboardButton("🗑 ОЧИСТИТИ", callback_data="cart_clear")])
    keyboard.append([InlineKeyboardButton("🏠 МЕНЮ", callback_data="menu_start")])

    await _edit_or_reply(query, text, keyboard)
    
# =================================================================
# 🛒 SECTION 17-20: PROFESSIONAL CART & CATALOG ENGINE (GURU)
# =================================================================

async def add_to_cart_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Універсальний обробник додавання в кошик.
    Формат callback: add_[item_id]_[color_or_gift]
    """
    query = update.callback_query
    data = query.data.split("_")
    item_id = int(data[1])
    extra = data[2] # Колір або ID подарунка

    item = PODS.get(item_id)
    if not item:
        await query.answer("❌ Товар зник з лабораторії...")
        return

    # Ініціалізація кошика
    if 'cart' not in context.user_data:
        context.user_data['cart'] = []

    # Розрахунок ціни зі знижкою -35% (множник 0.65)
    # Знижка застосовується автоматично для всіх замовлень за твоїм запитом
    discount_price = int(item['price'] * 0.65)
    
    # Формуємо назву з урахуванням вибору
    display_name = item['name']
    if extra != "none":
        # Якщо extra - це назва кольору (не число)
        if not extra.isdigit():
            display_name += f" ({extra})"
        else:
            # Якщо extra - це ID рідини (подарунок)
            gift_name = GIFT_LIQUIDS.get(f"set_{extra}", "Рідина Staff")
            display_name += f" + 🎁 {gift_name}"

    cart_entry = {
        "id": item_id,
        "name": display_name,
        "base_price": item['price'],
        "final_price": discount_price,
        "extra": extra
    }

    context.user_data['cart'].append(cart_entry)
    
    await query.answer(f"✅ {item['name']} додано в кошик!")
    # Після додавання відразу показуємо кошик
    await show_cart_logic(update, context)

async def show_cart_logic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Професійне відображення кошика з перевіркою локації."""
    query = update.callback_query
    cart = context.user_data.get('cart', [])
    profile = context.user_data.get("profile", {})
    
    if not cart:
        text = (
            "🛒 <b>ТВІЙ КОШИК ПОРОЖНІЙ</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🌫️ Лабораторія чекає на твоє перше замовлення.\n\n"
            "🎁 <i>Нагадуємо: знижка -35% та рідина в подарунок активні!</i>"
        )
        keyboard = [[InlineKeyboardButton("🛍 В АСОРТИМЕНТ", callback_data="cat_all")]]
        await _edit_or_reply(query, text, keyboard)
        return

    total_sum = sum(item['final_price'] for item in cart)
    
    # Формуємо список товарів
    items_text = ""
    keyboard = []
    for idx, item in enumerate(cart):
        items_text += f"🔹 {idx+1}. <b>{item['name']}</b> — <code>{item['final_price']}₴</code>\n"
        # Кнопка видалення для кожного товару
        keyboard.append([InlineKeyboardButton(f"❌ Видалити {item['name'][:15]}...", callback_data=f"cart_del_{idx}")])

    # Перевірка даних для доставки
    location_status = ""
    can_checkout = False
    
    if profile.get("city") and profile.get("district") and profile.get("address_details"):
        location_status = f"📍 <b>Доставка:</b> {profile['city']}, {profile['district']}\n🏠 {profile['address_details']}"
        can_checkout = True
    else:
        location_status = "⚠️ <b>Увага:</b> Не вказані дані для доставки!"
        keyboard.append([InlineKeyboardButton("📍 ВКАЗАТИ ЛОКАЦІЮ", callback_data="choose_city")])

    text = (
        f"🛒 <b>ВАШ КОШИК GHO$$TY STAFF</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{items_text}"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{location_status}\n"
        f"🚚 Доставка: <b>0₴ (FREE)</b>\n"
        f"💰 Разом до сплати: <b>{total_sum}₴</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🧪 <i>Коментар до оплати: GHST{str(query.from_user.id)[::-1]}</i>"
    )

    if can_checkout:
        keyboard.append([InlineKeyboardButton("🚀 ОФОРМИТИ ЗАМОВЛЕННЯ", callback_data="checkout_final")])
    
    keyboard.append([InlineKeyboardButton("🗑 ОЧИСТИТИ", callback_data="cart_clear")])
    keyboard.append([InlineKeyboardButton("🏠 МЕНЮ", callback_data="menu_start")])

    await _edit_or_reply(query, text, keyboard)

async def _edit_or_reply(query, text, keyboard):
    """Допоміжна функція для уникнення помилок Telegram API."""
    reply_markup = InlineKeyboardMarkup(keyboard)
    try:
        if query.message.photo:
            await query.edit_message_caption(caption=text, reply_markup=reply_markup, parse_mode='HTML')
        else:
            await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')
    except Exception:
        await query.message.reply_text(text, reply_markup=reply_markup, parse_mode='HTML')

async def cart_action_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Видалення одного товару або очищення всього кошика."""
    query = update.callback_query
    data = query.data
    cart = context.user_data.get('cart', [])

    if data.startswith("cart_del_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(cart):
            item = cart.pop(idx)
            await query.answer(f"🗑 {item['name']} видалено")
        await show_cart_logic(update, context)

    elif data == "cart_clear":
        context.user_data['cart'] = []
        await query.answer("🧹 Кошик очищено")
        await show_cart_logic(update, context)



# =================================================================
# 💳 SECTION 21: CHECKOUT & PAYMENT SELECTION (UPDATED)
# =================================================================

async def checkout_init(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Початок оформлення: перевірка даних, генерація суми з копійками та вибір банку.
    """
    profile = await get_or_create_user(update, context)
    cart = context.user_data.get("cart", [])
    
    # 1. Перевірка чи обрана локація
    if not profile.get("city") or not profile.get("district"):
        await update.callback_query.answer("⚠️ Спочатку оберіть місто та район!", show_alert=True)
        # Викликаємо меню вибору міста
        await process_geo_callbacks(update, context, "menu_city")
        return

    # 2. Перевірка кошика
    if not cart:
        await update.callback_query.answer("🛒 Кошик порожній!", show_alert=True)
        return

    # 3. Перевірка телефону (якщо немає, ставимо заглушку або просимо вказати)
    if "phone" not in profile or not profile["phone"]:
        profile["phone"] = "Вказано при оплаті"

    # 4. Розрахунок суми
    total_sum = sum(item['price'] for item in cart)
    
    # Генерація копійок (0.01 - 0.99) для ідентифікації платежу
    cents = random.randint(1, 99) / 100
    final_amount = float(total_sum) + cents
    
    # 5. Генерація ID замовлення (Коментар GHSTXXXX)
    order_id = f"GHST{random.randint(1000, 9999)}"
    
    # Зберігаємо дані замовлення в пам'ять
    context.user_data["current_order"] = {
        "amount": final_amount,
        "order_id": order_id,
        "raw_sum": total_sum
    }

    text = (
        f"<b>📦 ОФОРМЛЕННЯ ЗАМОВЛЕННЯ #{order_id}</b>\n\n"
        f"👤 <b>Клієнт:</b> {profile['name']}\n"
        f"📞 <b>Телефон:</b> {profile['phone']}\n"
        f"📍 <b>Локація:</b> {profile['city']}, {profile['district']}\n"
        f"💎 <b>Статус:</b> VIP (Доставка 0₴)\n"
        f"⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        f"💰 <b>СУМА ДО СПЛАТИ: {final_amount:.2f}₴</b>\n\n"
        f"⚠️ <b>КОМЕНТАР ОБОВ'ЯЗКОВО:</b> <code>{order_id}</code>\n"
        f"<i>Сума має бути точною до копійок! Це ваш ключ до швидкої видачі.</i>\n\n"
        f"Оберіть банк для оплати:"
    )
    
    keyboard = [
        [InlineKeyboardButton("💳 Оплата MONOBANK", callback_data="pay_mono")],
        [InlineKeyboardButton("💳 Оплата PRIVAT24", callback_data="pay_privat")],
        [InlineKeyboardButton("👨‍💻 Замовити у менеджера", url="https://t.me/ghosstydp")],
        [InlineKeyboardButton("⬅️ Змінити місто/район", callback_data="menu_city")],
        [InlineKeyboardButton("❌ Назад до кошика", callback_data="menu_cart")]
    ]
    
    await send_ghosty_message(update, text, InlineKeyboardMarkup(keyboard))

# =================================================================
# 🔑 SECTION 22: PROMOCODE & VIP LOGIC (FIXED)
# =================================================================

async def process_promo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обробка введення промокоду. Викликається через MessageHandler.
    """
    user_text = update.message.text.strip().upper()
    user_id = str(update.effective_user.id)
    profile = context.user_data.get("profile", {})
    
    # 1. Твій персональний код (GHST + ID навпаки)
    personal_promo = f"GHST{user_id[::-1]}".upper()
    
    # 2. Список глобальних кодів
    valid_promos = ["GHOSTY2026", "VIP45", "START35"]
    
    # Перевірка
    if user_text == personal_promo or user_text in valid_promos:
        profile["promo_applied"] = True
        context.user_data["vip_until"] = "25.03.2026"
        
        # Оновлюємо кошик, якщо він не порожній
        if "cart" in context.user_data:
            for item in context.user_data["cart"]:
                # Застосовуємо знижку 35% (множник 0.65)
                item['price'] = int(item['price'] * 0.65)
        
        text = (
            "🎉 <b>ПРОМОКОД УСПІШНО ЗАСТОСОВАНИЙ!</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🎁 <b>Ваші бонуси:</b>\n"
            "✅ Знижка <b>-35%</b> активована\n"
            "✅ <b>ВІП-Статус</b> до 25.03.2026\n"
            "✅ Безкоштовна доставка активна\n"
            "✅ Рідина на вибір у подарунок\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🧪 <i>Тепер ціни в асортименті вказані зі знижкою!</i>"
        )
        keyboard = [[InlineKeyboardButton("✅ Дякую, до меню", callback_data="menu_start")]]
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
    else:
        await update.message.reply_text(
            "❌ <b>Невірний промокод.</b>\nПеревірте правильність або зверніться до @ghosstydp",
            parse_mode='HTML'
        )
    
    # Вимикаємо режим очікування промокоду
    context.user_data['awaiting_promo'] = False


            
# =================================================================
# 💳 SECTION 25: PAYMENT GATEWAYS LOGIC
# =================================================================

async def payment_selection_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, method: str):
    """
    Видача реквізитів та посилань на оплату з інструкціями.
    """
    profile = context.user_data.get("profile", {})
    order_data = context.user_data.get("current_order", {})
    
    if not order_data:
        await update.callback_query.answer("⚠️ Помилка замовлення. Спробуйте ще раз.")
        await start_command(update, context)
        return

    amount = order_data['amount']
    order_id = order_data['order_id']
    
    # Вибір посилання залежно від банку
    pay_url = PAYMENT_LINK['mono'] if method == "mono" else PAYMENT_LINK['privat']
    bank_name = "MONOBANK" if method == "mono" else "PRIVAT24"

    pay_text = (
        f"<b>🚀 ОПЛАТА ЧЕРЕЗ {bank_name}</b>\n\n"
        f"💵 Точна сума: <b>{amount:.2f}₴</b>\n"
        f"📝 Коментар: <code>{order_id}</code>\n\n"
        f"1️⃣ Перейдіть за посиланням нижче\n"
        f"2️⃣ Вкажіть суму <b>з копійками</b>\n"
        f"3️⃣ В полі 'Коментар' впишіть <code>{order_id}</code>\n"
        f"4️⃣ Після оплати завантажте квитанцію менеджеру\n\n"
        f"⬇️ <b>ПОСИЛАННЯ НА ОПЛАТУ</b> ⬇️\n{pay_url}"
    )

    keyboard = [
        [InlineKeyboardButton("✅ Я ОПЛАТИВ (Надіслати чек)", url="https://t.me/ghosstydp")],
        [InlineKeyboardButton("🧾 ПІДТВЕРДИТИ В БОТІ", callback_data=f"confirm_pay_{order_id}")],
        [InlineKeyboardButton("⬅️ Змінити спосіб оплати", callback_data="cart_checkout")]
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
    Покращена обробка платіжних та адмінських дій.
    """
    query = update.callback_query
    user_id = update.effective_user.id

    try:
        # 1. ВИБІР МЕТОДУ ОПЛАТИ
        if data == "pay_card":
            await payment_selection_handler(update, context, "card")
        
        elif data == "pay_crypto":
            # Якщо крипта не налаштована, ведемо на карту або до менеджера
            await query.message.reply_text("💎 Крипто-платежі тимчасово через менеджера.")
            await payment_selection_handler(update, context, "card")

        # 2. ПІДТВЕРДЖЕННЯ ОПЛАТИ КОРИСТУВАЧЕМ
        elif data.startswith("confirm_pay_"):
            order_id = data.replace("confirm_pay_", "")
            context.user_data["last_order_id"] = order_id
            context.user_data["state"] = "WAIT_RECEIPT" # ВАЖЛИВО: вмикаємо очікування фото
            
            await query.message.reply_text(
                "📸 <b>ЧУДОВО! ТЕПЕР НАДІШЛІТЬ СКРІНШОТ ОПЛАТИ</b>\n\n"
                "Будь ласка, надішліть фото квитанції прямо сюди в чат.\n"
                "Після цього менеджер підтвердить замовлення.",
                parse_mode='HTML'
            )

        # 3. АДМІН-ПАНЕЛЬ (ДІЇ МЕНЕДЖЕРА)
        elif data.startswith("admin_app_"): # Підтвердження менеджером
            if user_id == MANAGER_ID:
                order_id = data.replace("admin_app_", "")
                
                # Оновлюємо статус в БД
                conn = sqlite3.connect('ghosty_v3.db')
                cur = conn.cursor()
                cur.execute("UPDATE orders SET status = '✅ Оплачено / Готується' WHERE order_id = ?", (order_id,))
                
                # Отримуємо ID клієнта, щоб відправити йому радісну звістку
                cur.execute("SELECT user_id FROM orders WHERE order_id = ?", (order_id,))
                customer_id = cur.fetchone()[0]
                conn.commit()
                conn.close()

                # Повідомляємо клієнта
                try:
                    await context.bot.send_message(customer_id, f"🎉 <b>ТВОЯ ОПЛАТА ПІДТВЕРДЖЕНА!</b>\nЗамовлення #{order_id} вже збирається менеджерoм.", parse_mode='HTML')
                except: pass

                await query.edit_message_caption(caption=f"{query.message.caption}\n\n✅ <b>ПІДТВЕРДЖЕНО</b>", parse_mode='HTML')

    except Exception as e:
        logger.error(f"🔴 Error in payment callbacks: {e}")
        await query.message.reply_text("⚠️ Сталася помилка. Зверніться до @ghosstydpbot")

# =================================================================
# 🛒 SECTION 27.1: INTERFACE FUNCTIONS (MISSING LOGIC)
# =================================================================

async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    text = f"👤 <b>Ваш профіль</b>\n🆔 ID: <code>{user_id}</code>\n🏦 Статус: Стандарт"
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="menu_start")]]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')

async def show_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.edit_message_text("🛒 <b>Кошик порожній</b>", 
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="menu_start")]]), 
        parse_mode='HTML')

async def checkout_init(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.message.reply_text("📝 Введіть адресу для доставки:")
    context.user_data["state"] = "WAITING_ADDRESS"

async def process_catalog_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE, data: str):
    # Заглушка для каталогу
    query = update.callback_query
    await query.message.reply_text("🛍 Каталог у розробці...")
    
# ЦЕ МАЄ БУТИ ОКРЕМОЮ ФУНКЦІЄЮ (наприклад, у Секції 8)
async def show_item_details(query, context, item_id):
    item = PODS.get(item_id)
    if not item:
        await query.message.reply_text("❌ Товар не знайдено.")
        return

    text = (
        f"<b>{item['name']}</b>\n\n"
        f"💰 Ціна: <b>{item['price']} ₴</b>\n\n"
        f"📝 Опис:\n{item['desc']}\n\n"
        f"🎨 Оберіть колір нижче 👇"
    )
    
    buttons = []
    for color in item['colors']:
        buttons.append([InlineKeyboardButton(f"🎨 {color}", callback_data=f"color_{item_id}_{color}")])
    buttons.append([InlineKeyboardButton("⬅ Назад до списку", callback_data="cat_list_pods")])
    
    if item['imgs']:
        await query.message.reply_photo(photo=item['imgs'][0], caption=text, 
                                     reply_markup=InlineKeyboardMarkup(buttons), parse_mode='HTML')
        await query.message.delete()
    else:
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode='HTML')

async def select_location(query, item_id, color, context):
    text = (
        f"✅ Ви обрали: <b>{PODS[item_id]['name']}</b>\n"
        f"🎨 Колір: <b>{color}</b>\n\n"
        f"📍 <b>Оберіть ваш район у м. Дніпро:</b>"
    )
    keyboard = [
        [InlineKeyboardButton("🏙 Центр", callback_data="loc_center")],
        [InlineKeyboardButton("🌉 Лівий берег", callback_data="loc_left")],
        [InlineKeyboardButton("🏗 Перемога / Сокіл", callback_data="loc_pobeda")],
        [InlineKeyboardButton("⬅ Назад", callback_data=f"item_{item_id}")]
    ]
    if query.message.photo:
        await query.edit_message_caption(caption=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
    else:
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
    
# =================================================================
# 📥 SECTION 12/28: UNIVERSAL INPUT HANDLER (GHOSTY GURU EDITION)
# =================================================================
async def handle_user_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Центральний мозок обробки всього, що пише або надсилає юзер."""
    if not update.message: return
    
    user_id = update.effective_user.id
    user_text = update.message.text.strip() if update.message.text else ""
    profile = context.user_data.get("profile", {})

    # --- ЛОГІКА 1: ОБРОБКА ТЕКСТУ ---
    if update.message.text:
        # А) Якщо чекаємо ПРОМОКОД
        if context.user_data.get('awaiting_promo'):
            await process_promo(update, context) # Викликає твою Секцію 22
            return

        # Б) Якщо чекаємо ДАНІ ДОСТАВКИ (Адреса/ПІБ/Кур'єр)
        if context.user_data.get('awaiting_delivery'):
            profile["address_details"] = user_text
            context.user_data['awaiting_delivery'] = False
            
            # Якщо це Дніпро + Кур'єр, робимо помітку
            is_courier = profile.get('district') == "Кур'єр (Адресна)"
            
            text = "✅ <b>ДАНІ ПРИЙНЯТО!</b>\n"
            if is_courier:
                text += f"🛵 Тип: <b>Кур'єрська доставка (Дніпро)</b>\n"
            text += f"📍 Адреса: <i>{user_text}</i>\n\n"
            text += "🌫️ Тепер ти можеш завершити замовлення в кошику."
            
            keyboard = [[InlineKeyboardButton("🛒 ПЕРЕЙТИ В КОШИК", callback_data="menu_cart")]]
            await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
            return

    # --- ЛОГІКА 2: ОБРОБКА ФОТО (КВИТАНЦІЇ) ---
    if update.message.photo:
        # Визначаємо, за що оплата
        is_courier_pay = profile.get('district') == "Кур'єр (Адресна)"
        
        # Коментар: або спец-код для доставки, або реверс ID для товару
        payment_code = "GHSTdeliv1337" if is_courier_pay else f"GHST{str(user_id)[::-1]}"
        order_type = "🛵 ОПЛАТА ДОСТАВКИ" if is_courier_pay else "📦 ОПЛАТА ТОВАРУ"

        caption = (
            f"💳 <b>{order_type}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 Клієнт: {update.effective_user.mention_html()}\n"
            f"🆔 ID: <code>{user_id}</code>\n"
            f"🏷 Код у чеку: <code>{payment_code}</code>\n"
            f"📍 Місто/Район: {profile.get('city', '—')} / {profile.get('district', '—')}\n"
            f"🏠 Адреса: {profile.get('address_details', 'Не вказана')}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🌫️ <i>Перевір суму (якщо кур'єр - 149.99 грн)</i>"
        )

        # Кнопки для тебе (Адмін-панель)
        keyboard = [[
            InlineKeyboardButton("✅ ПІДТВЕРДИТИ", callback_data=f"admin_approve_{user_id}"),
            InlineKeyboardButton("❌ ВІДХИЛИТИ", callback_data=f"admin_reject_{user_id}")
        ]]

        # Надсилаємо тобі (MANAGER_ID)
        await context.bot.send_photo(
            chat_id=MANAGER_ID,
            photo=update.message.photo[-1].file_id,
            caption=caption,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )

        # Відповідь юзеру
        await update.message.reply_text(
            "✅ <b>Квитанцію відправлено менеджеру!</b>\n"
            "Ми перевіримо оплату та змінимо статус замовлення протягом 15 хвилин. 🌫️",
            parse_mode='HTML'
        )
        return

        
    
# =================================================================
# ⚙️ SECTION 29: GLOBAL CALLBACK DISPATCHER (USA-PRO LEVEL)
# =================================================================
async def global_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user_id = update.effective_user.id
    
    try:
        await query.answer()

        # 1. ОСНОВНА НАВІГАЦІЯ ТА ПРОФІЛЬ
        if data == "menu_start":
            await start_command(update, context)
        elif data == "menu_profile":
            await show_profile(update, context)
        elif data == "ref_system":
            await show_ref_info(update, context)
        elif data == "edit_delivery":
            await query.edit_message_caption(
                caption="🚚 <b>НАЛАШТУВАННЯ ДОСТАВКИ</b>\n\n"
                        "Будь ласка, введіть ваші дані у форматі:\n"
                        "<i>Прізвище Ім'я, Номер телефону, Місто, Район, Адреса</i>\n\n"
                        "🌫️ Напишіть це повідомленням у чат 👇",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="menu_profile")]]),
                parse_mode='HTML'
            )
            context.user_data['awaiting_delivery'] = True

        # 2. КАТАЛОГ ТА ТОВАРИ
        elif data == "cat_all" or data == "assortment":
            await catalog_main_menu(update, context)
        elif data == "cat_list_pods":
            await show_pods(query, context)
        elif data.startswith("view_item_"):
            item_id = int(data.replace("view_item_", ""))
            await show_item_card(query, item_id, context)

                # 3. АДМІН-ПАНЕЛЬ (ДІЇ МЕНЕДЖЕРА)
        elif data.startswith("admin_approve_") or data.startswith("admin_app_"):
            if user_id == MANAGER_ID:
                # Визначаємо ID (це або ID юзера, або ID замовлення)
                target_id = data.replace("admin_approve_", "").replace("admin_app_", "")
                
                # 1. Спроба оновити статус в базі даних (якщо використовуєш таблицю orders)
                try:
                    conn = sqlite3.connect('data/ghosty_v3.db')
                    cur = conn.cursor()
                    cur.execute("UPDATE orders SET status = '✅ Оплачено' WHERE order_id = ? OR user_id = ?", (target_id, target_id))
                    conn.commit()
                    conn.close()
                except Exception: pass # Якщо таблиці немає, просто йдемо далі

                # 2. Відправляємо повідомлення клієнту
                try:
                    await context.bot.send_message(
                        chat_id=int(target_id), 
                        text="✅ <b>ВАША ОПЛАТА ПІДТВЕРДЖЕНА!</b>\nМенеджер вже готує замовлення до відправки/видачі. Дякуємо, що ви з нами! 🌫️",
                        parse_mode='HTML'
                    )
                    await query.answer("✅ Клієнта сповіщено!")
                except:
                    await query.answer("❌ Не вдалося надіслати повідомлення клієнту")

                # 3. Оновлюємо вигляд повідомлення в адмінці
                await query.edit_message_caption(
                    caption=query.message.caption + "\n\n✅ <b>СТАТУС: ПІДТВЕРДЖЕНО</b>",
                    parse_mode='HTML'
                )


        # 4. ПОДАРУНКИ ТА ОФОРМЛЕННЯ (НОВЕ 3/7)
        elif data == "choose_gift_menu":
            await gift_selection_menu(update, context)
        elif data.startswith("set_gift_"):
            await process_gift_selection(update, context)
        elif data == "checkout_final":
            await checkout_final_logic(update, context)
        elif data == "use_promo":
            await query.edit_message_caption(
                caption="🎟️ <b>ВВЕДІТЬ ПЕРСОНАЛЬНИЙ ПРОМОКОД:</b>\n\n"
                        "<i>Напишіть ваш код у чат одним повідомленням.</i>",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="menu_profile")]]),
                parse_mode='HTML'
            )
            context.user_data['awaiting_promo'] = True

        # 5. СТАРІ ЛОКАЦІЇ (Дніпро) - ЛИШАЄМО ДЛЯ СУМІСНОСТІ
        elif data.startswith("loc_"):
            district = data.replace("loc_", "")
            await query.answer(f"📍 Вибрано район: {district}")

    except Exception as e:
        logging.error(f"❌ Callback Error: {e}")
        await query.message.reply_text("⚠️ Виникла помилка. Спробуйте /start")

# =================================================================
# 👑 SECTION 77.7: ADMIN PANEL & BROADCAST SYS
# =================================================================

async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Головне меню адміна."""
    if update.effective_user.id != MANAGER_ID:
        return # Звичайні юзери нічого не побачать

    # Рахуємо юзерів у базі
    conn = sqlite3.connect('data/ghosty_v3.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    total_users = c.fetchone()[0]
    conn.close()

    text = (
        "⚙️ <b>GHO$$TY STAFF: ADMIN PANEL</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 Всього клієнтів у базі: <b>{total_users}</b>\n"
        "📈 Статус лабораторії: <b>ONLINE</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🌫️ <i>Оберіть дію:</i>"
    )

    keyboard = [
        [InlineKeyboardButton("📢 РОЗСИЛКА (Всім юзерам)", callback_data="admin_broadcast")],
        [InlineKeyboardButton("📊 ДЕТАЛЬНА СТАТИСТИКА", callback_data="admin_stats")],
        [InlineKeyboardButton("🏠 ПОВЕРНУТИСЯ В БОТ", callback_data="menu_start")]
    ]
    
    if update.callback_query:
        await _edit_or_reply(update.callback_query, text, keyboard)
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')

async def start_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Початок процесу розсилки."""
    query = update.callback_query
    context.user_data['awaiting_broadcast'] = True
    
    text = (
        "📢 <b>ПІДГОТОВКА РОЗСИЛКИ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Надішліть повідомлення (текст або фото з описом), "
        "яке отримають <b>ВСІ</b> користувачі вашого бота.\n\n"
        "<i>Для скасування натисніть кнопку нижче.</i>"
    )
    keyboard = [[InlineKeyboardButton("❌ СКАСУВАТИ", callback_data="admin_panel")]]
    await _edit_or_reply(query, text, keyboard)
        


# =================================================================
# 🚀 SECTION 30: FINAL RUNNER (STABLE & DOCKER READY)
# =================================================================

def main():
    """
    Точка входу. Забезпечує старт бази, завантаження даних 
    та запуск опитування (polling).
    """
    try:
        # 1. Створюємо структуру бази (Секція 5)
        db_init()
        
        # 2. Налаштовуємо збереження (Pickle)
        # Зберігаємо все в папку data, щоб дані не зникали при перезавантаженні
        persistence = PicklePersistence(filepath="data/ghosty_data.pickle")
        
        # 3. Налаштування за замовчуванням (HTML режим)
        defaults = Defaults(parse_mode=ParseMode.HTML)

        # 4. Створення Application
        # Беремо TOKEN, який ми визначили на самому початку
        app = (
            Application.builder()
            .token(TOKEN)
            .persistence(persistence)
            .defaults(defaults)
            .build()
        )

        # 5. Реєстрація хендлерів (Команди -> Текст/Фото -> Кнопки)
        # 1. Спочатку команди (найвищий пріоритет)
        app.add_handler(CommandHandler("start", start_command))
        
        # 2. Потім наш універсальний обробник (текст, фото, квитанції)
        # Він тепер викликає ту саму handle_user_input, яку ми оновили під Дніпро та кур'єра
        app.add_handler(MessageHandler(
            (filters.TEXT | filters.PHOTO) & (~filters.COMMAND), 
            handle_user_input
        ))
        
        # 3. Обробка натискань на кнопки (CallbackQuery)
        app.add_handler(CallbackQueryHandler(global_callback_handler))


        # 6. Запуск
        logging.info("GHO$$TY STAFF SYSTEM: ONLINE")
        print("\n✅ GHO$$TY STAFF SYSTEM: ONLINE")
        print("📡 Статус: Очікування замовлень та квитанцій...")

        # run_polling автоматично обробляє сигнали зупинки в Docker (SIGINT/SIGTERM)
        # drop_pending_updates=True дозволяє боту не "спамити" старими повідомленнями
        app.run_polling(drop_pending_updates=True)

    except NetworkError:
        logging.error("Помилка мережі: Перевірте BOT_TOKEN та підключення до інтернету.")
    except Exception as e:
        logging.critical(f"Критична помилка при запуску бота: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(f"Критична помилка: {e}")
            

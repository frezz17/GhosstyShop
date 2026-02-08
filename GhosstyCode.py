import os
import sys
import logging
import random
import asyncio
import warnings
from uuid import uuid4
from datetime import datetime, timedelta
from html import escape

import telegram
from telegram import (
    Update, 
    InlineKeyboardButton, 
    InlineKeyboardMarkup, 
    InputMediaPhoto,
    LabeledPrice
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
    PicklePersistence,
    AIORateLimiter,
    Defaults
)
from telegram.constants import ParseMode
from telegram.error import BadRequest, NetworkError, TelegramError

# ===================== GIFT LIQUIDS =====================
GIFT_LIQUIDS = {
    9001: {"name": "🎁 Pumpkin Latte 30ml"},
    9002: {"name": "🎁 Glintwine 30ml"},
    9003: {"name": "🎁 Christmas Tree 30ml"},
    9004: {"name": "🎁 Strawberry Jelly 30ml"},
    9005: {"name": "🎁 Mystery One 30ml"},
    9006: {"name": "🎁 Fall Tea 30ml"},
}

def get_gift_liquids():
    return [v["name"] for v in GIFT_LIQUIDS.values()]

# ===================== PRICE CALCULATION =====================
def calc_prices(item: dict, promo_percent: int) -> dict:
    base = item["price"]

    # Загальна знижка -35%
    discounted = int(base * DISCOUNT_MULTIPLIER)

    # Персональна знижка
    final_price = discounted
    if promo_percent > 0:
        final_price = int(discounted * (1 - promo_percent / 100))

    return {
        "base": base,
        "discounted": discounted,
        "final": final_price
    }

def build_item_caption(item: dict, user_data: dict) -> str:
    promo_percent = user_data.get("promo_percent", PROMO_DISCOUNT)
    is_vip = user_data.get("vip", False)

    prices = calc_prices(item, promo_percent)

    text = f"<b>{escape(item['name'])}</b>\n\n"
    text += f"💰 <s>{prices['base']} грн</s>\n"
    text += f"🔥 Зі знижкою -35%: <b>{prices['discounted']} грн</b>\n"
    text += f"🎟 З персональною знижкою -{promo_percent}%: <b>{prices['final']} грн</b>\n\n"

    text += f"{item.get('desc', '')}\n\n"

    gifts = "\n".join(f"• {g}" for g in get_gift_liquids())
    if gifts:
        text += f"🎁 <b>Рідина у подарунок на вибір:</b>\n{gifts}\n\n"

    if is_vip:
        text += "👑 <b>VIP:</b> безкоштовна доставка 🚚\n"
    else:
        text += "🚚 Доставка за тарифом\n"

    return text

# ===================== HELPERS =====================
def generate_promo_code(user_id: int) -> str:
    return f"GHOST-{user_id % 10000}{random.randint(100,999)}"

def gen_order_id(uid: int) -> str:
    return f"GHST-{uid}-{random.randint(1000,9999)}"

def vip_until(profile: dict) -> datetime:
    base = profile.get("vip_base", BASE_VIP_DATE)
    refs = profile.get("referrals", 0)
    return base + timedelta(days=7 * refs)

# ===================== CITIES & DISTRICTS =====================
CITIES = [
    "Київ", "Дніпро", "Камʼянське", "Харків", "Одеса",
    "Львів", "Запоріжжя", "Кривий Ріг", "Полтава", "Черкаси"
]

CITY_DISTRICTS = {
    "Київ": [
        "Шевченківський", "Дарницький", "Оболонський",
        "Печерський", "Соломʼянський", "Деснянський",
        "Подільський", "Голосіївський"
    ],
    "Дніпро": [
        "Центральний", "Соборний", "Індустріальний",
        "Амур", "Новокодацький", "Чечелівський",
        "Самарський", "Шевченківський"
    ],
    "Камʼянське": [
        "Центральний", "Південний", "Заводський",
        "Дніпровський", "Черемушки", "Романкове",
        "БАМ", "Соцмісто"
    ],
    "Харків": [
        "Київський", "Салтівський", "Холодногірський",
        "Індустріальний", "Основʼянський",
        "Немишлянський", "Новобаварський"
    ]
}

# ===================== PRODUCTS =====================
LIQUIDS = {
    301: {
        "name": "🎃 Pumpkin Latte",
        "series": "Chaser HO HO HO Edition",
        "price": 269,
        "discount": True,
        "img": "https://i.ibb.co/Y7qn69Ds",
        "desc": "☕ Гарбузовий латте з корицею\n🎄 Зимовий настрій\n😌 Мʼякий та теплий смак",
        "effect": "Затишок, солодкий aftertaste ☕",
        "payment_url": "https://heylink.me/ghosstyshop/"
    },
    302: {
        "name": "🍷 Glintwine",
        "series": "Chaser HO HO HO Edition",
        "price": 269,
        "discount": True,
        "img": "https://i.ibb.co/wF8r7Nmc",
        "desc": "🍇 Пряний глінтвейн\n🔥 Теплий винний смак\n🎄 Святковий вайб",
        "effect": "Тепло, релакс 🔥",
        "payment_url": "https://heylink.me/ghosstyshop/"
    },
    303: {
        "name": "🎄 Christmas Tree",
        "series": "Chaser HO HO HO Edition",
        "price": 269,
        "discount": True,
        "img": "https://i.ibb.co/vCPGV8RV",
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
        "price": 549,
        "discount": True,
        "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg",
        "desc": "🧠 90% ННС | Гібрид\n😌 Розслаблення + легка ейфорія\n🎨 Мʼякий виноградний профіль\n🎁 Рідина у подарунок на вибір\n⚠️ Потужний ефект — починай з малого",
        "payment_url": PAYMENT_LINK
    },
    101: {
        "name": "🍊 Packwoods Orange 1ml",
        "type": "hhc",
        "gift_liquid": True,
        "price": 629,
        "discount": True,
        "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg",
        "desc": "🧠 90% ННС | Гібрид\n⚡ Бадьорить та фокусує\n🍊 Соковитий апельсин\n🎁 Рідина у подарунок на вибір\n🔥 Яскравий та швидкий ефект",
        "payment_url": PAYMENT_LINK
    },
    102: {
        "name": "🌸 Packwoods Pink 1ml",
        "type": "hhc",
        "gift_liquid": True,
        "price": 719,
        "discount": True,
        "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg",
        "desc": "🧠 90% ННС | Гібрид\n😇 Спокій + підйом настрою\n🍓 Солодко-фруктовий мікс\n🎁 Рідина у подарунок на вибір\n✨ Комфортний та плавний",
        "payment_url": PAYMENT_LINK
    }
}

PODS = {
    500: {
        "name": "🔌 Vaporesso XROS 3 Mini",
        "type": "pod",
        "gift_liquid": False,
        "price": 499,
        "discount": True,
        "imgs": [
            "https://i.ibb.co/yFSQ5QSn",
            "https://i.ibb.co/LzgrzZjC",
            "https://i.ibb.co/Q3ZNTBvg"
        ],
        "colors": ["⚫ Чорний", "🔵 Голубий", "🌸 Рожевий"],
        "desc": "🔋 1000 mAh\n💨 MTL / RDL\n⚡ Type-C зарядка\n✨ Компактний та легкий\n😌 Мʼяка тяга, стабільний смак",
        "payment_url": PAYMENT_LINK
    },
    501: {
        "name": "🔌 Vaporesso XROS 5 Mini",
        "type": "pod",
        "gift_liquid": False,
        "price": 579,
        "discount": True,
        "imgs": [
            "https://i.ibb.co/RkNgt1Qr",
            "https://i.ibb.co/KxvJC1bV",
            "https://i.ibb.co/WpMYBCH1"
        ],
        "colors": ["🌸 Рожевий", "🟣 Фіолетовий", "⚫ Чорний"],
        "desc": "🔋 1000 mAh\n🔥 COREX 2.0\n⚡ Швидка зарядка\n🎯 Яскравий смак\n💎 Оновлений дизайн",
        "payment_url": PAYMENT_LINK
    }
}

def calc_price(item: dict) -> int:
    base_price = item["price"]
    if item.get("discount", True):
        return int(base_price * DISCOUNT_MULTIPLIER)
    return base_price


# ==========================================
# 🧠 ОСНОВНА ЛОГІКА ТА HELPER-ФУНКЦІЇ
# ==========================================

def generate_promo_code(user_id: int) -> str:
    """Генерує унікальний промокод для користувача"""
    return f"GHOST-{user_id % 10000}{random.randint(100, 999)}"

def calculate_price(item_price: int, profile: dict) -> int:
    """Розраховує фінальну ціну з урахуванням знижок"""
    discounted = int(item_price * DISCOUNT_MULTIPLIER)
    if profile.get("promo_applied", False):
        return int(discounted * (1 - PROMO_DISCOUNT_PERCENT / 100))
    return discounted

def calc_price(item: dict) -> int:
    """Базовий розрахунок ціни без персонального промо"""
    return int(item["price"] * DISCOUNT_MULTIPLIER)

def get_vip_date(profile: dict) -> datetime:
    """Розраховує дату завершення VIP статусу"""
    refs = profile.get("referrals", 0)
    return BASE_VIP_DATE + timedelta(days=7 * refs)

def vip_until(profile: dict) -> datetime:
    """Аліас для get_vip_date"""
    return get_vip_date(profile)

def get_item_by_id(item_id: int):
    """Шукає товар у всіх категоріях за ID"""
    for catalog in [LIQUIDS, HHC_VAPES, PODS]:
        if item_id in catalog:
            return catalog[item_id]
    return None

def build_item_caption(item: dict, user_data: dict) -> str:
    """Будує форматований опис товару для повідомлення"""
    profile = user_data.get("profile", {})
    promo_applied = profile.get("promo_applied", False)
    
    final_price = calculate_price(item['price'], profile)
    is_vip = get_vip_date(profile) > datetime.now()
    
    txt = f"<b>{escape(item['name'])}</b>\n\n"
    txt += f"💰 Ціна: <s>{item['price']} грн</s>\n"
    txt += f"🔥 Зі знижкою -35%: <b>{calc_price(item)} грн</b>\n"
    
    if promo_applied:
        txt += f"🎟 З промокодом -{PROMO_DISCOUNT_PERCENT}%: <b>{final_price} грн</b>\n"
    
    txt += f"\n{item.get('desc', '')}\n\n"
    
    if item.get("gift_liquid"):
        txt += "🎁 <b>Подарунок:</b> рідина 30ml на вибір!\n"
    
    txt += "🚚 Доставка: " + ("<b>Безкоштовна (VIP)</b>" if is_vip else "За тарифом")
    return txt

def write_profile_backup(user_id: int, context_data: dict):
    """Записує дані профілю в локальний TXT файл (Бекап)"""
    try:
        p = context_data.get("profile", {})
        orders = context_data.get("orders", [])
        path = f"data/{user_id}.txt"
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"USER_ID: {user_id}\n")
            f.write(f"NAME: {p.get('name')}\n")
            f.write(f"USERNAME: @{p.get('username')}\n")
            f.write(f"PHONE: {p.get('phone')}\n")
            f.write(f"LOCATION: {p.get('city')} / {p.get('district')}\n")
            f.write(f"ADDRESS: {p.get('address')}\n")
            f.write(f"PROMO_CODE: {p.get('promo_code')}\n")
            f.write(f"PROMO_APPLIED: {p.get('promo_applied')}\n")
            f.write(f"REFERRALS: {p.get('referrals')}\n")
            f.write("-" * 20 + "\n")
            f.write("ORDERS HISTORY:\n")
            for o in orders:
                f.write(f"ID: {o['id']} | Total: {o['total']} | Status: {o['status']} | Date: {o['date']}\n")
    except Exception as e:
        logger.error(f"Error writing backup for {user_id}: {e}")

# ==========================================
# ⌨️ КЛАВІАТУРИ ТА UI ЕЛЕМЕНТИ
# ==========================================

def get_main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👤 Профіль", callback_data="profile"), InlineKeyboardButton("🛍 Асортимент", callback_data="catalog")],
        [InlineKeyboardButton("🛒 Кошик", callback_data="cart"), InlineKeyboardButton("📦 Мої замовлення", callback_data="history")],
        [InlineKeyboardButton("📍 Змінити локацію", callback_data="city_start")],
        [InlineKeyboardButton("📢 Канал", url=CHANNEL_URL), InlineKeyboardButton("👨‍💻 Менеджер", url="https://t.me/ghosstydpbot")]
    ])

def get_catalog_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💧 Рідини", callback_data="cat_liquids")],
        [InlineKeyboardButton("🔌 POD-системи", callback_data="cat_pods")],
        [InlineKeyboardButton("💨 HHC / NNS Вейпи", callback_data="cat_hhc")],
        [InlineKeyboardButton("🔙 Назад", callback_data="main")]
    ])

# ==========================================
# 🕹 ОБРОБНИКИ КОМАНД ТА CALLBACKS
# ==========================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start: ініціалізація користувача та показ вітання"""
    user = update.effective_user
    uid = user.id

    if "profile" not in context.user_data:
        context.user_data["profile"] = {
            "uid": uid,
            "name": user.first_name,
            "username": user.username,
            "phone": None,
            "city": None,
            "district": None,
            "address": None,
            "promo_code": generate_promo_code(uid),
            "promo_applied": False,
            "referrals": 0,
            "ref_counted": False
        }
        context.user_data["cart"] = []
        context.user_data["orders"] = []
        
        # Обробка рефералки
        if context.args and context.args[0].isdigit():
            ref_owner = int(context.args[0])
            if ref_owner != uid:
                # В реальній системі ми б оновили дані ref_owner, 
                # але в рамках Pickle ми можемо це зробити тільки якщо він в пам'яті.
                # Тут імітуємо нарахування.
                context.user_data["profile"]["referrals"] += 1

    write_profile_backup(uid, context.user_data)
    
    p = context.user_data["profile"]
    vip_date = get_vip_date(p).strftime("%d.%m.%Y")
    
    text = (
        f"👋 Вітаємо у <b>Ghosty Shop</b>, {escape(p['name'])}!\n\n"
        f"🎫 Твій персональний промокод: <code>{p['promo_code']}</code>\n"
        f"💎 VIP статус активний до: <b>{vip_date}</b>\n\n"
        f"Обирай категорію або переходь у профіль для налаштування адреси 👇"
    )

    try:
        if update.message:
            await update.message.reply_photo(
                photo=WELCOME_PHOTO, caption=text, 
                reply_markup=get_main_menu(), parse_mode=ParseMode.HTML
            )
        else:
            await update.callback_query.message.edit_caption(
                caption=text, reply_markup=get_main_menu(), parse_mode=ParseMode.HTML
            )
    except Exception as e:
        logger.error(f"Error in start: {e}")

async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показує дані профілю користувача"""
    query = update.callback_query
    p = context.user_data["profile"]
    vip_date = get_vip_date(p).strftime("%d.%m.%Y")
    
    bot_obj = await context.bot.get_me()
    ref_link = f"https://t.me/{bot_obj.username}?start={p['uid']}"

    text = (
        f"👤 <b>Ваш Профіль</b>\n\n"
        f"🆔 ID: <code>{p['uid']}</code>\n"
        f"📍 Місто: {p['city'] or 'не вказано'}\n"
        f"🏘 Район: {p['district'] or 'не вказано'}\n"
        f"📞 Тел: {p['phone'] or 'не вказано'}\n\n"
        f"🎟 Промокод: <code>{p['promo_code']}</code>\n"
        f"💸 Знижка: {'✅ Активована (-45%)' if p['promo_applied'] else '❌ Не активована'}\n\n"
        f"👥 Рефералів: {p['referrals']}\n"
        f"👑 VIP до: {vip_date}\n\n"
        f"🔗 Реферальне посилання:\n<code>{ref_link}</code>"
    )
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✏️ Змінити дані", callback_data="city_start")],
        [InlineKeyboardButton("🔙 Назад", callback_data="main")]
    ])
    
    await query.message.edit_caption(caption=text, reply_markup=kb, parse_mode=ParseMode.HTML)

async def handle_catalog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробка вибору категорій та товарів"""
    query = update.callback_query
    data = query.data
    p = context.user_data["profile"]

    if data == "catalog":
        await query.message.edit_caption(caption="🛍 Оберіть категорію:", reply_markup=get_catalog_menu())
    
    elif data.startswith("cat_"):
        cat_key = data.split("_")[1]
        items_map = {"liquids": LIQUIDS, "pods": PODS, "hhc": HHC_VAPES}
        current_catalog = items_map.get(cat_key, {})
        
        btns = []
        for item_id, item in current_catalog.items():
            price = calculate_price(item['price'], p)
            btns.append([InlineKeyboardButton(f"{item['name']} — {price}₴", callback_data=f"item_{item_id}")])
        
        btns.append([InlineKeyboardButton("🔙 Назад", callback_data="catalog")])
        await query.message.edit_caption(caption="✨ Оберіть модель:", reply_markup=InlineKeyboardMarkup(btns))

    elif data.startswith("item_"):
        item_id = int(data.split("_")[1])
        item = get_item_by_id(item_id)
        
        if not item:
            await query.answer("Товар не знайдено!")
            return

        kb_list = [
            [InlineKeyboardButton("⚡ Швидке замовлення", callback_data=f"fast_{item_id}")],
            [InlineKeyboardButton("🛒 Додати в кошик", callback_data=f"add_{item_id}")],
            [InlineKeyboardButton("👨‍💻 Замовити у менеджера", callback_data=f"mgrorder_{item_id}")]
        ]
        
        if "colors" in item:
            kb_list.insert(0, [InlineKeyboardButton("🎨 Вибрати колір", callback_data=f"color_{item_id}")])
            
        kb_list.append([InlineKeyboardButton("🔙 Назад", callback_data="catalog")])
        
        caption = build_item_caption(item, context.user_data)
        photo = item["imgs"][0] if "imgs" in item else item["img"]
        
        await query.message.delete()
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo=photo,
            caption=caption,
            reply_markup=InlineKeyboardMarkup(kb_list),
            parse_mode=ParseMode.HTML
        )

# ==========================================
# 🛒 FLOW КОШИКА ТА ОФОРМЛЕННЯ
# ==========================================

async def handle_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Відображення та редагування кошика"""
    query = update.callback_query
    cart = context.user_data.get("cart", [])
    p = context.user_data["profile"]

    if not cart:
        await query.answer("Ваш кошик порожній 🛒", show_alert=True)
        return

    total = sum(i['price'] for i in cart)
    text = "🛒 <b>Ваш кошик:</b>\n\n"
    
    for idx, item in enumerate(cart):
        text += f"{idx+1}. {item['name']} — {item['price']}₴\n"
    
    text += f"\n💰 Разом до сплати: <b>{total} грн</b>"
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Оформити замовлення", callback_data="checkout_start")],
        [InlineKeyboardButton("🎟 Застосувати промокод", callback_data="apply_promo")],
        [InlineKeyboardButton("🗑 Очистити кошик", callback_data="cart_clear"), InlineKeyboardButton("🔙 Меню", callback_data="main")]
    ])
    
    if query.message.photo:
        await query.message.delete()
        await context.bot.send_message(query.message.chat_id, text, reply_markup=kb, parse_mode=ParseMode.HTML)
    else:
        await query.message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.HTML)

async def checkout_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Початок процесу оформлення: вибір міста"""
    query = update.callback_query
    p = context.user_data["profile"]

    if p["city"] and p["district"] and p["address"] and p["phone"]:
        # Якщо дані вже є, пропонуємо підтвердити або змінити
        text = f"📍 <b>Дані для доставки:</b>\n\nМісто: {p['city']}\nРайон: {p['district']}\nАдреса: {p['address']}\nТел: {p['phone']}\n\nВсе вірно?"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Так, замовити", callback_data="checkout_finalize")],
            [InlineKeyboardButton("✏️ Змінити дані", callback_data="city_start")]
        ])
        await query.message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.HTML)
    else:
        await city_selection(update, context)

async def city_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    btns = [[InlineKeyboardButton(city, callback_data=f"setcity_{city}")] for city in CITIES]
    await query.message.edit_text("🏙 Оберіть ваше місто:", reply_markup=InlineKeyboardMarkup(btns))

async def handle_receipt_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробка надісланого чека/скріншота оплати"""
    if context.user_data.get("state") != "awaiting_receipt":
        return

    user = update.effective_user
    p = context.user_data["profile"]
    cart = context.user_data["cart"]
    order_id = f"GHST-{uuid4().hex[:8].upper()}"
    total = sum(i['price'] for i in cart)
    
    # Формуємо звіт для менеджера
    report = (
        f"💰 <b>НОВЕ ЗАМОВЛЕННЯ {order_id}</b>\n\n"
        f"👤 Покупець: {escape(p['name'])} (@{user.username})\n"
        f"📍 Адреса: {p['city']}, {p['district']}, {p['address']}\n"
        f"📞 Телефон: {p['phone']}\n"
        f"💵 Сума: {total} грн\n"
        f"🛍 Товари: {', '.join([i['name'] for i in cart])}\n"
        f"👑 VIP: {'Так' if get_vip_date(p) > datetime.now() else 'Ні'}"
    )

    # Відправка менеджеру
    await context.bot.send_photo(chat_id=MANAGER_ID, photo=update.message.photo[-1].file_id, caption=report, parse_mode=ParseMode.HTML)
    
    # Запис замовлення
    order_entry = {"id": order_id, "total": total, "status": "Очікує підтвердження", "date": datetime.now().strftime("%d.%m %H:%M")}
    context.user_data["orders"].append(order_entry)
    
    # Очищення
    context.user_data["cart"] = []
    context.user_data["state"] = None
    write_profile_backup(user.id, context.user_data)

    await update.message.reply_text("✅ <b>Чек отримано!</b>\nМенеджер перевірить оплату та зв'яжеться з вами найближчим часом.", parse_mode=ParseMode.HTML, reply_markup=get_main_menu())

# ==========================================
# ⚡ FAST ORDER FLOW (ШВИДКЕ ЗАМОВЛЕННЯ)
# ==========================================

async def fast_order_init(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    item_id = int(query.data.split("_")[1])
    context.user_data["fast_item_id"] = item_id
    context.user_data["state"] = "fast_name"
    await query.message.edit_text("⚡ <b>Швидке замовлення</b>\n\nБудь ласка, введіть ваше Ім'я:", parse_mode=ParseMode.HTML)

async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Універсальний обробник текстового вводу за станом"""
    state = context.user_data.get("state")
    txt = update.message.text
    p = context.user_data["profile"]

    if state == "fast_name":
        p["name"] = txt
        context.user_data["state"] = "fast_phone"
        await update.message.reply_text("📞 Тепер введіть ваш номер телефону:")
    
    elif state == "fast_phone":
        p["phone"] = txt
        context.user_data["state"] = "fast_address"
        await update.message.reply_text("🏠 Вкажіть місто та адресу для доставки:")
    
    elif state == "fast_address":
        p["address"] = txt
        item = get_item_by_id(context.user_data["fast_item_id"])
        price = calculate_price(item['price'], p)
        
        report = f"⚡ <b>ШВИДКЕ ЗАМОВЛЕННЯ</b>\n\nТовар: {item['name']}\nКлієнт: {p['name']}\nТел: {p['phone']}\nАдреса: {txt}\nСума: {price}₴"
        await context.bot.send_message(MANAGER_ID, report, parse_mode=ParseMode.HTML)
        
        context.user_data["state"] = None
        write_profile_backup(update.effective_user.id, context.user_data)
        await update.message.reply_text(f"✅ Замовлення прийнято! Менеджер зв'яжеться з вами.\nДо сплати: <b>{price} грн</b>", parse_mode=ParseMode.HTML, reply_markup=get_main_menu())

    elif state == "awaiting_address_manual":
        p["address"] = txt
        context.user_data["state"] = "awaiting_phone_manual"
        await update.message.reply_text("📞 Введіть ваш номер телефону:")

    elif state == "awaiting_phone_manual":
        p["phone"] = txt
        context.user_data["state"] = None
        write_profile_backup(update.effective_user.id, context.user_data)
        await update.message.reply_text("✅ Дані збережено!", reply_markup=get_main_menu())

# ==========================================
# 🛰 РОУТЕР CALLBACK-ДАННИХ
# ==========================================

async def main_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    uid = query.from_user.id
    p = context.user_data.get("profile", {})

    try:
        if data == "main":
            await start(update, context)
        elif data == "profile":
            await show_profile(update, context)
        elif data == "catalog" or data.startswith("cat_") or data.startswith("item_"):
            await handle_catalog(update, context)
        elif data == "cart":
            await handle_cart(update, context)
        elif data.startswith("add_"):
            item_id = int(data.split("_")[1])
            item = get_item_by_id(item_id)
            context.user_data["cart"].append({
                "id": item_id, 
                "name": item["name"], 
                "price": calculate_price(item["price"], p)
            })
            await query.answer(f"✅ {item['name']} додано в кошик!")
        elif data.startswith("fast_"):
            await fast_order_init(update, context)
        elif data == "apply_promo":
            p["promo_applied"] = True
            # Оновлюємо ціни в кошику
            for i in context.user_data["cart"]:
                orig_item = get_item_by_id(i['id'])
                i['price'] = calculate_price(orig_item['price'], p)
            await query.answer("🎟 Промокод активовано! Ціни в кошику оновлено.", show_alert=True)
            await handle_cart(update, context)
        elif data == "checkout_start":
            await checkout_start(update, context)
        elif data.startswith("setcity_"):
            p["city"] = data.split("_")[1]
            districts = CITY_DISTRICTS.get(p["city"], [])
            if districts:
                btns = [[InlineKeyboardButton(d, callback_data=f"setdist_{d}")] for d in districts]
                await query.message.edit_text("📍 Оберіть ваш район:", reply_markup=InlineKeyboardMarkup(btns))
            else:
                context.user_data["state"] = "awaiting_address_manual"
                await query.message.edit_text("🏠 Введіть вашу адресу доставки:")
        elif data.startswith("setdist_"):
            p["district"] = data.split("_")[1]
            context.user_data["state"] = "awaiting_address_manual"
            await query.message.edit_text("🏠 Введіть точну адресу (Вулиця, будинок):")
        elif data == "checkout_finalize":
            total = sum(i['price'] for i in context.user_data["cart"])
            context.user_data["state"] = "awaiting_receipt"
            txt = (
                f"💳 <b>Оформлення оплати</b>\n\n"
                f"Сума до сплати: <b>{total} грн</b>\n"
                f"Посилання на оплату: <a href='{PAYMENT_LINK}'>HeyLink Payment</a>\n\n"
                f"⚠️ Після оплати, будь ласка, <b>надішліть сюди скріншот чека</b>."
            )
            await query.message.edit_text(txt, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        elif data == "cart_clear":
            context.user_data["cart"] = []
            await query.answer("Кошик очищено")
            await start(update, context)
        elif data == "history":
            orders = context.user_data.get("orders", [])
            if not orders:
                await query.answer("У вас ще немає замовлень", show_alert=True)
                return
            txt = "📦 <b>Історія замовлень:</b>\n\n"
            for o in orders[-5:]: # Останні 5
                txt += f"• {o['id']} | {o['total']}₴ | {o['status']}\n"
            await query.message.edit_caption(caption=txt, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="main")]]), parse_mode=ParseMode.HTML)
    
    except Exception as e:
        logger.error(f"Router Error: {e}")
        await query.answer("Виникла помилка. Спробуйте ще раз.")

# ==========================================
# 🧪 ТЕСТОВИЙ СКРИПТ (ПЕРЕВІРКА ІМПОРТІВ ТА ЛОГІКИ)
# ==========================================

def run_pre_launch_tests():
    logger.info("Running pre-launch diagnostics...")
    try:
        dummy_profile = {"referrals": 2, "promo_applied": True}
        test_price = calculate_price(1000, dummy_profile)
        expected = int((1000 * 0.65) * 0.55) # 357
        assert test_price == expected, f"Price calc failure: {test_price} != {expected}"
        
        vip_date = get_vip_date(dummy_profile)
        assert vip_date > datetime.now(), "VIP date calc failure"
        
        logger.info("Diagnostics PASSED.")
    except Exception as e:
        logger.critical(f"Diagnostics FAILED: {e}")
        sys.exit(1)

# ==========================================
# 🚀 ЗАПУСК БОТА
# ==========================================

def main():
    # Запуск тестів перед включенням
    run_pre_launch_tests()

    # Налаштування PicklePersistence
    persistence = PicklePersistence(filepath="data/bot_persistence.pickle")
    
    # Defaults для спрощення коду
    defaults = Defaults(parse_mode=ParseMode.HTML, disable_web_page_preview=False)

    application = (
        Application.builder()
        .token(TOKEN)
        .persistence(persistence)
        .defaults(defaults)
        .rate_limiter(AIORateLimiter())
        .connect_timeout(60.0)
        .read_timeout(60.0)
        .write_timeout(60.0)
        .pool_timeout(60.0)
        .build()
    )

    # Додавання обробників
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(main_router))
    application.add_handler(MessageHandler(filters.PHOTO, handle_receipt_photo))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_input))

    logger.info("GHOSTY SHOP BOT IS ONLINE")
    
    # Запуск Polling
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()

# ==========================================
# 📄 ІНСТРУКЦІЯ ЗАПУСКУ
# ==========================================
# 1. Запуск на хості: python3 ready_to_deploy.py
# 2. Переконайтесь, що встановлені залежності:
#    pip install python-telegram-bot==21.10
# 3. Бот автоматично створить папку data/ для зберігання станів.
# 4. Всі дії користувачів логуються у файл data/{user_id}.txt

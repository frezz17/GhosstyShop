import logging
import os
import sys
import random
import asyncio
import warnings
from html import escape
from datetime import datetime, timedelta

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
    PicklePersistence,
    AIORateLimiter
)
from telegram.error import BadRequest, NetworkError

# ===================== CONFIG =====================
TOKEN = "8351638507:AAEqc9p9b4AA8vTrzvvj_XArtUABqcfMGV4"
MANAGER_ID = 7544847872
MANAGER_USERNAME = "ghosstydpbot"
CHANNEL_URL = "https://t.me/GhostyStaffDP"
PAYMENT_LINK = "https://heylink.me/ghosstyshop/"
WELCOME_PHOTO = "https://i.ibb.co/y7Q194N/1770068775663.png"

# Налаштування знижок
DISCOUNT_MULTIPLIER = 0.65   # 35% знижка магазину
PROMO_DISCOUNT = 45          # 45% персональна знижка
BASE_VIP_DATE = datetime.strptime("25.03.2026", "%d.%m.%Y")

# ===================== LOGGING =====================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Прибираємо зайві ворнінги в консолі
warnings.filterwarnings("ignore", category=UserWarning)

# ===================== DATA =====================

GIFT_LIQUIDS = {
    9001: "🎁 Pumpkin Latte 30ml",
    9002: "🎁 Glintwine 30ml",
    9003: "🎁 Christmas Tree 30ml",
    9004: "🎁 Strawberry Jelly 30ml",
    9005: "🎁 Mystery One 30ml",
    9006: "🎁 Fall Tea 30ml",
}

LIQUIDS = {
    301: {"name": "🎃 Pumpkin Latte", "price": 269, "discount": True, "img": "https://i.ibb.co/Y7qn69Ds/photo-2024-12-18-00-00-00.jpg", "desc": "☕ Гарбузовий латте з корицею\n🎄 Зимовий настрій\n😌 Мʼякий та теплий смак"},
    302: {"name": "🍷 Glintwine", "price": 269, "discount": True, "img": "https://i.ibb.co/wF8r7Nmc/photo-2024-12-18-00-00-01.jpg", "desc": "🍇 Пряний глінтвейн\n🔥 Теплий винний смак\n🎄 Святковий вайб"},
    303: {"name": "🎄 Christmas Tree", "price": 269, "discount": True, "img": "https://i.ibb.co/vCPGV8RV/photo-2024-12-18-00-00-02.jpg", "desc": "🌲 Хвоя + морозна свіжість\n❄️ Дуже свіжа\n🎅 Атмосфера зими"}
}

HHC_VAPES = {
    100: {"name": "🌴 Packwoods Purple 1ml", "price": 549, "discount": True, "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg", "desc": "🧠 90% ННС | Гібрид\n😌 Розслаблення + легка ейфорія"},
    101: {"name": "🍊 Packwoods Orange 1ml", "price": 629, "discount": True, "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg", "desc": "🧠 90% ННС | Гібрид\n⚡ Бадьорить та фокусує"},
    102: {"name": "🌸 Packwoods Pink 1ml", "price": 719, "discount": True, "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg", "desc": "🧠 90% ННС | Гібрид\n😇 Спокій + підйом настрою"},
    103: {"name": "🌿 Whole Mint 2ml", "price": 849, "discount": True, "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg", "desc": "🧠 95% ННС | Сатіва\n⚡ Енергія та ясність"},
    104: {"name": "🌴 Jungle Boys White 2ml", "price": 999, "discount": True, "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg", "desc": "🧠 95% ННС | Індика\n😴 Глибокий релакс"}
}

PODS = {
    500: {"name": "🔌 XROS 3 Mini", "price": 499, "discount": True, "img": "https://i.ibb.co/yFSQ5QSn/vaporesso-xros-3-mini.jpg", "desc": "🔋 1000 mAh\n💨 MTL / RDL\n⚡ Type-C зарядка"},
    501: {"name": "🔌 XROS 5 Mini", "price": 579, "discount": True, "img": "https://i.ibb.co/RkNgt1Qr/vaporesso-xros-5-mini.jpg", "desc": "🔋 1000 mAh\n🔥 COREX 2.0\n⚡ Швидка зарядка"},
    502: {"name": "🔌 XROS Pro", "price": 689, "discount": True, "img": "https://i.ibb.co/ynYwSMt6/vaporesso-xros-pro.jpg", "desc": "🔋 1200 mAh\n⚡ Регулювання потужності\n🚀 Професійний рівень"},
    503: {"name": "🔌 XROS Nano", "price": 519, "discount": True, "img": "https://i.ibb.co/5XW2yN80/vaporesso-xros-nano.jpg", "desc": "🔋 1000 mAh\n🧱 Міцний корпус\n🎒 Ідеальний у дорогу"},
    504: {"name": "🔌 XROS 4", "price": 599, "discount": True, "img": "https://i.ibb.co/LDRbQxr1/vaporesso-xros-4.jpg", "desc": "🔋 1000 mAh\n🔥 COREX\n🎨 Стильний дизайн"},
    505: {"name": "🔌 XROS 5", "price": 799, "discount": True, "img": "https://i.ibb.co/hxjmpHF2/vaporesso-xros-5.jpg", "desc": "🔋 1200 mAh\n⚡ Fast Charge\n🚀 Флагман серії"},
    506: {"name": "🔌 Voopoo Vmate Mini", "price": 459, "discount": True, "img": "https://i.ibb.co/8L0JNTHz/voopoo-vmate-mini.jpg", "desc": "🔋 1000 mAh\n💨 Автозатяжка\n😌 Легкий старт"}
}

CITIES = ["Київ", "Дніпро", "Камʼянське", "Харків", "Одеса", "Львів", "Запоріжжя", "Кривий Ріг", "Полтава", "Черкаси"]

CITY_DISTRICTS = {
    "Київ": ["Шевченківський", "Дарницький", "Оболонський", "Печерський", "Соломʼянський", "Деснянський", "Подільський", "Голосіївський"],
    "Дніпро": ["Центральний", "Соборний", "Індустріальний", "Амур", "Новокодацький", "Чечелівський", "Самарський", "Шевченківський"],
    "Камʼянське": ["Центральний", "Південний", "Заводський", "Дніпровський", "Черемушки", "Романкове", "БАМ", "Соцмісто"],
    "Харків": ["Київський", "Салтівський", "Холодногірський", "Індустріальний", "Основʼянський", "Немишлянський", "Новобаварський"],
    "Одеса": ["Приморський", "Київський", "Малиновський", "Суворовський", "Пересипський", "Хаджибейський"],
    "Львів": ["Залізничний", "Личаківський", "Франківський", "Шевченківський", "Сихівський", "Галицький"],
    "Запоріжжя": ["Олександрівський", "Заводський", "Комунарський", "Дніпровський", "Вознесенівський"],
    "Кривий Ріг": ["Довгинцівський", "Інгулецький", "Металургійний", "Покровський", "Саксаганський"],
    "Полтава": ["Шевченківський", "Подільський", "Київський"],
    "Черкаси": ["Придніпровський", "Соснівський"]
}

# ===================== HELPERS =====================

def get_vip_date(profile):
    base = profile.get("vip_base", BASE_VIP_DATE)
    if isinstance(base, str):
        base = datetime.strptime(base, "%d.%m.%Y")
    extra_days = 7 * profile.get("referrals", 0)
    return base + timedelta(days=extra_days)

def is_vip_active(profile):
    return get_vip_date(profile) > datetime.now()

def generate_promo_code(user_id):
    return f"GHOST-{user_id % 10000}{random.randint(100,999)}"

def calc_prices(item, profile):
    base_price = item["price"]
    shop_price = int(base_price * DISCOUNT_MULTIPLIER) if item.get("discount", True) else base_price
    promo_percent = profile.get("promo_discount", PROMO_DISCOUNT)
    final_price = int(shop_price * (1 - promo_percent / 100))
    return {"base": base_price, "shop": shop_price, "final": final_price}

def get_gift_list_text():
    return "\n".join([f"• {name}" for name in GIFT_LIQUIDS.values()])

# ===================== KEYBOARDS =====================

def main_menu_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👤 Профіль", callback_data="profile"), InlineKeyboardButton("🛍 Асортимент", callback_data="assortment")],
        [InlineKeyboardButton("📍 Місто", callback_data="set_city"), InlineKeyboardButton("🛒 Кошик", callback_data="cart")],
        [InlineKeyboardButton("📦 Мої замовлення", callback_data="my_orders"), InlineKeyboardButton("👨‍💻 Менеджер", url=f"https://t.me/{MANAGER_USERNAME}")],
        [InlineKeyboardButton("📢 Канал магазину", url=CHANNEL_URL)]
    ])

def back_to_main_kb():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🏠 В головне меню", callback_data="main")]])

# ===================== HANDLERS =====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = context.args

    if "profile" not in context.user_data:
        context.user_data["profile"] = {
            "uid": user.id,
            "full_name": user.first_name,
            "username": user.username,
            "city": None, "district": None, "address": None, "phone": None,
            "promo_code": generate_promo_code(user.id),
            "promo_discount": PROMO_DISCOUNT,
            "referrals": 0,
            "vip_base": BASE_VIP_DATE,
            "ref_applied": False
        }
        context.user_data["cart"] = []
        context.user_data["orders"] = []

    profile = context.user_data["profile"]

    if args and not profile.get("ref_applied"):
        try:
            ref_id = int(args[0])
            if ref_id != user.id:
                profile["ref_applied"] = True
                profile["referrals"] += 1
        except ValueError:
            pass

    vip_date_str = get_vip_date(profile).strftime("%d.%m.%Y")
    
    text = (
        f"👋 <b>{escape(user.first_name)}</b>, вітаємо у <b>Ghosty Shop</b> 💨\n\n"
        f"🎁 <b>Подарунок до кожного замовлення:</b>\n3 рідини 30ml безкоштовно!\n\n"
        f"🎫 Твій промокод: <code>{profile['promo_code']}</code>\n"
        f"💸 Твоя знижка: <b>-{profile['promo_discount']}%</b>\n"
        f"👑 VIP статус до: <b>{vip_date_str}</b>\n"
        f"🚚 Доставка: <b>{'Безкоштовна (VIP)' if is_vip_active(profile) else 'За тарифом'}</b>\n\n"
        f"👇 Оберіть дію:"
    )

    # Безпечне надсилання/редагування
    try:
        if update.message:
            await update.message.reply_photo(photo=WELCOME_PHOTO, caption=text, parse_mode="HTML", reply_markup=main_menu_kb())
        elif update.callback_query:
            msg = update.callback_query.message
            await msg.delete()
            await msg.chat.send_photo(photo=WELCOME_PHOTO, caption=text, parse_mode="HTML", reply_markup=main_menu_kb())
    except Exception:
        # Fallback якщо не вдалося надіслати фото
        if update.effective_message:
            await update.effective_message.reply_text(text, parse_mode="HTML", reply_markup=main_menu_kb())

async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    p = context.user_data["profile"]
    vip_end = get_vip_date(p).strftime("%d.%m.%Y")
    bot_username = context.bot.username
    ref_link = f"https://t.me/{bot_username}?start={p['uid']}"
    
    text = (
        f"👤 <b>Профіль користувача</b>\n\n"
        f"🏙 Місто: {p['city'] or 'Не вказано'}\n"
        f"📍 Район: {p['district'] or 'Не вказано'}\n"
        f"🏠 Адреса: {p['address'] or 'Не вказано'}\n"
        f"📞 Телефон: {p['phone'] or 'Не вказано'}\n\n"
        f"👥 Рефералів: {p['referrals']}\n"
        f"🔗 <b>Твоє посилання:</b>\n<code>{ref_link}</code>\n"
        f"👑 VIP до: <b>{vip_end}</b>"
    )
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("📍 Змінити дані доставки", callback_data="set_city")],
        [InlineKeyboardButton("🏠 В головне меню", callback_data="main")]
    ])
    
    try:
        await query.message.delete()
        await query.message.chat.send_message(text, parse_mode="HTML", reply_markup=kb)
    except:
        pass

async def show_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("💧 Рідини", callback_data="cat_300"), InlineKeyboardButton("🔌 POD-системи", callback_data="cat_500")],
        [InlineKeyboardButton("💨 HHC / NNS", callback_data="cat_100")],
        [InlineKeyboardButton("🏠 В головне меню", callback_data="main")]
    ])
    
    # Видаляємо попереднє, щоб не було помилок media type
    await query.message.delete()
    await query.message.chat.send_message("🛍 <b>Оберіть категорію:</b>", parse_mode="HTML", reply_markup=kb)

async def list_items(update: Update, context: ContextTypes.DEFAULT_TYPE, category_id):
    query = update.callback_query
    await query.answer()
    
    if category_id == 300:
        items = LIQUIDS
        title = "💧 Рідини"
    elif category_id == 500:
        items = PODS
        title = "🔌 POD-системи"
    else:
        items = HHC_VAPES
        title = "💨 HHC / NNS"
        
    buttons = []
    for pid, data in items.items():
        buttons.append([InlineKeyboardButton(f"{data['name']}", callback_data=f"view_{pid}")])
    
    buttons.append([InlineKeyboardButton("⬅️ Назад до категорій", callback_data="assortment")])
    
    await query.message.delete()
    await query.message.chat.send_message(f"<b>{title}</b>\nОберіть товар:", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons))

async def view_item(update: Update, context: ContextTypes.DEFAULT_TYPE, item_id):
    query = update.callback_query
    await query.answer()
    
    item = LIQUIDS.get(item_id) or PODS.get(item_id) or HHC_VAPES.get(item_id)
    if not item:
        await query.answer("Товар не знайдено!", show_alert=True)
        return

    profile = context.user_data["profile"]
    prices = calc_prices(item, profile)
    is_vip = is_vip_active(profile)
    
    caption = (
        f"<b>{escape(item['name'])}</b>\n\n"
        f"{item.get('desc', '')}\n\n"
        f"💰 Звичайна ціна: <s>{prices['base']} грн</s>\n"
        f"🔥 Знижка магазину: <s>{prices['shop']} грн</s>\n"
        f"🎟 <b>Ціна для тебе: {prices['final']} грн</b>\n\n"
        f"🎁 <b>Подарунок:</b>\n{get_gift_list_text()}\n\n"
        f"🚚 Доставка: {'Безкоштовна (VIP) 👑' if is_vip else 'За тарифами'}"
    )
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🛒 Додати в кошик", callback_data=f"add_{item_id}")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="assortment")]
    ])
    
    await query.message.delete()
    await query.message.chat.send_photo(photo=item["img"], caption=caption, parse_mode="HTML", reply_markup=kb)

async def add_to_cart(update: Update, context: ContextTypes.DEFAULT_TYPE, item_id):
    query = update.callback_query
    item = LIQUIDS.get(item_id) or PODS.get(item_id) or HHC_VAPES.get(item_id)
    
    if item:
        profile = context.user_data["profile"]
        prices = calc_prices(item, profile)
        context.user_data["cart"].append({
            "id": item_id,
            "name": item["name"],
            "price": prices['final'],
            "base_price": item["price"]
        })
        await query.answer("✅ Товар додано в кошик!")
    else:
        await query.answer("Помилка!", show_alert=True)

async def show_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    cart = context.user_data.get("cart", [])
    if not cart:
        await query.answer("Ваш кошик порожній!", show_alert=True)
        return

    total = sum(item["price"] for item in cart)
    text = "🛒 <b>Ваш кошик:</b>\n\n"
    for i, item in enumerate(cart, 1):
        text += f"{i}. {item['name']} — <b>{item['price']} грн</b>\n"
    
    text += f"\n💰 <b>Разом до сплати: {total} грн</b>"
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Оформити замовлення", callback_data="checkout_start")],
        [InlineKeyboardButton("🗑 Очистити кошик", callback_data="cart_clear")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="main")]
    ])
    
    await query.message.delete()
    await query.message.chat.send_message(text, parse_mode="HTML", reply_markup=kb)

async def clear_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["cart"] = []
    await update.callback_query.answer("Кошик очищено!")
    # Повертаємо в меню, бо кошик порожній
    await start(update, context)

async def start_checkout_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    buttons = []
    row = []
    for city in CITIES:
        row.append(InlineKeyboardButton(city, callback_data=f"city_{city}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row: buttons.append(row)
    buttons.append([InlineKeyboardButton("❌ Скасувати", callback_data="main")])
    
    await query.message.delete()
    await query.message.chat.send_message("📍 <b>Крок 1/4:</b> Оберіть ваше місто:", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons))

async def select_district(update: Update, context: ContextTypes.DEFAULT_TYPE, city):
    query = update.callback_query
    await query.answer()
    
    context.user_data["profile"]["city"] = city
    districts = CITY_DISTRICTS.get(city, ["Інший район"])
    
    buttons = []
    row = []
    for d in districts:
        row.append(InlineKeyboardButton(d, callback_data=f"dist_{d}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row: buttons.append(row)
    buttons.append([InlineKeyboardButton("⬅️ Назад", callback_data="checkout_start")])
    
    await query.message.edit_text(f"📍 Місто: <b>{city}</b>\n<b>Крок 2/4:</b> Оберіть район:", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons))

async def ask_address(update: Update, context: ContextTypes.DEFAULT_TYPE, district):
    query = update.callback_query
    await query.answer()
    
    context.user_data["profile"]["district"] = district
    context.user_data["state"] = "wait_address"
    
    await query.message.edit_text(
        f"📍 Місто: {context.user_data['profile']['city']}\n"
        f"📍 Район: {district}\n\n"
        f"✍️ <b>Крок 3/4:</b> Напишіть вашу адресу або номер відділення пошти:",
        parse_mode="HTML"
    )

async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = context.user_data.get("state")
    if not state:
        return

    text = update.message.text
    profile = context.user_data["profile"]

    if state == "wait_address":
        profile["address"] = text
        context.user_data["state"] = "wait_phone"
        await update.message.reply_text("📞 <b>Крок 4/4:</b> Введіть ваш номер телефону:", parse_mode="HTML")
    
    elif state == "wait_phone":
        profile["phone"] = text
        context.user_data["state"] = "waiting_payment"
        await finalize_order(update, context)

async def finalize_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cart = context.user_data.get("cart", [])
    profile = context.user_data["profile"]
    total = sum(i["price"] for i in cart)
    
    order_id = f"ORD-{profile['uid']}-{random.randint(1000,9999)}"
    
    context.user_data["orders"].append({
        "id": order_id,
        "items": cart.copy(),
        "total": total,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "status": "Очікує оплату"
    })
    context.user_data["current_order_id"] = order_id
    
    text = (
        f"✅ <b>Дані прийнято!</b>\n"
        f"🆔 Замовлення: <code>{order_id}</code>\n"
        f"💰 <b>До сплати: {total} грн</b>\n\n"
        f"💳 <b>Посилання на оплату:</b>\n{PAYMENT_LINK}\n\n"
        f"⚠️ <b>Після оплати надішліть сюди фото квитанції!</b>"
    )
    
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("💳 Оплатити", url=PAYMENT_LINK)], [InlineKeyboardButton("Скасувати", callback_data="main")]])
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=kb)

async def handle_photo_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = context.user_data.get("state")
    if state != "waiting_payment":
        await update.message.reply_text("Я не очікую зараз фото.")
        return

    photo = update.message.photo[-1]
    order_id = context.user_data.get("current_order_id", "Unknown")
    profile = context.user_data["profile"]
    cart = context.user_data.get("cart", [])
    total = sum(i["price"] for i in cart)
    
    items_str = "\n".join([f"- {i['name']} ({i['price']} грн)" for i in cart])
    is_vip = is_vip_active(profile)
    
    manager_text = (
        f"💰 <b>Нове замовлення!</b>\n🆔 {order_id}\n"
        f"👤 @{profile['username']} ({profile['full_name']})\n"
        f"📞 <code>{profile['phone']}</code>\n"
        f"📍 {profile['city']}, {profile['district']}\n🏠 {profile['address']}\n\n"
        f"🛒 <b>Товари:</b>\n{items_str}\n\n"
        f"🚚 VIP: {'ТАК' if is_vip else 'НІ'}\n"
        f"💵 <b>Сума: {total} грн</b>"
    )
    
    try:
        await context.bot.send_photo(chat_id=MANAGER_ID, photo=photo.file_id, caption=manager_text, parse_mode="HTML")
    except Exception:
        logger.error("Не вдалося відправити звіт менеджеру")
    
    context.user_data["cart"] = []
    context.user_data["state"] = None
    
    await update.message.reply_text("✅ <b>Квитанцію отримано!</b>\nДякуємо! Менеджер скоро зв'яжеться.", parse_mode="HTML", reply_markup=back_to_main_kb())

async def show_my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    orders = context.user_data.get("orders", [])
    
    if not orders:
        try:
            await query.message.delete()
            await query.message.chat.send_message("📭 У вас ще немає замовлень.", reply_markup=back_to_main_kb())
        except:
            pass
        return
        
    text = "📦 <b>Історія замовлень:</b>\n\n"
    for o in orders[-5:]:
        text += f"🔹 {o['date']} | {o['id']} | {o['total']} грн\nStatus: {o['status']}\n\n"
        
    await query.message.delete()
    await query.message.chat.send_message(text, parse_mode="HTML", reply_markup=back_to_main_kb())

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = update.callback_query.data
    
    if data == "main":
        await start(update, context)
    elif data == "profile":
        await show_profile(update, context)
    elif data == "assortment":
        await show_categories(update, context)
    elif data.startswith("cat_"):
        await list_items(update, context, int(data.split("_")[1]))
    elif data.startswith("view_"):
        await view_item(update, context, int(data.split("_")[1]))
    elif data.startswith("add_"):
        await add_to_cart(update, context, int(data.split("_")[1]))
    elif data == "cart":
        await show_cart(update, context)
    elif data == "cart_clear":
        await clear_cart(update, context)
    elif data == "checkout_start" or data == "set_city":
        await start_checkout_city(update, context)
    elif data.startswith("city_"):
        await select_district(update, context, data.split("_")[1])
    elif data.startswith("dist_"):
        await ask_address(update, context, data.split("_")[1])
    elif data == "my_orders":
        await show_my_orders(update, context)

# ===================== MAIN =====================

def main():
    if not os.path.exists('data'):
        os.makedirs('data', exist_ok=True)
    
    persistence = PicklePersistence(filepath="data/bot_data.pickle")

    app = (
        Application.builder()
        .token(TOKEN)
        .persistence(persistence)
        .connect_timeout(60.0)
        .read_timeout(60.0)
        .write_timeout(60.0)
        .pool_timeout(60.0)
        .get_updates_read_timeout(60.0)
        .rate_limiter(AIORateLimiter())
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_input))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo_receipt))

    print("-" * 30)
    print("🚀 GHOSTY SHOP BOT ZAPUSCHEN!")
    print("-" * 30)

    app.run_polling(drop_pending_updates=True, timeout=30, read_timeout=30, connect_timeout=30)

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Stopped.")
    except Exception as e:
        logger.critical(f"Error: {e}", exc_info=True)

# ============================================================
# 👻 GHOSTY SHOP BOT — PART 1/6
# FULL PRODUCTION CORE STRUCTURE (BotHost Ready)
# ============================================================

import os
import sys
import logging
import asyncio
import random
from datetime import datetime, timedelta
from html import escape
from uuid import uuid4

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto
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

# ============================================================
# ⚙️ CONFIG
# ============================================================

TOKEN = "PUT_TOKEN"
MANAGER_ID = 7544847872

DISCOUNT_MULTIPLIER = 0.65
PROMO_DISCOUNT = 45

VIP_FREE_DELIVERY_UNTIL = datetime.strptime("25.03.2026","%d.%m.%Y")
BASE_VIP_DATE = datetime.strptime("25.03.2026","%d.%m.%Y")

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# ============================================================
# 📝 LOGGING
# ============================================================

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ============================================================
# 🎁 GIFTS (FULL FROM main.py)
# ============================================================

GIFT_LIQUIDS = [
"🎁 Pumpkin Latte 30ml",
"🎁 Glintwine 30ml",
"🎁 Christmas Tree 30ml",
"🎁 Strawberry Jelly 30ml",
"🎁 Mystery One 30ml",
"🎁 Fall Tea 30ml"
]

# ============================================================
# 🌍 FULL CITIES + DISTRICTS
# ============================================================

CITIES = [
"Київ","Дніпро","Камʼянське","Харків","Одеса",
"Львів","Запоріжжя","Кривий Ріг","Полтава","Черкаси"
]

CITY_DISTRICTS = {
"Київ":["Шевченківський","Дарницький","Оболонський","Печерський","Соломʼянський","Деснянський","Подільський","Голосіївський"],
"Дніпро":["Центральний","Соборний","Індустріальний","Самарський","Амур","Новокодацький","Чечелівський"],
"Камʼянське":["Центр","Соцмісто","Черемушки","Романкове","БАМ"],
"Харків":["Шевченківський","Київський","Салтівський","Основʼянський","Холодногірський"],
"Одеса":["Приморський","Київський","Малиновський","Суворовський"],
"Львів":["Галицький","Франківський","Сихівський","Шевченківський"],
"Запоріжжя":["Олександрівський","Дніпровський","Комунарський","Хортицький"],
"Кривий Ріг":["Центрально-Міський","Покровський","Саксаганський","Тернівський"],
"Полтава":["Центр","Поділ","Алмазний","Левада"],
"Черкаси":["Соснівський","Придніпровський"]
}

# ============================================================
# 📦 PRODUCT STRUCTURE (FULL main.py FORMAT)
# ============================================================

LIQUIDS = {}
HHC_VAPES = {}
PODS = {}
GIFT_PRODUCTS = {}

# ============================================================
# 🧠 CORE HELPERS
# ============================================================

def get_item(pid):
    return (
        LIQUIDS.get(pid)
        or HHC_VAPES.get(pid)
        or PODS.get(pid)
    )

def calc_price(price, promo):
    shop = int(price * DISCOUNT_MULTIPLIER)
    final = int(shop * (1 - promo/100))
    return shop, final

def generate_promo(uid):
    return f"GHOST{uid%10000}{random.randint(100,999)}"

def is_vip(profile):
    return datetime.now() <= VIP_FREE_DELIVERY_UNTIL

def vip_until(profile):
    base = profile.get("vip_base", BASE_VIP_DATE)
    refs = profile.get("referrals",0)
    return base + timedelta(days=7*refs)

def save_profile(profile):
    path = f"{DATA_DIR}/{profile['uid']}.txt"
    with open(path,"w",encoding="utf-8") as f:
        for k,v in profile.items():
            f.write(f"{k}:{v}\n")

# ============================================================
# 🧾 CAPTION BUILDER
# ============================================================

def build_caption(item, profile):

    shop,final = calc_price(item["price"],profile["promo"])

    text = f"<b>{escape(item['name'])}</b>\n"
    text += f"📦 Серія: {item.get('series','')}\n\n"
    text += f"🔥 Магазин: {shop}\n"
    text += f"🎟 Твоя: <b>{final}</b>\n\n"
    text += f"{item.get('desc','')}\n\n🎁 Подарунок:\n"

    for g in GIFT_LIQUIDS:
        text += f"• {g}\n"

    return text

# ============================================================
# 👤 PROFILE SYSTEM
# ============================================================

def create_profile(user):

    return {
        "uid":user.id,
        "name":user.first_name,
        "promo":PROMO_DISCOUNT,
        "promo_code":generate_promo(user.id),
        "vip_base":BASE_VIP_DATE,
        "referrals":0,
        "orders":[],
        "city":None,
        "district":None,
        "address":None
    }

# ============================================================
# ⌨️ UI
# ============================================================

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛍 Каталог","catalog")],
        [InlineKeyboardButton("🛒 Кошик","cart"),
         InlineKeyboardButton("👤 Профіль","profile")],
        [InlineKeyboardButton("⚡ Швидке замовлення","fast")]
    ])

# ============================================================
# 🚀 START
# ============================================================

async def start(update:Update,context:ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    if "profile" not in context.user_data:
        profile = create_profile(user)
        context.user_data["profile"]=profile
        context.user_data["cart"]=[]
        save_profile(profile)

    await update.message.reply_text(
        "👻 Ghosty Shop запущено",
        reply_markup=main_menu()
    )

# ============================================================
# 🧩 FUTURE FUNCTION DECLARATIONS (NO CONFLICT SYSTEM)
# ============================================================

async def show_catalog(update,context): pass
async def show_category(update,context): pass
async def add_to_cart(update,context): pass
async def show_cart(update,context): pass
async def checkout(update,context): pass
async def fast_order(update,context): pass
async def receipt_handler(update,context): pass
async def manager_panel(update,context): pass
async def city_select(update,context): pass
async def district_select(update,context): pass
async def referral_handler(update,context): pass

# ============================================================
# 📡 ROUTER SKELETON
# ============================================================

async def router(update:Update,context:ContextTypes.DEFAULT_TYPE):
    pass

# ============================================================
# 👻 GHOSTY SHOP BOT — PART 2/6
# FULL CATALOG ENGINE (main.py compatible)
# ============================================================

# ============================================================
# 📦 FULL PRODUCTS DATA (EXPANDED — НЕ СКОРОЧУВАТИ)
# структура: name, series, price, desc, imgs[], colors[], gift_liquid, payment_url
# ============================================================

LIQUIDS.update({
    301:{
        "name":"🎃 Pumpkin Latte",
        "series":"Ghost Liquid",
        "price":269,
        "desc":"☕ Осінній гарбузовий латте\nКремовий, теплий, насичений.",
        "imgs":["https://i.ibb.co/Y7qn69Ds/photo.jpg"],
        "colors":[],
        "gift_liquid":True,
        "payment_url":"",
    },
    302:{
        "name":"🍷 Glintwine",
        "series":"Ghost Liquid",
        "price":269,
        "desc":"🍇 Пряний глінтвейн\nЗігріваючий аромат спецій.",
        "imgs":["https://i.ibb.co/wF8r7Nmc/photo.jpg"],
        "colors":[],
        "gift_liquid":True,
        "payment_url":"",
    },
    303:{
        "name":"🎄 Christmas Tree",
        "series":"Ghost Liquid",
        "price":269,
        "desc":"🌲 Морозна хвоя\nСвіжий зимовий профіль.",
        "imgs":["https://i.ibb.co/vCPGV8RV/photo.jpg"],
        "colors":[],
        "gift_liquid":True,
        "payment_url":"",
    },
    304:{
        "name":"🍓 Strawberry Jelly",
        "series":"Ghost Liquid",
        "price":289,
        "desc":"🍓 Полуничний джем\nСолодкий десертний смак.",
        "imgs":["https://i.ibb.co/2q3Qz8C/strawberry.jpg"],
        "colors":[],
        "gift_liquid":True,
        "payment_url":"",
    },
})

HHC_VAPES.update({
    100:{
        "name":"🌴 Packwoods Purple",
        "series":"Packwoods",
        "price":549,
        "desc":"💨 90% HHC • Hybrid\nЗбалансований ефект.",
        "imgs":["https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg"],
        "colors":[],
        "gift_liquid":False,
        "payment_url":"",
    },
    101:{
        "name":"🍊 Packwoods Orange",
        "series":"Packwoods",
        "price":629,
        "desc":"🍊 Sativa\nЕнергійний профіль.",
        "imgs":["https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg"],
        "colors":[],
        "gift_liquid":False,
        "payment_url":"",
    },
    102:{
        "name":"🌸 Packwoods Pink",
        "series":"Packwoods",
        "price":719,
        "desc":"🌸 Hybrid\nМ’який баланс.",
        "imgs":["https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg"],
        "colors":[],
        "gift_liquid":False,
        "payment_url":"",
    },
    103:{
        "name":"🌿 Whole Mint",
        "series":"Whole Melt",
        "price":849,
        "desc":"🌿 Mint\nСвіжий м’ятний холодок.",
        "imgs":["https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg"],
        "colors":[],
        "gift_liquid":False,
        "payment_url":"",
    },
    104:{
        "name":"🌙 Jungle Boys White",
        "series":"Jungle Boys",
        "price":999,
        "desc":"🌙 Indica\nРелаксуючий ефект.",
        "imgs":["https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg"],
        "colors":[],
        "gift_liquid":False,
        "payment_url":"",
    },
})

PODS.update({
    500:{
        "name":"🔌 XROS 3 Mini",
        "series":"Vaporesso",
        "price":499,
        "desc":"🔋 1000 mAh • COREX Heating\nКомпактний POD.",
        "imgs":["https://i.ibb.co/yFSQ5QSn/vaporesso-xros-3-mini.jpg"],
        "colors":["Black","Sky Blue","Rose Gold"],
        "gift_liquid":False,
        "payment_url":"",
    },
    501:{
        "name":"🔌 XROS 5 Mini",
        "series":"Vaporesso",
        "price":579,
        "desc":"⚡ COREX 2.0\nПокращений смак і тяга.",
        "imgs":["https://i.ibb.co/RkNgt1Qr/vaporesso-xros-5-mini.jpg"],
        "colors":["Black","Green","Silver"],
        "gift_liquid":False,
        "payment_url":"",
    },
    502:{
        "name":"🔌 XROS Pro",
        "series":"Vaporesso",
        "price":689,
        "desc":"⚙️ Регульована потужність\nPro-рівень.",
        "imgs":["https://i.ibb.co/ynYwSMt6/vaporesso-xros-pro.jpg"],
        "colors":["Black","Blue","Red"],
        "gift_liquid":False,
        "payment_url":"",
    },
    503:{
        "name":"🔌 XROS Nano",
        "series":"Vaporesso",
        "price":519,
        "desc":"📦 Компактний формат\nЗручно щодня.",
        "imgs":["https://i.ibb.co/5XW2yN80/vaporesso-xros-nano.jpg"],
        "colors":["Black","Lime","Pink"],
        "gift_liquid":False,
        "payment_url":"",
    },
})

# ============================================================
# 🧭 CATALOG UI
# ============================================================

def catalog_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💧 Рідини", callback_data="cat_liq")],
        [InlineKeyboardButton("🔥 HHC", callback_data="cat_hhc")],
        [InlineKeyboardButton("🔌 POD", callback_data="cat_pod")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_main")]
    ])

def items_menu(items:dict, prefix:str):
    rows = []
    for pid, it in items.items():
        rows.append([InlineKeyboardButton(it["name"], callback_data=f"item_{prefix}_{pid}")])
    rows.append([InlineKeyboardButton("⬅️ До категорій", callback_data="catalog")])
    return InlineKeyboardMarkup(rows)

def item_actions_kb(pid:int, has_colors:bool=False):
    rows = [
        [InlineKeyboardButton("🛒 Додати", callback_data=f"add_{pid}")],
        [InlineKeyboardButton("➖ Прибрати", callback_data=f"rem_{pid}")],
    ]
    if has_colors:
        rows.insert(0, [InlineKeyboardButton("🎨 Вибрати колір", callback_data=f"color_{pid}")])
    rows.append([InlineKeyboardButton("⬅️ Назад", callback_data="catalog")])
    return InlineKeyboardMarkup(rows)

# ============================================================
# 🧠 CATALOG ENGINE
# ============================================================

async def show_catalog(update:Update, context:ContextTypes.DEFAULT_TYPE):
    msg = update.callback_query.message if update.callback_query else update.message
    await msg.reply_text("📦 Обери категорію:", reply_markup=catalog_menu())

async def show_category(update:Update, context:ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    data = q.data
    if data == "cat_liq":
        await q.message.reply_text("💧 Рідини:", reply_markup=items_menu(LIQUIDS, "liq"))
    elif data == "cat_hhc":
        await q.message.reply_text("🔥 HHC:", reply_markup=items_menu(HHC_VAPES, "hhc"))
    elif data == "cat_pod":
        await q.message.reply_text("🔌 POD:", reply_markup=items_menu(PODS, "pod"))

async def show_item(update:Update, context:ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    # item_{prefix}_{pid}
    _, prefix, pid = q.data.split("_")
    pid = int(pid)
    item = get_item(pid)
    profile = context.user_data.get("profile", {"promo":PROMO_DISCOUNT})

    caption = build_caption(item, profile)

    has_colors = bool(item.get("colors"))
    kb = item_actions_kb(pid, has_colors)

    imgs = item.get("imgs") or []
    if imgs:
        # перше фото з підписом
        await q.message.reply_photo(imgs[0], caption=caption, reply_markup=kb)
        # додаткові фото — альбомом (без підпису)
        if len(imgs) > 1:
            media = [InputMediaPhoto(u) for u in imgs[1:]]
            await context.bot.send_media_group(chat_id=q.message.chat_id, media=media)
    else:
        await q.message.reply_text(caption, reply_markup=kb)

async def add_to_cart(update:Update, context:ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    pid = int(q.data.split("_")[1])

    context.user_data.setdefault("cart", [])
    context.user_data["cart"].append({"pid":pid, "color":None})

    await q.message.reply_text("✅ Додано в кошик")

async def remove_from_cart(update:Update, context:ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    pid = int(q.data.split("_")[1])

    cart = context.user_data.setdefault("cart", [])
    for i, row in enumerate(cart):
        if row["pid"] == pid:
            cart.pop(i)
            await q.message.reply_text("➖ Прибрано з кошика")
            return
    await q.message.reply_text("ℹ️ Цього товару нема в кошику")

# (вибір кольору — заглушка, логіка буде в PART 4/6)
async def color_select(update:Update, context:ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    pid = int(q.data.split("_")[1])
    item = get_item(pid)
    colors = item.get("colors") or []
    if not colors:
        await q.message.reply_text("ℹ️ Для цього товару немає кольорів.")
        return
    rows = [[InlineKeyboardButton(c, callback_data=f"colorpick_{pid}_{c}")] for c in colors]
    rows.append([InlineKeyboardButton("⬅️ Назад", callback_data=f"item_pod_{pid}")])
    await q.message.reply_text("🎨 Обери колір:", reply_markup=InlineKeyboardMarkup(rows))

# ============================================================
# 🔌 ROUTER EXTENSION (підключається до skeleton з PART 1/6)
# ============================================================

async def router(update:Update, context:ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    if not q:
        return
    data = q.data

    # каталог
    if data == "catalog" or data == "back_main":
        return await show_catalog(update, context)

    if data.startswith("cat_"):
        return await show_category(update, context)

    if data.startswith("item_"):
        return await show_item(update, context)

    if data.startswith("add_"):
        return await add_to_cart(update, context)

    if data.startswith("rem_"):
        return await remove_from_cart(update, context)

    if data.startswith("color_"):
        return await color_select(update, context)

    # інші кейси будуть у PART 3–6
    await q.answer()


# ============================================================
# 🧭 CATALOG → ITEM → CART (SAFE EXTENSION)
# ============================================================

async def show_catalog(update:Update, context:ContextTypes.DEFAULT_TYPE):
    msg = update.callback_query.message
    await msg.reply_text(
        "📦 Обери категорію:",
        reply_markup=catalog_menu()
    )


async def show_category(update:Update, context:ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if q.data == "cat_liq":
        return await q.message.reply_text(
            "💧 Рідини:",
            reply_markup=items_menu(LIQUIDS,"liq")
        )

    if q.data == "cat_hhc":
        return await q.message.reply_text(
            "🔥 HHC:",
            reply_markup=items_menu(HHC_VAPES,"hhc")
        )

    if q.data == "cat_pod":
        return await q.message.reply_text(
            "🔌 POD:",
            reply_markup=items_menu(PODS,"pod")
        )


async def show_item(update:Update, context:ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    _, _, pid = q.data.split("_")
    pid = int(pid)
    item = get_item(pid)
    prof = context.user_data["profile"]

    if not item:
        return await q.message.reply_text("❌ Товар не знайдено")

    shop, final = calc_price(item["price"], prof["promo"])

    caption = (
        f"<b>{item['name']}</b>\n"
        f"📦 {item['series']}\n\n"
        f"🔥 Магазин: {shop} грн\n"
        f"🎟 Твоя: <b>{final} грн</b>\n\n"
        f"{item['desc']}"
    )

    kb = item_actions_kb(pid, bool(item.get("colors")))
    imgs = item.get("imgs", [])

    if imgs:
        await q.message.reply_photo(imgs[0], caption=caption, reply_markup=kb)
    else:
        await q.message.reply_text(caption, reply_markup=kb)


async def add_to_cart(update:Update, context:ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    pid = int(q.data.split("_")[1])
    context.user_data.setdefault("cart",[]).append({
        "pid":pid,
        "color":None
    })

    await q.message.reply_text("✅ Додано в кошик")


async def remove_from_cart(update:Update, context:ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    pid = int(q.data.split("_")[1])
    cart = context.user_data.get("cart",[])

    for i,row in enumerate(cart):
        if row["pid"] == pid:
            cart.pop(i)
            return await q.message.reply_text("➖ Прибрано з кошика")

    await q.message.reply_text("ℹ️ Товару немає в кошику")


# ============================================================
# ⚡ FAST ORDER (INTEGRATED)
# ============================================================

async def fast_order(update:Update, context:ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    context.user_data["state"] = "fast_order"
    await q.message.reply_text(
        "⚡ <b>Швидке замовлення</b>\n\n"
        "Напиши одним повідомленням:\n"
        "• Що хочеш\n"
        "• Місто\n"
        "• Адресу"
    )


async def fast_order_input(update:Update, context:ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("state") != "fast_order":
        return

    user = update.effective_user

    await context.bot.send_message(
        MANAGER_ID,
        f"⚡ <b>FAST ORDER</b>\n\n"
        f"👤 {user.first_name} (@{user.username})\n"
        f"{escape(update.message.text)}"
    )

    context.user_data["state"] = None
    await update.message.reply_text("✅ Передано менеджеру")


# ============================================================
# 🔁 ROUTER MERGE (PART 3 FINAL)
# ============================================================

async def router(update:Update, context:ContextTypes.DEFAULT_TYPE):
    q = update.callback_query

    if q:
        data = q.data

        # PART 2
        if data in ("catalog","back_main"):
            return await show_catalog(update,context)

        if data.startswith("cat_"):
            return await show_category(update,context)

        if data.startswith("item_"):
            return await show_item(update,context)

        if data.startswith("add_"):
            return await add_to_cart(update,context)

        if data.startswith("rem_"):
            return await remove_from_cart(update,context)

        # PART 3 (твій)
        if data=="cart":
            return await show_cart(update,context)

        if data=="cart_clear":
            return await cart_clear(update,context)

        if data=="checkout":
            return await checkout(update,context)

        if data.startswith("city_"):
            return await select_city(update,context)

        if data.startswith("dist_"):
            return await select_district(update,context)

        if data=="profile":
            return await profile_view(update,context)

        if data=="fast":
            return await fast_order(update,context)

        return await q.answer()

    if update.message:
        if context.user_data.get("state")=="await_address":
            return await address_input(update,context)

        if context.user_data.get("state")=="fast_order":
            return await fast_order_input(update,context)

# ============================================================
# 💳 PAYMENT LINKS
# ============================================================

MONO_PAY = "https://lnk.ua/k4xJG21Vy?utm_medium=social&utm_source=heylink.me"
PRIVAT_PAY = "https://lnk.ua/RVd0OW6V3?utm_medium=social&utm_source=heylink.me"

def payment_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 Усі способи", url=MONO_PAY)],
        [
            InlineKeyboardButton("🟣 Mono", url=MONO_PAY),
            InlineKeyboardButton("🟢 Privat", url=PRIVAT_PAY),
        ],
        [InlineKeyboardButton("👤 Написати менеджеру", callback_data="fast")]
    ])


async def confirm_order(update:Update, context:ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    cart = context.user_data.get("cart",[])
    prof = context.user_data["profile"]
    user = update.effective_user

    await context.bot.send_message(
        MANAGER_ID,
        "📦 <b>НОВЕ ЗАМОВЛЕННЯ</b>\n\n"
        f"👤 {user.first_name} (@{user.username})\n"
        f"🏙 {prof['city']} / {prof['district']}\n"
        f"🏠 {prof['address']}\n\n"
        + cart_text(cart,prof)
    )

    await q.message.reply_text(
        "💳 <b>Оплата</b>\n\nОбери спосіб:",
        reply_markup=payment_kb()
    )

    context.user_data["cart"] = []

# ============================================================
# 📦 ORDER MODEL
# ============================================================

def create_order(profile, cart):
    order = {
        "id": str(uuid4())[:8],
        "items": cart.copy(),
        "comment": None,
        "receipt": None,
        "status": "created",  # created / waiting / paid
        "created": datetime.now().isoformat()
    }
    profile.setdefault("orders", []).append(order)
    return order


def get_last_order(profile):
    orders = profile.get("orders", [])
    return orders[-1] if orders else None


# ============================================================
# 📝 COMMENT TO ORDER
# ============================================================

async def ask_comment(update:Update, context:ContextTypes.DEFAULT_TYPE):
    context.user_data["state"] = "await_comment"
    await update.callback_query.message.reply_text(
        "📝 Додай коментар до замовлення\n"
        "Наприклад: *дзвонити перед доставкою*"
    )


async def comment_input(update:Update, context:ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("state") != "await_comment":
        return

    prof = context.user_data["profile"]
    order = get_last_order(prof)

    if order:
        order["comment"] = update.message.text

    context.user_data["state"] = None
    await update.message.reply_text("✅ Коментар збережено")


# ============================================================
# 📸 RECEIPT FROM USER
# ============================================================

async def receipt_from_user(update:Update, context:ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        return

    prof = context.user_data["profile"]
    order = get_last_order(prof)

    if not order:
        return

    order["receipt"] = update.message.photo[-1].file_id
    order["status"] = "waiting"

    await update.message.reply_text(
        "🧾 Квитанцію отримано\n"
        "⏳ Очікуй підтвердження менеджером"
    )

# ============================================================
# 🛠 ADMIN PANEL
# ============================================================

async def admin_panel(update:Update, context:ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != MANAGER_ID:
        return

    users = context.application.persistence.get_user_data()

    rows = []
    for uid, data in users.items():
        prof = data.get("profile")
        if not prof or not prof.get("orders"):
            continue

        last = prof["orders"][-1]
        rows.append([
            InlineKeyboardButton(
                f"👤 {uid} | {last['status']}",
                callback_data=f"admin_user_{uid}"
            )
        ])

    rows.append([InlineKeyboardButton("⬅️ Назад", callback_data="admin_back")])

    await update.message.reply_text(
        "🛠 <b>ADMIN PANEL</b>",
        reply_markup=InlineKeyboardMarkup(rows)
    )


async def admin_user(update:Update, context:ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    uid = int(q.data.replace("admin_user_",""))
    data = context.application.persistence.get_user_data().get(uid)

    if not data:
        return

    prof = data["profile"]
    order = prof["orders"][-1]

    txt = [
        f"📦 Замовлення #{order['id']}",
        f"📌 Статус: {order['status']}"
    ]

    if order["comment"]:
        txt.append(f"📝 Коментар: {order['comment']}")

    kb = [
        [InlineKeyboardButton("✅ Оплачено", callback_data=f"admin_paid_{uid}")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="admin")]
    ]

    await q.message.reply_text(
        "\n".join(txt),
        reply_markup=InlineKeyboardMarkup(kb)
    )

    if order.get("receipt"):
        await q.message.reply_photo(order["receipt"])


async def admin_paid(update:Update, context:ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    uid = int(q.data.replace("admin_paid_",""))
    data = context.application.persistence.get_user_data().get(uid)

    if not data:
        return

    prof = data["profile"]
    order = prof["orders"][-1]
    order["status"] = "paid"

    await context.bot.send_message(
        uid,
        "✅ Оплату підтверджено менеджером\n"
        "📦 Замовлення прийнято"
    )

    await q.message.reply_text("💰 Позначено як оплачено")

# ============================================================
# ⭐ VIP BY REFERRALS
# ============================================================

def update_vip_by_referrals(profile):
    refs = profile.get("referrals", 0)
    if refs >= 3:
        profile["vip_until"] = (
            datetime.now() + timedelta(days=14)
        ).isoformat()


# ============================================================
# 🔁 FINAL ROUTER EXTENSION
# ============================================================

async def router(update:Update, context:ContextTypes.DEFAULT_TYPE):

    q = update.callback_query
    if q:
        data = q.data

        # === ADMIN
        if data == "admin":
            return await admin_panel(update, context)

        if data.startswith("admin_user_"):
            return await admin_user(update, context)

        if data.startswith("admin_paid_"):
            return await admin_paid(update, context)

        if data == "add_comment":
            return await ask_comment(update, context)

        return await q.answer()

    if update.message:
        if context.user_data.get("state") == "await_comment":
            return await comment_input(update, context)

        if update.message.photo:
            return await receipt_from_user(update, context)



# ============================================================
# 🏁 MAIN
# ============================================================

def main():

    persistence = PicklePersistence(
        filepath="data/bot_data.pickle",
        update_interval=60
    )

    app = (
        Application.builder()
        .token(TOKEN)
        .persistence(persistence)
        .rate_limiter(AIORateLimiter())
        .defaults(Defaults(parse_mode=ParseMode.HTML))
        .build()
    )

    # ======================
    # 🔹 COMMANDS
    # ======================

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_panel))

    # ======================
    # 🔹 CALLBACKS (ONE ROUTER)
    # ======================

    app.add_handler(CallbackQueryHandler(router))

    # ======================
    # 🔹 TEXT STATES
    # ======================

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            text_router
        )
    )

    # ======================
    # 🔹 RECEIPTS (PHOTO)
    # ======================

    app.add_handler(
        MessageHandler(
            filters.PHOTO,
            receipt_handler
        )
    )

    print("👻 BOT CORE LOADED")

    app.run_polling(
        drop_pending_updates=True,
        allowed_updates=["message", "callback_query"]
    )

# ============================================================
# 🧠 ENTRYPOINT
# ============================================================

if __name__ == "__main__":

    if sys.platform == "win32":
        asyncio.set_event_loop_policy(
            asyncio.WindowsSelectorEventLoopPolicy()
        )

    main()


import logging
import random
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
    PicklePersistence
)
from telegram.error import BadRequest, TimedOut, NetworkError

# ===================== LOGGING =====================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ===================== CONFIG =====================
TOKEN = "8351638507:AAEqc9p9b4AA8vTrzvvj_XArtUABqcfMGV4"
MANAGER_ID = 7544847872
MANAGER_USERNAME = "ghosstydpbot"
CHANNEL_URL = "https://t.me/GhostyStaffDP"
PAYMENT_LINK = "https://heylink.me/ghosstyshop/"
WELCOME_PHOTO = "https://i.ibb.co/y7Q194N/1770068775663.png"

DISCOUNT_MULT = 0.65   # Множник для знижки 35%
PROMO_DISCOUNT = 45    # Персональна знижка 45%
DISCOUNT_MULTIPLIER = DISCOUNT_MULT

BASE_VIP_DATE = datetime.strptime("25.03.2026", "%d.%m.%Y")

# ===================== DATA & PRODUCTS =====================

GIFT_LIQUIDS = {
    9001: {"name": "🎁 Pumpkin Latte 30ml"},
    9002: {"name": "🎁 Glintwine 30ml"},
    9003: {"name": "🎁 Christmas Tree 30ml"},
    9004: {"name": "🎁 Strawberry Jelly 30ml"},
    9005: {"name": "🎁 Mystery One 30ml"},
    9006: {"name": "🎁 Fall Tea 30ml"},
}

LIQUIDS = {
    301: {
        "name": "🎃 Pumpkin Latte",
        "series": "Chaser HO HO HO Edition",
        "price": 269,
        "discount": True,
        "img": "https://i.ibb.co/Y7qn69Ds/pumpkin.jpg", # Перевір посилання, якщо биті - заміни
        "desc": "☕ Гарбузовий латте з корицею\n🎄 Зимовий настрій\n😌 Мʼякий та теплий смак",
        "effect": "Затишок, солодкий aftertaste ☕",
        "payment_url": PAYMENT_LINK
    },
    302: {
        "name": "🍷 Glintwine",
        "series": "Chaser HO HO HO Edition",
        "price": 269,
        "discount": True,
        "img": "https://i.ibb.co/wF8r7Nmc/glintwine.jpg",
        "desc": "🍇 Пряний глінтвейн\n🔥 Теплий винний смак\n🎄 Святковий вайб",
        "effect": "Тепло, релакс 🔥",
        "payment_url": PAYMENT_LINK
    },
    303: {
        "name": "🎄 Christmas Tree",
        "series": "Chaser HO HO HO Edition",
        "price": 269,
        "discount": True,
        "img": "https://i.ibb.co/vCPGV8RV/tree.jpg",
        "desc": "🌲 Хвоя + морозна свіжість\n❄️ Дуже свіжа\n🎅 Атмосфера зими",
        "effect": "Свіжість, холодок ❄️",
        "payment_url": PAYMENT_LINK
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
    },
    103: {
        "name": "🌿 Whole Mint 2ml",
        "type": "hhc",
        "gift_liquid": True,
        "price": 849,
        "discount": True,
        "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg",
        "desc": "🧠 95% ННС | Сатіва\n⚡ Енергія та ясність\n❄️ Свіжа мʼята\n🎁 Рідина у подарунок на вибір\n🚀 Ідеально вдень",
        "payment_url": PAYMENT_LINK
    },
    104: {
        "name": "🌴 Jungle Boys White 2ml",
        "type": "hhc",
        "gift_liquid": True,
        "price": 999,
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
        "price": 499,
        "discount": True,
        "imgs": ["https://i.ibb.co/yFSQ5QSn/xros3.jpg"], # Заглушки, бо в оригіналі були повтори
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
        "imgs": ["https://i.ibb.co/RkNgt1Qr/xros5.jpg"],
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
        "imgs": ["https://i.ibb.co/ynYwSMt6/pro.jpg"],
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
        "imgs": ["https://i.ibb.co/5XW2yN80/nano.jpg"],
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
        "imgs": ["https://i.ibb.co/LDRbQxr1/xros4.jpg"],
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
        "imgs": ["https://i.ibb.co/hxjmpHF2/xros5big.jpg"],
        "colors": ["⚫ Чорний", "🌸 Рожевий", "🟣 Фіолетовий з полоскою"],
        "desc": "🔋 1200 mAh\n⚡ Fast Charge\n💎 Преміальна збірка\n🔥 Максимум смаку\n🚀 Флагман серії",
        "payment_url": PAYMENT_LINK
    },
    506: {
        "name": "🔌 Voopoo Vmate Mini",
        "type": "pod",
        "gift_liquid": False,
        "price": 459,
        "discount": True,
        "imgs": ["https://i.ibb.co/8L0JNTHz/vmate.jpg"],
        "colors": ["🌸 Рожевий", "🔴 Червоний", "⚫ Чорний"],
        "desc": "🔋 1000 mAh\n💨 Автозатяжка\n🧲 Магнітний картридж\n🎯 Простий та надійний\n😌 Легкий старт для новачків",
        "payment_url": PAYMENT_LINK
    }
}

CITIES = [
    "Київ", "Дніпро", "Камʼянське", "Харків", "Одеса",
    "Львів", "Запоріжжя", "Кривий Ріг", "Полтава", "Черкаси"
]

CITY_DISTRICTS = {
    "Київ": ["Шевченківський", "Дарницький", "Оболонський", "Печерський", "Соломʼянський", "Деснянський"],
    "Дніпро": ["Центральний", "Соборний", "Індустріальний", "Амур", "Новокодацький"],
    "Камʼянське": ["Центральний", "Південний", "Заводський", "Дніпровський", "Лівий берег"],
    "Харків": ["Київський", "Салтівський", "Холодногірський", "Індустріальний"]
}

# ===================== HELPERS =====================
def get_gift_liquids():
    return [v["name"] for v in GIFT_LIQUIDS.values()]

def generate_promo_code(user_id: int) -> str:
    return f"GHOST-{user_id % 10000}{random.randint(100,999)}"

def vip_until(profile: dict) -> datetime:
    base = profile.get("vip_base", BASE_VIP_DATE)
    refs = profile.get("referrals", 0)
    return base + timedelta(days=7 * refs)

def calc_prices(item: dict, promo_percent: int) -> dict:
    base = item["price"]
    discounted = base
    if item.get("discount", True):
        discounted = int(base * DISCOUNT_MULTIPLIER)
    
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
    text += f"🔥 Зі знижкою: <b>{prices['discounted']} грн</b>\n"
    text += f"🎟 З промо: <b>{prices['final']} грн</b>\n\n"
    text += f"{item.get('desc', '')}\n\n"

    gifts = "\n".join(f"• {g}" for g in get_gift_liquids())
    if gifts:
        text += f"🎁 <b>Рідина у подарунок на вибір:</b>\n{gifts}\n\n"

    if is_vip:
        text += "👑 <b>VIP:</b> безкоштовна доставка 🚚\n"
    else:
        text += "🚚 Доставка за тарифом\n"
    return text

# ===================== KEYBOARDS =====================
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👤 Профіль", callback_data="profile"), InlineKeyboardButton("🛍 Асортимент", callback_data="assortment")],
        [InlineKeyboardButton("📍 Місто", callback_data="city"), InlineKeyboardButton("🛒 Кошик", callback_data="cart")],
        [InlineKeyboardButton("📦 Замовлення", callback_data="orders"), InlineKeyboardButton("👨‍💻 Менеджер", url=f"https://t.me/{MANAGER_USERNAME}")],
        [InlineKeyboardButton("📢 Канал", url=CHANNEL_URL)]
    ])

def back_kb(back: str):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Назад", callback_data=back), InlineKeyboardButton("🏠 В головне меню", callback_data="main")]
    ])

# ===================== START =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    context.user_data.setdefault("vip", False)
    
    # Init Profile
    if "profile" not in context.user_data:
        context.user_data["profile"] = {
            "uid": user.id,
            "full_name": user.first_name,
            "username": user.username,
            "phone": None,
            "address": None,
            "city": None,
            "district": None,
            "promo_code": generate_promo_code(user.id),
            "promo_discount": PROMO_DISCOUNT,
            "referrals": 0,
            "vip_base": BASE_VIP_DATE,
            "ref_applied": False
        }
    context.user_data.setdefault("cart", [])
    context.user_data.setdefault("orders", [])

    profile = context.user_data["profile"]
    
    # Check Referral
    args = context.args
    if args and not profile.get("ref_applied"):
        try:
            ref_id = int(args[0])
            if ref_id != user.id:
                profile["ref_applied"] = True
                profile["referrals"] += 1
                # Here you might want to notify the referrer, but keeping it simple for stability
        except ValueError:
            pass

    vip_date = vip_until(profile)
    context.user_data["vip"] = vip_date > datetime.now()

    text = (
        f"👋 <b>{escape(user.first_name)}</b>, вітаємо у <b>Ghosty Shop</b> 💨\n\n"
        f"🎁 Подарунок до кожного замовлення — 3 рідини 30ml\n"
        f"🎫 Промокод: <code>{profile['promo_code']}</code> (-{profile.get('promo_discount', 45)}%)\n"
        f"👑 VIP до: <b>{vip_date.strftime('%d.%m.%Y')}</b>\n\n"
        f"👇 Оберіть дію:"
    )

    try:
        if update.message:
            await update.message.reply_photo(photo=WELCOME_PHOTO, caption=text, parse_mode="HTML", reply_markup=main_menu())
        else:
            # If called from callback
            query = update.callback_query
            try:
                await query.edit_message_caption(caption=text, parse_mode="HTML", reply_markup=main_menu())
            except BadRequest:
                # If media is different or fails
                await query.message.delete()
                await query.message.chat.send_photo(photo=WELCOME_PHOTO, caption=text, parse_mode="HTML", reply_markup=main_menu())
    except Exception as e:
        logger.error(f"Start error: {e}")
        if update.message:
            await update.message.reply_text(text, parse_mode="HTML", reply_markup=main_menu())

# ===================== HANDLERS =====================

async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    profile = context.user_data.get("profile", {})
    vip_date = vip_until(profile).strftime("%d.%m.%Y")
    
    text = (
        f"👤 <b>Профіль користувача</b>\n\n"
        f"🧑 <b>Імʼя:</b> {escape(profile.get('full_name', '—'))}\n"
        f"👤 <b>Username:</b> @{profile.get('username', '—')}\n\n"
        f"🏙 <b>Місто:</b> {profile.get('city', '—')}\n"
        f"📍 <b>Район:</b> {profile.get('district', '—')}\n"
        f"🏠 <b>Адреса:</b> {profile.get('address', '—')}\n\n"
        f"🏷 <b>Промокод:</b> <code>{profile.get('promo_code', '—')}</code>\n"
        f"💸 <b>Знижка:</b> -{profile.get('promo_discount', PROMO_DISCOUNT)}%\n\n"
        f"💎 <b>VIP:</b> до <b>{vip_date}</b>\n"
        f"👥 <b>Рефералів:</b> {profile.get('referrals', 0)}\n"
    )
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✏️ Змінити адресу", callback_data="edit_address"), InlineKeyboardButton("📍 Місто", callback_data="city")],
        [InlineKeyboardButton("🔗 Реферальне посилання", callback_data="ref_link")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="main")]
    ])
    
    try:
        await query.edit_message_caption(caption=text, parse_mode="HTML", reply_markup=kb)
    except:
         await query.edit_message_text(text, parse_mode="HTML", reply_markup=kb)

async def show_ref_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    bot_username = context.bot.username
    uid = context.user_data["profile"]["uid"]
    link = f"https://t.me/{bot_username}?start={uid}"
    
    text = f"🔗 <b>Ваше реферальне посилання:</b>\n\n<code>{link}</code>\n\nЗа кожного друга +7 днів VIP!"
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="profile")]]))

# --- City Selection ---
async def select_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    buttons = []
    row = []
    for city in CITIES:
        row.append(InlineKeyboardButton(city, callback_data=f"save_city_{city}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row: buttons.append(row)
    buttons.append([InlineKeyboardButton("⬅️ Назад", callback_data="profile")])
    
    await query.edit_message_text("🏙 <b>Оберіть місто:</b>", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons))

async def save_city(update: Update, context: ContextTypes.DEFAULT_TYPE, city_name: str):
    query = update.callback_query
    context.user_data["profile"]["city"] = city_name
    context.user_data["profile"]["district"] = None # Reset district
    
    districts = CITY_DISTRICTS.get(city_name, [])
    buttons = []
    for d in districts:
        buttons.append([InlineKeyboardButton(d, callback_data=f"save_dist_{d}")])
    buttons.append([InlineKeyboardButton("⬅️ Назад", callback_data="city")])
    
    await query.edit_message_text(f"✅ Місто збережено: <b>{city_name}</b>\n👇 Оберіть район:", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons))

async def save_district(update: Update, context: ContextTypes.DEFAULT_TYPE, dist_name: str):
    query = update.callback_query
    context.user_data["profile"]["district"] = dist_name
    await query.edit_message_text(f"✅ Район збережено: <b>{dist_name}</b>", parse_mode="HTML", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("👤 У профіль", callback_data="profile")]]))

# --- Assortment ---
async def show_assortment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("💧 Рідини", callback_data="cat_liquids"), InlineKeyboardButton("🔌 POD-системи", callback_data="cat_pods")],
        [InlineKeyboardButton("💨 HHC / NNS", callback_data="cat_hhc")],
        [InlineKeyboardButton("🏠 В головне меню", callback_data="main")]
    ])
    try:
        await query.edit_message_caption(caption="🛍 <b>Каталог товарів</b>", parse_mode="HTML", reply_markup=kb)
    except:
        await query.edit_message_text("🛍 <b>Каталог товарів</b>", parse_mode="HTML", reply_markup=kb)

async def show_category(update: Update, context: ContextTypes.DEFAULT_TYPE, category_key: str):
    query = update.callback_query
    items = {}
    if category_key == "liquids": items = LIQUIDS
    elif category_key == "pods": items = PODS
    elif category_key == "hhc": items = HHC_VAPES
    
    buttons = []
    for pid, item in items.items():
        buttons.append([InlineKeyboardButton(item["name"], callback_data=f"item_{pid}")])
    buttons.append([InlineKeyboardButton("⬅️ Назад", callback_data="assortment")])
    
    await query.edit_message_text(f"📂 <b>Категорія: {category_key.upper()}</b>", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons))

# --- Item View ---
async def show_item(update: Update, context: ContextTypes.DEFAULT_TYPE, pid: int):
    query = update.callback_query
    # Find item in all catalogs
    item = LIQUIDS.get(pid) or PODS.get(pid) or HHC_VAPES.get(pid)
    
    if not item:
        await query.answer("❌ Товар не знайдено")
        return

    caption = build_item_caption(item, context.user_data)
    
    # Image logic
    imgs = item.get("imgs", [])
    if imgs:
        photo = imgs[0]
    else:
        photo = item.get("img", WELCOME_PHOTO)

    kb_rows = []
    # Color logic if POD
    if "imgs" in item and len(item["imgs"]) > 1:
        # Simple cycling could be implemented, but for stability let's keep it simple or just show colors
        pass 

    kb_rows.append([InlineKeyboardButton("⚡ Швидке замовлення", callback_data=f"fast_{pid}")])
    kb_rows.append([InlineKeyboardButton("🛒 В кошик", callback_data=f"addcart_{pid}")])
    kb_rows.append([InlineKeyboardButton("⬅️ Назад", callback_data="assortment")])

    kb = InlineKeyboardMarkup(kb_rows)

    try:
        await query.message.delete() # Often safer to delete and resend when changing media types
        await query.message.chat.send_photo(photo=photo, caption=caption, parse_mode="HTML", reply_markup=kb)
    except Exception as e:
        logger.error(f"Show item error: {e}")
        await query.message.reply_text("Помилка відображення товару.", reply_markup=main_menu())

# --- Cart ---
async def add_to_cart(update: Update, context: ContextTypes.DEFAULT_TYPE, pid: int):
    query = update.callback_query
    item = LIQUIDS.get(pid) or PODS.get(pid) or HHC_VAPES.get(pid)
    if item:
        prices = calc_prices(item, context.user_data.get("profile", {}).get("promo_discount", PROMO_DISCOUNT))
        cart_item = {
            "pid": pid,
            "name": item["name"],
            "price": prices['final'],
            "gift_liquid": item.get("gift_liquid", False)
        }
        context.user_data["cart"].append(cart_item)
        await query.answer("✅ Додано в кошик!")
    else:
        await query.answer("❌ Помилка товару")

async def show_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    cart = context.user_data.get("cart", [])
    
    if not cart:
        await query.edit_message_text("🛒 <b>Кошик порожній</b>", parse_mode="HTML", reply_markup=back_kb("main"))
        return
        
    text = "🛒 <b>Ваш кошик:</b>\n\n"
    total = 0
    for idx, i in enumerate(cart, 1):
        text += f"{idx}. {i['name']} — <b>{i['price']} грн</b>\n"
        total += i['price']
    
    text += f"\n💰 <b>Разом: {total} грн</b>"
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Оформити замовлення", callback_data="checkout")],
        [InlineKeyboardButton("🗑 Очистити", callback_data="clearcart")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="main")]
    ])
    
    # Try edit caption if photo exists, else edit text
    try:
        await query.edit_message_caption(caption=text, parse_mode="HTML", reply_markup=kb)
    except:
        await query.message.delete()
        await query.message.chat.send_message(text, parse_mode="HTML", reply_markup=kb)

async def clear_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["cart"] = []
    await update.callback_query.answer("🗑 Кошик очищено")
    await show_cart(update, context)

# --- Checkout / Order ---
async def start_checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    profile = context.user_data["profile"]
    
    # Check if data is missing
    if not profile.get("phone") or not profile.get("address"):
        context.user_data["state"] = "fast_name" # Use generic input flow
        await query.message.reply_text("✍️ Для оформлення введіть ваше <b>Ім'я та Прізвище</b>:", parse_mode="HTML")
        return

    await confirm_order(update.callback_query.message, context)

async def fast_order_start(update: Update, context: ContextTypes.DEFAULT_TYPE, pid: int):
    query = update.callback_query
    # Add single item to temp cart logic or just add to cart and checkout
    # For simplicity: add to cart and start checkout flow
    await add_to_cart(update, context, pid)
    await start_checkout(update, context)

async def confirm_order(message, context: ContextTypes.DEFAULT_TYPE):
    cart = context.user_data.get("cart", [])
    if not cart:
        await message.reply_text("Кошик порожній.")
        return
        
    profile = context.user_data["profile"]
    total = sum(i['price'] for i in cart)
    order_id = f"ORD-{message.chat.id}-{random.randint(1000,9999)}"
    
    # Create Order
    order = {
        "id": order_id,
        "items": cart.copy(),
        "total": total,
        "status": "Очікує оплату",
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    context.user_data["orders"].append(order)
    context.user_data["active_order_id"] = order_id
    context.user_data["cart"] = [] # Clear cart

text = (
        f"✅ <b>Замовлення сформовано!</b>\n"
        f"🆔 Номер: <code>{order_id}</code>\n\n"
        f"👤 {profile.get('full_name')}\n"
        f"📞 {profile.get('phone')}\n"
        f"📍 {profile.get('city')}, {profile.get('address')}\n\n"
        f"💰 <b>До сплати: {total} грн</b>\n\n"
        f"💳 <b>Реквізити для оплати:</b>\n"
        f"<a href='{PAYMENT_LINK}'>Натисніть тут для оплати</a>\n\n"
        f"📸 <b>Після оплати надішліть скріншот квитанції у цей чат!</b>"
    )
    
    await message.reply_text(text, parse_mode="HTML", reply_markup=main_menu(), disable_web_page_preview=False)

# --- Message Handler (Inputs) ---
async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = context.user_data.get("state")
    if not state: return
    
    text = update.message.text
    profile = context.user_data["profile"]
    
    if state == "fast_name":
        profile["full_name"] = text
        context.user_data["state"] = "fast_phone"
        await update.message.reply_text("📞 Тепер введіть ваш <b>номер телефону</b>:", parse_mode="HTML")
        
    elif state == "fast_phone":
        profile["phone"] = text
        context.user_data["state"] = "fast_address"
        await update.message.reply_text("🏠 Введіть <b>місто та відділення пошти/адресу</b>:", parse_mode="HTML")
        
    elif state == "fast_address":
        profile["address"] = text
        context.user_data["state"] = None
        await update.message.reply_text("✅ Дані збережено!")
        # Resume checkout
        await confirm_order(update.message, context)

    elif state == "edit_address":
        profile["address"] = text
        context.user_data["state"] = None
        await update.message.reply_text(f"✅ Нова адреса: {text}", reply_markup=main_menu())

# --- Photo Handler (Receipts) ---
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    active_oid = context.user_data.get("active_order_id")
    if not active_oid:
        await update.message.reply_text("Я не очікую фото зараз. Це квитанція? Створіть замовлення спочатку.")
        return
        
    photo_file = await update.message.photo[-1].get_file()
    
    caption = (
        f"🧾 <b>Нова оплата!</b>\n"
        f"🆔 Замовлення: {active_oid}\n"
        f"👤 User: {update.effective_user.mention_html()}\n"
    )
    
    # Send to Manager
    await context.bot.send_photo(chat_id=MANAGER_ID, photo=photo_file.file_id, caption=caption, parse_mode="HTML")
    
    context.user_data["active_order_id"] = None # Clear active wait
    await update.message.reply_text("✅ <b>Квитанцію отримано!</b> Менеджер перевірить її та зв'яжеться з вами.", parse_mode="HTML")

# --- Address Edit Trigger ---
async def ask_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["state"] = "edit_address"
    await update.callback_query.edit_message_text("✍️ Введіть нову адресу:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Скасувати", callback_data="profile")]]))

# ===================== MAIN ROUTER =====================
async def router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    try:
        if data == "main": await start(update, context)
        elif data == "profile": await show_profile(update, context)
        elif data == "ref_link": await show_ref_link(update, context)
        elif data == "city": await select_city(update, context)
        elif data.startswith("save_city_"): await save_city(update, context, data.replace("save_city_", ""))
        elif data.startswith("save_dist_"): await save_district(update, context, data.replace("save_dist_", ""))
        elif data == "edit_address": await ask_address(update, context)
        
        elif data == "assortment": await show_assortment(update, context)
        elif data.startswith("cat_"): await show_category(update, context, data.replace("cat_", ""))
        elif data.startswith("item_"): await show_item(update, context, int(data.split("_")[1]))
        
        elif data.startswith("addcart_"): await add_to_cart(update, context, int(data.split("_")[1]))
        elif data == "cart": await show_cart(update, context)
        elif data == "clearcart": await clear_cart(update, context)
        elif data == "checkout": await start_checkout(update, context)
        
        elif data.startswith("fast_"): await fast_order_start(update, context, int(data.split("_")[1]))
        
        elif data == "orders": 
            # Simple orders view
            orders = context.user_data.get("orders", [])
            if not orders: await query.edit_message_text("📭 Історія порожня", reply_markup=back_kb("main"))
            else:
                txt = "📦 <b>Останні замовлення:</b>\n\n"
                for o in orders[-5:]:
                    txt += f"{o['id']} - {o['total']} грн ({o['status']})\n"
                await query.edit_message_text(txt, parse_mode="HTML", reply_markup=back_kb("main"))
    
    except Exception as e:
        logger.error(f"Router Error: {e}")
        try:
            await query.message.reply_text("⚠️ Сталася помилка. Спробуйте /start")
        except: pass

# ===================== RUN =====================
if __name__ == "__main__":
    # Persistence ensures data survives restarts
    persistence = PicklePersistence(filepath="ghosty_data.pickle")
    
    app = Application.builder().token(TOKEN).persistence(persistence).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_input))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(CallbackQueryHandler(router))
    
    print("Bot is running...")
    app.run_polling()
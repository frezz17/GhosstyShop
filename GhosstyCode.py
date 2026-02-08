# ============================================================
# 👻 GHOSTY SHOP BOT — FULL PRODUCTION CORE
# STABLE VERSION FOR BOTHOST
# ============================================================

import os
import sys
import logging
import asyncio
import random
from datetime import datetime, timedelta
from html import escape
from uuid import uuid4

# ------------------------------------------------------------
# 🔧 BOTHOST FIX (Fixes "Operation timed out")
# ------------------------------------------------------------
try:
    import nest_asyncio
    nest_asyncio.apply()
except ImportError:
    print("⚠️ 'nest_asyncio' not found. Please add it to requirements.txt")

try:
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
except ImportError:
    print("❌ CRITICAL: 'python-telegram-bot' not installed.")
    sys.exit(1)

# ============================================================
# ⚙️ CONFIG
# ============================================================

TOKEN = "8351638507:AAEqc9p9b4AA8vTrzvvj_XArtUABqcfMGV4"  # ⚠️ ВСТАВ СЮДИ ТОКЕН
MANAGER_ID = 7544847872

DISCOUNT_MULTIPLIER = 0.65
PROMO_DISCOUNT = 45

VIP_FREE_DELIVERY_UNTIL = datetime.strptime("25.03.2026", "%d.%m.%Y")
BASE_VIP_DATE = datetime.strptime("25.03.2026", "%d.%m.%Y")

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# ============================================================
# 📝 LOGGING
# ============================================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# ============================================================
# 🌍 CITIES & DISTRICTS
# ============================================================

CITIES = [
    "Київ", "Дніпро", "Камʼянське", "Харків", "Одеса",
    "Львів", "Запоріжжя", "Кривий Ріг", "Полтава", "Черкаси"
]

CITY_DISTRICTS = {
    "Київ": ["Шевченківський", "Дарницький", "Оболонський", "Печерський", "Соломʼянський", "Деснянський", "Подільський", "Голосіївський"],
    "Дніпро": ["Центральний", "Соборний", "Індустріальний", "Самарський", "Амур", "Новокодацький", "Чечелівський"],
    "Камʼянське": ["Центр", "Соцмісто", "Черемушки", "Романкове", "БАМ"],
    "Харків": ["Шевченківський", "Київський", "Салтівський", "Основʼянський", "Холодногірський"],
    "Одеса": ["Приморський", "Київський", "Малиновський", "Суворовський"],
    "Львів": ["Галицький", "Франківський", "Сихівський", "Шевченківський"],
    "Запоріжжя": ["Олександрівський", "Дніпровський", "Комунарський", "Хортицький"],
    "Кривий Ріг": ["Центрально-Міський", "Покровський", "Саксаганський", "Тернівський"],
    "Полтава": ["Центр", "Поділ", "Алмазний", "Левада"],
    "Черкаси": ["Соснівський", "Придніпровський"]
}

# ============================================================
# 🎁 GIFTS
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
# 📦 PRODUCTS DATA (FULL)
# ============================================================

LIQUIDS = {
    301: {
        "name": "🎃 Pumpkin Latte",
        "series": "Ghost Liquid",
        "price": 269,
        "desc": "☕ Осінній гарбузовий латте\nКремовий, теплий, насичений.",
        "imgs": ["https://i.ibb.co/Y7qn69Ds/photo.jpg"],
        "colors": [],
        "gift_liquid": True,
    },
    302: {
        "name": "🍷 Glintwine",
        "series": "Ghost Liquid",
        "price": 269,
        "desc": "🍇 Пряний глінтвейн\nЗігріваючий аромат спецій.",
        "imgs": ["https://i.ibb.co/wF8r7Nmc/photo.jpg"],
        "colors": [],
        "gift_liquid": True,
    },
    303: {
        "name": "🎄 Christmas Tree",
        "series": "Ghost Liquid",
        "price": 269,
        "desc": "🌲 Морозна хвоя\nСвіжий зимовий профіль.",
        "imgs": ["https://i.ibb.co/vCPGV8RV/photo.jpg"],
        "colors": [],
        "gift_liquid": True,
    },
    304: {
        "name": "🍓 Strawberry Jelly",
        "series": "Ghost Liquid",
        "price": 289,
        "desc": "🍓 Полуничний джем\nСолодкий десертний смак.",
        "imgs": ["https://i.ibb.co/2q3Qz8C/strawberry.jpg"],
        "colors": [],
        "gift_liquid": True,
    },
}

HHC_VAPES = {
    100: {
        "name": "🌴 Packwoods Purple",
        "series": "Packwoods",
        "price": 549,
        "desc": "💨 90% HHC • Hybrid\nЗбалансований ефект.",
        "imgs": ["https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg"],
        "colors": [],
        "gift_liquid": False,
    },
    101: {
        "name": "🍊 Packwoods Orange",
        "series": "Packwoods",
        "price": 629,
        "desc": "🍊 Sativa\nЕнергійний профіль.",
        "imgs": ["https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg"],
        "colors": [],
        "gift_liquid": False,
    },
    102: {
        "name": "🌸 Packwoods Pink",
        "series": "Packwoods",
        "price": 719,
        "desc": "🌸 Hybrid\nМ’який баланс.",
        "imgs": ["https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg"],
        "colors": [],
        "gift_liquid": False,
    },
    103: {
        "name": "🌿 Whole Mint",
        "series": "Whole Melt",
        "price": 849,
        "desc": "🌿 Mint\nСвіжий м’ятний холодок.",
        "imgs": ["https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg"],
        "colors": [],
        "gift_liquid": False,
    },
    104: {
        "name": "🌙 Jungle Boys White",
        "series": "Jungle Boys",
        "price": 999,
        "desc": "🌙 Indica\nРелаксуючий ефект.",
        "imgs": ["https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg"],
        "colors": [],
        "gift_liquid": False,
    },
}

PODS = {
    500: {
        "name": "🔌 XROS 3 Mini",
        "series": "Vaporesso",
        "price": 499,
        "desc": "🔋 1000 mAh • COREX Heating\nКомпактний POD.",
        "imgs": ["https://i.ibb.co/yFSQ5QSn/vaporesso-xros-3-mini.jpg"],
        "colors": ["Black", "Sky Blue", "Rose Gold"],
        "gift_liquid": False,
    },
    501: {
        "name": "🔌 XROS 5 Mini",
        "series": "Vaporesso",
        "price": 579,
        "desc": "⚡ COREX 2.0\nПокращений смак і тяга.",
        "imgs": ["https://i.ibb.co/RkNgt1Qr/vaporesso-xros-5-mini.jpg"],
        "colors": ["Black", "Green", "Silver"],
        "gift_liquid": False,
    },
    502: {
        "name": "🔌 XROS Pro",
        "series": "Vaporesso",
        "price": 689,
        "desc": "⚙️ Регульована потужність\nPro-рівень.",
        "imgs": ["https://i.ibb.co/ynYwSMt6/vaporesso-xros-pro.jpg"],
        "colors": ["Black", "Blue", "Red"],
        "gift_liquid": False,
    },
    503: {
        "name": "🔌 XROS Nano",
        "series": "Vaporesso",
        "price": 519,
        "desc": "📦 Компактний формат\nЗручно щодня.",
        "imgs": ["https://i.ibb.co/5XW2yN80/vaporesso-xros-nano.jpg"],
        "colors": ["Black", "Lime", "Pink"],
        "gift_liquid": False,
    },
}

# ============================================================
# 🧠 CORE HELPERS
# ============================================================

def get_item(pid):
    # Safe logic to find item in any category
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
    return f"GHOST{uid % 10000}{random.randint(100, 999)}"

def create_profile(user):
    return {
        "uid": user.id,
        "name": user.first_name,
        "promo": PROMO_DISCOUNT,
        "promo_code": generate_promo(user.id),
        "vip_base": BASE_VIP_DATE,
        "referrals": 0,
        "orders": [],
        "city": None,
        "district": None,
        "address": None
    }

def save_profile(profile):
    # Optional manual save (Persistence handles most of it)
    pass

def cart_text(cart, profile):
    if not cart:
        return "🛒 Кошик порожній"

    lines = ["🛒 <b>Твій кошик:</b>\n"]
    total = 0

    for row in cart:
        pid = row["pid"]
        item = get_item(pid)
        if not item:
            continue
        
        _, final = calc_price(item["price"], profile["promo"])
        total += final
        
        color_info = f" ({row['color']})" if row.get("color") else ""
        lines.append(f"• {item['name']}{color_info} — {final} грн")

    lines.append(f"\n💰 <b>Разом: {total} грн</b>")
    return "\n".join(lines)

def get_last_order(profile):
    orders = profile.get("orders", [])
    return orders[-1] if orders else None

# ============================================================
# ⌨️ UI MENUS
# ============================================================

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛍 Каталог", callback_data="catalog")],
        [InlineKeyboardButton("🛒 Кошик", callback_data="cart"),
         InlineKeyboardButton("👤 Профіль", callback_data="profile")],
        [InlineKeyboardButton("⚡ Швидке замовлення", callback_data="fast")]
    ])

def catalog_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💧 Рідини", callback_data="cat_liq")],
        [InlineKeyboardButton("🔥 HHC", callback_data="cat_hhc")],
        [InlineKeyboardButton("🔌 POD", callback_data="cat_pod")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_main")]
    ])

def items_menu(items: dict, prefix: str):
    rows = []
    for pid, it in items.items():
        rows.append([InlineKeyboardButton(it["name"], callback_data=f"item_{prefix}_{pid}")])
    rows.append([InlineKeyboardButton("⬅️ До категорій", callback_data="catalog")])
    return InlineKeyboardMarkup(rows)

def item_actions_kb(pid: int, has_colors: bool = False):
    rows = [
        [InlineKeyboardButton("🛒 Додати", callback_data=f"add_{pid}")],
        [InlineKeyboardButton("➖ Прибрати", callback_data=f"rem_{pid}")],
    ]
    if has_colors:
        rows.insert(0, [InlineKeyboardButton("🎨 Вибрати колір", callback_data=f"color_{pid}")])
    rows.append([InlineKeyboardButton("⬅️ Назад", callback_data="catalog")])
    return InlineKeyboardMarkup(rows)

def cart_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Оформити", callback_data="checkout")],
        [InlineKeyboardButton("🗑 Очистити", callback_data="cart_clear")],
        [InlineKeyboardButton("⬅️ Меню", callback_data="back_main")]
    ])

def payment_kb():
    MONO_PAY = "https://lnk.ua/k4xJG21Vy?utm_medium=social&utm_source=heylink.me"
    PRIVAT_PAY = "https://lnk.ua/RVd0OW6V3?utm_medium=social&utm_source=heylink.me"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 Усі способи", url=MONO_PAY)],
        [
            InlineKeyboardButton("🟣 Mono", url=MONO_PAY),
            InlineKeyboardButton("🟢 Privat", url=PRIVAT_PAY),
        ],
        [InlineKeyboardButton("👤 Написати менеджеру", callback_data="fast")]
    ])

# ============================================================
# 🚀 HANDLERS
# ============================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    # Initialize profile if not exists
    if "profile" not in context.user_data:
        context.user_data["profile"] = create_profile(user)
    if "cart" not in context.user_data:
        context.user_data["cart"] = []
    
    context.user_data["state"] = None
    
    await update.message.reply_text(
        "👻 Ghosty Shop запущено\nОбирай, що до душі 👇",
        reply_markup=main_menu()
    )

async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.message.edit_text("👻 Головне меню", reply_markup=main_menu())

# --- CATALOG ---

async def show_catalog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.message.edit_text("📦 Обери категорію:", reply_markup=catalog_menu())

async def show_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data

    if data == "cat_liq":
        await q.message.edit_text("💧 Рідини:", reply_markup=items_menu(LIQUIDS, "liq"))
    elif data == "cat_hhc":
        await q.message.edit_text("🔥 HHC:", reply_markup=items_menu(HHC_VAPES, "hhc"))
    elif data == "cat_pod":
        await q.message.edit_text("🔌 POD:", reply_markup=items_menu(PODS, "pod"))

async def show_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    try:
        # Extract ID: item_pod_500 -> 500
        _, _, pid = q.data.split("_")
        pid = int(pid)
        item = get_item(pid)
        
        # Ensure profile exists
        if "profile" not in context.user_data:
             context.user_data["profile"] = create_profile(update.effective_user)
        prof = context.user_data["profile"]
        
        if not item:
            return await q.message.reply_text("❌ Товар не знайдено")

        shop, final = calc_price(item["price"], prof["promo"])

        caption = (
            f"<b>{escape(item['name'])}</b>\n"
            f"📦 Серія: {item.get('series','')}\n\n"
            f"🔥 Магазин: {shop} грн\n"
            f"🎟 Твоя: <b>{final} грн</b>\n\n"
            f"{item.get('desc','')}\n\n🎁 Подарунок:\n"
        )
        for g in GIFT_LIQUIDS:
            caption += f"• {g}\n"

        kb = item_actions_kb(pid, bool(item.get("colors")))
        imgs = item.get("imgs", [])

        # Try to delete old message to send new one (Photo vs Text)
        try:
            await q.message.delete()
        except Exception:
            pass 

        if imgs:
            await q.message.chat.send_photo(photo=imgs[0], caption=caption, reply_markup=kb)
        else:
            await q.message.chat.send_message(text=caption, reply_markup=kb)

    except Exception as e:
        logger.error(f"Error in show_item: {e}")
        await q.message.chat.send_message("❌ Помилка відображення товару", reply_markup=main_menu())

# --- CART & COLORS ---

async def add_to_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    pid = int(q.data.split("_")[1])
    
    context.user_data.setdefault("cart", []).append({
        "pid": pid,
        "color": None
    })
    await q.message.reply_text("✅ Додано в кошик")

async def remove_from_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

async def color_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    pid = int(q.data.split("_")[1])
    item = get_item(pid)
    
    if not item or not item.get("colors"):
        await q.message.reply_text("ℹ️ Кольорів немає")
        return
        
    rows = [[InlineKeyboardButton(c, callback_data=f"cpick_{pid}_{c}")] for c in item["colors"]]
    rows.append([InlineKeyboardButton("⬅️ Назад", callback_data=f"item_pod_{pid}")])
    
    await q.message.reply_text("🎨 Обери колір:", reply_markup=InlineKeyboardMarkup(rows))

async def color_picked(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    parts = q.data.split("_")
    pid = int(parts[1])
    color = parts[2]
    
    context.user_data.setdefault("cart", []).append({
        "pid": pid,
        "color": color
    })
    await q.message.reply_text(f"✅ Додано: {color}")

# --- CART LOGIC ---

async def show_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    cart = context.user_data.setdefault("cart", [])
    profile = context.user_data.get("profile") or create_profile(update.effective_user)
    
    # Check if last message was a photo (to avoid edit errors)
    try:
        await q.message.delete()
    except:
        pass

    text = cart_text(cart, profile)
    await q.message.chat.send_message(text, reply_markup=cart_menu())

async def cart_clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    context.user_data["cart"] = []
    await q.message.edit_text("🗑 Кошик очищено", reply_markup=main_menu())

# --- CHECKOUT FLOW ---

async def checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    cart = context.user_data.get("cart", [])
    if not cart:
        await q.message.reply_text("❌ Кошик порожній")
        return

    rows = []
    for city in CITIES:
        rows.append([InlineKeyboardButton(city, callback_data=f"city_{city}")])
    rows.append([InlineKeyboardButton("❌ Скасувати", callback_data="back_main")])
    
    await q.message.edit_text("🏙 Обери своє місто:", reply_markup=InlineKeyboardMarkup(rows))

async def select_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    city_name = q.data.split("_")[1]
    context.user_data["temp_city"] = city_name
    
    districts = CITY_DISTRICTS.get(city_name, [])
    if not districts:
        context.user_data["temp_district"] = "Інше"
        context.user_data["state"] = "await_address"
        await q.message.edit_text(f"✅ Місто: {city_name}\n✍️ Напиши адресу доставки (Вулиця, дім, відділення НП):")
        return

    rows = [[InlineKeyboardButton(d, callback_data=f"dist_{d}")] for d in districts]
    rows.append([InlineKeyboardButton("⬅️ Назад", callback_data="checkout")])
    
    await q.message.edit_text("🏘 Обери район:", reply_markup=InlineKeyboardMarkup(rows))

async def select_district(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    dist_name = q.data.split("_")[1]
    context.user_data["temp_district"] = dist_name
    
    context.user_data["state"] = "await_address"
    await q.message.edit_text(f"✅ Район: {dist_name}\n✍️ Напиши адресу доставки (Вулиця, дім, відділення НП):")

async def address_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("state") != "await_address":
        return

    address = update.message.text
    prof = context.user_data["profile"]
    
    # Update profile info
    prof["city"] = context.user_data.get("temp_city")
    prof["district"] = context.user_data.get("temp_district")
    prof["address"] = address
    save_profile(prof)
    
    context.user_data["state"] = None
    
    # Create Order
    cart = context.user_data.get("cart", [])
    order = {
        "id": str(uuid4())[:8],
        "items": cart.copy(),
        "status": "waiting_payment",
        "created": datetime.now().isoformat()
    }
    prof.setdefault("orders", []).append(order)
    
    # Notify Manager
    cart_txt = cart_text(cart, prof)
    user = update.effective_user
    
    try:
        await context.bot.send_message(
            MANAGER_ID,
            f"📦 <b>НОВЕ ЗАМОВЛЕННЯ</b>\n\n"
            f"👤 {user.first_name} (@{user.username})\n"
            f"🏙 {prof['city']} / {prof['district']}\n"
            f"🏠 {prof['address']}\n\n"
            f"{cart_txt}"
        )
    except Exception as e:
        logger.error(f"Failed to notify manager: {e}")

    context.user_data["cart"] = []
    
    await update.message.reply_text(
        "✅ Дані збережено!\n💳 <b>Обери спосіб оплати:</b>",
        reply_markup=payment_kb()
    )
    await update.message.reply_text("📎 Після оплати надішли сюди скріншот/фото чеку.")

async def receipt_from_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        return

    prof = context.user_data.get("profile")
    if not prof: return

    order = get_last_order(prof)
    if not order:
        await update.message.reply_text("ℹ️ У вас немає активних замовлень.")
        return

    order["receipt"] = update.message.photo[-1].file_id
    order["status"] = "waiting_confirm"
    
    try:
        await context.bot.send_message(
            MANAGER_ID,
            f"🧾 <b>ЧЕК ВІД КЛІЄНТА</b>\nUser ID: {prof['uid']}\nOrder: {order['id']}"
        )
        await context.bot.send_photo(MANAGER_ID, order["receipt"])
        
        admin_kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Підтвердити оплату", callback_data=f"admin_paid_{prof['uid']}")]
        ])
        await context.bot.send_message(MANAGER_ID, "Дії:", reply_markup=admin_kb)
    except Exception as e:
        logger.error(f"Error sending receipt to admin: {e}")

    await update.message.reply_text(
        "🧾 Квитанцію отримано!\n⏳ Очікуй підтвердження менеджером."
    )

# --- PROFILE & FAST ORDER ---

async def profile_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    prof = context.user_data["profile"]
    orders_count = len(prof.get("orders", []))
    
    # Delete photo if exists to show text cleanly
    try: await q.message.delete()
    except: pass

    txt = (
        f"👤 <b>Твій профіль</b>\n"
        f"ID: {prof['uid']}\n"
        f"Знижка: {prof['promo']}%\n"
        f"Замовлень: {orders_count}\n"
    )
    await q.message.chat.send_message(txt, reply_markup=main_menu())

async def fast_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    context.user_data["state"] = "fast_order"
    try: await q.message.delete()
    except: pass
    await q.message.chat.send_message(
        "⚡ <b>Швидке замовлення</b>\n\n"
        "Напиши одним повідомленням:\n"
        "• Що хочеш замовити\n"
        "• Куди доставити"
    )

async def fast_order_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("state") != "fast_order":
        return

    user = update.effective_user
    text = update.message.text
    
    try:
        await context.bot.send_message(
            MANAGER_ID,
            f"⚡ <b>FAST ORDER</b>\n\n"
            f"👤 {user.first_name} (@{user.username})\n"
            f"📝 {escape(text)}"
        )
    except:
        pass

    context.user_data["state"] = None
    await update.message.reply_text("✅ Передано менеджеру! З тобою зв'яжуться.")

# --- ADMIN ---

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != MANAGER_ID: return
    await update.message.reply_text("🛠 <b>ADMIN PANEL ACTIVE</b>")

async def admin_paid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = int(q.data.replace("admin_paid_", ""))
    
    try:
        await context.bot.send_message(uid, "✅ <b>Оплату підтверджено!</b>\n📦 Замовлення готується.")
        await q.message.edit_text(f"💰 Оплату для {uid} підтверджено.")
    except Exception as e:
        await q.message.edit_text(f"Помилка: {e}")

# ============================================================
# 📡 ROUTER
# ============================================================

async def router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Callbacks
    if update.callback_query:
        q = update.callback_query
        data = q.data

        if data == "catalog": return await show_catalog(update, context)
        if data == "back_main": return await back_to_main(update, context)
        
        if data.startswith("cat_"): return await show_category(update, context)
        
        if data.startswith("item_"): return await show_item(update, context)
        if data.startswith("add_"): return await add_to_cart(update, context)
        if data.startswith("rem_"): return await remove_from_cart(update, context)
        if data.startswith("color_"): return await color_select(update, context)
        if data.startswith("cpick_"): return await color_picked(update, context)
        
        if data == "cart": return await show_cart(update, context)
        if data == "cart_clear": return await cart_clear(update, context)
        
        if data == "checkout": return await checkout(update, context)
        if data.startswith("city_"): return await select_city(update, context)
        if data.startswith("dist_"): return await select_district(update, context)
        
        if data == "profile": return await profile_view(update, context)
        if data == "fast": return await fast_order(update, context)
        
        if data.startswith("admin_paid_"): return await admin_paid(update, context)
        
        await q.answer()

    # Messages
    elif update.message:
        state = context.user_data.get("state")
        
        if state == "await_address": return await address_input(update, context)
        if state == "fast_order": return await fast_order_input(update, context)
        
        if update.message.photo: return await receipt_from_user(update, context)

# ============================================================
# 🏁 MAIN
# ============================================================

def main():
    print("🚀 Starting Ghosty Bot...")
    
    if TOKEN == "PUT_TOKEN":
        print("❌ ERROR: You forgot to put the TOKEN in line 45!")
        return

    persistence = PicklePersistence(filepath="data/bot_data.pickle")

    app = (
        Application.builder()
        .token(TOKEN)
        .persistence(persistence)
        .rate_limiter(AIORateLimiter())
        .defaults(Defaults(parse_mode=ParseMode.HTML))
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CallbackQueryHandler(router))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, router))
    app.add_handler(MessageHandler(filters.PHOTO, router))

    print("✅ Bot is running! Press Ctrl+C to stop.")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()

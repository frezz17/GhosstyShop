import logging
import random
from datetime import datetime, timedelta
from html import escape

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
    PicklePersistence
)
from telegram.error import BadRequest

# ===================== CONFIG =====================
TOKEN = "8351638507:AAG2HP0OmYx7ip8-uZcLQCilPTfoBhtEGq0"

MANAGER_USERNAME = "ghosstydp"
CHANNEL_URL = "https://t.me/GhostyStaffDP"
PAYMENT_URL = "https://heylink.me/ghosstyshop/"
WELCOME_PHOTO = "https://i.ibb.co/y7Q194N/1770068775663.png"

DISCOUNT_PERCENT = 35
DISCOUNT_MULT = 0.65
BASE_VIP_DATE = datetime.strptime("25.03.2026", "%d.%m.%Y")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ghosty-bot")

# ===================== HELPERS =====================
def apply_discount(price: float) -> float:
    return round(price * DISCOUNT_MULT, 2)

def gen_promo(uid: int) -> str:
    return f"GHST{uid % 10000}{random.randint(100,999)}"

def gen_order_id(uid: int) -> str:
    return f"GHST-{uid}-{random.randint(1000,9999)}"

def vip_until(profile: dict) -> datetime:
    return profile["vip_base"] + timedelta(days=7 * profile.get("referrals", 0))

async def safe_edit_media(message, photo_url: str, caption: str, kb):
    try:
        await message.edit_media(
            InputMediaPhoto(
                media=photo_url,
                caption=caption,
                parse_mode="HTML"
            ),
            reply_markup=kb
        )
    except BadRequest:
        try:
            await message.delete()
            await message.chat.send_photo(
                photo=photo_url,
                caption=caption,
                parse_mode="HTML",
                reply_markup=kb
            )
        except Exception as e:
            logger.warning(f"safe_edit_media failed: {e}")

# ===================== CITIES / DISTRICTS =====================
CITIES = [
    "Київ", "Дніпро", "Камʼянське", "Харків", "Одеса",
    "Львів", "Запоріжжя", "Полтава", "Кривий Ріг", "Черкаси"
]

DISTRICTS = {
    "Київ": ["Дарницький", "Оболонський", "Печерський"],
    "Дніпро": ["Центр", "Перемога", "Лівий берег"],
    "Камʼянське": ["Центр", "Соцмісто", "Лівобережжя"],
    "Харків": ["Салтівка", "Центр"],
    "Одеса": ["Приморський", "Таїрово"],
    "Львів": ["Сихів", "Центр"],
    "Запоріжжя": ["Бабурка"],
    "Полтава": ["Центр"],
    "Кривий Ріг": ["ЦМР"],
    "Черкаси": ["Центр"]
}

# ===================== PRODUCTS =====================
HHC_VAPES = {
    100: {
        "name": "😵‍💫 Packwoods Purple 1ml",
        "price": 549,
        "img": "https://i.ibb.co/DHXXSh2d/Ghost-Vape-3.jpg",
        "desc": "90% HHC | Hybrid\n💜 Релакс + ейфорія"
    },
    101: {
        "name": "🍊 Packwoods Orange 1ml",
        "price": 629,
        "img": "https://i.ibb.co/V03f2yYF/Ghost-Vape-1.jpg",
        "desc": "90% HHC | Hybrid\n⚡ Фокус"
    },
    102: {
        "name": "🌸 Packwoods Pink 1ml",
        "price": 719,
        "img": "https://i.ibb.co/65j1901/Ghost-Vape-2.jpg",
        "desc": "90% HHC | Hybrid\n🎉 Мʼякий стоун"
    },
    103: {
        "name": "❄️ Whole Melt Mint 2ml",
        "price": 849,
        "img": "https://i.ibb.co/675LQrNB/Ghost-Vape-4.jpg",
        "desc": "95% HHC | Sativa\n🧠 Чистий розум"
    },
    104: {
        "name": "🌴 Jungle Boys White 2ml",
        "price": 999,
        "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg",
        "desc": "95% HHC | Indica\n😴 Глибокий релакс"
    }
}

LIQUID_GIFTS = [
    "🎁 Pumpkin Latte",
    "🎁 Glintwine",
    "🎁 Christmas Tree"
]

PODS = {
    500: {
        "name": "🔌 Vaporesso XROS 3 Mini",
        "price": 499,
        "colors": {
            "black": {
                "title": "⚫ Чорний",
                "photos": [
                    "https://ibb.co/yFSQ5QSn",
                    "https://ibb.co/LzgrzZjC"
                ]
            },
            "pink": {
                "title": "🌸 Рожевий",
                "photos": [
                    "https://ibb.co/Q3ZNTBvg"
                ]
            }
        },
        "desc": "🔋 1000 mAh\n💨 MTL / RDL\n⚡ Type-C"
    },
    501: {
        "name": "🔌 Vaporesso XROS Pro",
        "price": 689,
        "colors": {
            "black": {
                "title": "⚫ Чорний",
                "photos": ["https://ibb.co/ynYwSMt6"]
            },
            "red": {
                "title": "🔴 Червоний",
                "photos": ["https://ibb.co/3mV7scXr"]
            }
        },
        "desc": "🔋 1200 mAh\n⚡ Fast Charge\n💨 Регуляція тяги"
    }
}

# ===================== MENUS =====================
def main_menu():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("👤 Профіль", callback_data="profile"),
            InlineKeyboardButton("🛍 Асортимент", callback_data="assortment")
        ],
        [
            InlineKeyboardButton("📍 Місто", callback_data="select_city"),
            InlineKeyboardButton("🛒 Кошик", callback_data="cart")
        ],
        [
            InlineKeyboardButton("📦 Замовлення", callback_data="orders"),
            InlineKeyboardButton("👨‍💻 Менеджер", url=f"https://t.me/{MANAGER_USERNAME}")
        ],
        [
            InlineKeyboardButton("📜 Угода", callback_data="terms"),
            InlineKeyboardButton("📢 Канал", url=CHANNEL_URL)
        ]
    ])
  # ===================== START =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = context.args

    if "profile" not in context.user_data:
        context.user_data["profile"] = {
            "uid": user.id,
            "name": user.first_name,
            "username": user.username,
            "phone": None,
            "city": None,
            "district": None,
            "address": None,
            "promo": gen_promo(user.id),
            "referrals": 0,
            "vip_base": BASE_VIP_DATE,
            "orders": []
        }

    # ===== REFERRAL =====
    if args:
        try:
            ref_id = int(args[0])
            if ref_id != user.id and "referred" not in context.user_data:
                context.user_data["referred"] = True
                # ⚠️ у реальному продакшені це йде в БД
        except ValueError:
            pass

    profile = context.user_data["profile"]
    vip_date = vip_until(profile)

    gifts = "\n".join(LIQUID_GIFTS)

    text = (
        f"👋 <b>{escape(user.first_name)}</b>, ласкаво просимо в <b>Ghosty Shop</b> 💨\n\n"
        f"🎫 Промокод: <code>{profile['promo']}</code> (-35%)\n"
        f"👑 VIP до: <b>{vip_date.strftime('%d.%m.%Y')}</b>\n"
        f"🚚 VIP доставка: <b>Безкоштовно</b>\n\n"
        f"🎁 <b>Подарунок до кожного замовлення:</b>\n{gifts}\n\n"
        f"👇 Обери дію:"
    )

    if update.message:
        await update.message.reply_photo(
            photo=WELCOME_PHOTO,
            caption=text,
            parse_mode="HTML",
            reply_markup=main_menu()
        )
    else:
        await update.callback_query.message.edit_caption(
            caption=text,
            parse_mode="HTML",
            reply_markup=main_menu()
        )

# ===================== PROFILE =====================
async def show_profile(q, context):
    profile = context.user_data["profile"]
    vip_date = vip_until(profile)

    text = (
        f"👤 <b>Профіль</b>\n\n"
        f"🧑 {escape(profile['name'])}\n"
        f"🔗 @{profile.get('username','—')}\n"
        f"📞 {profile.get('phone','—')}\n"
        f"📍 {profile.get('city','—')} / {profile.get('district','—')}\n"
        f"🏠 {profile.get('address','—')}\n\n"
        f"🎫 Промокод: <code>{profile['promo']}</code>\n"
        f"👥 Реферали: {profile['referrals']}\n"
        f"👑 VIP до: <b>{vip_date.strftime('%d.%m.%Y')}</b>"
    )

    kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✏️ Адреса", callback_data="edit_address"),
            InlineKeyboardButton("🔗 Реферал", callback_data="ref_link")
        ],
        [
            InlineKeyboardButton("⬅️ Назад", callback_data="main"),
            InlineKeyboardButton("🏠 Меню", callback_data="main")
        ]
    ])

    await q.message.edit_caption(
        caption=text,
        parse_mode="HTML",
        reply_markup=kb
    )

# ===================== CITY =====================
async def select_city(q):
    buttons = []
    for city in CITIES:
        buttons.append([InlineKeyboardButton(city, callback_data=f"city_{city}")])

    buttons.append([InlineKeyboardButton("⬅️ Назад", callback_data="main")])

    await q.message.edit_caption(
        caption="📍 <b>Оберіть місто</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def select_district(q, city):
    buttons = []
    for d in DISTRICTS.get(city, []):
        buttons.append([InlineKeyboardButton(d, callback_data=f"district_{d}")])

    await q.message.edit_caption(
        caption=f"📍 <b>{city}</b>\nОберіть район:",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(buttons)
              )
  # ===================== ASSORTMENT =====================
async def show_assortment(q):
    kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("😵‍💫 HHC / ННС", callback_data="hhc"),
            InlineKeyboardButton("🔌 Pod-системи", callback_data="pods")
        ],
        [
            InlineKeyboardButton("💧 Рідини", callback_data="liquids"),
            InlineKeyboardButton("⚡ Швидке замовлення", callback_data="fast_all")
        ],
        [
            InlineKeyboardButton("⬅️ Назад", callback_data="main")
        ]
    ])

    await q.message.edit_caption(
        caption="🛍️ <b>Асортимент</b>\n\nОберіть категорію:",
        parse_mode="HTML",
        reply_markup=kb
    )

# ===================== CATEGORY LIST =====================
async def list_items(q, items: dict, back_cb: str, title: str):
    buttons = []

    for pid, item in items.items():
        buttons.append([
            InlineKeyboardButton(item["name"], callback_data=f"item_{pid}"),
            InlineKeyboardButton("⚡", callback_data=f"fast_{pid}")
        ])

    buttons.append([
        InlineKeyboardButton("⬅️ Назад", callback_data=back_cb),
        InlineKeyboardButton("🏠 Меню", callback_data="main")
    ])

    await q.message.edit_caption(
        caption=title,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# ===================== ITEM VIEW =====================
async def show_item(q, context, pid: int):
    item = HHC_VAPES.get(pid) or LIQUIDS.get(pid) or PODS.get(pid)

    if not item:
        await q.message.reply_text("❌ Товар не знайдено")
        return

    base = item["price"]
    final = apply_discount(base)

    caption = (
        f"<b>{item['name']}</b>\n\n"
        f"{item.get('desc','')}\n\n"
        f"❌ {base} грн\n"
        f"✅ <b>{final} грн (-35%)</b>\n"
        f"🎁 3 рідини у подарунок\n"
        f"🚚 VIP доставка: 0 грн"
    )

    kb_rows = [
        [
            InlineKeyboardButton("🎨 Колір", callback_data=f"color_{pid}"),
            InlineKeyboardButton("⚡ Швидко", callback_data=f"fast_{pid}")
        ],
        [
            InlineKeyboardButton("🛒 В кошик", callback_data=f"add_{pid}"),
            InlineKeyboardButton("👨‍💻 Менеджер", url=f"https://t.me/{MANAGER_USERNAME}")
        ],
        [
            InlineKeyboardButton("⬅️ Назад", callback_data="pods" if pid >= 500 else "assortment")
        ]
    ]

    photo = item["imgs"][0] if "imgs" in item else item["img"]

    await safe_edit_media(
        q.message,
        photo,
        caption,
        InlineKeyboardMarkup(kb_rows)
    )

# ===================== COLOR SELECT =====================
async def select_color(q, context, pid):
    item = PODS.get(pid)
    if not item:
        await q.answer("❌ Кольори недоступні", show_alert=True)
        return

    buttons = []
    for idx, img in enumerate(item["imgs"]):
        buttons.append([
            InlineKeyboardButton(f"🎨 Варіант {idx+1}", callback_data=f"colorpick_{pid}_{idx}")
        ])

    buttons.append([InlineKeyboardButton("⬅️ Назад", callback_data=f"item_{pid}")])

    await q.message.edit_caption(
        caption=f"🎨 <b>Оберіть колір</b>\n\n{item['name']}",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def apply_color(q, context, pid, idx):
    item = PODS.get(pid)
    if not item:
        return

    context.user_data["selected_color"] = idx
    await show_item(q, context, pid)

# ===================== CART =====================
def get_cart(context):
    return context.user_data.setdefault("cart", [])

async def add_to_cart(q, context, pid):
    item = HHC_VAPES.get(pid) or LIQUIDS.get(pid) or PODS.get(pid)
    if not item:
        return

    cart = get_cart(context)
    cart.append(pid)

    await q.answer("✅ Додано в кошик")

async def show_cart(q, context):
    cart = get_cart(context)
    if not cart:
        await q.message.edit_caption(
            caption="🛒 <b>Кошик порожній</b>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Назад", callback_data="assortment")]
            ])
        )
        return

    total = 0
    lines = []
    buttons = []

    for i, pid in enumerate(cart):
        item = HHC_VAPES.get(pid) or LIQUIDS.get(pid) or PODS.get(pid)
        price = apply_discount(item["price"])
        total += price
        lines.append(f"• {item['name']} — {price} грн")
        buttons.append([InlineKeyboardButton(f"❌ {item['name']}", callback_data=f"del_{i}")])

    text = (
        "🛒 <b>Ваш кошик</b>\n\n"
        + "\n".join(lines)
        + f"\n\n💰 <b>Разом: {total} грн</b>\n🎁 3 рідини у подарунок"
    )

    buttons.append([
        InlineKeyboardButton("⚡ Замовити", callback_data="fast_all"),
        InlineKeyboardButton("⬅️ Назад", callback_data="assortment")
    ])

    await q.message.edit_caption(
        caption=text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def delete_from_cart(q, context, idx):
    cart = get_cart(context)
    if idx < len(cart):
        cart.pop(idx)
    await show_cart(q, context)

# ===================== FAST ORDER =====================
async def fast_start(q, context, pid=None):
    context.user_data["fast_pid"] = pid
    context.user_data["state"] = "fast_name"
    await q.message.reply_text(
        "⚡ <b>Швидке замовлення</b>\n\n✍️ Введіть імʼя та прізвище:",
        parse_mode="HTML"
    )
  # ===================== USER INPUT HANDLER =====================
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    state = context.user_data.get("state")
    profile = context.user_data["profile"]

    # ===== ADDRESS EDIT =====
    if state == "edit_address":
        profile["address"] = text
        context.user_data["state"] = None
        await update.message.reply_text("✅ Адресу збережено у профілі")
        return

    # ===== FAST ORDER FLOW =====
    if state == "fast_name":
        context.user_data["order_name"] = text
        context.user_data["state"] = "fast_phone"
        await update.message.reply_text("📞 Введіть номер телефону:")
        return

    if state == "fast_phone":
        profile["phone"] = text
        context.user_data["state"] = "fast_city"
        await update.message.reply_text("🏙️ Введіть місто доставки:")
        return

    if state == "fast_city":
        profile["city"] = text
        context.user_data["state"] = "fast_district"
        await update.message.reply_text("📍 Введіть район:")
        return

    if state == "fast_district":
        profile["district"] = text
        context.user_data["state"] = "fast_address"
        await update.message.reply_text("🏠 Введіть адресу доставки:")
        return

    if state == "fast_address":
        profile["address"] = text
        context.user_data["state"] = None
        await finalize_order(update, context)
        return

# ===================== FINALIZE ORDER =====================
async def finalize_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    profile = context.user_data["profile"]
    cart = context.user_data.get("cart", [])
    pid = context.user_data.get("fast_pid")

    items = []

    if pid:
        item = HHC_VAPES.get(pid) or LIQUIDS.get(pid) or PODS.get(pid)
        if item:
            items.append(item)
    else:
        for cid in cart:
            item = HHC_VAPES.get(cid) or LIQUIDS.get(cid) or PODS.get(cid)
            if item:
                items.append(item)

    if not items:
        await update.message.reply_text("❌ Замовлення порожнє")
        return

    order_id = gen_order_id(profile["uid"])
    total = sum(apply_discount(i["price"]) for i in items)

    # ===== USER MESSAGE =====
    user_text = (
        f"✅ <b>Замовлення сформовано</b>\n\n"
        f"🆔 <b>{order_id}</b>\n\n"
        + "\n".join(f"• {i['name']} — {apply_discount(i['price'])} грн" for i in items)
        + f"\n\n💰 <b>До оплати: {total} грн</b>\n"
        f"🎫 Промокод: <code>{profile['promo']}</code>\n"
        f"🎁 <b>3 рідини у подарунок</b>\n\n"
        f"📨 Натисніть кнопку нижче, щоб передати замовлення менеджеру"
    )

    kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📨 Надіслати менеджеру", callback_data=f"send_manager_{order_id}")
        ],
        [
            InlineKeyboardButton("🏠 В головне меню", callback_data="main")
        ]
    ])

    await update.message.reply_text(
        user_text,
        parse_mode="HTML",
        reply_markup=kb
    )

    context.user_data["last_order"] = {
        "id": order_id,
        "items": items,
        "total": total
    }
    context.user_data["cart"] = []

# ===================== SEND TO MANAGER =====================
async def send_to_manager(update: Update, context: ContextTypes.DEFAULT_TYPE, order_id: str):
    profile = context.user_data["profile"]
    order = context.user_data.get("last_order")

    if not order or order["id"] != order_id:
        await update.callback_query.answer("❌ Замовлення не знайдено", show_alert=True)
        return

    text = (
        f"🆕 <b>НОВЕ ЗАМОВЛЕННЯ</b>\n\n"
        f"🆔 {order_id}\n\n"
        f"👤 {profile['name']} (@{profile.get('username','—')})\n"
        f"📞 {profile.get('phone','—')}\n"
        f"🏙️ {profile.get('city','—')} / {profile.get('district','—')}\n"
        f"🏠 {profile.get('address','—')}\n\n"
        + "\n".join(f"• {i['name']} — {apply_discount(i['price'])} грн" for i in order["items"])
        + f"\n\n💰 Разом: {order['total']} грн\n"
        f"🎫 Промокод: {profile['promo']}\n"
        f"🎁 3 рідини у подарунок"
    )

    await context.bot.send_message(
        chat_id=f"@{MANAGER_USERNAME}",
        text=text,
        parse_mode="HTML"
    )

    await update.callback_query.message.edit_text(
        "✅ Замовлення передано менеджеру\n⏳ Очікуйте підтвердження",
        parse_mode="HTML"
    )
# ===================== CALLBACK ROUTER =====================
async def callbacks_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data
    profile = context.user_data.get("profile", {})

    # ===== MAIN / NAV =====
    if data == "main":
        await start(update, context)

    elif data == "assortment":
        await show_assortment(q)

    elif data == "profile":
        await show_profile(q, context)

    elif data == "cart":
        await show_cart(q, context)

    elif data == "orders":
        await show_orders(q, context)

    elif data == "terms":
        await show_terms(q)

    # ===== CITY / DISTRICT =====
    elif data == "city":
        await select_city(q)

    elif data.startswith("city_"):
        city = data.replace("city_", "")
        profile["city"] = city
        await after_city_selected(q, context, city)

    elif data == "select_district":
        await select_district(q, context)

    elif data.startswith("district_"):
        district = data.replace("district_", "")
        profile["district"] = district
        await district_saved(q, district)

    # ===== ASSORTMENT =====
    elif data.startswith("item_"):
        pid = int(data.split("_")[1])
        await show_item(q, context, pid)

    elif data.startswith("color_"):
        pid = int(data.split("_")[1])
        await select_color(q, context, pid)

    elif data.startswith("colorpick_"):
        _, pid, idx = data.split("_")
        await apply_color(q, context, int(pid), int(idx))

    # ===== CART =====
    elif data.startswith("add_"):
        pid = int(data.split("_")[1])
        await add_to_cart(q, context, pid)

    elif data.startswith("del_"):
        pid = int(data.split("_")[1])
        await delete_from_cart(q, context, pid)

    # ===== FAST ORDER =====
    elif data.startswith("fast_"):
        pid = int(data.split("_")[1])
        await fast_start(q, context, pid)

    elif data.startswith("send_manager_"):
        order_id = data.replace("send_manager_", "")
        await send_to_manager(update, context, order_id)

    else:
        await q.answer("⚠️ Невідома дія", show_alert=True)
        
  # ===================== CART HELPERS =====================
async def add_to_cart(q, context, pid: int):
    cart = context.user_data.setdefault("cart", [])
    cart.append(pid)
    await q.answer("🛒 Додано в кошик")

async def delete_from_cart(q, context, index: int):
    cart = context.user_data.get("cart", [])
    if 0 <= index < len(cart):
        cart.pop(index)
        await q.answer("❌ Видалено")
    await show_cart(q, context)

async def show_cart(q, context):
    cart = context.user_data.get("cart", [])
    if not cart:
        await q.message.edit_text(
            "🛒 <b>Кошик порожній</b>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 В головне меню", callback_data="main")]
            ])
        )
        return

    buttons = []
    total = 0

    for i, pid in enumerate(cart):
        item = HHC_VAPES.get(pid) or LIQUIDS.get(pid) or PODS.get(pid)
        if not item:
            continue
        price = apply_discount(item["price"])
        total += price
        buttons.append([
            InlineKeyboardButton(f"{item['name']} — {price} грн", callback_data=f"item_{pid}"),
            InlineKeyboardButton("❌", callback_data=f"del_{i}")
        ])

    buttons.append([
        InlineKeyboardButton("⚡ Швидке замовлення", callback_data="fast_all"),
        InlineKeyboardButton("🏠 В головне меню", callback_data="main")
    ])

    await q.message.edit_text(
        f"🛒 <b>Кошик</b>\n\n💰 Разом: <b>{total} грн</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# ===================== FAST ORDER =====================
async def fast_start(q, context, pid=None):
    context.user_data["fast_pid"] = pid
    context.user_data["state"] = "fast_name"
    await q.message.reply_text(
        "⚡ <b>Швидке замовлення</b>\n\n✍️ Введіть імʼя та прізвище:",
        parse_mode="HTML"
    )

# ===================== COLOR SELECTION =====================
async def select_color(q, context, pid: int):
    item = PODS.get(pid)
    if not item:
        await q.answer("❌ Кольори недоступні")
        return

    buttons = []
    for i, _ in enumerate(item["imgs"]):
        buttons.append([InlineKeyboardButton(f"🎨 Варіант {i+1}", callback_data=f"colorpick_{pid}_{i}")])

    buttons.append([
        InlineKeyboardButton("⬅️ Назад", callback_data=f"item_{pid}"),
        InlineKeyboardButton("🏠 В головне меню", callback_data="main")
    ])

    await q.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(buttons))

async def apply_color(q, context, pid: int, idx: int):
    item = PODS.get(pid)
    if not item:
        return

    context.user_data["selected_color"] = idx
    await q.answer("🎨 Колір обрано")

    await show_item(q, context, pid)

# ===================== SHOW ITEM =====================
async def show_item(q, context, pid: int):
    item = HHC_VAPES.get(pid) or LIQUIDS.get(pid) or PODS.get(pid)
    if not item:
        await q.answer("❌ Товар не знайдено")
        return

    base = item["price"]
    final = apply_discount(base)

    caption = (
        f"<b>{item['name']}</b>\n\n"
        f"{item.get('desc','')}\n\n"
        f"❌ {base} грн\n"
        f"✅ <b>{final} грн (-35%)</b>\n"
        f"🎁 3 рідини у подарунок\n"
        f"🚚 VIP доставка: 0 грн"
    )

    kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎨 Обрати колір", callback_data=f"color_{pid}"),
            InlineKeyboardButton("⚡ Швидке замовлення", callback_data=f"fast_{pid}")
        ],
        [
            InlineKeyboardButton("🛒 В кошик", callback_data=f"add_{pid}"),
            InlineKeyboardButton("👨‍💻 Менеджер", url=f"https://t.me/{MANAGER_USERNAME}")
        ],
        [
            InlineKeyboardButton("⬅️ Назад", callback_data="assortment"),
            InlineKeyboardButton("🏠 В головне меню", callback_data="main")
        ]
    ])

    photo = item["imgs"][0] if "imgs" in item else item["img"]

    await safe_edit_media(q.message, photo, caption, kb)

# ===================== APPLICATION START =====================
def main():
    persistence = PicklePersistence(filepath="ghosty_data.pkl")

    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .persistence(persistence)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callbacks_router))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    logger.info("🚀 Ghosty Shop Bot started")
    app.run_polling()

if __name__ == "__main__":
    main()
  

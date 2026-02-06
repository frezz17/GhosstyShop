# =========================================================
# GHOSTY SHOP BOT — FULL VERSION
# python-telegram-bot v20+
# PART 1 / 4 — CONFIG, GLOBAL DATA, PRODUCTS, CITIES
# =========================================================

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

DELIVERY_INFO = (
    "🚚 <b>Доставка</b>\n\n"
    "• Нова Пошта / Укрпошта\n"
    "• Відправка в день замовлення\n"
    "• VIP-доставка — <b>БЕЗКОШТОВНО</b>"
)

TERMS_TEXT = (
    "📜 <b>Угода користувача</b>\n\n"
    "Оформлюючи замовлення, ви підтверджуєте згоду "
    "з правилами магазину та політикою конфіденційності."
)

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
        await message.delete()
        await message.chat.send_photo(
            photo=photo_url,
            caption=caption,
            parse_mode="HTML",
            reply_markup=kb
        )

# ===================== CITIES & DISTRICTS =====================
CITIES = [
    "Дніпро",
    "Київ",
    "Харків",
    "Одеса",
    "Львів",
    "Запоріжжя",
    "Камʼянське",
    "Кривий Ріг",
    "Полтава",
    "Черкаси"
]

CITY_DISTRICTS = {
    "Дніпро": [
        "Центральний",
        "Соборний",
        "Шевченківський",
        "Індустріальний",
        "АНД",
        "Новокодацький",
        "Самарський",
        "Чечелівський"
    ],
    "Київ": [
        "Печерський",
        "Шевченківський",
        "Дарницький",
        "Дніпровський",
        "Подільський",
        "Оболонський",
        "Соломʼянський",
        "Святошинський"
    ],
    "Камʼянське": [
        "Центральний",
        "Південний",
        "Заводський",
        "Дніпровський",
        "Черемушки",
        "Романково",
        "Соцмісто",
        "Лівобережний"
    ]
}

# ===================== GIFTS (AUTO) =====================
GIFT_LIQUIDS = [
    "🎁 Chaser Strawberry Jelly 30ml 65mg",
    "🎁 Chaser Mystery One 30ml 65mg",
    "🎁 Chaser Fall Tea 30ml 65mg"
]

# ===================== HHC / ННС (5 шт) =====================
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
        "desc": "90% HHC | Hybrid\n⚡ Фокус та енергія"
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

# ===================== LIQUIDS (3 набори) =====================
LIQUIDS = {
    301: {
        "name": "🎃 Pumpkin Latte",
        "price": 269,
        "img": "https://ibb.co/Y7qn69Ds",
        "desc": "☕ Гарбузовий латте"
    },
    302: {
        "name": "🍷 Glintwine",
        "price": 269,
        "img": "https://ibb.co/wF8r7Nmc",
        "desc": "🔥 Пряний глінтвейн"
    },
    303: {
        "name": "🎄 Christmas Tree",
        "price": 269,
        "img": "https://ibb.co/vCPGV8RV",
        "desc": "🌲 Хвоя та холод"
    }
}

# ===================== POD SYSTEMS (БАГАТО, З КОЛЬОРАМИ) =====================
PODS = {
    500: {
        "name": "🔌 Vaporesso XROS 3 Mini",
        "price": 499,
        "desc": "🔋 1000 mAh | ⚡ Type-C | 💨 MTL/RDL",
        "colors": {
            "Чорний": ["https://ibb.co/yFSQ5QSn"],
            "Голубий": ["https://ibb.co/LzgrzZjC"],
            "Рожевий": ["https://ibb.co/Q3ZNTBvg"]
        }
    },
    501: {
        "name": "🔌 Vaporesso XROS 5 Mini",
        "price": 579,
        "desc": "🔥 COREX 2.0 | ⚡ Fast Charge",
        "colors": {
            "Рожевий": ["https://ibb.co/RkNgt1Qr"],
            "Фіолетовий": ["https://ibb.co/KxvJC1bV"],
            "Чорний": ["https://ibb.co/WpMYBCH1"]
        }
    },
    502: {
        "name": "🔌 Vaporesso XROS Pro",
        "price": 689,
        "desc": "🔋 1200 mAh | 💨 Регуляція затяжки",
        "colors": {
            "Чорний": ["https://ibb.co/ynYwSMt6"],
            "Червоний": ["https://ibb.co/3mV7scXr"]
        }
    }
}
# =========================================================
# PART 2 / 4 — START, MAIN MENU, PROFILE, CITY & DISTRICT
# =========================================================

# ===================== START =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ...
    user = update.effective_user

    # ---------- INIT USER DATA ----------
    if "profile" not in context.user_data:
        context.user_data["profile"] = {
            "id": user.id,
            "name": user.full_name,
            "username": user.username or "—",
            "city": None,
            "district": None,
            "address": None,
            "phone": None,
            "promo": gen_promo(user.id),
            "vip_base": BASE_VIP_DATE,
            "referrals": 0
        }

    if "cart" not in context.user_data:
        context.user_data["cart"] = []

    if "orders" not in context.user_data:
        context.user_data["orders"] = []
if "cart" not in context.user_data:
    context.user_data["cart"] = []

if "orders" not in context.user_data:
    context.user_data["orders"] = []
    # ---------- REFERRAL ----------
    if context.args:
        ref_id = context.args[0]
        if ref_id.isdigit() and int(ref_id) != user.id:
            context.user_data["profile"]["referrals"] += 1

    await update.message.reply_photo(
        photo=WELCOME_PHOTO,
        caption=(
            "👋 <b>Ласкаво просимо до GHOSTY SHOP</b>\n\n"
            "💨 HHC / ННС вейпи\n"
            "🔌 Pod-системи\n"
            "💧 Рідини\n\n"
            "🎁 <b>Подарунок до КОЖНОГО замовлення</b>\n"
            "🏷 <b>-35% персональна знижка</b>\n"
            "🚚 VIP-доставка — безкоштовна"
        ),
        parse_mode="HTML",
        reply_markup=main_menu_kb()
    )

# ===================== MAIN MENU =====================
def main_menu_kb():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("👤 Профіль", callback_data="profile"),
            InlineKeyboardButton("🛍 Асортимент", callback_data="assortment")
        ],
        [
            InlineKeyboardButton("📍 Обрати місто", callback_data="city"),
            InlineKeyboardButton("🛒 Кошик", callback_data="cart")
        ],
        [
            InlineKeyboardButton("📦 Мої замовлення", callback_data="orders"),
            InlineKeyboardButton("👨‍💼 Менеджер", callback_data="manager")
        ],
        [
            InlineKeyboardButton("📜 Угода", callback_data="terms"),
            InlineKeyboardButton("📢 Канал", url=CHANNEL_URL)
        ]
    ])

# ===================== PROFILE =====================
async def show_profile(q, context):
    profile = context.user_data["profile"]
    vip_date = vip_until(profile).strftime("%d.%m.%Y")

    text = (
        "👤 <b>Ваш профіль</b>\n\n"
        f"🆔 ID: <code>{profile['id']}</code>\n"
        f"👤 Імʼя: {escape(profile['name'])}\n"
        f"🔗 Username: @{profile['username']}\n\n"
        f"📍 Місто: {profile['city'] or '—'}\n"
        f"🏘 Район: {profile['district'] or '—'}\n"
        f"🏠 Адреса: {profile['address'] or '—'}\n"
        f"📞 Телефон: {profile['phone'] or '—'}\n\n"
        f"🏷 <b>Промокод:</b> <code>{profile['promo']}</code> (-35%)\n"
        f"💎 <b>VIP до:</b> {vip_date}\n"
        f"👥 Рефералів: {profile['referrals']}"
    )

    kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📍 Обрати місто", callback_data="city"),
            InlineKeyboardButton("🏠 Змінити адресу", callback_data="set_address")
        ],
        [
            InlineKeyboardButton("⬅️ Назад", callback_data="main"),
            InlineKeyboardButton("🏠 В головне меню", callback_data="main")
        ]
    ])

    await q.message.edit_caption(
        caption=text,
        parse_mode="HTML",
        reply_markup=kb
    )

# ===================== CITY SELECT =====================
async def show_cities(q):
    buttons = [
        [InlineKeyboardButton(f"🏙 {c}", callback_data=f"city_{c}")]
        for c in CITIES
    ]
    buttons.append([
        InlineKeyboardButton("⬅️ Назад", callback_data="main"),
        InlineKeyboardButton("🏠 В головне меню", callback_data="main")
    ])

    await q.message.edit_text(
        "📍 <b>Оберіть місто:</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def save_city(q, context, city):
    context.user_data["profile"]["city"] = city
    context.user_data["profile"]["district"] = None

    await q.message.edit_text(
        f"✅ <b>Місто збережено:</b> {city}\n\nОберіть район:",
        parse_mode="HTML",
        reply_markup=district_kb(city)
    )

# ===================== DISTRICT =====================
def district_kb(city):
    buttons = [
        [InlineKeyboardButton(f"📍 {d}", callback_data=f"district_{d}")]
        for d in CITY_DISTRICTS.get(city, [])
    ]
    buttons.append([
        InlineKeyboardButton("⬅️ Назад", callback_data="city"),
        InlineKeyboardButton("🏠 В головне меню", callback_data="main")
    ])
    return InlineKeyboardMarkup(buttons)

async def save_district(q, context, district):
    context.user_data["profile"]["district"] = district

    await q.message.edit_text(
        f"✅ <b>Район збережено:</b> {district}",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("👤 Профіль", callback_data="profile"),
                InlineKeyboardButton("🏠 В головне меню", callback_data="main")
            ]
        ])
    )

# ===================== ADDRESS INPUT =====================
async def ask_address(q):
    await q.message.edit_text(
        "🏠 <b>Введіть адресу доставки:</b>",
        parse_mode="HTML"
    )
    context = q._bot.context  # safe placeholder

async def save_address(update: Update, context):
    context.user_data["profile"]["address"] = update.message.text
    await update.message.reply_text(
        "✅ Адресу збережено",
        reply_markup=main_menu_kb()
)


# ===================== CART LOGIC =====================
  async def add_to_cart(q, context, pid: int):
    item = HHC_VAPES.get(pid) or LIQUIDS.get(pid) or PODS.get(pid)

    if not item:
        await q.answer("❌ Товар не знайдено")
        return

    if "cart" not in context.user_data:
        context.user_data["cart"] = []

    context.user_data["cart"].append({
        "pid": pid,
        "name": item["name"],
        "price": apply_discount(item["price"])
    })

    await q.answer("✅ Додано в кошик")

# ===================== CALLBACKS =====================
async def callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data

    # 🔐 init
    if "profile" not in context.user_data:
        await start(update, context)
        return

    # ===== MAIN =====
    if data == "main":
        await start(update, context)

    # ===== ASSORTMENT =====
    elif data == "assortment":
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
                InlineKeyboardButton("🏠 В головне меню", callback_data="main")
            ]
        ])

        await q.message.edit_caption(
            caption="🛍 <b>Асортимент</b>\n\nОберіть категорію 👇",
            parse_mode="HTML",
            reply_markup=kb
        )

    # ===== HHC =====
    elif data == "hhc":
        buttons = [
            [
                InlineKeyboardButton(item["name"], callback_data=f"item_{pid}"),
                InlineKeyboardButton("⚡", callback_data=f"fast_{pid}")
            ]
            for pid, item in HHC_VAPES.items()
        ]

        buttons.append([
            InlineKeyboardButton("⬅️ Назад", callback_data="assortment"),
            InlineKeyboardButton("🏠 В головне меню", callback_data="main")
        ])

        await q.message.edit_caption(
            caption="😵‍💫 <b>HHC / ННС</b>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    # ===== LIQUIDS =====
    elif data == "liquids":
        buttons = [
            [
                InlineKeyboardButton(item["name"], callback_data=f"item_{pid}"),
                InlineKeyboardButton("⚡", callback_data=f"fast_{pid}")
            ]
            for pid, item in LIQUIDS.items()
        ]

        buttons.append([
            InlineKeyboardButton("⬅️ Назад", callback_data="assortment"),
            InlineKeyboardButton("🏠 В головне меню", callback_data="main")
        ])

        await q.message.edit_caption(
            caption="💧 <b>Рідини</b>\n🎁 <i>Йдуть у подарунок до кожного замовлення</i>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    # ===== PODS =====
    elif data == "pods":
        buttons = [
            [
                InlineKeyboardButton(item["name"], callback_data=f"item_{pid}"),
                InlineKeyboardButton("⚡", callback_data=f"fast_{pid}")
            ]
            for pid, item in PODS.items()
        ]

        buttons.append([
            InlineKeyboardButton("⬅️ Назад", callback_data="assortment"),
            InlineKeyboardButton("🏠 В головне меню", callback_data="main")
        ])

        await q.message.edit_caption(
            caption="🔌 <b>Pod-системи</b>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    # ===== ITEM VIEW =====
    elif data.startswith("item_"):
        pid = int(data.split("_")[1])
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
            f"🎁 Рідини у подарунок\n"
            f"🚚 Доставка безкоштовна"
        )

        kb = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🛒 В кошик", callback_data=f"add_{pid}"),
                InlineKeyboardButton("⚡ Швидке замовлення", callback_data=f"fast_{pid}")
            ],
            [
                InlineKeyboardButton("👨‍💻 Менеджер", url=f"https://t.me/{MANAGER_USERNAME}")
            ],
            [
                InlineKeyboardButton("⬅️ Назад", callback_data="assortment"),
                InlineKeyboardButton("🏠 В головне меню", callback_data="main")
            ]
        ])

        photo = item["imgs"][0] if "imgs" in item else item["img"]

        await safe_edit_media(q.message, photo, caption, kb)

    # ===== ADD TO CART =====
    elif data.startswith("add_"):
        pid = int(data.split("_")[1])
        await add_to_cart(q, context, pid)

    # ===== FAST ORDER =====
    elif data.startswith("fast_"):
        pid = int(data.split("_")[1]) if "_" in data else None
        context.user_data["fast_pid"] = pid
        context.user_data["state"] = "fast_name"

        await q.message.reply_text(
            "⚡ <b>Швидке замовлення</b>\n\n✍️ Введіть імʼя та прізвище:",
            parse_mode="HTML"
      )
      # ===================== CALLBACKS =====================
async def callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data

    # ===== MAIN =====
    if data == "main":
        await start(update, context)

    # ===== ASSORTMENT =====
    elif data == "assortment":
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
                InlineKeyboardButton("🏠 В головне меню", callback_data="main")
            ]
        ])

        await q.message.edit_caption(
            caption="🛍️ <b>Асортимент</b>\n\nОберіть категорію:",
            parse_mode="HTML",
            reply_markup=kb
        )

    # ===== HHC =====
    elif data == "hhc":
        buttons = [
            [
                InlineKeyboardButton(item["name"], callback_data=f"item_{pid}"),
                InlineKeyboardButton("⚡", callback_data=f"fast_{pid}")
            ]
            for pid, item in HHC_VAPES.items()
        ]

        buttons.append([
            InlineKeyboardButton("⬅️ Назад", callback_data="assortment"),
            InlineKeyboardButton("🏠 В головне меню", callback_data="main")
        ])

        await q.message.edit_caption(
            caption="😵‍💫 <b>HHC / ННС</b>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    # ===== PODS =====
    elif data == "pods":
        buttons = [
            [
                InlineKeyboardButton(item["name"], callback_data=f"item_{pid}"),
                InlineKeyboardButton("⚡", callback_data=f"fast_{pid}")
            ]
            for pid, item in PODS.items()
        ]

        buttons.append([
            InlineKeyboardButton("⬅️ Назад", callback_data="assortment"),
            InlineKeyboardButton("🏠 В головне меню", callback_data="main")
        ])

        await q.message.edit_caption(
            caption="🔌 <b>Pod-системи</b>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    # ===== LIQUIDS =====
    elif data == "liquids":
        buttons = [
            [
                InlineKeyboardButton(item["name"], callback_data=f"item_{pid}"),
                InlineKeyboardButton("⚡", callback_data=f"fast_{pid}")
            ]
            for pid, item in LIQUIDS.items()
        ]

        buttons.append([
            InlineKeyboardButton("⬅️ Назад", callback_data="assortment"),
            InlineKeyboardButton("🏠 В головне меню", callback_data="main")
        ])

        await q.message.edit_caption(
            caption="💧 <b>Рідини</b>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    # ===== ITEM VIEW =====
    elif data.startswith("item_"):
        pid = int(data.split("_")[1])

        item = HHC_VAPES.get(pid) or LIQUIDS.get(pid) or PODS.get(pid)
        if not item:
            await q.answer("❌ Товар не знайдено")
            return

        base_price = item["price"]
        final_price = apply_discount(base_price)

        caption = (
            f"<b>{item['name']}</b>\n\n"
            f"{item.get('desc','')}\n\n"
            f"❌ {base_price} грн\n"
            f"✅ <b>{final_price} грн (-35%)</b>\n"
            f"🎁 Подарунок: 3 набори рідин\n"
            f"🚚 Доставка: Безкоштовна"
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

    # ===== ADD TO CART =====
    elif data.startswith("add_"):
        pid = int(data.split("_")[1])
        await add_to_cart(q, context, pid)

    # ===== FAST ORDER =====
    elif data == "fast_all":
        context.user_data["fast_pid"] = None
        context.user_data["state"] = "fast_name"
        await q.message.reply_text(
            "⚡ <b>Швидке замовлення</b>\n\n✍️ Введіть імʼя та прізвище:",
            parse_mode="HTML"
        )

    elif data.startswith("fast_"):
        pid = int(data.split("_")[1])
        context.user_data["fast_pid"] = pid
        context.user_data["state"] = "fast_name"
        await q.message.reply_text(
            "⚡ <b>Швидке замовлення</b>\n\n✍️ Введіть імʼя та прізвище:",
            parse_mode="HTML"
  )
  # ===================== TEXT INPUT HANDLER =====================
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    state = context.user_data.get("state")
    profile = context.user_data.setdefault("profile", {})

    # ===== ADDRESS EDIT FROM PROFILE =====
    if state == "edit_address":
        profile["address"] = text
        context.user_data["state"] = None

        await update.message.reply_text(
            "✅ <b>Адресу збережено в профілі</b>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("👤 Профіль", callback_data="profile"),
                    InlineKeyboardButton("🏠 В головне меню", callback_data="main")
                ]
            ])
        )
        return

    # ===== FAST ORDER FLOW =====
    if state == "fast_name":
        context.user_data["order_name"] = text
        context.user_data["state"] = "fast_phone"
        await update.message.reply_text("📞 Введіть номер телефону:")
        return

    if state == "fast_phone":
        profile["phone"] = text
        context.user_data["state"] = "fast_address"
        await update.message.reply_text("📦 Введіть адресу доставки:")
        return

    if state == "fast_address":
        profile["address"] = text
        context.user_data["state"] = None
        await finalize_fast_order(update, context)
        return
      # ===================== FINALIZE FAST ORDER =====================
async def finalize_fast_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    profile = context.user_data["profile"]
    pid = context.user_data.get("fast_pid")

    item = HHC_VAPES.get(pid) or LIQUIDS.get(pid) or PODS.get(pid)
    if not item:
        await update.message.reply_text("❌ Помилка: товар не знайдено")
        return

    order_id = gen_order_id(profile["uid"])
    base_price = item["price"]
    final_price = apply_discount(base_price)

    # ===== MESSAGE FOR USER =====
    user_text = (
        f"✅ <b>Замовлення #{order_id} сформовано</b>\n\n"
        f"📦 <b>Товар:</b> {item['name']}\n"
        f"💰 <b>Ціна зі знижкою:</b> {final_price} грн (-35%)\n"
        f"🎁 <b>Подарунок:</b> 3 набори рідин\n\n"
        f"👤 <b>Дані доставки:</b>\n"
        f"• {profile.get('name','—')}\n"
        f"• 📞 {profile.get('phone','—')}\n"
        f"• 📍 {profile.get('address','—')}\n\n"
        f"📌 <b>Статус:</b> очікує оплати"
    )

    await update.message.reply_text(
        user_text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("💳 Оплатити", url=PAYMENT_URL),
            ],
            [
                InlineKeyboardButton(
                    "📤 Надіслати менеджеру",
                    callback_data=f"send_manager_{order_id}"
                )
            ],
            [
                InlineKeyboardButton("🏠 В головне меню", callback_data="main")
            ]
        ])
    )

    # ===== SAVE LAST ORDER =====
    orders = context.user_data.setdefault("orders", [])
    orders.append({
        "order_id": order_id,
        "item": item["name"],
        "price": final_price,
        "status": "waiting_payment"
    })
  # ===================== CITIES & DISTRICTS =====================
CITIES = [
    "Дніпро",
    "Київ",
    "Харків",
    "Одеса",
    "Львів",
    "Запоріжжя",
    "Кривий Ріг",
    "Камʼянське",
    "Полтава",
    "Черкаси"
]

CITY_DISTRICTS = {
    "Дніпро": [
        "Центральний",
        "Соборний",
        "Індустріальний",
        "Новокодацький",
        "Самарський",
        "Амур-Нижньодніпровський",
        "Чечелівський",
        "Шевченківський",
      "Доставка по адресу"
    ],
    "Камʼянське": [
        "Заводський",
        "Дніпровський",
        "Південний",
        "Лівобережний",
        "Романкове",
        "БАМ",
        "Соцмісто",
        "Центр"
    ]
}
async def show_cities(q):
    buttons = [
        [InlineKeyboardButton(f"🏙 {c}", callback_data=f"city_{c}")]
        for c in CITIES
    ]

    buttons.append([
        InlineKeyboardButton("⬅️ Назад", callback_data="main"),
        InlineKeyboardButton("🏠 В головне меню", callback_data="main")
    ])

    await q.message.edit_text(
        "📍 <b>Оберіть місто</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
  async def send_to_manager(update: Update, context: ContextTypes.DEFAULT_TYPE, order_id: str):
    profile = context.user_data["profile"]
    orders = context.user_data.get("orders", [])
    order = next((o for o in orders if o["order_id"] == order_id), None)

    if not order:
        await update.callback_query.answer("❌ Замовлення не знайдено")
        return

    vip_date = vip_until(profile)

    text = (
        f"🆕 <b>НОВЕ ЗАМОВЛЕННЯ</b>\n\n"
        f"🆔 {order_id}\n"
        f"📦 {order['item']}\n"
        f"💰 {order['price']} грн (-35%)\n\n"
        f"👤 <b>Клієнт:</b>\n"
        f"{profile.get('name','—')}\n"
        f"@{profile.get('username','—')}\n"
        f"📞 {profile.get('phone','—')}\n\n"
        f"📍 <b>Доставка:</b>\n"
        f"{profile.get('city','—')} / {profile.get('district','—')}\n"
        f"{profile.get('address','—')}\n\n"
        f"🎁 Подарунок: 3 набори рідин\n"
        f"👑 VIP до: {vip_date.strftime('%d.%m.%Y')}\n"
        f"📌 Статус: очікує оплати"
    )

    await context.bot.send_message(
        chat_id=f"@{MANAGER_USERNAME}",
        text=text,
        parse_mode="HTML"
    )

    await update.callback_query.message.reply_text(
        "✅ <b>Замовлення надіслано менеджеру</b>\n"
        "Менеджер почав обробку 💼",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🏠 В головне меню", callback_data="main")]
        ])
    )
    async def show_cart(q, context):
    cart = context.user_data.get("cart", [])

    if not cart:
        await q.message.edit_text(
            "🛒 <b>Кошик порожній</b>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🛍 Асортимент", callback_data="assortment")]
            ])
        )
        return

    text = "🛒 <b>Ваш кошик:</b>\n\n"
    buttons = []

    total = 0
    for i, item in enumerate(cart):
        text += f"• {item['name']} — {item['price']} грн\n"
        total += item["price"]
        buttons.append([
            InlineKeyboardButton("❌ Видалити", callback_data=f"del_{i}")
        ])

    text += f"\n<b>Разом:</b> {round(total,2)} грн"

    buttons.append([
        InlineKeyboardButton("⚡ Швидке замовлення", callback_data="fast_all"),
        InlineKeyboardButton("🏠 В головне меню", callback_data="main")
    ])

    await q.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


async def delete_from_cart(q, context, idx: int):
    try:
        context.user_data["cart"].pop(idx)
        await show_cart(q, context)
    except Exception:
        await q.answer("❌ Помилка")
      def handle_referral(context, ref_id: int, user_id: int):
    if ref_id == user_id:
        return

    if "ref_used" in context.user_data:
        return

    context.user_data["ref_used"] = True
    context.user_data["profile"]["referrals"] += 1
async def show_orders(q, context):
    orders = context.user_data.get("orders", [])

    if not orders:
        await q.message.edit_text(
            "📦 <b>У вас ще немає замовлень</b>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🛍 Асортимент", callback_data="assortment")]
            ])
        )
        return

    text = "📦 <b>Мої замовлення:</b>\n\n"
    for o in orders[-5:]:
        text += (
            f"🆔 {o['order_id']}\n"
            f"📦 {o['item']}\n"
            f"💰 {o['price']} грн\n"
            f"📌 {o['status']}\n\n"
        )

    await q.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🏠 В головне меню", callback_data="main")]
        ])
    )
async def ask_payment_proof(q):
    await q.message.reply_text(
        "📸 <b>ВІДПРАВТЕ КВИТАНЦІЮ</b>\n"
        "Менеджер перевірить оплату",
        parse_mode="HTML"
    )


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    profile = context.user_data["profile"]
    photo = update.message.photo[-1]

    caption = (
        f"📸 <b>КВИТАНЦІЯ</b>\n\n"
        f"{profile.get('name')}\n"
        f"@{profile.get('username')}\n"
        f"{profile.get('city')} / {profile.get('district')}"
    )

    await context.bot.send_photo(
        chat_id=f"@{MANAGER_USERNAME}",
        photo=photo.file_id,
        caption=caption,
        parse_mode="HTML"
    )

    await update.message.reply_text(
        "✅ Квитанцію передано менеджеру",
        parse_mode="HTML"
    )
async def callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data

    if data == "main":
        await start(update, context)

    elif data == "profile":
        await show_profile(q, context)

    elif data == "assortment":
        await show_assortment(q)

    elif data == "cart":
        await show_cart(q, context)

    elif data == "orders":
        await show_orders(q, context)

    elif data == "city":
        await show_cities(q)

    elif data.startswith("city_"):
        city = data.replace("city_", "")
        context.user_data["profile"]["city"] = city
        await q.message.edit_text(
            f"🏙 <b>{city}</b>\nОберіть район",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("➡️ Обрати район", callback_data="select_district")]
            ])
        )

    elif data == "select_district":
        await show_districts(q, context)

    elif data.startswith("district_"):
        context.user_data["profile"]["district"] = data.replace("district_", "")
        await q.message.edit_text(
            "✅ Район збережено",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("👤 Профіль", callback_data="profile")]
            ])
        )

    elif data.startswith("item_"):
        await show_item(q, context, int(data.split("_")[1]))

    elif data.startswith("add_"):
        await add_to_cart(q, context, int(data.split("_")[1]))

    elif data.startswith("del_"):
        await delete_from_cart(q, context, int(data.split("_")[1]))

    elif data.startswith("fast_"):
        await fast_start(q, context, int(data.split("_")[1]))

    elif data.startswith("send_manager_"):
        await send_to_manager(update, context, data.replace("send_manager_", ""))
      def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callbacks))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    logger.info("🚀 Ghosty Shop BOT запущено без помилок")
    app.run_polling()


if __name__ == "__main__":
    main()

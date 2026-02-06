import logging
import random
import string
from html import escape
from datetime import datetime, timedelta

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
    filters
)
from telegram.error import BadRequest


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===================== CONFIG =====================
TOKEN = "8351638507:AAEqc9p9b4AA8vTrzvvj_XArtUABqcfMGV4"

MANAGER_ID = 7544847872
CHANNEL_URL = "https://t.me/GhostyStaffDP"
PAYMENT_LINK = "https://heylink.me/ghosstyshop/"
WELCOME_PHOTO = "https://i.ibb.co/y7Q194N/1770068775663.png"

DISCOUNT_PERCENT = 45
DISCOUNT_MULT = 0.55
PROMO_DISCOUNT = 45
DISCOUNT_MULTIPLIER = DISCOUNT_MULT

BASE_VIP_DATE = datetime.strptime("25.03.2026", "%d.%m.%Y")

import random
import string



# ===================== PRICE + VIEW ENGINE =====================

def calc_prices(item: dict, promo_percent: int) -> dict:
    base = item["price"]

    discounted = base
    if item.get("discount", False):
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

    text += f"{item['desc']}\n\n"

    if item.get("gift_liquid"):
        gifts = "\n".join(f"• {g}" for g in get_gift_liquids())
        text += (
            "🎁 <b>Рідина у подарунок на вибір:</b>\n"
            f"{gifts}\n\n"
        )

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
        except Exception:
            logger.warning("safe_edit_media failed")

# ===================== CITIES & DISTRICTS =====================
CITIES = [
    "Київ",
    "Дніпро",
    "Камʼянське",
    "Харків",
    "Одеса",
    "Львів",
    "Запоріжжя",
    "Кривий Ріг",
    "Полтава",
    "Черкаси"
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


def calc_price(item: dict) -> int:
    """
    Рахує фінальну ціну з урахуванням знижки.
    За замовчуванням знижка є завжди.
    Вимикається якщо discount=False у товарі.
    """
    base_price = item["price"]

    if item.get("discount", True):
        return int(base_price * DISCOUNT_MULTIPLIER)

    return base_price
    
    context.user_data["cart"].append({
    "pid": pid,
    "name": item["name"],
    "price": calc_price(item),
    "base_price": item["price"]
})
    
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


# 💧 РІДИНИ (3 набори, продаються + йдуть у подарунок)
LIQUIDS = {
    301: {
        "name": "🎃 Pumpkin Latte",
        "series": "Chaser HO HO HO Edition",
        "price": 269,
        "discount": False,
        "img": "https://ibb.co/Y7qn69Ds",
        "desc": (
            "☕ Гарбузовий латте з корицею\n"
            "🎄 Зимовий настрій\n"
            "😌 Мʼякий та теплий смак"
        ),
        "effect": "Затишок, солодкий aftertaste ☕",
        "payment_url": "https://heylink.me/ghosstyshop/"
    },

    302: {
        "name": "🍷 Glintwine",
        "series": "Chaser HO HO HO Edition",
        "price": 269,
        "discount": False,
        "img": "https://ibb.co/wF8r7Nmc",
        "desc": (
            "🍇 Пряний глінтвейн\n"
            "🔥 Теплий винний смак\n"
            "🎄 Святковий вайб"
        ),
        "effect": "Тепло, релакс 🔥",
        "payment_url": "https://heylink.me/ghosstyshop/"
    },

    303: {
        "name": "🎄 Christmas Tree",
        "series": "Chaser HO HO HO Edition",
        "price": 269,
        "discount": False,
        "img": "https://ibb.co/vCPGV8RV",
        "desc": (
            "🌲 Хвоя + морозна свіжість\n"
            "❄️ Дуже свіжа\n"
            "🎅 Атмосфера зими"
        ),
        "effect": "Свіжість, холодок ❄️",
        "payment_url": "https://heylink.me/ghosstyshop/"
    }
}

async def show_liquids(q, context: ContextTypes.DEFAULT_TYPE):
    buttons = []

    for pid, item in LIQUIDS.items():
        buttons.append(
            [InlineKeyboardButton(item["name"], callback_data=f"item_{pid}")]
        )

    buttons.append(
        [InlineKeyboardButton("⬅ Назад", callback_data="assortment")]
    )

    await q.message.edit_text(
        "💧 <b>Рідини</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# ===================== HHC / NNS =====================
HHC_VAPES = {

    100: {
        "name": "🌴 Packwoods Purple 1ml",
        "type": "hhc",
        "gift_liquid": True,
        "price": 549,
        "discount": True,
        "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg",
        "desc": (
            "🧠 90% ННС | Гібрид\n"
            "😌 Розслаблення + легка ейфорія\n"
            "🎨 Мʼякий виноградний профіль\n"
            "🎁 Рідина у подарунок на вибір\n"
            "⚠️ Потужний ефект — починай з малого"
        ),
        "payment_url": PAYMENT_LINK
    },

    101: {
        "name": "🍊 Packwoods Orange 1ml",
        "type": "hhc",
        "gift_liquid": True,
        "price": 629,
        "discount": True,
        "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg",
        "desc": (
            "🧠 90% ННС | Гібрид\n"
            "⚡ Бадьорить та фокусує\n"
            "🍊 Соковитий апельсин\n"
            "🎁 Рідина у подарунок на вибір\n"
            "🔥 Яскравий та швидкий ефект"
        ),
        "payment_url": PAYMENT_LINK
    },

    102: {
        "name": "🌸 Packwoods Pink 1ml",
        "type": "hhc",
        "gift_liquid": True,
        "price": 719,
        "discount": True,
        "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg",
        "desc": (
            "🧠 90% ННС | Гібрид\n"
            "😇 Спокій + підйом настрою\n"
            "🍓 Солодко-фруктовий мікс\n"
            "🎁 Рідина у подарунок на вибір\n"
            "✨ Комфортний та плавний"
        ),
        "payment_url": PAYMENT_LINK
    },

    103: {
        "name": "🌿 Whole Mint 2ml",
        "type": "hhc",
        "gift_liquid": True,
        "price": 849,
        "discount": True,
        "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg",
        "desc": (
            "🧠 95% ННС | Сатіва\n"
            "⚡ Енергія та ясність\n"
            "❄️ Свіжа мʼята\n"
            "🎁 Рідина у подарунок на вибір\n"
            "🚀 Ідеально вдень"
        ),
        "payment_url": PAYMENT_LINK
    },

    104: {
        "name": "🌴 Jungle Boys White 2ml",
        "type": "hhc",
        "gift_liquid": True,
        "price": 999,
        "discount": True,  # ❗ ЗНИЖКА УВІМКНЕНА
        "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg",
        "desc": (
            "🧠 95% ННС | Індика\n"
            "😴 Глибокий релакс\n"
            "🌲 Насичений терпкий смак\n"
            "🎁 Рідина у подарунок на вибір\n"
            "🌙 Ідеально для вечора та сну"
        ),
        "payment_url": PAYMENT_LINK
    }

}

async def show_hhc(q, context: ContextTypes.DEFAULT_TYPE):
    buttons = []

    for pid, item in HHC_VAPES.items():
        buttons.append(
            [InlineKeyboardButton(item["name"], callback_data=f"item_{pid}")]
        )

    buttons.append(
        [InlineKeyboardButton("⬅ Назад", callback_data="assortment")]
    )

    await q.message.edit_text(
        "💨 <b>NNS / HHC Вейпи</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# ===================== POD SYSTEMS =====================
PODS = {

    500: {
        "name": "🔌 Vaporesso XROS 3 Mini",
        "type": "pod",
        "gift_liquid": False,
        "price": 499,
        "discount": True,
        "imgs": [
            "https://ibb.co/yFSQ5QSn",
            "https://ibb.co/LzgrzZjC",
            "https://ibb.co/Q3ZNTBvg"
        ],
        "colors": ["⚫ Чорний", "🔵 Голубий", "🌸 Рожевий"],
        "desc": (
            "🔋 1000 mAh\n"
            "💨 MTL / RDL\n"
            "⚡ Type-C зарядка\n"
            "✨ Компактний та легкий\n"
            "😌 Мʼяка тяга, стабільний смак"
        ),
        "payment_url": PAYMENT_LINK
    },

    501: {
        "name": "🔌 Vaporesso XROS 5 Mini",
        "type": "pod",
        "gift_liquid": False,
        "price": 579,
        "discount": True,
        "imgs": [
            "https://ibb.co/RkNgt1Qr",
            "https://ibb.co/KxvJC1bV",
            "https://ibb.co/WpMYBCH1"
        ],
        "colors": ["🌸 Рожевий", "🟣 Фіолетовий", "⚫ Чорний"],
        "desc": (
            "🔋 1000 mAh\n"
            "🔥 COREX 2.0\n"
            "⚡ Швидка зарядка\n"
            "🎯 Яскравий смак\n"
            "💎 Оновлений дизайн"
        ),
        "payment_url": PAYMENT_LINK
    },

    502: {
        "name": "🔌 Vaporesso XROS Pro",
        "type": "pod",
        "gift_liquid": False,
        "price": 689,
        "discount": True,
        "imgs": [
            "https://ibb.co/ynYwSMt6",
            "https://ibb.co/3mV7scXr",
            "https://ibb.co/xSJCgpJ5"
        ],
        "colors": ["⚫ Чорний", "🔴 Темно-червоний", "🌸 Рожево-червоний"],
        "desc": (
            "🔋 1200 mAh\n"
            "⚡ Регулювання потужності\n"
            "💨 RDL / MTL\n"
            "🔥 Максимальний смак\n"
            "🚀 Професійний рівень"
        ),
        "payment_url": PAYMENT_LINK
    },

    503: {
        "name": "🔌 Vaporesso XROS Nano",
        "type": "pod",
        "gift_liquid": False,
        "price": 519,
        "discount": True,
        "imgs": [
            "https://ibb.co/5XW2yN80",
            "https://ibb.co/93dJ8wKS",
            "https://ibb.co/Qj90hyyz"
        ],
        "colors": ["🪖 Камуфляж 1", "🪖 Камуфляж 2", "🪖 Камуфляж 3"],
        "desc": (
            "🔋 1000 mAh\n"
            "💨 MTL\n"
            "🧱 Міцний корпус\n"
            "🎒 Ідеальний у дорогу\n"
            "😌 Спокійна, рівна тяга"
        ),
        "payment_url": PAYMENT_LINK
    },

    504: {
        "name": "🔌 Vaporesso XROS 4",
        "type": "pod",
        "gift_liquid": False,
        "price": 599,
        "discount": True,
        "imgs": [
            "https://ibb.co/LDRbQxr1",
            "https://ibb.co/NPHYSjN",
            "https://ibb.co/LhbzXD57"
        ],
        "colors": ["🌸 Рожевий", "⚫ Чорний", "🔵 Синій"],
        "desc": (
            "🔋 1000 mAh\n"
            "🔥 COREX\n"
            "🎨 Стильний дизайн\n"
            "👌 Баланс смаку та тяги\n"
            "✨ Щоденний комфорт"
        ),
        "payment_url": PAYMENT_LINK
    },

    505: {
        "name": "🔌 Vaporesso XROS 5",
        "type": "pod",
        "gift_liquid": False,
        "price": 799,
        "discount": True,
        "imgs": [
            "https://ibb.co/hxjmpHF2",
            "https://ibb.co/DDkgjtV4",
            "https://ibb.co/r2C9JTzz"
        ],
        "colors": ["⚫ Чорний", "🌸 Рожевий", "🟣 Фіолетовий з полоскою"],
        "desc": (
            "🔋 1200 mAh\n"
            "⚡ Fast Charge\n"
            "💎 Преміальна збірка\n"
            "🔥 Максимум смаку\n"
            "🚀 Флагман серії"
        ),
        "payment_url": PAYMENT_LINK
    },

    506: {
        "name": "🔌 Voopoo Vmate Mini Pod Kit",
        "type": "pod",
        "gift_liquid": False,
        "price": 459,
        "discount": True,
        "imgs": [
            "https://ibb.co/8L0JNTHz",
            "https://ibb.co/0RZ1VDnG",
            "https://ibb.co/21LPrbbj"
        ],
        "colors": ["🌸 Рожевий", "🔴 Червоний", "⚫ Чорний"],
        "desc": (
            "🔋 1000 mAh\n"
            "💨 Автозатяжка\n"
            "🧲 Магнітний картридж\n"
            "🎯 Простий та надійний\n"
            "😌 Легкий старт для новачків"
        ),
        "payment_url": PAYMENT_LINK
    }

}

async def show_pods(q, context: ContextTypes.DEFAULT_TYPE):
    buttons = []

    for pid, item in PODS.items():
        buttons.append(
            [InlineKeyboardButton(item["name"], callback_data=f"item_{pid}")]
        )

    buttons.append(
        [InlineKeyboardButton("⬅ Назад", callback_data="assortment")]
    )

    await q.message.edit_text(
        "🔌 <b>POD-системи</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(buttons)
)
# ===================== UNIVERSAL ITEM VIEW =====================

async def show_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # callback_data: item:<group>:<id>
    try:
        _, group, pid = query.data.split(":")
        pid = int(pid)
    except ValueError:
        await query.message.reply_text("❌ Невірний формат товару")
        return

    catalog_map = {
        "liquid": LIQUIDS,
        "hhc": HHC_VAPES,
        "pod": PODS
    }

    catalog = catalog_map.get(group)
    if not catalog or pid not in catalog:
        await query.message.reply_text("❌ Товар не знайдено")
        return

    item = catalog[pid]

    caption = build_item_caption(item, context.user_data)

    imgs = item.get("imgs") or [item.get("img")]
    photo = imgs[0]

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🛒 Купити", url=item["payment_url"])],
        [InlineKeyboardButton("⬅ Назад", callback_data=f"back:{group}")]
    ])

    try:
        await query.message.edit_photo(
            photo=photo,
            caption=caption,
            parse_mode="HTML",
            reply_markup=keyboard
        )
    except BadRequest:
        await query.message.delete()
        await query.message.chat.send_photo(
            photo=photo,
            caption=caption,
            parse_mode="HTML",
            reply_markup=keyboard
        ) 
        
# ===================== CALLBACKS ROUTER =====================
async def callbacks_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    if not q:
        return

    await q.answer()
    data = q.data

    if data == "main":
        await start(update, context)

    elif data == "profile":
        await show_profile(q, context)

    elif data == "assortment":
        await show_assortment(q, context)
        
elif data == "liquids":
    await show_liquids(q, context)

elif data == "pods":
    await show_pods(q, context)

elif data == "hhc":
    await show_hhc(q, context)

    elif data == "cart":
        await show_cart(q, context)

    elif data == "orders":
        await show_orders(q, context)

    elif data == "city":
        await select_city(q, context)

    elif data.startswith("city_"):
        await save_city(q, context, data.replace("city_", ""))

    elif data.startswith("district_"):
        await save_district(q, context, data.replace("district_", ""))

    elif data.startswith("item_"):
        await show_item(q, context, int(data.split("_")[1]))

    elif data.startswith("color_"):
        await select_color(q, context, int(data.split("_")[1]))

    elif data.startswith("colorpick_"):
        _, pid, idx = data.split("_")
        await apply_color(q, context, int(pid), int(idx))

    elif data.startswith("add_"):
        await add_to_cart(q, context, int(data.split("_")[1]))

    elif data.startswith("del_"):
        await delete_from_cart(q, context, int(data.split("_")[1]))

    elif data.startswith("fast_"):
        pid = int(data.split("_")[1])
        await fast_start(q, context, pid)

    elif data.startswith("send_manager_"):
        order_id = data.replace("send_manager_", "")
        await send_to_manager(update, context, order_id)

    else:
        await q.answer("⚠️ Невідома дія", show_alert=True)
        
        elif data.startswith("item_"):
    await show_item(q, context, int(data.split("_")[1]))

# ===================== KEYBOARDS =====================
def main_menu():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("👤 Профіль", callback_data="profile"),
            InlineKeyboardButton("🛍 Асортимент", callback_data="assortment")
        ],
        [
            InlineKeyboardButton("📍 Місто", callback_data="city"),
            InlineKeyboardButton("🛒 Кошик", callback_data="cart")
        ],
        [
            InlineKeyboardButton("📦 Замовлення", callback_data="orders"),
            InlineKeyboardButton("👨‍💻 Менеджер", url="https://t.me/ghosstydpbot")
        ],
        [
            InlineKeyboardButton("📢 Канал", url=CHANNEL_URL)
        ]
    ])


def back_kb(back: str):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⬅️ Назад", callback_data=back),
            InlineKeyboardButton("🏠 В головне меню", callback_data="main")
        ]
    ])
# ===================== START ===================== 
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.setdefault("promo_percent", PROMO_DISCOUNT)
context.user_data.setdefault("vip", False)
    user = update.effective_user

    # Перевіряємо та ініціалізуємо профіль (виправлено назву context)
    if "profile" not in context.user_data:
        context.user_data["profile"] = {
            "uid": user.id,
            "full_name": user.first_name,
            "username": user.username,
            "phone": None,
            "address": None,
            "promo_code": generate_promo_code(user.id),
            "promo_discount": PROMO_DISCOUNT,
            "referrals": 0,
            "vip_base": BASE_VIP_DATE,
            "ref_applied": False
        }
        context.user_data["cart"] = []
        context.user_data["orders"] = []

    profile = context.user_data["profile"]
    vip_date = vip_until(profile)

    text = (
        f"👋 <b>{escape(user.first_name)}</b>, вітаємо у <b>Ghosty Shop</b> 💨\n\n"
        f"🎁 Подарунок до кожного замовлення — 3 рідини 30ml\n"
        f"🎫 Промокод: <code>{profile['promo_code']}</code> (-{profile.get('promo_discount', 45)}%)\n"
        f"👑 VIP до: <b>{vip_date.strftime('%d.%m.%Y')}</b>\n\n"
        f"👇 Оберіть дію:"
    )

    await update.message.reply_photo(
        photo=WELCOME_PHOTO,
        caption=text,
        parse_mode="HTML",
        reply_markup=main_menu()
    )


    # Розрахунок дати VIP (використовуємо твою функцію vip_until)
    vip_date = vip_until(profile)

    # ===== ДИЗАЙН ПОВІДОМЛЕННЯ (Збережено) =====
    text = (
        f"👋 <b>{escape(user.first_name)}</b>, вітаємо у <b>Ghosty Shop</b> 💨\n\n"
        f"🎁 Подарунок до кожного замовлення — 3 рідини 30ml\n"
        f"🎫 Промокод: <code>{profile['promo_code']}</code> (-{profile['promo_discount']}%)\n"
        f"👑 VIP до: <b>{vip_date.strftime('%d.%m.%Y')}</b>\n\n"
        f"👇 Оберіть дію:"
    )

    # ===== ВІДПРАВКА (Виправлено) =====
    try:
        await update.message.reply_photo(
            photo=WELCOME_PHOTO,
            caption=text,
            parse_mode="HTML",
            reply_markup=main_menu()
        )
    except Exception as e:
        # Якщо фото не завантажиться, відправимо просто текст, щоб бот не стопився
        await update.message.reply_text(
            text,
            parse_mode="HTML",
            reply_markup=main_menu()
        )

    # ===== INIT USER DATA =====
    if "profile" not in context.user_data:
        context.user_data["profile"] = {
            "uid": user.id,
            "name": user.first_name,
            "username": user.username,
            "phone": None,
            "city": None,
            "district": None,
            "address": None,
            "promo_code": generate_promo_code(user.id),
            "promo_discount": PROMO_DISCOUNT,
            "referrals": 0,
            "vip_base": BASE_VIP_DATE,
            "ref_applied": False
        }
        context.user_data["cart"] = []
        context.user_data["orders"] = []

    profile = context.user_data["profile"]

    # ===== REFERRAL SYSTEM =====
    if args:
        try:
            ref_id = int(args[0])
            if ref_id != user.id and not profile["ref_applied"]:
                profile["ref_applied"] = True
                profile["referrer"] = ref_id
        except ValueError:
            pass

    # ===== VIP DATE =====
    vip_date = vip_until(profile)

    # ===== WELCOME TEXT =====
    welcome_text = (
        f"👋 <b>{escape(user.first_name)}</b>, вітаємо у <b>Ghosty Shop</b> 💨\n\n"
        f"🎁 <b>Подарунок до кожного замовлення:</b>\n"
        f"• 3 рідини 30ml — <b>безкоштовно</b> 🎉\n\n"
        f"🎫 <b>Промокод:</b> <code>{profile['promo_code']}</code> (-{profile['promo_discount']}%)\n"
        f"👑 <b>VIP статус</b> до: <b>{vip_date.strftime('%d.%m.%Y')}</b>\n"
        f"🚚 Доставка: <b>Безкоштовна</b>\n\n"
        f"👇 Оберіть дію:"
    )

    # ===== SEND MESSAGE =====
    if update.message:
        await update.message.reply_photo(
            photo=WELCOME_PHOTO,
            caption=welcome_text,
            parse_mode="HTML",
            reply_markup=main_menu()
        )
    else:
        await update.callback_query.message.edit_caption(
            caption=welcome_text,
            parse_mode="HTML",
            reply_markup=main_menu()
                )
        
# ===================== PROFILE =====================
async def show_profile(q, context):
    profile = context.user_data.setdefault("profile", {})

    promo = profile.get("promo_code", "—")
    discount = profile.get("promo_discount", PROMO_DISCOUNT)

    city = profile.get("city", "—")
    district = profile.get("district", "—")
    address = profile.get("address", "—")

    vip_date = vip_until(profile).strftime("%d.%m.%Y")

    text = (
        f"👤 <b>Профіль користувача</b>\n\n"
        f"🧑 <b>Імʼя:</b> {escape(profile.get('name','—'))}\n"
        f"👤 <b>Username:</b> @{profile.get('username','—')}\n\n"
        f"🏙 <b>Місто:</b> {city}\n"
        f"📍 <b>Район:</b> {district}\n"
        f"🏠 <b>Адреса:</b> {address}\n\n"
        f"🏷 <b>Промокод:</b> <code>{promo}</code>\n"
        f"💸 <b>Знижка:</b> -{discount}%\n\n"
        f"💎 <b>VIP:</b> до <b>{vip_date}</b>\n"
        f"🚚 <b>Доставка:</b> безкоштовна\n"
    )

    await q.edit_message_text(
        text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✏️ Змінити адресу", callback_data="edit_address"),
                InlineKeyboardButton("📍 Місто / район", callback_data="city")
            ],
            [
                InlineKeyboardButton("⬅️ Назад", callback_data="main")
            ]
        ])
    )

# ===================== REF LINK =====================
async def show_ref_link(q, context):
    await q.answer()

    profile = context.user_data["profile"]
    link = f"https://t.me/{context.bot.username}?start={profile['uid']}"

    await q.edit_message_text(
        f"🔗 <b>Ваш реферальний лінк</b>\n\n"
        f"<code>{link}</code>\n\n"
        f"➕ <b>+7 днів VIP</b> за кожного друга",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Назад", callback_data="profile")]
        ])
    )

# ===================== CITY SELECT =====================
    
async def select_city(q, context):
    await q.answer()

    buttons = [
        [InlineKeyboardButton(f"🏙 {c}", callback_data=f"city_{c}")]
        for c in CITIES
    ]
    buttons.append([
        InlineKeyboardButton("⬅️ Назад", callback_data="profile"),
        InlineKeyboardButton("🏠 В головне меню", callback_data="main")
    ])

    await q.edit_message_text(
        "🏙 <b>Оберіть місто</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# ===================== SAVE CITY =====================
    
async def save_city(q, context, city):
    await q.answer()

    profile = context.user_data.setdefault("profile", {})
    profile["city"] = city
    profile["district"] = None

    buttons = [
        [InlineKeyboardButton(f"📍 {d}", callback_data=f"district_{d}")]
        for d in CITY_DISTRICTS.get(city, [])
    ]
    buttons.append([
        InlineKeyboardButton("⬅️ Назад", callback_data="city"),
        InlineKeyboardButton("🏠 В головне меню", callback_data="main")
    ])

    await q.edit_message_text(
        f"🏙 <b>{city}</b>\n\nОберіть район:",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# ===================== SAVE DISTRICT =====================
    
async def save_district(q, context, district):
    await q.answer()

    profile = context.user_data["profile"]
    profile["district"] = district

    await q.edit_message_text(
        f"✅ <b>Район збережено:</b> {district}",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("👤 Профіль", callback_data="profile"),
                InlineKeyboardButton("🏠 В головне меню", callback_data="main")
            ]
        ])
    )
 
# ===================== CALLBACKS ROUTER =====================
async def callbacks_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data

    if data == "main":
        await q.message.edit_text(
            "🏠 <b>Головне меню</b>",
            parse_mode="HTML",
            reply_markup=main_menu()
        )

    elif data == "profile":
        await q.message.edit_text("👤 Профіль", reply_markup=back_kb("main"))

    elif data == "assortment":
        await q.message.edit_text("🛍 Асортимент", reply_markup=back_kb("main"))

    else:
        await q.answer("⚠️ Невідома дія", show_alert=True)
        

# ===================== SEND TO MANAGER =====================
async def send_to_manager(update: Update, context: ContextTypes.DEFAULT_TYPE, order_id: str):
    query = update.callback_query
    user = update.effective_user

    profile = context.user_data.get("profile", {})
    orders = context.user_data.get("orders", [])

    order = next((o for o in orders if o["id"] == order_id), None)
    if not order:
        await query.answer("❌ Замовлення не знайдено", show_alert=True)
        return
 
    text
# ===================== ADDRESS EDIT =====================  
async def edit_address(q, context):
    await q.answer()

    context.user_data["state"] = "address"

    await q.edit_message_text(
        "📦 <b>Введіть адресу доставки</b>\n"
        "Можна вставити Google Maps або текст:",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("⬅️ Скасувати", callback_data="cancel_input")
            ]
        ])
    )
     
# ===================== CANCEL INPUT ===================== 
    
async def cancel_input(q, context):
    await q.answer()
    context.user_data["state"] = None

    await q.edit_message_text(
        "❌ Ввід скасовано",
        parse_mode="HTML",
        reply_markup=main_menu()
    )


        # ===== ADDRESS =====
    if state == "address":
        profile["address"] = text
        context.user_data["state"] = None

        await update.message.reply_text(
            "✅ <b>Адресу доставки збережено</b>",
            parse_mode="HTML"
        )
        return



    # ===== NAME =====
    if state == "name":
        profile["name"] = text
        context.user_data["state"] = None

        await update.message.reply_text(
            f"✅ Імʼя збережено: <b>{text}</b>",
            parse_mode="HTML",
            reply_markup=main_menu()
        )
        return

    # ===== PHONE =====
    if state == "phone":
        if not text.startswith("+380") or len(text) != 13:
            await update.message.reply_text(
                "❌ Введіть номер у форматі <b>+380XXXXXXXXX</b>",
                parse_mode="HTML"
            )
            return

        profile["phone"] = text
        context.user_data["state"] = None

        await update.message.reply_text(
            f"📞 Телефон збережено: <b>{text}</b>",
            parse_mode="HTML",
            reply_markup=main_menu()
        )
        return

    # ===== DEFAULT =====
    await update.message.reply_text(
        "ℹ️ Скористайтесь кнопками меню 👇",
        reply_markup=main_menu()
    )


    # ===================== TEXT HANDLER ===================== 
async def fast_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    text = update.message.text.strip()
    state = context.user_data.get("state")

    profile = context.user_data.setdefault("profile", {})

    # ===== ADDRESS =====
    if state == "address":
        profile["address"] = text
        context.user_data["state"] = None

        await update.message.reply_text(
            "✅ <b>Адресу доставки збережено</b>\n\n"
            "Ви можете змінити її у профілі або використати при замовленні.",
            parse_mode="HTML",
            reply_markup=main_menu()
        )
        return

    # ===== NAME =====
    if state == "name":
        profile["name"] = text
        context.user_data["state"] = None

        await update.message.reply_text(
            f"✅ Імʼя збережено: <b>{text}</b>",
            parse_mode="HTML",
            reply_markup=main_menu()
        )
        return

    # ===== PHONE =====
    if state == "phone":
        if not text.startswith("+380") or len(text) != 13:
            await update.message.reply_text(
                "❌ Введіть номер у форматі <b>+380XXXXXXXXX</b>",
                parse_mode="HTML"
            )
            return

        profile["phone"] = text
        context.user_data["state"] = None

        await update.message.reply_text(
            f"📞 Телефон збережено: <b>{text}</b>",
            parse_mode="HTML",
            reply_markup=main_menu()
        )
        return

    # ===== FAST ORDER COMMENT =====
    if state == "fast_comment":
        context.user_data["fast_comment"] = text
        context.user_data["state"] = None

        await update.message.reply_text(
            "📝 <b>Коментар до замовлення збережено</b>\n\n"
            "Натисніть кнопку нижче, щоб надіслати замовлення менеджеру.",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Надіслати менеджеру", callback_data="send_manager_fast")],
                [InlineKeyboardButton("🏠 В головне меню", callback_data="main")]
            ])
        )
        return

    # ===== DEFAULT =====
    await update.message.reply_text(
        "ℹ️ Я не зрозумів повідомлення.\n"
        "Будь ласка, скористайтесь меню 👇",
        reply_markup=main_menu()
    )
      # ===================== ASSORTMENT =====================
async def show_assortment(q, context):
    kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💧 Рідини", callback_data="liquids"),
InlineKeyboardButton("🔌 POD-системи", callback_data="pods"),
InlineKeyboardButton("💨 HHC / NNS", callback_data="hhc"),
InlineKeyboardButton("⚡ Швидке замовлення", callback_data="fast_all")
        ],
        [
            InlineKeyboardButton("🏠 В головне меню", callback_data="main")
        ]
    ])

    text = "🛍 <b>Асортимент</b>\n\nОберіть категорію:"

    try:
        await q.message.edit_caption(
            caption=text,
            parse_mode="HTML",
            reply_markup=kb
        )
    except:
        await q.message.edit_text(
            text,
            parse_mode="HTML",
            reply_markup=kb
    )
# ===================== CATEGORY LIST ===================== 
async def show_category(q, items: dict, title: str, back: str):
    buttons = []

    for pid, item in items.items():
        buttons.append([
            InlineKeyboardButton(item["name"], callback_data=f"item_{pid}"),
            InlineKeyboardButton("⚡", callback_data=f"fast_{pid}")
        ])

    buttons.append([
        InlineKeyboardButton("⬅️ Назад", callback_data=back),
        InlineKeyboardButton("🏠 В головне меню", callback_data="main")
    ])

    try:
        await q.message.edit_caption(
            caption=title,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except:
        await q.message.edit_text(
            title,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(buttons)
        )


# ===================== ITEM VIEW ===================== 
async def show_item(q, context, pid: int):
    item = (
        HHC_VAPES.get(pid)
        or LIQUIDS.get(pid)
        or PODS.get(pid)
    )

    if not item:
        await q.answer("❌ Товар не знайдено")
        return

    base_price = item["price"]
    final_price = round(base_price * DISCOUNT_MULT, 2)

    discount_percent = int((1 - DISCOUNT_MULT) * 100)

    caption = (
        f"<b>{item['name']}</b>\n\n"
        f"{item.get('desc','')}\n\n"
        f"❌ {base_price} грн\n"
        f"✅ <b>{final_price} грн (-{discount_percent}%)</b>\n\n"
        f"🎁 <b>Подарунок:</b> 3 рідини 30ml\n"
        f"🚚 VIP доставка: 0 грн"
    )

    # ===== PHOTO =====
    color_idx = context.user_data.get("selected_color", 0)

    if "imgs" in item and item["imgs"]:
        photo = item["imgs"][color_idx]
    else:
        photo = item.get("img")

    kb_buttons = []

    if "imgs" in item and len(item["imgs"]) > 1:
        kb_buttons.append([
            InlineKeyboardButton("🎨 Обрати колір", callback_data=f"color_{pid}")
        ])

    kb_buttons.append([
        InlineKeyboardButton("⚡ Швидке замовлення", callback_data=f"fast_{pid}"),
        InlineKeyboardButton("🛒 В кошик", callback_data=f"add_{pid}")
    ])

    kb_buttons.append([
        InlineKeyboardButton("👨‍💻 Менеджер", url=f"https://t.me/{MANAGER_USERNAME}")
    ])

    kb_buttons.append([
        InlineKeyboardButton("⬅️ Назад", callback_data="assortment"),
        InlineKeyboardButton("🏠 В головне меню", callback_data="main")
    ])


    
# ===================== COLOR SELECT =====================
async def select_color(q, context, pid: int):
    item = (
        PODS.get(pid)
        or HHC_VAPES.get(pid)
    )

    if not item or "imgs" not in item or len(item["imgs"]) < 2:
        await q.answer("❌ Немає варіантів кольору")
        return

    buttons = [
        [
            InlineKeyboardButton(
                f"🎨 {item.get('colors',[f'Колір {i+1}'])[i]}",
                callback_data=f"colorpick_{pid}_{i}"
            )
        ]
        for i in range(len(item["imgs"]))
    ]

    buttons.append([
        InlineKeyboardButton("⬅️ Назад", callback_data=f"item_{pid}"),
        InlineKeyboardButton("🏠 В головне меню", callback_data="main")
    ])

    await q.message.edit_text(
        f"🎨 <b>{item['name']}</b>\nОберіть колір:",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    
# ===================== CART =====================
    
    
async def add_to_cart(q, context, pid: int):
    item = HHC_VAPES.get(pid) or PODS.get(pid) or LIQUIDS.get(pid)

    if not item:
        await q.answer("❌ Товар не знайдено")
        return

    cart = context.user_data.setdefault("cart", [])

    cart.append({
        "pid": pid,
        "name": item["name"],
        "price": calc_price(item),
        "base_price": item["price"],
        "gift_liquid": item.get("gift_liquid", False)
    })

    await q.answer("✅ Додано в кошик")

# ===================== FAST ORDER =====================
async def fast_start(q, context, pid=None):
    cart = context.user_data.setdefault("cart", [])

    if pid:
        await add_to_cart(q, context, pid)

    if not context.user_data.get("cart"):
        await q.answer("❌ Кошик порожній")
        return

    context.user_data["state"] = "fast_name"

    await q.message.reply_text(
        "⚡ <b>Швидке замовлення</b>\n\n"
        "✍️ Введіть <b>Імʼя та Прізвище</b>:",
        parse_mode="HTML"
    )
    

# ===================== FAST ORDER FLOW =====================
async def fast_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    state = context.user_data.get("state")
    if not state:
        return  # ❗ не ловимо зайві повідомлення

    text = update.message.text.strip()
    profile = context.user_data.setdefault("profile", {})

    if state == "fast_name":
        profile["full_name"] = text
        context.user_data["state"] = "fast_phone"
        await update.message.reply_text("📞 <b>Введіть номер телефону:</b>", parse_mode="HTML")
        return

    if state == "fast_phone":
        profile["phone"] = text
        context.user_data["state"] = "fast_address"
        await update.message.reply_text(
            "📍 <b>Введіть адресу доставки</b>\n(текст або Google Maps):",
            parse_mode="HTML"
        )
        return

    if state == "fast_address":
        profile["address"] = text
        context.user_data["state"] = None
        await confirm_order(update, context)
        return

    

# ===================== CONFIRM ORDER =====================
async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cart = context.user_data.get("cart", [])
    profile = context.user_data.get("profile", {})

    if not cart:
        await update.message.reply_text("❌ Кошик порожній")
        return

    orders = context.user_data.setdefault("orders", [])
    order_id = f"GHST-{update.effective_user.id}-{len(orders)+1}"
    total = sum(i.get("price", 0) for i in cart)

    text = (
        f"📦 <b>Замовлення сформовано</b>\n\n"
        f"🆔 <b>{order_id}</b>\n\n"
        f"👤 {profile.get('full_name','—')}\n"
        f"📞 {profile.get('phone','—')}\n"
        f"📍 {profile.get('address','—')}\n\n"
        f"🛒 <b>Товари:</b>\n"
    )

    for i in cart:
        text += f"• {i['name']} — {i['price']} грн\n"

    text += (
        f"\n🎁 <b>Подарунок:</b> 3 рідини 30ml\n"
        f"💰 <b>До оплати:</b> {total} грн\n\n"
        f"💳 Оплата за посиланням ⬇️"
    )

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 Оплатити", url=PAYMENT_LINK)],
        [InlineKeyboardButton("📤 Надіслати менеджеру", callback_data=f"send_manager_{order_id}")],
        [InlineKeyboardButton("🏠 В головне меню", callback_data="main")]
    ])

    await update.message.reply_text(text, parse_mode="HTML", reply_markup=kb)

    orders.append({
        "id": order_id,
        "items": cart.copy(),
        "total": total,
        "status": "Очікує оплату"
    })
    context.user_data["cart"] = []



# ===================== HANDLE PAYMENT RECEIPT =====================
async def handle_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    orders = context.user_data.get("orders", [])
    active_order_id = context.user_data.get("active_order_id")

    if not active_order_id:
        await update.message.reply_text(
            "ℹ️ Немає активного замовлення.\n"
            "Будь ласка, оформіть замовлення через кошик.",
            reply_markup=main_menu()
        )
        return

    order = next((o for o in orders if o["id"] == active_order_id), None)
    if not order:
        await update.message.reply_text("❌ Замовлення не знайдено")
        return

    # беремо фото
    photo = update.message.photo[-1].file_id

    caption = (
        f"💳 <b>Квитанція про оплату</b>\n\n"
        f"🆔 {order['id']}\n"
        f"👤 {user.first_name} (@{user.username or '—'})\n"
        f"💰 {order['total']} грн\n"
        f"📦 Статус: Оплачено (очікує підтвердження)"
    )

    # надсилаємо менеджеру
    await context.bot.send_photo(
        chat_id=MANAGER_ID,
        photo=photo,
        caption=caption,
        parse_mode="HTML"
    )

    # оновлюємо статус
    order["status"] = "Оплачено (на перевірці)"

    await update.message.reply_text(
        "✅ <b>Квитанцію надіслано менеджеру</b>\n\n"
        "Очікуйте підтвердження 💨",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🏠 В головне меню", callback_data="main")]
        ])
    )



# ===================== ORDERS HISTORY =====================
async def show_orders(q, context):
    orders = context.user_data.get("orders", [])

    if not orders:
        await q.message.edit_text(
            "📭 <b>Замовлень ще немає</b>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 В головне меню", callback_data="main")]
            ])
        )
        return

    text = "📦 <b>Мої замовлення:</b>\n\n"
    buttons = []

    for o in orders:
        text += (
            f"🆔 <b>{o['id']}</b>\n"
            f"📦 {o['status']}\n"
            f"💰 {o['total']} грн\n\n"
        )
        buttons.append([
            InlineKeyboardButton(
                f"📄 {o['id']}",
                callback_data=f"order_{o['id']}"
            )
        ])

    buttons.append([
        InlineKeyboardButton("🏠 В головне меню", callback_data="main")
    ])

    await q.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# ===================== BOT START =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот запущено ✅")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

if __name__ == "__main__":
    main()

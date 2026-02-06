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
    PicklePersistence,
    filters
)
from telegram.error import BadRequest

# ===================== CONFIG =====================
TOKEN = "8351638507:AAG2HP0OmYx7ip8-uZcLQCilPTfoBhtEGq0"

MANAGER_ID = "7544847872"
CHANNEL_URL = "https://t.me/GhostyStaffDP"
PAYMENT_LINK = "https://heylink.me/ghosstyshop/"
WELCOME_PHOTO = "https://i.ibb.co/y7Q194N/1770068775663.png"

DISCOUNT_PERCENT = 45
DISCOUNT_MULT = 0.55
BASE_VIP_DATE = datetime.strptime("25.03.2026", "%d.%m.%Y")

# ===================== CONFIG =====================
TOKEN = "..."
MANAGER_ID = ...
DISCOUNT_MULTIPLIER = 0.65
PROMO_CODE = "GHOST35"
VIP_FREE_DELIVERY_UNTIL = "25.03.2026"

import random
import string

PROMO_DISCOUNT = 45  # %
DISCOUNT_MULTIPLIER = 0.55


# ===================== PROMO =====================
def generate_promo_code(user_id: int) -> str:
    """
    Генерує персональний промокод користувача
    Наприклад: GHOST-8347
    """
    suffix = ''.join(random.choices(string.digits, k=4))
    return f"GHOST-{suffix}"
    
# ===================== PRICING =====================
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
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ghosty-bot")

# ===================== PERSISTENCE =====================
persistence = PicklePersistence(filepath="ghosty_data.pkl")

# ===================== HELPERS =====================
def apply_discount(price: float) -> float:
    return round(price * DISCOUNT_MULT, 2)

def gen_promo(uid: int) -> str:
    return f"GHST{uid % 10000}{random.randint(100,999)}"

def gen_order_id(uid: int) -> str:
    return f"GHST-{uid}-{random.randint(1000,9999)}"

def vip_until(profile: dict) -> datetime:
    refs = profile.get("referrals", 0)
    return profile["vip_base"] + timedelta(days=7 * refs)

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
    
# 🎁 ПОДАРУНКИ — додаються ДО КОЖНОГО ЗАМОВЛЕННЯ
🎁 Подарунок (на вибір):
• Pumpkin Latte
• Glintwine
• Christmas Tree
• Strawberry Jelly
• Mystery One
• Fall Tea
• ...

def get_gift_liquids():
    return [v["name"] for v in LIQUIDS.values()]
    
GIFT_LIQUIDS = {
    9001: {"name": "🎁 Gift Liquid Mix #1", "desc": "Фруктовий мікс 30ml"},
    9002: {"name": "🎁 Gift Liquid Mix #2", "desc": "Ягідний мікс 30ml"},
    9003: {"name": "🎁 Gift Liquid Mix #3", "desc": "Мʼятний мікс 30ml"}
}

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

# 😵‍💫 HHC / ННС ВЕЙПИ (5 шт)
HHC_VAPES = {
    100: {
        "name": "😵‍💫 Packwoods Purple 1ml",
        "price": 549,
        "discount": True,
        "img": "https://i.ibb.co/DHXXSh2d/Ghost-Vape-3.jpg",
        "desc": (
            "🌿 90% ННС | Гібрид\n"
            "💜 Глибокий релакс + мʼяка ейфорія\n"
            "🧠 Розслабляє тіло, заспокоює думки\n"
            "🎯 Підійде для вечірнього чілу\n\n"
            "🎁 Рідина у подарунок на вибір"
        ),
        "effect": "Релакс, ейфорія, антистрес 😌",
        "payment_url": "https://heylink.me/ghosstyshop/"
    },

    101: {
        "name": "🍊 Packwoods Orange 1ml",
        "price": 629,
        "discount": True,
        "img": "https://i.ibb.co/V03f2yYF/Ghost-Vape-1.jpg",
        "desc": (
            "🌿 90% ННС | Гібрид\n"
            "⚡ Бадьорість + концентрація\n"
            "🍊 Яскравий цитрус\n"
            "🚀 Піднімає настрій та фокус\n\n"
            "🎁 Рідина у подарунок на вибір"
        ),
        "effect": "Енергія, фокус, позитив ⚡",
        "payment_url": "https://heylink.me/ghosstyshop/"
    },

    102: {
        "name": "🌸 Packwoods Pink 1ml",
        "price": 719,
        "discount": True,
        "img": "https://i.ibb.co/65j1901/Ghost-Vape-2.jpg",
        "desc": (
            "🌿 90% ННС | Гібрид\n"
            "🎉 Мʼякий стоун без перевантаження\n"
            "🌸 Легкий солодкий аромат\n"
            "🛋 Комфортний стан тіла\n\n"
            "🎁 Рідина у подарунок на вибір"
        ),
        "effect": "Комфорт, легкий стоун 😇",
        "payment_url": "https://heylink.me/ghosstyshop/"
    },

    103: {
        "name": "❄️ Whole Mint 2ml",
        "price": 849,
        "discount": True,
        "img": "https://i.ibb.co/675LQrNB/Ghost-Vape-4.jpg",
        "desc": (
            "🌿 95% ННС | Сатіва\n"
            "❄️ Свіжий мʼятний смак\n"
            "🧠 Чистий розум + мотивація\n"
            "📈 Підходить для активного дня\n\n"
            "🎁 Рідина у подарунок на вибір"
        ),
        "effect": "Ясність, енергія, мотивація 🧠",
        "payment_url": "https://heylink.me/ghosstyshop/"
    },

    104: {
        "name": "🌴 Jungle Boys White 2ml",
        "price": 999,
        "discount": True,  # ✅ ЗНИЖКА УВІМКНЕНА
        "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg",
        "desc": (
            "🌿 95% ННС | Індика\n"
            "😴 Глибокий релакс, сонливість\n"
            "🛌 Ідеально для вечора\n"
            "🔥 Потужний ефект\n\n"
            "🎁 Рідина у подарунок на вибір"
        ),
        "effect": "Глибокий релакс, сон 😴",
        "payment_url": "https://heylink.me/ghosstyshop/"
    }
}
# 🔌 POD-СИСТЕМИ (багато, з кольорами)
PODS = {
    500: {
        "name": "Vaporesso XROS 3 Mini",
        "price": 499,
        "imgs": [
            "https://ibb.co/yFSQ5QSn",
            "https://ibb.co/LzgrzZjC",
            "https://ibb.co/Q3ZNTBvg"
        ],
        "colors": ["Чорний", "Голубий", "Рожевий"],
        "desc": "🔋 1000 mAh\n💨 MTL/RDL\n⚡ Type-C"
    },
    501: {
        "name": "Vaporesso XROS 5",
        "price": 799,
        "imgs": [
            "https://ibb.co/hxjmpHF2",
            "https://ibb.co/DDkgjtV4",
            "https://ibb.co/r2C9JTzz"
PODS = {
    500: {
        "name": "🔌 Vaporesso XROS 3 Mini",
        "price": 499,
        "discount": False,
        "imgs": [
            "https://ibb.co/yFSQ5QSn",
            "https://ibb.co/LzgrzZjC",
            "https://ibb.co/Q3ZNTBvg"
        ],
        "colors": ["⚫ Чорний", "🔵 Голубий", "🌸 Рожевий"],
        "desc": (
            "🔋 Акумулятор: 1000 mAh\n"
            "💨 Затяжка: MTL / RDL\n"
            "⚡ Зарядка: Type-C\n"
            "✨ Компактний та легкий"
        ),
        "payment_url": "https://heylink.me/ghosstyshop/"
    },

    501: {
        "name": "🔌 Vaporesso XROS 5 Mini",
        "price": 579,
        "discount": False,
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
            "💨 Насичений смак"
        ),
        "payment_url": "https://heylink.me/ghosstyshop/"
    },

    502: {
        "name": "🔌 Vaporesso XROS Pro",
        "price": 689,
        "discount": False,
        "imgs": [
            "https://ibb.co/ynYwSMt6",
            "https://ibb.co/3mV7scXr",
            "https://ibb.co/xSJCgpJ5"
        ],
        "colors": ["⚫ Чорний", "🔴 Темно-червоний", "🌺 Рожево-червоний"],
        "desc": (
            "🔋 1200 mAh\n"
            "⚡ Fast Charge\n"
            "🎚 Регулювання затяжки\n"
            "🚀 Потужний та стильний"
        ),
        "payment_url": "https://heylink.me/ghosstyshop/"
    },

    503: {
        "name": "🔌 Vaporesso XROS Nano",
        "price": 519,
        "discount": False,
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
            "🎯 Надійний у дорозі"
        ),
        "payment_url": "https://heylink.me/ghosstyshop/"
    },

    504: {
        "name": "🔌 Vaporesso XROS 4",
        "price": 599,
        "discount": False,
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
            "👌 Збалансований"
        ),
        "payment_url": "https://heylink.me/ghosstyshop/"
    },

    505: {
        "name": "🔌 Vaporesso XROS 5",
        "price": 799,
        "discount": False,
        "imgs": [
            "https://ibb.co/hxjmpHF2",
            "https://ibb.co/DDkgjtV4",
            "https://ibb.co/r2C9JTzz"
        ],
        "colors": ["⚫ Чорний", "🌸 Рожевий", "🟣 Фіолетовий з полоскою"],
        "desc": (
            "🔋 1200 mAh\n"
            "⚡ Fast Charge\n"
            "💎 Преміум збірка\n"
            "🔥 Максимум смаку"
        ),
        "payment_url": "https://heylink.me/ghosstyshop/"
    },

    506: {
        "name": "🔌 Voopoo Vmate Mini Pod Kit",
        "price": 459,
        "discount": False,
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
            "🎒 Зручний щодня"
        ),
        "payment_url": "https://heylink.me/ghosstyshop/"
    }
}
# ===================== SEND TO MANAGER =====================
async def send_to_manager(update: Update, context: ContextTypes.DEFAULT_TYPE, order_id: str):
    query = update.callback_query
    user = update.effective_user
    profile = context.user_data.get("profile", {})
    orders = context.user_data.get("orders", [])

    order = next((o for o in orders if o["id"] == order_id), None)
    if not order:
        await query.answer("❌ Замовлення не знайдено")
        return

    text = (
        f"📥 <b>Нове замовлення</b>\n\n"
        f"🆔 <b>{order_id}</b>\n"
        f"👤 {profile.get('full_name', '-')}\n"
        f"📞 {profile.get('phone', '-')}\n"
        f"📍 {profile.get('address', '-')}\n"
        f"👤 @{user.username or '—'}\n\n"
        f"🛒 <b>Товари:</b>\n"
    )

    for i in order["items"]:
        text += f"• {i['name']} — {i['price']} грн\n"

    text += (
        f"\n🎁 <b>Подарунок:</b> 3 рідини\n"
        f"💸 <b>Сума:</b> {order['total']} грн\n"
        f"🏷 <b>Промокод:</b> {PROMO_CODE} (-{DISCOUNT_PERCENT}%)\n"
        f"📦 <b>Статус:</b> {order['status']}"
    )

    await context.bot.send_message(
        chat_id=MANAGER_ID,
        text=text,
        parse_mode="HTML"
    )

    await query.edit_message_text(
        "✅ <b>Дані надіслано менеджеру</b>\n\nОчікуйте підтвердження.",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🏠 В головне меню", callback_data="main")]
        ])
)
    
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
            InlineKeyboardButton("👨‍💻 Менеджер", url=f"https://t.me/{MANAGER_USERNAME}")
        ],
        [
            InlineKeyboardButton("📜 Угода", callback_data="terms"),
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
    user = update.effective_user
    args = context.args
    
if "promo_code" not in profile:
    profile["promo_code"] = generate_promo_code(update.effective_user.id)
    
    profile["promo_discount"] = PROMO_DISCOUNT
    
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
            "vip_base": BASE_VIP_DATE
        }
        context.user_data["cart"] = []
        context.user_data["orders"] = []

    # ===== REFERRAL =====
    if args:
        try:
            ref_id = int(args[0])
            profile = context.user_data["profile"]
            if ref_id != user.id and not profile.get("ref_applied"):
                profile["ref_applied"] = True
                profile["referrer"] = ref_id
        except ValueError:
            pass

    profile = context.user_data["profile"]
    vip_date = vip_until(profile)

    welcome_text = (
        f"👋 <b>{escape(user.first_name)}</b>, вітаємо у <b>Ghosty Shop</b> 💨\n\n"
        f"🎁 <b>Подарунок до кожного замовлення:</b>\n"
        f"• 3 рідини 30ml (безкоштовно)\n\n"
        f"🎫 Промокод: <code>{profile['promo']}</code> (-35%)\n"
        f"👑 VIP до: <b>{vip_date.strftime('%d.%m.%Y')}</b>\n"
        f"🚚 Доставка: <b>Безкоштовна</b>\n\n"
        f"👇 Оберіть дію:"
    )

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

    vip_until = profile.get("vip_until", "—")

    text = (
        f"👤 <b>Профіль користувача</b>\n\n"
        f"🏙 <b>Місто:</b> {city}\n"
        f"📍 <b>Район:</b> {district}\n"
        f"🏠 <b>Адреса:</b> {address}\n\n"
        f"🏷 <b>Промокод:</b> <code>{promo}</code>\n"
        f"💸 <b>Знижка:</b> -{discount}%\n\n"
        f"💎 <b>VIP:</b> до {vip_until}\n"
        f"🚚 Безкоштовна доставка\n"
    )

    await q.edit_message_text(
        text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✏️ Змінити дані", callback_data="edit_profile")
            ],
            [
                InlineKeyboardButton("⬅️ Назад", callback_data="main")
            ]
        ])
    )

# ===================== REF LINK =====================
async def show_ref_link(q, context):
    profile = context.user_data["profile"]
    link = f"https://t.me/{context.bot.username}?start={profile['uid']}"

    await q.message.reply_text(
        f"🔗 <b>Ваш реферальний лінк</b>\n\n"
        f"{link}\n\n"
        f"➕ <b>+7 днів VIP</b> за кожного друга",
        parse_mode="HTML"
    )

# ===================== CITY SELECT =====================
async def select_city(q, context):
    buttons = [
        [InlineKeyboardButton(f"🏙 {c}", callback_data=f"city_{c}")]
        for c in CITIES
    ]
    buttons.append([
        InlineKeyboardButton("⬅️ Назад", callback_data="profile"),
        InlineKeyboardButton("🏠 В головне меню", callback_data="main")
    ])

    await q.message.edit_text(
        "🏙 <b>Оберіть місто</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# ===================== SAVE CITY =====================
async def save_city(q, context, city):
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

    await q.message.edit_text(
        f"🏙 <b>{city}</b>\n\nОберіть район:",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# ===================== SAVE DISTRICT =====================
async def save_district(q, context, district):
    profile = context.user_data["profile"]
    profile["district"] = district

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

# ===================== ADDRESS EDIT =====================
async def edit_address(q, context):
    context.user_data["state"] = "address"
    await q.message.reply_text(
        "📦 Введіть адресу доставки (можна вставити Google Maps):"
    )

# ===================== TEXT HANDLER =====================
async def fast_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    text = update.message.text.strip()
    state = context.user_data.get("state")

    # гарантовано існує profile
    profile = context.user_data.setdefault("profile", {})

    # ===== SAVE ADDRESS =====
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

    # ===== SAVE NAME =====
    if state == "name":
        profile["name"] = text
        context.user_data["state"] = None

        await update.message.reply_text(
            f"✅ Імʼя збережено: <b>{text}</b>",
            parse_mode="HTML",
            reply_markup=main_menu()
        )
        return

    # ===== SAVE PHONE =====
    if state == "phone":
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
            "📝 Коментар до замовлення збережено.\n\n"
            "Натисніть кнопку нижче, щоб надіслати замовлення менеджеру.",
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
            InlineKeyboardButton("🏠 В головне меню", callback_data="main")
        ]
    ])

    await q.message.edit_caption(
        caption="🛍 <b>Асортимент</b>\n\nОберіть категорію:",
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

    await q.message.edit_caption(
        caption=f"{title}",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# ===================== ITEM VIEW =====================
async def show_item(q, context, pid: int):
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
        f"✅ <b>{final_price} грн (-35%)</b>\n\n"
        f"🎁 <b>Подарунок:</b> 3 рідини 30ml\n"
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

# ===================== COLOR SELECT =====================
async def select_color(q, context, pid: int):
    item = PODS.get(pid)
    if not item or "imgs" not in item:
        await q.answer("❌ Немає варіантів кольору")
        return

    buttons = []
    for idx, _ in enumerate(item["imgs"]):
        buttons.append([
            InlineKeyboardButton(f"🎨 Колір {idx+1}", callback_data=f"colorpick_{pid}_{idx}")
        ])

    buttons.append([
        InlineKeyboardButton("⬅️ Назад", callback_data=f"item_{pid}"),
        InlineKeyboardButton("🏠 В головне меню", callback_data="main")
    ])

    await q.message.edit_text(
        f"🎨 <b>{item['name']}</b>\nОберіть колір:",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def apply_color(q, context, pid: int, idx: int):
    item = PODS.get(pid)
    if not item:
        return

    context.user_data["selected_color"] = idx
    await show_item(q, context, pid)

# ===================== CART =====================
async def add_to_cart(q, context, pid: int):
    item = HHC_VAPES.get(pid) or LIQUIDS.get(pid) or PODS.get(pid)

    if not item:
        await q.answer("❌ Товар не знайдено")
        return

    cart = context.user_data.setdefault("cart", [])

    cart.append({
        "pid": pid,
        "name": item["name"],
        "price": calc_price(item),
        "base_price": item["price"]
    })

    await q.answer("✅ Додано в кошик")

async def show_cart(q, context):
    cart = context.user_data.get("cart", [])

    if not cart:
        await q.message.edit_text(
            "🛒 <b>Кошик порожній</b>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🛍 Асортимент", callback_data="assortment")],
                [InlineKeyboardButton("🏠 В головне меню", callback_data="main")]
            ])
        )
        return

    text = "🛒 <b>Ваш кошик:</b>\n\n"
    total = 0
    buttons = []

    for i, item in enumerate(cart):
        text += f"• {item['name']} — {item['price']} грн\n"
        total += item["price"]
        buttons.append([InlineKeyboardButton(f"❌ Видалити {i+1}", callback_data=f"del_{i}")])

    text += f"\n💰 <b>Разом:</b> {total} грн"

    buttons.append([
        InlineKeyboardButton("⚡ Оформити", callback_data="fast_all"),
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
    except:
        await q.answer("❌ Помилка")

# ===================== FAST ORDER =====================
async def fast_start(q, context, pid=None):
    context.user_data["fast_pid"] = pid
    context.user_data["state"] = "fast_name"

    await q.message.reply_text(
        "⚡ <b>Швидке замовлення</b>\n\n✍️ Введіть <b>Імʼя та Прізвище</b>:",
        parse_mode="HTML"
                                )
  # ===================== FAST ORDER FLOW =====================
async def fast_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = context.user_data.get("state")

    if not state:
        return  # ❗ важливо — інакше ловитиме всі повідомлення

    text = update.message.text.strip()
    profile = context.user_data.setdefault("profile", {})

    if state == "fast_name":
        profile["full_name"] = text
        context.user_data["state"] = "fast_phone"
        await update.message.reply_text("📞 Введіть номер телефону:")
        return

    if state == "fast_phone":
        profile["phone"] = text
        context.user_data["state"] = "fast_address"
        await update.message.reply_text(
            "📍 Введіть адресу доставки (текст або Google Maps):"
        )
        return

    if state == "fast_address":
        profile["address"] = text
        context.user_data["state"] = None
        await confirm_order(update, context)
        return


# ===================== PRICING =====================

DISCOUNT_PERCENT = 45
DISCOUNT_MULTIPLIER = 0.55
PROMO_CODE = "GHOSSTY352728"

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
# ===================== CONFIRM ORDER =====================
# ===================== CONFIRM ORDER =====================
async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cart = context.user_data.get("cart", [])
    profile = context.user_data.get("profile", {})

    if not cart:
        if update.message:
            await update.message.reply_text("❌ Кошик порожній")
        else:
            await update.callback_query.answer("❌ Кошик порожній", show_alert=True)
        return

    orders = context.user_data.setdefault("orders", [])
    order_id = f"GHST-{update.effective_user.id}-{len(orders) + 1}"

    promo = profile.get("promo", "AUTO-35")
    total = sum(i["price"] for i in cart)

    text = (
        f"📦 <b>Замовлення сформовано</b>\n\n"
        f"🆔 <b>{order_id}</b>\n\n"
        f"👤 {profile.get('full_name', '—')}\n"
        f"📞 {profile.get('phone', '—')}\n"
        f"📍 {profile.get('address', '—')}\n\n"
        f"🛒 <b>Товари:</b>\n"
    )

    for i in cart:
        text += f"• {i['name']} — {i['price']} грн\n"

    text += (
        f"\n🎁 <b>Подарунок:</b> 3 рідини 30ml\n"
        f"🏷 <b>Промокод:</b> {promo} (-35%)\n"
        f"🚚 <b>Доставка:</b> Безкоштовна (VIP)\n"
        f"💰 <b>До оплати:</b> {total} грн\n\n"
        f"💳 Оплата за посиланням нижче ⬇️"
    )

    kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💳 Оплатити", url=PAYMENT_LINK),
        ],
        [
            InlineKeyboardButton(
                "📤 Надіслати менеджеру",
                callback_data=f"send_manager_{order_id}"
            )
        ],
        [
            InlineKeyboardButton(
                "💳 Я оплатив / Надіслати квитанцію",
                callback_data=f"pay_{order_id}"
            )
        ],
        [
            InlineKeyboardButton("🏠 В головне меню", callback_data="main")
        ]
    ])

    # ✅ куди відповідати
    target = (
        update.message
        if update.message
        else update.callback_query.message
    )

    await target.reply_text(
        text,
        parse_mode="HTML",
        reply_markup=kb
    )

    # ✅ ЗБЕРІГАЄМО ЗАМОВЛЕННЯ
    orders.append({
        "id": order_id,
        "items": cart.copy(),
        "total": total,
        "promo": promo,
        "status": "Очікує оплату",
        "delivery": "VIP безкоштовна"
    })

    # очищаємо кошик
    context.user_data["cart"] = []

    # запамʼятати активне замовлення
    context.user_data["active_order_id"] = order_id

# ===================== SEND TO MANAGER =====================
async def send_to_manager(update: Update, context: ContextTypes.DEFAULT_TYPE, order_id: str):
    user = update.effective_user
    profile = context.user_data.get("profile", {})
    orders = context.user_data.get("orders", [])

    order = next((o for o in orders if o["id"] == order_id), None)
    if not order:
        await update.callback_query.answer("❌ Замовлення не знайдено")
        return

    text = (
        f"📥 <b>Нове замовлення</b>\n\n"
        f"🆔 {order_id}\n"
        f"👤 {profile.get('full_name')}\n"
        f"📞 {profile.get('phone')}\n"
        f"📍 {profile.get('address')}\n"
        f"👤 @{user.username}\n\n"
        f"🛒 Товари:\n"
    )

    for i in order["items"]:
        text += f"• {i['name']} — {i['price']} грн\n"

    text += (
        f"\n🎁 Подарунок: 3 рідини\n"
        f"💰 Сума: {order['total']} грн\n"
        f"📦 Статус: {order['status']}"
    )

    await context.bot.send_message(
        chat_id=MANAGER_ID,
        text=text,
        parse_mode="HTML"
    )

    await update.callback_query.edit_message_text(
        "✅ <b>Дані надіслано менеджеру</b>\n\nОчікуйте підтвердження.",
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
    for o in orders:
        text += f"🆔 {o['id']} — {o['status']} — {o['total']} грн\n"

    await q.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🏠 В головне меню", callback_data="main")]
        ])
    )

async def callbacks_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data

    # ===== MAIN MENU =====
    if data == "main":
        await q.edit_message_text(
            "🏠 <b>Головне меню</b>",
            parse_mode="HTML",
            reply_markup=main_menu()
        )

    elif data == "profile":
        await show_profile(q, context)

    elif data == "assortment":
        await show_assortment(q)

    elif data == "hhc":
        await show_category(q, HHC_VAPES, "😵‍💫 <b>HHC / ННС</b>", "assortment")

    elif data == "pods":
        await show_category(q, PODS, "🔌 <b>Pod-системи</b>", "assortment")

    elif data == "liquids":
        await show_category(q, LIQUIDS, "💧 <b>Рідини</b>", "assortment")

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

    else:
        await q.answer("⚠️ Невідома дія")
# ===================== BOT START =====================
def main():
    persistence = PicklePersistence(filepath="bot_data.pkl")

    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .persistence(persistence)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callbacks_router))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fast_input))
    app.add_handler(MessageHandler(filters.PHOTO, handle_receipt))  # ⬅️ ДЛЯ КВИТАНЦІЙ

    app.run_polling()


if __name__ == "__main__":
    main()

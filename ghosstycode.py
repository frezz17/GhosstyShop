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
    refs = profile.get("referrals", 0)
    return profile["vip_base"] + timedelta(days=7 * refs)

async def safe_edit_media(message, photo_url: str, caption: str, kb):
    try:
        await message.edit_media(
            media=InputMediaPhoto(
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
            logger.warning(f"safe_edit_media fallback failed: {e}")

# ===================== PRODUCTS =====================
HHC_VAPES = {
    100: {
        "name": "😵‍💫 Packwoods Purple 1ml",
        "price": 549,
        "img": "https://i.ibb.co/DHXXSh2d/Ghost-Vape-3.jpg",
        "desc": "90% HHC | Hybrid\n💜 Глибокий релакс + ейфорія"
    },
    101: {
        "name": "🍊 Packwoods Orange 1ml",
        "price": 629,
        "img": "https://i.ibb.co/V03f2yYF/Ghost-Vape-1.jpg",
        "desc": "90% HHC | Hybrid\n⚡ Бадьорість та фокус"
    },
    102: {
        "name": "🌸 Packwoods Pink 1ml",
        "price": 719,
        "img": "https://i.ibb.co/65j1901/Ghost-Vape-2.jpg",
        "desc": "90% HHC | Hybrid\n🎉 Мʼякий стоун"
    },
    103: {
        "name": "❄️ Whole Mint 2ml",
        "price": 849,
        "img": "https://i.ibb.co/675LQrNB/Ghost-Vape-4.jpg",
        "desc": "95% HHC | Sativa\n🧠 Чистий розум"
    },
    104: {
        "name": "🌴 Jungle Boys White 2ml",
        "price": 999,
        "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg",
        "desc": "95% HHC | Indica\n😴 Глибокий релакс\n❗ Без знижки"
    }
}

LIQUIDS = {
    301: {
        "name": "🎃 Pumpkin Latte",
        "price": 269,
        "img": "https://ibb.co/Y7qn69Ds",
        "desc": "☕ Гарбузовий латте з корицею"
    },
    302: {
        "name": "🍷 Glintwine",
        "price": 269,
        "img": "https://ibb.co/wF8r7Nmc",
        "desc": "🍇 Пряний глінтвейн"
    },
    303: {
        "name": "🎄 Christmas Tree",
        "price": 269,
        "img": "https://ibb.co/vCPGV8RV",
        "desc": "🌲 Хвоя та свіжість"
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
            InlineKeyboardButton("📍 Обрати місто", callback_data="city"),
            InlineKeyboardButton("🛒 Кошик", callback_data="cart")
        ],
        [
            InlineKeyboardButton("📦 Мої замовлення", callback_data="orders"),
            InlineKeyboardButton("👨‍💻 Менеджер", url=f"https://t.me/{MANAGER_USERNAME}")
        ],
        [
            InlineKeyboardButton("📜 Угода користувача", callback_data="terms"),
            InlineKeyboardButton("📢 Канал", url=CHANNEL_URL)
        ]
    ])

def back_menu(back_cb: str):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⬅️ Назад", callback_data=back_cb),
            InlineKeyboardButton("🏠 В головне меню", callback_data="main")
        ]
    ])
  
LIQUIDS = {
    301: {"name": "🎃 Pumpkin Latte", "price": 269, "img": "https://ibb.co/Y7qn69Ds"},
    302: {"name": "🍷 Glintwine", "price": 269, "img": "https://ibb.co/wF8r7Nmc"},
    303: {"name": "🎄 Christmas Tree", "price": 269, "img": "https://ibb.co/vCPGV8RV"},
}

# ================= MENUS =================
def main_menu():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("👤 Профіль", callback_data="profile"),
            InlineKeyboardButton("🛍️ Асортимент", callback_data="assortment")
        ],
        [
            InlineKeyboardButton("📍 Обрати місто", callback_data="select_city"),
            InlineKeyboardButton("🛒 Кошик", callback_data="cart")
        ],
        [
            InlineKeyboardButton("📋 Мої замовлення", callback_data="orders"),
            InlineKeyboardButton("👨‍💻 Менеджер", url=f"https://t.me/{MANAGER_USERNAME}")
        ],
        [
            InlineKeyboardButton("📜 Угода користувача", callback_data="terms"),
            InlineKeyboardButton("📢 Канал", url=CHANNEL_URL)
        ]
    ])

def back_kb(back):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⬅️ Назад", callback_data=back),
            InlineKeyboardButton("🏠 В головне меню", callback_data="main")
        ]
    ])
LIQUIDS = {
    301: {"name": "🎃 Pumpkin Latte", "price": 269, "img": "https://ibb.co/Y7qn69Ds", "desc": "Гарбузовий латте ☕"},
    302: {"name": "🍷 Glintwine", "price": 269, "img": "https://ibb.co/wF8r7Nmc", "desc": "Пряний глінтвейн 🔥"},
    303: {"name": "🎄 Christmas Tree", "price": 269, "img": "https://ibb.co/vCPGV8RV", "desc": "Хвоя та холод 🌲"},
}

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
        "desc": "90% HHC | Hybrid\n⚡ Енергія та фокус"
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

PODS = {
    500: {
        "name": "🔌 Vaporesso XROS 3 Mini",
        "price": 499,
        "imgs": [
            "https://ibb.co/yFSQ5QSn",
            "https://ibb.co/LzgrzZjC",
            "https://ibb.co/Q3ZNTBvg"
        ],
        "desc": (
            "🔋 Акумулятор: 1000 mAh\n"
            "💨 Тип затяжки: MTL / RDL\n"
            "⚡ Зарядка: Type-C\n"
            "🎨 Кольори: чорний, голубий, рожевий"
        )
    },
    501: {
        "name": "🔌 Vaporesso XROS 5 Mini",
        "price": 579,
        "imgs": [
            "https://ibb.co/RkNgt1Qr",
            "https://ibb.co/KxvJC1bV",
            "https://ibb.co/WpMYBCH1"
        ],
        "desc": (
            "🔋 1000 mAh\n"
            "🔥 COREX 2.0\n"
            "⚡ Швидка зарядка\n"
            "🎨 рожевий / фіолетовий / чорний"
        )
    },
    502: {
        "name": "🔌 Vaporesso XROS Pro",
        "price": 689,
        "imgs": [
            "https://ibb.co/ynYwSMt6",
            "https://ibb.co/3mV7scXr",
            "https://ibb.co/xSJCgpJ5"
        ],
        "desc": (
            "🔋 1200 mAh\n"
            "⚡ Fast Charge\n"
            "💨 Регуляція затяжки\n"
            "🎨 чорний / темно-червоний / рожево-червоний"
        )
    },
    503: {
        "name": "🔌 Vaporesso XROS Nano",
        "price": 519,
        "imgs": [
            "https://ibb.co/5XW2yN80",
            "https://ibb.co/93dJ8wKS",
            "https://ibb.co/Qj90hyyz"
        ],
        "desc": (
            "🔋 1000 mAh\n"
            "🪖 Камуфляж\n"
            "💨 MTL\n"
            "🎨 camo 1 / 2 / 3"
        )
    },
    504: {
        "name": "🔌 Vaporesso XROS 4",
        "price": 599,
        "imgs": [
            "https://ibb.co/LDRbQxr1",
            "https://ibb.co/NPHYSjN",
            "https://ibb.co/LhbzXD57"
        ],
        "desc": (
            "🔋 1000 mAh\n"
            "🔥 COREX\n"
            "🎨 рожевий / чорний / синій"
        )
    },
    505: {
        "name": "🔌 Vaporesso XROS 5",
        "price": 799,
        "imgs": [
            "https://ibb.co/hxjmpHF2",
            "https://ibb.co/DDkgjtV4",
            "https://ibb.co/r2C9JTzz"
        ],
        "desc": (
            "🔋 1200 mAh\n"
            "⚡ Fast Charge\n"
            "🎨 чорний / рожевий / фіолетовий з полоскою"
        )
    },
    506: {
        "name": "🔌 Voopoo Vmate Mini Pod Kit",
        "price": 459,
        "imgs": [
            "https://ibb.co/8L0JNTHz",
            "https://ibb.co/0RZ1VDnG",
            "https://ibb.co/21LPrbbj"
        ],
        "desc": (
            "🔋 1000 mAh\n"
            "💨 Автозатяжка\n"
            "🎨 рожевий / червоний / чорний"
        )
    }
}
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
            "vip_base": BASE_VIP_DATE
        }

    # ===== рефералка =====
    if args:
        try:
            ref_id = int(args[0])
            if ref_id != user.id:
                context.user_data["referrer_id"] = ref_id
        except ValueError:
            pass

    profile = context.user_data["profile"]
    vip_date = vip_until(profile)

    text = (
        f"👋 <b>{escape(user.first_name)}</b>, вітаємо у <b>Ghosty Shop</b> 💨\n\n"
        f"🎫 Ваш промокод: <code>{profile['promo']}</code> (-35%)\n"
        f"👑 VIP активний до: <b>{vip_date.strftime('%d.%m.%Y')}</b>\n"
        f"🚚 Доставка: <b>Безкоштовна</b>\n\n"
        f"👇 Оберіть дію:"
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

# ===================== CALLBACKS =====================
async def callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data
    

    for pid, item in PODS.items():
        buttons.append([
            InlineKeyboardButton(item["name"], callback_data=f"item_{pid}"),
            InlineKeyboardButton("⚡", callback_data=f"fast_{pid}")
        ])

    buttons.append([
        InlineKeyboardButton("⬅️ Назад", callback_data="assortment"),
        InlineKeyboardButton("🏠 В головне меню", callback_data="main")
    ])

    await q.message.edit_caption(
        caption="🔌 <b>Pod-системи</b>\n\nОбери модель 👇",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

await safe_edit_media(
    q.message,
    item["imgs"][0] if "imgs" in item else item["img"],
    caption,
    kb
)

elif data == "fast_all":
        context.user_data["state"] = "fast_name"
        context.user_data["fast_pid"] = None
        await q.message.reply_text(
            "⚡ <b>Швидке замовлення</b>\n\n✍️ Введіть імʼя та прізвище:",
            parse_mode="HTML"
        )

async def callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data
    profile = context.user_data["profile"]

    # ===== MAIN =====
    if data == "main":
        await start(update, context)

    # ===== PROFILE =====
    elif data == "profile":
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
                InlineKeyboardButton("✏️ Змінити адресу", callback_data="edit_address"),
                InlineKeyboardButton("🔗 Реферал-лінк", callback_data="ref_link")
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

    elif data == "ref_link":
        link = f"https://t.me/{context.bot.username}?start={profile['uid']}"
        await q.message.reply_text(
            f"🔗 <b>Ваш реферальний лінк</b>\n\n{link}\n\n"
            f"➕ +7 днів VIP за кожного друга!",
            parse_mode="HTML"
        )

    elif data == "edit_address":
        context.user_data["state"] = "address"
        await q.message.reply_text("📦 Введіть нову адресу доставки:")


    # ===== ITEM VIEW =====
    elif data.startswith("item_"):
    elif data.startswith("item_"):
    pid = int(data.split("_")[1])

    item = HHC_VAPES.get(pid) or LIQUIDS.get(pid) or PODS.get(pid)
    if not item:
        await q.message.reply_text("❌ Товар не знайдено")
        return

    base_price = item["price"]
    final_price = apply_discount(base_price)

    caption = (
        f"<b>{item['name']}</b>\n\n"
        f"{item.get('desc','')}\n\n"
        f"❌ {base_price} грн\n"
        f"✅ <b>{final_price} грн (-35%)</b>\n"
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
            InlineKeyboardButton("⬅️ Назад", callback_data="pods" if pid >= 500 else "assortment"),
            InlineKeyboardButton("🏠 В головне меню", callback_data="main")
        ]
    ])

    photo = item["imgs"][0] if "imgs" in item else item["img"]

    await safe_edit_media(q.message, photo, caption, kb)

    # ===== FAST ORDER INIT =====
    elif data.startswith("fast_"):
        pid = int(data.split("_")[1])
        context.user_data["fast_pid"] = pid
        context.user_data["state"] = "fast_name"
        await q.message.reply_text("✍️ Введіть імʼя та прізвище для замовлення:"
                                   
      # ===================== TEXT INPUT HANDLER =====================
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    state = context.user_data.get("state")
    profile = context.user_data["profile"]

    if state == "address":
        profile["address"] = text
        context.user_data["state"] = None
        await update.message.reply_text("✅ Адресу збережено у профілі")
        return

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
        await finalize_order(update, context)
        return


# ===================== FINALIZE ORDER =====================
async def finalize_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pid = context.user_data.get("fast_pid")
    item = HHC_VAPES.get(pid) or LIQUIDS.get(pid) or PODS.get(pid)
    profile = context.user_data["profile"]

    order_id = f"GHST{profile['uid']}{random.randint(100,999)}"
    base = item["price"]
    total = apply_discount(base)

    text = (
        f"✅ <b>Замовлення #{order_id} сформовано</b>\n\n"
        f"📦 <b>Товар:</b> {item['name']}\n"
        f"💰 Ціна: {base} грн\n"
        f"🎫 Промокод: <code>{profile['promo']}</code>\n"
        f"🔥 <b>До оплати (-35%): {total:.2f} грн</b>\n\n"
        f"💳 <b>Оплата:</b>\n"
        f"{PAYMENT_URL}\n\n"
        f"📝 Коментар до переказу:\n"
        f"<code>{order_id}</code>\n\n"
        f"👇 Після цього можете відправити дані менеджеру"
    )

    kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💳 Оплатити", url=PAYMENT_URL),
            InlineKeyboardButton("✅ Відправити менеджеру", callback_data=f"send_mgr_{order_id}")
        ],
        [
            InlineKeyboardButton("🏠 В головне меню", callback_data="main")
        ]
    ])

    await update.message.reply_text(text, parse_mode="HTML", reply_markup=kb)

    context.user_data["last_order"] = {
        "id": order_id,
        "item": item["name"],
        "price": total
    }


# ===================== SEND TO MANAGER =====================
async def send_to_manager(context: ContextTypes.DEFAULT_TYPE, order_id: str, profile: dict):
    msg = (
        f"🆕 <b>НОВЕ ЗАМОВЛЕННЯ</b>\n\n"
        f"🆔 {order_id}\n"
        f"👤 {profile['name']} (@{profile.get('username','—')})\n"
        f"📞 {profile.get('phone')}\n"
        f"📦 {profile.get('address')}\n\n"
        f"🎫 Промокод: {profile['promo']}\n"
        f"👑 VIP до: {vip_until(profile).strftime('%d.%m.%Y')}\n"
        f"💰 Сума зі знижкою: {context.user_data['last_order']['price']:.2f} грн"
    )

    await context.bot.send_message(
        chat_id=f"@{MANAGER_USERNAME}",
        text=msg,
        parse_mode="HTML"
    )


# ===================== CALLBACK CONTINUATION =====================
async def callbacks_extra(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data
    profile = context.user_data["profile"]

    if data.startswith("send_mgr_"):
        order_id = data.replace("send_mgr_", "")
        await send_to_manager(context, order_id, profile)
        await q.message.reply_text("✅ Дані успішно передані менеджеру 👨‍💻")


# ===================== APP INIT =====================
def main():
    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callbacks))
    app.add_handler(CallbackQueryHandler(callbacks_extra))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    logger.info("✅ Бот успішно запущено на сервері BotHost.ru — все працює")
    app.run_polling()


if __name__ == "__main__":
    main()

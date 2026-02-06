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
    filters
)
from telegram.error import BadRequest

# ================= CONFIG =================
TOKEN = "8351638507:AAG2HP0OmYx7ip8-uZcLQCilPTfoBhtEGq0"
MANAGER_USERNAME = "ghosstydp"
CHANNEL_URL = "https://t.me/GhostyStaffDP"
PAYMENT_URL = "https://heylink.me/ghosstyshop/"
WELCOME_PHOTO = "https://i.ibb.co/y7Q194N/1770068775663.png"

DISCOUNT_MULT = 0.65
BASE_VIP_DATE = datetime.strptime("25.03.2026", "%d.%m.%Y")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================= HELPERS =================
def discount(price: float) -> float:
    return round(price * DISCOUNT_MULT, 2)

def gen_promo():
    return f"GHOST-{random.randint(1000,9999)}"

def gen_order_id(uid):
    return f"GHST-{uid}-{random.randint(1000,9999)}"

def calc_vip_until(profile):
    return profile["vip_until"] + timedelta(days=7 * profile["referrals"])

async def safe_edit_media(msg, media, kb):
    try:
        await msg.edit_media(media=media, reply_markup=kb)
    except BadRequest:
        try:
            await msg.delete()
            await msg.reply_photo(
                photo=media.media,
                caption=media.caption,
                parse_mode="HTML",
                reply_markup=kb
            )
        except Exception:
            pass

# ================== PRODUCTS ==================
HHC_VAPES = {
    100: {
        "name": "😵‍💫 Packwoods Purple",
        "price": 549,
        "img": "https://i.ibb.co/DHXXSh2d/Ghost-Vape-3.jpg",
        "desc": "90% HHC | Hybrid\n💨 Релакс + ейфорія"
    },
    101: {
        "name": "🍊 Packwoods Orange",
        "price": 629,
        "img": "https://i.ibb.co/V03f2yYF/Ghost-Vape-1.jpg",
        "desc": "90% HHC | Hybrid\n⚡ Енергія та фокус"
    },
    102: {
        "name": "🌸 Packwoods Pink",
        "price": 719,
        "img": "https://i.ibb.co/65j1901/Ghost-Vape-2.jpg",
        "desc": "90% HHC | Hybrid\n🎉 Мʼякий стоун"
    },
    103: {
        "name": "❄️ Whole Mint",
        "price": 849,
        "img": "https://i.ibb.co/675LQrNB/Ghost-Vape-4.jpg",
        "desc": "95% HHC | Sativa\n🧠 Чистий розум"
    },
    104: {
        "name": "🌴 Jungle Boys White",
        "price": 999,
        "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg",
        "desc": "95% HHC | Indica\n😴 Глибокий релакс"
    }
}

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
  HHC_VAPES = {
    100: {
        "name": "😵‍💫 Packwoods Purple",
        "price": 549,
        "img": "https://i.ibb.co/DHXXSh2d/Ghost-Vape-3.jpg",
        "desc": "90% HHC | Hybrid\n💨 Релакс + ейфорія"
    },
    101: {
        "name": "🍊 Packwoods Orange",
        "price": 629,
        "img": "https://i.ibb.co/V03f2yYF/Ghost-Vape-1.jpg",
        "desc": "90% HHC | Hybrid\n⚡ Енергія та фокус"
    },
    102: {
        "name": "🌸 Packwoods Pink",
        "price": 719,
        "img": "https://i.ibb.co/65j1901/Ghost-Vape-2.jpg",
        "desc": "90% HHC | Hybrid\n🎉 Мʼякий стоун"
    },
    103: {
        "name": "❄️ Whole Mint",
        "price": 849,
        "img": "https://i.ibb.co/675LQrNB/Ghost-Vape-4.jpg",
        "desc": "95% HHC | Sativa\n🧠 Чистий розум"
    },
    104: {
        "name": "🌴 Jungle Boys White",
        "price": 999,
        "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg",
        "desc": "95% HHC | Indica\n😴 Глибокий релакс"
    }
}

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

HHC = {
    100: {"name": "Packwoods Purple", "price": 549, "img": "https://i.ibb.co/DHXXSh2d/Ghost-Vape-3.jpg",
          "desc": "😵‍💫 Гібрид | 90% HHC\nРелакс + ейфорія"},
    101: {"name": "Packwoods Orange", "price": 629, "img": "https://i.ibb.co/V03f2yYF/Ghost-Vape-1.jpg",
          "desc": "🍊 Гібрид | 90% HHC\nЕнергія та фокус"},
    102: {"name": "Packwoods Pink", "price": 719, "img": "https://i.ibb.co/65j1901/Ghost-Vape-2.jpg",
          "desc": "🌸 Гібрид | 90% HHC\nМʼякий стоун"},
    103: {"name": "Whole Mint", "price": 849, "img": "https://i.ibb.co/675LQrNB/Ghost-Vape-4.jpg",
          "desc": "❄️ Сатива | 95% HHC\nЧистий розум"},
    104: {"name": "Jungle Boys White", "price": 999, "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg",
          "desc": "🌴 Індика | 95% HHC\nГлибокий релакс"},
}
# ================== START ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = context.args

    if "profile" not in context.user_data:
        context.user_data["profile"] = {
            "name": user.first_name,
            "username": user.username,
            "city": None,
            "district": None,
            "address": None,
            "promo": gen_promo(),
            "referrals": 0,
            "vip_until": BASE_VIP_DATE
        }

    # рефералка
    if args and not context.user_data.get("referred"):
        context.user_data["referred"] = True
        context.user_data["profile"]["referrals"] += 1

    p = context.user_data["profile"]
    vip_until = calc_vip_until(p)

    text = (
        f"👋 <b>{escape(user.first_name)}</b>, вітаємо в <b>Ghosty Shop</b>\n\n"
        f"🎫 Промокод: <code>{p['promo']}</code> (-35%)\n"
        f"👑 VIP до: <b>{vip_until.strftime('%d.%m.%Y')}</b>\n"
        f"🚚 Доставка: Безкоштовна\n\n"
        f"👇 Оберіть дію:"
    )

    if update.message:
        await update.message.reply_photo(
            WELCOME_PHOTO, caption=text, parse_mode="HTML", reply_markup=main_menu()
        )
    else:
        await update.callback_query.message.edit_caption(
            text, parse_mode="HTML", reply_markup=main_menu()
        )

async def callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    d = q.data
    p = context.user_data["profile"]

    if d == "main":
        await start(update, context)

    elif d == "assortment":
        kb = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("😵‍💫 HHC / ННС", callback_data="hhc"),
                InlineKeyboardButton("💧 Рідини", callback_data="liq")
            ],
            [
                InlineKeyboardButton("⚡ Швидке замовлення", callback_data="fast_any"),
                InlineKeyboardButton("🏠 В головне меню", callback_data="main")
            ]
        ])
        await q.message.edit_caption(
            "🛍️ <b>Асортимент</b>", parse_mode="HTML", reply_markup=kb
        )

    elif d == "hhc":
        kb = []
        for pid, item in HHC_VAPES.items():
            kb.append([
                InlineKeyboardButton(item["name"], callback_data=f"prod_{pid}"),
                InlineKeyboardButton("⚡", callback_data=f"fast_{pid}")
            ])
        kb.append([
            InlineKeyboardButton("⬅️ Назад", callback_data="assortment"),
            InlineKeyboardButton("🏠 В головне меню", callback_data="main")
        ])
        await q.message.edit_caption(
            "😵‍💫 <b>HHC / ННС Вейпи</b>", parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(kb)
        )

    elif d.startswith("prod_"):
        pid = int(d.split("_")[1])
        item = HHC_VAPES[pid]
        price = discount(item["price"])

        text = (
            f"<b>{item['name']}</b>\n\n"
            f"{item['desc']}\n\n"
            f"❌ {item['price']} грн\n"
            f"✅ <b>{price} грн (-35%)</b>\n"
            f"🎁 Подарунок: рідина\n"
            f"👑 VIP доставка: 0 грн"
        )

        kb = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🎁 Обрати подарунок", callback_data=f"gift_{pid}"),
                InlineKeyboardButton("⚡ Швидке замовлення", callback_data=f"fast_{pid}")
            ],
            [
                InlineKeyboardButton("⬅️ Назад", callback_data="hhc"),
                InlineKeyboardButton("🏠 В головне меню", callback_data="main")
            ]
        ])

        await safe_edit_media(
            q.message,
            InputMediaPhoto(item["img"], caption=text, parse_mode="HTML"),
            kb
        )

    elif d.startswith("fast_"):
        pid = int(d.split("_")[1])
        context.user_data["fast_pid"] = pid
        context.user_data["state"] = "name"
        await q.message.reply_text("✍️ Введіть імʼя та прізвище:")
      # ================== TEXT INPUT ==================
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = context.user_data.get("state")
    p = context.user_data["profile"]
    text = update.message.text

    if state == "name":
        p["name"] = text
        context.user_data["state"] = "phone"
        await update.message.reply_text("📞 Введіть номер телефону:")

    elif state == "phone":
        p["phone"] = text
        context.user_data["state"] = "address"
        await update.message.reply_text("📦 Введіть адресу доставки:")

    elif state == "address":
        p["address"] = text
        context.user_data["state"] = None

        pid = context.user_data["fast_pid"]
        item = HHC_VAPES[pid]
        order_id = gen_order_id(update.effective_user.id)
        price = discount(item["price"])

        summary = (
            f"✅ <b>Замовлення #{order_id}</b>\n\n"
            f"{item['name']} x1\n"
            f"💰 Сума: <b>{price} грн</b>\n"
            f"🎫 Промокод: <code>{p['promo']}</code>\n"
            f"📦 Адреса: {p['address']}\n\n"
            f"💬 Коментар до переказу:\n<code>{order_id}</code>"
        )

        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💳 Оплатити", url=PAYMENT_URL)],
            [InlineKeyboardButton("☑️ Відправити менеджеру", callback_data=f"send_{order_id}")],
            [InlineKeyboardButton("🏠 В головне меню", callback_data="main")]
        ])

        await update.message.reply_text(summary, parse_mode="HTML", reply_markup=kb)

async def send_manager(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    oid = q.data.split("_")[1]
    p = context.user_data["profile"]

    text = (
        f"📦 <b>НОВЕ ЗАМОВЛЕННЯ</b>\n\n"
        f"🆔 {oid}\n"
        f"👤 {p['name']}\n"
        f"📞 {p.get('phone','—')}\n"
        f"📍 {p.get('address','—')}\n"
        f"🎫 {p['promo']}\n"
        f"👑 VIP активний\n"
        f"⏳ Статус: Очікує оплату"
    )

    await context.bot.send_message(
        chat_id=f"@{MANAGER_USERNAME}",
        text=text,
        parse_mode="HTML"
    )

    await q.message.reply_text("✅ Дані передано менеджеру")

# ================= RUN =================
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(callbacks))
app.add_handler(CallbackQueryHandler(send_manager, pattern="^send_"))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

app.run_polling()
logger.info("BOT STARTED SUCCESSFULLY")

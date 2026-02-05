import random
import logging
from datetime import datetime
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
    ContextTypes
)

# ================== CONFIG ==================
TOKEN = "PASTE_YOUR_TOKEN_HERE"
MANAGER_URL = "https://t.me/ghosstydp"
WELCOME_PHOTO = "https://i.ibb.co/y7Q194N/1770068775663.png"

PROMO_EXPIRY = "25.03.2026"
DISCOUNT_RATE = 0.65  # -35%

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ================== LOCATIONS ==================
LOCATIONS = {
    "🏙️ Київ": ["🏛️ Печерський", "🎡 Оболонський", "🏗️ Дарницький", "🌳 Деснянський", "🛤️ Святошинський", "🌲 Голосіївський", "🎓 Шевченківський", "✈️ Солом’янський"],
    "🏗️ Харків": ["🏢 Салтівка", "🏛️ Центр", "🏔️ Холодна Гора", "🏟️ Слобідський", "🏭 Індустріальний", "🛠️ ХТЗ", "🏗️ Олексіївка", "🏤 Московський"],
    "⚓ Одеса": ["🌊 Приморський", "🚜 Суворовський", "🍷 Малиновський", "🏖️ Київський", "🏢 Таїрово", "🏠 Черемушки", "🏥 Слобідка", "🏘️ Млини"],
    "🌊 Дніпро": ["🏙️ Центр", "🎡 Перемога", "🌳 Тополя", "🛍️ Лівобережний-3 / Караван", "🌉 Амур-Нижньодніпровський", "🏗️ Чечелівський", "🏢 Шевченківський", "🏭 Новокодацький"],
    "🦁 Львів": ["🏰 Галицький", "🚂 Залізничний", "🎨 Франківський", "🌳 Шевченківський", "🏢 Сихівський", "⛲ Личаківський", "🏘️ Рясне", "🌲 Брюховичі"],
    "⚡ Запоріжжя": ["🔋 Дніпровський", "🌳 Вознесенівський", "🏛️ Олександрівський", "🏘️ Комунарський", "🐎 Хортицький", "🏢 Шевченківський", "🏭 Заводський", "🌅 Південний"],
    "🔩 Кривий Ріг": ["🏙️ Центральний", "⛏️ Тернівський", "🏛️ Покровський", "🎡 Саксаганський", "🚂 Довгинцівський", "🏭 Металургійний", "🌳 Інгулецький", "🏗️ Південний"],
    "⛲ Вінниця": ["🏢 Замостя", "🍒 Вишенька", "🌊 Поділ", "🏛️ Старе місто", "🎓 Академічний", "🏗️ Тяжилів", "🏘️ Слов’янка", "🇰🇷 Корея"],
    "🚢 Миколаїв": ["🏙️ Центральний", "🏗️ Заводський", "🌊 Інгульський", "⚓ Корабельний", "🏘️ Варварівка", "🌳 Тернівка", "🌲 Матвіївка", "🏠 Соляні"],
    "🛠️ Кам'янське": ["🏤 Центральний", "🏗️ Південний", "🌊 Дніпровський", "🏠 Новокам’янка", "🏢 Победа", "🏘️ Правобережний", "🌳 Лівобережний", "🏙️ Соцмісто"]
}

# ================== VAPES ==================
VAPES = [
    {"id": 0, "name": "🍊 Packwoods Orange", "old": 469, "img": "https://i.ibb.co/V03f2yYF/Ghost-Vape-1.jpg"},
    {"id": 1, "name": "🌸 Packwoods Pink", "old": 549, "img": "https://i.ibb.co/65j1901/Ghost-Vape-2.jpg"},
    {"id": 2, "name": "🍇 Packwoods Purple", "old": 674, "img": "https://i.ibb.co/svXqXPgL/Ghost-Vape-3.jpg"},
    {"id": 3, "name": "❄️ Whole Mint", "old": 809, "img": "https://i.ibb.co/675LQrNB/Ghost-Vape-4.jpg"},
    {"id": 4, "name": "🌴 Jungle Boys", "old": 949, "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg"}
]

# ================== KEYBOARDS ==================
def main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👤 Мій профіль", callback_data="profile")],
        [InlineKeyboardButton("💨 Вейпи", callback_data="catalog")],
        [InlineKeyboardButton("📍 Обрати місто", callback_data="cities")],
        [InlineKeyboardButton("👨‍💻 Менеджер", url=MANAGER_URL)]
    ])

# ================== START ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if "promo" not in context.user_data:
        context.user_data["promo"] = f"GHOST-{random.randint(100,999)}"
        context.user_data["reg"] = datetime.now().strftime("%d.%m.%Y")

    text = (
        f"🌿 *Вітаємо, {user.first_name}!* 🌿\n\n"
        f"🎁 Ваш персональний промокод:\n`{context.user_data['promo']}`\n\n"
        f"🔥 Знижка *-35%* на перше замовлення\n"
        f"⏳ Дійсний до *{PROMO_EXPIRY}*"
    )

    await update.message.reply_photo(
        WELCOME_PHOTO,
        caption=text,
        parse_mode="Markdown",
        reply_markup=main_keyboard()
    )

# ================== CALLBACKS ==================
async def callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    ud = context.user_data
    data = q.data
    user = q.from_user

    async def edit(text, img=WELCOME_PHOTO, kb=None):
        await q.message.edit_media(
            InputMediaPhoto(media=img, caption=text, parse_mode="Markdown"),
            reply_markup=kb
        )

    # ---- CATALOG ----
    if data == "catalog":
        buttons = []
        for v in VAPES:
            new_price = int(v["old"] * DISCOUNT_RATE)
            buttons.append([InlineKeyboardButton(f"{v['name']} | {new_price}₴ 🔥", callback_data=f"vape_{v['id']}")])
        buttons.append([InlineKeyboardButton("⬅️ Назад", callback_data="home")])
        await edit("💨 *Каталог вейпів (-35%)*", kb=InlineKeyboardMarkup(buttons))

    elif data.startswith("vape_"):
        v = VAPES[int(data.split("_")[1])]
        new_price = int(v["old"] * DISCOUNT_RATE)

        caption = (
            f"*{v['name']}*\n"
            f"━━━━━━━━━━━━━━\n"
            f"❌ Стара ціна: ~{v['old']}₴~\n"
            f"✅ Нова ціна: *{new_price}₴*\n\n"
            f"🎫 Промокод: `{ud['promo']}`\n"
            f"⏳ До {PROMO_EXPIRY}\n\n"
            f"📍 {ud.get('city','❌ Місто не обрано')} / {ud.get('dist','❌')}"
        )

        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🛒 Замовити", url=MANAGER_URL)],
            [InlineKeyboardButton("⬅️ Назад", callback_data="catalog")]
        ])

        await edit(caption, img=v["img"], kb=kb)

    # ---- PROFILE ----
    elif data == "profile":
        text = (
            f"👤 *МІЙ ПРОФІЛЬ*\n"
            f"━━━━━━━━━━━━━━\n"
            f"👤 {user.first_name}\n"
            f"🔗 @{user.username or 'немає'}\n"
            f"🆔 `{user.id}`\n\n"
            f"🎫 Промокод: `{ud['promo']}`\n"
            f"🔥 Знижка: -35%\n"
            f"⏳ До {PROMO_EXPIRY}\n\n"
            f"📍 {ud.get('city','❌')} / {ud.get('dist','❌')}"
        )

        await edit(text, kb=InlineKeyboardMarkup([
            [InlineKeyboardButton("📍 Змінити місто", callback_data="cities")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="home")]
        ]))

    # ---- LOCATIONS ----
    elif data == "cities":
        kb = [[InlineKeyboardButton(city, callback_data=f"city_{city}")] for city in LOCATIONS]
        kb.append([InlineKeyboardButton("⬅️ Назад", callback_data="home")])
        await edit("📍 *Оберіть місто:*", kb=InlineKeyboardMarkup(kb))

    elif data.startswith("city_"):
        city = data.replace("city_", "")
        ud["city"] = city
        kb = [[InlineKeyboardButton(d, callback_data=f"dist_{d}")] for d in LOCATIONS[city]]
        kb.append([InlineKeyboardButton("⬅️ Назад", callback_data="cities")])
        await edit(f"🏙️ *{city}*\nОберіть район:", kb=InlineKeyboardMarkup(kb))

    elif data.startswith("dist_"):
        ud["dist"] = data.replace("dist_", "")
        await edit("✅ *Локацію збережено!*", kb=main_keyboard())

    elif data == "home":
        await edit("🏠 *Головне меню*", kb=main_keyboard())

# ================== RUN ==================
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callbacks))
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()

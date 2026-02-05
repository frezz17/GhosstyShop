import random
import logging
from datetime import datetime
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# ================== CONFIG ==================
TOKEN = "8351638507:AAEOSgiUsQHk2DtI2aurKqGhoS5-JPLqf-g"
MANAGER_URL = "https://t.me/ghosstydp"
WELCOME_PHOTO = "https://i.ibb.co/y7Q194N/1770068775663.png"
PROMO_EXPIRY = "25.03.2026"
DISCOUNT_RATE = 0.55  # -45%

# Professional Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# ================== DATA REPOSITORY ==================
LOCATIONS = {
    "Київ 🏙️": ["Печерський 🏛️", "Оболонський 🎡", "Дарницький 🏗️", "Деснянський 🌳", "Святошинський 🛤️", "Голосіївський 🌲", "Шевченківський 🎓", "Солом’янський ✈️"],
    "Харків 🏗️": ["Салтівка 🏢", "Центр 🏛️", "Холодна Гора 🏔️", "Слобідський 🏟️", "Індустріальний 🏭", "ХТЗ 🛠️", "Олексіївка 🏗️", "Московський 🏤"],
    "Одеса ⚓": ["Приморський 🌊", "Суворовський 🚜", "Малиновський 🍷", "Київський 🏖️", "Ближні Млини 🏠", "Дальні Млини 🏘️", "Таїрово 🏢", "Слобідка 🏥"],
    "Дніпро 🌊": ["Центр 🏙️", "Перемога 🎡", "Тополя 🌳", "Лівобережний-3 🚉", "Чечелівський 🏗️", "Шевченківський 🏢", "Новокодацький 🏭", "Амур-Нижньодніпровський 🌉"],
    "Львів 🦁": ["Галицький 🏰", "Залізничний 🚂", "Франківський 🎨", "Шевченківський 🌳", "Сихівський 🏢", "Личаківський ⛲", "Горіхів 🏘️", "Старий Львів 🏛️"],
    "Запоріжжя ⚡": ["Дніпровський 🔋", "Вознесенівський 🌳", "Олександрівський 🏛️", "Комунарський 🏘️", "Хортицький 🐎", "Шевченківський 🏢", "Заводський 🏭", "Острови 🏝️"],
    "Кривий Ріг 🔩": ["Центральний 🏙️", "Тернівський ⛏️", "Покровський 🏛️", "Саксаганський 🎡", "Довгинцівський 🚂", "Металургійний 🏭", "Інгулецький 🌳", "Південний 🏗️"],
    "Вінниця ⛲": ["Замостя 🏢", "Вишенька 🍒", "Поділ 🌊", "Старе місто 🏛️", "Бригантина ⛴️", "Академічний 🎓", "Тяжилів 🏗️", "Слов’янка 🏘️"],
    "Миколаїв 🚢": ["Центральний 🏙️", "Заводський 🏗️", "Інгульський 🌊", "Корабельний ⚓", "Варварівка 🏘️", "Тернівка 🌳", "Соляні 🏠", "Матвіївка 🌲"],
    "Чернігів 🏰": ["Деснянський 🌳", "Новозаводський 🏛️", "Центр 🎡", "Лісковиця 🏘️", "Шерстянка 🏭", "Масани 🏗️", "Бобровиця 🏠", "Подусівка 🌲"],
    "Кам'янське 🛠️": ["Центральний 🏤", "Південний 🏗️", "Дніпровський 🌊", "Новокам’янка 🏠", "Победа 🏢", "Правобережний 🏘️", "Лівобережний 🌳", "Місто-центр 🏙️"]
}

VAPES = [
    {"id": 0, "name": "🍊 Packwoods Orange", "old": 1149.0, "img": "https://i.ibb.co/V03f2yYF/Ghost-Vape-1.jpg"},
    {"id": 1, "name": "🌸 Packwoods Pink", "old": 1259.0, "img": "https://i.ibb.co/65j1901/Ghost-Vape-2.jpg"},
    {"id": 2, "name": "🍇 Packwoods Purple", "old": 1369.0, "img": "https://i.ibb.co/svXqXPgL/Ghost-Vape-3.jpg"},
    {"id": 3, "name": "❄️ Whole Mint", "old": 1549.0, "img": "https://i.ibb.co/675LQrNB/Ghost-Vape-4.jpg"},
    {"id": 4, "name": "🌴 Jungle Boys", "old": 1659.0, "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg"}
]

NEW_TERMS = (
    "📜 *Умови, правила, відповідальність*\n\n"
    "1️⃣ Проєкт має навчально-демонстраційний характер.\n"
    "2️⃣ Інформація подається виключно з ознайомчою метою.\n"
    "3️⃣ Матеріали не є рекомендацією до придбання чи використання.\n"
    "4️⃣ Користувач самостійно несе відповідальність за свої дії.\n"
    "5️⃣ Адміністрація не зберігає персональні дані.\n"
    "6️⃣ Участь у взаємодії є добровільною.\n\n"
    "⚠️ *Важливо:*\n"
    "7️⃣ Магазин не є реальним та не здійснює продаж товарів.\n"
    "8️⃣ Жоден товар не буде доставлений.\n"
    "9️⃣ Усі переказані кошти вважаються добровільним подарунком.\n"
    "🔟 Всі грошові операції через менеджера — подарунок кодеру та розробнику Gho$$tyyy/"
)
# ================== KEYBOARDS ==================
def main_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👤 Мій профіль 💳", callback_data="profile")],
        [InlineKeyboardButton("🌿 ННС-Вейпи 💨", callback_data="catalog")],
        [InlineKeyboardButton("🏙 Обрати місто 📍", callback_data="cities")],
        [InlineKeyboardButton("💻 Менеджер 👨‍💻", url=MANAGER_URL)],
        [InlineKeyboardButton("📜 Політика ⚖️", callback_data="terms")],
    ])

# ================== HANDLERS ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if "promo" not in context.user_data:
        context.user_data["promo"] = f"GHOST-{random.randint(100,999)}PR"
        context.user_data["reg"] = datetime.now().strftime("%d.%m.%Y")

    text = (
        f"🌿 *Вітаємо, {user.first_name}!* 🌿\n\n"
        f"🎫 Промокод: `{context.user_data['promo']}`\n"
        f"📅 Діє до: {PROMO_EXPIRY}\n\n"
        f"⬇️ Оберіть дію:"
    )

    await update.message.reply_photo(
        WELCOME_PHOTO,
        caption=text,
        parse_mode="Markdown",
        reply_markup=main_kb()
    )

async def callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data
    ud = context.user_data

    async def render(text, kb):
        await q.message.edit_caption(
            caption=text,
            parse_mode="Markdown",
            reply_markup=kb
        )

    if data == "catalog":
        btns = []
        for v in VAPES:
            price = round(v["old"] * DISCOUNT_RATE)
            btns.append([
                InlineKeyboardButton(
                    f"{v['name']} | {price}₴",
                    callback_data=f"v_{v['id']}"
                )
            ])
        btns.append([InlineKeyboardButton("⬅️ Назад", callback_data="home")])
        await render("🔥 *Каталог (-35%):*", InlineKeyboardMarkup(btns))

    elif data.startswith("v_"):
        v = VAPES[int(data.split("_")[1])]
        price = round(v["old"] * DISCOUNT_RATE)
        await render(
            f"*{v['name']}*\n"
            f"❌ {v['old']}₴\n"
            f"✅ {price}₴\n"
            f"📍 {ud.get('city','Місто не обрано')}, {ud.get('district','')}",
            InlineKeyboardMarkup([
                [InlineKeyboardButton("🛍 Замовити", url=MANAGER_URL)],
                [InlineKeyboardButton("⬅️ Назад", callback_data="catalog")]
            ])
        )

    elif data == "cities":
        btns = [[InlineKeyboardButton(c, callback_data=f"c_{c}")] for c in LOCATIONS]
        btns.append([InlineKeyboardButton("⬅️ Назад", callback_data="home")])
        await render("🏙 *Оберіть місто:*", InlineKeyboardMarkup(btns))

    elif data.startswith("c_"):
        city = data[2:]
        ud["city"] = city
        btns = [[InlineKeyboardButton(d, callback_data=f"d_{d}")] for d in LOCATIONS[city]]
        await render(f"🏘 *{city}* — район:", InlineKeyboardMarkup(btns))

    elif data.startswith("d_"):
        ud["district"] = data[2:]
        await render("✅ *Локацію збережено!*", main_kb())

    elif data == "profile":
        await render(
            f"👤 *Профіль*\n"
            f"🆔 `{q.from_user.id}`\n"
            f"🎫 `{ud.get('promo')}`\n"
            f"📍 {ud.get('city','—')} {ud.get('district','')}",
            InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="home")]])
        )

    elif data == "terms":
        await render(TERMS, InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="home")]]))

    elif data == "home":
        await render("🏠 *Головне меню*", main_kb())

# ================== RUN ==================
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callbacks))
    print("✅ BOT ONLINE")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()

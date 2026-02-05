import logging
import random
import urllib.parse
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
TOKEN = "8351638507:AAEOSgiUsQHk2DtI2aurKqGhoS5-JPLqf-g"  # <--- ВСТАВ СЮДИ ТОКЕН
MANAGER_USERNAME = "ghosstydp"
CHANNEL_URL = "https://t.me/GhostyStaffDP"
WELCOME_PHOTO = "https://i.ibb.co/y7Q194N/1770068775663.png" # Твоє фото
DEFAULT_AVATAR = "https://i.ibb.co/y7Q194N/1770068775663.png" # Заглушка, якщо немає фото профілю

PROMO_EXPIRY = "25.03.2026"
DISCOUNT_PERCENT = 45
DISCOUNT_MULT = 0.55  # Ціна * 0.55 = ціна зі знижкою 45%

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ================== DATA ==================
LOCATIONS = {
    "🏙️ Київ": ["🏛️ Печерський", "🎡 Оболонський", "🏗️ Дарницький", "🌳 Деснянський", "🛤️ Святошинський", "🌲 Голосіївський", "🎓 Шевченківський", "✈️ Солом’янський"],
    "🏗️ Харків": ["🏢 Салтівка", "🏛️ Центр", "🏔️ Холодна Гора", "🏟️ Слобідський", "🏭 Індустріальний", "🛠️ ХТЗ", "🏗️ Олексіївка", "🏤 Московський"],
    "⚓ Одеса": ["🌊 Приморський", "🚜 Суворовський", "🍷 Малиновський", "🏖️ Київський", "🏢 Таїрово", "🏠 Черемушки", "🏥 Слобідка", "🏘️ Млини"],
    "🌊 Дніпро": ["🏙️ Центр", "🎡 Перемога", "🌳 Тополя", "🛍️ Лівобережний-3 (ТЦ Караван)", "🌉 Амур-Нижньодніпровський", "🏗️ Чечелівський", "🏢 Шевченківський", "🏭 Новокодацький"],
    "🦁 Львів": ["🏰 Галицький", "🚂 Залізничний", "🎨 Франківський", "🌳 Шевченківський", "🏢 Сихівський", "⛲ Личаківський", "🏘️ Рясне", "🌲 Брюховичі"],
    "⚡ Запоріжжя": ["🔋 Дніпровський", "🌳 Вознесенівський", "🏛️ Олександрівський", "🏘️ Комунарський", "🐎 Хортицький", "🏢 Шевченківський", "🏭 Заводський", "🌅 Південний"],
    "🔩 Кривий Ріг": ["🏙️ Центральний", "⛏️ Тернівський", "🏛️ Покровський", "🎡 Саксаганський", "🚂 Довгинцівський", "🏭 Металургійний", "🌳 Інгулецький", "🏗️ Південний"],
    "⛲ Вінниця": ["🏢 Замостя", "🍒 Вишенька", "🌊 Поділ", "🏛️ Старе місто", "🎓 Академічний", "🏗️ Тяжилів", "🏘️ Слов’янка", "🇰🇷 Корея"],
    "🚢 Миколаїв": ["🏙️ Центральний", "🏗️ Заводський", "🌊 Інгульський", "⚓ Корабельний", "🏘️ Варварівка", "🌳 Тернівка", "🌲 Матвіївка", "🏠 Соляні"],
    "🛠️ Кам'янське": ["🏤 Центральний", "🏗️ Південний", "🌊 Дніпровський", "🏠 Новокам’янка", "🏢 Победа", "🏘️ Правобережний", "🌳 Лівобережний", "🏙️ Соцмісто"]
}

VAPES = [
    {
        "id": 0,
        "name": "🍊 Packwoods Orange",
        "mg": "1000mg",
        "type": "Гібрид",
        "content": "90% ННС",
        "old_price": 499, 
        "desc": "Соковитий цитрусовий вибух. Ідеальний баланс для творчості та релаксу.",
        "img": "https://i.ibb.co/V03f2yYF/Ghost-Vape-1.jpg"
    },
    {
        "id": 1,
        "name": "🌸 Packwoods Pink",
        "mg": "1000mg",
        "type": "Гібрид",
        "content": "90% ННС",
        "old_price": 579,
        "desc": "Солодкий ягідний аромат з квітковими нотками. М'який ефект ейфорії.",
        "img": "https://i.ibb.co/65j1901/Ghost-Vape-2.jpg"
    },
    {
        "id": 2,
        "name": "🍇 Packwoods Purple",
        "mg": "1000mg",
        "type": "Гібрид",
        "content": "90% ННС",
        "old_price": 689,
        "desc": "Глибокий виноградний смак. Потужний розслаблюючий ефект для вечора.",
        "img": "https://i.ibb.co/svXqXPgL/Ghost-Vape-3.jpg"
    },
    {
        "id": 3,
        "name": "❄️ Whole Mint",
        "mg": "2000mg",
        "type": "Сатіва",
        "content": "95% ННС",
        "old_price": 777,
        "desc": "Освіжаюча м'ята. Чиста енергія та фокус, ідеально для активного дня.",
        "img": "https://i.ibb.co/675LQrNB/Ghost-Vape-4.jpg"
    },
    {
        "id": 4,
        "name": "🌴 Jungle Boys White",
        "mg": "2000mg",
        "type": "Індика",
        "content": "95% ННС",
        "old_price": 859,
        "desc": "Тропічна міць. Глибокий стоун ефект, максимальне розслаблення тіла.",
        "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg"
    }
]

# ================== HELPERS ==================
def get_main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👤 Мій Профіль", callback_data="profile")],
        [InlineKeyboardButton("💨 Каталог ННС-Вейпів", callback_data="catalog")],
        [InlineKeyboardButton("📍 Обрати Місто/Район", callback_data="cities")],
        [InlineKeyboardButton("👻 Канал Ghosstyyy", url=CHANNEL_URL)],
        [InlineKeyboardButton("👨‍💻 Зв'язок з Менеджером", url=f"https://t.me/{MANAGER_USERNAME}")]
    ])

def generate_manager_link(user, promo, city, district, items="Не обрано"):
    text = (
        f"Привіт! 👋\n"
        f"Я хочу зробити замовлення.\n"
        f"👤 ID: {user.id}\n"
        f"🎫 Промокод: {promo}\n"
        f"📍 Місто: {city}\n"
        f"🏘 Район: {district}\n"
        f"🛒 Товар: {items}"
    )
    encoded = urllib.parse.quote(text)
    return f"https://t.me/{MANAGER_USERNAME}?text={encoded}"

# ================== HANDLERS ==================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # Генерація промокоду
    if "promo" not in context.user_data:
        context.user_data["promo"] = f"GHOST-{random.randint(1000,9999)}"
        context.user_data["reg_date"] = datetime.now().strftime("%d.%m.%Y")
    
    # Довгий привітальний текст (~120 слів)
    welcome_text = (
        f"👋 *Йо, {user.first_name}! Вітаємо в Ghosty Shop!* 👻💨\n\n"
        f"Ти потрапив у найкращий шоп одноразових ННС-вейпів в Україні! Ми тут не для того, щоб просто продати, "
        f"а щоб подарувати тобі справжній релакс та нові враження. 🌌\n\n"
        f"🚀 *Чому ми?*\n"
        f"Ми працюємо швидко, якісно і завжди на зв'язку. Твій комфорт — наш пріоритет. У нас ти знайдеш топові "
        f"американські бренди Packwoods, Jungle Boys та інші з найчистішим дистилятом.\n\n"
        f"🎁 *Твій Бонус:*\n"
        f"Спеціально для тебе ми підготували *ПЕРСОНАЛЬНИЙ ПРОМОКОД* на шалену знижку *-45%*! "
        f"Він діє на твоє перше замовлення, тож не прогав шанс спробувати преміум якість за смішною ціною.\n\n"
        f"👇 *Що далі?*\n"
        f"Тисни кнопки внизу, обирай своє місто, чекай свій стафф і насолоджуйся життям на повну! "
        f"Ми вже готові прийняти твоє замовлення. Погнали! 🔥"
    )

    await update.message.reply_photo(
        photo=WELCOME_PHOTO,
        caption=welcome_text,
        parse_mode="Markdown",
        reply_markup=get_main_keyboard()
    )

async def callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    user = q.from_user
    ud = context.user_data
    data = q.data

    # Функція для редагування повідомлення
    async def edit(caption, photo=None, kb=None):
        media = InputMediaPhoto(media=photo, caption=caption, parse_mode="Markdown") if photo else None
        if media:
            try:
                await q.message.edit_media(media=media, reply_markup=kb)
            except Exception:
                # Якщо фото те саме, просто редагуємо текст (щоб не було помилок API)
                 await q.message.edit_caption(caption=caption, parse_mode="Markdown", reply_markup=kb)
        else:
             await q.message.edit_caption(caption=caption, parse_mode="Markdown", reply_markup=kb)

    # --- ГОЛОВНЕ МЕНЮ ---
    if data == "main_menu":
        await edit(
            caption=f"🏠 *Головне меню*\nОбирай, куди попрямуємо далі! 👇",
            photo=WELCOME_PHOTO,
            kb=get_main_keyboard()
        )

    # --- ПРОФІЛЬ ---
    elif data == "profile":
        # Спроба отримати фото профілю
        profile_photo = DEFAULT_AVATAR
        photos = await user.get_profile_photos(limit=1)
        if photos and photos.total_count > 0:
            profile_photo = photos.photos[0][-1].file_id

        city = ud.get("city", "Не обрано ❌")
        dist = ud.get("dist", "Не обрано ❌")
        promo = ud.get("promo", "ERROR")
        
        share_link = generate_manager_link(user, promo, city, dist)

        caption = (
            f"👤 *ТВІЙ ПРОФІЛЬ*\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📸 *Користувач:* {user.first_name}\n"
            f"🔗 *Юзернейм:* @{user.username if user.username else 'Приховано'}\n"
            f"🆔 *ID:* `{user.id}` (тисни щоб скопіювати)\n\n"
            f"🎫 *Твій Промокод:* `{promo}`\n"
            f"📉 *Знижка:* -45% на перше замовлення\n"
            f"⏳ *Діє до:* {PROMO_EXPIRY}\n\n"
            f"📍 *Локація:* {city}\n"
            f"🏘 *Район:* {dist}\n"
            f"━━━━━━━━━━━━━━━━━━"
        )
        
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("📤 Надіслати дані Менеджеру", url=share_link)],
            [InlineKeyboardButton("📍 Змінити Місто", callback_data="cities")],
            [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]
        ])
        
        await edit(caption, photo=profile_photo, kb=kb)

    # --- КАТАЛОГ ---
    elif data == "catalog":
        buttons = []
        for v in VAPES:
            # Розрахунок ціни
            price = int(v["old_price"] * DISCOUNT_MULT)
            btn_text = f"{v['name']} | {price}₴"
            buttons.append([InlineKeyboardButton(btn_text, callback_data=f"prod_{v['id']}")])
        
        buttons.append([InlineKeyboardButton("🔙 Назад", callback_data="main_menu")])
        
        await edit(
            caption="💨 *Обери свій смак:*\nВсі позиції в наявності. Тисни для деталей!",
            photo=WELCOME_PHOTO, # Можна поставити загальне фото каталогу
            kb=InlineKeyboardMarkup(buttons)
        )

    # --- ТОВАР ДЕТАЛЬНО ---
    elif data.startswith("prod_"):
        v_id = int(data.split("_")[1])
        v = VAPES[v_id]
        new_price = int(v["old_price"] * DISCOUNT_MULT)
        
        city_status = ud.get("city", "❌ Не обрано")
        
        caption = (
            f"*{v['name']}*\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🧬 *Тип:* {v['type']}\n"
            f"🧪 *Вміст:* {v['content']} ({v['mg']})\n"
            f"📝 *Опис:* {v['desc']}\n\n"
            f"❌ Стара ціна: ~{v['old_price']} грн~\n"
            f"✅ *Ціна (-45%): {new_price} грн*\n\n"
            f"🎫 Промокод: `{ud.get('promo')}`\n"
            f"📍 Твоє місто: {city_status}\n"
        )
        
        # Логіка кнопок
        btns = []
        if "city" not in ud:
            btns.append([InlineKeyboardButton("📍 Спочатку обери місто", callback_data="cities")])
        else:
            # Генеруємо лінк на оплату/замовлення цього товару
            buy_link = generate_manager_link(user, ud['promo'], ud['city'], ud.get('dist', 'Не обрано'), v['name'])
            btns.append([InlineKeyboardButton("🛒 ЗАМОВИТИ", url=buy_link)])
            
        btns.append([InlineKeyboardButton("🔙 До списку", callback_data="catalog")])
        
        await edit(caption, photo=v["img"], kb=InlineKeyboardMarkup(btns))

    # --- МІСТА ---
    elif data == "cities":
        user_city = ud.get("city")
        kb_buttons = []
        
        # Генерація кнопок з галочками
        temp_row = []
        for i, city_name in enumerate(LOCATIONS.keys()):
            mark = "✅ " if city_name == user_city else ""
            btn = InlineKeyboardButton(f"{mark}{city_name}", callback_data=f"setcity_{city_name}")
            temp_row.append(btn)
            if len(temp_row) == 2: # По 2 міста в ряд
                kb_buttons.append(temp_row)
                temp_row = []
        if temp_row:
            kb_buttons.append(temp_row)
            
        kb_buttons.append([InlineKeyboardButton("🔙 Назад", callback_data="main_menu")])
        
        await edit(
            caption="📍 *Оберіть ваше місто:*\nНатисніть на назву міста, щоб обрати.",
            photo=WELCOME_PHOTO,
            kb=InlineKeyboardMarkup(kb_buttons)
        )

    # --- РАЙОНИ ---
    elif data.startswith("setcity_"):
        selected_city = data.split("_")[1]
        ud["city"] = selected_city # Зберігаємо вибір
        
        # Перехід до районів
        user_dist = ud.get("dist")
        districts = LOCATIONS[selected_city]
        
        kb_buttons = []
        for d in districts:
            mark = "✅ " if d == user_dist else ""
            kb_buttons.append([InlineKeyboardButton(f"{mark}{d}", callback_data=f"setdist_{d}")])
            
        kb_buttons.append([InlineKeyboardButton("🔙 Назад до міст", callback_data="cities")])
        
        await edit(
            caption=f"🏙 *Місто: {selected_city}*\nТепер оберіть зручний район для отримання:",
            photo=WELCOME_PHOTO,
            kb=InlineKeyboardMarkup(kb_buttons)
        )

    # --- ФІНАЛІЗАЦІЯ ВИБОРУ ---
    elif data.startswith("setdist_"):
        selected_dist = data.split("_")[1]
        ud["dist"] = selected_dist
        
        await edit(
            caption=f"✅ *Локацію збережено!*\n\n📍 Місто: {ud['city']}\n🏘 Район: {ud['dist']}\n\nТепер можна переходити до замовлення.",
            photo=WELCOME_PHOTO,
            kb=InlineKeyboardMarkup([
                [InlineKeyboardButton("💨 До каталогу", callback_data="catalog")],
                [InlineKeyboardButton("👤 У профіль", callback_data="profile")]
            ])
        )

# ================== RUN ==================
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callbacks))
    
    print("Бот запущено...")
    app.run_polling(drop_pending_updates=True)


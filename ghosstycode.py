import logging
import random
import urllib.parse
from collections import Counter
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

# ================== КОНФІГУРАЦІЯ / CONFIG ==================
TOKEN = "8351638507:AAEOSgiUsQHk2DtI2aurKqGhoS5-JPLqf-g"
MANAGER_USERNAME = "ghosstydp"
CHANNEL_URL = "https://t.me/GhostyStaffDP"

WELCOME_PHOTO = "https://i.ibb.co/y7Q194N/1770068775663.png"
CART_PHOTO = "https://cdn-icons-png.flaticon.com/512/3081/3081840.png"

DISCOUNT_PERCENT = 35
DISCOUNT_MULT = 0.65 # Коефіцієнт для розрахунку ціни (100% - 35% = 65%)

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# ================== БАЗА ДАНИХ ТОВАРІВ / PRODUCTS ==================
PRODUCTS = {
    # --- ННС ВЕЙПИ (HHC) ---
    100: {"name": "🍊 Packwoods Orange", "cat": "hhc", "price": 499, "img": "https://i.ibb.co/V03f2yYF/Ghost-Vape-1.jpg", "variants": ["1000mg"], 
          "desc": "✨ Ефект: Глибоке розслаблення тіла, легка ейфорія та творчий підйом. Ідеально для вечора.\n🔋 Склад: 90% ННС дистилят."},
    101: {"name": "🌸 Packwoods Pink", "cat": "hhc", "price": 579, "img": "https://i.ibb.co/65j1901/Ghost-Vape-2.jpg", "variants": ["1000mg"],
          "desc": "✨ Ефект: М'який соціальний ефект, знімає тривогу, покращує настрій.\n🌸 Смак: Солодка полуниця з вершками."},
    102: {"name": "🍇 Packwoods Purple", "cat": "hhc", "price": 689, "img": "https://i.ibb.co/DHXXSh2d/Ghost-Vape-3.jpg", "variants": ["1000mg"],
          "desc": "✨ Ефект: Потужний 'стоун', заспокоює думки, допомагає при безсонні.\n🍇 Смак: Насичений виноград."},
    103: {"name": "❄️ Whole Mint", "cat": "hhc", "price": 777, "img": "https://i.ibb.co/675LQrNB/Ghost-Vape-4.jpg", "variants": ["2000mg"],
          "desc": "✨ Ефект: Бадьорість та фокус. Сатіва-домінант. Енергія на весь день.\n❄️ Смак: Крижана м'ята."},
    104: {"name": "🌴 Jungle Boys White", "cat": "hhc", "price": 859, "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg", "variants": ["2000mg"],
          "desc": "✨ Ефект: Максимальна сила. Поєднання ейфорії та повного фізичного релаксу.\n🌴 Смак: Тропічні фрукти."},

    # --- ПОД-СИСТЕМИ (PODS) ---
    200: {"name": "⚡ Vaporesso XROS 4", "cat": "pod", "price": 699, "img": "https://vandalvape.life/image/cache/catalog/pod/vaporesso/xros%204/Vaporesso-Xros-4-Black-1000x1000.webp", "variants": ["Black", "Purple", "Blue"], 
          "desc": "⚙️ Хар-ки: Акумулятор 1000mAh, 3 режими потужності, алюмінієвий корпус. Найкращий вибір 2024!"},
    201: {"name": "🚀 Vaporesso XROS 5", "cat": "pod", "price": 799, "img": "https://vandalvape.life/image/cache/catalog/pod/vaporesso/xros%204/Vaporesso-Xros-4-Black-1000x1000.webp", "variants": ["Black", "Pink", "Blue"],
          "desc": "⚙️ Хар-ки: Нова серія. Покращений обдув, сумісність з усіма картриджами XROS, швидка зарядка Type-C."},
    202: {"name": "🧊 XROS 4 Nano", "cat": "pod", "price": 719, "img": "https://vandalvape.life/image/cache/catalog/pod/vaporesso/xros%204%20nano/Xros-4-Nano-Twilight-Purple-1000x1000.webp", "variants": ["Black", "Blue", "Silver"],
          "desc": "⚙️ Хар-ки: Компактний квадратний дизайн, великий екран, регулювання тугості затяжки."},
    203: {"name": "💎 XROS Pro", "cat": "pod", "price": 929, "img": "https://vandalvape.life/image/cache/catalog/pod/vaporesso/xros%20pro/Vaporesso-XROS-PRO-Black-1000x1000.webp", "variants": ["Pink", "Black", "Red"],
          "desc": "⚙️ Хар-ки: Преміум версія. Потужність до 30W, окрема кнопка блокування, супер-смакопередача."},
    204: {"name": "🔥 Vmate Mini", "cat": "pod", "price": 570, "img": "https://vandalvape.life/image/cache/catalog/pod/voopoo/vmate%20e/VooPoo-VMATE-E-Classic-Black-1000x1000.webp", "variants": ["Black", "Pink", "Red"],
          "desc": "⚙️ Хар-ки: Легкий та компактний, автоматична затяжка, ідеально для сольового нікотину."},

    # --- РІДИНИ (LIQUIDS) ---
    300: {"name": "🍋 Chaser Balance", "cat": "liquid", "price": 229, "img": "https://vandalvape.life/image/cache/catalog//premix/Chaser%20Lux%2030/newfoto/VitaminVV-1000x1000.webp", "variants": ["50mg (30ml)", "65mg (30ml)"],
          "desc": "🍋 Смак: Енергетик (Energetic). Насичений кислий смак з бульбашками."},
    301: {"name": "🍓 Chaser Berry Lemon", "cat": "liquid", "price": 229, "img": "https://vandalvape.life/image/cache/catalog/premix/Chaser%20Lux%2030/newfoto/BerryLemonVV-1000x1000.webp", "variants": ["50mg (30ml)", "65mg (30ml)"],
          "desc": "🍓 Смак: Ягідний лимонад. Солодка малина з лимонною кислинкою."},
}

# ================== ЛОКАЦІЇ / LOCATIONS ==================
LOCATIONS = {
    "🏙️ Київ": ["🏛️ Печерський", "🎡 Оболонський", "🏗️ Дарницький", "🌳 Деснянський", "🛤️ Святошинський", "🌲 Голосіївський", "🎓 Шевченківський", "✈️ Солом’янський"],
    "🏗️ Харків": ["🏢 Салтівка", "🏛️ Центр", "🏔️ Холодна Гора", "🏟️ Слобідський", "🏭 Індустріальний", "🛠️ ХТЗ", "🏗️ Олексіївка", "🏤 Московський"],
    "⚓ Одеса": ["🌊 Приморський", "🚜 Суворовський", "🍷 Малиновський", "🏖️ Київський", "🏢 Таїрово", "🏠 Черемушки", "🏥 Слобідка", "🏘️ Млини"],
    "🌊 Дніпро": ["🛍️ Лівобережний-3 (Караван)", "🏙️ Центр", "🎡 Перемога", "🌳 Тополя", "🌉 Амур", "🏗️ Чечелівський", "🏢 Шевченківський", "🏭 Новокодацький"],
    "🦁 Львів": ["🏰 Галицький", "🚂 Залізничний", "🎨 Франківський", "🌳 Шевченківський", "🏢 Сихівський", "⛲ Личаківський", "🏘️ Рясне", "🌲 Брюховичі"],
    "⚡ Запоріжжя": ["🔋 Дніпровський", "🌳 Вознесенівський", "🏛️ Олександрівський", "🏘️ Комунарський", "🐎 Хортицький", "🏢 Шевченківський", "🏭 Заводський", "🌅 Південний"],
    "🔩 Кривий Ріг": ["🏙️ Центральний", "⛏️ Тернівський", "🏛️ Покровський", "🎡 Саксаганський", "🚂 Довгинцівський", "🏭 Металургійний", "🌳 Інгулецький", "🏗️ Південний"],
    "⛲ Вінниця": ["🏢 Замостя", "🍒 Вишенька", "🌊 Поділ", "🏛️ Старе місто", "🎓 Академічний", "🏗️ Тяжилів", "🏘️ Слов’янка", "🇰🇷 Корея"],
    "🚢 Миколаїв": ["🏙️ Центральний", "🏗️ Заводський", "🌊 Інгульський", "⚓ Корабельний", "🏘️ Варварівка", "🌳 Тернівка", "🌲 Матвіївка", "🏠 Соляні"],
    "🛠️ Кам'янське": ["🏤 Центральний", "🏗️ Південний", "🌊 Дніпровський", "🏠 Новокам’янка", "🏢 Победа", "🏘️ Правобережний", "🌳 Лівобережний", "🏙️ Соцмісто"]
}

# ================== КЛАВІАТУРИ / KEYBOARDS ==================

def get_main_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👤 Мій Профіль", callback_data="profile"), InlineKeyboardButton("📦 Асортимент", callback_data="assortment")],
        [InlineKeyboardButton("🌿 ННС-Вейпи", callback_data="list_hhc"), InlineKeyboardButton("🔋 Поди", callback_data="list_pod"), InlineKeyboardButton("💧 Рідини", callback_data="list_liquid")],
        [InlineKeyboardButton("📍 Обрати Місто/Район", callback_data="sel_city_menu")],
        [InlineKeyboardButton("📜 Політика", callback_data="policy")],
        [InlineKeyboardButton("👨‍💻 Менеджер", url=f"https://t.me/{MANAGER_USERNAME}"), InlineKeyboardButton("👻 Канал", url=CHANNEL_URL)]
    ])

# ================== ОСНОВНІ ФУНКЦІЇ / HANDLERS ==================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if "promo" not in context.user_data:
        context.user_data.update({
            "promo": f"GHST-{random.randint(1000,9999)}",
            "cart": [], "promo_active": False,
            "location": {"city": None, "dist": None}
        })
    
    welcome_text = (
        f"👋 *Вітаємо в Ghosty Shop, {user.first_name}!* 👻\n\n"
        f"Шукаєш якість за адекватні гроші? Ти в правильному місці! Ми пропонуємо найнижчі ціни та найкращий стафф в Україні. "
        f"Наш асортимент включає лише перевірені бренди США та Європи. Швидка доставка та повна анонімність гарантовані. "
        f"Твій комфорт — наш пріоритет! Погнали до вибору! 🔥\n\n"
        f"🎁 *Твій Промокод:* `{context.user_data['promo']}`\n"
        f"(-35% на все + рідина у подарунок!)"
    )
    await update.message.reply_photo(photo=WELCOME_PHOTO, caption=welcome_text, parse_mode="Markdown", reply_markup=get_main_kb())

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ud = context.user_data
    state = ud.get("input_state")
    text = update.message.text.strip()

    if state == "wait_promo":
        if text == ud.get("promo"):
            ud["promo_active"] = True
            ud["input_state"] = None
            await update.message.reply_text("✅ *Промокод застосовано!* Всі ціни в кошику знижено на 35%.", parse_mode="Markdown")
            await show_cart(update, context, new_msg=True)
        else:
            await update.message.reply_text("❌ Невірний код. Скопіюйте код з профілю та відправте ще раз.")
    
    elif state == "wait_name":
        ud["order_name"] = text
        ud["input_state"] = "wait_phone"
        await update.message.reply_text("📱 Тепер введіть ваш номер телефону:")
    
    elif state == "wait_phone":
        ud["order_phone"] = text
        ud["input_state"] = "wait_post"
        await update.message.reply_text("📦 Номер відділення або поштомату Нової Пошти:")
    
    elif state == "wait_post":
        ud["order_post"] = text
        ud["input_state"] = None
        await finalize_order(update, context)

# ================== ЛОГІКА КОШИКА / CART LOGIC ==================

async def show_cart(update: Update, context: ContextTypes.DEFAULT_TYPE, new_msg=False):
    ud = context.user_data
    cart = ud.get("cart", [])
    if not cart:
        text = "🛒 *Ваш кошик порожній.*"
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 До товарів", callback_data="assortment")]])
    else:
        counts = Counter([f"{i['name']} ({i['variant']})" for i in cart])
        raw_sum = sum(i['price'] for i in cart)
        final_sum = int(raw_sum * DISCOUNT_MULT) if ud.get("promo_active") else raw_sum
        
        text = "🛒 *ВАШ КОШИК:*\n━━━━━━━━━━━━━━━━━━\n"
        for item, count in counts.items():
            text += f"▫️ {item} x{count}\n"
        
        text += f"━━━━━━━━━━━━━━━━━━\n💰 Разом: *{final_sum} грн*\n"
        if ud.get("promo_active"):
            text += "🎫 Промокод: `-35% Активовано` ✅\n"
        else:
            text += f"🎫 Промокод: `НЕМАЄ` (Введіть `{ud['promo']}`)\n"
        text += "🎁 Бонус: *Рідина у подарунок!* 💧"
        
        kb_btns = []
        if not ud.get("promo_active"):
            kb_btns.append([InlineKeyboardButton("🎟 Застосувати промокод", callback_data="enter_promo")])
        kb_btns.append([InlineKeyboardButton("✅ Оформити замовлення", callback_data="checkout_start")])
        kb_btns.append([InlineKeyboardButton("🗑 Очистити", callback_data="clear_cart"), InlineKeyboardButton("🔙 Назад", callback_data="main_menu")])
        kb = InlineKeyboardMarkup(kb_btns)

    if new_msg: await update.message.reply_photo(photo=CART_PHOTO, caption=text, parse_mode="Markdown", reply_markup=kb)
    else: await update.callback_query.message.edit_media(media=InputMediaPhoto(media=CART_PHOTO, caption=text, parse_mode="Markdown"), reply_markup=kb)

# ================== КОЛБЕКИ / CALLBACKS ==================

async def callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    ud = context.user_data
    data = q.data

    # --- Навігація ---
    if data == "main_menu":
        await q.message.edit_media(media=InputMediaPhoto(media=WELCOME_PHOTO, caption="🏠 *Головне меню*", parse_mode="Markdown"), reply_markup=get_main_kb())
    
    elif data == "assortment":
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🌿 ННС-Вейпи", callback_data="list_hhc")],
            [InlineKeyboardButton("🔋 Под-Системи", callback_data="list_pod")],
            [InlineKeyboardButton("💧 Рідини", callback_data="list_liquid")],
            [InlineKeyboardButton("🛒 Мій кошик", callback_data="open_cart")],
            [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]
        ])
        await q.message.edit_caption(caption="📦 *Оберіть категорію товару:*", reply_markup=kb)

    elif data.startswith("list_"):
        cat = data.split("_")[1]
        btns = []
        for pid, p in PRODUCTS.items():
            if p["cat"] == cat:
                # Показуємо одразу ціну зі знижкою якщо промо активне
                disp_price = int(p['price'] * DISCOUNT_MULT) if ud.get("promo_active") else p['price']
                btns.append([InlineKeyboardButton(f"{p['name']} | {disp_price}₴", callback_data=f"prod_{pid}")])
        btns.append([InlineKeyboardButton("🔙 Назад", callback_data="assortment")])
        await q.message.edit_caption(caption="⬇️ *Оберіть товар для перегляду:*", reply_markup=InlineKeyboardMarkup(btns))

    elif data.startswith("prod_"):
        pid = int(data.split("_")[1])
        p = PRODUCTS[pid]
        p_active = ud.get("promo_active")
        price_text = f"❌ ~{p['price']} грн~\n✅ *{int(p['price']*DISCOUNT_MULT)} грн*" if p_active else f"💰 *{p['price']} грн*"
        
        caption = (
            f"🏷 *{p['name']}*\n━━━━━━━━━━━━━━━━━━\n"
            f"{p['desc']}\n\n"
            f"{price_text}\n"
            f"🎁 *Подарунок: Рідина 30мл на вибір!*\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🎫 Твій промо: `{ud['promo']}`\n"
            f"📍 Твоя локація: {ud['location']['city'] or 'Не обрано'}, {ud['location']['dist'] or '❌'}"
        )
        btns = [[InlineKeyboardButton(f"➕ Додати {v}", callback_data=f"add_{pid}_{v}")] for v in p["variants"]]
        btns.append([InlineKeyboardButton("🛒 Кошик", callback_data="open_cart"), InlineKeyboardButton("🔙 Назад", callback_data=f"list_{p['cat']}")])
        await q.message.edit_media(media=InputMediaPhoto(media=p["img"], caption=caption, parse_mode="Markdown"), reply_markup=InlineKeyboardMarkup(btns))

    # --- Кошик та промо ---
    elif data.startswith("add_"):
        pid, var = int(data.split("_")[1]), data.split("_")[2]
        p = PRODUCTS[pid]
        ud["cart"].append({"name": p["name"], "variant": var, "price": p["price"]})
        await q.answer(f"✅ {p['name']} додано!")

    elif data == "open_cart": await show_cart(update, context)
    elif data == "clear_cart":
        ud["cart"] = []; ud["promo_active"] = False
        await q.answer("🗑 Очищено"); await show_cart(update, context)
    elif data == "enter_promo":
        ud["input_state"] = "wait_promo"
        await q.message.reply_text("🎫 *Вставте скопійований промокод:*")

    # --- Оформлення замовлення ---
    elif data == "checkout_start":
        if not ud.get("cart"): await q.answer("Кошик порожній!", show_alert=True); return
        ud["input_state"] = "wait_name"
        await q.message.reply_text("📝 *Починаємо оформлення!*\nВведіть Прізвище та Ім'я:")

    # --- Локація та Профіль ---
    elif data == "profile":
        loc = ud["location"]
        txt = (f"👤 *ТВІЙ ПРОФІЛЬ*\n━━━━━━━━━━━━━━━━━━\n🆔 ID: `{q.from_user.id}`\n🎫 Промо: `{ud['promo']}`\n"
               f"📍 Місто: {loc['city'] or '❌'}\n🏘 Район: {loc['dist'] or '❌'}\n━━━━━━━━━━━━━━━━━━")
        await q.message.edit_caption(caption=txt, parse_mode="Markdown", reply_markup=get_main_kb())

    elif data == "sel_city_menu":
        btns = [[InlineKeyboardButton(c, callback_data=f"setcity_{c}")] for c in LOCATIONS.keys()]
        btns.append([InlineKeyboardButton("🔙 Назад", callback_data="main_menu")])
        await q.message.edit_caption(caption="📍 *Обери своє місто:*", reply_markup=InlineKeyboardMarkup(btns))

    elif data.startswith("setcity_"):
        city = data.split("_")[1]; ud["location"]["city"] = city
        btns = [[InlineKeyboardButton(d, callback_data=f"setdist_{d}")] for d in LOCATIONS[city]]
        await q.message.edit_caption(caption=f"🏙 *Місто {city}*\nТепер обери район:", reply_markup=InlineKeyboardMarkup(btns))

    elif data.startswith("setdist_"):
        ud["location"]["dist"] = data.split("_")[1]
        await q.answer("✅ Локацію збережено!"); await q.message.edit_caption(caption="✅ *Локацію оновлено в профілі!*", reply_markup=get_main_kb())

    elif data == "policy":
        txt = ("📜 *Політика користувача*\n━━━━━━━━━━━━━━━━━━\n- Замовлення оброблюються та відправляються по всім містам України *ЦІЛОДОБОВО*.\n"
               "- Тільки 18+.\n- Анонімна упаковка.\n- Оплата при отриманні або на карту.")
        await q.message.edit_caption(caption=txt, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]]))

# ================== ФІНАЛІЗАЦІЯ ЗАМОВЛЕННЯ / ORDER ==================

async def finalize_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ud = context.user_data
    cart = ud["cart"]
    promo_act = ud.get("promo_active")
    total = int(sum(i['price'] for i in cart) * (DISCOUNT_MULT if promo_act else 1))
    
    items_str = "\n".join([f"• {i['name']} ({i['variant']})" for i in cart])
    order_id = f"GHST#{update.effective_user.id}-{random.randint(10,99)}"
    
    manager_msg = (
        f"🆕 *НОВЕ ЗАМОВЛЕННЯ {order_id}*\n"
        f"👤 Клієнт: {ud['order_name']}\n"
        f"📞 Тел: {ud['order_phone']}\n"
        f"📍 Локація: {ud['location']['city']}, {ud['location']['dist']}\n"
        f"📦 Пошта: {ud['order_post']}\n\n"
        f"🛒 *ТОВАРИ:*\n{items_str}\n"
        f"💰 Сума: {total} грн\n"
        f"🎫 Промокод: {'ТАК' if promo_act else 'НІ'}\n"
        f"🎁 Подарунок: Рідина 30мл"
    )
    
    link = f"https://t.me/{MANAGER_USERNAME}?text={urllib.parse.quote(manager_msg)}"
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("✈️ НАДІСЛАТИ МЕНЕДЖЕРУ", url=link)], [InlineKeyboardButton("🔙 В головне меню", callback_data="main_menu")]])
    
    await update.message.reply_text(f"✅ *Замовлення {order_id} готове!*\nНатисніть кнопку нижче, щоб передати дані менеджеру.", parse_mode="Markdown", reply_markup=kb)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callbacks))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text))
    print("🤖 Бот Ghosty Shop запущено...")
    app.run_polling()

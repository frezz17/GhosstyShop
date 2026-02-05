import logging
import random
import urllib.parse
from collections import Counter
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
    MessageHandler,
    ContextTypes,
    filters
)
from telegram.error import BadRequest

# ================== КОНФІГУРАЦІЯ / CONFIG ==================
TOKEN = "8351638507:AAEOSgiUsQHk2DtI2aurKqGhoS5-JPLqf-g"  # Вставте сюди свій токен
MANAGER_USERNAME = "ghosstydp"
CHANNEL_URL = "https://t.me/GhostyStaffDP"
BOT_USERNAME = "GhostyShopBot"

WELCOME_PHOTO = "https://i.ibb.co/y7Q194N/1770068775663.png"
CART_PHOTO = "https://img.freepik.com/premium-vector/medical-cannabis-logo-with-marijuana-leaf-glowing-neon-sign_75817-1830.jpg"

DISCOUNT_PERCENT = 45
DISCOUNT_MULT = 0.55
VIP_END_DATE = "25.03.2026"

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# ================== БАЗА ДАНИХ / DATABASE ==================
PRODUCTS = {
    # --- ННС ВЕЙПИ (HHC) ---
    100: {"name": "🍊 Packwoods Orange", "cat": "hhc", "price": 499, "img": "https://i.ibb.co/V03f2yYF/Ghost-Vape-1.jpg", "variants": ["1мл рідини"],
          "desc": "✨ Ефект: Глибоке розслаблення тіла, легка ейфорія.\n🔋 Склад: 90% ННС дистилят."},
    101: {"name": "🌸 Packwoods Pink", "cat": "hhc", "price": 579, "img": "https://i.ibb.co/65j1901/Ghost-Vape-2.jpg", "variants": ["1мл рідини"],
          "desc": "✨ Ефект: М'який соціальний ефект, знімає тривогу.\n🌸 Смак: Солодка полуниця."},
    102: {"name": "🍇 Packwoods Purple", "cat": "hhc", "price": 689, "img": "https://i.ibb.co/DHXXSh2d/Ghost-Vape-3.jpg", "variants": ["1мл рідини"],
          "desc": "✨ Ефект: Потужний 'стоун', заспокоює думки.\n🍇 Смак: Насичений виноград."},
    103: {"name": "❄️ Whole Mint", "cat": "hhc", "price": 777, "img": "https://i.ibb.co/675LQrNB/Ghost-Vape-4.jpg", "variants": ["2мл рідини"],
          "desc": "✨ Ефект: Бадьорість та фокус. Сатіва-домінант.\n❄️ Смак: Крижана м'ята."},
    104: {"name": "🌴 Jungle Boys White", "cat": "hhc", "price": 859, "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg", "variants": ["2мл рідини"],
          "desc": "✨ Ефект: Максимальна сила. Ейфорія та релакс.\n🌴 Смак: Тропічні фрукти."},

    # --- ПОД-СИСТЕМИ (PODS) ---
    200: {"name": "⚡ Vaporesso XROS 4", "cat": "pod", "price": 699, "img": "https://vandalvape.life/image/cache/catalog/pod/vaporesso/xros%204/Vaporesso-Xros-4-Black-1000x1000.webp", "variants": ["Black", "Purple", "Blue"],
          "desc": "⚙️ Хар-ки: Акумулятор 1000mAh, 3 режими потужності. Топ 2024!"},
    201: {"name": "🚀 Vaporesso XROS 5", "cat": "pod", "price": 799, "img": "https://vandalvape.life/image/cache/catalog/pod/vaporesso/xros%204/Vaporesso-Xros-4-Black-1000x1000.webp", "variants": ["Black", "Pink", "Blue"],
          "desc": "⚙️ Хар-ки: Нова серія. Покращений обдув, швидка зарядка Type-C."},
    202: {"name": "🧊 XROS 4 Nano", "cat": "pod", "price": 719, "img": "https://vandalvape.life/image/cache/catalog/pod/vaporesso/xros%204%20nano/Xros-4-Nano-Twilight-Purple-1000x1000.webp", "variants": ["Black", "Blue", "Silver"],
          "desc": "⚙️ Хар-ки: Компактний дизайн, великий екран, регулювання обдуву."},
    203: {"name": "💎 XROS Pro", "cat": "pod", "price": 929, "img": "https://vandalvape.life/image/cache/catalog/pod/vaporesso/xros%20pro/Vaporesso-XROS-PRO-Black-1000x1000.webp", "variants": ["Pink", "Black", "Red"],
          "desc": "⚙️ Хар-ки: Преміум. Потужність до 30W, кнопка блокування."},
    204: {"name": "🔥 Vmate Mini", "cat": "pod", "price": 570, "img": "https://vandalvape.life/image/cache/catalog/pod/voopoo/vmate%20e/VooPoo-VMATE-E-Classic-Black-1000x1000.webp", "variants": ["Black", "Pink", "Red"],
          "desc": "⚙️ Хар-ки: Легкий, компактний, автозатяжка."},

    # --- РІДИНИ (LIQUIDS) ---
    300: {"name": "🍋 Chaser Balance", "cat": "liquid", "price": 229, "img": "https://vandalvape.life/image/cache/catalog//premix/Chaser%20Lux%2030/newfoto/VitaminVV-1000x1000.webp", "variants": ["50mg", "65mg"],
          "desc": "🍋 Смак: Енергетик. Кислий смак з бульбашками."},
    301: {"name": "🍓 Chaser Berry", "cat": "liquid", "price": 229, "img": "https://vandalvape.life/image/cache/catalog/premix/Chaser%20Lux%2030/newfoto/BerryLemonVV-1000x1000.webp", "variants": ["50mg", "65mg"],
          "desc": "🍓 Смак: Ягідний лимонад. Малина з лимоном."},
}

LOCATIONS = {
    "🏙️ Київ": ["🏛️ Печерський", "🎡 Оболонський", "🏗️ Дарницький", "🌳 Деснянський", "🛤️ Святошинський", "🌲 Голосіївський", "🎓 Шевченківський", "✈️ Солом’янський"],
    "🏗️ Харків": ["🏢 Салтівка", "🏛️ Центр", "🏔️ Холодна Гора", "🏟️ Слобідський", "🏭 Індустріальний", "🛠️ ХТЗ", "🏗️ Олексіївка", "🏤 Московський"],
    "⚓ Одеса": ["🌊 Приморський", "🚜 Суворовський", "🍷 Малиновський", "🏖️ Київський", "🏢 Таїрово", "🏠 Черемушки", "🏥 Слобідка", "🏘️ Млини"],
    "🌊 Дніпро": ["🛍️ Лівобережний", "🏙️ Центр", "🎡 Перемога", "🌳 Тополя", "🌉 Амур", "🏗️ Чечелівський", "🏢 Шевченківський", "🏭 Новокодацький"],
    "🦁 Львів": ["🏰 Галицький", "🚂 Залізничний", "🎨 Франківський", "🌳 Шевченківський", "🏢 Сихівський", "⛲ Личаківський", "🏘️ Рясне", "🌲 Брюховичі"],
    "⚡ Запоріжжя": ["🔋 Дніпровський", "🌳 Вознесенівський", "🏛️ Олександрівський", "🏘️ Комунарський", "🐎 Хортицький", "🏢 Шевченківський", "🏭 Заводський", "🌅 Південний"],
    "🔩 Кривий Ріг": ["🏙️ Центральний", "⛏️ Тернівський", "🏛️ Покровський", "🎡 Саксаганський", "🚂 Довгинцівський", "🏭 Металургійний", "🌳 Інгулецький", "🏗️ Південний"],
    "⛲ Вінниця": ["🏢 Замостя", "🍒 Вишенька", "🌊 Поділ", "🏛️ Старе місто", "🎓 Академічний", "🏗️ Тяжилів", "🏘️ Слов’янка", "🇰🇷 Корея"],
    "🚢 Миколаїв": ["🏙️ Центральний", "🏗️ Заводський", "🌊 Інгульський", "⚓ Корабельний", "🏘️ Варварівка", "🌳 Тернівка", "🌲 Матвіївка", "🏠 Соляні"],
    "🛠️ Кам'янське": ["🏤 Центральний", "🏗️ Південний", "🌊 Дніпровський", "🏠 Новокам’янка", "🏢 Победа", "🏘️ Правобережний", "🌳 Лівобережний", "🏙️ Соцмісто"]
}

# ================== HELPER FUNCTIONS ==================

def get_main_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👤 Мій Профіль", callback_data="profile")],
        [InlineKeyboardButton("📦 Асортимент", callback_data="assortment")],
        [InlineKeyboardButton("🌿 ННС-Вейпи", callback_data="list_hhc"), InlineKeyboardButton("🔋 Поди", callback_data="list_pod")],
        [InlineKeyboardButton("💧 Рідини", callback_data="list_liquid"), InlineKeyboardButton("📜 Політика", callback_data="policy")],
        [InlineKeyboardButton("📍 Обрати Місто", callback_data="sel_city_menu"), InlineKeyboardButton("📦 Мої замовлення", callback_data="my_orders")],
        [InlineKeyboardButton("👨‍💻 Менеджер", url=f"https://t.me/{MANAGER_USERNAME}"), InlineKeyboardButton("👻 Канал", url=CHANNEL_URL)]
    ])

async def safe_edit_media(message, media, reply_markup=None):
    try:
        await message.edit_media(media=media, reply_markup=reply_markup)
    except BadRequest:
        pass  # Ignore if content is the same

async def safe_edit_caption(message, caption, reply_markup=None):
    try:
        await message.edit_caption(caption=caption, parse_mode="Markdown", reply_markup=reply_markup)
    except BadRequest:
        pass

# ================== HANDLERS ==================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = context.args
    
    # Ініціалізація даних користувача
    if "promo" not in context.user_data:
        context.user_data.update({
            "promo": f"GHST-{random.randint(1000,9999)}",
            "cart": [],
            "promo_active": False,
            "location": {"city": None, "dist": None},
            "input_state": None,
            "orders": [],
            "vip": False,
            "referrer": None
        })

    # Перевірка реферала
    if args and len(args) > 0:
        ref_id = args[0]
        # Якщо перейшов за посиланням і це не він сам
        if str(ref_id) != str(user.id) and context.user_data.get("referrer") is None:
            context.user_data["referrer"] = ref_id
            context.user_data["vip"] = True # Даємо VIP тому хто перейшов

    welcome_text = (
        f"👋 *Вітаємо в Ghosty Shop, {user.first_name}!* 👻\n\n"
        f"Шукаєш якість за адекватні гроші? Ти в правильному місці! "
        f"Ми пропонуємо найнижчі ціни та найкращий стафф в Україні.\n\n"
        f"✅ Тільки оригінальна продукція.\n🚀 Швидка та безкоштовна доставка.\n🤫 Повна анонімність.\n\n"
        f"🎁 *Твій персональний Промокод:* `{context.user_data['promo']}`\n"
        f"(-35% на все + рідина у подарунок на перше замовлення!)"
    )
    
    if update.message:
        await update.message.reply_photo(photo=WELCOME_PHOTO, caption=welcome_text, parse_mode="Markdown", reply_markup=get_main_kb())
    else:
        # Якщо викликано через кнопку "Назад в головне"
        await safe_edit_media(update.callback_query.message, InputMediaPhoto(media=WELCOME_PHOTO, caption=welcome_text, parse_mode="Markdown"), reply_markup=get_main_kb())

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ud = context.user_data
    state = ud.get("input_state")
    text = update.message.text.strip()

    if state == "wait_promo":
        if text == ud.get("promo"):
            ud["promo_active"] = True
            ud["input_state"] = None
            await update.message.reply_text("✅ *Промокод застосовано!* Всі ціни знижено на 35%.", parse_mode="Markdown")
            await show_cart(update, context, new_msg=True)
        else:
            await update.message.reply_text("❌ Невірний код. Спробуйте ще раз або поверніться в меню.")
    
    elif state == "wait_name":
        ud["order_name"] = text
        ud["input_state"] = "wait_phone"
        await update.message.reply_text("📱 *Введіть ваш номер телефону:*")
    
    elif state == "wait_phone":
        ud["order_phone"] = text
        ud["input_state"] = "wait_post"
        await update.message.reply_text("📮 *Введіть номер відділення або поштомату Нової Пошти:*\n(Наприклад: Відділення 25 або 4455)")
    
    elif state == "wait_post":
        ud["order_post"] = text
        ud["input_state"] = None
        await finalize_order(update, context)

# ================== CART LOGIC ==================

async def show_cart(update: Update, context: ContextTypes.DEFAULT_TYPE, new_msg=False):
    ud = context.user_data
    cart = ud.get("cart", [])
    
    if not cart:
        text = "🛒 *Ваш кошик порожній.*"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("📦 До товарів", callback_data="assortment")],
            [InlineKeyboardButton("🏠 В головне меню", callback_data="main_menu")]
        ])
    else:
        raw_sum = sum(i['price'] for i in cart)
        final_sum = int(raw_sum * DISCOUNT_MULT) if ud.get("promo_active") else raw_sum
        
        text = "🛒 *ВАШ КОШИК:*\n━━━━━━━━━━━━━━━━━━\n"
        
        # Створення кнопок для видалення товарів
        kb_btns = []
        for idx, item in enumerate(cart):
            text += f"{idx+1}. {item['name']} ({item['variant']}) - {item['price']} грн\n"
            # Кнопка видалення для кожного товару за індексом
            kb_btns.append([InlineKeyboardButton(f"❌ Видалити №{idx+1}", callback_data=f"del_cart_{idx}")])
        
        text += f"━━━━━━━━━━━━━━━━━━\n💰 Разом: *{final_sum} грн*\n"
        text += "🎫 Промокод: " + ("✅ АКТИВНИЙ" if ud.get("promo_active") else "❌ НЕМАЄ") + "\n"
        text += "🎁 Бонус: *Рідина у подарунок!* 💧"
        
        if not ud.get("promo_active"):
            kb_btns.append([InlineKeyboardButton("🎟 Застосувати промокод", callback_data="enter_promo")])
        
        kb_btns.append([InlineKeyboardButton("✅ Оформити замовлення", callback_data="checkout_start")])
        kb_btns.append([InlineKeyboardButton("🗑 Очистити все", callback_data="clear_cart")])
        kb_btns.append([InlineKeyboardButton("📦 До товарів", callback_data="assortment")])
        kb_btns.append([InlineKeyboardButton("🏠 В головне меню", callback_data="main_menu")])
        
        kb = InlineKeyboardMarkup(kb_btns)

    if new_msg:
        await update.message.reply_photo(photo=CART_PHOTO, caption=text, parse_mode="Markdown", reply_markup=kb)
    else:
        await safe_edit_media(update.callback_query.message, InputMediaPhoto(media=CART_PHOTO, caption=text, parse_mode="Markdown"), reply_markup=kb)

# ================== HISTORY LOGIC ==================

async def show_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    orders = context.user_data.get("orders", [])
    if not orders:
        txt = "📂 *Історія замовлень порожня.*"
    else:
        txt = "📂 *ВАШІ ЗАМОВЛЕННЯ:*\n\n"
        for o in reversed(orders[-5:]): # Показуємо останні 5
            txt += f"🧾 *{o['date']}* | {o['total']} грн\n{o['items']}\n━━━━━━━━━━━━\n"
    
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]])
    await safe_edit_caption(update.callback_query.message, txt, kb)

# ================== CALLBACKS ==================

async def callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    ud = context.user_data
    data = q.data

    # --- Navigation ---
    if data == "main_menu":
        await start(update, context)

    elif data == "assortment":
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🌿 ННС-Вейпи", callback_data="list_hhc")],
            [InlineKeyboardButton("🔋 Под-Системи", callback_data="list_pod")],
            [InlineKeyboardButton("💧 Рідини", callback_data="list_liquid")],
            [InlineKeyboardButton("🛒 Кошик", callback_data="open_cart"), InlineKeyboardButton("🏠 Головне меню", callback_data="main_menu")]
        ])
        await safe_edit_caption(q.message, "📦 *Оберіть категорію товару:*", kb)
    
    elif data == "my_orders":
        await show_history(update, context)

    # --- Profile & Referral ---
    elif data == "profile":
        loc = ud.get("location", {})
        city_stat = f"{loc.get('city')} ✅" if loc.get("city") else "❌ Не обрано"
        dist_stat = f"{loc.get('dist')} ✅" if loc.get("dist") else "❌ Не обрано"
        username = f"@{q.from_user.username}" if q.from_user.username else "❌ Не вказано"
        
        # Логіка VIP
        is_vip = ud.get("vip", False)
        vip_text = f"💎 VIP-Статус: *АКТИВНИЙ* (Безкоштовна доставка до {VIP_END_DATE}) ✅" if is_vip else "💎 VIP-Статус: ❌ Неактивний"
        
        # Реферальне посилання
        ref_link = f"https://t.me/{BOT_USERNAME}?start={q.from_user.id}"

        txt = (
            f"👤 *ТВІЙ ПРОФІЛЬ*\n━━━━━━━━━━━━━━━━━━\n"
            f"🆔 ID: `{q.from_user.id}`\n"
            f"👤 Username: {username}\n"
            f"🎫 Промо: `{ud.get('promo','❌')}`\n\n"
            f"{vip_text}\n"
            f"🔗 *Твоє реферальне посилання:*\n`{ref_link}`\n"
            f"_(Запроси друга та отримай VIP статус! Переваги: безкоштовна доставка)_\n\n"
            f"📍 Місто: {city_stat}\n"
            f"🏘 Район: {dist_stat}\n"
            f"━━━━━━━━━━━━━━━━━━"
        )

        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🌆 Змінити місто та район", callback_data="sel_city_menu")],
            [InlineKeyboardButton("📦 Мої замовлення", callback_data="my_orders")],
            [InlineKeyboardButton("🏠 Назад в меню", callback_data="main_menu")]
        ])

        await safe_edit_caption(q.message, txt, kb)

    # --- Location System ---
    elif data == "sel_city_menu" or data.startswith("setcity_") or data.startswith("setdist_"):
        if data.startswith("setcity_"):
            chosen_city = data.split("_", 1)[1]
            if ud["location"]["city"] != chosen_city:
                ud["location"]["dist"] = None
            ud["location"]["city"] = chosen_city
        elif data.startswith("setdist_"):
            chosen_dist = data.split("_", 1)[1]
            ud["location"]["dist"] = chosen_dist

        current_city = ud["location"]["city"]

        if data == "sel_city_menu":
            btns = []
            for city_name in LOCATIONS.keys():
                mark = " ✅" if city_name == current_city else ""
                btns.append([InlineKeyboardButton(f"{city_name}{mark}", callback_data=f"setcity_{city_name}")])
            btns.append([InlineKeyboardButton("🏠 Головне меню", callback_data="main_menu")])
            await safe_edit_caption(q.message, "📍 *Обери своє місто:*", InlineKeyboardMarkup(btns))
            
        elif data.startswith("setcity_") or data.startswith("setdist_"):
            if not current_city: return 
            districts = LOCATIONS[current_city]
            current_dist = ud["location"]["dist"]
            
            btns = []
            row = []
            for d in districts:
                mark = " ✅" if d == current_dist else ""
                row.append(InlineKeyboardButton(f"{d}{mark}", callback_data=f"setdist_{d}"))
                if len(row) == 2:
                    btns.append(row); row = []
            if row: btns.append(row)
            
            btns.append([InlineKeyboardButton("🔙 Назад до міст", callback_data="sel_city_menu")])
            status_text = f"✅ Район {current_dist} збережено!" if current_dist else "Оберіть район зі списку:"
            caption = f"🏙 *Місто: {current_city}*\n{status_text}"
            await safe_edit_caption(q.message, caption, InlineKeyboardMarkup(btns))

    # --- Product Catalog ---
    elif data.startswith("list_"):
        cat = data.split("_")[1]
        btns = []
        for pid, p in PRODUCTS.items():
            if p["cat"] == cat:
                price = int(p['price'] * DISCOUNT_MULT) if ud.get("promo_active") else p['price']
                btns.append([InlineKeyboardButton(f"{p['name']} | {price}₴", callback_data=f"prod_{pid}")])
        btns.append([InlineKeyboardButton("🔙 До категорій", callback_data="assortment")])
        btns.append([InlineKeyboardButton("🏠 В головне меню", callback_data="main_menu")])
        await safe_edit_caption(q.message, "⬇️ *Оберіть товар:*", InlineKeyboardMarkup(btns))

    elif data.startswith("prod_"):
        pid = int(data.split("_")[1])
        p = PRODUCTS[pid]
        p_active = ud.get("promo_active")
        price_text = f"❌ ~{p['price']} грн~\n✅ *{int(p['price']*DISCOUNT_MULT)} грн*" if p_active else f"💰 *{p['price']} грн*"
        
        loc_txt = f"{ud['location']['city'] or '❌'}, {ud['location']['dist'] or '❌'}"
        
        caption = (
            f"🏷 *{p['name']}*\n━━━━━━━━━━━━━━━━━━\n"
            f"{p['desc']}\n\n{price_text}\n"
            f"🎁 *Подарунок: Рідина 30мл!*\n━━━━━━━━━━━━━━━━━━\n"
            f"📍 Локація: {loc_txt}"
        )
        btns = [[InlineKeyboardButton(f"➕ Додати {v}", callback_data=f"add_{pid}_{v}")] for v in p["variants"]]
        btns.append([InlineKeyboardButton("🛒 Кошик", callback_data="open_cart")])
        btns.append([InlineKeyboardButton(f"🔙 До списку {p['cat'].upper()}", callback_data=f"list_{p['cat']}")])
        btns.append([InlineKeyboardButton("🏠 В головне меню", callback_data="main_menu")])
        
        await safe_edit_media(q.message, InputMediaPhoto(media=p["img"], caption=caption, parse_mode="Markdown"), reply_markup=InlineKeyboardMarkup(btns))

    # --- Cart Actions ---
    elif data.startswith("add_"):
        pid, var = int(data.split("_")[1]), data.split("_")[2]
        p = PRODUCTS[pid]
        ud["cart"].append({"name": p["name"], "variant": var, "price": p["price"]})
        # При додаванні нічого не змінюємо візуально, просто повідомлення
        await q.answer(f"✅ {p['name']} додано до кошика!", show_alert=False)

    elif data == "open_cart": await show_cart(update, context)
    
    elif data == "clear_cart":
        ud["cart"] = []; ud["promo_active"] = False
        await q.answer("🗑 Кошик очищено"); await show_cart(update, context)
    
    elif data.startswith("del_cart_"):
        # Видалення конкретного товару
        idx = int(data.split("_")[2])
        try:
            ud["cart"].pop(idx)
            await q.answer("🗑 Товар видалено")
        except IndexError:
            await q.answer("⚠️ Помилка оновлення", show_alert=True)
        await show_cart(update, context)

    elif data == "enter_promo":
        ud["input_state"] = "wait_promo"
        await q.message.reply_text("🎫 *Введіть ваш промокод:*")

    # --- Checkout ---
    elif data == "checkout_start":
        if not ud.get("cart"): await q.answer("Кошик порожній!", show_alert=True); return
        ud["input_state"] = "wait_name"
        await q.message.reply_text("📝 *Оформлення замовлення*\nВведіть ваше Прізвище та Ім'я:")

    elif data == "policy":
        txt = (
            "📜 *Умови, правила, відповідальність*\n\n"
            "1️⃣ Проєкт має навчально-дослідницький характер.\n"
            "2️⃣ Інформація в боті подається виключно з ознайомчою метою.\n"
            "3️⃣ Матеріали не є рекомендацією до придбання чи використання продукції шопу.\n"
            "4️⃣ Користувач самостійно несе відповідальність за свої дії та автоматично погоджується з цима правилами при натисканні /start у боті.\n"
            "5️⃣ Адміністрація не зберігає персональні дані користувача та не використовує їх.\n"
            "6️⃣ Адміністрація не несе за відповідальності за любі дії користувача у боті, та не зобов'язується повертати переказані менеджеру кошти за послугу \"Спілкування з менеджером Шопу\" під видом товару.\n\n"
            "⚠️ *Важливо:*\n"
            "7️⃣ Магазин не є реальним та не здійснює продаж товарів, також магазин немає складів на території України.\n"
            "8️⃣ Жоден товар не буде доставлений до замовника, товара не існує.\n"
            "9️⃣ Усі переказані кошти вважаються добровільним подарунком, повернути їх - не можна.\n"
            "🔟 Всі грошові операції через менеджера — подарунок кодеру та розробнику Gho$$tyyy/"
        )
        await safe_edit_caption(q.message, txt, InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]]))


# ================== FINALIZE ORDER ==================

async def finalize_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ud = context.user_data
    cart = ud["cart"]
    promo_act = ud.get("promo_active")
    total = int(sum(i['price'] for i in cart) * (DISCOUNT_MULT if promo_act else 1))
    
    items_str = "\n".join([f"• {i['name']} ({i['variant']})" for i in cart])
    order_id = f"GHST#{update.effective_user.id}-{random.randint(10,99)}"
    
    loc_info = f"{ud['location']['city'] or 'Не обрано'}, {ud['location']['dist'] or 'Не обрано'}"
    
    # Збереження в історію
    ud.get("orders", []).append({
        "id": order_id,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "total": total,
        "items": items_str
    })

    manager_msg = (
        f"🆕 *ORDER {order_id}*\n"
        f"👤 {ud['order_name']}\n📞 {ud['order_phone']}\n📦 Post: {ud['order_post']}\n"
        f"📍 {loc_info}\n\n"
        f"🛒 *ITEMS:*\n{items_str}\n"
        f"💰 Total: {total} UAH\n"
        f"🎫 Promo: {'YES' if promo_act else 'NO'}"
    )
    
    link = f"https://t.me/{MANAGER_USERNAME}?text={urllib.parse.quote(manager_msg)}"
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✈️ НАДІСЛАТИ МЕНЕДЖЕРУ", url=link)], 
        [InlineKeyboardButton("🏠 В головне меню", callback_data="main_menu")]
    ])
    
    # Очистка кошика після замовлення
    ud["cart"] = []
    ud["promo_active"] = False

    await update.message.reply_text(f"✅ *Замовлення {order_id} сформовано!*\nНатисніть кнопку нижче, щоб відправити дані менеджеру.", parse_mode="Markdown", reply_markup=kb)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callbacks))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text))
    print("🤖 Бот Ghosty Shop запущено...")
    app.run_polling()

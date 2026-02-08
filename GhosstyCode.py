import os
import sys
import logging
import random
import asyncio
import re
from html import escape
from datetime import datetime, timedelta

import telegram
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
    PicklePersistence
)
from telegram.error import BadRequest, NetworkError, TelegramError

# ===================== CONFIG =====================
TOKEN = "8351638507:AAEqc9p9b4AA8vTrzvvj_XArtUABqcfMGV4"
MANAGER_ID = 7544847872
MANAGER_USERNAME = "ghosstydp"
CHANNEL_URL = "https://t.me/GhostyStaffDP"
PAYMENT_LINK = "https://heylink.me/ghosstyshop/"
WELCOME_PHOTO = "https://i.ibb.co/y7Q194N/1770068775663.png"

# Константи для розрахунків
DISCOUNT_MULTIPLIER = 0.65
PROMO_DISCOUNT = 35
BASE_VIP_DATE = datetime(2026, 3, 25)

os.makedirs('data', exist_ok=True)

# ===================== PRODUCTS =====================
LIQUIDS = {
    301: {
        "name": "🎃 Pumpkin Latte",
        "series": "Chaser HO HO HO Edition",
        "price": 269,
        "discount": True,
        "img": "https://i.ibb.co/Y7qn69Ds/photo-2024-12-18-00-00-00.jpg",
        "desc": "☕ Гарбузовий латте з корицею\n🎄 Зимовий настрій\n😌 Мʼякий та теплий смак",
        "effect": "Затишок, солодкий aftertaste ☕",
    },
    302: {
        "name": "🍷 Glintwine",
        "series": "Chaser HO HO HO Edition",
        "price": 269,
        "discount": True,
        "img": "https://i.ibb.co/wF8r7Nmc/photo-2024-12-18-00-00-01.jpg",
        "desc": "🍇 Пряний глінтвейн\n🔥 Теплий винний смак\n🎄 Святковий вайб",
        "effect": "Тепло, релакс 🔥",
    },
    303: {
        "name": "🎄 Christmas Tree",
        "series": "Chaser HO HO HO Edition",
        "price": 269,
        "discount": True,
        "img": "https://i.ibb.co/vCPGV8RV/photo-2024-12-18-00-00-02.jpg",
        "desc": "🌲 Хвоя + морозна свіжість\n❄️ Дуже свіжа\n🎅 Атмосфера зими",
        "effect": "Свіжість, холодок ❄️",
    }
}

HHC_VAPES = {
    100: {
        "name": "🌴 Packwoods Purple 1ml",
        "type": "hhc",
        "gift_liquid": True,
        "price": 549,
        "discount": True,
        "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg",
        "desc": "🧠 90% ННС | Гібрид\n😌 Розслаблення + легка ейфорія\n🎨 Мʼякий виноградний профіль\n🎁 Рідина у подарунок на вибір\n⚠️ Потужний ефект — починай з малого",
    },
    101: {
        "name": "🍊 Packwoods Orange 1ml",
        "type": "hhc",
        "gift_liquid": True,
        "price": 629,
        "discount": True,
        "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg",
        "desc": "🧠 90% ННС | Гібрид\n⚡ Бадьорить та фокусує\n🍊 Соковитий апельсин\n🎁 Рідина у подарунок на вибір\n🔥 Яскравий та швидкий ефект",
    },
    102: {
        "name": "🌸 Packwoods Pink 1ml",
        "type": "hhc",
        "gift_liquid": True,
        "price": 719,
        "discount": True,
        "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg",
        "desc": "🧠 90% ННС | Гібрид\n😇 Спокій + підйом настрою\n🍓 Солодко-фруктовий мікс\n🎁 Рідина у подарунок на вибір\n✨ Комфортний та плавний",
    },
    103: {
        "name": "🌿 Whole Mint 2ml",
        "type": "hhc",
        "gift_liquid": True,
        "price": 849,
        "discount": True,
        "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg",
        "desc": "🧠 95% ННС | Сатіва\n⚡ Енергія та ясність\n❄️ Свіжа мʼята\n🎁 Рідина у подарунок на вибір\n🚀 Ідеально вдень",
    },
    104: {
        "name": "🌴 Jungle Boys White 2ml",
        "type": "hhc",
        "gift_liquid": True,
        "price": 999,
        "discount": True,
        "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg",
        "desc": "🧠 95% ННС | Індика\n😴 Глибокий релакс\n🌲 Насичений терпкий смак\n🎁 Рідина у подарунок на вибір\n🌙 Ідеально для вечора та сну",
    }
}

PODS = {
    500: { "name": "🔌 Vaporesso XROS 3 Mini", "type": "pod", "gift_liquid": False, "price": 499, "discount": True, "img": "https://i.ibb.co/yFSQ5QSn/vaporesso-xros-3-mini.jpg", "desc": "🔋 1000 mAh\n💨 MTL / RDL\n⚡ Type-C зарядка\n✨ Компактний та легкий" },
    501: { "name": "🔌 Vaporesso XROS 5 Mini", "type": "pod", "gift_liquid": False, "price": 579, "discount": True, "img": "https://i.ibb.co/RkNgt1Qr/vaporesso-xros-5-mini.jpg", "desc": "🔋 1000 mAh\n🔥 COREX 2.0\n⚡ Швидка зарядка\n🎯 Яскравий смак" },
    502: { "name": "🔌 Vaporesso XROS Pro", "type": "pod", "gift_liquid": False, "price": 689, "discount": True, "img": "https://i.ibb.co/ynYwSMt6/vaporesso-xros-pro.jpg", "desc": "🔋 1200 mAh\n⚡ Регулювання потужності\n💨 RDL / MTL\n🔥 Максимальний смак" },
    503: { "name": "🔌 Vaporesso XROS Nano", "type": "pod", "gift_liquid": False, "price": 519, "discount": True, "img": "https://i.ibb.co/5XW2yN80/vaporesso-xros-nano.jpg", "desc": "🔋 1000 mAh\n💨 MTL\n🧱 Міцний корпус" },
    504: { "name": "🔌 Vaporesso XROS 4", "type": "pod", "gift_liquid": False, "price": 599, "discount": True, "img": "https://i.ibb.co/LDRbQxr1/vaporesso-xros-4.jpg", "desc": "🔋 1000 mAh\n🔥 COREX\n🎨 Стильний дизайн" },
    505: { "name": "🔌 Vaporesso XROS 5", "type": "pod", "gift_liquid": False, "price": 799, "discount": True, "img": "https://i.ibb.co/hxjmpHF2/vaporesso-xros-5.jpg", "desc": "🔋 1200 mAh\n⚡ Fast Charge\n💎 Преміальна збірка" },
    506: { "name": "🔌 Voopoo Vmate Mini Pod Kit", "type": "pod", "gift_liquid": False, "price": 459, "discount": True, "img": "https://i.ibb.co/8L0JNTHz/voopoo-vmate-mini.jpg", "desc": "🔋 1000 mAh\n💨 Автозатяжка\n🧲 Магнітний картридж" }
}

# ===================== CITIES & DISTRICTS =====================
CITIES = [
    "Київ", "Дніпро", "Кам'янське", "Харків", "Одеса",
    "Львів", "Запоріжжя", "Кривий Ріг", "Полтава", "Черкаси"
]

CITY_DISTRICTS = {
    "Київ": [
        "Шевченківський", "Дарницький", "Оболонський", "Печерський",
        "Солом'янський", "Деснянський", "Подільський", "Голосіївський"
    ],
    "Дніпро": [
        "Центральний", "Соборний", "Індустріальний", "Амур",
        "Новокодацький", "Чечелівський", "Самарський", "Доставка на вказану адресу"
    ],
    "Кам'янське": [
        "Центральний", "Південний", "Заводський", "Дніпровський",
        "Черемушки", "Романкове", "БАМ", "Соцмісто"
    ],
    "Харків": [
        "Київський", "Салтівський", "Холодногірський", "Індустріальний",
        "Основ'янський", "Немишлянський", "Новобаварський", "Шевченківський"
    ],
    "Одеса": [
        "Приморський", "Київський", "Малиновський", "Суворовський",
        "Пересипський", "Хаджибейський", "Таїровський", "Люстдорфський"
    ],
    "Львів": [
        "Залізничний", "Личаківський", "Франківський", "Шевченківський",
        "Сихівський", "Галицький", "Королівський", "Новий"
    ],
    "Запоріжжя": [
        "Олександрівський", "Заводський", "Комунарський", "Дніпровський",
        "Вознесенівський", "Шевченківський", "Хортицький", "Центральний"
    ],
    "Кривий Ріг": [
        "Довгинцівський", "Інгулецький", "Металургійний", "Покровський",
        "Саксаганський", "Тернівський", "Центрально-Міський", "Червоногвардійський"
    ],
    "Полтава": [
        "Шевченківський", "Подільський", "Київський", "Залізничний",
        "Октябрський", "Ленінський", "Центральний", "Новосанжарський"
    ],
    "Черкаси": [
        "Придніпровський", "Соснівський", "Смілянський", "Канівський",
        "Золотоніський", "Уманський", "Звенигородський", "Городищенський"
    ]
}

# ===================== HELPERS =====================

def generate_promo_code(user_id: int) -> str:
    return f"GHOST-{user_id % 10000}{random.randint(100,999)}"

def gen_order_id(uid: int) -> str:
    return f"GHST-{uid}-{random.randint(1000,9999)}"

def get_gift_liquids_list():
    return [data["name"] for data in LIQUIDS.values()]

def vip_until(profile: dict) -> datetime:
    base = profile.get("vip_base", BASE_VIP_DATE)
    refs = profile.get("referrals", 0)
    return base + timedelta(days=7 * refs)

def calc_prices(item: dict, promo_percent: int) -> dict:
    base = item["price"]
    discounted = int(base * DISCOUNT_MULTIPLIER) if item.get("discount", True) else base
    final = int(discounted * (1 - promo_percent / 100))
    return {"base": base, "discounted": discounted, "final": final}

def build_item_caption(item: dict, user_data: dict) -> str:
    profile = user_data.get("profile", {})
    promo_percent = profile.get("promo_discount", PROMO_DISCOUNT)
    v_date = vip_until(profile)
    is_vip = datetime.now() < v_date
    prices = calc_prices(item, promo_percent)

    text = f"<b>{escape(item['name'])}</b>\n"
    if "series" in item: text += f"✨ <i>{item['series']}</i>\n"
    text += "━━━━━━━━━━━━━━━━━━\n"
    text += f"💰 Ціна: <s>{prices['base']} грн</s>\n"
    text += f"🔥 Акція -35%: <b>{prices['discounted']} грн</b>\n"
    text += f"🎟 З промокодом -{promo_percent}%: <u><b>{prices['final']} грн</b></u>\n\n"
    text += f"{item.get('desc', '')}\n"
    
    if item.get("gift_liquid"):
        gifts = "\n".join(f"  • {g}" for g in get_gift_liquids_list())
        text += f"\n🎁 <b>ПОДАРУНОК НА ВИБІР:</b>\n{gifts}\n"

    text += "━━━━━━━━━━━━━━━━━━\n"
    if is_vip:
        text += f"💎 <b>VIP активовано</b> (Безкоштовна доставка)\n📅 До: {v_date.strftime('%d.%m.%Y')}\n"
    else:
        text += "🚚 Доставка: за тарифами пошти\n"
    return text

# ===================== HANDLERS =====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    # Ініціалізація профілю, якщо юзер новий
    if 'profile' not in context.user_data:
        context.user_data['profile'] = {
            'user_id': user.id, 
            'full_name': user.full_name, 
            'username': user.username,
            'city': None, 
            'district': None, 
            'address': None, 
            'phone': None,
            'promo_code': generate_promo_code(user.id), 
            'promo_discount': PROMO_DISCOUNT,
            'referrals': 0, 
            'vip_base': BASE_VIP_DATE, 
            'orders_history': []
        }
        context.user_data['cart'] = []

    # Реферальна логіка
    if context.args and context.args[0].isdigit():
        ref_id = int(context.args[0])
        if ref_id != user.id and 'referred_by' not in context.user_data['profile']:
            context.user_data['profile']['referred_by'] = ref_id

    welcome_text = (
        f"👋 <b>Вітаємо у Ghosty Shop, {escape(user.first_name)}!</b> 👻\n\n"
        f"🔥 <b>Твої привілеї:</b>\n"
        f"• Промокод: <code>{context.user_data['profile']['promo_code']}</code>\n"
        f"• 💎 VIP-статус: <b>Активний</b>\n"
        f"• 🎁 <b>Подарунок:</b> Рідина до кожного HHC!\n\n"
        f"Обирай категорію та насолоджуйся 👇"
    )
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🛍 Асортимент", callback_data="catalog"), InlineKeyboardButton("👤 Профіль", callback_data="profile")],
        [InlineKeyboardButton("🛒 Кошик", callback_data="view_cart"), InlineKeyboardButton("🔗 Реферали", callback_data="refs")],
        [InlineKeyboardButton("📜 Угода", callback_data="policy"), InlineKeyboardButton("🆘 Допомога", url=f"https://t.me/{MANAGER_USERNAME}")],
        [InlineKeyboardButton("👨‍💻 Менеджер", url=f"https://t.me/{MANAGER_USERNAME}"), InlineKeyboardButton("📣 Канал", url=CHANNEL_URL)]
    ])

    if update.message:
        await update.message.reply_photo(WELCOME_PHOTO, caption=welcome_text, parse_mode="HTML", reply_markup=kb)
    else:
        # Якщо ми повернулися з іншого меню, редагуємо існуюче повідомлення
        try:
            await update.callback_query.edit_message_caption(caption=welcome_text, parse_mode="HTML", reply_markup=kb)
        except:
            await update.callback_query.message.reply_photo(WELCOME_PHOTO, caption=welcome_text, parse_mode="HTML", reply_markup=kb)
            await update.callback_query.message.delete()

async def catalog_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("💨 ННС-ВЕЙПИ", callback_data="cat_hhc")],
        [InlineKeyboardButton("🔌 ПОД-СИСТЕМИ", callback_data="cat_pods")],
        [InlineKeyboardButton("💧 РІДИНИ", callback_data="cat_liq")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="main")]
    ])
    await update.callback_query.edit_message_caption("🛍 <b>Оберіть категорію товарів:</b>", parse_mode="HTML", reply_markup=kb)

async def list_items(update: Update, context: ContextTypes.DEFAULT_TYPE, cat):
    data_map = {"hhc": HHC_VAPES, "pods": PODS, "liq": LIQUIDS}
    items = data_map[cat]
    kb = []
    for iid, item in items.items():
        kb.append([InlineKeyboardButton(f"{item['name']} | {item['price']}₴", callback_data=f"show_{cat}_{iid}")])
    kb.append([InlineKeyboardButton("⬅️ Назад", callback_data="catalog")])
    await update.callback_query.edit_message_caption(f"✨ <b>Доступні товари ({cat.upper()}):</b>", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(kb))

async def show_item(update: Update, context: ContextTypes.DEFAULT_TYPE, cat, iid):
    iid = int(iid)
    item = (HHC_VAPES if cat=="hhc" else (PODS if cat=="pods" else LIQUIDS))[iid]
    txt = build_item_caption(item, context.user_data)
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🛒 Додати в кошик", callback_data=f"add_{cat}_{iid}")],
        [InlineKeyboardButton("⬅️ Назад", callback_data=f"cat_{cat}")]
    ])
    await update.callback_query.message.reply_photo(item['img'], caption=txt, parse_mode="HTML", reply_markup=kb)
    await update.callback_query.message.delete()

# --- Політика (Угода) ---
async def show_policy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = (
        "📜 <b>Угода користувача Ghosty Shop</b>\n\n"
        "1. Купуючи товар, ви підтверджуєте, що вам виповнилося 18 років.\n"
        "2. Магазин працює за повною або частковою передоплатою.\n"
        "3. Доставка здійснюється кур'єром по місту або Новою Поштою.\n"
        "4. Весь товар проходить перевірку перед відправкою.\n"
        "5. У разі виникнення питань щодо якості, звертайтеся до менеджера протягом 24 годин після отримання.\n\n"
        "🛡 <i>Ми гарантуємо анонімність та якість продукції.</i>"
    )
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="main")]])
    await update.callback_query.edit_message_caption(txt, parse_mode="HTML", reply_markup=kb)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    d = q.data
    await q.answer()

    if d == "main": await start(update, context)
    elif d == "catalog": await catalog_menu(update, context)
    elif d == "policy": await show_policy(update, context)
    elif d.startswith("cat_"): await list_items(update, context, d.split("_")[1])
    elif d.startswith("show_"): await show_item(update, context, d.split("_")[1], d.split("_")[2])
    elif d.startswith("add_"):
        cat, iid = d.split("_")[1], int(d.split("_")[2])
        item = (HHC_VAPES if cat=="hhc" else (PODS if cat=="pods" else LIQUIDS))[iid]
        context.user_data['cart'].append(item)
        await q.answer(f"✅ {item['name']} додано до кошика!")
    elif d == "view_cart": await view_cart(update, context)
    elif d == "clear_cart":
        context.user_data['cart'] = []
        await q.edit_message_text("🗑 Кошик очищено!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Меню", callback_data="main")]]))
    elif d == "checkout": await start_checkout(update, context)
    elif d == "profile": await show_profile(update, context)
    elif d == "change_geo": await change_geo(update, context)
    elif d.startswith("setcity_"): await set_city(update, context, d.split("_")[1])
    elif d.startswith("setdist_"): await set_dist(update, context, d.split("_")[1])

# --- Текстовий обробник (для адреси та телефону) ---
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = context.user_data.get('state')
    text = update.message.text

    if state == "wait_addr":
        context.user_data['profile']['address'] = text
        context.user_data['state'] = "wait_phone"
        await update.message.reply_text("📞 <b>Майже готово!</b>\nТепер введіть ваш номер телефону для зв'язку:")
    
    elif state == "wait_phone":
        context.user_data['profile']['phone'] = text
        context.user_data['state'] = None
        await update.message.reply_text(
            "✅ <b>Дані збережено!</b>\nТепер ви можете оформити замовлення з кошика.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛒 Перейти до кошика", callback_data="view_cart")]])
        )

# --- Профіль та Гео ---
async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    p = context.user_data['profile']
    txt = (
        f"👤 <b>Ваш кабінет Ghosty Shop</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🆔 ID: <code>{p['user_id']}</code>\n"
        f"🏙 Місто: {p['city'] or '❌ Не вказано'}\n"
        f"📍 Район: {p['district'] or '❌ Не вказано'}\n"
        f"🏠 Адреса: {p['address'] or '❌ Не вказано'}\n"
        f"📞 Тел: {p['phone'] or '❌ Не вказано'}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🏷 Промокод: <code>{p['promo_code']}</code>\n"
        f"👥 Рефералів: {p['referrals']}"
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("📍 Налаштувати дані", callback_data="change_geo")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="main")]
    ])
    await update.callback_query.edit_message_caption(txt, parse_mode="HTML", reply_markup=kb)

async def view_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cart = context.user_data.get('cart', [])
    if not cart:
        await update.callback_query.answer("Ваш кошик порожній! 🛒", show_alert=True)
        return
    
    promo = context.user_data['profile']['promo_discount']
    total = sum([calc_prices(i, promo)['final'] for i in cart])
    
    txt = "🛒 <b>Ваш кошик:</b>\n\n"
    for idx, item in enumerate(cart, 1):
        txt += f"{idx}. {item['name']} — {calc_prices(item, promo)['final']}₴\n"
    
    txt += f"\n💰 <b>Разом до сплати: {total} грн</b>\n"
    txt += "🚚 Доставка: <b>БЕЗКОШТОВНА (VIP)</b>"
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Оформити замовлення", callback_data="checkout")],
        [InlineKeyboardButton("🗑 Очистити кошик", callback_data="clear_cart")],
        [InlineKeyboardButton("🏠 Головне меню", callback_data="main")]
    ])
    
    if update.callback_query.message.photo:
        await update.callback_query.message.reply_text(txt, parse_mode="HTML", reply_markup=kb)
        await update.callback_query.message.delete()
    else:
        await update.callback_query.edit_message_text(txt, parse_mode="HTML", reply_markup=kb)

async def start_checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    p = context.user_data['profile']
    if not p['city'] or not p['address'] or not p['phone']:
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("📍 Заповнити профіль", callback_data="change_geo")]])
        await update.callback_query.edit_message_text("❌ <b>Для замовлення не вистачає даних!</b>\nБудь ласка, заповніть місто, адресу та телефон.", parse_mode="HTML", reply_markup=kb)
        return

    order_id = gen_order_id(p['user_id'])
    cart = context.user_data['cart']
    total = sum([calc_prices(i, p['promo_discount'])['final'] for i in cart])
    
    items_list = "\n".join([f"• {i['name']}" for i in cart])
    
    # Повідомлення клієнту
    client_txt = (
        f"📦 <b>Замовлення {order_id} прийнято!</b>\n\n"
        f"💵 Сума до сплати: <b>{total} грн</b>\n"
        f"📍 Адреса: {p['city']}, {p['district']}, {p['address']}\n\n"
        f"💳 Оплатіть за посиланням або чекайте на реквізити менеджера:"
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 Оплатити зараз", url=PAYMENT_LINK)],
        [InlineKeyboardButton("🖼 Надіслати чек", url=f"https://t.me/{MANAGER_USERNAME}")],
        [InlineKeyboardButton("🏠 В меню", callback_data="main")]
    ])
    await update.callback_query.edit_message_text(client_txt, parse_mode="HTML", reply_markup=kb)

    # Повідомлення менеджеру
    manager_txt = (
        f"🔔 <b>НОВЕ ЗАМОВЛЕННЯ {order_id}</b>\n\n"
        f"👤 Клієнт: @{p['username']} (ID: {p['user_id']})\n"
        f"📞 Телефон: {p['phone']}\n"
        f"📍 Локація: {p['city']}, {p['district']}\n"
        f"🏠 Адреса: {p['address']}\n\n"
        f"📦 Товари:\n{items_list}\n"
        f"💰 Разом: <b>{total} грн</b>"
    )
    await context.bot.send_message(chat_id=MANAGER_ID, text=manager_txt, parse_mode="HTML")
    context.user_data['cart'] = [] # Очищуємо кошик після успіху

# --- Допоміжні функції географії ---
async def change_geo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [[InlineKeyboardButton(c, callback_data=f"setcity_{c}")] for c in CITY_DISTRICTS.keys()]
    kb.append([InlineKeyboardButton("⬅️ Назад", callback_data="profile")])
    await update.callback_query.edit_message_text("🏙 <b>Оберіть ваше місто:</b>", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(kb))

async def set_city(update: Update, context: ContextTypes.DEFAULT_TYPE, city):
    context.user_data['profile']['city'] = city
    kb = [[InlineKeyboardButton(d, callback_data=f"setdist_{d}")] for d in CITY_DISTRICTS[city]]
    await update.callback_query.edit_message_text(f"📍 Місто {city}.\n<b>Оберіть ваш район:</b>", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(kb))

async def set_dist(update: Update, context: ContextTypes.DEFAULT_TYPE, dist):
    context.user_data['profile']['district'] = dist
    context.user_data['state'] = "wait_addr"
    await update.callback_query.edit_message_text("🏠 <b>Тепер надішліть у чат назву вулиці та номер будинку</b>\n(Або номер відділення Нової Пошти):")

# ===================== MAIN =====================
def main():
    pers = PicklePersistence(filepath="data/ghosty.pickle")
    app = Application.builder().token(TOKEN).persistence(pers).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    # Додайте MessageHandlers для текстів та фото (аналогічно попереднім версіям)
    
    print("🚀 Ghosty Shop Online!")
    app.run_polling()

if __name__ == "__main__":
    main()

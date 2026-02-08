import os
import sys
import logging
import random
import json
import asyncio
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

# Створення необхідних каталогів
os.makedirs('data', exist_ok=True)

# ===================== LOGGING =====================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ===================== CONFIG & CONSTANTS =====================
TOKEN = "8351638507:AAEqc9p9b4AA8vTrzvvj_XArtUABqcfMGV4"
MANAGER_ID = 7544847872
MANAGER_USERNAME = "ghosstydpbot"
CHANNEL_URL = "https://t.me/GhostyStaffDP"
PAYMENT_LINK = "https://heylink.me/ghosstyshop/"
WELCOME_PHOTO = "https://i.ibb.co/y7Q194N/1770068775663.png"

DISCOUNT_MULTIPLIER = 0.65  # Базова знижка магазину
PROMO_DISCOUNT_VAL = 0.35   # Знижка за промокодом (-35%)
BASE_VIP_DATE = datetime(2026, 3, 25)
GIFT_LIQUIDS = ["🍓 Полуничний Мікс", "🍏 Кисле Яблуко", "🧊 Крижана М'ята"]

# ===================== DATA: CITIES & PRODUCTS =====================
CITIES = ["Київ", "Дніпро", "Кам'янське", "Харків", "Одеса", "Львів", "Запоріжжя", "Кривий Ріг", "Полтава", "Черкаси"]
CITY_DISTRICTS = {
    "Київ": ["Голосіївський", "Дарницький", "Деснянський", "Дніпровський", "Оболонський", "Печерський", "Подільський", "Святошинський", "Солом'янський", "Шевченківський"],
    "Дніпро": ["Амур-Нижньодніпровський", "Індустріальний", "Самарський", "Центральний", "Чечелівський", "Шевченківський", "Соборний", "Новокодацький"],
    "Кам'янське": ["Дніпровський", "Заводський", "Південний"],
    "Харків": ["Київський", "Салтівський", "Шевченківський"],
}

HHC_VAPES = {
    101: {"name": "🌴 Packwoods Purple 1ml", "price": 1200, "desc": "Смак: Виноград. Склад: 95% HHC. Ефект: Релакс.", "img": WELCOME_PHOTO},
    102: {"name": "🍊 Packwoods Orange 1ml", "price": 1200, "desc": "Смак: Цитрус. Склад: 95% HHC. Ефект: Енергія.", "img": WELCOME_PHOTO},
}
PODS = {
    501: {"name": "🔌 XROS 3 Mini", "price": 950, "desc": "Батарея: 1000mAh. Зарядка: Type-C. Компактний.", "img": WELCOME_PHOTO},
}
LIQUIDS = {
    301: {"name": "💧 Hype Juice 30ml", "price": 350, "desc": "Міцність: 50mg. Співвідношення: 50/50.", "img": WELCOME_PHOTO},
}

# ===================== HELPERS: LOGGING & CALCULATIONS =====================
def save_user_file(user):
    with open('data/users.txt', 'a', encoding='utf-8') as f:
        f.write(f"{datetime.now()}|{user.id}|{user.username}|{user.first_name}\n")

def save_order_file(order_data):
    with open('data/orders.txt', 'a', encoding='utf-8') as f:
        f.write(json.dumps(order_data, ensure_ascii=False) + "\n")
    with open('data/users_orders.txt', 'a', encoding='utf-8') as f:
        f.write(f"Замовлення #{order_data['order_id']} від {order_data['user_id']} на суму {order_data['total']} грн\n")

def get_vip_date(profile):
    return BASE_VIP_DATE + timedelta(days=7 * profile.get('referrals', 0))

def calc_prices(item, promo_applied=False):
    base = item['price']
    discounted = int(base * DISCOUNT_MULTIPLIER)
    final = int(discounted * (1 - PROMO_DISCOUNT_VAL)) if promo_applied else discounted
    return base, discounted, final

# ===================== HANDLERS: START & PROFILE =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    save_user_file(user)
    
    if 'profile' not in context.user_data:
        promo = f"GHST{str(user.id)[::-1]}"
        context.user_data['profile'] = {
            'uid': user.id, 'name': user.first_name, 'username': user.username,
            'referrals': 0, 'promo_code': promo, 'promo_used': False,
            'city': None, 'district': None, 'address': None, 'phone': None
        }
        context.user_data['cart'] = []
        context.user_data['orders'] = []

    # Реферальна логіка
    if context.args and context.args[0].startswith('ref'):
        try:
            ref_id = int(context.args[0].replace('ref', ''))
            if ref_id != user.id and not context.user_data.get('is_referred'):
                # В реальній системі тут треба знайти context іншого юзера,
                # але для PicklePersistence без БД ми імітуємо нарахування при першому вході.
                context.user_data['is_referred'] = True
                logger.info(f"User {user.id} referred by {ref_id}")
        except: pass

    text = (
        "🇺🇦 Вітаємо в <b>Ghosty Shop</b>! 👻\n\n"
        "Магазин офіційно відкрито! У нас ви знайдете найкращі <b>ннс вейпи</b>, "
        "сучасні <b>pod системи</b> та преміальні <b>рідини</b>.\n\n"
        "👑 <b>VIP Статус:</b> дарує безкоштовну доставку! Отримуйте його за запрошення друзів.\n"
        "🎟 Використовуйте свій промокод у профілі, щоб отримати <b>-35% знижки</b>!\n\n"
        "Оберіть пункт меню нижче 👇"
    )
    
    kb = [
        [InlineKeyboardButton("👤 Профіль", callback_data="profile"), InlineKeyboardButton("🛍 асортимент", callback_data="assortment")],
        [InlineKeyboardButton("🛒 Кошик", callback_data="view_cart"), InlineKeyboardButton("👨‍💻 Менеджер", url=f"https://t.me/{MANAGER_USERNAME}")],
        [InlineKeyboardButton("🔗 Реферальна система", callback_data="referral"), InlineKeyboardButton("📣 Канал", url=CHANNEL_URL)],
        [InlineKeyboardButton("📜 Політика користувача", callback_data="policy")]
    ]
    
    if update.message:
        await update.message.reply_photo(WELCOME_PHOTO, caption=text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(kb))
    else:
        await update.callback_query.edit_message_caption(caption=text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(kb))

async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    p = context.user_data['profile']
    vip_date = get_vip_date(p).strftime("%d.%m.%Y")
    
    text = (
        f"👤 <b>Ваш Профіль</b>\n\n"
        f"🆔 ID: <code>{p['uid']}</code>\n"
        f"👤 Нік: {escape(p['name'])}\n"
        f"🔗 Юзернейм: @{p['username'] or '—'}\n\n"
        f"🎟 Промокод: <code>{p['promo_code']}</code> (-35%)\n"
        f"💎 VIP до: <b>{vip_date}</b>\n"
        f"👥 Рефералів: {p['referrals']}\n\n"
        f"📍 Місто: {p['city'] or '—'}\n"
        f"🏘 Район: {p['district'] or '—'}\n"
        f"🏠 Адреса: {p['address'] or '—'}\n"
        f"📞 Тел: {p['phone'] or '—'}"
    )
    
    kb = [
        [InlineKeyboardButton("📋 Мої замовлення", callback_data="my_orders")],
        [InlineKeyboardButton("🆔 Копіювати ID", callback_data="copy_id"), InlineKeyboardButton("🎟 Копіювати промо", callback_data="copy_promo")],
        [InlineKeyboardButton("🏙 Змінити місто", callback_data="edit_city"), InlineKeyboardButton("🏘 Змінити район", callback_data="edit_district")],
        [InlineKeyboardButton("🚚 Змінити дані доставки", callback_data="quick_order")],
        [InlineKeyboardButton("⬅ Назад", callback_data="main")]
    ]
    await update.callback_query.edit_message_caption(caption=text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(kb))

# ===================== HANDLERS: ASSORTMENT & CART =====================
async def show_assortment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [
        [InlineKeyboardButton("💨 ННС Вейпи", callback_data="cat_hhc")],
        [InlineKeyboardButton("🔌 POD Системи", callback_data="cat_pods")],
        [InlineKeyboardButton("💧 Рідини", callback_data="cat_liquids")],
        [InlineKeyboardButton("⬅ Назад", callback_data="main")]
    ]
    await update.callback_query.edit_message_caption("🛍 <b>асортимент магазину</b>\n\nОберіть категорію:", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(kb))

async def list_products(update: Update, context: ContextTypes.DEFAULT_TYPE, category_dict, title):
    btns = []
    p = context.user_data['profile']
    for pid, item in category_dict.items():
        _, _, final = calc_prices(item, p['promo_used'])
        btns.append([InlineKeyboardButton(f"{item['name']} — {final}грн", callback_data=f"item_{pid}")])
    btns.append([InlineKeyboardButton("⬅ Назад", callback_data="assortment")])
    await update.callback_query.edit_message_caption(title, reply_markup=InlineKeyboardMarkup(btns))

async def view_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    pid = int(query.data.split("_")[1])
    all_items = {**HHC_VAPES, **PODS, **LIQUIDS}
    item = all_items[pid]
    p = context.user_data['profile']
    
    base, disc, final = calc_prices(item, p['promo_used'])
    
    text = (
        f"<b>{item['name']}</b>\n\n"
        f"📝 <b>Опис:</b> {item['desc']}\n\n"
        f"💰 Базова ціна: <s>{base} грн</s>\n"
        f"🔥 Зі знижкою: <b>{disc} грн</b>\n"
        f"🎟 Фінальна (з промо): <u>{final} грн</u>\n"
    )
    
    kb = [
        [InlineKeyboardButton("🛒 Додати в кошик", callback_data=f"addcart_{pid}")],
        [InlineKeyboardButton("🩺 Швидке замовлення", callback_data=f"fastorder_{pid}")],
        [InlineKeyboardButton("⬅ Назад", callback_data="assortment")]
    ]
    await query.message.reply_photo(item['img'], caption=text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(kb))
    await query.delete_message()

async def add_to_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pid = int(update.callback_query.data.split("_")[1])
    all_items = {**HHC_VAPES, **PODS, **LIQUIDS}
    item = all_items[pid]
    context.user_data['cart'].append(item)
    await update.callback_query.answer("✅ Товар додано в кошик!")

async def view_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    cart = context.user_data.get('cart', [])
    p = context.user_data['profile']
    
    if not cart:
        await query.answer("🛒 Кошик порожній!", show_alert=True)
        return

    text = "🛒 <b>Ваш Кошик:</b>\n\n"
    total = 0
    for idx, item in enumerate(cart):
        _, _, final = calc_prices(item, p['promo_used'])
        text += f"{idx+1}. {item['name']} — {final} грн\n"
        total += final
    
    text += f"\n💰 Разом: <b>{total} грн</b>"
    
    kb = [
        [InlineKeyboardButton("✅ Оформити замовлення", callback_data="checkout")],
        [InlineKeyboardButton("🎟 Застосувати промокод", callback_data="apply_promo")] if not p['promo_used'] else [],
        [InlineKeyboardButton("🛍 В каталог", callback_data="assortment"), InlineKeyboardButton("🗑 Очистити", callback_data="clear_cart")],
        [InlineKeyboardButton("⬅ Назад", callback_data="main")]
    ]
    # Фільтрація порожніх списків
    kb = [row for row in kb if row]
    
    if query.message.photo:
        await query.message.reply_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(kb))
        await query.delete_message()
    else:
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(kb))

# ===================== HANDLERS: CHECKOUT & FLOW =====================
async def checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    p = context.user_data['profile']
    if not p['city'] or not p['phone']:
        await update.callback_query.message.reply_text("Для замовлення потрібно вказати дані доставки.")
        await start_quick_order(update, context)
        return

    kb = [[InlineKeyboardButton(gift, callback_data=f"gift_{idx}")] for idx, gift in enumerate(GIFT_LIQUIDS)]
    await update.callback_query.edit_message_text("🎁 Оберіть подарункову рідину до замовлення:", reply_markup=InlineKeyboardMarkup(kb))

async def finalize_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    gift_idx = int(query.data.split("_")[1])
    gift = GIFT_LIQUIDS[gift_idx]
    
    p = context.user_data['profile']
    cart = context.user_data['cart']
    order_id = f"GHST-{random.randint(1000, 9999)}"
    total = sum(calc_prices(item, p['promo_used'])[2] for item in cart)
    
    order_data = {
        "order_id": order_id, "user_id": p['uid'], "items": [i['name'] for i in cart],
        "gift": gift, "total": total, "address": f"{p['city']}, {p['district']}, {p['address']}",
        "phone": p['phone'], "promo_used": p['promo_used'], "timestamp": str(datetime.now())
    }
    
    context.user_data['orders'].append(order_data)
    save_order_file(order_data)
    
    # Повідомлення менеджеру
    mgr_text = (
        f"⚡ <b>Нове замовлення #{order_id}</b>\n\n"
        f"👤 Юзер: @{p['username']} ({p['uid']})\n"
        f"📦 Товари: {', '.join(order_data['items'])}\n"
        f"🎁 Подарунок: {gift}\n"
        f"📍 Адреса: {order_data['address']}\n"
        f"📞 Тел: {p['phone']}\n"
        f"💰 До оплати: <b>{total} грн</b>\n\n"
        f"🔴🔴 {PAYMENT_LINK} 🔴🔴"
    )
    mgr_kb = [[InlineKeyboardButton("💳 Оплатити", url=PAYMENT_LINK)], [InlineKeyboardButton("📤 Надіслати клієнту", callback_data=f"confirm_{order_id}")]]
    await context.bot.send_message(MANAGER_ID, mgr_text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(mgr_kb))
    
    await query.edit_message_text(f"✅ Замовлення #{order_id} прийнято!\nВартість: {total} грн\nОплатіть за посиланням вище 👆", 
                                  reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💳 Оплатити", url=PAYMENT_LINK)], [InlineKeyboardButton("🏠 Меню", callback_data="main")]]))
    context.user_data['cart'] = []

# ===================== CALLBACK ROUTER =====================
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    d = q.data
    await q.answer()
    
    try:
        if d == "main": await start(update, context)
        elif d == "profile": await show_profile(update, context)
        elif d == "assortment": await show_assortment(update, context)
        elif d == "cat_hhc": await list_products(update, context, HHC_VAPES, "💨 ННС Вейпи:")
        elif d == "cat_pods": await list_products(update, context, PODS, "🔌 POD Системи:")
        elif d == "cat_liquids": await list_products(update, context, LIQUIDS, "💧 Рідини:")
        elif d.startswith("item_"): await view_product(update, context)
        elif d.startswith("addcart_"): await add_to_cart(update, context)
        elif d == "view_cart": await view_cart(update, context)
        elif d == "checkout": await checkout(update, context)
        elif d.startswith("gift_"): await finalize_order(update, context)
        elif d == "copy_id":
            await q.message.reply_text(f"Твій ID: <code>{q.from_user.id}</code>\n(Натисніть на число, щоб скопіювати)", parse_mode="HTML")
        elif d == "copy_promo":
            await q.message.reply_text(f"Твій Промокод: <code>{context.user_data['profile']['promo_code']}</code>\n(Натисніть на код, щоб скопіювати)", parse_mode="HTML")
        elif d == "apply_promo":
            context.user_data['profile']['promo_used'] = True
            await q.edit_message_text("✅ Промокод застосовано! Ціни оновлено.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛒 Назад в кошик", callback_data="view_cart")]]))
        elif d == "referral":
            link = f"https://t.me/{(await context.bot.get_me()).username}?start=ref{q.from_user.id}"
            await q.edit_message_caption(f"🔗 <b>Ваше реферальне посилання:</b>\n{link}\n\nКожен друг додає вам +7 днів VIP!", parse_mode="HTML", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅ Назад", callback_data="main")]]))
        elif d == "policy":
            await q.edit_message_caption("📜 <b>Політика користувача</b>\n\n1. Нам 18+.\n2. Доставка НП.\n3. Оплата 100%.", parse_mode="HTML", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅ Назад", callback_data="main")]]))
        elif d == "edit_city":
            kb = [[InlineKeyboardButton(c, callback_data=f"setcity_{c}")] for c in CITIES]
            await q.edit_message_text("📍 Оберіть місто:", reply_markup=InlineKeyboardMarkup(kb))
        elif d.startswith("setcity_"):
            city = d.split("_")[1]
            context.user_data['profile']['city'] = city
            districts = CITY_DISTRICTS.get(city, ["Центральний"])
            kb = [[InlineKeyboardButton(dist, callback_data=f"setdist_{dist}")] for dist in districts]
            await q.edit_message_text(f"🏙 {city}. Оберіть район:", reply_markup=InlineKeyboardMarkup(kb))
        elif d.startswith("setdist_"):
            context.user_data['profile']['district'] = d.split("_")[1]
            context.user_data['state'] = "wait_address"
            await q.edit_message_text("🏠 Введіть адресу доставки (Вулиця, Будинок):")
        elif d == "quick_order" or d.startswith("fastorder_"):
            if d.startswith("fastorder_"):
                pid = int(d.split("_")[1])
                context.user_data['cart'] = [{**HHC_VAPES, **PODS, **LIQUIDS}[pid]]
            await q.edit_message_text("📍 Почнемо оформлення. Оберіть місто:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(c, callback_data=f"setcity_{c}")] for c in CITIES]))
    except Exception as e:
        logger.error(f"Callback error: {e}")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = context.user_data.get('state')
    text = update.message.text
    
    if state == "wait_address":
        context.user_data['profile']['address'] = text
        context.user_data['state'] = "wait_phone"
        await update.message.reply_text("📞 Введіть ваш номер телефону (напр. 0931234567):")
    elif state == "wait_phone":
        if len(text) >= 10:
            context.user_data['profile']['phone'] = text
            context.user_data['state'] = None
            await update.message.reply_text("✅ Дані збережено! Можете переходити до замовлення.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛒 В кошик", callback_data="view_cart")]]))
        else:
            await update.message.reply_text("❌ Невірний формат. Спробуйте ще раз:")

# ===================== MAIN =====================
def main():
    persistence = PicklePersistence(filepath="data/ghossty_persistence.pickle")
    app = Application.builder().token(TOKEN).persistence(persistence).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    print("🤖 Ghosty Shop Bot запущено — BotHost ready")
    app.run_polling()

if __name__ == "__main__":
    main()

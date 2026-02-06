import logging
import random
import urllib.parse
from datetime import datetime
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

# ================== КОНФІГУРАЦІЯ ==================
TOKEN = "8351638507:AAG2HP0OmYx7ip8-uZcLQCilPTfoBhtEGq0" 
MANAGER_USERNAME = "ghosstydp"
CHANNEL_URL = "https://t.me/GhostyStaffDP"
PAYMENT_URL = "https://heylink.me/ghosstyshop/"
WELCOME_PHOTO = "https://i.ibb.co/y7Q194N/1770068775663.png"
CART_PHOTO = "https://img.freepik.com/premium-vector/medical-cannabis-logo-with-marijuana-leaf-glowing-neon-sign_75817-1830.jpg"

# Знижки та дати
DISCOUNT_PERCENT = 35
DISCOUNT_MULT = 0.55  # 1.00 - 0.45
VIP_END_DATE = "25.03.2026"

# Логування (без print)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ================== БАЗА ДАНИХ ФОТО ==================
# Список з 21 фото для подів (по порядку з ТЗ)
POD_IMAGES = [
    "https://ibb.co/yFSQ5QSn", "https://ibb.co/LzgrzZjC", "https://ibb.co/Q3ZNTBvg", # 1-3 (XROS 3 Mini)
    "https://ibb.co/RkNgt1Qr", "https://ibb.co/KxvJC1bV", "https://ibb.co/WpMYBCH1", # 4-6 (XROS 5 Mini)
    "https://ibb.co/ynYwSMt6", "https://ibb.co/3mV7scXr", "https://ibb.co/xSJCgpJ5", # 7-9 (XROS Pro)
    "https://ibb.co/5XW2yN80", "https://ibb.co/93dJ8wKS", "https://ibb.co/Qj90hyyz", # 10-12 (XROS Nano)
    "https://ibb.co/LDRbQxr1", "https://ibb.co/NPHYSjN", "https://ibb.co/LhbzXD57",  # 13-15 (XROS 4)
    "https://ibb.co/hxjmpHF2", "https://ibb.co/DDkgjtV4", "https://ibb.co/r2C9JTzz", # 16-18 (XROS 5)
    "https://ibb.co/8L0JNTHz", "https://ibb.co/0RZ1VDnG", "https://ibb.co/21LPrbbj"  # 19-21 (Vmate Mini)
]

# ================== БАЗА ДАНИХ ТОВАРІВ ==================
PRODUCTS = {
    # --- HHC ---
    100: {"name": "Packwoods Purple", "cat": "hhc", "price": 549, "img": "https://i.ibb.co/DHXXSh2d/Ghost-Vape-3.jpg", "desc": "1ml | 90% HHC | Hybrid 😵‍💫\nПотужний стоун ефект, розслабляє тіло."},
    101: {"name": "Packwoods Orange", "cat": "hhc", "price": 629, "img": "https://i.ibb.co/V03f2yYF/Ghost-Vape-1.jpg", "desc": "1ml | 90% HHC | Hybrid 🍊\nКреатив та енергія, смак цитрусу."},
    102: {"name": "Packwoods Pink", "cat": "hhc", "price": 719, "img": "https://i.ibb.co/65j1901/Ghost-Vape-2.jpg", "desc": "1ml | 90% HHC | Hybrid 🌸\nМ'яка ейфорія, ідеально для вечірок."},
    103: {"name": "Whole Mint", "cat": "hhc", "price": 849, "img": "https://i.ibb.co/675LQrNB/Ghost-Vape-4.jpg", "desc": "2ml | 95% HHC | Sativa ❄️\nЧистий розум та фокус. Крижана м'ята."},
    104: {"name": "Jungle Boys White", "cat": "hhc", "price": 999, "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg", "desc": "2ml | 95% HHC | Indica 🌴\nМаксимальний релакс, глибокий сон."},

    # --- РІДИНИ (CHASER) ---
    # Всі рідини мають ID 300+, ціна 269 грн
    # Ho Ho Ho
    301: {"name": "🎃 Pumpkin Latte", "cat": "liq", "price": 269, "img": "https://ibb.co/Y7qn69Ds", "desc": "Пряний гарбузовий лате ☕️"},
    302: {"name": "🍷 Glintwine", "cat": "liq", "price": 269, "img": "https://ibb.co/wF8r7Nmc", "desc": "Зігріваючий глінтвейн 🍇"},
    303: {"name": "🎄 Christmas Tree", "cat": "liq", "price": 269, "img": "https://ibb.co/vCPGV8RV", "desc": "Хвойний аромат свята 🌲"},
    # Special Berry
    304: {"name": "🍓 Strawberry Jelly", "cat": "liq", "price": 269, "img": "https://ibb.co/mWQs09p", "desc": "Ніжне полуничне желе 🍮"},
    305: {"name": "🔮 Mystery One", "cat": "liq", "price": 269, "img": "https://ibb.co/sdfdkcFH", "desc": "Секретний мікс ягід 🫐"},
    306: {"name": "🍂 Fall Tea", "cat": "liq", "price": 269, "img": "https://ibb.co/jk14Fc8", "desc": "Осінній чай з фруктами 🍵"},
    # Limited Ultra
    307: {"name": "🍇 Grape Blackberry", "cat": "liq", "price": 269, "img": "https://ibb.co/qMdCpMhr", "desc": "Виноград та ожина 🖤"},
    308: {"name": "🥤 Cola Pomelo", "cat": "liq", "price": 269, "img": "https://ibb.co/Xrh3ZXqZ", "desc": "Кола з помело 🍊"},
    309: {"name": "🌹 Blackcurrant Rose", "cat": "liq", "price": 269, "img": "https://ibb.co/0jy5zRy9", "desc": "Смородина та троянда 🥀"},
    # Balance
    310: {"name": "💊 Vitamin", "cat": "liq", "price": 269, "img": "https://ibb.co/HpqtVjx5", "desc": "Вітамінний заряд 🍏"},
    311: {"name": "🍋 Berry Lemonade", "cat": "liq", "price": 269, "img": "https://ibb.co/Ldrvc3jx", "desc": "Ягідний лимонад 🍹"},
    312: {"name": "⚡ Energetic", "cat": "liq", "price": 269, "img": "https://ibb.co/SSDhtSc", "desc": "Класичний енергетик 🔋"},

    # --- POD-СИСТЕМИ ---
    # ID 200+. Images map to POD_IMAGES list.
    200: {
        "name": "Vaporesso XROS 3 Mini", "cat": "pod", "price": 499, 
        "colors": ["Black ⚫️", "Blue 🔵", "Pink 🌸"], 
        "imgs": [POD_IMAGES[0], POD_IMAGES[1], POD_IMAGES[2]],
        "desc": "Компактний, надійний, смачний. Топ продажів! 🔥"
    },
    201: {
        "name": "Vaporesso XROS 5 Mini", "cat": "pod", "price": 579, 
        "colors": ["Pink 🌸", "Purple 🟣", "Black ⚫️"], 
        "imgs": [POD_IMAGES[3], POD_IMAGES[4], POD_IMAGES[5]],
        "desc": "Новинка! Покращений смак та дизайн. ✨"
    },
    202: {
        "name": "Vaporesso XROS Pro", "cat": "pod", "price": 689, 
        "colors": ["Black ⚫️", "Dark Red 🔴", "Pink Red 🌺"], 
        "imgs": [POD_IMAGES[6], POD_IMAGES[7], POD_IMAGES[8]],
        "desc": "Професійний вибір. Екран, регулювання, потужність. 🔋"
    },
    203: {
        "name": "Vaporesso XROS Nano", "cat": "pod", "price": 519, 
        "colors": ["Camo 1 🪖", "Camo 2 ⚔️", "Camo 3 🛡"], 
        "imgs": [POD_IMAGES[9], POD_IMAGES[10], POD_IMAGES[11]],
        "desc": "Стильний квадратний форм-фактор. Зручно носити на шиї. 🎖"
    },
    204: {
        "name": "Vaporesso XROS 4", "cat": "pod", "price": 599, 
        "colors": ["Pink 🌸", "Black ⚫️", "Blue 🔵"], 
        "imgs": [POD_IMAGES[12], POD_IMAGES[13], POD_IMAGES[14]],
        "desc": "Сучасна класика. Алюмінієвий корпус, швидка зарядка. ⚡️"
    },
    205: {
        "name": "Vaporesso XROS 5", "cat": "pod", "price": 799, 
        "colors": ["Black ⚫️", "Pink 🌸", "Purple Stripe 🟣"], 
        "imgs": [POD_IMAGES[15], POD_IMAGES[16], POD_IMAGES[17]],
        "desc": "Флагман серії. Максимальний смак та технології. 🚀"
    },
    206: {
        "name": "Voopoo Vmate Mini", "cat": "pod", "price": 459, 
        "colors": ["Pink 🌸", "Red 🔴", "Black ⚫️"], 
        "imgs": [POD_IMAGES[18], POD_IMAGES[19], POD_IMAGES[20]],
        "desc": "Легкий, зручний, з чудовою смакопередачею. 💨"
    },
}

LOCATIONS = {
    "🏙️ Київ": ["Печерський", "Оболонський", "Дарницький", "Деснянський", "Святошинський", "Голосіївський", "Шевченківський", "Солом’янський"],
    "🏗️ Харків": ["Салтівка", "Центр", "Холодна Гора", "Слобідський", "Індустріальний", "ХТЗ", "Олексіївка"],
    "⚓ Одеса": ["Приморський", "Суворовський", "Малиновський", "Київський", "Таїрово", "Черемушки", "Слобідка"],
    "🌊 Дніпро": ["Лівобережний", "Центр", "Перемога", "Тополя", "Амур", "Чечелівський", "Шевченківський", "Отримати в Дніпрі на руки"],
    "🦁 Львів": ["Галицький", "Залізничний", "Франківський", "Шевченківський", "Сихівський", "Личаківський"],
    "⚡ Запоріжжя": ["Дніпровський", "Вознесенівський", "Олександрівський", "Комунарський", "Хортицький"],
    "🔩 Кривий Ріг": ["Центральний", "Тернівський", "Покровський", "Саксаганський", "Довгинцівський"],
    "⛲ Вінниця": ["Замостя", "Вишенька", "Поділ", "Старе місто", "Академічний", "Тяжилів"],
    "📦 Пошта": ["Вказати відділення НП"]
}

# ================== HELPERS ==================
def get_discount_price(price):
    return int(price * DISCOUNT_MULT)

def get_main_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👤 Профіль", callback_data="profile"), 
         InlineKeyboardButton("🛍️ Асортимент", callback_data="cat_list")],
        
        [InlineKeyboardButton("📍 Обрати місто", callback_data="select_city"), 
         InlineKeyboardButton("🛒 Кошик", callback_data="view_cart")],
        
        [InlineKeyboardButton("📋 Мої замовлення", callback_data="my_orders"), 
         InlineKeyboardButton("👨‍💻 Менеджер", url=f"https://t.me/{MANAGER_USERNAME}")],
        
        [InlineKeyboardButton("📜 Угода", callback_data="terms"), 
         InlineKeyboardButton("📢 GhosstyChannel", url=CHANNEL_URL)]
    ])


async def safe_edit_media(message, media, reply_markup=None):
    try:
        await message.edit_media(media=media, reply_markup=reply_markup)
    except BadRequest:
        try:
            await message.delete()
            await message.reply_photo(photo=media.media, caption=media.caption, parse_mode="HTML", reply_markup=reply_markup)
        except Exception as e:
            logger.error(f"Error safe_edit: {e}")

async def safe_edit_text(message, text, reply_markup=None):
    try:
        await message.edit_caption(caption=text, parse_mode="HTML", reply_markup=reply_markup)
    except BadRequest:
        try:
            await message.edit_text(text=text, parse_mode="HTML", reply_markup=reply_markup)
        except:
            pass

# ================== HANDLERS ==================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        if "data" not in context.user_data:
            context.user_data["data"] = {
                "cart": [],
                "orders": [],
                "city": None,
                "address": None,
                "name": user.first_name,
                "phone": None,
                "vip": True,
                "promo": f"GHOST-{random.randint(1000,9999)}"
            }
        
        ud = context.user_data["data"]
        items_count = len(PRODUCTS)
        
        txt = (
            f"👋 <b>Вітаю, {escape(user.first_name)}!</b>\n\n"
            f"🌬️ <b>Ghosty Shop</b> — твій провідник у світ релаксу.\n"
            f"🔥 У нас тільки <b>кращий та прущий стафф</b> в Україні!\n\n"
            f"📦 <b>Товарів в наявності:</b> {items_count} шт.\n"
            f"🎁 <b>Твоя знижка:</b> -35% (Промокод: <code>{ud['promo']}</code>)\n"
            f"👑 <b>VIP Статус:</b> Активний ✅\n"
            f"🚚 <b>Доставка:</b> Безкоштовна до {VIP_END_DATE}\n\n"
            f"👇 Обирай категорію:"
        )
        
        if update.message:
            await update.message.reply_photo(photo="https://i.ibb.co/y7Q194N/1770068775663.png", caption=txt, parse_mode="HTML", reply_markup=get_main_kb())
        else:
            await safe_edit_media(update.callback_query.message, InputMediaPhoto("https://i.ibb.co/y7Q194N/1770068775663.png", caption=txt), reply_markup=get_main_kb())
    except Exception as e:
        logger.error(f"Start error: {e}")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        ud = context.user_data.get("data")
        state = context.user_data.get("state")
        text = update.message.text
        
        if state == "wait_name":
            ud["name"] = text
            context.user_data["state"] = "wait_phone"
            await update.message.reply_text("📱 <b>Введіть ваш номер телефону:</b>", parse_mode="HTML")
            
        elif state == "wait_phone":
            ud["phone"] = text
            context.user_data["state"] = "wait_address"
            await update.message.reply_text("📮 <b>Введіть адресу доставки (або номер відділення НП):</b>", parse_mode="HTML")
            
        elif state == "wait_address":
            ud["address"] = text
            context.user_data["state"] = None
            await finalize_checkout(update, context)
            
    except Exception as e:
        logger.error(f"Text handler error: {e}")

async def callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        q = update.callback_query
        await q.answer()
        data = q.data
        ud = context.user_data.get("data")
        if not ud: await start(update, context); return

        # --- NAVIGATION ---
        if data == "main_menu":
            await start(update, context)
            
        elif data == "assortment":
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("😵‍💫 HHC Вейпи", callback_data="list_hhc")],
                [InlineKeyboardButton("💧 Рідини Chaser", callback_data="list_liq")],
                [InlineKeyboardButton("🔋 Pod-Системи", callback_data="list_pod")],
                [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]
            ])
            await safe_edit_text(q.message, "📂 <b>Каталог товарів:</b>\nОберіть категорію:", kb)

        # --- LISTS ---
        elif data.startswith("list_"):
            cat = data.split("_")[1]
            btns = []
            for pid, p in PRODUCTS.items():
                if p["cat"] == cat:
                    price = get_discount_price(p['price'])
                    name = p['name']
                    btns.append([InlineKeyboardButton(f"{name} | {price} грн", callback_data=f"prod_{pid}")])
            btns.append([InlineKeyboardButton("🔙 Назад", callback_data="assortment")])
            await safe_edit_text(q.message, f"📜 <b>Список товарів ({cat.upper()}):</b>", InlineKeyboardMarkup(btns))

        # --- PRODUCT VIEW ---
        elif data.startswith("prod_"):
            pid = int(data.split("_")[1])
            p = PRODUCTS[pid]
            
            # Якщо це Под - показуємо перший колір
            if p["cat"] == "pod":
                await show_pod_view(q.message, pid, 0) # 0 index for first color
                return

            new_price = get_discount_price(p['price'])
            txt = (
                f"🔥 <b>{p['name']}</b>\n\n"
                f"{p['desc']}\n\n"
                f"❌ Ціна: ~{p['price']} грн~\n"
                f"✅ <b>Ціна (-35%): {new_price} грн</b>\n"
                f"👑 VIP Доставка: 0 грн"
            )
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ Додати в кошик", callback_data=f"add_{pid}")],
                [InlineKeyboardButton("🔙 Назад", callback_data=f"list_{p['cat']}")]
            ])
            await safe_edit_media(q.message, InputMediaPhoto(p['img'], caption=txt, parse_mode="HTML"), reply_markup=kb)

        # --- POD VIEW & COLOR CHANGE ---
        elif data.startswith("podview_"):
            # podview_PID_COLORINDEX
            parts = data.split("_")
            pid = int(parts[1])
            c_idx = int(parts[2])
            await show_pod_view(q.message, pid, c_idx)

        # --- ADD TO CART LOGIC ---
        elif data.startswith("add_"):
            # add_PID or add_PID_ColorIdx
            parts = data.split("_")
            pid = int(parts[1])
            p = PRODUCTS[pid]
            
            # Якщо це ПОД, треба вибрати подарунок
            if p['cat'] == 'pod':
                c_idx = int(parts[2])
                # Зберігаємо тимчасово, що юзер хоче додати цей под
                context.user_data["temp_pod_add"] = {"pid": pid, "c_idx": c_idx}
                # Показуємо меню вибору подарунка
                await show_gift_menu(q.message)
                return

            # Звичайний товар
            item = {
                "pid": pid,
                "name": p['name'],
                "price": p['price'],
                "variant": "-",
                "gift": None
            }
            ud["cart"].append(item)
            await q.answer("✅ Товар додано в кошик!", show_alert=True)
            await start(update, context) # Return to main

        # --- GIFT SELECTION ---
        elif data.startswith("gift_"):
            # gift_LiqPID
            liq_pid = int(data.split("_")[1])
            liq_name = PRODUCTS[liq_pid]["name"]
            
            # Дістаємо збережений под
            pod_info = context.user_data.get("temp_pod_add")
            if pod_info:
                pid = pod_info["pid"]
                c_idx = pod_info["c_idx"]
                p = PRODUCTS[pid]
                color_name = p["colors"][c_idx]
                
                # Додаємо в кошик ПОД з приміткою про подарунок
                item = {
                    "pid": pid,
                    "name": p['name'],
                    "price": p['price'],
                    "variant": color_name,
                    "gift": liq_name
                }
                ud["cart"].append(item)
                
                # Очищаємо темп
                del context.user_data["temp_pod_add"]
                
                await q.message.reply_text(f"✅ Ви обрали подарунок: {liq_name} 🎁💨\nТовар додано в кошик!")
                await start(update, context)

        # --- CART & CHECKOUT ---
        elif data == "cart":
            await show_cart(update, context)
            
        elif data.startswith("del_"):
            idx = int(data.split("_")[1])
            if 0 <= idx < len(ud["cart"]):
                del ud["cart"][idx]
                await show_cart(update, context)
                
        elif data == "clear_cart":
            ud["cart"] = []
            await show_cart(update, context)
            
        elif data == "checkout":
            if not ud["cart"]:
                await q.answer("Кошик порожній!", show_alert=True)
                return
            context.user_data["state"] = "wait_name"
            await q.message.reply_text("📝 <b>Оформлення замовлення</b>\n\nЯк до вас звертатися (ПІБ)?", parse_mode="HTML")

        elif data == "fast_order":
             context.user_data["state"] = "wait_name"
             await q.message.reply_text("⚡ <b>Швидке замовлення</b>\nМенеджер допоможе підібрати товар.\n\nВведіть ваше ім'я:", parse_mode="HTML")

        # --- PROFILE & CITY ---
        elif data == "profile":
            city = ud['city'] or "Не обрано"
            addr = ud['address'] or "Не вказано"
            vip_stat = f"АКТИВНИЙ до {VIP_END_DATE} 👑" if ud['vip'] else "Неактивний"
            
            txt = (
                f"👤 *ПРОФІЛЬ КОРИСТУВАЧА*\n"
        f"━━━━━━━━━━━━━━━\n"
        f"👤 *Ім'я:* {escape(user.first_name)}\n"
        f"🏷 *Username:* @{user.username if user.username else 'відсутній'}\n"
        f"📍 *Місто:* {city}\n"
        f"🏘 *Район:* {dist}\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🎫 *Ваш промокод:* `GHOSTY35` (Знижка -35%)\n"
        f"👑 *Статус:* VIP\n"
        f"🚚 *Доставка:* ✅ Безкоштовна (до {VIP_END_DATE})\n"
        f"━━━━━━━━━━━━━━━\n"
        f"💡 *Дані доставки збережені та використовуються при замовленні.*"
      )

          kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Змінити місто/район", callback_data="select_city")],
        [InlineKeyboardButton("🔙 В головне меню", callback_data="main_menu")]
    ])
    
    # Відображення фото та тексту профілю без помилок
    try:
        await query.message.edit_media(
            InputMediaPhoto(WELCOME_PHOTO, caption=profile_text, parse_mode="Markdown"),
            reply_markup=kb
        )
    except Exception:
        # Якщо фото не завантажилось, відправляємо текстом
        await query.message.edit_caption(profile_text, reply_markup=kb, parse_mode="Markdown")

# ================== ПРИКЛАД ВІКНА ТОВАРУ ЗІ ЗНИЖКОЮ ==================
def get_product_text(p_id):
    p = PRODUCTS[p_id]
    # Розрахунок знижки 35% (множимо на 0.65)
    discount_price = int(p['price'] * 0.65)
    
    return (
        f"📦 *{p['name']}*\n\n"
        f"{p['desc']}\n\n"
        f"💰 Стара ціна: ~~{p['price']} UAH~~\n"
        f"🔥 *Ціна з промокодом (-35%):* `{discount_price} UAH`\n"
        f"🚚 *Доставка:* 0 UAH (VIP активний)"
  )
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("📍 Змінити місто", callback_data="sel_city")],
                [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]
            ])
            await safe_edit_text(q.message, txt, kb)

        elif data == "sel_city":
            btns = []
            row = []
            for city_name in LOCATIONS.keys():
                row.append(InlineKeyboardButton(city_name, callback_data=f"setcity_{city_name}"))
                if len(row) == 2:
                    btns.append(row)
                    row = []
            if row: btns.append(row)
            btns.append([InlineKeyboardButton("🔙 Назад", callback_data="main_menu")])
            await safe_edit_text(q.message, "📍 <b>Оберіть ваше місто зі списку:</b>", InlineKeyboardMarkup(btns))

        elif data.startswith("setcity_"):
            city = data.split("_")[1]
            ud["city"] = city
            # Show districts
            dists = LOCATIONS[city]
            btns = []
            row = []
            for d in dists:
                row.append(InlineKeyboardButton(d, callback_data=f"setdist_{d}"))
                if len(row) == 2:
                    btns.append(row); row = []
            if row: btns.append(row)
            await safe_edit_text(q.message, f"🏙 Місто: {city}\n<b>Оберіть район:</b>", InlineKeyboardMarkup(btns))

        elif data.startswith("setdist_"):
            dist = data.split("_")[1]
            ud["address"] = f"{ud['city']}, {dist}" # Save as part of address for simplicity
            await q.answer("✅ Локацію збережено!")
            await start(update, context)

    except Exception as e:
        logger.error(f"Callback error: {e}")

# ================== LOGIC FUNCTIONS ==================

async def show_pod_view(message, pid, c_idx):
  

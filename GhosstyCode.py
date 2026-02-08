# =================================================================
# ⚙️ SECTION 1: GLOBAL CONFIGURATION (UPDATED)
# =================================================================
TOKEN = "8351638507:AAFA9Ke-4Uln9yshcOe9CmCChdcilvx22xw"
MANAGER_ID = 7544847872
MANAGER_USERNAME = "ghosstydpbot"
CHANNEL_URL = "https://t.me/GhostyStaffDP"
WELCOME_PHOTO = "https://i.ibb.co/y7Q194N/1770068775663.png"

# Економіка
DISCOUNT_MULT = 0.65         # -35%
PROMO_DISCOUNT_MULT = 0.65   # -35%
VIP_EXPIRY = "25.03.2026"
MIN_ORDER_SUM = 300 

# Реквізити
PAYMENT_LINK = {
    "mono": "https://lnk.ua/k4xJG21Vy?utm_medium=social&utm_source=heylink.me",
    "privat": "https://lnk.ua/RVd0OW6V3?utm_medium=social&utm_source=heylink.me"
}

# Повна база товарів
CATALOG_DATA = {
    101: {"name": "💨 HHC Vape: Amnesia Haze", "price": 1450, "desc": "95% HHC. Ефект: Енергія.", "img": "https://i.ibb.co/L9vC8L3/hhc1.png", "has_gift": True},
    102: {"name": "💨 HHC Vape: Girl Scout Cookies", "price": 1450, "desc": "95% HHC. Ефект: Релакс.", "img": "https://i.ibb.co/L9vC8L3/hhc1.png", "has_gift": True},
    301: {"name": "🧪 Рідина: Apple Ice", "price": 300, "desc": "Зелене яблуко з льодом.", "img": "https://i.ibb.co/m0fD8k9/liquid.png"},
    302: {"name": "🧪 Рідина: Blueberry Mint", "price": 300, "desc": "Чорниця та м'ята.", "img": "https://i.ibb.co/m0fD8k9/liquid.png"},
    501: {"name": "🔌 Vaporesso XROS 3 Mini", "price": 950, "desc": "Надійний девайс.", "colors": ["Black", "Silver"], "img": "https://i.ibb.co/9v3Kz5K/xros3.png"},
    701: {"name": "📦 Набір 'Classic'", "price": 750, "desc": "3 будь-які рідини на вибір.", "img": "https://i.ibb.co/m0fD8k9/set.png", "has_gift": True},
    702: {"name": "📦 Набір 'Party'", "price": 1200, "desc": "5 рідин + стікерпак Gho$$tyyy.", "img": "https://i.ibb.co/m0fD8k9/set.png", "has_gift": True}
}

# Категорії для кнопок каталогу
CATEGORIES = {
    "cat_list_hhc": [101, 102],
    "cat_list_pods": [501],
    "cat_list_liquids": [301, 302],
    "cat_list_sets": [701, 702]
}

# Логування та файлова система
os.makedirs('data/logs', exist_ok=True)
os.makedirs('data/backups', exist_ok=True)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler("data/logs/ghosty_system.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("GhostyCore")


# =================================================================
# 🛠 SECTION 2: ERROR HANDLING & LOGGING
# =================================================================

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Логування помилок та сповіщення адміна."""
    # Логуємо помилку в файл
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    
    # Формуємо повідомлення про помилку для адміна
    try:
        error_msg = (
            f"🆘 <b>CRITICAL ERROR:</b>\n\n"
            f"❌ <b>Тип:</b> <code>{type(context.error).__name__}</code>\n"
            f"📝 <b>Опис:</b> <code>{escape(str(context.error))}</code>"
        )
        
        # Відправляємо сповіщення адміну
        await context.bot.send_message(chat_id=MANAGER_ID, text=error_msg)
    except Exception as e:
        logger.error(f"Could not send error message to admin: {e}")

# =================================================================

# =================================================================
# 📍 SECTION 2: ПОВНА ГЕОГРАФІЯ (11 МІСТ, 8 РАЙОНІВ КОЖНЕ)
# =================================================================

CITIES_LIST = [
    "Київ", "Дніпро", "Одеса", "Харків", "Львів", 
    "Запоріжжя", "Кривий Ріг", "Миколаїв", "Вінниця", "Полтава", "Камʼянське"
]

CITY_DISTRICTS = {
    "Київ": ["Печерський", "Шевченківський", "Подільський", "Оболонський", "Дарницький", "Дніпровський", "Desnianskyi", "Солом'янський"],
    "Дніпро": ["Центральний", "Соборний", "Шевченківський", "Чечелівський", "Новокодацький", "Амур-Нижньодніпровський", "Індустріальний", "Самарський"],
    "Одеса": ["Приморський", "Київський", "Малиновський", "Суворовський", "Аркадія", "Молдованка", "Черемушки", "Таїрове"],
    "Харків": ["Київський", "Шевченківський", "Салтівський", "Холодногірський", "Основ'янський", "Немишлянський", "Слобідський", "Індустріальний"],
    "Львів": ["Галицький", "Франківський", "Личаківський", "Сихівський", "Залізничний", "Шевченківський", "Левандівка", "Центр"],
    "Запоріжжя": ["Олександрівський", "Заводський", "Комунарський", "Дніпровський", "Вознесенівський", "Хортицький", "Шевченківський", "Бородінський"],
    "Кривий Ріг": ["Центрально-Міський", "Металургійний", "Довгинцівський", "Саксаганський", "Тернівський", "Покровський", "Інгулецький", "95-й квартал"],
    "Миколаїв": ["Центральний", "Заводський", "Інгульський", "Корабельний", "Соляні", "Намив", "ПТЗ", "Ліски"],
    "Вінниця": ["Центральний", "Замостянський", "Староміський", "Вишенька", "Поділля", "Тяжилів", "П'ятничани", "Академічний"],
    "Полтава": ["Шевченківський", "Київський", "Подільський", "Центр", "Алмазний", "Левада", "Половки", "Розсошенці"],
    "Камʼянське": ["Центральний", "Заводський", "Південний", "Дніпровський", "Соцмісто", "Черемушки", "Лівий берег", "БАМ"]
}

# Спеціальна опція для Дніпра
DNIPRO_SPECIAL = ["📍 Район (Клад)", "🏠 Адресна доставка (+50 грн)"]

# =================================================================
# 🛍 SECTION 3: ПОВНИЙ КАТАЛОГ (ДАНІ З MAIN.PY)
# =================================================================

# --- 🎁 ПОДАРУНКОВІ РІДИНИ (30мл на вибір до HHC та Наборів) ---
GIFT_LIQUIDS = {
    9001: {"name": "🎁 Pumpkin Latte 30ml", "desc": "Теплий осінній смак пряного гарбуза."},
    9002: {"name": "🎁 Glintwine 30ml", "desc": "Насичений виноград та зимові спеції."},
    9003: {"name": "🎁 Christmas Tree 30ml", "desc": "Унікальний аромат морозної хвої."},
    9004: {"name": "🎁 Strawberry Jelly 30ml", "desc": "Солодкий десертний аромат полуниці."},
    9005: {"name": "🎁 Mystery One 30ml", "desc": "Секретний мікс від Ghosty Staff."},
    9006: {"name": "🎁 Fall Tea 30ml", "desc": "Чайний аромат з нотками лимону."},
    9007: {"name": "🎁 Banana Ice 30ml", "desc": "Стиглий банан з крижаною свіжістю."},
    9008: {"name": "🎁 Wild Berries 30ml", "desc": "Класичний мікс лісових ягід."}
}

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
        "payment_url": "https://heylink.me/ghosstyshop/"
    },
    302: {
        "name": "🍷 Glintwine",
        "series": "Chaser HO HO HO Edition",
        "price": 269,
        "discount": True,
        "img": "https://i.ibb.co/wF8r7Nmc/photo-2024-12-18-00-00-01.jpg",
        "desc": "🍇 Пряний глінтвейн\n🔥 Теплий винний смак\n🎄 Святковий вайб",
        "effect": "Тепло, релакс 🔥",
        "payment_url": "https://heylink.me/ghosstyshop/"
    },
    303: {
        "name": "🎄 Christmas Tree",
        "series": "Chaser HO HO HO Edition",
        "price": 269,
        "discount": True,
        "img": "https://i.ibb.co/vCPGV8RV/photo-2024-12-18-00-00-02.jpg",
        "desc": "🌲 Хвоя + морозна свіжість\n❄️ Дуже свіжа\n🎅 Атмосфера зими",
        "effect": "Свіжість, холодок ❄️",
        "payment_url": "https://heylink.me/ghosstyshop/"
    }
}

HHC_VAPES = {
    100: {
        "name": "🌴 Packwoods Purple 1ml",
        "type": "hhc",
        "gift_liquid": True,
        "price": 699.77,
        "discount": True,
        "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg",
        "desc": "🧠 90% ННС | Гібрид\n😌 Розслаблення + легка ейфорія\n🎨 Мʼякий виноградний профіль\n🎁 Рідина у подарунок на вибір\n⚠️ Потужний ефект — починай з малого",
        "payment_url": PAYMENT_LINK
    },
    101: {
        "name": "🍊 Packwoods Orange 1ml",
        "type": "hhc",
        "gift_liquid": True,
        "price": 699.77,
        "discount": True,
        "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg",
        "desc": "🧠 90% ННС | Гібрид\n⚡ Бадьорить та фокусує\n🍊 Соковитий апельсин\n🎁 Рідина у подарунок на вибір\n🔥 Яскравий та швидкий ефект",
        "payment_url": PAYMENT_LINK
    },
    102: {
        "name": "🌸 Packwoods Pink 1ml",
        "type": "hhc",
        "gift_liquid": True,
        "price": 699.77,
        "discount": True,
        "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg",
        "desc": "🧠 90% ННС | Гібрид\n😇 Спокій + підйом настрою\n🍓 Солодко-фруктовий мікс\n🎁 Рідина у подарунок на вибір\n✨ Комфортний та плавний",
        "payment_url": PAYMENT_LINK
    },
    103: {
        "name": "🌿 Whole Mint 2ml",
        "type": "hhc",
        "gift_liquid": True,
        "price": 879.77,
        "discount": True,
        "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg",
        "desc": "🧠 95% ННС | Сатіва\n⚡ Енергія та ясність\n❄️ Свіжа мʼята\n🎁 Рідина у подарунок на вибір\n🚀 Ідеально вдень",
        "payment_url": PAYMENT_LINK
    },
    104: {
        "name": "🌴 Jungle Boys White 2ml",
        "type": "hhc",
        "gift_liquid": True,
        "price": 999.77,
        "discount": True,
        "img": "https://i.ibb.co/Zzk29HMy/Ghost-Vape-5.jpg",
        "desc": "🧠 95% ННС | Індика\n😴 Глибокий релакс\n🌲 Насичений терпкий смак\n🎁 Рідина у подарунок на вибір\n🌙 Ідеально для вечора та сну",
        "payment_url": PAYMENT_LINK
    }
}

PODS = {
    500: {
        "name": "🔌 Vaporesso XROS 3 Mini",
        "type": "pod",
        "gift_liquid": False,
        "price": 499.77,
        "discount": True,
        "img": "https://i.ibb.co/yFSQ5QSn/vaporesso-xros-3-mini.jpg",
        "desc": "🔋 1000 mAh\n💨 MTL / RDL\n⚡ Type-C зарядка\n✨ Компактний та легкий\n😌 Мʼяка тяга, стабільний смак",
        "payment_url": PAYMENT_LINK
    },
    501: {
        "name": "🔌 Vaporesso XROS 5 Mini",
        "type": "pod",
        "gift_liquid": False,
        "price": 674.77,
        "discount": True,
        "img": "https://i.ibb.co/RkNgt1Qr/vaporesso-xros-5-mini.jpg",
        "desc": "🔋 1000 mAh\n🔥 COREX 2.0\n⚡ Швидка зарядка\n🎯 Яскравий смак\n💎 Оновлений дизайн",
        "payment_url": PAYMENT_LINK
    },
    502: {
        "name": "🔌 Vaporesso XROS Pro",
        "type": "pod",
        "gift_liquid": False,
        "price": 974.77,
        "discount": True,
        "img": "https://i.ibb.co/ynYwSMt6/vaporesso-xros-pro.jpg",
        "desc": "🔋 1200 mAh\n⚡ Регулювання потужності\n💨 RDL / MTL\n🔥 Максимальний смак\n🚀 Професійний рівень",
        "payment_url": PAYMENT_LINK
    },
    503: {
        "name": "🔌 Vaporesso XROS Nano",
        "type": "pod",
        "gift_liquid": False,
        "price": 659.77,
        "discount": True,
        "img": "https://i.ibb.co/5XW2yN80/vaporesso-xros-nano.jpg",
        "desc": "🔋 1000 mAh\n💨 MTL\n🧱 Міцний корпус\n🎒 Ідеальний у дорогу\n😌 Спокійна, рівна тяга",
        "payment_url": PAYMENT_LINK
    },
    504: {
        "name": "🔌 Vaporesso XROS 4",
        "type": "pod",
        "gift_liquid": False,
        "price": 629.77,
        "discount": True,
        "img": "https://i.ibb.co/LDRbQxr1/vaporesso-xros-4.jpg",
        "desc": "🔋 1000 mAh\n🔥 COREX\n🎨 Стильний дизайн\n👌 Баланс смаку та тяги\n✨ Щоденний комфорт",
        "payment_url": PAYMENT_LINK
    },
    505: {
        "name": "🔌 Vaporesso XROS 5",
        "type": "pod",
        "gift_liquid": False,
        "price": 799.77,
        "discount": True,
        "img": "https://i.ibb.co/hxjmpHF2/vaporesso-xros-5.jpg",
        "desc": "🔋 1200 mAh\n⚡ Fast Charge\n💎 Преміальна збірка\n🔥 Максимум смаку\n🚀 Флагман серії",
        "payment_url": PAYMENT_LINK
    },
    506: {
        "name": "🔌 Voopoo Vmate Mini Pod Kit",
        "type": "pod",
        "gift_liquid": False,
        "price": 459.77,
        "discount": True,
        "img": "https://i.ibb.co/8L0JNTHz/voopoo-vmate-mini.jpg",
        "desc": "🔋 1000 mAh\n💨 Автозатяжка\n🧲 Магнітний картридж\n🎯 Простий та надійний\n😌 Легкий старт для новачків",
        "payment_url": PAYMENT_LINK
    }
}

# =================================================================
# 📜 SECTION 4: УГОДА ТА ПРАВИЛА
# =================================================================
TERMS_TEXT = (
    "📜 <b>Умови, правила, відповідальність</b>\n\n"
    "1️⃣ Проєкт має навчально-демонстраційний характер.\n"
    "2️⃣ Інформація подається виключно з ознайомчою метою.\n"
    "3️⃣ Матеріали не є рекомендацією до придбання чи використання.\n"
    "4️⃣ Користувач самостійно несе відповідальність за свої дії.\n"
    "5️⃣ Адміністрація не зберігає персональні дані.\n"
    "6️⃣ Участь у взаємодії є добровільною.\n\n"
    "⚠️ <b>Важливо:</b>\n"
    "7️⃣ Магазин не є реальним та не здійснює продаж товарів.\n"
    "8️⃣ Жоден товар не буде доставлений.\n"
    "9️⃣ Усі переказані кошти вважаються добровільним подарунком.\n"
    "🔟 Грошові операції — подарунок розробнику Gho$$tyyy/"
)
# =================================================================
# 🧠 SECTION 5: DATABASE ENGINE & PERSISTENCE
# =================================================================

def db_init():
    """
    Створення та перевірка структури бази даних SQLite.
    Це гарантує збереження даних користувачів навіть після перезавантаження сервера.
    """
    try:
        conn = sqlite3.connect('data/ghosty_v3.db')
        cursor = conn.cursor()
        
        # Таблиця користувачів: зберігаємо профіль, рефералів та VIP-статус
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                city TEXT,
                district TEXT,
                address TEXT,
                referrals INTEGER DEFAULT 0,
                referred_by INTEGER,
                orders_count INTEGER DEFAULT 0,
                is_vip INTEGER DEFAULT 0,
                reg_date TEXT,
                last_active TEXT
            )
        ''')
        
        # Таблиця замовлень: для історії та адміністрування
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                user_id INTEGER,
                items_text TEXT,
                total_sum INTEGER,
                status TEXT,
                order_date TEXT,
                payment_method TEXT,
                delivery_info TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.critical(f"Critical error during DB initialization: {e}")
        sys.exit(1)

# =================================================================
# 👤 SECTION 6: USER PROFILE & REFERRAL SYSTEM (FIXED & SYNCED)
# =================================================================

async def get_or_create_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Комплексна ініціалізація користувача.
    Обробляє: реєстрацію, реферальні посилання, VIP-дати та адресні дані.
    """
    user = update.effective_user
    uid = user.id
    current_time = datetime.now().strftime("%d.%m.%Y %H:%M")
    
    # Ініціалізація профілю в пам'яті (context.user_data)
    if "profile" not in context.user_data:
        context.user_data["profile"] = {
            "uid": uid,
            "name": escape(user.first_name) if user.first_name else "Клієнт",
            "username": f"@{user.username}" if user.username else "Приховано",
            "city": None,
            "district": None,
            "address_details": None,      # ВИПРАВЛЕНО: обов'язкове поле для адресних замовлень
            "promo_applied": False,
            "promo_code": f"GHST{uid}",   # ВИПРАВЛЕНО: персональний промокод GHST + ID
            "referrals": 0,
            "orders_count": 0,
            "vip_status": f"VIP до {VIP_EXPIRY}", # Текстовий статус для відображення
            "reg_date": current_time
        }
        
        # Обробка реферального посилання
        if context.args and context.args[0].isdigit():
            referrer_id = int(context.args[0])
            if referrer_id != uid:
                context.user_data["profile"]["referred_by"] = referrer_id
                logger.info(f"User {uid} registered via ref-link from {referrer_id}")

    # Перестраховка: якщо старий профіль не мав поля address_details, додаємо його
    if "address_details" not in context.user_data["profile"]:
        context.user_data["profile"]["address_details"] = None

    # Синхронізація з фізичною базою даних SQLite
    try:
        conn = sqlite3.connect('data/ghosty_v3.db')
        c = conn.cursor()
        c.execute('''
            INSERT OR IGNORE INTO users (user_id, username, first_name, reg_date, last_active)
            VALUES (?, ?, ?, ?, ?)
        ''', (uid, user.username, user.first_name, current_time, current_time))
        
        # Оновлення часу останньої активності та імені (якщо змінив у ТГ)
        c.execute('''
            UPDATE users 
            SET last_active = ?, username = ?, first_name = ? 
            WHERE user_id = ?
        ''', (current_time, user.username, user.first_name, uid))
        
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        logger.error(f"SQLite Sync Error: {e}")

    return context.user_data["profile"]

# =================================================================
# 🛠 SECTION 7: CORE UTILITIES (FIXED)
# =================================================================

def get_item_data(item_id):
    try:
        return CATALOG_DATA.get(int(item_id))
    except:
        return None

async def send_ghosty_message(update: Update, text: str, reply_markup=None, photo=None):
    try:
        if update.callback_query:
            msg = update.callback_query.message
            if photo:
                try:
                    await msg.edit_media(media=InputMediaPhoto(photo, caption=text, parse_mode='HTML'), reply_markup=reply_markup)
                except:
                    await msg.reply_photo(photo=photo, caption=text, reply_markup=reply_markup, parse_mode='HTML')
            else:
                if msg.photo:
                    await msg.edit_caption(caption=text, reply_markup=reply_markup, parse_mode='HTML')
                else:
                    await msg.edit_text(text=text, reply_markup=reply_markup, parse_mode='HTML')
        else:
            if photo:
                await update.message.reply_photo(photo=photo, caption=text, reply_markup=reply_markup, parse_mode='HTML')
            else:
                await update.message.reply_text(text=text, reply_markup=reply_markup, parse_mode='HTML')
    except Exception as e:
        logger.error(f"Delivery error: {e}")

async def send_ghosty_media(update, text, reply_markup, photo):
    await send_ghosty_message(update, text, reply_markup, photo)

# =================================================================
# 🏠 SECTION 8: START & PROFILE (STABLE)
# =================================================================

async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    p = context.user_data["profile"]
    text = (
        f"<b>👤 ВАШ ПРОФІЛЬ Gho$$tyyy</b>\n\n"
        f"🆔 ID: <code>{p['uid']}</code>\n"
        f"📍 Місто: {p.get('city') or 'Не вказано'}\n"
        f"🏘 Район: {p.get('district') or 'Не вказано'}\n"
        f"🎁 Промо: <code>{p['promo_code']}</code>"
    )
    keyboard = [
        [InlineKeyboardButton("📍 Дані доставки (змінити)", callback_data="menu_city")],
        [InlineKeyboardButton("🏠 На головну", callback_data="menu_start")]
    ]
    await send_ghosty_message(update, text, InlineKeyboardMarkup(keyboard))
    
    
# =================================================================
# ⚙️ SECTION 9: GLOBAL CALLBACK DISPATCHER (PARTIAL)
# =================================================================

async def main_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Центральний обробник всіх натискань кнопок.
    """
    query = update.callback_query
    data = query.data
    await query.answer() # Прибираємо годинник на кнопці
    
    logger.info(f"User {update.effective_user.id} clicked: {data}")

    # Навігація головного меню
    if data == "menu_start":
        await start_command(update, context)
    elif data == "menu_terms":
        await terms_handler(update, context)
    # Інші гілки (Каталог, Кошик, Профіль) будуть у наступних частинах
    # =================================================================
# 📍 SECTION 10: GEOGRAPHY LOGIC (CITIES & DISTRICTS)
# =================================================================

async def city_selection_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Виводить список 11 міст для вибору.
    """
    text = (
        "📍 <b>Оберіть ваше місто</b>\n\n"
        "Ми працюємо у 10 найбільших містах України та Кам'янському. "
        "Оберіть локацію, щоб побачити доступні райони та методи отримання:"
    )
    
    keyboard = []
    # Формуємо сітку кнопок 2 в ряд
    for i in range(0, len(CITIES_LIST), 2):
        row = []
        city1 = CITIES_LIST[i]
        row.append(InlineKeyboardButton(city1, callback_data=f"set_city_{city1}"))
        if i + 1 < len(CITIES_LIST):
            city2 = CITIES_LIST[i+1]
            row.append(InlineKeyboardButton(city2, callback_data=f"set_city_{city2}"))
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("🏠 Головне меню", callback_data="menu_start")])
    
    await send_ghosty_message(update, text, InlineKeyboardMarkup(keyboard))

async def district_selection_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, city_name: str):
    """
    Виводить 8 районів для обраного міста.
    """
    districts = CITY_DISTRICTS.get(city_name, [])
    text = f"📍 <b>Місто: {city_name}</b>\n\nОберіть район для отримання замовлення:"
    
    keyboard = []
    for i in range(0, len(districts), 2):
        row = []
        d1 = districts[i]
        row.append(InlineKeyboardButton(d1, callback_data=f"set_dist_{d1}"))
        if i + 1 < len(districts):
            d2 = districts[i+1]
            row.append(InlineKeyboardButton(d2, callback_data=f"set_dist_{d2}"))
        keyboard.append(row)
    
    # Спеціальна логіка для Дніпра (Адресна доставка)
    if city_name == "Дніпро":
        keyboard.append([InlineKeyboardButton("🏠 АДРЕСНА ДОСТАВКА (+50 грн)", callback_data="set_delivery_address")])
    
    keyboard.append([InlineKeyboardButton("⬅️ Назад до міст", callback_data="menu_city")])
    
    await send_ghosty_message(update, text, InlineKeyboardMarkup(keyboard))

# =================================================================
# 🚚 SECTION 11: ADDRESS DELIVERY & LOCATION SAVING
# =================================================================

async def save_location_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, dist_name: str = None, is_address: bool = False):
    """
    Зберігає обрану локацію в профіль користувача та базу SQLite.
    """
    profile = context.user_data["profile"]
    user_id = update.effective_user.id
    
    if is_address:
        profile["district"] = "Адресна доставка"
        profile["delivery_type"] = "address"
        msg = "✅ <b>Ви обрали адресну доставку по Дніпру!</b>\nВам потрібно буде вказати адресу при оформленні."
    else:
        profile["district"] = dist_name
        profile["delivery_type"] = "klad"
        msg = f"✅ <b>Локацію встановлено:</b> {profile['city']}, р-н {dist_name}"

    # Оновлення в SQLite
    try:
        conn = sqlite3.connect('data/ghosty_v3.db')
        c = conn.cursor()
        c.execute("UPDATE users SET city = ?, district = ? WHERE user_id = ?", 
                 (profile["city"], profile["district"], user_id))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Error saving location to DB: {e}")

    keyboard = [
        [InlineKeyboardButton("🛍 Перейти до покупок", callback_data="cat_main")],
        [InlineKeyboardButton("🏠 В меню", callback_data="menu_start")]
    ]
    await send_ghosty_message(update, msg, InlineKeyboardMarkup(keyboard))

# =================================================================
# 👤 SECTION 12: USER CABINET (PROFILE)
# =================================================================

async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Відображає кабінет користувача: ID, Реферали, Статус, Локація.
    """
    profile = await get_or_create_user(update, context)
    
    # Генеруємо реферальне посилання
    bot_username = (await context.bot.get_me()).username
    ref_link = f"https://t.me/{bot_username}?start={profile['uid']}"
    
    text = (
        f"👤 <b>ОСОБИСТИЙ КАБІНЕТ</b>\n\n"
        f"🆔 Ваш ID: <code>{profile['uid']}</code>\n"
        f"🏷 Статус: <b>{'VIP (-45%)' if profile['promo_applied'] else 'Покупець (-35%)'}</b>\n"
        f"📍 Місто: {profile['city'] if profile['city'] else '❌ Не обрано'}\n"
        f"🗺 Район: {profile['district'] if profile['district'] else '❌ Не обрано'}\n\n"
        f"👥 Запрошено друзів: <b>{profile['referrals']}</b>\n"
        f"🎁 Ваше реферальне посилання:\n<code>{ref_link}</code>\n\n"
        f"<i>Запрошуйте друзів та отримуйте бонуси на баланс!</i>"
    )
    
    keyboard = [
        [InlineKeyboardButton("💳 Поповнити баланс", callback_data="profile_topup")],
        [InlineKeyboardButton("📍 Змінити локацію", callback_data="menu_city")],
        [InlineKeyboardButton("🏠 Головне меню", callback_data="menu_start")]
    ]
    
    await send_ghosty_message(update, text, InlineKeyboardMarkup(keyboard))

# =================================================================
# ⚙️ SECTION 13: CALLBACK DISPATCHER (CITIES & PROFILE)
# =================================================================

# Цей шматок коду додається до основного main_callback_handler у фінальній збірці
async def process_geo_(update: Update, context: ContextTypes.DEFAULT_TYPE, data: str):
    """
    Обробка географічних колбеків.
    """
    profile = context.user_data["profile"]
    
    if data == "menu_city":
        await city_selection_menu(update, context)
        
    elif data.startswith("set_city_"):
        city = data.replace("set_city_", "")
        profile["city"] = city
        await district_selection_menu(update, context, city)
        
    elif data.startswith("set_dist_"):
        dist = data.replace("set_dist_", "")
        await save_location_handler(update, context, dist_name=dist)
        
    elif data == "set_delivery_address":
        await save_location_handler(update, context, is_address=True)
        
    elif data == "menu_profile":
        await show_profile(update, context)
        
       # =================================================================
# 🛍 SECTION 14: CATALOG ENGINE (FIXED)
# =================================================================

async def catalog_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Головне меню каталогу."""
    text = (
        "<b>🛍 КАТАЛОГ GHOSTY STAFF</b>\n\n"
        "Оберіть категорію товарів 👇\n"
        "🎁 <i>Подарунок до кожного HHC вейпу!</i>"
    )
    keyboard = [
        [InlineKeyboardButton("💨 HHC Вейпи", callback_data="cat_list_hhc")],
        [InlineKeyboardButton("🔌 POD-системи", callback_data="cat_list_pods")],
        [InlineKeyboardButton("📦 Набори рідин", callback_data="cat_list_sets")],
        [InlineKeyboardButton("🏠 Головне меню", callback_data="menu_start")]
    ]
    await send_ghosty_message(update, text, InlineKeyboardMarkup(keyboard))

# Додай цей аліас, щоб обидві назви функцій працювали
async def show_catalog_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await catalog_main_menu(update, context)
    
# =================================================================
# 🔍 SECTION 15: ITEM DETAIL VIEW & ATTRIBUTE SELECTION
# =================================================================

async def view_item_details(update: Update, context: ContextTypes.DEFAULT_TYPE, item_id: int):
    """
    Відображає фото товару, опис та ціну. 
    Додає кнопки вибору кольору або подарунка, якщо потрібно.
    """
    profile = context.user_data["profile"]
    item = get_item_data(item_id)
    
    if not item:
        await query.answer("❌ Товар не знайдено")
        return

    price = calc_price(item['price'], profile)
    caption = (
        f"<b>{item['name']}</b>\n\n"
        f"{item['desc']}\n\n"
        f"💰 Ціна для вас: <b>{price}₴</b>"
    )
    
    keyboard = []
    
    # Якщо це Pod-система, виводимо вибір кольору
    if "colors" in item:
        caption += "\n\n🌈 <b>Доступні кольори:</b>"
        for color_name in item['colors'].keys():
            keyboard.append([InlineKeyboardButton(f"🎨 {color_name}", callback_data=f"select_col_{item_id}_{color_name}")])
    
    # Якщо товар передбачає подарунок (HHC або Сет)
    elif item.get("has_gift"):
        keyboard.append([InlineKeyboardButton("🎁 ОБРАТИ ПОДАРУНОК", callback_data=f"choose_gift_{item_id}")])
    
    # Якщо товар без атрибутів (простий)
    else:
        keyboard.append([InlineKeyboardButton("🛒 Додати у кошик", callback_data=f"add_cart_{item_id}")])

    keyboard.append([InlineKeyboardButton("⬅️ Назад до списку", callback_data=f"cat_list_{'hhc' if item_id < 200 else 'pods' if item_id < 600 else 'sets'}")])
    
    photo_url = item.get('img')
    # Якщо це Pod і вже обрано колір, показуємо фото кольору
    if "selected_color" in context.user_data and context.user_data.get("current_item_id") == item_id:
        color = context.user_data["selected_color"]
        photo_url = item['colors'].get(color, photo_url)

    await send_ghosty_message(update, caption, InlineKeyboardMarkup(keyboard), photo_url)

# =================================================================
# =================================================================
# 🎁 SECTION 19: GIFT SELECTION SYSTEM (FOR HHC & OFFERS)
# =================================================================

async def gift_selection_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, item_id: int):
    """
    Відображає список доступних подарунків (наприклад, безкоштовні рідини).
    """
    main_item = get_item_data(item_id)
    if not main_item:
        await update.callback_query.answer("❌ Товар не знайдено")
        return

    # Текст для вибору подарунка
    text = (
        f"🎁 <b>АКЦІЯ: ОБЕРІТЬ ПОДАРУНОК</b>\n\n"
        f"До товару <b>{main_item['name']}</b> ви можете додати одну рідину абсолютно <b>БЕЗКОШТОВНО</b>!\n\n"
        f"Оберіть смак, який вам до вподоби 👇"
    )

    # Список ID товарів, які можуть бути подарунками (наприклад, рідини)
    # Ти можеш змінити ці ID на ті, що є у твоєму CATALOG_DATA
    gift_options = [301, 302, 303, 304] 
    
    keyboard = []
    for g_id in gift_options:
        gift_item = get_item_data(g_id)
        if gift_item:
            # Формат callback: add_{ID основного товару}_{ID подарунка}
            keyboard.append([InlineKeyboardButton(f"🧪 {gift_item['name']}", callback_data=f"add_{item_id}_{g_id}")])
    
    keyboard.append([InlineKeyboardButton("⬅️ Скасувати", callback_data=f"view_item_{item_id}")])

    # Якщо у тебе є спеціальне фото для акцій, встав GIFT_PHOTO, інакше фото товару
    photo = main_item.get('img')
    await send_ghosty_media(update, text, InlineKeyboardMarkup(keyboard), photo)
# =================================================================
# 🛒 SECTION 17: ADD TO CART HANDLERS
# =================================================================

async def add_to_cart_final(update: Update, context: ContextTypes.DEFAULT_TYPE, item_id: int, color: str = None, gift_id: int = None):
    """
    Фінальна функція додавання в кошик зі всіма параметрами.
    """
    profile = context.user_data["profile"]
    item = get_item_data(item_id)
    gift = get_item_data(gift_id) if gift_id else None
    
    final_price = calc_price(item['price'], profile)
    
    cart_entry = {
        "cart_id": str(uuid4())[:8],
        "id": item_id,
        "name": item['name'],
        "price": final_price,
        "color": color,
        "gift": gift['name'] if gift else None
    }
    
    context.user_data.setdefault("cart", []).append(cart_entry)
    
    success_text = f"✅ <b>{item['name']}</b> додано у кошик!"
    if color: success_text += f"\n🎨 Колір: {color}"
    if gift: success_text += f"\n🎁 Подарунок: {gift['name']}"
    
    keyboard = [
        [InlineKeyboardButton("🛒 ПЕРЕЙТИ В КОШИК", callback_data="menu_cart")],
        [InlineKeyboardButton("🛍 Продовжити покупки", callback_data="cat_main")]
    ]
    
    await send_ghosty_message(update, success_text, InlineKeyboardMarkup(keyboard))

# =================================================================
# ⚙️ SECTION 18: CATALOG SYSTEM (CALLBACKS & ADD TO CART)
# =================================================================

async def process_catalog_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE, data: str):
    """
    Центральний обробник натискань у каталозі.
    """
    # 1. Головне меню каталогу
    if data == "cat_main":
        await catalog_main_menu(update, context)
        
    # 2. Перегляд детальної картки товару
    elif data.startswith("view_item_"):
        item_id = int(data.replace("view_item_", ""))
        item = get_item_data(item_id)
        
        if not item:
            await update.callback_query.answer("❌ Товар не знайдено")
            return

        text = f"<b>{item['name']}</b>\n\n{item['desc']}\n\n💰 Ціна: <b>{item['price']}₴</b>"
        keyboard = []
        
        # Вибір кольору (для ПОД-систем)
        if "colors" in item:
            text += "\n\n🌈 <b>Оберіть колір пристрою:</b>"
            for color in item["colors"]:
                keyboard.append([InlineKeyboardButton(f"🎨 {color}", callback_data=f"add_{item_id}_{color}")])
        
        # Вибір подарунка (для HHC вейпів)
        elif item.get("has_gift"):
            keyboard.append([InlineKeyboardButton("🎁 Обрати рідину у подарунок", callback_data=f"choose_gift_{item_id}")])
        
        # Звичайний товар (рідини)
        else:
            keyboard.append([InlineKeyboardButton("🛒 Додати в кошик", callback_data=f"add_{item_id}_none")])
            
        keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="cat_main")])
        await send_ghosty_media(update, text, InlineKeyboardMarkup(keyboard), item.get('img'))

    # 3. Виклик меню подарунків
    elif data.startswith("choose_gift_"):
        item_id = int(data.replace("choose_gift_", ""))
        await gift_selection_menu(update, context, item_id)

    # 4. ФІНАЛЬНЕ ДОДАВАННЯ В КОШИК (через handler нижче)
    elif data.startswith("add_"):
        await add_to_cart_handler(update, context, data)

async def add_to_cart_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, data: str):
    """
    Логіка додавання: обробляє колір, подарунок та застосовує знижку -35%.
    """
    parts = data.split("_")
    item_id = int(parts[1])
    extra_info = parts[2] if len(parts) > 2 else "none"
    
    item = get_item_data(item_id)
    if not item:
        await update.callback_query.answer("❌ Помилка товару")
        return

    # Копіюємо дані товару, щоб не змінити оригінал в базі
    cart_item = item.copy()
    
    # АВТОМАТИЧНА ЗНИЖКА -35% (Ціна = 65% від початкової)
    cart_item['price'] = int(cart_item['price'] * 0.65)

    # Додаємо інформацію про колір
    if extra_info != "none" and not extra_info.isdigit():
        cart_item['name'] = f"{item['name']} (Колір: {extra_info})"
    
    # Додаємо інформацію про подарунок (якщо вибрано ID рідини)
    elif extra_info.isdigit():
        gift = get_item_data(int(extra_info))
        if gift:
            cart_item['name'] = f"{item['name']} + 🎁 {gift['name']}"

    # Ініціалізація кошика, якщо він порожній
    if "cart" not in context.user_data or context.user_data["cart"] is None:
        context.user_data["cart"] = []
    
    context.user_data["cart"].append(cart_item)
    
    await update.callback_query.answer(f"✅ Додано: {cart_item['name']}")
    
    # Після додавання відправляємо користувача в кошик для оформлення
    await show_cart(update, context)
        
# =================================================================
# 🛒 SECTION 19: THE SHOPPING CART SYSTEM (FIXED)
# =================================================================

async def show_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    profile = context.user_data.get("profile", {})
    cart = context.user_data.get("cart", [])
    
    if not cart:
        text = "🛒 <b>Ваш кошик порожній</b>\n\nОберіть щось цікаве в каталозі!"
        keyboard = [[InlineKeyboardButton("🛍 В каталог", callback_data="cat_main")]]
        await send_ghosty_message(update, text, InlineKeyboardMarkup(keyboard))
        return

    total_sum = sum(item['price'] for item in cart)
    text = "🛒 <b>ВАШ КОШИК</b>\n⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
    
    keyboard = []
    for idx, item in enumerate(cart):
        text += f"<b>{idx+1}. {item['name']}</b> — <code>{item['price']}₴</code>\n"
        keyboard.append([InlineKeyboardButton(f"❌ Видалити {item['name'][:15]}...", callback_data=f"cart_del_{idx}")])

    text += f"⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n💰 Разом: <b>{total_sum}₴</b>"

    if not profile.get("city") or not profile.get("district"):
        text += "\n\n⚠️ <i>Оберіть локацію для оформлення!</i>"
        keyboard.append([InlineKeyboardButton("📍 Обрати локацію", callback_data="menu_city")])
    else:
        keyboard.append([InlineKeyboardButton("✅ ОФОРМИТИ ЗАМОВЛЕННЯ", callback_data="cart_checkout")])

    keyboard.append([InlineKeyboardButton("🗑 Очистити кошик", callback_data="cart_clear")])
    keyboard.append([InlineKeyboardButton("🏠 На головну", callback_data="menu_start")])
    
    await send_ghosty_message(update, text, InlineKeyboardMarkup(keyboard))
    
# =================================================================
# 🛠 SECTION 20: CART MODIFICATION HANDLERS
# =================================================================

async def cart_action_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, data: str):
    """
    Обробка видалення та очищення кошика.
    """
    cart = context.user_data.get("cart", [])
    
    if data.startswith("cart_del_"):
        idx = int(data.replace("cart_del_", ""))
        if 0 <= idx < len(cart):
            removed = cart.pop(idx)
            await update.callback_query.answer(f"🗑 {removed['name']} видалено")
        await show_cart(update, context)
        
    elif data == "cart_clear":
        context.user_data["cart"] = []
        await update.callback_query.answer("🧹 Кошик очищено")
        await show_cart(update, context)

# =================================================================
# 💳 SECTION 21: CHECKOUT & PAYMENT SELECTION (UPDATED)
# =================================================================

async def checkout_init(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Початок оформлення: перевірка даних, генерація суми з копійками та вибір банку.
    """
    profile = await get_or_create_user(update, context)
    cart = context.user_data.get("cart", [])
    
    # 1. Перевірка чи обрана локація
    if not profile.get("city") or not profile.get("district"):
        await update.callback_query.answer("⚠️ Спочатку оберіть місто та район!", show_alert=True)
        # Викликаємо меню вибору міста
        await process_geo_callbacks(update, context, "menu_city")
        return

    # 2. Перевірка кошика
    if not cart:
        await update.callback_query.answer("🛒 Кошик порожній!", show_alert=True)
        return

    # 3. Перевірка телефону (якщо немає, ставимо заглушку або просимо вказати)
    if "phone" not in profile or not profile["phone"]:
        profile["phone"] = "Вказано при оплаті"

    # 4. Розрахунок суми
    total_sum = sum(item['price'] for item in cart)
    
    # Генерація копійок (0.01 - 0.99) для ідентифікації платежу
    cents = random.randint(1, 99) / 100
    final_amount = float(total_sum) + cents
    
    # 5. Генерація ID замовлення (Коментар GHSTXXXX)
    order_id = f"GHST{random.randint(1000, 9999)}"
    
    # Зберігаємо дані замовлення в пам'ять
    context.user_data["current_order"] = {
        "amount": final_amount,
        "order_id": order_id,
        "raw_sum": total_sum
    }

    text = (
        f"<b>📦 ОФОРМЛЕННЯ ЗАМОВЛЕННЯ #{order_id}</b>\n\n"
        f"👤 <b>Клієнт:</b> {profile['name']}\n"
        f"📞 <b>Телефон:</b> {profile['phone']}\n"
        f"📍 <b>Локація:</b> {profile['city']}, {profile['district']}\n"
        f"💎 <b>Статус:</b> VIP (Доставка 0₴)\n"
        f"⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        f"💰 <b>СУМА ДО СПЛАТИ: {final_amount:.2f}₴</b>\n\n"
        f"⚠️ <b>КОМЕНТАР ОБОВ'ЯЗКОВО:</b> <code>{order_id}</code>\n"
        f"<i>Сума має бути точною до копійок! Це ваш ключ до швидкої видачі.</i>\n\n"
        f"Оберіть банк для оплати:"
    )
    
    keyboard = [
        [InlineKeyboardButton("💳 Оплата MONOBANK", callback_data="pay_mono")],
        [InlineKeyboardButton("💳 Оплата PRIVAT24", callback_data="pay_privat")],
        [InlineKeyboardButton("👨‍💻 Замовити у менеджера", url="https://t.me/ghosstydp")],
        [InlineKeyboardButton("⬅️ Змінити місто/район", callback_data="menu_city")],
        [InlineKeyboardButton("❌ Назад до кошика", callback_data="menu_cart")]
    ]
    
    await send_ghosty_message(update, text, InlineKeyboardMarkup(keyboard))

# =================================================================
# 🔑 SECTION 22: PROMOCODE & VIP LOGIC
# =================================================================

async def apply_promo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Ручне введення промокоду через MessageHandler.
    """
    user_text = update.message.text.strip().upper()
    profile = context.user_data["profile"]
    
    # Список робочих промокодів
    valid_promos = ["GHOSTY2026", "VIP45", "START35"]
    
    if user_text in valid_promos or user_text == profile.get("promo_code"):
        profile["promo_applied"] = True
        # Оновлюємо ціни в кошику, якщо вони там вже були
        if "cart" in context.user_data:
            for item in context.user_data["cart"]:
                # Перераховуємо ціну кожного товару зі знижкою 45%
                base_item = get_item_data(item['id'])
                if base_item:
                    item['price'] = int(base_item['price'] * PROMO_DISCOUNT_MULT)
        
        await update.message.reply_text(
            "✅ <b>ПРОМОКОД АКТИВОВАНО!</b>\nВаша знижка тепер становить <b>45%</b> на всі товари.",
            parse_mode=ParseMode.HTML
        )
        await start_command(update, context)
    else:
        await update.message.reply_text("❌ <b>Невірний промокод.</b> Спробуйте ще раз або зверніться до менеджера.")

# =================================================================
# ⚙️ SECTION 23: CALLBACK DISPATCHER (CART & CHECKOUT)
# =================================================================

async def process_cart_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE, data: str):
    """
    Інтеграція колбеків кошика в головний цикл.
    """
    if data == "menu_cart":
        await show_cart(update, context)
    elif data.startswith("cart_"):
        await cart_action_handler(update, context, data)
    elif data == "cart_checkout":
        await checkout_init(update, context)
    elif data.startswith("pay_"):
        # Буде реалізовано в Частині 6 (Платіжні шлюзи та реквізити)
        await query.answer("⌛ Перехід до оплати...")

# =================================================================
# 📋 SECTION 24: STATE MANAGEMENT (DNP ADDRESS COLLECTION)
# =================================================================

async def handle_user_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Глобальний обробник текстового вводу.
    Використовується для збору адреси доставки та введення промокодів.
    """
    user_id = update.effective_user.id
    text = update.message.text
    state = context.user_data.get("state")

    # Якщо користувач вводить адресу для Дніпра
    if state == "WAITING_ADDRESS":
        if len(text) < 10:
            await update.message.reply_text("❌ <b>Адреса занадто коротка.</b>\nБудь ласка, вкажіть вулицю, номер будинку та під'їзд:")
            return
        
        context.user_data["profile"]["address_details"] = text
        context.user_data["state"] = None
        
        # Повертаємо до вибору оплати після введення адреси
        await update.message.reply_text(f"✅ <b>Адресу збережено:</b>\n<code>{text}</code>")
        await checkout_init(update, context)

    # Якщо користувач вводить промокод
    elif state == "WAITING_PROMO":
        await apply_promo_command(update, context)
    
    else:
        # Стандартна відповідь на невідомий текст
        await update.message.reply_text("🤖 Використовуйте кнопки меню для навігації.")

# =================================================================
# 💳 SECTION 25: PAYMENT GATEWAYS LOGIC
# =================================================================

async def payment_selection_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, method: str):
    """
    Видача реквізитів та посилань на оплату з інструкціями.
    """
    profile = context.user_data.get("profile", {})
    order_data = context.user_data.get("current_order", {})
    
    if not order_data:
        await update.callback_query.answer("⚠️ Помилка замовлення. Спробуйте ще раз.")
        await start_command(update, context)
        return

    amount = order_data['amount']
    order_id = order_data['order_id']
    
    # Вибір посилання залежно від банку
    pay_url = PAYMENT_LINK['mono'] if method == "mono" else PAYMENT_LINK['privat']
    bank_name = "MONOBANK" if method == "mono" else "PRIVAT24"

    pay_text = (
        f"<b>🚀 ОПЛАТА ЧЕРЕЗ {bank_name}</b>\n\n"
        f"💵 Точна сума: <b>{amount:.2f}₴</b>\n"
        f"📝 Коментар: <code>{order_id}</code>\n\n"
        f"1️⃣ Перейдіть за посиланням нижче\n"
        f"2️⃣ Вкажіть суму <b>з копійками</b>\n"
        f"3️⃣ В полі 'Коментар' впишіть <code>{order_id}</code>\n"
        f"4️⃣ Після оплати завантажте квитанцію менеджеру\n\n"
        f"⬇️ <b>ПОСИЛАННЯ НА ОПЛАТУ</b> ⬇️\n{pay_url}"
    )

    keyboard = [
        [InlineKeyboardButton("✅ Я ОПЛАТИВ (Надіслати чек)", url="https://t.me/ghosstydp")],
        [InlineKeyboardButton("🧾 ПІДТВЕРДИТИ В БОТІ", callback_data=f"confirm_pay_{order_id}")],
        [InlineKeyboardButton("⬅️ Змінити спосіб оплати", callback_data="cart_checkout")]
    ]

    await send_ghosty_message(update, pay_text, InlineKeyboardMarkup(keyboard))

# =================================================================
# 🛡 SECTION 26: ORDER CONFIRMATION (ADMIN NOTIFICATION)
# =================================================================

async def confirm_payment_request(update: Update, context: ContextTypes.DEFAULT_TYPE, pay_id: str):
    """
    Відправка замовлення менеджеру для ручної перевірки.
    """
    profile = context.user_data["profile"]
    cart = context.user_data["cart"]
    order_data = context.user_data.get("current_order", {})
    
    # Формування звіту для адміна
    items_summary = "\n".join([f"- {i['name']} ({i['price']}₴) {'+ 🎁' if i.get('gift') else ''}" for i in cart])
    
    admin_msg = (
        f"🔔 <b>НОВЕ ЗАМОВЛЕННЯ #{pay_id}</b>\n\n"
        f"👤 Клієнт: {profile['name']} ({profile['username']})\n"
        f"🆔 ID: <code>{profile['uid']}</code>\n\n"
        f"📍 Локація: {profile['city']}, {profile['district']}\n"
        f"🏠 Адреса: {profile.get('address_details', 'Клад')}\n\n"
        f"🛒 Товари:\n{items_summary}\n\n"
        f"💰 <b>СУМА: {order_data['amount']}₴</b>\n"
        f"💳 Спосіб: Оплата перевіряється..."
    )

    try:
        # Відправка менеджеру
        await context.bot.send_message(
            chat_id=MANAGER_ID,
            text=admin_msg,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Підтвердити", callback_data=f"adm_approve_{pay_id}_{profile['uid']}"),
                 InlineKeyboardButton("❌ Відхилити", callback_data=f"adm_decline_{pay_id}_{profile['uid']}")]
            ])
        )
        
        # Повідомлення користувачу
        user_msg = (
            f"✅ <b>Заявка на замовлення #{pay_id} прийнята!</b>\n\n"
            "Менеджер перевірить оплату протягом 15-30 хвилин. "
            "Ви отримаєте сповіщення про зміну статусу.\n\n"
            "Дякуємо, що ви з Ghosty Staff! 🔥"
        )
        
        # Очищуємо кошик після успішного запиту
        context.user_data["cart"] = []
        
        await send_ghosty_message(update, user_msg, InlineKeyboardMarkup([[InlineKeyboardButton("🏠 В меню", callback_data="menu_start")]]))

    except Exception as e:
        logger.error(f"Failed to send admin notification: {e}")
        await update.callback_query.answer("⚠️ Помилка зв'язку з сервером. Спробуйте пізніше.", show_alert=True)

# =================================================================
# ⚙️ SECTION 27: CALLBACK DISPATCHER (PAYMENT & ADMIN)
# =================================================================

async def process_payment_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE, data: str):
    """
    Обробка платіжних колбеків.
    """
    if data == "pay_card":
        await payment_selection_handler(update, context, "card")
    elif data == "pay_crypto":
        await payment_selection_handler(update, context, "crypto")
    elif data.startswith("confirm_pay_"):
        p_id = data.replace("confirm_pay_", "")
        await confirm_payment_request(update, context, p_id)

# =================================================================
# ⚙️ SECTION 29: GLOBAL CALLBACK DISPATCHER (FIXED)
# =================================================================

async def global_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Центральний розподільник для всіх кнопок бота."""
    query = update.callback_query
    data = query.data
    
    # Захист від порожніх даних профілю
    if "profile" not in context.user_data:
        await get_or_create_user(update, context)
    if context.user_data.get("cart") is None:
        context.user_data["cart"] = []

    try:
        # Відповідаємо відразу, щоб прибрати іконку завантаження
        await query.answer()

        # 1. Основна навігація
        if data == "menu_start": 
            await start_command(update, context)
        elif data == "menu_terms": 
            await terms_handler(update, context)
        elif data == "menu_profile": 
            await show_profile(update, context)
        elif data == "menu_cart": 
            await show_cart(update, context)
        elif data == "menu_city": 
            await city_selection_menu(update, context)
        
        # 2. Локації (Міста/Райони)
        elif any(x in data for x in ["set_city_", "set_dist_", "delivery_address"]):
            await process_geo_(update, context, data)
        
        # 3. Каталог (Категорії, товари, подарунки)
        elif any(x in data for x in ["cat_", "view_item_", "add_", "choose_gift_"]):
            if data == "cat_main":
                await catalog_main_menu(update, context)
            else:
                await process_catalog_callbacks(update, context, data)
        
        # 4. Кошик та Оформлення
        elif "cart_" in data: 
            if data == "cart_checkout": 
                await checkout_init(update, context)
            else: 
                await cart_action_handler(update, context, data)
        
        # 5. Оплата
        elif data in ["pay_mono", "pay_privat"]:
            bank = data.replace("pay_", "")
            await payment_selection_handler(update, context, bank)
        elif "confirm_pay_" in data:
            await process_payment_callbacks(update, context, data)
        
        # 6. Адмінка
        elif data.startswith("adm_"):
            if update.effective_user.id == MANAGER_ID:
                await admin_decision_handler(update, context)
                
    except Exception as e:
        logger.error(f"🔴 Callback Dispatcher Error: {e}", exc_info=True)

# =================================================================
# 🚀 SECTION 30: FINAL RUNNER (ANTI-CONFLICT VERSION)
# =================================================================

def main():
    """Запуск бота з примусовим скиданням конфліктів."""
    
    # 1. Створюємо папки, якщо їх немає
    for path in ['data', 'data/logs']:
        if not os.path.exists(path):
            os.makedirs(path)

    # 2. База даних
    db_init()
    
    # 3.Persistence (Збереження стану)
    pers = PicklePersistence(filepath="data/ghosty_data.pickle")
    
    # 4. Налаштування Defaults
    from telegram import LinkPreviewOptions
    defaults = Defaults(
        parse_mode=ParseMode.HTML, 
        link_preview_options=LinkPreviewOptions(is_disabled=True)
    )
    
    # 5. Створення додатка
    app = Application.builder() \
        .token(TOKEN) \
        .persistence(pers) \
        .defaults(defaults) \
        .build()

    # 6. Реєстрація хендлерів
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_input))
    app.add_handler(CallbackQueryHandler(global_callback_handler))
    
    # 7. Обробник помилок
    if 'error_handler' in globals():
        app.add_error_handler(error_handler)

    print("--- [ GHO$$TY STAFF: SYSTEM ONLINE ] ---")
    print("--- [ Спроба підключення до Telegram... ] ---")
    
    # drop_pending_updates=True — ВИРІШУЄ КОНФЛІКТИ ПРИ СТАРТІ
    # close_if_open=True — Додатковий захист від подвійного запуску
    app.run_polling(drop_pending_updates=True, close_if_open=True)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(f"Критична помилка запуску: {e}")

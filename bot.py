import asyncio
import aiosqlite
import os
import sys
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters
)

# ==============================
# 🔑 تنظیمات پیکربندی
# ==============================
# توکن را از متغیر محیطی بخوانید
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("لطفاً متغیر محیطی TELEGRAM_BOT_TOKEN را تنظیم کنید!")

ADMIN_PASSWORD = "1186"

# رمز کشورها (چهاررقمی، منحصر به فرد)
COUNTRY_PASSWORDS = {
    "United States 🇺🇸": "1776",
    "Britain 🇬🇧": "2021",
    "France 🇫🇷": "1789",
    "Israel 🇮🇱": "1948",
    "South Korea 🇰🇷": "1953",
    "Saudi Arabia 🇸🇦": "1932",
    "Qatar 🇶🇦": "1971",
    "Russia 🇷🇺": "1917",
    "China 🇨🇳": "1949",
    "Iran 🇮🇷": "1979",
    "North Korea 🇰🇵": "1958",
    "Pakistan 🇵🇰": "1947",
    "Lebanon 🇱🇧": "1943",
    "Palestine 🇵🇸": "1988",
    "India 🇮🇳": "1950",
    "Japan 🇯🇵": "1945",
    "Germany 🇩🇪": "1990",
    "Italy 🇮🇹": "1861",
    "Mexico 🇲🇽": "1821",
    "Spain 🇪🇸": "1492"
}

# بودجه اولیه هر کشور
INITIAL_BUDGETS = {
    "United States 🇺🇸": 1_200_000_000,
    "Britain 🇬🇧": 1_000_000_000,
    "France 🇫🇷": 800_000_000,
    "Israel 🇮🇱": 600_000_000,
    "South Korea 🇰🇷": 600_000_000,
    "Saudi Arabia 🇸🇦": 500_000_000,
    "Qatar 🇶🇦": 400_000_000,
    "Russia 🇷🇺": 1_200_000_000,
    "China 🇨🇳": 1_100_000_000,
    "Iran 🇮🇷": 1_000_000_000,
    "North Korea 🇰🇵": 800_000_000,
    "Pakistan 🇵🇰": 600_000_000,
    "Lebanon 🇱🇧": 400_000_000,
    "Palestine 🇵🇸": 300_000_000,
    "India 🇮🇳": 1_000_000_000,
    "Japan 🇯🇵": 800_000_000,
    "Germany 🇩🇪": 800_000_000,
    "Italy 🇮🇹": 700_000_000,
    "Mexico 🇲🇽": 500_000_000,
    "Spain 🇪🇸": 600_000_000
}

# منابع هر کشور
COUNTRY_RESOURCES = {
    "United States 🇺🇸": ["Iron", "Aluminum", "Copper", "Gold", "Platinum", "Uranium"],
    "Britain 🇬🇧": ["Iron", "Aluminum", "Gold", "Uranium"],
    "France 🇫🇷": ["Iron", "Copper", "Gold", "Uranium"],
    "Israel 🇮🇱": ["Iron", "Aluminum", "Gold"],
    "South Korea 🇰🇷": ["Iron", "Aluminum", "Gold", "Uranium"],
    "Saudi Arabia 🇸🇦": ["Iron", "Aluminum", "Gold", "Platinum"],
    "Qatar 🇶🇦": ["Aluminum"],
    "Russia 🇷🇺": ["Iron", "Aluminum", "Copper", "Gold", "Platinum", "Uranium"],
    "China 🇨🇳": ["Iron", "Aluminum", "Copper", "Gold", "Platinum", "Uranium"],
    "Iran 🇮🇷": ["Iron", "Aluminum", "Copper", "Gold", "Platinum", "Uranium"],
    "North Korea 🇰🇵": ["Iron", "Aluminum", "Gold", "Uranium"],
    "Pakistan 🇵🇰": ["Iron", "Gold", "Uranium"],
    "Lebanon 🇱🇧": ["Iron", "Aluminum", "Copper"],
    "Palestine 🇵🇸": ["Iron", "Aluminum"],
    "India 🇮🇳": ["Iron", "Aluminum", "Copper"],
    "Japan 🇯🇵": ["Iron", "Aluminum", "Gold", "Platinum"],
    "Germany 🇩🇪": ["Iron", "Copper", "Gold", "Platinum"],
    "Italy 🇮🇹": ["Iron", "Gold"],
    "Mexico 🇲🇽": ["Iron", "Copper", "Gold"],
    "Spain 🇪🇸": ["Iron", "Copper", "Gold", "Platinum"]
}

# سازه‌های اولیه غیرشهری
INITIAL_STRUCTURES = {
    "United States 🇺🇸": {"civilian_factory": 5, "military_factory": 5, "missile_launcher": 10, "warehouse": 2},
    "Britain 🇬🇧": {"civilian_factory": 4, "military_factory": 3, "missile_launcher": 5, "warehouse": 2},
    "France 🇫🇷": {"civilian_factory": 4, "military_factory": 4, "missile_launcher": 4, "warehouse": 2},
    "Israel 🇮🇱": {"civilian_factory": 3, "military_factory": 4, "missile_launcher": 7, "warehouse": 2},
    "South Korea 🇰🇷": {"civilian_factory": 2, "military_factory": 4, "missile_launcher": 8, "warehouse": 2},
    "Saudi Arabia 🇸🇦": {"civilian_factory": 4, "military_factory": 3, "missile_launcher": 4, "warehouse": 2},
    "Qatar 🇶🇦": {"civilian_factory": 2, "military_factory": 2, "missile_launcher": 2, "warehouse": 2},
    "Russia 🇷🇺": {"civilian_factory": 4, "military_factory": 8, "missile_launcher": 8, "warehouse": 4},
    "China 🇨🇳": {"civilian_factory": 6, "military_factory": 3, "missile_launcher": 5, "warehouse": 2},
    "Iran 🇮🇷": {"civilian_factory": 4, "military_factory": 5, "missile_launcher": 10, "warehouse": 2},
    "North Korea 🇰🇵": {"civilian_factory": 2, "military_factory": 6, "missile_launcher": 8, "warehouse": 3},
    "Pakistan 🇵🇰": {"civilian_factory": 2, "military_factory": 2, "missile_launcher": 2, "warehouse": 1},
    "Lebanon 🇱🇧": {"civilian_factory": 4, "military_factory": 3, "missile_launcher": 5, "warehouse": 2},
    "Palestine 🇵🇸": {"civilian_factory": 1, "military_factory": 1, "missile_launcher": 1, "warehouse": 1},
    "India 🇮🇳": {"civilian_factory": 4, "military_factory": 4, "missile_launcher": 5, "warehouse": 2},
    "Japan 🇯🇵": {"civilian_factory": 3, "military_factory": 5, "missile_launcher": 6, "warehouse": 2},
    "Germany 🇩🇪": {"civilian_factory": 5, "military_factory": 4, "missile_launcher": 5, "warehouse": 2},
    "Italy 🇮🇹": {"civilian_factory": 3, "military_factory": 3, "missile_launcher": 4, "warehouse": 2},
    "Mexico 🇲🇽": {"civilian_factory": 2, "military_factory": 2, "missile_launcher": 3, "warehouse": 1},
    "Spain 🇪🇸": {"civilian_factory": 3, "military_factory": 3, "missile_launcher": 4, "warehouse": 2}
}

# نیروهای اولیه ارتش
INITIAL_ARMY_TEXTS = {
    "United States 🇺🇸": "Air: 2× F-22 Raptor, 2× F-35 | Ground: 5× M1 Abrams | Navy: 1× Arleigh Burke-class",
    "Britain 🇬🇧": "Air: 2× Eurofighter Typhoon | Ground: 5× Challenger 2 | Navy: 1× Type 45 destroyer",
    "France 🇫🇷": "Air: 2× Rafale, 1× Mirage 2000 | Ground: 5× Leclerc | Navy: 1× Charles de Gaulle carrier",
    "Israel 🇮🇱": "Air: 3× F-35 | Ground: 10× Merkava | Navy: 2× Sa'ar 6 corvettes",
    "South Korea 🇰🇷": "Air: 2× KF-21, 2× F-15K | Ground: 10× K2 Black Panther | Navy: 1× Sejong-class destroyer",
    "Saudi Arabia 🇸🇦": "Air: 2× F-15SA | Ground: 10× M1A2 | Navy: 2× Al Riyadh frigates",
    "Qatar 🇶🇦": "Air: 2× Rafale | Ground: 5× Leopard 2 | Navy: 2× Al Zubarah corvettes",
    "Russia 🇷🇺": "Air: 2× Su-57, 2× Su-35 | Ground: 10× T-90 | Navy: 1× Admiral Gorshkov frigate",
    "China 🇨🇳": "Air: 2× J-20, 2× J-16 | Ground: 10× Type 99 | Navy: 1× Type 055 destroyer",
    "Iran 🇮🇷": "Air: 2× F-14, 2× Su-30 | Ground: 10× Zulfiqar | Navy: 2× Ghadir submarines",
    "North Korea 🇰🇵": "Air: 2× MiG-29 | Ground: 20× T-62 | Navy: 2× Romeo-class subs",
    "Pakistan 🇵🇰": "Air: 2× JF-17 | Ground: 10× Al-Khalid | Navy: 1× Zulfiquar frigate",
    "Lebanon 🇱🇧": "Air: 2× Hawker Hunter | Ground: 10× M48 Patton | Navy: 2× patrol boats",
    "Palestine 🇵🇸": "Air: None | Ground: 50× infantry | Navy: None",
    "India 🇮🇳": "Air: 2× Rafale, 2× Tejas | Ground: 10× Arjun | Navy: 1× INS Vikrant carrier",
    "Japan 🇯🇵": "Air: 2× F-35, 2× F-15J | Ground: 10× Type 10 | Navy: 1× Izumo-class carrier",
    "Germany 🇩🇪": "Air: 2× Eurofighter | Ground: 10× Leopard 2A7 | Navy: 1× F125 frigate",
    "Italy 🇮🇹": "Air: 2× Eurofighter, 2× F-35 | Ground: 10× Ariete | Navy: 1× Cavour carrier",
    "Mexico 🇲🇽": "Air: 2× F-5 | Ground: 10× M60 | Navy: 2× Sierra-class frigates",
    "Spain 🇪🇸": "Air: 2× Eurofighter | Ground: 10× Leopard 2E | Navy: 1× Álvaro de Bazán frigate"
}

# تعاریف سازه‌ها
NON_CITY_STRUCTURES = {
    "civilian_factory": {"name": "Civilian Factory 🏭", "cost": 1_000_000, "time_hours": 6},
    "military_factory": {"name": "Military Factory 🪖", "cost": 1_200_000, "time_hours": 8},
    "missile_launcher": {"name": "Missile Launcher 🚀", "cost": 2_500_000, "time_hours": 12},
    "warehouse": {"name": "Warehouse 📦", "cost": 3_000_000, "time_hours": 20}
}

CITY_STRUCTURES = {
    "facilities": {"name": "Facilities 🚏", "cost": 10_000_000, "time_hours": 24},
    "airport": {"name": "Airport 🛬", "cost": 30_000_000, "time_hours": 48},
    "shelter": {"name": "Shelter 🏬", "cost": 5_000_000, "time_hours": 20},
    "dock": {"name": "Dock ⚓", "cost": 20_000_000, "time_hours": 48}
}

# تعاریف معدن‌ها
MINES = {
    "Uranium": {"cost": 20_000_000, "time_hours": 5, "yield": 0.5},
    "Gold": {"cost": 10_000_000, "time_hours": 3, "yield": 1},
    "Iron": {"cost": 5_000_000, "time_hours": 1, "yield": 10},
    "Aluminum": {"cost": 5_000_000, "time_hours": 2, "yield": 10},
    "Copper": {"cost": 5_000_000, "time_hours": 1, "yield": 5},
    "Platinum": {"cost": 7_000_000, "time_hours": 2, "yield": 2}
}

# ==============================
# 🗃️ راه‌اندازی پایگاه داده
# ==============================
async def init_db():
    """ایجاد جداول مورد نیاز در SQLite"""
    async with aiosqlite.connect("game.db") as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                country TEXT,
                balance INTEGER,
                army_text TEXT,
                in_session_with TEXT,
                session_turn TEXT,
                is_admin BOOLEAN DEFAULT 0,
                state TEXT DEFAULT 'start',
                state_data TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS structures (
                user_id INTEGER,
                type TEXT,
                count INTEGER,
                PRIMARY KEY (user_id, type)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS resources (
                user_id INTEGER,
                resource_type TEXT,
                amount REAL,
                PRIMARY KEY (user_id, resource_type)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS mines (
                user_id INTEGER,
                resource_type TEXT,
                next_yield TEXT,
                PRIMARY KEY (user_id, resource_type)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS construction_queue (
                user_id INTEGER,
                structure_type TEXT,
                completion_time TEXT,
                PRIMARY KEY (user_id, structure_type)
            )
        """)
        await db.commit()

# ==============================
# 🧠 توابع کمکی
# ==============================
async def get_admin_user_id():
    """دریافت شناسه کاربر ادمین"""
    async with aiosqlite.connect("game.db") as db:
        async with db.execute("SELECT user_id FROM users WHERE is_admin = 1") as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None

async def get_country_by_user(user_id):
    """دریافت نام کشور کاربر"""
    async with aiosqlite.connect("game.db") as db:
        async with db.execute("SELECT country FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None

async def get_occupied_countries():
    """لیست کشورهای اشغال‌شده"""
    async with aiosqlite.connect("game.db") as db:
        async with db.execute("SELECT country FROM users WHERE country IS NOT NULL AND is_admin = 0") as cursor:
            return [row[0] for row in await cursor.fetchall()]

async def send_to_admin(context, message):
    """ارسال پیام به ادمین"""
    admin_id = await get_admin_user_id()
    if admin_id:
        try:
            await context.bot.send_message(chat_id=admin_id, text=message)
        except Exception as e:
            print(f"ارسال به ادمین شکست خورد: {e}")

# ==============================
# 🌐 مدیریت ورود
# ==============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور شروع"""
    await update.message.reply_text("رمز عبور را وارد کنید:")

async def handle_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت ورود با رمز"""
    user_id = update.effective_user.id
    password = update.message.text.strip()
    
    # چک کردن اینکه آیا کاربر قبلاً وارد شده
    async with aiosqlite.connect("game.db") as db:
        async with db.execute("SELECT country, is_admin FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row and (row[0] or row[1]):
                await show_main_menu(update, context)
                return

    # چک کردن رمز ادمین
    if password == ADMIN_PASSWORD:
        async with aiosqlite.connect("game.db") as db:
            async with db.execute("SELECT user_id FROM users WHERE is_admin = 1") as cursor:
                if await cursor.fetchone():
                    await update.message.reply_text("ادمین قبلاً وجود دارد!")
                    return
            await db.execute(
                "INSERT OR REPLACE INTO users (user_id, is_admin, state) VALUES (?, 1, 'admin_menu')",
                (user_id,)
            )
            await db.commit()
            await show_admin_menu(update, context)
            return

    # چک کردن رمز کشورها
    for country, pwd in COUNTRY_PASSWORDS.items():
        if password == pwd:
            async with aiosqlite.connect("game.db") as db:
                async with db.execute("SELECT user_id FROM users WHERE country = ?", (country,)) as cursor:
                    if await cursor.fetchone():
                        await update.message.reply_text(f"کشور {country} قبلاً اشغال شده است!")
                        return
                
                balance = INITIAL_BUDGETS[country]
                army_text = INITIAL_ARMY_TEXTS[country]
                
                await db.execute(
                    """INSERT OR REPLACE INTO users 
                    (user_id, country, balance, army_text, state) 
                    VALUES (?, ?, ?, ?, 'main_menu')""",
                    (user_id, country, balance, army_text)
                )
                
                # ایجاد سازه‌های اولیه
                for struct_type, count in INITIAL_STRUCTURES[country].items():
                    await db.execute(
                        "INSERT INTO structures (user_id, type, count) VALUES (?, ?, ?)",
                        (user_id, struct_type, count)
                    )
                
                # ایجاد منابع اولیه
                for resource in COUNTRY_RESOURCES[country]:
                    await db.execute(
                        "INSERT INTO resources (user_id, resource_type, amount) VALUES (?, ?, 0)",
                        (user_id, resource)
                    )
                
                await db.commit()
                await show_main_menu(update, context)
                return
    
    await update.message.reply_text("رمز نامعتبر است!")

# ==============================
# 🧭 منوی اصلی
# ==============================
async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش منوی اصلی کاربر"""
    keyboard = [
        [InlineKeyboardButton("Profile", callback_data="profile")],
        [InlineKeyboardButton("Non-City Structures", callback_data="non_city_structures")],
        [InlineKeyboardButton("City Structures", callback_data="city_structures")],
        [InlineKeyboardButton("Mines", callback_data="mines")],
        [InlineKeyboardButton("Diplomatic Session", callback_data="session")],
        [InlineKeyboardButton("Army", callback_data="army")],
        [InlineKeyboardButton("Research", callback_data="research")],
        [InlineKeyboardButton("Send Message to Country", callback_data="send_msg_country")],
        [InlineKeyboardButton("Attack", callback_data="attack")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.message.edit_text("Main Menu:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("Main Menu:", reply_markup=reply_markup)

async def show_admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش منوی ادمین"""
    keyboard = [
        [InlineKeyboardButton("Resources", callback_data="admin_resources")],
        [InlineKeyboardButton("Manage Structures", callback_data="admin_structures")],
        [InlineKeyboardButton("Message to Player", callback_data="admin_message")],
        [InlineKeyboardButton("Army", callback_data="admin_army")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.message.edit_text("Admin Panel:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("Admin Panel:", reply_markup=reply_markup)

# ==============================
# 🏗️ ساخت سازه
# ==============================
async def show_non_city_structures(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش سازه‌های غیرشهری"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    async with aiosqlite.connect("game.db") as db:
        counts = {}
        async with db.execute("SELECT type, count FROM structures WHERE user_id = ?", (user_id,)) as cursor:
            async for row in cursor:
                counts[row[0]] = row[1]
        
        text = "Non-City Structures:\n"
        for struct_id, struct_info in NON_CITY_STRUCTURES.items():
            count = counts.get(struct_id, 0)
            text += f"- {struct_info['name']}: {count}\n"
        
        keyboard = []
        for struct_id, struct_info in NON_CITY_STRUCTURES.items():
            keyboard.append([InlineKeyboardButton(
                struct_info['name'], 
                callback_data=f"build_non_city_{struct_id}"
            )])
        keyboard.append([InlineKeyboardButton("Back", callback_data="main_menu")])
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def build_non_city_structure(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ساخت سازه غیرشهری"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    struct_id = query.data.split("_")[-1]
    struct_info = NON_CITY_STRUCTURES[struct_id]
    
    async with aiosqlite.connect("game.db") as db:
        async with db.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,)) as cursor:
            balance = (await cursor.fetchone())[0]
        
        if balance < struct_info['cost']:
            await query.edit_message_text("موجودی کافی نیست!")
            return
        
        new_balance = balance - struct_info['cost']
        await db.execute("UPDATE users SET balance = ? WHERE user_id = ?", (new_balance, user_id))
        
        completion_time = datetime.utcnow() + timedelta(hours=struct_info['time_hours'])
        await db.execute(
            """INSERT OR REPLACE INTO construction_queue 
            (user_id, structure_type, completion_time) 
            VALUES (?, ?, ?)""",
            (user_id, struct_id, completion_time.isoformat())
        )
        await db.commit()
        
        completion_str = completion_time.strftime("%Y-%m-%d %H:%M UTC")
        await query.edit_message_text(
            f"ساخت آغاز شد!\n"
            f"{struct_info['name']} در {completion_str} آماده می‌شود\n"
            f"هزینه: ${struct_info['cost']:,}"
        )

# ==============================
# ⛏️ ساخت معدن
# ==============================
async def show_mines(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش منوی معدن"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    country = await get_country_by_user(user_id)
    available_resources = COUNTRY_RESOURCES[country]
    
    async with aiosqlite.connect("game.db") as db:
        current_mines = []
        async with db.execute("SELECT resource_type FROM mines WHERE user_id = ?", (user_id,)) as cursor:
            async for row in cursor:
                current_mines.append(row[0])
        
        text = "Your Mines:\n"
        if current_mines:
            for res in current_mines:
                text += f"- {res}\n"
        else:
            text += "None\n"
        
        keyboard = []
        for resource in available_resources:
            keyboard.append([InlineKeyboardButton(
                f"{resource} 🪨", 
                callback_data=f"build_mine_{resource}"
            )])
        keyboard.append([InlineKeyboardButton("Back", callback_data="main_menu")])
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def build_mine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ساخت معدن"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    resource = query.data.split("_")[-1]
    mine_info = MINES[resource]
    
    async with aiosqlite.connect("game.db") as db:
        async with db.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,)) as cursor:
            balance = (await cursor.fetchone())[0]
        
        if balance < mine_info['cost']:
            await query.edit_message_text("موجودی کافی نیست!")
            return
        
        new_balance = balance - mine_info['cost']
        await db.execute("UPDATE users SET balance = ? WHERE user_id = ?", (new_balance, user_id))
        
        next_yield = datetime.utcnow() + timedelta(hours=mine_info['time_hours'])
        await db.execute(
            """INSERT OR REPLACE INTO mines 
            (user_id, resource_type, next_yield) 
            VALUES (?, ?, ?)""",
            (user_id, resource, next_yield.isoformat())
        )
        
        await db.execute(
            "INSERT OR IGNORE INTO resources (user_id, resource_type, amount) VALUES (?, ?, 0)",
            (user_id, resource)
        )
        await db.commit()
        
        await query.edit_message_text(
            f"معدن ساخته شد!\n"
            f"اولین تولید در {mine_info['time_hours']} ساعت\n"
            f"هزینه: ${mine_info['cost']:,}"
        )

# ==============================
# 💬 جلسه دیپلماتیک
# ==============================
async def show_session_countries(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش کشورهای قابل جلسه"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    country = await get_country_by_user(user_id)
    occupied = await get_occupied_countries()
    targets = [c for c in occupied if c != country]
    
    if not targets:
        await query.edit_message_text("کشور دیگری وجود ندارد!")
        return
    
    keyboard = [[InlineKeyboardButton(c, callback_data=f"session_req_{c}")] for c in targets]
    keyboard.append([InlineKeyboardButton("Back", callback_data="main_menu")])
    await query.edit_message_text("کشور را انتخاب کنید:", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_session_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت درخواست جلسه"""
    query = update.callback_query
    await query.answer()
    
    requester_id = query.from_user.id
    target_country = query.data.split("_")[-1]
    
    async with aiosqlite.connect("game.db") as db:
        async with db.execute("SELECT user_id FROM users WHERE country = ?", (target_country,)) as cursor:
            row = await cursor.fetchone()
            if not row:
                await query.edit_message_text("کشور یافت نشد!")
                return
            target_id = row[0]
    
    context.bot_data[f"pending_session_{target_id}"] = requester_id
    requester_country = await get_country_by_user(requester_id)
    
    keyboard = [
        [InlineKeyboardButton("Accept", callback_data=f"session_accept_{requester_country}")],
        [InlineKeyboardButton("Reject", callback_data="session_reject")]
    ]
    await context.bot.send_message(
        chat_id=target_id,
        text=f"{requester_country} درخواست جلسه داده است!",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    await query.edit_message_text("درخواست ارسال شد!")

# ==============================
# 📨 ارسال پیام/حمله
# ==============================
async def show_message_countries(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش کشورهای قابل ارسال پیام"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    country = await get_country_by_user(user_id)
    occupied = await get_occupied_countries()
    targets = [c for c in occupied if c != country]
    
    if not targets:
        await query.edit_message_text("کشور دیگری وجود ندارد!")
        return
    
    keyboard = [[InlineKeyboardButton(c, callback_data=f"msg_country_{c}")] for c in targets]
    keyboard.append([InlineKeyboardButton("Back", callback_data="main_menu")])
    await query.edit_message_text("کشور را انتخاب کنید:", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_message_country_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """انتخاب کشور برای ارسال پیام"""
    query = update.callback_query
    await query.answer()
    
    target_country = query.data.split("_")[-1]
    context.user_data["msg_target"] = target_country
    context.user_data["msg_type"] = "message"
    
    await query.edit_message_text(f"پیام را برای {target_country} ارسال کنید:")

async def handle_attack_country_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """انتخاب کشور برای حمله"""
    query = update.callback_query
    await query.answer()
    
    target_country = query.data.split("_")[-1]
    context.user_data["msg_target"] = target_country
    context.user_data["msg_type"] = "attack"
    
    await query.edit_message_text(f"شرح حمله به {target_country} را ارسال کنید:")

async def handle_message_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت متن ارسالی"""
    user_id = update.effective_user.id
    text = update.message.text
    msg_type = context.user_data.get("msg_type")
    target_country = context.user_data.get("msg_target")
    
    if not msg_type or not target_country:
        await update.message.reply_text("وضعیت نامعتبر!")
        return
    
    sender_country = await get_country_by_user(user_id)
    
    async with aiosqlite.connect("game.db") as db:
        async with db.execute("SELECT user_id FROM users WHERE country = ?", (target_country,)) as cursor:
            row = await cursor.fetchone()
            if not row:
                await update.message.reply_text("کشور یافت نشد!")
                return
            target_id = row[0]
    
    if msg_type == "attack":
        await context.bot.send_message(
            chat_id=target_id,
            text=f"⚠️ حمله از {sender_country}:\n{text}"
        )
        await send_to_admin(context, f"⚠️ حمله: {sender_country} → {target_country}\n{text}")
    else:
        await context.bot.send_message(
            chat_id=target_id,
            text=f"📨 پیام از {sender_country}:\n{text}"
        )
        await send_to_admin(context, f"📨 پیام: {sender_country} → {target_country}\n{text}")
    
    await update.message.reply_text("پیام ارسال شد!")
    await show_main_menu(update, context)

# ==============================
# 📖 پروفایل/ارتش/تحقیق
# ==============================
async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش پروفایل"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    country = await get_country_by_user(user_id)
    
    async with aiosqlite.connect("game.db") as db:
        async with db.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,)) as cursor:
            balance = (await cursor.fetchone())[0]
        
        structures = {}
        async with db.execute("SELECT type, count FROM structures WHERE user_id = ?", (user_id,)) as cursor:
            async for row in cursor:
                structures[row[0]] = row[1]
        
        resources = {}
        async with db.execute("SELECT resource_type, amount FROM resources WHERE user_id = ?", (user_id,)) as cursor:
            async for row in cursor:
                resources[row[0]] = row[1]
    
    text = f"Profile: {country}\n"
    text += f"Balance: ${balance:,}\n\n"
    
    text += "Structures:\n"
    for struct_id, count in structures.items():
        struct_name = NON_CITY_STRUCTURES.get(struct_id, CITY_STRUCTURES.get(struct_id))
        if struct_name:
            text += f"- {struct_name['name']}: {count}\n"
    
    text += "\nResources:\n"
    for res, amount in resources.items():
        text += f"- {res}: {amount:.2f}\n"
    
    keyboard = [[InlineKeyboardButton("Back", callback_data="main_menu")]]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def show_army(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش ارتش"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    country = await get_country_by_user(user_id)
    
    async with aiosqlite.connect("game.db") as db:
        async with db.execute("SELECT army_text FROM users WHERE user_id = ?", (user_id,)) as cursor:
            army_text = (await cursor.fetchone())[0]
    
    text = f"Army Profile: {country}\n\n{army_text}\n\n"
    text += "اگر درخواستی دارید، ارسال کنید:"
    
    context.user_data["awaiting_army_request"] = True
    await query.edit_message_text(text)

async def start_research(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شروع تحقیق"""
    query = update.callback_query
    await query.answer()
    
    context.user_data["awaiting_research"] = True
    await query.edit_message_text("گزارش تحقیقاتی را ارسال کنید:")

# ==============================
# 🔧 مدیریت ادمین
# ==============================
async def show_admin_countries(update: Update, context: ContextTypes.DEFAULT_TYPE, action):
    """نمایش کشورهای ادمین"""
    query = update.callback_query
    await query.answer()
    
    occupied = await get_occupied_countries()
    if not occupied:
        await query.edit_message_text("کشوری وجود ندارد!")
        return
    
    keyboard = [[InlineKeyboardButton(c, callback_data=f"admin_{action}_{c}")] for c in occupied]
    keyboard.append([InlineKeyboardButton("Back", callback_data="admin_menu")])
    await query.edit_message_text("کشور را انتخاب کنید:", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_admin_resources(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت منابع توسط ادمین"""
    query = update.callback_query
    await query.answer()
    
    country = query.data.split("_")[-1]
    context.user_data["admin_country"] = country
    context.user_data["admin_action"] = "resources"
    
    async with aiosqlite.connect("game.db") as db:
        async with db.execute("SELECT user_id FROM users WHERE country = ?", (country,)) as cursor:
            user_id = (await cursor.fetchone())[0]
        
        resources = {}
        async with db.execute("SELECT resource_type, amount FROM resources WHERE user_id = ?", (user_id,)) as cursor:
            async for row in cursor:
                resources[row[0]] = row[1]
    
    text = f"Resources for {country}:\n"
    for res, amount in resources.items():
        text += f"- {res}: {amount:.2f}\n"
    
    keyboard = [[InlineKeyboardButton(res, callback_data=f"admin_edit_res_{res}")] for res in resources.keys()]
    keyboard.append([InlineKeyboardButton("Back", callback_data="admin_resources_countries")])
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_admin_structures(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت سازه‌ها توسط ادمین"""
    query = update.callback_query
    await query.answer()
    
    country = query.data.split("_")[-1]
    context.user_data["admin_country"] = country
    context.user_data["admin_action"] = "structures"
    
    async with aiosqlite.connect("game.db") as db:
        async with db.execute("SELECT user_id FROM users WHERE country = ?", (country,)) as cursor:
            user_id = (await cursor.fetchone())[0]
        
        structures = {}
        async with db.execute("SELECT type, count FROM structures WHERE user_id = ?", (user_id,)) as cursor:
            async for row in cursor:
                structures[row[0]] = row[1]
    
    text = f"Structures for {country}:\n"
    for struct_id, count in structures.items():
        struct_info = NON_CITY_STRUCTURES.get(struct_id) or CITY_STRUCTURES.get(struct_id)
        if struct_info:
            text += f"- {struct_info['name']}: {count}\n"
    
    keyboard = []
    for struct_id in structures.keys():
        struct_info = NON_CITY_STRUCTURES.get(struct_id) or CITY_STRUCTURES.get(struct_id)
        if struct_info:
            keyboard.append([InlineKeyboardButton(
                struct_info['name'],
                callback_data=f"admin_edit_struct_{struct_id}"
            )])
    keyboard.append([InlineKeyboardButton("Back", callback_data="admin_structures_countries")])
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

# ==============================
# 🔄 مدیریت دکمه‌ها
# ==============================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت تمام دکمه‌ها"""
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "main_menu":
        await show_main_menu(update, context)
        return
    elif data == "admin_menu":
        await show_admin_menu(update, context)
        return
    elif data == "profile":
        await show_profile(update, context)
        return
    elif data == "army":
        await show_army(update, context)
        return
    elif data == "research":
        await start_research(update, context)
        return
    
    if data == "admin_resources":
        await show_admin_countries(update, context, "resources")
        return
    elif data == "admin_structures":
        await show_admin_countries(update, context, "structures")
        return
    elif data == "admin_message":
        await show_admin_countries(update, context, "message")
        return
    elif data == "admin_army":
        await show_admin_countries(update, context, "army")
        return
    
    if data.startswith("non_city_structures"):
        await show_non_city_structures(update, context)
        return
    elif data.startswith("build_non_city_"):
        await build_non_city_structure(update, context)
        return
    elif data.startswith("mines"):
        await show_mines(update, context)
        return
    elif data.startswith("build_mine_"):
        await build_mine(update, context)
        return
    elif data == "session":
        await show_session_countries(update, context)
        return
    elif data.startswith("session_req_"):
        await handle_session_request(update, context)
        return
    elif data == "send_msg_country":
        await show_message_countries(update, context)
        return
    elif data.startswith("msg_country_"):
        await handle_message_country_selection(update, context)
        return
    elif data == "attack":
        await show_message_countries(update, context)
        context.user_data["attack_mode"] = True
        return
    
    if data.startswith("admin_resources_") and not data.startswith("admin_edit_res_"):
        await handle_admin_resources(update, context)
        return
    elif data.startswith("admin_structures_") and not data.startswith("admin_edit_struct_"):
        await handle_admin_structures(update, context)
        return

# ==============================
# 🚀 اجرای اصلی
# ==============================
async def main():
    """تابع اصلی راه‌اندازی ربات"""
    await init_db()
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_password))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, handle_message_text))
    
    print("ربات شروع شد...")
    await application.run_polling()

# ==============================
# 🧠 اجرای برنامه
# ==============================
if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    asyncio.run(main())

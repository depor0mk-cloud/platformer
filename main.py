import asyncio
import json
import random
from datetime import datetime, timedelta
from typing import Dict, Optional
import pytz

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters
)

import firebase_admin
from firebase_admin import credentials, db

# Инициализация Firebase
cred_dict = {
    "type": "service_account",
    "project_id": "boevik-1e8c3",
    "private_key_id": "24e8099d413eb699471adb8c4a656f6d7faf8f39",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQDOhqXZpqS6nb1T\nOeFEqo44AivSsmRChCrh11MZ9ofyaKqPJvHNeZRSiiFdjO8FvdqOxJnUz+dB0HSy\n6rUrx6+JuyInU3dh+fJPMulf8D83odnDV8oA8dvHLck6VMieKz45Wap4ypeqc6B+\nlnu3F9dAPl3Pmjzzb+nVS+c4vggSio6fd9DVua/fMiOVtC5cXUhjwst4pz1sieDf\n4eTRyjIlJg3b7JlbmRT44ssQYJltz4dVG2KtjKM5NtyU/R5OHjA8FefxTpr1zt0c\nDsZVITkd0KlZ9dDgN1t9D2Sk4WD1AnBSVWeoOdVEJD1gt4RALozRB6LFV1NNW50r\nnCNNcE2HAgMBAAECggeAKbZHRATky241gVw0084QyF4j5Lu0BT01fgSj26APyBV8\nsUn/12zBWMReRctDsWitfl1V5oYRIplMIKDH864ylYJOvRueBpNZbcaOHRrkYcOW\nPF58RaGTrpBgTqA2HsAEIsgp5pigdkRBO6AAH7Q4fNi70MTJn69QToy0iCDVd4zY\nQLmdk36/0EEA3gcg7uLQgQASAtzCqxGPDxNRgTfltQsi6mowNISMLwj6AwPrH4AS\nJNAlNXPIxII7mp2MeOb0mn9gXSrgzD8bSfOoycQBU04tYUZYm98STU5aH7wxatl0\nPpwkhy1BhEXKY3YLXm0vPBWxKHLHc1WLCW8sBLEn8QKBgQD87GKPr6v0xxEJRjHQ\nnZ1W09oQW3Q+Qf7wKaEhr/ysDoMPACum5wZWN7mExJ1Pgm+yN1H02lMEATJHYj2F\nbhoxAbO/YIyhaixIOnciPjlrHoF3Q1Ecp6qpN4qYSlO0+/QY2HSANF4gJq0rPWZk\nibF0S+aTABUnW8tllem7c1PpVwKBgQDRCcd4k4Yl80Kgit19UXE/2KMxK2ZHAncE\nY2QiZwYz0y4hsIkR93bt/fRx+f4jm4h+NlV+AGKcG+gSojvKTPFGeq5hw5blA10y\nbW8+aJCduihRV/Ok8oicuA9Eg6pDgSrAQu85GhCNMiJWUWCjYh1n3mV+PZOiuInC\niWbpPgevUQKBgFHHBJ88x7afXszG23h+Xc8jNJCxYUZ4BDwW2biQtHvVPV7uSS7v\n58acwelBwTNiE0dmR6OJq+nRkTYvd4Da9rD9weaRCydtst+vt7FkuR//fxDWvTUs\nqSuJf9B5x9Lu3B/kbNa/F+gBWWBvu9mqA6x8lhLVpgFR1tQDws0PHwSFaoGAX1Z4\ndVPDQRe7cYEkF33HivkBJPHISeaj5Yp3JwGZ4JUWWyMqwNj+kvjaPglokVDkZbve\nLgN69fv8UlNPtap1+FEHq2sLLRPls5QZwnrqSiWXMdJNOxOqnt+LhxIN24/TsbBV\nbtOmbN9KrdebnaioBLF31KW86eAEZIdKOmKiGqECgYBPTUUqwSt/XjhTAluZ0NGv\nE/RqthzazKCv7lbq93uNak3vUxzFSFRq+FDe2mAI4Rcm3zHY81XSEC8MPZ8vgP4\nNSQEaf3jH8fai+20nj6Kzkg6dGARHtUoThPTOmde9cvONge2+qQBm2HUrpCwAxwH\nBn+wtsxmTo0MWADhgTwyaw==\n-----END PRIVATE KEY-----\n",
    "client_email": "firebase-adminsdk-fbsvc@boevik-1e8c3.iam.gserviceaccount.com",
    "client_id": "116136449002776595932",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40boevik-1e8c3.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}

cred = credentials.Certificate(cred_dict)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://boevik-1e8c3-default-rtdb.europe-west1.firebasedatabase.app/'
})

ADMIN_USERNAME = "Trim_peek"
BOT_TOKEN = "8555470613:AAHiu1CzPOHZPOXP8uLtKWodBjYzXQJWVwE"

# Хранилище для временных данных пользователей
user_states = {}

class ClanBot:
    def __init__(self):
        self.ref = db.reference('/')
        self.init_settings()
    
    def init_settings(self):
        settings = self.ref.child('settings').get()
        if not settings:
            self.ref.child('settings').set({
                'bot_enabled': True,
                'test_mode': False,
                'peace_time_start': None,
                'peace_time_end': None,
                'max_clan_members': 15,
                'factory_prices': {
                    'financial': 1000,
                    'weapon': 1250
                },
                'production_price': 1000
            })
    
    def check_bot_status(self, user_id: int) -> Optional[str]:
        settings = self.ref.child('settings').get()
        if not settings.get('bot_enabled'):
            return "🛠 Бот на тех.перерыве"
        if settings.get('test_mode') and user_id != self.get_admin_id():
            return "🔧 Бот на тестовом осмотре"
        return None
    
    def is_peace_time(self) -> bool:
        settings = self.ref.child('settings').get()
        start = settings.get('peace_time_start')
        end = settings.get('peace_time_end')
        if not start or not end:
            return False
        
        now = datetime.now(pytz.UTC).time()
        start_time = datetime.strptime(start, "%H:%M").time()
        end_time = datetime.strptime(end, "%H:%M").time()
        
        if start_time < end_time:
            return start_time <= now <= end_time
        else:
            return now >= start_time or now <= end_time
    
    def get_admin_id(self) -> int:
        users = self.ref.child('users').get()
        if users:
            for uid, data in users.items():
                if data.get('username') == ADMIN_USERNAME:
                    return int(uid)
        return 0
    
    def get_user_clan(self, user_id: int) -> Optional[str]:
        user_data = self.ref.child(f'users/{user_id}').get()
        return user_data.get('clan') if user_data else None
    
    def create_user(self, user_id: int, username: str):
        self.ref.child(f'users/{user_id}').set({
            'username': username,
            'clan': None,
            'level': 1,
            'exp': 0,
            'contribution': 0,
            'personal_balance': 0,
            'cooldowns': {},
            'achievements': [],
            'factories_built': 0
        })
    
    def log_action(self, action: str, user_id: int, details: str):
        timestamp = datetime.now(pytz.UTC).isoformat()
        self.ref.child('logs').push({
            'timestamp': timestamp,
            'action': action,
            'user_id': user_id,
            'details': details
        })

bot_instance = ClanBot()

async def check_access(update: Update, context: ContextTypes.DEFAULT_TYPE, require_clan=False) -> bool:
    user_id = update.effective_user.id
    
    status_msg = bot_instance.check_bot_status(user_id)
    if status_msg:
        await update.message.reply_text(status_msg)
        return False
    
    user_data = bot_instance.ref.child(f'users/{user_id}').get()
    if not user_data:
        bot_instance.create_user(user_id, update.effective_user.username or str(user_id))
    
    if require_clan:
        clan_id = bot_instance.get_user_clan(user_id)
        if not clan_id:
            await update.message.reply_text("Вы не состоите в клане.")
            return False
    
    return True

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_access(update, context):
        return
    
    keyboard = [
        [InlineKeyboardButton("👁️ Мой клан", callback_data="my_clan"),
         InlineKeyboardButton("📋 Список кланов", callback_data="clan_list")],
        [InlineKeyboardButton("⚔️ Создать клан", callback_data="create_clan"),
         InlineKeyboardButton("📜 Правила", callback_data="rules")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🎮 Добро пожаловать в клан-бот!\n\n"
        "Выберите действие:",
        reply_markup=reply_markup
    )

async def create_clan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_access(update, context):
        return
    
    user_id = update.effective_user.id
    clan_id = bot_instance.get_user_clan(user_id)
    
    if clan_id:
        await update.message.reply_text("Вы уже в клане. Покиньте его, чтобы создать новый.")
        return
    
    if len(context.args) < 2:
        await update.message.reply_text("Использование: /создать_клан [название] [тег]")
        return
    
    clan_name = " ".join(context.args[:-1])
    clan_tag = context.args[-1]
    
    clans = bot_instance.ref.child('clans').get()
    if clans:
        for cid, data in clans.items():
            if data.get('name') == clan_name or data.get('tag') == clan_tag:
                await update.message.reply_text("Клан с таким названием или тегом уже существует.")
                return
    
    user_states[user_id] = {
        'action': 'create_clan',
        'name': clan_name,
        'tag': clan_tag
    }
    
    keyboard = [
        [InlineKeyboardButton("✅ Да, создать", callback_data="confirm_create_clan"),
         InlineKeyboardButton("❌ Отмена", callback_data="cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"Будет создан клан {clan_name} [{clan_tag}]. Вы уверены?",
        reply_markup=reply_markup
    )

async def my_clan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_access(update, context, require_clan=True):
        return
    
    user_id = update.effective_user.id
    clan_id = bot_instance.get_user_clan(user_id)
    clan_data = bot_instance.ref.child(f'clans/{clan_id}').get()
    
    if not clan_data:
        await update.message.reply_text("Клан не найден.")
        return
    
    members = clan_data.get('members', {})
    treasury = clan_data.get('treasury', 0)
    army = clan_data.get('army', 0)
    weapons = clan_data.get('weapons', 0)
    capital_hp = clan_data.get('capital_hp', 10000)
    level = clan_data.get('level', 1)
    exp = clan_data.get('exp', 0)
    
    factories = clan_data.get('factories', {})
    financial_factories = sum(1 for f in factories.values() if f.get('type') == 'financial')
    weapon_factories = sum(1 for f in factories.values() if f.get('type') == 'weapon')
    
    financial_production = sum(f.get('production', 10) for f in factories.values() if f.get('type') == 'financial')
    weapon_production = sum(f.get('production', 10) for f in factories.values() if f.get('type') == 'weapon')
    
    productions = clan_data.get('productions', {})
    
    text = f"""🏰 Клан {clan_data['name']} [{clan_data['tag']}]

👑 Лидер: @{clan_data['leader_username']}
👥 Участники: {len(members)}/{bot_instance.ref.child('settings/max_clan_members').get()}
📊 Уровень: {level} | Опыт: {exp}
❤️ Здоровье столицы: {capital_hp}

💰 Казна: {treasury} монет
🔫 Склад оружия: {weapons} автоматов

🏭 Заводы:
   🏦 Финансовых: {financial_factories} (производят {financial_production} монет/час)
   🔫 Оружейных: {weapon_factories} (производят {weapon_production} автоматов/час)

⚔️ Армия: {army} солдат
"""
    
    if productions:
        text += "\n📦 Производства:\n"
        for prod_id, prod_data in list(productions.items())[:5]:
            text += f"   {prod_data['name']}: {prod_data.get('stock', 0)} шт. (ур.{prod_data.get('level', 1)})\n"
    
    keyboard = [
        [InlineKeyboardButton("👥 Участники", callback_data=f"members_{clan_id}"),
         InlineKeyboardButton("🏭 Заводы", callback_data=f"factories_{clan_id}")],
        [InlineKeyboardButton("⚔️ Война", callback_data=f"war_{clan_id}"),
         InlineKeyboardButton("🚀 Ракеты", callback_data=f"missiles_{clan_id}")],
        [InlineKeyboardButton("📦 Производство", callback_data=f"production_{clan_id}")]
    ]
    
    if clan_data['leader'] == user_id:
        keyboard.append([InlineKeyboardButton("📋 Заявки", callback_data=f"applications_{clan_id}"),
                        InlineKeyboardButton("✏️ Описание", callback_data=f"edit_desc_{clan_id}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, reply_markup=reply_markup)

async def work_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_access(update, context, require_clan=True):
        return
    
    user_id = update.effective_user.id
    user_data = bot_instance.ref.child(f'users/{user_id}').get()
    
    cooldown = user_data.get('cooldowns', {}).get('work')
    if cooldown:
        cooldown_time = datetime.fromisoformat(cooldown)
        if datetime.now(pytz.UTC) < cooldown_time:
            remaining = (cooldown_time - datetime.now(pytz.UTC)).seconds // 60
            await update.message.reply_text(f"⏰ Вы сможете работать через {remaining} минут.")
            return
    
    clan_id = bot_instance.get_user_clan(user_id)
    earnings = random.randint(100, 500)
    
    bot_instance.ref.child(f'clans/{clan_id}/treasury').set(
        bot_instance.ref.child(f'clans/{clan_id}/treasury').get() + earnings
    )
    bot_instance.ref.child(f'users/{user_id}/contribution').set(
        user_data.get('contribution', 0) + earnings
    )
    bot_instance.ref.child(f'users/{user_id}/cooldowns/work').set(
        (datetime.now(pytz.UTC) + timedelta(hours=6)).isoformat()
    )
    
    new_treasury = bot_instance.ref.child(f'clans/{clan_id}/treasury').get()
    new_contribution = bot_instance.ref.child(f'users/{user_id}/contribution').get()
    
    await update.message.reply_text(
        f"✅ Вы поработали и заработали {earnings} монет для клана!\n"
        f"💰 Казна клана: {new_treasury} монет\n"
        f"📊 Ваш вклад: {new_contribution} монет"
    )
    
    bot_instance.log_action('work', user_id, f'Earned {earnings} coins')

async def work2_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_access(update, context, require_clan=True):
        return
    
    user_id = update.effective_user.id
    user_data = bot_instance.ref.child(f'users/{user_id}').get()
    
    cooldown = user_data.get('cooldowns', {}).get('work2')
    if cooldown:
        cooldown_time = datetime.fromisoformat(cooldown)
        if datetime.now(pytz.UTC) < cooldown_time:
            remaining = (cooldown_time - datetime.now(pytz.UTC)).seconds // 3600
            await update.message.reply_text(f"⏰ Вы сможете работать через {remaining} часов.")
            return
    
    clan_id = bot_instance.get_user_clan(user_id)
    earnings = random.randint(200, 800)
    
    bot_instance.ref.child(f'clans/{clan_id}/treasury').set(
        bot_instance.ref.child(f'clans/{clan_id}/treasury').get() + earnings
    )
    bot_instance.ref.child(f'users/{user_id}/contribution').set(
        user_data.get('contribution', 0) + earnings
    )
    bot_instance.ref.child(f'users/{user_id}/cooldowns/work2').set(
        (datetime.now(pytz.UTC) + timedelta(hours=12)).isoformat()
    )
    
    new_treasury = bot_instance.ref.child(f'clans/{clan_id}/treasury').get()
    new_contribution = bot_instance.ref.child(f'users/{user_id}/contribution').get()
    
    await update.message.reply_text(
        f"✅ Вы отработали смену и заработали {earnings} монет для клана!\n"
        f"💰 Казна клана: {new_treasury} монет\n"
        f"📊 Ваш вклад: {new_contribution} монет"
    )
    
    bot_instance.log_action('work2', user_id, f'Earned {earnings} coins')

async def factory_work_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_access(update, context, require_clan=True):
        return
    
    user_id = update.effective_user.id
    user_data = bot_instance.ref.child(f'users/{user_id}').get()
    
    cooldown = user_data.get('cooldowns', {}).get('factory_work')
    if cooldown:
        cooldown_time = datetime.fromisoformat(cooldown)
        if datetime.now(pytz.UTC) < cooldown_time:
            remaining = (cooldown_time - datetime.now(pytz.UTC)).seconds // 3600
            await update.message.reply_text(f"⏰ Вы сможете работать на заводе через {remaining} часов.")
            return
    
    clan_id = bot_instance.get_user_clan(user_id)
    earnings = random.randint(1000, 2000)
    
    bot_instance.ref.child(f'clans/{clan_id}/treasury').set(
        bot_instance.ref.child(f'clans/{clan_id}/treasury').get() + earnings
    )
    bot_instance.ref.child(f'users/{user_id}/contribution').set(
        user_data.get('contribution', 0) + earnings
    )
    bot_instance.ref.child(f'users/{user_id}/cooldowns/factory_work').set(
        (datetime.now(pytz.UTC) + timedelta(hours=48)).isoformat()
    )
    
    new_treasury = bot_instance.ref.child(f'clans/{clan_id}/treasury').get()
    new_contribution = bot_instance.ref.child(f'users/{user_id}/contribution').get()
    
    await update.message.reply_text(
        f"✅ Вы отработали смену на заводе и произвели продукции на {earnings} монет!\n"
        f"💰 Казна клана: {new_treasury} монет\n"
        f"📊 Ваш вклад: {new_contribution} монет"
    )
    
    bot_instance.log_action('factory_work', user_id, f'Earned {earnings} coins')

async def build_factory_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_access(update, context, require_clan=True):
        return
    
    if len(context.args) < 1:
        await update.message.reply_text("Использование: /строй_завод [финансовый/оружейный]")
        return
    
    factory_type = context.args[0].lower()
    if factory_type not in ['финансовый', 'оружейный']:
        await update.message.reply_text("Тип завода должен быть 'финансовый' или 'оружейный'")
        return
    
    user_id = update.effective_user.id
    clan_id = bot_instance.get_user_clan(user_id)
    clan_data = bot_instance.ref.child(f'clans/{clan_id}').get()
    
    settings = bot_instance.ref.child('settings').get()
    factory_type_en = 'financial' if factory_type == 'финансовый' else 'weapon'
    cost = settings['factory_prices'][factory_type_en]
    
    if clan_data.get('treasury', 0) < cost:
        await update.message.reply_text(
            f"В казне недостаточно средств. Нужно {cost} монет, а у вас {clan_data.get('treasury', 0)}"
        )
        return
    
    factories = clan_data.get('factories', {})
    if len(factories) >= 20:
        await update.message.reply_text("Вы достигли лимита заводов. Уничтожьте один, чтобы построить новый.")
        return
    
    user_states[user_id] = {
        'action': 'build_factory',
        'type': factory_type_en,
        'cost': cost
    }
    
    keyboard = [
        [InlineKeyboardButton("✅ Построить", callback_data="confirm_build_factory"),
         InlineKeyboardButton("❌ Отмена", callback_data="cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    emoji = "🏦" if factory_type == "финансовый" else "🔫"
    await update.message.reply_text(
        f"Построить {emoji} {factory_type} завод за {cost} монет?",
        reply_markup=reply_markup
    )

async def declare_war_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_access(update, context, require_clan=True):
        return
    
    if bot_instance.is_peace_time():
        settings = bot_instance.ref.child('settings').get()
        await update.message.reply_text(
            f"🌙 Мирное время! Боевые действия разрешены от {settings['peace_time_end']} до {settings['peace_time_start']}"
        )
        return
    
    user_id = update.effective_user.id
    clan_id = bot_instance.get_user_clan(user_id)
    clan_data = bot_instance.ref.child(f'clans/{clan_id}').get()
    
    if clan_data['leader'] != user_id:
        await update.message.reply_text("Только лидер может объявлять войну.")
        return
    
    if len(context.args) < 1:
        await update.message.reply_text("Использование: /объявить_войну [название/тег клана]")
        return
    
    target_identifier = " ".join(context.args)
    clans = bot_instance.ref.child('clans').get()
    
    target_clan_id = None
    for cid, data in clans.items():
        if data.get('name') == target_identifier or data.get('tag') == target_identifier:
            target_clan_id = cid
            break
    
    if not target_clan_id:
        await update.message.reply_text("Клан не найден.")
        return
    
    if target_clan_id == clan_id:
        await update.message.reply_text("Вы не можете объявить войну своему клану.")
        return
    
    user_states[user_id] = {
        'action': 'declare_war',
        'target': target_clan_id
    }
    
    target_data = bot_instance.ref.child(f'clans/{target_clan_id}').get()
    keyboard = [
        [InlineKeyboardButton("⚔️ Объявить войну", callback_data="confirm_declare_war"),
         InlineKeyboardButton("❌ Отмена", callback_data="cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"Вы хотите объявить войну клану {target_data['name']} [{target_data['tag']}]?",
        reply_markup=reply_markup
    )

async def mobilization_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_access(update, context, require_clan=True):
        return
    
    user_id = update.effective_user.id
    clan_id = bot_instance.get_user_clan(user_id)
    clan_data = bot_instance.ref.child(f'clans/{clan_id}').get()
    user_data = bot_instance.ref.child(f'users/{user_id}').get()
    
    if clan_data['leader'] != user_id and user_id not in clan_data.get('officers', []):
        await update.message.reply_text("Только лидер и офицеры могут проводить мобилизацию.")
        return
    
    cooldown = user_data.get('cooldowns', {}).get('mobilization')
    if cooldown:
        cooldown_time = datetime.fromisoformat(cooldown)
        if datetime.now(pytz.UTC) < cooldown_time:
            remaining = (cooldown_time - datetime.now(pytz.UTC)).seconds // 3600
            await update.message.reply_text(f"⏰ Вы сможете провести мобилизацию через {remaining} часов.")
            return
    
    cost = 500
    if clan_data.get('treasury', 0) < cost:
        await update.message.reply_text(f"В казне недостаточно средств. Нужно {cost} монет.")
        return
    
    troops = random.randint(1000, 2500)
    
    bot_instance.ref.child(f'clans/{clan_id}/treasury').set(
        clan_data.get('treasury', 0) - cost
    )
    bot_instance.ref.child(f'clans/{clan_id}/army').set(
        clan_data.get('army', 0) + troops
    )
    bot_instance.ref.child(f'users/{user_id}/cooldowns/mobilization').set(
        (datetime.now(pytz.UTC) + timedelta(hours=5)).isoformat()
    )
    
    new_army = bot_instance.ref.child(f'clans/{clan_id}/army').get()
    
    await update.message.reply_text(
        f"✅ Вы провели мобилизацию за {cost} монет и набрали {troops} солдат.\n"
        f"⚔️ Теперь в армии клана {new_army} бойцов."
    )
    
    bot_instance.log_action('mobilization', user_id, f'Mobilized {troops} troops')

async def attack_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_access(update, context, require_clan=True):
        return
    
    if bot_instance.is_peace_time():
        settings = bot_instance.ref.child('settings').get()
        await update.message.reply_text(
            f"🌙 Мирное время! Боевые действия разрешены от {settings['peace_time_end']} до {settings['peace_time_start']}"
        )
        return
    
    user_id = update.effective_user.id
    clan_id = bot_instance.get_user_clan(user_id)
    clan_data = bot_instance.ref.child(f'clans/{clan_id}').get()
    
    if clan_data['leader'] != user_id and user_id not in clan_data.get('officers', []):
        await update.message.reply_text("Только лидер и офицеры могут атаковать.")
        return
    
    war = clan_data.get('war')
    if not war or not war.get('active'):
        await update.message.reply_text("Вы не находитесь в состоянии войны.")
        return
    
    if len(context.args) < 1:
        keyboard = [
            [InlineKeyboardButton("100", callback_data="attack_100"),
             InlineKeyboardButton("500", callback_data="attack_500")],
            [InlineKeyboardButton("1000", callback_data="attack_1000"),
             InlineKeyboardButton("Макс", callback_data="attack_max")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Выберите количество бойцов:", reply_markup=reply_markup)
        return
    
    try:
        troops = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Количество должно быть числом.")
        return
    
    if troops > clan_data.get('army', 0):
        await update.message.reply_text("У вас недостаточно бойцов.")
        return
    
    user_states[user_id] = {
        'action': 'attack',
        'troops': troops,
        'target': war['enemy']
    }
    
    keyboard = [
        [InlineKeyboardButton("✅ Атаковать", callback_data="confirm_attack"),
         InlineKeyboardButton("❌ Отмена", callback_data="cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    target_data = bot_instance.ref.child(f'clans/{war["enemy"]}').get()
    await update.message.reply_text(
        f"Отправить {troops} бойцов в атаку на клан {target_data['name']}?",
        reply_markup=reply_markup
    )

async def admin_panel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if update.effective_user.username != ADMIN_USERNAME:
        await update.message.reply_text("У вас нет доступа к этой команде.")
        return
    
    keyboard = [
        [InlineKeyboardButton("ВКЛ/ОТКЛ БОТА", callback_data="admin_toggle_bot"),
         InlineKeyboardButton("РЕЖИМ СНА", callback_data="admin_peace_mode"),
         InlineKeyboardButton("РАССЫЛКА", callback_data="admin_broadcast")],
        [InlineKeyboardButton("БЭКАП", callback_data="admin_backup"),
         InlineKeyboardButton("ОЧИСТКА БД", callback_data="admin_clear_db"),
         InlineKeyboardButton("ЗАМОРОЗИТЬ КЛАН", callback_data="admin_freeze_clan")],
        [InlineKeyboardButton("РАЗМОРОЗИТЬ КЛАН", callback_data="admin_unfreeze_clan"),
         InlineKeyboardButton("ВЫДАТЬ РЕСУРСЫ", callback_data="admin_give_resources"),
         InlineKeyboardButton("СНЯТЬ РЕСУРСЫ", callback_data="admin_take_resources")],
        [InlineKeyboardButton("Далее ➡️", callback_data="admin_page_2")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    settings = bot_instance.ref.child('settings').get()
    status = "✅ Включен" if settings.get('bot_enabled') else "🔴 Выключен"
    test = "✅ Включен" if settings.get('test_mode') else "🔴 Выключен"
    
    await update.message.reply_text(
        f"🔐 АДМИН-ПАНЕЛЬ\n\n"
        f"Статус бота: {status}\n"
        f"Тестовый режим: {test}",
        reply_markup=reply_markup
    )

async def test_mode_on_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.username != ADMIN_USERNAME:
        await update.message.reply_text("У вас нет доступа к этой команде.")
        return
    
    bot_instance.ref.child('settings/test_mode').set(True)
    
    wars = bot_instance.ref.child('clans').get()
    if wars:
        for clan_id, clan_data in wars.items():
            if clan_data.get('war', {}).get('active'):
                bot_instance.ref.child(f'clans/{clan_id}/war/active').set(False)
    
    await update.message.reply_text("🔧 Тестовый режим активирован. Все войны приостановлены.")
    bot_instance.log_action('test_mode_on', update.effective_user.id, 'Activated test mode')

async def test_mode_off_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.username != ADMIN_USERNAME:
        await update.message.reply_text("У вас нет доступа к этой команде.")
        return
    
    bot_instance.ref.child('settings/test_mode').set(False)
    await update.message.reply_text("✅ Тестовый режим деактивирован. Бот вернулся в нормальный режим.")
    bot_instance.log_action('test_mode_off', update.effective_user.id, 'Deactivated test mode')

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    if data == "cancel":
        if user_id in user_states:
            del user_states[user_id]
        await query.edit_message_text("❌ Действие отменено.")
        return
    
    if data == "confirm_create_clan":
        if user_id not in user_states or user_states[user_id].get('action') != 'create_clan':
            await query.edit_message_text("Ошибка: данные не найдены.")
            return
        
        state = user_states[user_id]
        clan_id = bot_instance.ref.child('clans').push({
            'name': state['name'],
            'tag': state['tag'],
            'leader': user_id,
            'leader_username': query.from_user.username or str(user_id),
            'members': {user_id: 'leader'},
            'treasury': 0,
            'army': 0,
            'weapons': 0,
            'capital_hp': 10000,
            'level': 1,
            'exp': 0,
            'factories': {},
            'productions': {},
            'officers': [],
            'frozen': False
        }).key
        
        bot_instance.ref.child(f'users/{user_id}/clan').set(clan_id)
        del user_states[user_id]
        
        keyboard = [[InlineKeyboardButton("👁️ Мой клан", callback_data="my_clan")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"✅ Клан создан! Вы лидер клана {state['name']} [{state['tag']}]",
            reply_markup=reply_markup
        )
        bot_instance.log_action('create_clan', user_id, f"Created clan {state['name']}")
    
    elif data == "my_clan":
        clan_id = bot_instance.get_user_clan(user_id)
        if not clan_id:
            await query.edit_message_text("Вы не состоите в клане.")
            return
        
        update.message = query.message
        await my_clan_command(update, context)
    
    elif data == "confirm_build_factory":
        if user_id not in user_states or user_states[user_id].get('action') != 'build_factory':
            await query.edit_message_text("Ошибка: данные не найдены.")
            return
        
        state = user_states[user_id]
        clan_id = bot_instance.get_user_clan(user_id)
        clan_data = bot_instance.ref.child(f'clans/{clan_id}').get()
        
        if clan_data.get('treasury', 0) < state['cost']:
            await query.edit_message_text("В казне недостаточно средств.")
            return
        
        bot_instance.ref.child(f'clans/{clan_id}/treasury').set(
            clan_data.get('treasury', 0) - state['cost']
        )
        
        factory_id = bot_instance.ref.child(f'clans/{clan_id}/factories').push({
            'type': state['type'],
            'builder': user_id,
            'level': 1,
            'production': 10,
            'built_at': datetime.now(pytz.UTC).isoformat()
        }).key
        
        bot_instance.ref.child(f'users/{user_id}/factories_built').set(
            bot_instance.ref.child(f'users/{user_id}/factories_built').get() + 1
        )
        
        del user_states[user_id]
        
        emoji = "🏦" if state['type'] == 'financial' else "🔫"
        type_name = "финансовый" if state['type'] == 'financial' else "оружейный"
        
        await query.edit_message_text(
            f"✅ {emoji} {type_name.capitalize()} завод построен! Он производит 10 ед./час"
        )
        bot_instance.log_action('build_factory', user_id, f"Built {state['type']} factory")
    
    elif data == "confirm_declare_war":
        if user_id not in user_states or user_states[user_id].get('action') != 'declare_war':
            await query.edit_message_text("Ошибка: данные не найдены.")
            return
        
        state = user_states[user_id]
        clan_id = bot_instance.get_user_clan(user_id)
        target_id = state['target']
        
        bot_instance.ref.child(f'clans/{clan_id}/war').set({
            'active': True,
            'enemy': target_id,
            'started_at': datetime.now(pytz.UTC).isoformat()
        })
        
        bot_instance.ref.child(f'clans/{target_id}/war').set({
            'active': True,
            'enemy': clan_id,
            'started_at': datetime.now(pytz.UTC).isoformat()
        })
        
        target_data = bot_instance.ref.child(f'clans/{target_id}').get()
        clan_data = bot_instance.ref.child(f'clans/{clan_id}').get()
        
        del user_states[user_id]
        
        await query.edit_message_text(
            f"⚔️ Война объявлена клану {target_data['name']}! Лидеры и офицеры могут атаковать."
        )
        bot_instance.log_action('declare_war', user_id, f"Declared war on {target_id}")
    
    elif data == "confirm_attack":
        if user_id not in user_states or user_states[user_id].get('action') != 'attack':
            await query.edit_message_text("Ошибка: данные не найдены.")
            return
        
        state = user_states[user_id]
        clan_id = bot_instance.get_user_clan(user_id)
        target_id = state['target']
        troops = state['troops']
        
        await query.edit_message_text("⚔️ Атака началась, ожидайте результата...")
        
        await asyncio.sleep(random.randint(10, 30))
        
        clan_data = bot_instance.ref.child(f'clans/{clan_id}').get()
        target_data = bot_instance.ref.child(f'clans/{target_id}').get()
        
        our_weapons = clan_data.get('weapons', 0)
        our_effectiveness = min(1.0, our_weapons / max(troops, 1))
        our_power = troops * our_effectiveness
        
        enemy_troops = target_data.get('army', 0)
        enemy_weapons = target_data.get('weapons', 0)
        enemy_defense = target_data.get('defense', 0)
        
        enemy_effectiveness = min(1.0, enemy_weapons / max(enemy_troops + enemy_defense, 1))
        enemy_power = (enemy_troops * 0.3 + enemy_defense) * enemy_effectiveness
        
        our_losses = int(troops * (enemy_power / (our_power + enemy_power + 1)) * random.uniform(0.3, 0.7))
        enemy_losses = int(enemy_troops * 0.1 * random.uniform(0.5, 1.5))
        capital_damage = int(our_power * 2)
        
        bot_instance.ref.child(f'clans/{clan_id}/army').set(
            max(0, clan_data.get('army', 0) - our_losses)
        )
        bot_instance.ref.child(f'clans/{target_id}/army').set(
            max(0, target_data.get('army', 0) - enemy_losses)
        )
        bot_instance.ref.child(f'clans/{target_id}/capital_hp').set(
            max(0, target_data.get('capital_hp', 10000) - capital_damage)
        )
        
        del user_states[user_id]
        
        await query.edit_message_text(
            f"📊 Результат атаки:\n\n"
            f"💀 Ваши потери: {our_losses} бойцов\n"
            f"💀 Потери врага: {enemy_losses} бойцов\n"
            f"🏰 Урон по столице врага: {capital_damage} HP"
        )
        bot_instance.log_action('attack', user_id, f"Attacked {target_id} with {troops} troops")
    
    elif data == "admin_toggle_bot":
        if query.from_user.username != ADMIN_USERNAME:
            return
        
        settings = bot_instance.ref.child('settings').get()
        new_status = not settings.get('bot_enabled', True)
        bot_instance.ref.child('settings/bot_enabled').set(new_status)
        
        status_text = "включен" if new_status else "выключен"
        await query.edit_message_text(f"✅ Бот {status_text}")
    
    elif data == "admin_backup":
        if query.from_user.username != ADMIN_USERNAME:
            return
        
        all_data = bot_instance.ref.get()
        backup_json = json.dumps(all_data, indent=2, ensure_ascii=False)
        
        filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(backup_json)
        
        await context.bot.send_document(
            chat_id=query.from_user.id,
            document=open(filename, 'rb'),
            caption="📦 Бэкап базы данных"
        )
        
        import os
        os.remove(filename)
        
        await query.answer("Бэкап создан и отправлен в личные сообщения")
    
    elif data.startswith("admin_"):
        await query.answer("Функция в разработке")

async def hourly_task():
    while True:
        await asyncio.sleep(3600)
        
        clans = bot_instance.ref.child('clans').get()
        if not clans:
            continue
        
        for clan_id, clan_data in clans.items():
            factories = clan_data.get('factories', {})
            
            for factory_id, factory_data in factories.items():
                if factory_data['type'] == 'financial':
                    production = factory_data.get('production', 10)
                    bot_instance.ref.child(f'clans/{clan_id}/treasury').set(
                        clan_data.get('treasury', 0) + production
                    )
                elif factory_data['type'] == 'weapon':
                    production = factory_data.get('production', 10)
                    bot_instance.ref.child(f'clans/{clan_id}/weapons').set(
                        clan_data.get('weapons', 0) + production
                    )
            
            productions = clan_data.get('productions', {})
            for prod_id, prod_data in productions.items():
                level = prod_data.get('level', 1)
                production_rate = 5 if level == 1 else 10
                bot_instance.ref.child(f'clans/{clan_id}/productions/{prod_id}/stock').set(
                    prod_data.get('stock', 0) + production_rate
                )

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("создать_клан", create_clan_command))
    application.add_handler(CommandHandler("мой_клан", my_clan_command))
    application.add_handler(CommandHandler("работа", work_command))
    application.add_handler(CommandHandler("работа2", work2_command))
    application.add_handler(CommandHandler("завод", factory_work_command))
    application.add_handler(CommandHandler("строй_завод", build_factory_command))
    application.add_handler(CommandHandler("объявить_войну", declare_war_command))
    application.add_handler(CommandHandler("мобилизация", mobilization_command))
    application.add_handler(CommandHandler("атака", attack_command))
    application.add_handler(CommandHandler("omg2105", admin_panel_command))
    application.add_handler(CommandHandler("вкл2105", test_mode_on_command))
    application.add_handler(CommandHandler("выкл2105", test_mode_off_command))
    
    application.add_handler(CallbackQueryHandler(callback_handler))
    
    loop = asyncio.get_event_loop()
    loop.create_task(hourly_task())
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()

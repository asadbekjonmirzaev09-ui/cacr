import asyncio
import random
import json
import os
import time
from pathlib import Path
from datetime import datetime
from telegram import Bot, InputFile, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode

# ========== КОНФИГУРАЦИЯ ==========
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8948525560:AAFnQ9bot_3OD0jZTu9f29OGdpxbNOJOZ-0")
GAME_PASSWORD = "theganja"
ADMIN_USERNAME = "Codex_etoya"
ADMIN_ID = 8809547398
IMAGES_DIR = Path("images")
IMAGES_DIR_LIGHT = Path("images2")  # папка для Light тарифа

NORMAL_IMAGES = ["1.jpg", "2.jpg", "3.jpg", "4.jpg", "5.jpg", "6.jpg", "7.jpg", "8.jpg", "9.jpg", "10.jpg"]
SPECIAL_IMAGE = "fotox.jpg"
SPECIAL_CHANCE = 0.5

USERS_FILE = "registered_users.json"
BALANCE_FILE = "user_balances.json"
LANGUAGE_FILE = "user_languages.json"
SIGNALS_FILE = "user_signals.json"
BLACKLIST_FILE = "blacklist.json"

SIGNAL_LIMITS = {
    "light": 50,
    "pro": 150,
    "ultra": 999999
}

# ========== КОНФИГУРАЦИЯ ТАРИФОВ ДЛЯ ИГРЫ ==========
TARIFF_IMAGES = {
    "light": {
        "dir": IMAGES_DIR_LIGHT,
        "images": ["1.jpg", "2.jpg", "3.jpg", "4.jpg", "5.jpg", "6.jpg", "7.jpg", "8.jpg", "9.jpg", "10.jpg"],
        "special_chance": 0.2  # 20% шанс на fotox.jpg
    },
    "pro": {
        "dir": IMAGES_DIR,
        "images": ["1.jpg", "2.jpg", "3.jpg", "4.jpg", "5.jpg", "6.jpg", "7.jpg", "8.jpg", "9.jpg", "10.jpg"],
        "special_chance": 0.4  # 40% шанс на fotox.jpg
    },
    "ultra": {
        "dir": IMAGES_DIR,
        "images": ["1.jpg", "2.jpg", "3.jpg", "4.jpg", "5.jpg", "6.jpg", "7.jpg", "8.jpg", "9.jpg", "10.jpg"],
        "special_chance": 0.6  # 60% шанс на fotox.jpg
    }
}

# ========== ЯЗЫКИ ==========
LANGUAGES = {
    "uz": "🇺🇿 O'zbek",
    "ru": "🇷🇺 Русский",
    "en": "🇬🇧 English",
    "tg": "🇹🇯 Тоҷикӣ",
    "all": "🌍 Barcha tillar"
}

# ========== ПЕРЕВОДЫ ==========
TEXTS = {
    "uz": {
        "welcome": "🐔 XUSH KELIBSIZ, {username}!",
        "main_menu": "🏠 MENYU",
        "play": "🐔 O'YIN BOSHLASH",
        "tariffs": "💳 TARIFLAR",
        "servers": "🌍 SERVERLAR",
        "admin": "👑 ADMINISTRATOR",
        "not_admin": "❌ Siz admin emassiz!",
        "balance_info": "💰 Balans: {balance} so'm",
        "tariff_status": "📊 Tarif: {tariff}",
        "no_access": "❌ RUHSAT YO'Q!",
        "error": "❌ Xatolik yuz berdi!",
        "signals_info": "📊 Signal: {used}/{limit}",
        "signals_infinite": "📊 Signal: ♾️ Cheksiz",
        "no_tariff": "📊 Signal: ❌ Tarif yo'q",
        "signals_limit_reached": "⚠️ SIGNALLAR TUGADI!\n\n📊 Ishlatilgan: {used}/{limit}\n⏰ Ertaga soat 11:00 dan keyin urinib ko'ring!\n\n📌 Sizning tarifingiz: {tariff}",
        "signals_status": "📊 SIGNAL STATISTIKASI\n\n📌 Tarif: {tariff}\n📈 Ishlatilgan: {used}\n📉 Qolgan: {remaining}\n📊 Holat: {status}\n🔄 Yangilanish: ertaga 11:00",
        "user_blocked": "🚫 SIZ BLOKLANGANSIZ!\n\nSiz administrator tomonidan bloklangansiz.\nSababini bilish uchun administratorga murojaat qiling.",
        "block_success": "✅ Foydalanuvchi bloklandi!\n\n📱 ID: {user_id}\n👤 Ism: {username}\n📅 Vaqt: {time}",
        "unblock_success": "✅ Foydalanuvchi blokdan ochildi!\n\n📱 ID: {user_id}\n👤 Ism: {username}",
        "block_not_found": "❌ Foydalanuvchi topilmadi!",
        "block_already": "⚠️ Foydalanuvchi allaqachon bloklangan!",
        "unblock_not_found": "❌ Foydalanuvchi blokda topilmadi!",
        "blacklist_title": "🚫 BLOKLANGAN FOYDALANUVCHILAR\n\nJami: {count}",
        "blacklist_empty": "📭 Bloklangan foydalanuvchilar yo'q",
        "blacklist_item": "📱 ID: {id}\n👤 Ism: {username}\n📅 Vaqt: {time}\n",
        "balance_added": "✅ Balans to'ldirildi!\n\n📱 Foydalanuvchi ID: {chat_id}\n💰 Qo'shilgan summa: {amount}\n💳 Yangi balans: {balance}",
        "balance_check": "💰 BALANS MA'LUMOTI\n\n📱 Foydalanuvchi ID: {chat_id}\n💳 Balans: {balance}",
        "must_be_number": "❌ Summa son bo'lishi kerak!",
        "wrong_format": "❌ Noto'g'ri format!",
        "broadcast_start": "📢 REKLAMA JO'Natish\n\nTilni tanlang:",
        "broadcast_sending": "📤 Reklama yuborilmoqda...",
        "broadcast_success": "✅ Reklama muvaffaqiyatli yuborildi!\n\n👥 Qabul qilganlar: {sent}\n❌ Xatolik: {failed}",
        "broadcast_no_users": "❌ Bu tilda foydalanuvchilar topilmadi!",
        "broadcast_cancel": "❌ Bekor qilindi!",
        "broadcast_instruction": "📝 Endi reklama matnini yoki faylni (rasm/video) yuboring.\n\n❌ Bekor qilish uchun /cancel_broadcast",
        "broadcast_lang_selected": "✅ Til tanlandi: {lang}",
        "broadcast_cancel_confirm": "✅ Reklama bekor qilindi!",
        "old_button": "⚠️ Kupon eskirgan. Yangi menyu yuborilmoqda...",
        "game_start": "🐔 O'YIN BOSHLANDI!",
        "game_continue": "🎮 DAVOM ETISH",
        "game_over": "🎲 MAG'LUBIYAT!\nYangi sikl boshlanmoqda!",
        "good_luck": "🐔 Omad tilaymiz!",
        "game_reset": "✅ O'yin tugadi!",
        "back": "◀️ ORQAGA",
        "register": "📝 RO'YXATDAN O'TISH",
        "enter_password_btn": "🔑 PAROLNI KIRITISH",
        "enter_password": "🔐 PAROLNI KIRITING",
        "enter_password_prompt": "🔐 PAROLNI KIRITING\n\nParolni xabar sifatida yuboring:",
        "not_registered": "📝 RO'YXATDAN O'TISH KERAK!",
        "enter_id": "✍️ TO'LIQ ID-INGIZNI YOZING!",
        "example_id": "📌 Masalan: 8773403704 yoki MyName123",
        "id_instruction": "⚠️ DIQQAT: O'zingizga qulay ID (raqam yoki harflar) ni kiriting!",
        "registration_success": "✅ RO'YXATDAN O'TISH MUVOFIQIYATLI!",
        "your_id": "📱 Sizning ID: {custom_id}",
        "your_name": "👤 Ism: {username}",
        "initial_balance": "💰 Boshlang'ich balans: 100 000 so'm",
        "password_instruction": "🔐 ENDI PAROLNI KIRITING!",
        "password_hint": "💡 Parol: {password}",
        "wrong_id": "❌ NOTO'G'RI ID!",
        "retry": "🔄 QAYTA URINISH",
        "password_correct": "✅ PAROL TO'G'RI!",
        "access_granted": "KIRISH RUHSAT ETILDI!",
        "wrong_password": "❌ NOTO'G'RI PAROL!",
        "retry_password": "🔑 QAYTA URINISH",
        "need_tariff": "⚠️ AVVAL TARIF ULANG!",
        "need_tariff_desc": "O'yinni boshlash uchun avval tarif ulashingiz kerak!",
        "must_register": "❌ AVVAL RO'YXATDAN O'TING!",
        "no_balance": "❌ BALANSINGIZ YETARLI EMAS!",
        "tariff_price": "💲 Tarif narxi: {price}",
        "need_more": "📉 Yetishmayotgan summa: {need}",
        "contact_admin_balance": "Balansni to'ldirish uchun 👑 ADMINISTRATOR ga murojaat qiling.",
        "tariff_selected": "✅ TARIF FAQATLASHTIRILDI!",
        "new_balance": "💰 Yangi balans: {balance}",
        "tariff_info": "💳 TARIFLAR\n\n💰 Sizning balansingiz: {balance}\n📊 Joriy tarif: {tariff}\n\n",
        "choose_language": "🌐 TILNI TANLANG",
        "language_selected": "✅ Til o'zgartirildi!",
        "select_language": "🌐 TILNI TANLANG",
        "current_tariff": "Yo'q",
        "none": "Yo'q",
        "currency": "so'm",
        "servers_title": "🌍 SERVERLAR\n\nQuyidagi serverlardan birini tanlang:",
        "server_uz": "🇺🇿 O'zbekiston",
        "server_ru": "🇷🇺 Rossiya",
        "server_tj": "🇹🇯 Tojikiston",
        "server_us": "🇺🇸 Amerika",
        "server_selected": "✅ Siz serverga ulandingiz: {server}!",
        "choose_tariff": "Tarifni tanlang:",
        "admin_contact": "👤 Ваш ID: {custom_id}\n📱 Telegram ID: {user_id}\n\n📩 Отправьте этот ID администратору для решения вопросов.",
        "write_admin": "📩 НАПИСАТЬ АДМИНИСТРАТОРУ",
        "photo_error": "❌ Xato: {filename} topilmadi!",
        "enter_valid_id": "✍️ O'zingizning ID-INGIZNI yozing!",
        "top_up_balance": "💰 BALANSNI TO'LDIRISH",
        "top_up_info": "💰 BALANSNI TO'LDIRISH\n\nMinimal to'ldirish summasi: 10 000 so'm\n\n📩 Balansni to'ldirish uchun administratorga yozing:",
        "top_up_min_amount": "10 000 so'm"
    },
    "ru": {
        "welcome": "🐔 ДОБРО ПОЖАЛОВАТЬ, {username}!",
        "main_menu": "🏠 МЕНЮ",
        "play": "🐔 НАЧАТЬ ИГРУ",
        "tariffs": "💳 ТАРИФЫ",
        "servers": "🌍 СЕРВЕРЫ",
        "admin": "👑 АДМИНИСТРАТОР",
        "not_admin": "❌ Вы не админ!",
        "balance_info": "💰 Баланс: {balance} $",
        "tariff_status": "📊 Тариф: {tariff}",
        "no_access": "❌ НЕТ ДОСТУПА!",
        "error": "❌ Произошла ошибка!",
        "signals_info": "📊 Сигналы: {used}/{limit}",
        "signals_infinite": "📊 Сигналы: ♾️ Безлимит",
        "no_tariff": "📊 Сигналы: ❌ Нет тарифа",
        "signals_limit_reached": "⚠️ СИГНАЛЫ ЗАКОНЧИЛИСЬ!\n\n📊 Использовано: {used}/{limit}\n⏰ Попробуйте завтра после 11:00!\n\n📌 Ваш тариф: {tariff}",
        "signals_status": "📊 СТАТИСТИКА СИГНАЛОВ\n\n📌 Тариф: {tariff}\n📈 Использовано: {used}\n📉 Осталось: {remaining}\n📊 Статус: {status}\n🔄 Обновление: завтра 11:00",
        "user_blocked": "🚫 ВЫ ЗАБЛОКИРОВАНЫ!\n\nВы заблокированы администратором.\nДля уточнения причины обратитесь к администратору.",
        "block_success": "✅ Пользователь заблокирован!\n\n📱 ID: {user_id}\n👤 Имя: {username}\n📅 Время: {time}",
        "unblock_success": "✅ Пользователь разблокирован!\n\n📱 ID: {user_id}\n👤 Имя: {username}",
        "block_not_found": "❌ Пользователь не найден!",
        "block_already": "⚠️ Пользователь уже заблокирован!",
        "unblock_not_found": "❌ Пользователь не найден в черном списке!",
        "blacklist_title": "🚫 ЗАБЛОКИРОВАННЫЕ ПОЛЬЗОВАТЕЛИ\n\nВсего: {count}",
        "blacklist_empty": "📭 Заблокированных пользователей нет",
        "blacklist_item": "📱 ID: {id}\n👤 Имя: {username}\n📅 Время: {time}\n",
        "balance_added": "✅ Баланс пополнен!\n\n📱 ID пользователя: {chat_id}\n💰 Добавлено: {amount} $\n💳 Новый баланс: {balance} $",
        "balance_check": "💰 ИНФОРМАЦИЯ О БАЛАНСЕ\n\n📱 ID пользователя: {chat_id}\n💳 Баланс: {balance} $",
        "must_be_number": "❌ Сумма должна быть числом!",
        "wrong_format": "❌ Неверный формат!",
        "broadcast_start": "📢 РАССЫЛКА РЕКЛАМЫ\n\nВыберите язык:",
        "broadcast_sending": "📤 Отправка рекламы...",
        "broadcast_success": "✅ Реклама успешно отправлена!\n\n👥 Получили: {sent}\n❌ Ошибок: {failed}",
        "broadcast_no_users": "❌ Пользователи с этим языком не найдены!",
        "broadcast_cancel": "❌ Отменено!",
        "broadcast_instruction": "📝 Теперь отправьте текст рекламы или файл (фото/видео).\n\n❌ Для отмены используйте /cancel_broadcast",
        "broadcast_lang_selected": "✅ Язык выбран: {lang}",
        "broadcast_cancel_confirm": "✅ Рассылка отменена!",
        "old_button": "⚠️ Кнопка устарела. Отправляю новое меню...",
        "game_start": "🐔 ИГРА НАЧАТА!",
        "game_continue": "🎮 ПРОДОЛЖИТЬ",
        "game_over": "🎲 ПОРАЖЕНИЕ!\nНачинается новый цикл!",
        "good_luck": "🐔 Удачи!",
        "game_reset": "✅ Игра завершена!",
        "back": "◀️ НАЗАД",
        "register": "📝 ЗАРЕГИСТРИРОВАТЬСЯ",
        "enter_password_btn": "🔑 ВВЕСТИ ПАРОЛЬ",
        "enter_password": "🔐 ВВЕДИТЕ ПАРОЛЬ",
        "enter_password_prompt": "🔐 ВВЕДИТЕ ПАРОЛЬ\n\nОтправьте пароль сообщением:",
        "not_registered": "📝 НЕОБХОДИМА РЕГИСТРАЦИЯ!",
        "enter_id": "✍️ ВВЕДИТЕ ВАШ ПОЛНЫЙ ID!",
        "example_id": "📌 Например: 8773403704 или MyName123",
        "id_instruction": "⚠️ ВНИМАНИЕ: Введите удобный для вас ID (цифры или буквы)!",
        "registration_success": "✅ РЕГИСТРАЦИЯ УСПЕШНА!",
        "your_id": "📱 Ваш ID: {custom_id}",
        "your_name": "👤 Имя: {username}",
        "initial_balance": "💰 Начальный баланс: 100 $",
        "password_instruction": "🔐 ТЕПЕРЬ ВВЕДИТЕ ПАРОЛЬ!",
        "password_hint": "💡 Пароль: {password}",
        "wrong_id": "❌ НЕВЕРНЫЙ ID!",
        "retry": "🔄 ПОПРОБОВАТЬ СНОВА",
        "password_correct": "✅ ПАРОЛЬ ВЕРНЫЙ!",
        "access_granted": "ДОСТУП РАЗРЕШЕН!",
        "wrong_password": "❌ НЕВЕРНЫЙ ПАРОЛЬ!",
        "retry_password": "🔑 ПОПРОБОВАТЬ СНОВА",
        "need_tariff": "⚠️ СНАЧАЛА ПОДКЛЮЧИТЕ ТАРИФ!",
        "need_tariff_desc": "Чтобы начать игру, сначала подключите тариф!",
        "must_register": "❌ СНАЧАЛА ЗАРЕГИСТРИРУЙТЕСЬ!",
        "no_balance": "❌ НЕДОСТАТОЧНО БАЛАНСА!",
        "tariff_price": "💲 Цена тарифа: {price}",
        "need_more": "📉 Недостающая сумма: {need} $",
        "contact_admin_balance": "Для пополнения баланса обратитесь к 👑 АДМИНИСТРАТОРУ.",
        "tariff_selected": "✅ ТАРИФ АКТИВИРОВАН!",
        "new_balance": "💰 Новый баланс: {balance} $",
        "tariff_info": "💳 ТАРИФЫ\n\n💰 Ваш баланс: {balance} $\n📊 Текущий тариф: {tariff}\n\n",
        "choose_language": "🌐 ВЫБЕРИТЕ ЯЗЫК",
        "language_selected": "✅ Язык изменен!",
        "select_language": "🌐 ВЫБЕРИТЕ ЯЗЫК",
        "current_tariff": "Нет",
        "none": "Нет",
        "currency": "$",
        "servers_title": "🌍 СЕРВЕРЫ\n\nВыберите один из серверов:",
        "server_uz": "🇺🇿 Узбекистан",
        "server_ru": "🇷🇺 Россия",
        "server_tj": "🇹🇯 Таджикистан",
        "server_us": "🇺🇸 Америка",
        "server_selected": "✅ Вы подключились к серверу: {server}!",
        "choose_tariff": "Выберите тариф:",
        "admin_contact": "👤 Ваш ID: {custom_id}\n📱 Telegram ID: {user_id}\n\n📩 Отправьте этот ID администратору для решения вопросов.",
        "write_admin": "📩 НАПИСАТЬ АДМИНИСТРАТОРУ",
        "photo_error": "❌ Ошибка: {filename} не найден!",
        "enter_valid_id": "✍️ Введите ваш ID!",
        "top_up_balance": "💰 ПОПОЛНИТЬ БАЛАНС",
        "top_up_info": "💰 ПОПОЛНЕНИЕ БАЛАНСА\n\nМинимальная сумма пополнения: 10 $\n\n📩 Для пополнения баланса напишите администратору:",
        "top_up_min_amount": "10 $"
    },
    "en": {
        "welcome": "🐔 WELCOME, {username}!",
        "main_menu": "🏠 MENU",
        "play": "🐔 START GAME",
        "tariffs": "💳 TARIFFS",
        "servers": "🌍 SERVERS",
        "admin": "👑 ADMINISTRATOR",
        "not_admin": "❌ You are not admin!",
        "balance_info": "💰 Balance: {balance} $",
        "tariff_status": "📊 Tariff: {tariff}",
        "no_access": "❌ NO ACCESS!",
        "error": "❌ An error occurred!",
        "signals_info": "📊 Signals: {used}/{limit}",
        "signals_infinite": "📊 Signals: ♾️ Unlimited",
        "no_tariff": "📊 Signals: ❌ No tariff",
        "signals_limit_reached": "⚠️ SIGNALS ARE OVER!\n\n📊 Used: {used}/{limit}\n⏰ Try again tomorrow after 11:00!\n\n📌 Your tariff: {tariff}",
        "signals_status": "📊 SIGNAL STATISTICS\n\n📌 Tariff: {tariff}\n📈 Used: {used}\n📉 Remaining: {remaining}\n📊 Status: {status}\n🔄 Reset: tomorrow 11:00",
        "user_blocked": "🚫 YOU ARE BLOCKED!\n\nYou have been blocked by the administrator.\nPlease contact the administrator for more information.",
        "block_success": "✅ User blocked!\n\n📱 ID: {user_id}\n👤 Username: {username}\n📅 Time: {time}",
        "unblock_success": "✅ User unblocked!\n\n📱 ID: {user_id}\n👤 Username: {username}",
        "block_not_found": "❌ User not found!",
        "block_already": "⚠️ User is already blocked!",
        "unblock_not_found": "❌ User not found in blacklist!",
        "blacklist_title": "🚫 BLOCKED USERS\n\nTotal: {count}",
        "blacklist_empty": "📭 No blocked users",
        "blacklist_item": "📱 ID: {id}\n👤 Username: {username}\n📅 Time: {time}\n",
        "balance_added": "✅ Balance added!\n\n📱 User ID: {chat_id}\n💰 Added: {amount} $\n💳 New balance: {balance} $",
        "balance_check": "💰 BALANCE INFO\n\n📱 User ID: {chat_id}\n💳 Balance: {balance} $",
        "must_be_number": "❌ Amount must be a number!",
        "wrong_format": "❌ Wrong format!",
        "broadcast_start": "📢 AD BROADCAST\n\nSelect language:",
        "broadcast_sending": "📤 Sending advertisement...",
        "broadcast_success": "✅ Advertisement sent successfully!\n\n👥 Received: {sent}\n❌ Failed: {failed}",
        "broadcast_no_users": "❌ No users found with this language!",
        "broadcast_cancel": "❌ Cancelled!",
        "broadcast_instruction": "📝 Now send the advertisement text or file (photo/video).\n\n❌ To cancel use /cancel_broadcast",
        "broadcast_lang_selected": "✅ Language selected: {lang}",
        "broadcast_cancel_confirm": "✅ Broadcast cancelled!",
        "old_button": "⚠️ Button is outdated. Sending new menu...",
        "game_start": "🐔 GAME STARTED!",
        "game_continue": "🎮 CONTINUE",
        "game_over": "🎲 DEFEAT!\nStarting new cycle!",
        "good_luck": "🐔 Good luck!",
        "game_reset": "✅ Game finished!",
        "back": "◀️ BACK",
        "register": "📝 REGISTER",
        "enter_password_btn": "🔑 ENTER PASSWORD",
        "enter_password": "🔐 ENTER PASSWORD",
        "enter_password_prompt": "🔐 ENTER PASSWORD\n\nSend password as message:",
        "not_registered": "📝 REGISTRATION REQUIRED!",
        "enter_id": "✍️ ENTER YOUR FULL ID!",
        "example_id": "📌 Example: 8773403704 or MyName123",
        "id_instruction": "⚠️ NOTE: Enter an ID that's convenient for you (numbers or letters)!",
        "registration_success": "✅ REGISTRATION SUCCESSFUL!",
        "your_id": "📱 Your ID: {custom_id}",
        "your_name": "👤 Name: {username}",
        "initial_balance": "💰 Initial balance: 100 $",
        "password_instruction": "🔐 NOW ENTER THE PASSWORD!",
        "password_hint": "💡 Password: {password}",
        "wrong_id": "❌ INVALID ID!",
        "retry": "🔄 TRY AGAIN",
        "password_correct": "✅ PASSWORD CORRECT!",
        "access_granted": "ACCESS GRANTED!",
        "wrong_password": "❌ WRONG PASSWORD!",
        "retry_password": "🔑 TRY AGAIN",
        "need_tariff": "⚠️ FIRST CONNECT TARIFF!",
        "need_tariff_desc": "To start the game, you must first connect a tariff!",
        "must_register": "❌ REGISTER FIRST!",
        "no_balance": "❌ INSUFFICIENT BALANCE!",
        "tariff_price": "💲 Tariff price: {price}",
        "need_more": "📉 Amount needed: {need} $",
        "contact_admin_balance": "Contact 👑 ADMINISTRATOR to top up balance.",
        "tariff_selected": "✅ TARIFF ACTIVATED!",
        "new_balance": "💰 New balance: {balance} $",
        "tariff_info": "💳 TARIFFS\n\n💰 Your balance: {balance} $\n📊 Current tariff: {tariff}\n\n",
        "choose_language": "🌐 CHOOSE LANGUAGE",
        "language_selected": "✅ Language changed!",
        "select_language": "🌐 CHOOSE LANGUAGE",
        "current_tariff": "None",
        "none": "None",
        "currency": "$",
        "servers_title": "🌍 SERVERS\n\nSelect one of the servers:",
        "server_uz": "🇺🇿 Uzbekistan",
        "server_ru": "🇷🇺 Russia",
        "server_tj": "🇹🇯 Tajikistan",
        "server_us": "🇺🇸 America",
        "server_selected": "✅ You have connected to the server: {server}!",
        "choose_tariff": "Choose tariff:",
        "admin_contact": "👤 Your ID: {custom_id}\n📱 Telegram ID: {user_id}\n\n📩 Send this ID to the administrator to resolve issues.",
        "write_admin": "📩 WRITE TO ADMIN",
        "photo_error": "❌ Error: {filename} not found!",
        "enter_valid_id": "✍️ Enter your ID!",
        "top_up_balance": "💰 TOP UP BALANCE",
        "top_up_info": "💰 TOP UP BALANCE\n\nMinimum top up amount: 10 $\n\n📩 To top up your balance, write to the administrator:",
        "top_up_min_amount": "10 $"
    },
    "tg": {
        "welcome": "🐔 ХУШ ОМАДЕД, {username}!",
        "main_menu": "🏠 МЕНЮ",
        "play": "🐔 ОҒОЗИ БОЗӢ",
        "tariffs": "💳 ТАРИФҲО",
        "servers": "🌍 СЕРВЕРҲО",
        "admin": "👑 МАЪМУР",
        "not_admin": "❌ Шумо маъмур нестед!",
        "balance_info": "💰 Баланс: {balance} сӯм",
        "tariff_status": "📊 Тариф: {tariff}",
        "no_access": "❌ ДАСТРАСӢ НЕСТ!",
        "error": "❌ Хато рух дод!",
        "signals_info": "📊 Сигнал: {used}/{limit}",
        "signals_infinite": "📊 Сигнал: ♾️ Беохир",
        "no_tariff": "📊 Сигнал: ❌ Тариф нест",
        "signals_limit_reached": "⚠️ СИГНАЛҲО ТАМОМ ШУДАНД!\n\n📊 Истифода шуд: {used}/{limit}\n⏰ Пагоҳ аз соати 11:00 кӯшиш кунед!\n\n📌 Тарифи шумо: {tariff}",
        "signals_status": "📊 СТАТИСТИКАИ СИГНАЛҲО\n\n📌 Тариф: {tariff}\n📈 Истифода шуд: {used}\n📉 Мондааст: {remaining}\n📊 Ҳолат: {status}\n🔄 Навсозӣ: пагоҳ 11:00",
        "user_blocked": "🚫 ШУМО БЛОК КАРДА ШУДЕД!\n\nШумо аз ҷониби маъмур блок карда шудед.\nБарои маълумот ба маъмур муроҷиат кунед.",
        "block_success": "✅ Корбар блок карда шуд!\n\n📱 ID: {user_id}\n👤 Ном: {username}\n📅 Вақт: {time}",
        "unblock_success": "✅ Корбар аз блок кушода шуд!\n\n📱 ID: {user_id}\n👤 Ном: {username}",
        "block_not_found": "❌ Корбар ёфт нашуд!",
        "block_already": "⚠️ Корбар аллакай блок шудааст!",
        "unblock_not_found": "❌ Корбар дар рӯйхати сиёҳ ёфт нашуд!",
        "blacklist_title": "🚫 КОРБАРОНИ БЛОКШУДА\n\nҲамагӣ: {count}",
        "blacklist_empty": "📭 Корбарони блокшуда нестанд",
        "blacklist_item": "📱 ID: {id}\n👤 Ном: {username}\n📅 Вақт: {time}\n",
        "balance_added": "✅ Баланс пур шуд!\n\n📱 ID-и корбар: {chat_id}\n💰 Илова шуд: {amount} сӯм\n💳 Баланси нав: {balance} сӯм",
        "balance_check": "💰 ИТТИЛООТ ДАР БОРАИ БАЛАНС\n\n📱 ID-и корбар: {chat_id}\n💳 Баланс: {balance} сӯм",
        "must_be_number": "❌ Маблағ бояд адад бошад!",
        "wrong_format": "❌ Формати нодуруст!",
        "broadcast_start": "📢 РЕКЛАМА ФИРИСТОДАН\n\nЗабонро интихоб кунед:",
        "broadcast_sending": "📤 Реклама фиристода мешавад...",
        "broadcast_success": "✅ Реклама бомуваффақият фиристода шуд!\n\n👥 Қабул карданд: {sent}\n❌ Хато: {failed}",
        "broadcast_no_users": "❌ Корбарон бо ин забон ёфт нашуд!",
        "broadcast_cancel": "❌ Бекор карда шуд!",
        "broadcast_instruction": "📝 Акнун матни реклама ё файл (расм/видео) фиристед.\n\n❌ Бекор кардан барои /cancel_broadcast",
        "broadcast_lang_selected": "✅ Забон интихоб шуд: {lang}",
        "broadcast_cancel_confirm": "✅ Реклама бекор карда шуд!",
        "old_button": "⚠️ Кнопка кӯҳна шуд. Менюи нав фиристода мешавад...",
        "game_start": "🐔 БОЗИ ОҒОЗ ШУД!",
        "game_continue": "🎮 ИДОМА ДОДАН",
        "game_over": "🎲 ШИКАСТ!\nДавраи нав оғоз мешавад!",
        "good_luck": "🐔 Корбарорӣ!",
        "game_reset": "✅ Бозӣ тамом шуд!",
        "back": "◀️ БОЗГАШТ",
        "register": "📝 БА ҚАЙД ГИРИФТАН",
        "enter_password_btn": "🔑 ВОРИД КАРДАНИ РАМЗ",
        "enter_password": "🔐 РАМЗРО ВОРИД КУНЕД",
        "enter_password_prompt": "🔐 РАМЗРО ВОРИД КУНЕД\n\nРамзро ҳамчун паём фиристед:",
        "not_registered": "📝 БА ҚАЙД ГИРИФТАН ЛОЗИМ АСТ!",
        "enter_id": "✍️ ID-И ПУРРАИ ХУДРО ВОРИД КУНЕД!",
        "example_id": "📌 Масалан: 8773403704 ё MyName123",
        "id_instruction": "⚠️ ДИҚҚАТ: ID-и бароятон қулай (рақам ё ҳарф) - ро ворид кунед!",
        "registration_success": "✅ БА ҚАЙД ГИРИФТАН МУВАФФАҚИЯТЛИ!",
        "your_id": "📱 ID-и Шумо: {custom_id}",
        "your_name": "👤 Ном: {username}",
        "initial_balance": "💰 Баланси аввалӣ: 100 сӯм",
        "password_instruction": "🔐 АКНУН РАМЗРО ВОРИД КУНЕД!",
        "password_hint": "💡 Рамз: {password}",
        "wrong_id": "❌ ID-И НОДУРУСТ!",
        "retry": "🔄 АЗ НАВ КӮШИШ",
        "password_correct": "✅ РАМЗ ДУРУСТ АСТ!",
        "access_granted": "ДАСТРАСӢ ИҶОЗАТ ДОДА ШУД!",
        "wrong_password": "❌ РАМЗИ НОДУРУСТ!",
        "retry_password": "🔑 АЗ НАВ КӮШИШ",
        "need_tariff": "⚠️ АВВАЛ ТАРИФ ПАЙВАСТ КУНЕД!",
        "need_tariff_desc": "Барои оғози бозӣ, аввал тариф пайваст кунед!",
        "must_register": "❌ АВВАЛ БА ҚАЙД ГИРИФТАН ЛОЗИМ!",
        "no_balance": "❌ БАЛАНС НОКОФӢ!",
        "tariff_price": "💲 Нархи тариф: {price}",
        "need_more": "📉 Маблағи нақс: {need} сӯм",
        "contact_admin_balance": "Барои пур кардани баланс ба 👑 МАЪМУР муроҷиат кунед.",
        "tariff_selected": "✅ ТАРИФ ФАЪОЛ ГАРДИД!",
        "new_balance": "💰 Баланси нав: {balance} сӯм",
        "tariff_info": "💳 ТАРИФҲО\n\n💰 Баланси Шумо: {balance} сӯм\n📊 Тарифи ҷорӣ: {tariff}\n\n",
        "choose_language": "🌐 ЗАБОНРО ИНТИХОБ КУНЕД",
        "language_selected": "✅ Забон тағйир ёфт!",
        "select_language": "🌐 ЗАБОНРО ИНТИХОБ КУНЕД",
        "current_tariff": "Нест",
        "none": "Нест",
        "currency": "сӯм",
        "servers_title": "🌍 СЕРВЕРҲО\n\nЯке аз серверҳоро интихоб кунед:",
        "server_uz": "🇺🇿 Ӯзбекистон",
        "server_ru": "🇷🇺 Русия",
        "server_tj": "🇹🇯 Тоҷикистон",
        "server_us": "🇺🇸 Амрико",
        "server_selected": "✅ Шумо ба сервер пайваст шудед: {server}!",
        "choose_tariff": "Тарифро интихоб кунед:",
        "admin_contact": "👤 ID-и Шумо: {custom_id}\n📱 Telegram ID: {user_id}\n\n📩 Ин ID-ро ба маъмур фиристед то масъалаҳо ҳал шаванд.",
        "write_admin": "📩 НАВИШТАН БА МАЪМУР",
        "photo_error": "❌ Хато: {filename} ёфт нашуд!",
        "enter_valid_id": "✍️ ID-и худатонро ворид кунед!",
        "top_up_balance": "💰 ПОПОЛНИТЬ БАЛАНС",
        "top_up_info": "💰 ПОПОЛНЕНИЕ БАЛАНСА\n\nМинимальная сумма пополнения: 10 сомони\n\n📩 Для пополнения баланса напишите администратору:",
        "top_up_min_amount": "10 сомони"
    }
}

# ============================

# ========== ТАРИФЫ ==========
TARIFF_PRICES = {
    "uz": {"light": 350000, "pro": 500000, "ultra": 1000000},
    "ru": {"light": 30, "pro": 50, "ultra": 100},
    "en": {"light": 30, "pro": 50, "ultra": 100},
    "tg": {"light": 300, "pro": 500, "ultra": 1000}
}

TARIFFS = {
    "light": {"name": "Light Bot"},
    "pro": {"name": "Pro Bot"},
    "ultra": {"name": "Ultra Bot"}
}

# ============================

def load_json_file(filename, default=None):
    if default is None:
        default = {}
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return default
    return default

def save_json_file(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

registered_users = load_json_file(USERS_FILE)
user_balances = load_json_file(BALANCE_FILE)
user_languages = load_json_file(LANGUAGE_FILE)
blacklist = load_json_file(BLACKLIST_FILE)
user_states = {}
broadcast_states = {}

# ========== ФУНКЦИИ ДЛЯ РАБОТЫ С БЛОК-ЛИСТОМ ==========

def is_user_blocked(chat_id):
    chat_id = str(chat_id)
    return chat_id in blacklist

def block_user(chat_id, username=None):
    chat_id = str(chat_id)
    if chat_id in blacklist:
        return False
    blacklist[chat_id] = {
        "username": username or "Unknown",
        "blocked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    save_json_file(BLACKLIST_FILE, blacklist)
    return True

def unblock_user(chat_id):
    chat_id = str(chat_id)
    if chat_id not in blacklist:
        return False
    del blacklist[chat_id]
    save_json_file(BLACKLIST_FILE, blacklist)
    return True

def get_blacklist():
    return blacklist

# ========== ФУНКЦИИ ДЛЯ РАБОТЫ С СИГНАЛАМИ ==========

def load_signals():
    if os.path.exists(SIGNALS_FILE):
        try:
            with open(SIGNALS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_signals(signals_data):
    with open(SIGNALS_FILE, 'w', encoding='utf-8') as f:
        json.dump(signals_data, f, ensure_ascii=False, indent=2)

def get_user_signals(chat_id):
    chat_id = str(chat_id)
    signals_data = load_signals()
    today = time.strftime("%Y-%m-%d")
    
    if chat_id not in signals_data:
        signals_data[chat_id] = {"count": 0, "date": today}
        save_signals(signals_data)
        return 0
    
    if signals_data[chat_id].get("date") != today:
        signals_data[chat_id] = {"count": 0, "date": today}
        save_signals(signals_data)
        return 0
    
    return signals_data[chat_id].get("count", 0)

def increment_user_signals(chat_id):
    chat_id = str(chat_id)
    signals_data = load_signals()
    today = time.strftime("%Y-%m-%d")
    
    if chat_id not in signals_data or signals_data[chat_id].get("date") != today:
        signals_data[chat_id] = {"count": 0, "date": today}
    
    signals_data[chat_id]["count"] += 1
    save_signals(signals_data)
    return signals_data[chat_id]["count"]

def can_use_signal(chat_id):
    chat_id = str(chat_id)
    user_state = get_user_state(chat_id)
    tariff = user_state.get("tariff", "none")
    
    if tariff == "none":
        return False, "no_tariff"
    
    limit = SIGNAL_LIMITS.get(tariff, 0)
    
    if limit == 999999:
        return True, None
    
    used = get_user_signals(chat_id)
    
    if used >= limit:
        return False, "signals_limit_reached"
    
    return True, None

# ============================

def get_user_language(chat_id):
    chat_id = str(chat_id)
    return user_languages.get(chat_id, "uz")

def set_user_language(chat_id, lang):
    chat_id = str(chat_id)
    user_languages[chat_id] = lang
    save_json_file(LANGUAGE_FILE, user_languages)

def get_text(chat_id, key, **kwargs):
    lang = get_user_language(chat_id)
    text = TEXTS.get(lang, TEXTS["uz"]).get(key, key)
    if kwargs:
        return text.format(**kwargs)
    return text

def get_tariff_price(chat_id, tariff_key):
    lang = get_user_language(chat_id)
    prices = TARIFF_PRICES.get(lang, TARIFF_PRICES["uz"])
    return prices.get(tariff_key, 0)

def get_tariff_price_text(chat_id, tariff_key):
    price = get_tariff_price(chat_id, tariff_key)
    currency = get_text(chat_id, "currency")
    return f"{price} {currency}"

def get_user_state(chat_id):
    chat_id = str(chat_id)
    if chat_id not in user_states:
        user_states[chat_id] = {
            "current_index": 0,
            "special_triggered": False,
            "has_access": False,
            "registered": chat_id in registered_users,
            "step": "main",
            "tariff": "none",
            "server": "none"
        }
    return user_states[chat_id]

def get_balance(chat_id):
    chat_id = str(chat_id)
    return user_balances.get(chat_id, 0)

def set_balance(chat_id, amount):
    chat_id = str(chat_id)
    user_balances[chat_id] = amount
    save_json_file(BALANCE_FILE, user_balances)

def add_balance(chat_id, amount):
    chat_id = str(chat_id)
    current = user_balances.get(chat_id, 0)
    user_balances[chat_id] = current + amount
    save_json_file(BALANCE_FILE, user_balances)

def reset_user_cycle(chat_id):
    chat_id = str(chat_id)
    has_access = user_states.get(chat_id, {}).get("has_access", False)
    registered = user_states.get(chat_id, {}).get("registered", False)
    tariff = user_states.get(chat_id, {}).get("tariff", "none")
    server = user_states.get(chat_id, {}).get("server", "none")
    user_states[chat_id] = {
        "current_index": 0,
        "special_triggered": False,
        "has_access": has_access,
        "registered": registered,
        "step": "main",
        "tariff": tariff,
        "server": server
    }

# ========== ФУНКЦИИ МЕНЮ ==========

async def send_main_menu_to_user(context, chat_id, update=None):
    chat_id = str(chat_id)
    user_state = get_user_state(chat_id)
    
    if is_user_blocked(chat_id):
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=get_text(chat_id, "user_blocked")
            )
        except:
            pass
        return False
    
    username = "User"
    if chat_id in registered_users:
        username = registered_users[chat_id].get("username", "User")
    
    tariff_info = get_text(chat_id, "tariff_status", tariff=user_state['tariff'].upper() if user_state['tariff'] != 'none' else get_text(chat_id, "none"))
    balance_info = get_text(chat_id, "balance_info", balance=get_balance(chat_id))
    server_info = f"🌍 Server: {user_state['server'].upper() if user_state['server'] != 'none' else 'Tanlanmagan'}"
    
    signals_text = ""
    if user_state['tariff'] != 'none':
        tariff = user_state['tariff']
        limit = SIGNAL_LIMITS.get(tariff, 0)
        used = get_user_signals(chat_id)
        if limit == 999999:
            signals_text = get_text(chat_id, "signals_infinite")
        else:
            signals_text = get_text(chat_id, "signals_info", used=used, limit=limit)
    else:
        signals_text = get_text(chat_id, "no_tariff")
    
    keyboard = []
    keyboard.append([InlineKeyboardButton("🌐 " + get_text(chat_id, "choose_language"), callback_data="change_language")])
    
    if not user_state["registered"]:
        keyboard.append([InlineKeyboardButton(get_text(chat_id, "register"), callback_data="register")])
    else:
        keyboard.append([InlineKeyboardButton(get_text(chat_id, "play"), callback_data="play")])
    
    keyboard.append([InlineKeyboardButton(get_text(chat_id, "tariffs"), callback_data="show_tariffs")])
    keyboard.append([InlineKeyboardButton(get_text(chat_id, "servers"), callback_data="show_servers")])
    keyboard.append([InlineKeyboardButton(get_text(chat_id, "top_up_balance"), callback_data="top_up_balance")])
    keyboard.append([InlineKeyboardButton(get_text(chat_id, "admin"), callback_data="contact_admin")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = get_text(chat_id, "welcome", username=username)
    full_text = f"{welcome_text}\n\n{tariff_info}\n{balance_info}\n{server_info}\n{signals_text}"
    
    try:
        if update:
            await update.message.reply_text(text=full_text, reply_markup=reply_markup)
        else:
            await context.bot.send_message(chat_id=chat_id, text=full_text, reply_markup=reply_markup)
        return True
    except Exception as e:
        print(f"Не удалось отправить меню пользователю {chat_id}: {e}")
        return False

async def show_main_menu(update, chat_id, edit=False):
    chat_id = str(chat_id)
    user_state = get_user_state(chat_id)
    user_state["step"] = "main"
    
    if is_user_blocked(chat_id):
        await update.callback_query.edit_message_text(get_text(chat_id, "user_blocked"))
        return
    
    username = "User"
    if chat_id in registered_users:
        username = registered_users[chat_id].get("username", "User")
    
    tariff_info = get_text(chat_id, "tariff_status", tariff=user_state['tariff'].upper() if user_state['tariff'] != 'none' else get_text(chat_id, "none"))
    balance_info = get_text(chat_id, "balance_info", balance=get_balance(chat_id))
    server_info = f"🌍 Server: {user_state['server'].upper() if user_state['server'] != 'none' else 'Tanlanmagan'}"
    
    signals_text = ""
    if user_state['tariff'] != 'none':
        tariff = user_state['tariff']
        limit = SIGNAL_LIMITS.get(tariff, 0)
        used = get_user_signals(chat_id)
        if limit == 999999:
            signals_text = get_text(chat_id, "signals_infinite")
        else:
            signals_text = get_text(chat_id, "signals_info", used=used, limit=limit)
    else:
        signals_text = get_text(chat_id, "no_tariff")
    
    keyboard = []
    keyboard.append([InlineKeyboardButton("🌐 " + get_text(chat_id, "choose_language"), callback_data="change_language")])
    
    if not user_state["registered"]:
        keyboard.append([InlineKeyboardButton(get_text(chat_id, "register"), callback_data="register")])
    else:
        keyboard.append([InlineKeyboardButton(get_text(chat_id, "play"), callback_data="play")])
    
    keyboard.append([InlineKeyboardButton(get_text(chat_id, "tariffs"), callback_data="show_tariffs")])
    keyboard.append([InlineKeyboardButton(get_text(chat_id, "servers"), callback_data="show_servers")])
    keyboard.append([InlineKeyboardButton(get_text(chat_id, "top_up_balance"), callback_data="top_up_balance")])
    keyboard.append([InlineKeyboardButton(get_text(chat_id, "admin"), callback_data="contact_admin")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = get_text(chat_id, "welcome", username=username)
    full_text = f"{welcome_text}\n\n{tariff_info}\n{balance_info}\n{server_info}\n{signals_text}"
    
    if edit:
        try:
            await update.callback_query.edit_message_text(text=full_text, reply_markup=reply_markup)
            return
        except:
            pass
    
    try:
        await update.callback_query.message.reply_text(text=full_text, reply_markup=reply_markup)
    except:
        pass

# ========== КОМАНДЫ АДМИНИСТРАТОРА ==========

async def add_balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        chat_id = str(update.effective_chat.id)
        await update.message.reply_text(get_text(chat_id, "not_admin"))
        return
    try:
        args = context.args
        if len(args) < 2:
            chat_id = str(update.effective_chat.id)
            await update.message.reply_text("❌ Noto'g'ri format!\n\n/addbalance [chat_id] [summa]")
            return
        target_chat_id = str(args[0])
        amount = int(args[1])
        if amount <= 0:
            chat_id = str(update.effective_chat.id)
            await update.message.reply_text("❌ Summa 0 dan katta bo'lishi kerak!")
            return
        add_balance(target_chat_id, amount)
        current_balance = get_balance(target_chat_id)
        chat_id = str(update.effective_chat.id)
        await update.message.reply_text(
            f"✅ Balans to'ldirildi!\n\n"
            f"📱 Foydalanuvchi ID: {target_chat_id}\n"
            f"💰 Qo'shilgan summa: {amount}\n"
            f"💳 Yangi balans: {current_balance}"
        )
        try:
            await context.bot.send_message(
                chat_id=target_chat_id,
                text=f"💰 BALANSINGIZ TO'LDIRILDI!\n\n➕ Qo'shilgan: {amount}\n💳 Yangi balans: {current_balance}",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("💳 TARIFLAR", callback_data="show_tariffs")],
                    [InlineKeyboardButton("🏠 MENYU", callback_data="main_menu")]
                ])
            )
        except:
            pass
    except ValueError:
        chat_id = str(update.effective_chat.id)
        await update.message.reply_text("❌ Summa son bo'lishi kerak!")
    except Exception as e:
        chat_id = str(update.effective_chat.id)
        await update.message.reply_text(f"❌ Xatolik yuz berdi!\n{str(e)}")

async def remove_balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        chat_id = str(update.effective_chat.id)
        await update.message.reply_text(get_text(chat_id, "not_admin"))
        return
    try:
        args = context.args
        if len(args) < 2:
            chat_id = str(update.effective_chat.id)
            await update.message.reply_text("❌ Noto'g'ri format!\n\n/removebalance [chat_id] [summa]")
            return
        target_chat_id = str(args[0])
        amount = int(args[1])
        if amount <= 0:
            chat_id = str(update.effective_chat.id)
            await update.message.reply_text("❌ Summa 0 dan katta bo'lishi kerak!")
            return
        current_balance = get_balance(target_chat_id)
        if current_balance < amount:
            chat_id = str(update.effective_chat.id)
            await update.message.reply_text(f"❌ Foydalanuvchida yetarli mablag' yo'q!\n\n💰 Joriy balans: {current_balance}")
            return
        new_balance = current_balance - amount
        set_balance(target_chat_id, new_balance)
        chat_id = str(update.effective_chat.id)
        await update.message.reply_text(
            f"✅ Balansdan pul yechib olindi!\n\n"
            f"📱 ID: {target_chat_id}\n"
            f"📉 Yechib olingan: {amount}\n"
            f"💳 Yangi balans: {new_balance}"
        )
        try:
            await context.bot.send_message(
                chat_id=target_chat_id,
                text=f"💰 BALANSINGIZDAN PUL YECHIB OLINDI!\n\n📉 Yechib olingan: {amount}\n💳 Yangi balans: {new_balance}",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("👑 ADMINISTRATOR", callback_data="contact_admin")],
                    [InlineKeyboardButton("🏠 MENYU", callback_data="main_menu")]
                ])
            )
        except:
            pass
    except ValueError:
        chat_id = str(update.effective_chat.id)
        await update.message.reply_text("❌ Summa son bo'lishi kerak!")
    except Exception as e:
        chat_id = str(update.effective_chat.id)
        await update.message.reply_text(f"❌ Xatolik yuz berdi!\n{str(e)}")

async def check_balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        chat_id = str(update.effective_chat.id)
        await update.message.reply_text(get_text(chat_id, "not_admin"))
        return
    try:
        args = context.args
        if len(args) < 1:
            chat_id = str(update.effective_chat.id)
            await update.message.reply_text("❌ Noto'g'ri format!\n\n/checkbalance [chat_id]")
            return
        target_chat_id = str(args[0])
        balance = get_balance(target_chat_id)
        chat_id = str(update.effective_chat.id)
        await update.message.reply_text(
            f"💰 BALANS MA'LUMOTI\n\n"
            f"📱 Foydalanuvchi ID: {target_chat_id}\n"
            f"💳 Balans: {balance}"
        )
    except Exception as e:
        chat_id = str(update.effective_chat.id)
        await update.message.reply_text(f"❌ Xatolik yuz berdi!\n{str(e)}")

async def block_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        chat_id = str(update.effective_chat.id)
        await update.message.reply_text(get_text(chat_id, "not_admin"))
        return
    try:
        args = context.args
        if len(args) < 1:
            chat_id = str(update.effective_chat.id)
            await update.message.reply_text("❌ Noto'g'ri format!\n\n/block [chat_id]")
            return
        target_chat_id = str(args[0])
        if target_chat_id not in registered_users:
            chat_id = str(update.effective_chat.id)
            await update.message.reply_text(get_text(chat_id, "block_not_found"))
            return
        if is_user_blocked(target_chat_id):
            chat_id = str(update.effective_chat.id)
            await update.message.reply_text(get_text(chat_id, "block_already"))
            return
        username = registered_users[target_chat_id].get("username", "Unknown")
        block_user(target_chat_id, username)
        chat_id = str(update.effective_chat.id)
        await update.message.reply_text(get_text(chat_id, "block_success", user_id=target_chat_id, username=username, time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        try:
            await context.bot.send_message(chat_id=target_chat_id, text=get_text(target_chat_id, "user_blocked"))
        except:
            pass
    except Exception as e:
        chat_id = str(update.effective_chat.id)
        await update.message.reply_text(f"{get_text(chat_id, 'error')}\n{str(e)}")

async def unblock_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        chat_id = str(update.effective_chat.id)
        await update.message.reply_text(get_text(chat_id, "not_admin"))
        return
    try:
        args = context.args
        if len(args) < 1:
            chat_id = str(update.effective_chat.id)
            await update.message.reply_text("❌ Noto'g'ri format!\n\n/unblock [chat_id]")
            return
        target_chat_id = str(args[0])
        if not is_user_blocked(target_chat_id):
            chat_id = str(update.effective_chat.id)
            await update.message.reply_text(get_text(chat_id, "unblock_not_found"))
            return
        username = blacklist[target_chat_id].get("username", "Unknown")
        unblock_user(target_chat_id)
        chat_id = str(update.effective_chat.id)
        await update.message.reply_text(get_text(chat_id, "unblock_success", user_id=target_chat_id, username=username))
        try:
            await context.bot.send_message(chat_id=target_chat_id, text="✅ Вы были разблокированы администратором!\n\nМожете продолжить пользоваться ботом.")
        except:
            pass
    except Exception as e:
        chat_id = str(update.effective_chat.id)
        await update.message.reply_text(f"{get_text(chat_id, 'error')}\n{str(e)}")

async def blacklist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        chat_id = str(update.effective_chat.id)
        await update.message.reply_text(get_text(chat_id, "not_admin"))
        return
    chat_id = str(update.effective_chat.id)
    blacklist_data = get_blacklist()
    if not blacklist_data:
        await update.message.reply_text(get_text(chat_id, "blacklist_empty"))
        return
    text = get_text(chat_id, "blacklist_title", count=len(blacklist_data)) + "\n\n"
    for user_chat_id, data in blacklist_data.items():
        username = data.get("username", "Unknown")
        blocked_at = data.get("blocked_at", "Unknown")
        text += get_text(chat_id, "blacklist_item", id=user_chat_id, username=username, time=blocked_at) + "─" * 30 + "\n"
    await update.message.reply_text(text)

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        chat_id = str(update.effective_chat.id)
        await update.message.reply_text(get_text(chat_id, "not_admin"))
        return
    chat_id = str(update.effective_chat.id)
    lang_stats = {}
    for user_chat_id, lang in user_languages.items():
        if lang not in lang_stats:
            lang_stats[lang] = 0
        lang_stats[lang] += 1
    stats_text = f"📊 USER STATISTICS\n\n📝 Registered: {len(registered_users)}\n🌐 With language: {len(user_languages)}\n🚫 Blocked: {len(blacklist)}\n❌ No language: {len(registered_users) - len(user_languages)}\n\n📊 BY LANGUAGE:\n"
    for lang_code, count in lang_stats.items():
        lang_name = LANGUAGES.get(lang_code, lang_code)
        stats_text += f"  {lang_name}: {count}\n"
    if not lang_stats:
        stats_text += "  No data\n"
    await update.message.reply_text(stats_text)

async def signals_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    user_state = get_user_state(chat_id)
    tariff = user_state.get("tariff", "none")
    if tariff == "none":
        await update.message.reply_text("❌ У вас нет активного тарифа!\n\nПодключите тариф в разделе 💳 ТАРИФЫ")
        return
    limit = SIGNAL_LIMITS.get(tariff, 0)
    used = get_user_signals(chat_id)
    if limit == 999999:
        remaining_text = "♾️ Безлимит"
        status = "🟢 Активен (безлимит)"
    else:
        remaining = limit - used
        remaining_text = str(remaining)
        status = "🟢 Активен" if used < limit else "🔴 Закончились"
    await update.message.reply_text(get_text(chat_id, "signals_status", tariff=tariff.upper(), used=used, remaining=remaining_text, status=status))

# ========== ФУНКЦИИ ДЛЯ РАССЫЛКИ ==========

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        chat_id = str(update.effective_chat.id)
        await update.message.reply_text(get_text(chat_id, "not_admin"))
        return
    chat_id = str(update.effective_chat.id)
    keyboard = []
    for lang_code, lang_name in LANGUAGES.items():
        keyboard.append([InlineKeyboardButton(lang_name, callback_data=f"broadcast_lang_{lang_code}")])
    keyboard.append([InlineKeyboardButton("❌ " + get_text(chat_id, "broadcast_cancel"), callback_data="broadcast_cancel")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(get_text(chat_id, "broadcast_start"), reply_markup=reply_markup)

async def cancel_broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        chat_id = str(update.effective_chat.id)
        await update.message.reply_text(get_text(chat_id, "not_admin"))
        return
    chat_id = str(update.effective_chat.id)
    if chat_id in broadcast_states:
        del broadcast_states[chat_id]
        await update.message.reply_text(get_text(chat_id, "broadcast_cancel_confirm"))
    else:
        await update.message.reply_text("❌ Активная рассылка не найдена!")

async def handle_broadcast_lang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await query.edit_message_text("❌ Вы не администратор!")
        return
    chat_id = str(update.effective_chat.id)
    lang_code = query.data.replace("broadcast_lang_", "")
    if lang_code == "cancel":
        await query.edit_message_text(get_text(chat_id, "broadcast_cancel"))
        return
    broadcast_states[chat_id] = {"lang": lang_code, "step": "waiting_message"}
    lang_name = LANGUAGES.get(lang_code, lang_code)
    await query.edit_message_text(f"{get_text(chat_id, 'broadcast_lang_selected', lang=lang_name)}\n\n{get_text(chat_id, 'broadcast_instruction')}")

# ========== ИСПРАВЛЕННАЯ ФУНКЦИЯ РАССЫЛКИ (ВСЕ ПОЛЬЗОВАТЕЛИ) ==========
async def handle_broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = str(update.effective_chat.id)
    
    if user_id != ADMIN_ID:
        return
    if chat_id not in broadcast_states:
        await send_main_menu_to_user(context, chat_id, update)
        return
    
    state = broadcast_states[chat_id]
    if state.get("step") != "waiting_message":
        await send_main_menu_to_user(context, chat_id, update)
        return
    
    lang_code = state["lang"]
    
    # ===== СОБИРАЕМ ВСЕХ ПОЛЬЗОВАТЕЛЕЙ ИЗ ВСЕХ ВОЗМОЖНЫХ ИСТОЧНИКОВ =====
    users_to_send = set()
    
    # 1. Все зарегистрированные
    for user_chat_id in registered_users.keys():
        users_to_send.add(user_chat_id)
    
    # 2. Все, у кого есть язык
    for user_chat_id in user_languages.keys():
        users_to_send.add(user_chat_id)
    
    # 3. Все, у кого есть баланс
    for user_chat_id in user_balances.keys():
        users_to_send.add(user_chat_id)
    
    # 4. Все, кто в черном списке
    for user_chat_id in blacklist.keys():
        users_to_send.add(user_chat_id)
    
    # 5. Все, кто есть в user_states
    for user_chat_id in user_states.keys():
        users_to_send.add(user_chat_id)
    
    # 6. ВСЕ, кто есть в файлах сигналов
    try:
        signals_data = load_signals()
        for user_chat_id in signals_data.keys():
            users_to_send.add(user_chat_id)
    except:
        pass
    
    # Если выбран конкретный язык - фильтруем
    if lang_code != "all":
        filtered_users = set()
        for user_chat_id in users_to_send:
            user_lang = user_languages.get(user_chat_id, "")
            if user_lang == lang_code:
                filtered_users.add(user_chat_id)
        users_to_send = filtered_users
    
    users_to_send = list(users_to_send)
    
    if not users_to_send:
        await update.message.reply_text(
            "❌ Нет пользователей для рассылки!\n\n"
            "💡 Чтобы добавить пользователей:\n"
            "1. Попросите кого-то написать боту\n"
            "2. Или добавьте ID вручную через Console"
        )
        del broadcast_states[chat_id]
        await send_main_menu_to_user(context, chat_id, update)
        return
    
    await update.message.reply_text(f"📤 Начинаю рассылку {len(users_to_send)} пользователям...")
    
    sent = 0
    failed = 0
    
    text = update.message.text
    caption = update.message.caption or ""
    video = update.message.video
    photo = update.message.photo[-1] if update.message.photo else None
    document = update.message.document
    
    menu_button = InlineKeyboardButton("🏠 Меню", callback_data="main_menu")
    
    if video:
        for user_chat_id in users_to_send:
            try:
                await context.bot.send_video(
                    chat_id=user_chat_id,
                    video=video.file_id,
                    caption=caption or text or "",
                    reply_markup=InlineKeyboardMarkup([[menu_button]])
                )
                sent += 1
                await asyncio.sleep(0.3)
            except Exception as e:
                failed += 1
                print(f"Не удалось отправить видео пользователю {user_chat_id}: {e}")
    elif photo:
        for user_chat_id in users_to_send:
            try:
                await context.bot.send_photo(
                    chat_id=user_chat_id,
                    photo=photo.file_id,
                    caption=caption or text or "",
                    reply_markup=InlineKeyboardMarkup([[menu_button]])
                )
                sent += 1
                await asyncio.sleep(0.3)
            except Exception as e:
                failed += 1
                print(f"Не удалось отправить фото пользователю {user_chat_id}: {e}")
    elif document:
        for user_chat_id in users_to_send:
            try:
                await context.bot.send_document(
                    chat_id=user_chat_id,
                    document=document.file_id,
                    caption=caption or text or "",
                    reply_markup=InlineKeyboardMarkup([[menu_button]])
                )
                sent += 1
                await asyncio.sleep(0.3)
            except Exception as e:
                failed += 1
                print(f"Не удалось отправить документ пользователю {user_chat_id}: {e}")
    elif text:
        for user_chat_id in users_to_send:
            try:
                await context.bot.send_message(
                    chat_id=user_chat_id,
                    text=text,
                    reply_markup=InlineKeyboardMarkup([[menu_button]])
                )
                sent += 1
                await asyncio.sleep(0.3)
            except Exception as e:
                failed += 1
                print(f"Не удалось отправить сообщение пользователю {user_chat_id}: {e}")
    else:
        await update.message.reply_text("❌ Неподдерживаемый формат сообщения!")
        del broadcast_states[chat_id]
        await send_main_menu_to_user(context, chat_id, update)
        return
    
    await update.message.reply_text(
        f"✅ Реклама отправлена!\n\n"
        f"👥 Получили: {sent}\n"
        f"❌ Ошибок: {failed}\n"
        f"📊 Всего пользователей: {len(users_to_send)}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🏠 " + get_text(chat_id, "main_menu"), callback_data="main_menu")]
        ])
    )
    
    del broadcast_states[chat_id]
    await send_main_menu_to_user(context, chat_id, update)

# ========== ОСТАЛЬНЫЕ ФУНКЦИИ ==========

async def show_language_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = str(update.effective_chat.id)
    keyboard = [
        [InlineKeyboardButton("🇺🇿 O'zbek", callback_data="lang_uz")],
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton("🇹🇯 Тоҷикӣ", callback_data="lang_tg")],
        [InlineKeyboardButton("◀️ " + get_text(chat_id, "back"), callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("🌐 " + get_text(chat_id, "select_language"), reply_markup=reply_markup)

async def change_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = str(update.effective_chat.id)
    lang = query.data.replace("lang_", "")
    if lang in LANGUAGES:
        set_user_language(chat_id, lang)
        await query.edit_message_text("✅ " + get_text(chat_id, "language_selected"), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 " + get_text(chat_id, "main_menu"), callback_data="main_menu")]]))

async def register_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = str(update.effective_chat.id)
    await query.edit_message_text(
        f"{get_text(chat_id, 'not_registered')}\n\n{get_text(chat_id, 'enter_id')}\n\n{get_text(chat_id, 'example_id')}\n\n{get_text(chat_id, 'id_instruction')}",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ " + get_text(chat_id, "back"), callback_data="main_menu")]])
    )
    user_state = get_user_state(chat_id)
    user_state["step"] = "registration"

async def handle_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    user_state = get_user_state(chat_id)
    if user_state["step"] != "registration":
        return
    username = update.effective_user.username or update.effective_user.first_name
    user_input_id = update.message.text.strip()
    if user_input_id and len(user_input_id) > 0:
        registered_users[chat_id] = {"username": username, "chat_id": chat_id, "custom_id": user_input_id, "registered_at": str(update.message.date)}
        save_json_file(USERS_FILE, registered_users)
        user_state["registered"] = True
        user_state["step"] = "main"
        if chat_id not in user_balances:
            set_balance(chat_id, 100)
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(get_text(chat_id, "play"), callback_data="play")],
            [InlineKeyboardButton(get_text(chat_id, "enter_password_btn"), callback_data="enter_password")],
            [InlineKeyboardButton(get_text(chat_id, "tariffs"), callback_data="show_tariffs")],
            [InlineKeyboardButton(get_text(chat_id, "admin"), callback_data="contact_admin")],
            [InlineKeyboardButton("🏠 " + get_text(chat_id, "main_menu"), callback_data="main_menu")]
        ])
        await update.message.reply_text(
            f"{get_text(chat_id, 'registration_success')}\n\n{get_text(chat_id, 'your_id', custom_id=user_input_id)}\n{get_text(chat_id, 'your_name', username=username)}\n{get_text(chat_id, 'initial_balance')}\n\n{get_text(chat_id, 'password_instruction')}\n{get_text(chat_id, 'password_hint', password=GAME_PASSWORD)}",
            reply_markup=keyboard
        )
    else:
        await update.message.reply_text(f"{get_text(chat_id, 'wrong_id')}\n\n{get_text(chat_id, 'enter_valid_id')}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(chat_id, "retry"), callback_data="register")]]))

async def show_servers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = str(update.effective_chat.id)
    keyboard = [
        [InlineKeyboardButton("🇺🇿 " + get_text(chat_id, "server_uz"), callback_data="server_uz")],
        [InlineKeyboardButton("🇷🇺 " + get_text(chat_id, "server_ru"), callback_data="server_ru")],
        [InlineKeyboardButton("🇹🇯 " + get_text(chat_id, "server_tj"), callback_data="server_tj")],
        [InlineKeyboardButton("🇺🇸 " + get_text(chat_id, "server_us"), callback_data="server_us")],
        [InlineKeyboardButton("◀️ " + get_text(chat_id, "back"), callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(get_text(chat_id, "servers_title"), reply_markup=reply_markup)

async def handle_server_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = str(update.effective_chat.id)
    user_state = get_user_state(chat_id)
    server_key = query.data.replace("server_", "")
    server_names = {"uz": get_text(chat_id, "server_uz"), "ru": get_text(chat_id, "server_ru"), "tj": get_text(chat_id, "server_tj"), "us": get_text(chat_id, "server_us")}
    user_state["server"] = server_key
    await query.edit_message_text(get_text(chat_id, "server_selected", server=server_names.get(server_key, server_key)), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 " + get_text(chat_id, "main_menu"), callback_data="main_menu")]]))

# ========== ФУНКЦИЯ TOP UP BALANCE ==========
async def top_up_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки пополнения баланса"""
    query = update.callback_query
    await query.answer()
    chat_id = str(update.effective_chat.id)
    
    text = f"""{get_text(chat_id, "top_up_info")}

👤 Администратор: @Codex_etoya

📌 Ваш ID: {chat_id}
💰 Текущий баланс: {get_balance(chat_id)} сӯм

📩 Нажмите на кнопку ниже, чтобы написать администратору:"""
    
    keyboard = [
        [InlineKeyboardButton("📩 " + get_text(chat_id, "write_admin"), url=f"tg://user?id={ADMIN_ID}")],
        [InlineKeyboardButton("◀️ " + get_text(chat_id, "back"), callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text=text, reply_markup=reply_markup)

# ========== ФУНКЦИЯ SHOW_TARIFFS ==========
async def show_tariffs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = str(update.effective_chat.id)
    user_state = get_user_state(chat_id)
    balance = get_balance(chat_id)
    tariff_name = user_state['tariff'].upper() if user_state['tariff'] != 'none' else get_text(chat_id, "none")
    
    lang = get_user_language(chat_id)
    
    tariff_descriptions = {
        "tg": {
            "light": """🟢 Боти «Light»
300 сомонӣ дар моҳ
✅ Дақиқӣ: 75–80%
✅ То 50 сигнал дар рӯз
✅ Танҳо: «chicken road»
❌ Бе дастгирии техникӣ
❌ Бе филтри коэффициентҳо""",
            "pro": """🟡 Боти «Pro»
500 сомонӣ дар моҳ
✅ Дақиқӣ: 85–90%
✅ То 150 сигнал дар рӯз
✅ Танҳо: «chicken road» ва «минаҳо» (Mines)
✅ Филтри коэффициентҳо (аз 1.5 то 3.0)
✅ Дастгирии техникии аввалиятнок 12/7
🎁 Бонус: рӯйхати аввалини идоракунии банкролл ройгон""",
            "ultra": """🔴 Боти «Ultra»
1000 сомонӣ дар моҳ
✅ Танҳо: «chicken road» ва «минаҳо»
✅ Дақиқӣ: 90–99%
✅ Миқдори сигналҳо маҳдуд нест
✅ AI-таҳлил + сигналҳои зинда
✅ Вориди автоматикии купони ставка
✅ Менеҷери шахсӣ
✅ Таҳлили амиқи сигналҳои бохта
🎁 Бонусҳо:
— 30% тахфиф ба обунаи солона
— Канали махфии Telegram бо пешгӯиҳои топ-капперҳо

👇 Секретный канал 
https://t.me/+nb_yAPpN3zI2ZTQy"""
        },
        "uz": {
            "light": """🟢 Light Bot
350 000 so'm / oy
✅ Aniqlik: 75–80%
✅ Kuniga 50 tagacha signal
✅ Faqat: «chicken road»
❌ Texnik yordam yo'q
❌ Koeffitsient filtri yo'q""",
            "pro": """🟡 Pro Bot
500 000 so'm / oy
✅ Aniqlik: 85–90%
✅ Kuniga 150 tagacha signal
✅ Faqat: «chicken road» va «mines»
✅ Koeffitsient filtri (1.5 dan 3.0 gacha)
✅ 12/7 ustuvor texnik yordam
🎁 Bonus: bepul bankroll boshqaruvi ro'yxati""",
            "ultra": """🔴 Ultra Bot
1 000 000 so'm / oy
✅ «chicken road» va «mines»
✅ Aniqlik: 90–99%
✅ Cheksiz signallar
✅ AI-tahlil + jonli signallar
✅ Avtomatik tikish kuponlari
✅ Shaxsiy menejer
✅ Yo'qotilgan signallarni chuqur tahlil qilish
🎁 Bonuslar:
— Yillik obunaga 30% chegirma
— Top-kapperlar bashoratlari bilan maxsus Telegram kanali

👇 Maxfiy kanal
https://t.me/+nb_yAPpN3zI2ZTQy"""
        },
        "ru": {
            "light": """🟢 Light Bot
30$ / месяц
✅ Точность: 75–80%
✅ До 50 сигналов в день
✅ Только: «chicken road»
❌ Без техподдержки
❌ Без фильтра коэффициентов""",
            "pro": """🟡 Pro Bot
50$ / месяц
✅ Точность: 85–90%
✅ До 150 сигналов в день
✅ «chicken road» и «мины» (Mines)
✅ Фильтр коэффициентов (от 1.5 до 3.0)
✅ Приоритетная техподдержка 12/7
🎁 Бонус: список управления банкроллом бесплатно""",
            "ultra": """🔴 Ultra Bot
100$ / месяц
✅ «chicken road» и «мины»
✅ Точность: 90–99%
✅ Неограниченное количество сигналов
✅ AI-анализ + живые сигналы
✅ Автоматический ввод купонов ставок
✅ Персональный менеджер
✅ Глубокий анализ проигранных сигналов
🎁 Бонусы:
— 30% скидка на годовую подписку
— Закрытый Telegram-канал с прогнозами топ-капперов

👇 Секретный канал
https://t.me/+nb_yAPpN3zI2ZTQy"""
        },
        "en": {
            "light": """🟢 Light Bot
30$ / month
✅ Accuracy: 75–80%
✅ Up to 50 signals per day
✅ Only: «chicken road»
❌ No technical support
❌ No coefficient filter""",
            "pro": """🟡 Pro Bot
50$ / month
✅ Accuracy: 85–90%
✅ Up to 150 signals per day
✅ «chicken road» and «mines»
✅ Coefficient filter (from 1.5 to 3.0)
✅ Priority technical support 12/7
🎁 Bonus: free bankroll management list""",
            "ultra": """🔴 Ultra Bot
100$ / month
✅ «chicken road» and «mines»
✅ Accuracy: 90–99%
✅ Unlimited signals
✅ AI-analysis + live signals
✅ Automatic bet coupons input
✅ Personal manager
✅ Deep analysis of lost signals
🎁 Bonuses:
— 30% discount on annual subscription
— Private Telegram channel with top-capper predictions

👇 Secret channel
https://t.me/+nb_yAPpN3zI2ZTQy"""
        }
    }
    
    descriptions = tariff_descriptions.get(lang, tariff_descriptions["ru"])
    
    light_desc = descriptions.get("light", "")
    pro_desc = descriptions.get("pro", "")
    ultra_desc = descriptions.get("ultra", "")
    
    text = f"""💳 ТАРИФҲО

💰 Баланси Шумо: {balance} сӯм
📊 Тарифи ҷорӣ: {tariff_name}

{light_desc}

{pro_desc}

{ultra_desc}

Тарифро интихоб кунед:"""
    
    light_price = get_tariff_price_text(chat_id, "light")
    pro_price = get_tariff_price_text(chat_id, "pro")
    ultra_price = get_tariff_price_text(chat_id, "ultra")
    
    keyboard = [
        [InlineKeyboardButton(f"🟢 LIGHT BOT - {light_price}", callback_data="tariff_light")],
        [InlineKeyboardButton(f"🟡 PRO BOT - {pro_price}", callback_data="tariff_pro")],
        [InlineKeyboardButton(f"🔴 ULTRA BOT - {ultra_price}", callback_data="tariff_ultra")],
        [InlineKeyboardButton("🌐 " + get_text(chat_id, "choose_language"), callback_data="change_language")],
        [InlineKeyboardButton("◀️ " + get_text(chat_id, "back"), callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text=text, reply_markup=reply_markup)

async def handle_tariff_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = str(update.effective_chat.id)
    user_state = get_user_state(chat_id)
    tariff_key = query.data.replace("tariff_", "")
    tariff_info = TARIFFS.get(tariff_key)
    if not tariff_info:
        return
    balance = get_balance(chat_id)
    price = get_tariff_price(chat_id, tariff_key)
    currency = get_text(chat_id, "currency")
    if balance < price:
        await query.edit_message_text(
            f"{get_text(chat_id, 'no_balance')}\n\n{get_text(chat_id, 'tariff_price', price=f'{price} {currency}')}\n{get_text(chat_id, 'need_more', need=price-balance)}\n\n{get_text(chat_id, 'contact_admin_balance')}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(chat_id, "admin"), callback_data="contact_admin")], [InlineKeyboardButton("◀️ " + get_text(chat_id, "back"), callback_data="show_tariffs")]])
        )
        return
    set_balance(chat_id, balance - price)
    user_state["tariff"] = tariff_key
    user_state["has_access"] = True
    await query.edit_message_text(
        f"{get_text(chat_id, 'tariff_selected')}\n\n{get_text(chat_id, 'tariff', tariff=tariff_info['name'])}\n{get_text(chat_id, 'tariff_price', price=f'{price} {currency}')}\n{get_text(chat_id, 'new_balance', balance=get_balance(chat_id))}\n\n🐔 {get_text(chat_id, 'play')}",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(chat_id, "play"), callback_data="play")], [InlineKeyboardButton("🏠 " + get_text(chat_id, "main_menu"), callback_data="main_menu")]])
    )

async def play_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = str(update.effective_chat.id)
    user_state = get_user_state(chat_id)
    
    if not user_state["registered"]:
        await query.edit_message_text(get_text(chat_id, "must_register"))
        return
    
    tariff = user_state.get("tariff", "none")
    if tariff == "none":
        await query.edit_message_text(
            f"❌ {get_text(chat_id, 'no_access')}\n\n"
            f"⚠️ {get_text(chat_id, 'need_tariff')}\n\n"
            f"{get_text(chat_id, 'need_tariff_desc')}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(get_text(chat_id, "tariffs"), callback_data="show_tariffs")],
                [InlineKeyboardButton(get_text(chat_id, "enter_password_btn"), callback_data="enter_password")],
                [InlineKeyboardButton("🏠 " + get_text(chat_id, "main_menu"), callback_data="main_menu")]
            ])
        )
        return
    
    reset_user_cycle(chat_id)
    
    # Получаем настройки для тарифа
    tariff_config = TARIFF_IMAGES.get(tariff, TARIFF_IMAGES["light"])
    images_dir = tariff_config["dir"]
    images_list = tariff_config["images"]
    
    # Выбираем РАНДОМНУЮ фотографию
    random_index = random.randint(0, len(images_list) - 1)
    photo_path = images_dir / images_list[random_index]
    
    if photo_path.exists():
        await send_photo_with_buttons(context, chat_id, photo_path, get_text(chat_id, "game_start"))
        try:
            await query.delete_message()
        except:
            pass
    else:
        await context.bot.send_message(chat_id, get_text(chat_id, "photo_error", filename=photo_path.name))

async def enter_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = str(update.effective_chat.id)
    await query.edit_message_text(get_text(chat_id, "enter_password_prompt"), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(chat_id, "admin"), callback_data="contact_admin")], [InlineKeyboardButton("◀️ " + get_text(chat_id, "back"), callback_data="main_menu")]]))
    user_state = get_user_state(chat_id)
    user_state["step"] = "password"

async def handle_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    user_state = get_user_state(chat_id)
    if user_state["step"] != "password":
        return
    password = update.message.text.strip()
    if password == GAME_PASSWORD:
        user_state["has_access"] = True
        user_state["step"] = "main"
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(get_text(chat_id, "play"), callback_data="play")], [InlineKeyboardButton(get_text(chat_id, "tariffs"), callback_data="show_tariffs")], [InlineKeyboardButton(get_text(chat_id, "admin"), callback_data="contact_admin")], [InlineKeyboardButton("🏠 " + get_text(chat_id, "main_menu"), callback_data="main_menu")]])
        await update.message.reply_text(f"{get_text(chat_id, 'password_correct')}\n\n{get_text(chat_id, 'access_granted')}", reply_markup=keyboard)
        return
    await update.message.reply_text(f"{get_text(chat_id, 'wrong_password')}\n\n{get_text(chat_id, 'retry_password')}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(chat_id, "retry_password"), callback_data="enter_password")]]))

async def contact_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = str(update.effective_chat.id)
    user_id = update.effective_user.id
    custom_id = "Не зарегистрирован"
    if chat_id in registered_users:
        custom_id = registered_users[chat_id].get("custom_id", user_id)
    text = get_text(chat_id, "admin_contact", custom_id=custom_id, user_id=user_id)
    keyboard = [[InlineKeyboardButton(get_text(chat_id, "write_admin"), url=f"tg://user?id={ADMIN_ID}")], [InlineKeyboardButton("◀️ " + get_text(chat_id, "back"), callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=text, reply_markup=reply_markup)

async def send_photo_with_buttons(context, chat_id, photo_path, caption=""):
    keyboard = [
        [InlineKeyboardButton("🎮 " + get_text(chat_id, "game_continue"), callback_data="next")],
        [InlineKeyboardButton("👑 " + get_text(chat_id, "admin"), callback_data="contact_admin")],
        [InlineKeyboardButton("🏠 " + get_text(chat_id, "main_menu"), callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    with open(photo_path, 'rb') as f:
        await context.bot.send_photo(chat_id=chat_id, photo=InputFile(f), caption=caption, reply_markup=reply_markup)

async def catch_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    user_state = get_user_state(chat_id)
    
    # ===== АВТОМАТИЧЕСКОЕ ДОБАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯ =====
    if chat_id not in registered_users:
        username = update.effective_user.username or update.effective_user.first_name or "User"
        registered_users[chat_id] = {
            "username": username,
            "chat_id": chat_id,
            "custom_id": str(chat_id),
            "registered_at": str(datetime.now())
        }
        save_json_file(USERS_FILE, registered_users)
        print(f"✅ Новый пользователь добавлен: {chat_id} ({username})")
    
    if chat_id not in user_states:
        user_states[chat_id] = {
            "current_index": 0,
            "special_triggered": False,
            "has_access": False,
            "registered": True,
            "step": "main",
            "tariff": "none",
            "server": "none"
        }
    
    if update.effective_user.id == ADMIN_ID and chat_id in broadcast_states:
        if broadcast_states[chat_id].get("step") == "waiting_message":
            await handle_broadcast_message(update, context)
            return
    
    if user_state["step"] == "registration":
        await handle_registration(update, context)
        return
    if user_state["step"] == "password":
        await handle_password(update, context)
        return
    
    if chat_id not in user_languages:
        keyboard = [
            [InlineKeyboardButton("🇺🇿 O'zbek", callback_data="lang_uz")],
            [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")],
            [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
            [InlineKeyboardButton("🇹🇯 Тоҷикӣ", callback_data="lang_tg")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "🌐 TILNI TANLANG / ВЫБЕРИТЕ ЯЗЫК / CHOOSE LANGUAGE / ЗАБОНРО ИНТИХОБ КУНЕД",
            reply_markup=reply_markup
        )
        return
    
    await send_main_menu_to_user(context, chat_id, update)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = str(update.effective_chat.id)
    user_state = get_user_state(chat_id)
    data = query.data
    
    if data.startswith("broadcast_lang_"):
        await handle_broadcast_lang(update, context)
        return
    if data == "main_menu":
        await show_main_menu(update, chat_id, edit=True)
        return
    if data == "change_language":
        await show_language_selection(update, context)
        return
    if data.startswith("lang_"):
        await change_language(update, context)
        return
    if data == "register":
        await register_user(update, context)
        return
    if data == "play":
        await play_game(update, context)
        return
    if data == "enter_password":
        await enter_password(update, context)
        return
    if data == "contact_admin":
        await contact_admin(update, context)
        return
    if data == "top_up_balance":
        await top_up_balance(update, context)
        return
    if data == "reset":
        await show_main_menu(update, chat_id, get_text(chat_id, "game_reset"), edit=True)
        return
    if data == "show_tariffs":
        await show_tariffs(update, context)
        return
    if data == "show_servers":
        await show_servers(update, context)
        return
    if data.startswith("server_"):
        await handle_server_selection(update, context)
        return
    if data.startswith("tariff_"):
        await handle_tariff_selection(update, context)
        return
    if data == "next":
        if not user_state["has_access"]:
            await query.edit_message_text(get_text(chat_id, "no_access"))
            return
        can_use, error_key = can_use_signal(chat_id)
        if not can_use:
            tariff = user_state.get("tariff", "none")
            limit = SIGNAL_LIMITS.get(tariff, 0)
            used = get_user_signals(chat_id)
            message = get_text(chat_id, "signals_limit_reached", used=used, limit=limit, tariff=tariff.upper())
            keyboard = [[InlineKeyboardButton("📊 Мой тариф", callback_data="show_tariffs")], [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            try:
                await query.edit_message_text(text=message, reply_markup=reply_markup)
            except:
                await query.message.reply_text(text=message, reply_markup=reply_markup)
            return
        used = increment_user_signals(chat_id)
        tariff = user_state.get("tariff", "none")
        limit = SIGNAL_LIMITS.get(tariff, 0)
        if limit != 999999:
            remaining = limit - used
            signals_info = f"\n\n📊 Сигнал {used}/{limit} (осталось {remaining})"
        else:
            signals_info = f"\n\n📊 Сигнал {used}/∞ (безлимит)"
        
        # Получаем настройки для текущего тарифа
        tariff_config = TARIFF_IMAGES.get(tariff, TARIFF_IMAGES["light"])
        images_dir = tariff_config["dir"]
        images_list = tariff_config["images"]
        special_chance = tariff_config["special_chance"]
        
        will_be_special = (not user_state["special_triggered"]) and random.random() < special_chance
        
        if will_be_special:
            photo_path = IMAGES_DIR / SPECIAL_IMAGE
            user_state["special_triggered"] = True
            caption = f"{get_text(chat_id, 'game_over')}{signals_info}"
            await send_photo_with_buttons(context, chat_id, photo_path, caption)
            reset_user_cycle(chat_id)
        else:
            # ВЫБИРАЕМ РАНДОМНУЮ фотографию
            random_index = random.randint(0, len(images_list) - 1)
            photo_name = images_list[random_index]
            photo_path = images_dir / photo_name
            caption = f"{get_text(chat_id, 'good_luck')}{signals_info}"
            await send_photo_with_buttons(context, chat_id, photo_path, caption)
        try:
            await query.delete_message()
        except:
            pass
        return
    try:
        await query.edit_message_text(get_text(chat_id, "old_button"), reply_markup=None)
    except:
        pass
    await asyncio.sleep(1)
    await send_main_menu_to_user(context, chat_id, update)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await catch_all(update, context)

# ========== MAIN ==========

def main():
    IMAGES_DIR.mkdir(exist_ok=True)
    IMAGES_DIR_LIGHT.mkdir(exist_ok=True)
    
    # Проверяем файлы в images
    all_images = NORMAL_IMAGES + [SPECIAL_IMAGE]
    missing = [img for img in all_images if not (IMAGES_DIR / img).exists()]
    if missing:
        print(f"⚠️ Yo'qolgan fayllar (images): {', '.join(missing)}")
        print(f"📁 Fayllarni shu papkaga joylang: {IMAGES_DIR.absolute()}")
    else:
        print("✅ Barcha fayllar topildi! (images)")
    
    # Проверяем файлы в images2
    light_images = TARIFF_IMAGES["light"]["images"]
    missing_light = [img for img in light_images if not (IMAGES_DIR_LIGHT / img).exists()]
    if missing_light:
        print(f"⚠️ Yo'qolgan fayllar (images2): {', '.join(missing_light)}")
        print(f"📁 Fayllarni shu papkaga joylang: {IMAGES_DIR_LIGHT.absolute()}")
    else:
        print("✅ Barcha fayllar topildi! (images2)")
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Команды администратора
    application.add_handler(CommandHandler("addbalance", add_balance_command))
    application.add_handler(CommandHandler("removebalance", remove_balance_command))
    application.add_handler(CommandHandler("checkbalance", check_balance_command))
    application.add_handler(CommandHandler("block", block_command))
    application.add_handler(CommandHandler("unblock", unblock_command))
    application.add_handler(CommandHandler("blacklist", blacklist_command))
    application.add_handler(CommandHandler("broadcast", broadcast_command))
    application.add_handler(CommandHandler("cancel_broadcast", cancel_broadcast_command))
    application.add_handler(CommandHandler("stats", stats_command))
    
    # Команда для проверки сигналов
    application.add_handler(CommandHandler("signals", signals_command))
    
    # Основные обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, catch_all))
    application.add_handler(MessageHandler(filters.PHOTO, handle_broadcast_message))
    application.add_handler(MessageHandler(filters.VIDEO, handle_broadcast_message))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_broadcast_message))
    
    print("=" * 50)
    print("🤖 CHICKEN ROAD BOT")
    print("=" * 50)
    print(f"🔑 Parol: {GAME_PASSWORD}")
    print(f"👑 Admin ID: {ADMIN_ID}")
    print("\n💳 Команды администратора:")
    print("   /addbalance [id] [summa] - Пополнить баланс")
    print("   /removebalance [id] [summa] - Уменьшить баланс")
    print("   /checkbalance [id] - Проверить баланс")
    print("   /block [id] - Заблокировать пользователя")
    print("   /unblock [id] - Разблокировать пользователя")
    print("   /blacklist - Список заблокированных")
    print("   /broadcast - Запустить рекламную рассылку")
    print("   /cancel_broadcast - Отменить рассылку")
    print("   /stats - Статистика")
    print("\n📊 Команды пользователя:")
    print("   /signals - Проверить остаток сигналов")
    print("\n📢 Особенности:")
    print("   ✅ Автоматическое меню при любом сообщении")
    print("   ✅ Работают все кнопки (даже старые)")
    print("   ✅ Не нужно писать /start")
    print("   ✅ Поддержка всех языков")
    print("   ✅ Реклама доходит до всех пользователей")
    print("   ✅ Система подсчета сигналов по тарифам")
    print("   ✅ Уведомление об окончании сигналов")
    print("   ✅ Блокировка пользователей")
    print("=" * 50)
    
    application.run_polling()

if __name__ == "__main__":
    main()
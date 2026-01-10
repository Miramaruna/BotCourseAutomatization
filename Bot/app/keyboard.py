from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from config import COURSES_CONFIG

# Главное меню
button_start = [
    # [KeyboardButton(text="/start")],
    [KeyboardButton(text="/buy")],
    [KeyboardButton(text="⚙️ Админка")]
]

keyboard_start = ReplyKeyboardMarkup(
    keyboard=button_start,
    resize_keyboard=True
)

# Клавиатура выбора курсов (динамическая из конфига)
# def get_buy_keyboard(user_data=None):
#     buttons = []
#     mapping = {"course_1": 3, "course_2": 4, "course_3": 5}  # Индексы в user_data
#     for key, data in COURSES_CONFIG.items():
#         # Если юзера нет в базе, значит ничего не куплено
#         is_bought = user_data[mapping[key]] if user_data else False
#         # Важно: callback_data должен начинаться с "buy_", как в handlers
#         buttons.append([InlineKeyboardButton(text=data["name"], callback_data=f"buy_{key}")])
#     return InlineKeyboardMarkup(inline_keyboard=buttons)

def keyboard_decision(user_id: int, course_key: str):
    buttons = [
        [InlineKeyboardButton(text="✅ Одобрить", callback_data=f"accept-{user_id}-{course_key}")],
        [InlineKeyboardButton(text="❌ Отклонить", callback_data=f"decline-{user_id}-{course_key}")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Кнопка в админ-панели
# keyboard_admin = InlineKeyboardMarkup(inline_keyboard=[
#     [InlineKeyboardButton(text="📊 Выгрузить Excel", callback_data="export_excel")]
# ])

keyboard_admin = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats"),
        InlineKeyboardButton(text="📥 Excel Отчет", callback_data="export_excel")
    ],
    [
        InlineKeyboardButton(text="🎁 Выдать курс", callback_data="admin_give_course"),
        InlineKeyboardButton(text="📢 Проверка подписок", callback_data="check_membership")
    ]
])

# В файле keyboard.py
def get_buy_keyboard(user_data):
    """
    user_data — это кортеж из БД (результат chek_user)
    Индексы: course_1 (3), course_2 (4), course_3 (5)
    """
    buttons = []
    
    # Сопоставляем ключи конфига с индексами в БД
    mapping = {"course_1": 3, "course_2": 4, "course_3": 5}
    
    for key, data in COURSES_CONFIG.items():
        is_bought = user_data[mapping[key]] if user_data else False
        
        status_tag = "✅ Куплено" if is_bought else f"💳 {data['price']}"
        button_text = f"{data['name']} | {status_tag}"
        
        # Если куплено, можно либо отключить кнопку, либо оставить для инфо
        callback_data = "already_owned" if is_bought else f"buy_{key}"
        
        buttons.append([InlineKeyboardButton(text=button_text, callback_data=callback_data)])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)
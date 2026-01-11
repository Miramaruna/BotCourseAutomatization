from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from config import COURSES_CONFIG
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Главное меню
start_kb_user = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="/buy")],
        # [KeyboardButton(text="⚙️ Админка")]
    ],
    resize_keyboard=True
)

start_kb_admin = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="/buy")],
        [KeyboardButton(text="⚙️ Админка")]
    ],
    resize_keyboard=True
)

async def get_buy_keyboard_dynamic(user_data):
    from app.database.requests import get_active_courses
    courses = await get_active_courses()
    builder = InlineKeyboardBuilder()
    
    # Маппинг колонок из таблицы users (индексы: course_1=3, course_2=4, course_3=5)
    mapping = {"course_1": 3, "course_2": 4, "course_3": 5}
    
    for c_id, name, price, ch_id, is_active in courses:
        is_bought = user_data[mapping[c_id]] if user_data and c_id in mapping else False
        
        btn_text = f"{name} | ✅ Куплено" if is_bought else f"{name} | 💳 {price} сом"
        cb_data = "already_owned" if is_bought else f"buy_{c_id}"
        
        builder.row(InlineKeyboardButton(text=btn_text, callback_data=cb_data))
    
    return builder.as_markup()
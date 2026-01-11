from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

admin_panel_kb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats"),
        InlineKeyboardButton(text="📥 Excel Отчет", callback_data="export_excel")
    ],
    [
        InlineKeyboardButton(text="🎁 Выдать курс", callback_data="admin_give_course"),
        InlineKeyboardButton(text="📢 Проверка подписок", callback_data="check_membership"),
    ],
    [
        InlineKeyboardButton(text="📚 Управление курсами", callback_data="manage_courses")
    ]
])

def decision_kb(user_id: int, course_key: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Одобрить", callback_data=f"accept-{user_id}-{course_key}")],
        [InlineKeyboardButton(text="❌ Отклонить", callback_data=f"decline-{user_id}-{course_key}")]
    ])

stats_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔄 Обновить", callback_data="admin_stats")],
    [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_admin")]
])

def courses_edit_kb(courses):
    builder = InlineKeyboardBuilder()
    for c_id, name, price, ch_id in courses:
        builder.row(InlineKeyboardButton(text=f"⚙️ {name} ({price} сом)", callback_data=f"edit_c_{c_id}"))
    builder.row(InlineKeyboardButton(text="➕ Добавить курс", callback_data="add_course"))
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_admin"))
    return builder.as_markup()

def course_actions_kb(course_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Переименовать", callback_data=f"rename_{course_id}")],
        [InlineKeyboardButton(text="💰 Изменить цену", callback_data=f"reprice_{course_id}")],
        [InlineKeyboardButton(text="🆔 Изменить ID канала", callback_data=f"rechannel_{course_id}")],
        [InlineKeyboardButton(text="🗑 Удалить курс", callback_data=f"confirm_del_{course_id}")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="manage_courses")]
    ])
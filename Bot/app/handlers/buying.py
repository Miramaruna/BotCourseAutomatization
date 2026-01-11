import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import COURSES_CONFIG, ADMIN_IDS
from app.database.requests import chek_user, purchase_course
from app.keyboards.user_kb import get_buy_keyboard_dynamic
from app.keyboards.admin_kb import decision_kb

router = Router()
logger = logging.getLogger('bot_actions')
photo_file = FSInputFile("Assets/payment.jpg")

class BuyCourse(StatesGroup):
    waiting_for_course_image = State()
    course = State()

@router.message(Command("buy"))
async def cmd_buy(message: Message, state: FSMContext):
    user = await chek_user(message.from_user.id)
    # Если юзера нет в базе (странный кейс, но возможен), редирект на старт или ошибка
    if not user:
        await message.answer("⚠️ Пожалуйста, введите /start для регистрации.")
        return
    
    keyboard = await get_buy_keyboard_dynamic(user)

    await message.answer(
        "🛒 **Выберите курс для покупки:**\nВаши курсы отмечены галочкой ✅",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "already_owned")
async def owned_info(callback: CallbackQuery):
    await callback.answer("🌟 Этот курс уже доступен вам!", show_alert=True)

@router.callback_query(F.data.startswith("buy_"))
async def start_purchase(callback: CallbackQuery, state: FSMContext):
    course_key = callback.data.replace("buy_", "")
    course_data = COURSES_CONFIG.get(course_key)
    
    await callback.message.answer_photo(
        photo=photo_file,
        caption=f"📍 Курс: **{course_data['name']}**\n💰 Цена: **{course_data['price']}**\n\nОтправьте скриншот оплаты.",
        parse_mode="Markdown"
    )
    await state.set_state(BuyCourse.waiting_for_course_image)
    await state.update_data(course=course_key)
    await callback.answer()

@router.message(BuyCourse.waiting_for_course_image, F.photo)
async def process_receipt(message: Message, state: FSMContext):
    data = await state.get_data()
    course_key = data.get('course')
    course_name = COURSES_CONFIG[course_key]['name']
    
    logger.info(f"RECEIPT: User {message.from_user.id} uploaded for '{course_name}'")
    await message.answer("📥 Скриншот получен. Ждите одобрения!")
    
    # Сохранение фото
    file_id = message.photo[-1].file_id
    file_path = f"payments/{message.from_user.id}_{course_key}.jpg"
    await message.bot.download(file=file_id, destination=file_path)
    
    # Рассылка админам
    admin_photo = FSInputFile(file_path)
    for admin_id in ADMIN_IDS:
        try:
            await message.bot.send_photo(
                chat_id=admin_id,
                photo=admin_photo,
                caption=f"🔔 **Новая заявка!**\n👤 Юзер: @{message.from_user.username}\n🆔 ID: {message.from_user.id}\n📚 Курс: {course_name}",
                reply_markup=decision_kb(message.from_user.id, course_key),
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Failed sending to admin {admin_id}: {e}")
    
    await state.clear()

# --- ОБРАБОТКА РЕШЕНИЯ АДМИНА ---

@router.callback_query(F.data.startswith("accept-"))
async def accept_payment(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS: return

    _, user_id, course_key = callback.data.split("-")
    user_id = int(user_id)
    course_data = COURSES_CONFIG.get(course_key)
    
    # Парсим цену (удаляем всё кроме цифр)
    price_int = int(''.join(filter(str.isdigit, course_data['price'])))
    
    await purchase_course(user_id, course_key, price_int)
    logger.info(f"APPROVED: Admin {callback.from_user.username} -> User {user_id} -> {course_key}")

    # Создание ссылки
    invite_text = ""
    if course_data.get("channel_id"):
        try:
            link = await callback.bot.create_chat_invite_link(course_data["channel_id"], member_limit=1)
            invite_text = f"\n\n🔗 Ссылка: {link.invite_link}"
        except Exception:
            invite_text = "\n\n⚠️ Ссылка не создана, свяжитесь с админом."

    await callback.bot.send_message(
        chat_id=user_id, 
        text=f"✅ Покупка {course_data['name']} одобрена!{invite_text}",
        parse_mode="HTML"
    )
    await callback.message.edit_caption(
        caption=callback.message.caption + f"\n\n🟢 Одобрено админом @{callback.from_user.username}",
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("decline-"))
async def decline_payment(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS: return

    _, user_id, course_key = callback.data.split("-")
    user_id = int(user_id)
    
    logger.info(f"DECLINED: Admin {callback.from_user.username} -> User {user_id}")
    
    await callback.bot.send_message(user_id, "❌ Ваша оплата отклонена.")
    await callback.message.edit_caption(
        caption=callback.message.caption + f"\n\n🔴 Отклонено админом @{callback.from_user.username}"
    )
    await callback.answer()
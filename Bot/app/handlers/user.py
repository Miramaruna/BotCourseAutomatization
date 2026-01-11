import logging
from aiogram import Router, F
from aiogram.types import Message, ChatJoinRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ChatMemberUpdated

from config import COURSES_CONFIG, ADMIN_IDS
from app.database.requests import chek_user, add_user, update_user_name
from app.keyboards.user_kb import start_kb_user, start_kb_admin, get_buy_keyboard_dynamic

router = Router()
logger = logging.getLogger('bot_actions')
chats_registry = set()

class Registration(StatesGroup):
    waiting_for_name = State()

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    user = await chek_user(message.from_user.id)
    if not user:
        await add_user(message.from_user.id, message.from_user.username, message.chat.id)
        await message.answer("👋 Здравствуйте! Пожалуйста, введите вашу **Фамилию и Имя**:", parse_mode="Markdown")
        await state.set_state(Registration.waiting_for_name)
    else:
        name = user[2] if user[2] else 'друг'
        if message.from_user.id in ADMIN_IDS:
            await message.answer(f"С возвращением, {name}!", reply_markup=start_kb_admin)
        else:
            await message.answer(f"С возвращением, {name}!", reply_markup=start_kb_user)

@router.message(Registration.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    logger.info(f"REGISTRATION: User {message.from_user.id} set name to '{message.text}'")
    await update_user_name(message.from_user.id, message.text)
    await state.clear()
    if message.from_user.id in ADMIN_IDS:
        await message.answer(f"Приятно познакомиться, {message.text}! Теперь вам доступно меню.", reply_markup=start_kb_admin)
    else:
        await message.answer(f"Приятно познакомиться, {message.text}! Теперь вам доступно меню.", reply_markup=start_kb_user)

@router.chat_join_request()
async def handle_join_request(update: ChatJoinRequest):
    user_id = update.from_user.id
    chat_id = update.chat.id
    
    target_course_key = None
    for key, data in COURSES_CONFIG.items():
        if data.get("channel_id") == chat_id:
            target_course_key = key
            break

    if not target_course_key:
        return

    user = await chek_user(user_id)
    mapping = {"course_1": 3, "course_2": 4, "course_3": 5}
    
    is_bought = False
    if user:
        is_bought = bool(user[mapping[target_course_key]])
        if user_id in ADMIN_IDS:
            is_bought = True 

    if is_bought:
        await update.approve()
        logger.info(f"JOIN APPROVED: User {user_id} joined '{COURSES_CONFIG[target_course_key]['name']}'")
        await update.bot.send_message(user_id, f"✅ Ваша заявка в группу **{update.chat.title}** одобрена автоматически!")
    else:
        logger.warning(f"JOIN DENIED: User {user_id} -> '{COURSES_CONFIG[target_course_key]['name']}' (No payment)")
        await update.decline()
        await update.bot.send_message(
            user_id, 
            f"❌ Доступ в группу **{update.chat.title}** ограничен.\nСначала необходимо приобрести курс.",
            reply_markup=get_buy_keyboard_dynamic(user)
        )
        
@router.message(Command("chat_id"))
async def cmd_chat_id(message: Message):
    await message.answer(f"Ваш chat_id: {message.chat.id}")
    
# Отслеживаем, в какие группы добавлен бот
@router.my_chat_member()
async def on_my_chat_member(update: ChatMemberUpdated):
    chat_id = update.chat.id
    if update.new_chat_member.status in ["member", "administrator"]:
        chats_registry.add(chat_id)
    elif update.new_chat_member.status in ["left", "kicked"]:
        chats_registry.discard(chat_id)

# Команда для запуска проверки
@router.message(Command("check"))
async def check_user_in_groups(message: Message):
    user_id = message.from_user.id
    user_name = message.from_user.full_name
    
    print(f"\n--- Проверка пользователя: {user_name} (ID: {user_id}) ---")
    
    found_any = False
    for chat_id in chats_registry:
        try:
            # Проверяем статус пользователя в конкретном чате
            member = await message.bot.get_chat_member(chat_id, user_id)
            
            # Если пользователь состоит в группе
            if member.status not in ["left", "kicked"]:
                chat = await message.bot.get_chat(chat_id)
                print(f"[НАЙДЕН] Группа: {chat.title} | ID: {chat_id}")
                found_any = True
        except Exception as e:
            # Ошибка может возникнуть, если бота удалили, пока он был оффлайн
            continue
            
    if not found_any:
        print("Пользователь не найден ни в одной из общих групп.")
    
    print("--- Проверка завершена ---\n")
    await message.answer("Результат проверки выведен в терминал сервера.")
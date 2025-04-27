import asyncio
import random
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, F, types, Router
from aiogram.filters import Command
from aiogram.types import ChatPermissions

# Настройки
TOKEN = "7809092146:AAHt5mOUHHyl2Vzt1MI1UdA8nR6fU7iG3_U"
warns = {}
ranks = {}  # Формат: {chat_id: {user_id: ранг}}
RANK_PRIORITY = {
    "User": 10,
    "Модер": 30,
    "Крутенький": 50,
    "Создатель": 80,
    "Высший создатель": 100
}

bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

# Загрузка матов
with open("bad_words.txt", encoding="utf-8") as f:
    bad_words = set(word.strip().lower() for word in f if word.strip())

# Проверка полномочий
def can_manage(executor_rank, target_rank):
    return RANK_PRIORITY.get(executor_rank, 0) > RANK_PRIORITY.get(target_rank, 0)

def get_rank(chat_id, user_id):
    return ranks.get(chat_id, {}).get(user_id, "User")

def set_rank(chat_id, user_id, rank):
    if chat_id not in ranks:
        ranks[chat_id] = {}
    ranks[chat_id][user_id] = rank

# Назначаем Высшего Создателя при первом сообщении
@router.message()
async def auto_assign(message: types.Message):
    if message.chat.type in ["group", "supergroup"]:
        if message.chat.id not in ranks:
            ranks[message.chat.id] = {}
            ranks[message.chat.id][message.from_user.id] = "Высший создатель"

# Команды
@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.reply("Бот активен. Введите /help для списка команд.")

@router.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.reply("⚙️ Команды: /ban /unban /mute /unmute /warn /unwarn /kick /up /down\n🎮 Игры: !дуэль, !ктокто")

@router.message(Command("warn"))
async def cmd_warn(message: types.Message):
    if message.reply_to_message:
        chat_id = message.chat.id
        executor = message.from_user.id
        target = message.reply_to_message.from_user.id

        executor_rank = get_rank(chat_id, executor)
        target_rank = get_rank(chat_id, target)

        if not can_manage(executor_rank, target_rank):
            return await message.reply("❌ Недостаточно прав для выдачи варна.")

        warns[target] = warns.get(target, 0) + 1
        await message.reply(f"⚠️ Предупреждение {warns[target]} для {message.reply_to_message.from_user.first_name}")
        if warns[target] >= 3:
            warns[target] = 0
            await bot.restrict_chat_member(
                chat_id,
                target,
                permissions=ChatPermissions(can_send_messages=False),
                until_date=datetime.now() + timedelta(minutes=30)
            )
            await message.reply(f"⏰ {message.reply_to_message.from_user.first_name} замьючен на 30 минут за 3 предупреждения.")

@router.message(Command("unwarn"))
async def cmd_unwarn(message: types.Message):
    if message.reply_to_message:
        target = message.reply_to_message.from_user.id
        warns[target] = max(0, warns.get(target, 0) - 1)
        await message.reply(f"ℹ️ Снято предупреждение. Текущее: {warns[target]}")

@router.message(Command("ban"))
async def cmd_ban(message: types.Message):
    if message.reply_to_message:
        chat_id = message.chat.id
        executor = message.from_user.id
        target = message.reply_to_message.from_user.id

        executor_rank = get_rank(chat_id, executor)
        target_rank = get_rank(chat_id, target)

        if not can_manage(executor_rank, target_rank):
            return await message.reply("❌ Недостаточно прав для бана.")

        await bot.ban_chat_member(chat_id, target)
        await message.reply("✅ Пользователь забанен.")

@router.message(Command("unban"))
async def cmd_unban(message: types.Message):
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        await bot.unban_chat_member(message.chat.id, user_id)
        await message.reply("✅ Пользователь разбанен.")

@router.message(Command("mute"))
async def cmd_mute(message: types.Message):
    if message.reply_to_message:
        chat_id = message.chat.id
        executor = message.from_user.id
        target = message.reply_to_message.from_user.id

        executor_rank = get_rank(chat_id, executor)
        target_rank = get_rank(chat_id, target)

        if not can_manage(executor_rank, target_rank):
            return await message.reply("❌ Недостаточно прав для мута.")

        await bot.restrict_chat_member(
            chat_id,
            target,
            permissions=ChatPermissions(can_send_messages=False),
            until_date=datetime.now() + timedelta(minutes=30)
        )
        await message.reply("✅ Пользователь замьючен на 30 минут.")

@router.message(Command("unmute"))
async def cmd_unmute(message: types.Message):
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        await bot.restrict_chat_member(
            message.chat.id,
            user_id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True
            )
        )
        await message.reply("✅ Пользователь размьючен.")

@router.message(Command("kick"))
async def cmd_kick(message: types.Message):
    if message.reply_to_message:
        chat_id = message.chat.id
        executor = message.from_user.id
        target = message.reply_to_message.from_user.id

        executor_rank = get_rank(chat_id, executor)
        target_rank = get_rank(chat_id, target)

        if not can_manage(executor_rank, target_rank):
            return await message.reply("❌ Недостаточно прав для кика.")

        await bot.ban_chat_member(chat_id, target)
        await bot.unban_chat_member(chat_id, target)
        await message.reply("✅ Пользователь кикнут.")

@router.message(Command("up"))
async def cmd_up(message: types.Message):
    if message.reply_to_message:
        chat_id = message.chat.id
        executor = message.from_user.id
        target = message.reply_to_message.from_user.id

        if get_rank(chat_id, executor) not in ["Создатель", "Высший создатель"]:
            return await message.reply("❌ Только Создатель или Высший Создатель может повышать.")

        target_rank = get_rank(chat_id, target)

        next_rank = {
            "User": "Модер",
            "Модер": "Крутенький",
            "Крутенький": "Создатель"
        }.get(target_rank)

        if next_rank:
            set_rank(chat_id, target, next_rank)
            await message.reply(f"✅ Повышен до {next_rank}.")
        else:
            await message.reply("❌ Нельзя повысить.")

@router.message(Command("down"))
async def cmd_down(message: types.Message):
    if message.reply_to_message:
        chat_id = message.chat.id
        executor = message.from_user.id
        target = message.reply_to_message.from_user.id

        if get_rank(chat_id, executor) not in ["Создатель", "Высший создатель"]:
            return await message.reply("❌ Только Создатель или Высший Создатель может понижать.")

        target_rank = get_rank(chat_id, target)

        prev_rank = {
            "Создатель": "Крутенький",
            "Крутенький": "Модер",
            "Модер": "User"
        }.get(target_rank)

        if prev_rank:
            set_rank(chat_id, target, prev_rank)
            await message.reply(f"✅ Понижен до {prev_rank}.")
        else:
            await message.reply("❌ Нельзя понизить.")

# Обработка обычных сообщений (мат-фильтр + мини-игры)
@router.message(F.text)
async def message_handler(message: types.Message):
    text = message.text.lower()
    user = message.from_user

    if any(bad_word in text for bad_word in bad_words):
        await message.delete()
        warns[user.id] = warns.get(user.id, 0) + 1
        await message.answer(f"🚫 Мат! Предупреждение: {warns[user.id]}")
        if warns[user.id] >= 3:
            warns[user.id] = 0
            await bot.restrict_chat_member(
                message.chat.id,
                user.id,
                permissions=ChatPermissions(can_send_messages=False),
                until_date=datetime.now() + timedelta(minutes=30)
            )
            await message.answer(f"⏰ {user.first_name} замьючен на 30 минут за 3 предупреждения.")
        return

    if "!дуэль" in text:
        admins = await bot.get_chat_administrators(message.chat.id)
        names = [admin.user.first_name for admin in admins]
        if len(names) >= 2:
            await message.reply(f"⚔️ Победил: {random.choice(names)}")
    elif "!ктокто" in text:
        await message.reply(f"🤔 Это точно {user.first_name}!")

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

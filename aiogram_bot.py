import asyncio
import random
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import ChatPermissions

TOKEN = "7809092146:AAHt5mOUHHyl2Vzt1MI1UdA8nR6fU7iG3_U"
ADMIN_IDS = {7014503619}
warns = {}

# Загрузка матов
with open("bad_words.txt", encoding="utf-8") as f:
    bad_words = set(word.strip().lower() for word in f if word.strip())

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Команды
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.reply("Бот активен. Введите /help для списка команд.")

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.reply("⚙️ Команды модерации:\n/ban /mute /warn /unwarn /kick\n🎮 Игры: !дуэль, !ктокто")

@dp.message(Command("ban"))
async def cmd_ban(message: types.Message):
    if message.reply_to_message:
        await bot.ban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
        await message.reply("Пользователь забанен.")

@dp.message(Command("mute"))
async def cmd_mute(message: types.Message):
    if message.reply_to_message:
        await bot.restrict_chat_member(
            message.chat.id,
            message.reply_to_message.from_user.id,
            permissions=ChatPermissions(can_send_messages=False)
        )
        await message.reply("Пользователь замьючен.")

@dp.message(Command("warn"))
async def cmd_warn(message: types.Message):
    if message.reply_to_message:
        user = message.reply_to_message.from_user
        warns[user.id] = warns.get(user.id, 0) + 1
        await message.reply(f"⚠️ Предупреждение {warns[user.id]} для {user.first_name}")
        if warns[user.id] >= 3:
            await bot.ban_chat_member(message.chat.id, user.id)
            await message.reply(f"❌ {user.first_name} забанен за 3 предупреждения.")

@dp.message(Command("unwarn"))
async def cmd_unwarn(message: types.Message):
    if message.reply_to_message:
        user = message.reply_to_message.from_user
        warns[user.id] = max(0, warns.get(user.id, 0) - 1)
        await message.reply(f"ℹ️ Предупреждение снято. Текущее: {warns[user.id]}")

@dp.message(Command("kick"))
async def cmd_kick(message: types.Message):
    if message.reply_to_message:
        await bot.ban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
        await bot.unban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
        await message.reply("Пользователь кикнут.")

@dp.message(Command("unlock3434"))
async def cmd_unlock(message: types.Message):
    if message.from_user.id in ADMIN_IDS:
        await message.reply("🔓 Секретная команда выполнена.")

# Обработка текстовых сообщений
@dp.message(F.text)
async def message_handler(message: types.Message):
    text = message.text.lower()
    user = message.from_user

    # Мат-фильтр
    if any(bad_word in text for bad_word in bad_words):
        await message.delete()
        warns[user.id] = warns.get(user.id, 0) + 1
        await message.answer(f"🚫 Мат! Предупреждение: {warns[user.id]}")
        if warns[user.id] >= 3:
            await bot.ban_chat_member(message.chat.id, user.id)
            await message.answer(f"❌ {user.first_name} забанен за 3 нарушения.")
        return

    # Игры
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

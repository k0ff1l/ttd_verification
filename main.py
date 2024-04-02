import discord
from aiogram.client.default import DefaultBotProperties
from discord.ext import commands
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.filters import CommandStart
import random
from cfg import TELEGRAM_BOT_TOKEN, DISCORD_BOT_TOKEN, CHAT_ID

# Инициализация Телеграм-бота
telegram_bot = Bot(token=TELEGRAM_BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Инициализация Дискорд-бота
intents = discord.Intents.all()

discord_bot = commands.Bot(command_prefix='!', intents=intents);


# Функция для отправки сообщения в Телеграм
async def send_telegram_message(user_id, text):
    await telegram_bot.send_message(user_id, text)


async def send_message_discord(channel_id, text):
    channel = discord_bot.get_channel(channel_id)
    await channel.send(text)


codes = {}


# Обработчик команды с параметром username
@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"твой айди - {message.from_user.id}")


# Команда для отправки кода подтверждения в Дискорд
@discord_bot.command()
async def send_code(ctx):

    #if user is verified, don't send code
    guild = ctx.guild
    role = discord.utils.get(guild.roles, name="verified")
    if role in ctx.author.roles:
        await ctx.send("Вы уже подтверждены")
        return

    try:
        if len(ctx.message.content.split(' ')) < 2:
            await ctx.send("Укажите ID пользователя")
            return
        user_id = ctx.message.content.split(' ')[1]

    except IndexError:
        await ctx.send("Произошла ошибка при извлечении ID пользователя")

    member = await telegram_bot.get_chat_member(CHAT_ID, user_id)
    if member.status in ['left', 'kicked', 'restricted']:
        await ctx.send("Пользователь не находится в чате")
        return

    code = random.randint(10000, 99999)
    codes[ctx.message.author.id] = str(code)
    await send_telegram_message(user_id, f"Код подтверждения: {code}")
    await ctx.send("Код подтверждения отправлен в Телеграм")


@discord_bot.command()
async def verify_code(ctx):
    # todo : if in verified list, return
    # if ...

    if len(ctx.message.content.split(' ')) < 2:
        await ctx.send("Укажите код подтверждения")
        return

    code = ctx.message.content.split(' ')[1]
    if code == codes[ctx.message.author.id]:
        await ctx.send("Код подтвержден")
        codes.pop(ctx.message.author.id)
        # выдай роль
        guild = ctx.guild
        role = discord.utils.get(guild.roles, name="verified")
        await ctx.author.add_roles(role)
    else:
        await ctx.send("Код неверный")


# Слушатель событий Дискорд-бота
@discord_bot.event
async def on_ready():
    print('Logged in as')
    print(discord_bot.user.name)
    print(discord_bot.user.id)
    print('------')


discord_bot.run(DISCORD_BOT_TOKEN)


async def main():
    await dp.start_polling(telegram_bot)
    await asyncio.sleep(0)


if __name__ == '__main__':
    import asyncio

    asyncio.run(main())

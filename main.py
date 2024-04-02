import asyncio
import random

import discord
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from discord.ext import commands

from cfg import TELEGRAM_BOT_TOKEN, DISCORD_BOT_TOKEN, CHAT_ID, ROLE_NAME

telegram_bot = Bot(token=TELEGRAM_BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

intents = discord.Intents.all()

discord_bot = commands.Bot(command_prefix='!', intents=intents)

# async def send_message_discord(channel_id, text):
#     channel = discord_bot.get_channel(channel_id)
#     await channel.send(text)


codes = {}
attempts = {}

# todo: fix /start
@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(
        f"твой айди - {message.from_user.id}, используй его в дискорде с командой <code>!send_code {message.from_user.id}</code>")


async def already_verified(ctx):
    guild = ctx.guild
    role = discord.utils.get(guild.roles, name=ROLE_NAME)
    if role in ctx.author.roles:
        await ctx.send("вы уже подтверждены")
        return True
    return False


@discord_bot.command()
async def send_code(ctx):
    if await already_verified(ctx):
        return

    try:
        if len(ctx.message.content.split(' ')) < 2:
            await ctx.send("укажите ID пользователя")
            return
        user_id = ctx.message.content.split(' ')[1]
    except IndexError:
        await ctx.send("произошла ошибка при извлечении ID пользователя")

    member = await telegram_bot.get_chat_member(CHAT_ID, user_id)
    if member.status in ['left', 'kicked', 'restricted']:
        await ctx.send("пользователь не находится в чате")
        return

    code = random.randint(10000, 99999)
    codes[ctx.message.author.id] = str(code)
    await telegram_bot.send_message(user_id, f"ваш код подтверждения: {code}, через 120 секунд он будет уничтожен")
    await ctx.send("код подтверждения отправлен в Телеграм")
    await asyncio.sleep(120)
    try:
        codes.pop(ctx.message.author.id)
    except KeyError:
        pass
    print('deleted code')


@discord_bot.command()
async def verify_code(ctx):
    if await already_verified(ctx):
        return

    if ctx.message.author.id not in attempts:
        attempts[ctx.message.author.id] = 0

    if attempts[ctx.message.author.id] > 3:
        await ctx.send("превышено количество попыток, повторите через 20 минут")
        await asyncio.sleep(1200)
        attempts[ctx.message.author.id] = 0
        return

    if len(ctx.message.content.split(' ')) < 2:
        await ctx.send("укажите код подтверждения")
        return

    attempts[ctx.message.author.id] += 1

    code = ctx.message.content.split(' ')[1]
    try:
        if code == codes[ctx.message.author.id]:
            await ctx.send("код подтвержден")
            attempts.pop(ctx.message.author.id)
            codes.pop(ctx.message.author.id)
            guild = ctx.guild
            role = discord.utils.get(guild.roles, name=ROLE_NAME)
            await ctx.author.add_roles(role)
        else:
            await ctx.send("код неверный")
    except KeyError:
        await ctx.send("код истёк")


@discord_bot.event
async def on_ready():
    print('logged in as', discord_bot.user.name, discord_bot.user.id)


discord_bot.run(DISCORD_BOT_TOKEN)


async def main():
    await dp.start_polling(telegram_bot)


if __name__ == '__main__':
    asyncio.run(main())

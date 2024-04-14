import aiogram.client.default
import asyncio
import discord
import random
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from cfg import TELEGRAM_BOT_TOKEN, DISCORD_BOT_TOKEN, CHAT_ID, ROLE_NAME, WELCOME_MSG
from discord.ext import commands

dp = Dispatcher()

discord_bot = commands.Bot(command_prefix='/', intents=discord.Intents.all())

telegram_bot = Bot(token=TELEGRAM_BOT_TOKEN,
                   default=aiogram.client.default.DefaultBotProperties(parse_mode=ParseMode.HTML))

codes = {}
attempts = {}

# todo
'''
оптимизировать количество шагов, чтобы сразу по старту проверял, есть ли человек
в нужной группе, если есть отправляет временный код, подтверждает

учесть, что нужно ещё и переименовывать пользователя в его реальное имя и фамилию.
'''


@dp.message(CommandStart())
async def command_start_handler(message):
    await message.answer(
        f"твой айди - {message.from_user.id}, используй его в дискорде с командой \n <code>/send {message.from_user.id}</code>")


async def already_verified(ctx):
    guild = ctx.guild
    role = discord.utils.get(guild.roles, name=ROLE_NAME)
    if role in ctx.author.roles:
        await ctx.author.send("вы уже подтверждены")
        return True
    return False


@discord_bot.command()
async def send(ctx):
    await ctx.message.delete()
    if await already_verified(ctx):
        return
    user_id = "***"
    try:
        if len(ctx.message.content.split(' ')) < 2:
            await ctx.author.send("укажите ID пользователя")
            return
        user_id = ctx.message.content.split(' ')[1]
    except IndexError:
        await ctx.author.send("произошла ошибка при извлечении ID пользователя")

    if user_id == "***":
        await ctx.author.send("произошла ошибка при извлечении ID пользователя")
        raise Exception("User ID is not defined")

    member = await telegram_bot.get_chat_member(CHAT_ID, user_id)
    if member.status in ['left', 'kicked', 'restricted']:
        await ctx.author.send("пользователь не находится в чате")
        return

    code = random.randint(10000, 99999)
    codes[ctx.message.author.id] = str(code)
    await telegram_bot.send_message(user_id, f"ваш код подтверждения: {code}, через 120 секунд он будет уничтожен \n "
                                             f"вместе с кодом введите ваше реальное имя и фамилию \n"
                                             f"<code>/verify {code} имя фамилия</code>")
    await ctx.author.send("код подтверждения отправлен в телеграм")
    await asyncio.sleep(120)
    try:
        codes.pop(ctx.message.author.id)
    except KeyError:
        pass
    print('deleted code')


@discord_bot.command()
async def verify(ctx):
    await ctx.message.delete()
    if await already_verified(ctx):
        return

    if ctx.message.author.id not in attempts:
        attempts[ctx.message.author.id] = 0

    if attempts[ctx.message.author.id] > 3:
        await ctx.author.send("превышено количество попыток, повторите через 20 минут")
        await asyncio.sleep(1200)
        attempts[ctx.message.author.id] = 0
        return

    if len(ctx.message.content.split(' ')) < 2:
        await ctx.author.send("укажите код подтверждения")
        return

    attempts[ctx.message.author.id] += 1

    code, name, surname = ctx.message.content.split(' ')[1], ctx.message.content.split(' ')[2], ctx.message.content.split(' ')[3]
    try:
        if code == codes[ctx.message.author.id]:
            await ctx.author.send("код подтвержден")
            await ctx.author.edit(nick=name + ' ' + surname)
            attempts.pop(ctx.message.author.id)
            codes.pop(ctx.message.author.id)
            guild = ctx.guild
            role = discord.utils.get(guild.roles, name=ROLE_NAME)
            await ctx.author.add_roles(role)
        else:
            await ctx.author.send("код неверный")
    except KeyError:
        await ctx.author.send("код истёк")


@discord_bot.event
async def on_member_join(ctx):
    await ctx.author.send(WELCOME_MSG)

# for test
@discord_bot.command()
async def ost(ctx):
    await on_member_join(ctx)

# just some utils
@discord_bot.command()
async def clear(ctx, amount=5):
    if ctx.author.guild_permissions.manage_messages:
        await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f'{amount} сообщений было удалено.', delete_after=5)
    else:
        await ctx.send("У вас нет прав для выполнения этой команды.")


@discord_bot.command()
async def test_on_join(ctx):
    await on_member_join(ctx)


@discord_bot.event
async def on_ready():
    print('logged in as', discord_bot.user.name, discord_bot.user.id)


async def discord_bot_task():
    await discord_bot.start(DISCORD_BOT_TOKEN)


async def main():
    telegram_task = asyncio.create_task(dp.start_polling(telegram_bot))
    discord_task = asyncio.create_task(discord_bot_task())
    await telegram_task
    await discord_task


if __name__ == "__main__":
    print("starting main")
    asyncio.run(main())

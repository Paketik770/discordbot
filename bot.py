import asyncio
import logging

import discord
from discord.ext import commands

import db
from config import BOT_TOKEN, GUILD_ID, PREFIX

logging.basicConfig(level=logging.INFO)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)


@bot.event
async def on_ready():
    db.init_db()
    print(f"Бот {bot.user} готов к работе!")
    print(f"Бот видит серверы (guilds):")
    for g in bot.guilds:
        print(f"  - {g.name} | id={g.id}")
    print(f"Конфиг GUILD_ID = {GUILD_ID}")
    print(f"GUILD_ID найден в списке: {any(g.id == GUILD_ID for g in bot.guilds)}")
    print(f"Загруженные cog-и: {list(bot.cogs.keys())}")
    print(f"Команд в дереве: {[c.name for c in bot.tree.get_commands()]}")
    print(f"Синхронизирую команды...")
    await asyncio.sleep(2)
    try:
        guild = discord.Object(id=GUILD_ID) if GUILD_ID else None
        synced = 0
        if guild:
            synced = len(await bot.tree.sync(guild=guild))
            print(f"Guild sync: {synced} команд")
        if synced == 0:
            # глобальная синхронизация как fallback (занимает до часа)
            synced = len(await bot.tree.sync())
            print(f"Глобальная синхронизация: {synced} команд")
    except Exception as e:
        print(f"Ошибка синхронизации команд: {e}")


async def main():
    await bot.load_extension("cogs.ranks")
    await bot.load_extension("cogs.admin")
    await bot.start(BOT_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
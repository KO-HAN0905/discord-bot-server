import discord
from discord.ext import commands
import os
from config import DISCORD_BOT_TOKEN, PREFIX
from datetime import datetime

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)
bot.start_time = datetime.now()

@bot.event
async def on_ready():
    print(f'OK: {bot.user} online')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='!help'))

async def load_cogs():
    for f in os.listdir('./cogs'):
        if f.endswith('.py') and f != '__init__.py':
            try:
                await bot.load_extension(f'cogs.{f[:-3]}')
                print(f'OK: {f}')
            except Exception as e:
                print(f'ERROR: {f} - {e}')

async def main():
    async with bot:
        await load_cogs()
        await bot.start(DISCORD_BOT_TOKEN)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())

import discord

from discord.ext import commands

from config import TOKEN


intents = discord.Intents.default()

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


@bot.event
async def on_ready():

    await bot.load_extension("commands")

    synced = await bot.tree.sync()

    print("---------------------")
    print(bot.user)
    print(f"{len(synced)}個のコマンドを同期")
    print("---------------------")


bot.run(TOKEN)
import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

TOKEN = os.getenv("DISCORD_TOKEN")

# Wstaw tu swoje ID kanałów
WELCOME_CHANNEL_ID = 1368259729914069194   # np. #welcome
FAREWELL_CHANNEL_ID = 1368262433503707308  # np. #farewell

intents = discord.Intents.default()
intents.members = True  # ważne: potrzebne do wykrywania join/leave
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Zalogowano jako {bot.user}")

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        embed = discord.Embed(
            title=f"Witaj {member.name}!",
            description=f"Baw się dobrze na serwerze **{member.guild.name}**! 🎉",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.set_footer(text=f"Dołączył(a): {member.joined_at.strftime('%Y-%m-%d %H:%M:%S')}" if member.joined_at else "Nowy członek")
        await channel.send(embed=embed)

@bot.event
async def on_member_remove(member):
    channel = bot.get_channel(FAREWELL_CHANNEL_ID)
    if channel:
        embed = discord.Embed(
            title=f"żegnaj **{member.name}** 😢",
            description=f"**{member.name}** opuścił/a serwer **{member.guild.name}**.",
            color=discord.Color.red()
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        await channel.send(embed=embed)




app = Flask('')

@app.route('/')
def home():
    return "Bot działa!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()



keep_alive()
bot.run(TOKEN)
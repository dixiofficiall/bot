import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread
import requests
import time
from transformers import GPT2LMHeadModel, GPT2Tokenizer

TOKEN = os.getenv("DISCORD_TOKEN")

# Wstaw tu swoje ID kanałów
WELCOME_CHANNEL_ID = 1368259729914069194   # np. #welcome
FAREWELL_CHANNEL_ID = 1368262433503707308  # np. #farewell
AI_CHANNEL_ID = 1368343534079311872  # <-- Podaj ID kanału tekstowego, na którym bot będzie odpowiadał jako AI

# Inicjalizacja bota Discord
intents = discord.Intents.default()
intents.members = True  # ważne: potrzebne do wykrywania join/leave
intents.message_content = True  # pozwala na dostęp do treści wiadomości

bot = commands.Bot(command_prefix="!", intents=intents)

# Inicjalizacja modelu GPT-2
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2")

# Funkcja generująca odpowiedź AI na podstawie tekstu
def generate_response(text):
    inputs = tokenizer.encode(text, return_tensors="pt")
    outputs = model.generate(inputs, max_length=50, num_return_sequences=1, no_repeat_ngram_size=2, top_p=0.9, temperature=0.7)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response

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

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return  # Ignoruj wiadomości wysyłane przez bota
    
    # Sprawdzanie, czy wiadomość pochodzi z odpowiedniego kanału
    if message.channel.id == AI_CHANNEL_ID:
        # Jeśli wiadomość zawiera słowo "fnaf", generuj odpowiedź na temat FNaF
        if "fnaf" in message.content.lower():
            response = generate_response("Tell me about Five Nights at Freddy's")
            await message.channel.send(response)
        
        # Jeśli wiadomość zawiera "hello", odpowiedz "hello"
        elif "hello" in message.content.lower():
            response = generate_response("Say hello!")
            await message.channel.send(response)
        
        # Przetwarzanie komend (np. !ping)
        await bot.process_commands(message)

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

# Flask
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

# Pingowanie Render
def auto_ping():
    while True:
        try:
            requests.get("https://dashboard.render.com/web/srv-d0b7elje5dus7381e41g/logs")  # <-- podmień na swój adres Render
            print("Ping wysłany.")
        except Exception as e:
            print(f"Błąd pingu: {e}")
        time.sleep(30)  # ping co 30 sekund

# Uruchomienie pingu w osobnym wątku
Thread(target=auto_ping).start()

# Uruchomienie bota Discord
bot.run(TOKEN)


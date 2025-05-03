import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread
import requests
import time
from transformers import GPT2LMHeadModel, GPT2Tokenizer

TOKEN = os.getenv("DISCORD_TOKEN")


WELCOME_CHANNEL_ID = 1368259729914069194  
FAREWELL_CHANNEL_ID = 1368262433503707308  
AI_CHANNEL_ID = 1368343534079311872  


intents = discord.Intents.default()
intents.members = True  
intents.message_content = True  

bot = commands.Bot(command_prefix="!", intents=intents)


tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2")


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
        return  
    
    
    if message.channel.id == AI_CHANNEL_ID:
        
        if "fnaf" in message.content.lower():
            response = generate_response("Tell me about Five Nights at Freddy's")
            await message.channel.send(response)
        
        
        elif "hello" in message.content.lower():
            response = generate_response("Say hello!")
            await message.channel.send(response)
        
  
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


def auto_ping():
    while True:
        try:
            requests.get("https://dashboard.render.com/web/srv-d0b7elje5dus7381e41g/logs") 
            print("Ping wysłany.")
        except Exception as e:
            print(f"Błąd pingu: {e}")
        time.sleep(30)  


Thread(target=auto_ping).start()


bot.run(TOKEN)


import discord
from discord.ext import commands
from keep_alive import keep_alive
import os
import requests

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

@bot.event
async def on_ready():
    print(f'Gogeta has awakened. Logged in as {bot.user}')

def generate_gogeta_reply(prompt):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "openai/gpt-4o",
        "messages": [
            {"role": "system", "content": "You are Gogeta, the fusion of Goku and Vegeta. You are wise, calm, and intellectual. Respond thoughtfully, with depth and clarity, like a strategist. Do not be aggressive or vulgar."},
            {"role": "user", "content": prompt}
        ]
    }
    try:
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        return res.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return "Something went wrong with my thoughts... try again later."

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user in message.mentions or isinstance(message.channel, discord.DMChannel):
        user_input = message.content.replace(f"<@!{bot.user.id}>", "").strip()
        if user_input:
            await message.channel.typing()
            reply = generate_gogeta_reply(user_input)
            await message.channel.send(reply)

    await bot.process_commands(message)

keep_alive()
bot.run(os.getenv("TOKEN"))

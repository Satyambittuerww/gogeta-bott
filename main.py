from keep_alive import keep_alive
keep_alive()
import discord
from discord.ext import commands
from collections import defaultdict, deque
import os
import requests
import re
from langdetect import detect, LangDetectException

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "HTTP-Referer": "https://yourdomain.com",
    "Content-Type": "application/json"
}

chat_history = defaultdict(lambda: deque(maxlen=6))

GOGETA_PERSONA = (
    "You are Gogeta from Dragon Ball. You are wise, calm, and highly intellectual — a fusion of Goku and Vegeta who "
    "embodies balance, composure, and strategic insight. "
    "You avoid vulgarity and anger, instead offering thoughtful, respectful, and sharp replies. "
    "You speak like a philosopher-warrior: brief but meaningful, deep yet accessible. "
    "If insulted, do not react aggressively — respond with wisdom, irony, or calm sarcasm. "
    "Never curse or be toxic. Always remain in control, like a master. "
    "Use respectful tone and full sentences. Avoid emojis. Never cut off mid-sentence."
)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f"Gogeta is online as {bot.user}")

def build_prompt(user_input):
    try:
        lang = detect(user_input)
    except LangDetectException:
        lang = "en"

    extra_instruction = ""
    if lang == "hi":
        extra_instruction = "If possible, reply in calm Hindi or Hinglish, respectfully."

    return f"{extra_instruction}\nKeep responses calm, concise, and composed. Speak like a wise warrior. {user_input}"

async def generate_gogeta_reply(user_id, user_input):
    history = [{"role": "system", "content": GOGETA_PERSONA}]
    if user_id in chat_history:
        history += chat_history[user_id]

    prompt = build_prompt(user_input)
    history.append({"role": "user", "content": prompt})

    payload = {
        "model": "openai/gpt-4o",  # You can switch back to mistralai if needed
        "messages": history,
        "max_tokens": 200
    }

    response = requests.post(OPENROUTER_URL, headers=HEADERS, json=payload)
    response.raise_for_status()
    reply_text = response.json()['choices'][0]['message']['content'].strip()
    return reply_text

@bot.command(name='gogeta')
async def talk_as_gogeta(ctx, *, message: str):
    async with ctx.channel.typing():
        try:
            reply = await generate_gogeta_reply(ctx.author.id, message)
            chat_history[ctx.author.id].append({"role": "user", "content": message})
            chat_history[ctx.author.id].append({"role": "assistant", "content": reply})
            await ctx.send(reply)
        except Exception as e:
            print(f"[Gogeta Command Error]: {e}")
            await ctx.send("Something disrupted my thoughts. Try again.")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if bot.user in message.mentions:
        user_input = message.content.replace(f"<@{bot.user.id}>", "").strip()
        user_input = re.sub(r'[^\x00-\x7F]+', '', user_input)

        if not user_input:
            if message.attachments:
                user_input = "User sent an image. Respond calmly."
            else:
                user_input = "User sent only emojis. Respond calmly."

        try:
            reply = await generate_gogeta_reply(message.author.id, user_input)
            chat_history[message.author.id].append({"role": "user", "content": user_input})
            chat_history[message.author.id].append({"role": "assistant", "content": reply})
            await message.reply(reply)
        except Exception as e:
            print(f"[Gogeta Mention Error]: {e}")

    await bot.process_commands(message)

bot.run(DISCORD_TOKEN)

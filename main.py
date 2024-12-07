import discord
import psutil
import time
import json
import os
import sys
import asyncio
import aiohttp
import requests
import platform
from datetime import datetime
from PIL import Image
from log import send_webhook
from discord.ext import commands
from reportlab.lib.pagesizes import letter # type: ignore
from reportlab.pdfgen import canvas # type: ignore
import io

with open('config.json', 'r') as file:
    data = json.load(file)


token = data["token"]
client = commands.Bot(command_prefix=">", self_bot=True)
active_sessions = {}
IMGFLIP_USERNAME = data['imgflip_username']
IMGFLIP_PASSWORD = data['imgflip_password']
MEME_TEMPLATES = data['meme_templates']

@client.event
async def on_ready():
    computer_name = platform.node()
    if computer_name not in active_sessions:
        active_sessions[computer_name] = {"start_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    send_webhook(f"C2 Started on {computer_name}.")
    send_webhook("C2 Startup Completed, now online!")   

@client.command()
async def sessions(ctx):
    session_info = [f"{comp} - Start Time: {info['start_time']}" for comp, info in active_sessions.items()]
    await ctx.reply(f"```json\nActive Sessions:\n```" + "\n".join(session_info))

@client.command()
async def kick(ctx, member: discord.Member):
    await ctx.reply(f"Kicking member {member} ({member.id})..")
    await asyncio.sleep(1)
    
    try:
        await member.kick(reason="Automated kick by LithiumBot")
        send_webhook(f"Successfully kicked the member with the ID of {member.id}.")
        await ctx.reply(f"{member.mention} ({member.id}) has been kicked from the server.")
    except:
        send_webhook(f"Failed to kick {member.id}.")
        await ctx.reply("Failed to kick this member. Please try again.")

@client.command(name="serverinfo", aliases=["sinfo", "server"])
async def serverinfo(ctx):
    guild = ctx.guild
    server_info = (
        f"Server Name: {guild.name}\n"
        f"Server ID: {guild.id}\n"
        f"Creation Date: {guild.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"Member Count: {guild.member_count}\n"
        f"Online Members: {len([m for m in guild.members if m.status == discord.Status.online])}\n"
        f"Total Channels: {len(guild.channels)}\n"
        f"Text Channels: {len([c for c in guild.channels if isinstance(c, discord.TextChannel)])}\n"
        f"Voice Channels: {len([c for c in guild.channels if isinstance(c, discord.VoiceChannel)])}\n"
        f"Roles Count: {len(guild.roles)}\n"
        f"Emojis Count: {len(guild.emojis)}\n"
        f"Boost Level: {guild.premium_tier}\n"
        f"Boost Count: {guild.premium_subscription_count}"
    )
    message = f"Server Info / {guild.name} / {guild.id}\n\n{server_info}"
    await ctx.reply(f"```json\n{message}\n```")
    send_webhook(f"```json\nFound Server Info: {message}```")

@client.command(aliases=["w"])
async def weather(ctx, *, city: str):
    url = f"https://wttr.in/{city}?format=%C+%t+%h+%p+%w+%v+%c+%S+%s"
    response = requests.get(url)
    if response.status_code != 200:
        await ctx.reply("Error: Unable to retrieve weather data.")
        return
    weather_data = response.text
    await ctx.reply(f"```json\n{weather_data}\n```")
    send_webhook(f"```json\nFound Weather Status: {weather_data}```")

@client.command(aliases=["av", "pfp"])
async def avatar(ctx, member: discord.User):
    try:
        await ctx.reply(f"```json\nMEMBER ID: {member.id}\nAVATAR URL: {member.avatar.url}\n```\n{member.avatar.url}")
        send_webhook(f"Found the avatar of the user {member.mention}.\n{member.avatar.url}")
    except:
        await ctx.reply("Could not find the avatar of this user.")
        send_webhook("Couldn't find the avatar of this user.")

@client.command(aliases=["crypt", "cryptocurrency"])
async def crypto(ctx, symbol: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd') as response:
            if response.status == 200:
                data = await response.json()
                if symbol in data:
                    price = data[symbol]['usd']
                    await ctx.reply(f"The current price of {symbol.upper()} is ${price:.2f}")
                    send_webhook(f"Succesfully found the price of {symbol.upper()} at ${price:.2f}")
                else:
                    await ctx.reply(f"Could not find data for the symbol '{symbol}'.")
            else:
                await ctx.reply("Couldn't fetch cryptocurrency data at the moment.")

@client.command(aliases=["ui", "info"])
async def userinfo(ctx, member: discord.User = None):
    if member is None:
        member = ctx.author
    user_info = f"User Info Command\nStatus: Working (online)\n\nUSER INFORMATION:\nUsername: {member.name}\n"
    await ctx.reply(f"```json\n{user_info}\n```")

@client.command(aliases=["p"])
async def ping(ctx):
    start_time = time.monotonic()
    message = await ctx.reply("Pinging...")
    end_time = time.monotonic()
    latency = (end_time - start_time) * 1000
    heartbeat_latency = client.latency * 100
    ping_info = (
        f"LithiumBot v1 Ping Command\n"
        f"Status: Working (online)\n\n"
        f"PING INFORMATION:\n"
        f"Message Latency: {latency:.2f} ms\n"
        f"Discord API Latency: {heartbeat_latency:.2f} ms"
    )
    await message.edit(content=f"```json\n{ping_info}\n```")
    await ctx.message.delete()

@client.command(aliases=["sys", "host", "stats"])
async def system(ctx):
    uname = platform.uname()
    cpufreq = psutil.cpu_freq()
    boot_time_timestamp = psutil.boot_time()
    bt = datetime.fromtimestamp(boot_time_timestamp)
    svmem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    disk_usage = psutil.disk_usage('/')
    net_if_addrs = psutil.net_if_addrs()
    net_if_stats = psutil.net_if_stats()
    battery = psutil.sensors_battery() if psutil.sensors_battery() else None

    os_info = (
        f"LithiumBot v1 - Development Version\n"
        f"Status: Working (online)\n\n"
        f"SYSTEM INFORMATION:\n"
        f"System: {uname.system}\n"
        f"Node Name: {uname.node}\n"
        f"Release: {uname.release}\n"
        f"Version: {uname.version}\n"
        f"Machine: {uname.machine}\n\n"
        f"BOOT TIME:\n"
        f"{bt.year}/{bt.month}/{bt.day} {bt.hour}:{bt.minute}:{bt.second}\n\n"
        f"CPU INFO:\n"
        f"Physical Cores: {psutil.cpu_count(logical=False)}\n"
        f"Total Cores: {psutil.cpu_count(logical=True)}\n"
        f"Current Frequency: {cpufreq.current:.2f} MHz\n\n"
        f"MEMORY INFORMATION:\n"
        f"Total: {svmem.total / (1024 ** 3):.2f} GB\n"
        f"Available: {svmem.available / (1024 ** 3):.2f} GB\n"
        f"Used: {svmem.used / (1024 ** 3):.2f} GB\n"
        f"Percentage: {svmem.percent}%\n\n"
        f"SWAP MEMORY:\n"
        f"Total: {swap.total / (1024 ** 3):.2f} GB\n"
        f"Free: {swap.free / (1024 ** 3):.2f} GB\n"
        f"Used: {swap.used / (1024 ** 3):.2f} GB\n"
        f"Percentage: {swap.percent}%\n\n"
        f"DISK USAGE:\n"
        f"Total: {disk_usage.total / (1024 ** 3):.2f} GB\n"
        f"Used: {disk_usage.used / (1024 ** 3):.2f} GB\n"
        f"Free: {disk_usage.free / (1024 ** 3):.2f} GB\n"
        f"Percentage: {disk_usage.percent}%\n\n"
    )
    await ctx.reply(f"```json\n{os_info}\n```")

@client.command(name="generate_meme")
async def generate_meme(ctx, meme_type: str, *, texts: str):
    # Split the input text into lines
    lines = texts.split('|')
    if len(lines) != 2:
        await ctx.reply("Please provide exactly two lines of text separated by '|'. Example: 'Top Line|Bottom Line'")
        return
    
    top_text, bottom_text = lines
    meme_templates = data["meme_templates"]
    if meme_type not in MEME_TEMPLATES:
        await ctx.reply("Unknown meme type. Available types are: " + ", ".join(MEME_TEMPLATES.keys()))
        return
    
    imgflip_url = "https://api.imgflip.com/caption_image"
    params = {
        "template_id": meme_templates[meme_type],
        "username": IMGFLIP_USERNAME,
        "password": IMGFLIP_PASSWORD,
        "text0": top_text,
        "text1": bottom_text
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(imgflip_url, params=params) as response:
            if response.status == 200:
                json_response = await response.json()
                if 'data' in json_response and 'url' in json_response['data']:
                    meme_url = json_response['data']['url']
                    await ctx.reply(meme_url)
                    await ctx.message.delete()
                    send_webhook(f"Generated {meme_type} Meme: {meme_url} with top text: '{top_text}' and bottom text: '{bottom_text}'")
                else:
                    await ctx.reply("Error: Unexpected response format from Imgflip API.")
                    await ctx.message.delete()
                    send_webhook("Error: Unexpected response format from Imgflip API.")
            else:
                await ctx.reply("Failed to generate meme. Please try again later.")
                await ctx.message.delete()
                send_webhook("Failed to generate meme. Imgflip API response status: " + str(response.status))

@client.command(name="joke")
async def joke(ctx, *, theme: str = "Any"):
    # Convert the theme to lowercase
    theme = theme.lower()
    
    # Define valid themes
    valid_themes = ["programming", "miscellaneous", "puns", "spooky", "christmas", "any"]
    
    if theme not in valid_themes:
        await ctx.reply(f"Invalid theme. Valid themes are: {', '.join(valid_themes)}.")
        return

    async with aiohttp.ClientSession() as session:
        url = f"https://v2.jokeapi.dev/joke/{theme}"
        async with session.get(url) as response:
            if response.status == 200:
                joke_data = await response.json()
                if joke_data.get('type') == 'single':
                    joke_text = joke_data.get('joke', 'No joke found.')
                    await ctx.reply(f"**Joke:** {joke_text}")
                    send_webhook(f"Joke: {joke_text}")
                elif joke_data.get('type') == 'twopart':
                    setup = joke_data.get('setup', 'No joke setup found.')
                    punchline = joke_data.get('delivery', 'No punchline found.')
                    await ctx.reply(f"**Joke:** {setup}\n**Punchline:** {punchline}\n**Category:** {joke_data.get('category', 'No category found.')}")
                    send_webhook(f"Joke: {setup} - {punchline}")
                else:
                    await ctx.reply("Error: Unexpected joke type.")
                    send_webhook("Error: Unexpected joke type.")
            else:
                await ctx.reply("Failed to fetch a joke. Please try again later.")
                send_webhook("Failed to fetch a joke. API response status: " + str(response.status))

@client.command(name="convert")
async def convert(ctx, file: discord.Attachment, target_format: str):
    # Ensure the target format is lowercase
    target_format = target_format.lower()

    if target_format not in ['pdf', 'jpg', 'png']:
        await ctx.reply("Invalid target format. Supported formats are 'pdf', 'jpg', and 'png'.")
        return

    # Download the file
    file_path = f"temp_{file.filename}"
    await file.save(file_path)

    if target_format in ['jpg', 'png']:
        # Ensure source file is an image
        try:
            with Image.open(file_path) as img:
                # Convert image to target format
                if target_format == 'jpg':
                    converted_file_path = f"{os.path.splitext(file_path)[0]}.jpg"
                    img.convert('RGB').save(converted_file_path, 'JPEG')
                elif target_format == 'png':
                    converted_file_path = f"{os.path.splitext(file_path)[0]}.png"
                    img.save(converted_file_path, 'PNG')
                
                # Send the converted file
                await ctx.send(f"```json\nConverting...```\n{file.filename} converted to {target_format}.")
                await ctx.send(file=discord.File(converted_file_path))
        except IOError:
            await ctx.reply("The source file must be a valid image file (PNG/JPG).")
            os.remove(file_path)
            return

        # Cleanup temporary files
        os.remove(file_path)
        os.remove(converted_file_path)
    
    elif target_format == 'pdf':
        if not file.filename.endswith('.txt'):
            await ctx.reply("The source file must be a text file (.txt) for PDF conversion.")
            os.remove(file_path)
            return

        pdf_output_path = f"{os.path.splitext(file_path)[0]}.pdf"
        c = canvas.Canvas(pdf_output_path, pagesize=letter)
        width, height = letter
        y = height - 40  # Starting Y position

        try:
            # Open file with UTF-8 encoding
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    # Add text to the PDF
                    c.drawString(40, y, line.strip())
                    y -= 15  # Move down for the next line
                    if y < 40:  # Start a new page if the current page is full
                        c.showPage()
                        y = height - 40

        except UnicodeDecodeError:
            await ctx.reply("Error: Unable to decode the file. Ensure it's a UTF-8 encoded text file.")
            os.remove(file_path)
            return

        c.save()

        # Send the converted PDF file
        await ctx.send(f"```json\nConverting...```\n{file.filename} converted to PDF.")
        await ctx.send(file=discord.File(pdf_output_path))
        

        # Cleanup temporary files
        os.remove(file_path)
        os.remove(pdf_output_path)
    else:
        await ctx.reply("Unsupported format conversion. Currently supported are 'pdf', 'jpg', and 'png'.")
        os.remove(file_path)

@client.command()
async def shutdown(ctx):
    await ctx.reply(f"```json\nShutting down the bot...\n```")
    await client.close()
    sys.exit()

@client.command(aliases=["reboot", "update"])
async def restart(ctx):
    await ctx.reply(f"```json\nRestarting the bot...\n```")
    send_webhook("Bot is restarting.")
    os.execv(sys.executable, ['python'] + sys.argv)
    
@client.command()
async def credits(ctx):
    await ctx.reply(f"```json\nLithiumBot v1 by @l_iquid and @someoneig22\n```")
    send_webhook("LithiumBot v1 by @l_iquid and @someoneig22")

#@client.command()
#async def source(ctx):
#   await ctx.reply(f"```json\nSource code: https://github.com/Lithium01/LithiumBot\n```")
#    send_webhook("Source code: https://github.com/Lithium01/LithiumBot")

client.run(token)

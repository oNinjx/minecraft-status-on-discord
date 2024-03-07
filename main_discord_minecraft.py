import discord
from discord.ext import tasks
import requests
import os
import datetime
import pytz
from keep_alive import keep_alive
keep_alive()

# Retrieve Discord bot token from Replit secrets environment variable
TOKEN = os.getenv('token')

# Minecraft server IP and port
MINECRAFT_SERVER_IP = 'play.htmc.one'
MINECRAFT_SERVER_PORT = 25662

# Initialize Discord client
intents = discord.Intents.default()
client = discord.Client(intents=intents)

# Variable to store the previous player count and message ID
prev_player_count = 0
message_id = None

# Function to query Minecraft server for player count and status
def get_server_info():
    try:
        response = requests.get(f'https://api.mcsrvstat.us/2/{MINECRAFT_SERVER_IP}:{MINECRAFT_SERVER_PORT}')
        data = response.json()
        print("Server response:", data)  # Debugging message
        if 'online' in data and data['online']:
            status = '`💚 ONLINE`'
        else:
            status = '`❤️ OFFLINE`'
        player_count = data.get('players', {}).get('online', 0) + 4  # Add 4 to the retrieved player count
        return status, player_count
    except Exception as e:
        print(f"Error occurred while querying Minecraft server: {e}")
        return '`❤️ OFFLINE`', 4  # Return default player count as 4 if there's an error

# Function to check if it's 6:38 PM Indian time
def is_indian_time_638pm():
    tz_india = pytz.timezone('Asia/Kolkata')
    current_time = datetime.datetime.now(tz_india)
    return current_time.hour == 18 and current_time.minute == 38

# Update Discord channel with player count and server status
@tasks.loop(seconds=30)  # Update every 30 seconds
async def update_player_count():
    global prev_player_count, message_id
    status, player_count = get_server_info()

    # If it's 6:38 PM Indian time, send a message mentioning @here
    if is_indian_time_638pm():
        channel = client.get_channel(1201058767488430150)  # Replace with your channel ID
        await channel.send("@here Server is up and restarted!")

    # If player count has changed or server status has changed, update Discord message
    if player_count != prev_player_count or not message_id:
        channel = client.get_channel(1201058767488430150)  # Replace with your channel ID
        if message_id:
            message = await channel.fetch_message(message_id)
            embed = message.embeds[0]
            embed.set_field_at(0, name='> **Status**', value=f'``{status}``', inline=False)
            embed.set_field_at(1, name='> **Playing**', value=f'```Total: {player_count} Players ❤️```', inline=False)
            await message.edit(embed=embed)
        else:
            embed = discord.Embed(title='Hometown Network', url='https://htmc.one/', color=discord.Color.green() if 'ONLINE' in status else discord.Color.red())
            embed.add_field(name='> **Status**', value=f'``{status}``', inline=False)
            embed.add_field(name='> **Playing**', value=f'```Total: {player_count} Players ❤️```', inline=False)
            embed.add_field(name='> **Server IP**', value='```PLAY.HTMC.ONE```', inline=True)
            embed.add_field(name='> **Server Port**', value='```25662```', inline=True)
            embed.add_field(name='> **Server Events**', value='```PVP Event 15 March\nBase Raiding 30 March```', inline=False)
            embed.add_field(name='> **Server Restart Time**', value='```18:38 IST Daily```', inline=False)
            embed.add_field(name='> **Versions**', value='```[1.9x-1.20.4x]```          ', inline=False)
            embed.set_image(url='https://cdn.discordapp.com/attachments/1200404861959819274/1209834352515751996/standard.gif?ex=65fad20b&is=65e85d0b&hm=a8a24f66bfa767efe074c455e7650d4a745f4c9bea9fa4056dbc5abd3a6fac88')
            embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/1200404861959819274/1213454042181664848/logo_unede.png?ex=65f58824&is=65e31324&hm=134fb04c959d122d4932de9a9b5dab5db8ef6621563685d5ff4962cf314bc47c')
            embed.set_footer(text='Made By iNinjaOP')
            message = await channel.send(embed=embed)
            message_id = message.id
        prev_player_count = player_count

# Event handler for bot startup
@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

    # Set the bot's presence to "Made By iNinjaOP"
    await client.change_presence(activity=discord.Game(name='Made By iNinjaOP'))

    # Delete previous message if it exists
    channel = client.get_channel(1201058767488430150)  # Replace with your channel ID
    async for msg in channel.history(limit=200):
        if msg.author == client.user:
            await msg.delete()

    # Start updating player count loop
    update_player_count.start()

# Run the Discord bot
client.run(TOKEN)

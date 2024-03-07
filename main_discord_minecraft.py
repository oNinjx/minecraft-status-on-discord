import discord
from discord.ext import tasks
import requests

# Discord bot token
TOKEN = 'MTIxNTE1NTI2NTU5OTU3MDAxMA.GlPz-i.sPMAKkM3VTBD6lgPU99zJZa6nL_qp4n-LQEYGU'

# Minecraft server IP and port
MINECRAFT_SERVER_IP = 'play.htmc.one'
MINECRAFT_SERVER_PORT = 25662

# Initialize Discord client
client = discord.Client(intents=discord.Intents.default())

# Variable to store the previous player count
prev_player_count = 0
message = None

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

# Update Discord channel with player count and server status
@tasks.loop(seconds=30)  # Update every 30 seconds
async def update_player_count():
    global prev_player_count, message
    status, player_count = get_server_info()

    # If player count has changed or server status has changed, update Discord message
    if player_count != prev_player_count or (message and message.embeds[0].fields[0].value != status):
        if message:
            await message.delete()  # Delete previous message
        channel = client.get_channel(1201058767488430150)  # Replace with your channel ID
        embed = discord.Embed(title='Hometown Network', color=discord.Color.green() if 'ONLINE' in status else discord.Color.red())
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
        prev_player_count = player_count

# Event handler for bot startup
@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

    # Delete previous message if it exists
    channel = client.get_channel(1201058767488430150)  # Replace with your channel ID
    async for msg in channel.history(limit=200):
        if msg.author == client.user:
            await msg.delete()

    # Start updating player count loop
    update_player_count.start()

# Run the Discord bot
client.run(TOKEN)

import discord

# Discord bot setup
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Configuration
DISCORD_CHANNEL_ID = 1353667776111312926  # Replace with your channel ID

# Discord bot events
@client.event
async def on_ready():
    print(f'Bot logged in as {client.user}')
    channel = client.get_channel(DISCORD_CHANNEL_ID)
    if channel:
        await channel.send("Bot started successfully! Testing Discord connection.")
    else:
        print("Channel not found! Check DISCORD_CHANNEL_ID.")

# Start the bot
print("Starting bot with debug log...")
client.run(os.getenv('DISCORD_TOKEN'))

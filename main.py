import discord
from discord.ext import tasks
import requests
from bs4 import BeautifulSoup
import json
import os
import asyncio
import aiohttp

# Discord bot setup
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Configuration
WEBSITE_URL = "https://withhive.com/notice/game/2409"  # MLB Perfect Inning notices
DISCORD_CHANNEL_ID = 1353667776111312926  # Replace with your channel ID
CHECK_INTERVAL = 60  # Check every minute (for testing)
DATA_FILE = "seen_posts.json"  # File to store seen post IDs

# Load or initialize seen posts
def load_seen_posts():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return []

def save_seen_posts(posts):
    with open(DATA_FILE, 'w') as f:
        json.dump(posts, f)

# Scrape the website
def scrape_website():
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124'}
        response = requests.get(WEBSITE_URL, timeout=10, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        posts = soup.find_all('article')  # Find all notice articles
        new_posts = []
        save_seen_posts([])  # Reset seen posts for testing
        seen_posts = load_seen_posts()

        for post in posts:
            link_elem = post.find('a')
            if not link_elem or 'href' not in link_elem.attrs:
                continue
            title_elem = link_elem.find('strong')
            date_elem = link_elem.find('time')
            if not title_elem or not date_elem:
                continue
            title = title_elem.text.strip()
            relative_link = link_elem['href']  # e.g., /notice/game/2409/13961
            link = f"https://withhive.com{relative_link}"  # Full URL
            post_id = relative_link  # Use relative link as unique ID
            date = date_elem.text.strip()  # e.g., 04-24-2025

            if post_id not in seen_posts:
                new_posts.append({'title': title, 'link': link, 'id': post_id, 'date': date})
                seen_posts.append(post_id)

        save_seen_posts(seen_posts)
        print(f"Found {len(posts)} posts, {len(new_posts)} new.")
        return new_posts
    except Exception as e:
        print(f"Error scraping website: {e}")
        return []

# Async function to post to Discord
async def post_to_discord(new_posts):
    channel = client.get_channel(DISCORD_CHANNEL_ID)
    if not channel:
        print("Channel not found!")
        return
    for post in new_posts:
        message = f"New notice: {post['title']}\nLink: {post['link']}\nDate: {post['date']}"
        await channel.send(message)
        print(f"Posted: {post['title']}")

# Periodic check (outside Discord events)
async def periodic_check():
    while True:
        print("Periodic check triggered...")
        if client.is_ready():
            new_posts = scrape_website()
            await post_to_discord(new_posts)
        else:
            print("Bot not ready yet, waiting...")
        await asyncio.sleep(CHECK_INTERVAL)

# Discord bot events
@client.event
async def on_ready():
    print(f'Bot logged in as {client.user}')
    channel = client.get_channel(DISCORD_CHANNEL_ID)
    if channel:
        await channel.send("Bot started successfully! Testing Discord connection.")
    else:
        print("Channel not found! Check DISCORD_CHANNEL_ID.")

# Main function to run both Discord bot and periodic check
async def main():
    # Start the periodic check in the background
    asyncio.create_task(periodic_check())
    # Start the Discord bot
    await client.start(os.getenv('DISCORD_TOKEN'))

# Run the bot
if __name__ == "__main__":
    print("Starting bot and initial scrape...")
    # Initial scrape before Discord bot fully starts
    new_posts = scrape_website()
    # Run the main async loop
    asyncio.run(main())

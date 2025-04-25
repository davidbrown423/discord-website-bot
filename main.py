import discord
from discord.ext import tasks
import json
import os
import asyncio
from playwright.async_api import async_playwright

# Discord bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)

# Configuration
CHANNEL_ID = 1353667776111312926  # Replace with your channel ID
CHECK_INTERVAL = 60  # Check every minute (for testing)
DATA_FILE = "last_post.json"  # File to store last seen post ID

# Load or initialize last post ID
def load_last_post_id():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f).get("id", "")
    return ""

def save_last_post_id(post_id):
    with open(DATA_FILE, 'w') as f:
        json.dump({"id": post_id}, f)

# Fetch latest post using Playwright
async def fetch_latest_post():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://withhive.com/notice/game/2409", timeout=60000)

        # Wait for posts to load
        await page.wait_for_selector("ul.board_list > li", timeout=10000)
        posts = await page.query_selector_all("ul.board_list > li")

        results = []

        for post in posts:
            try:
                post_id = await post.get_attribute("data-id")
                title_elem = await post.query_selector(".title")  # Updated selector
                date_elem = await post.query_selector(".date")    # Updated selector

                if title_elem is None or date_elem is None:
                    print(f"⚠️ Skipping post {post_id}: Missing title or date element")
                    continue

                title = await title_elem.inner_text()
                date_str = await date_elem.inner_text()
                post_url = f"https://withhive.com/notice/2409/{post_id}"

                # Format for Discord
                results.append({
                    "id": post_id,
                    "title": title.strip(),
                    "date": date_str.strip(),
                    "url": post_url
                })
            except Exception as e:
                print(f"⚠️ Skipping post due to error: {e}")
                continue

        await browser.close()
        return results

# Periodic check for new posts
@tasks.loop(seconds=CHECK_INTERVAL)
async def check_for_new_post():
    print("🔁 Checking for new Hive notices...")
    last_seen_id = load_last_post_id()
    posts = await fetch_latest_post()

    if not posts:
        print("📭 No posts found.")
        return

    latest = posts[0]  # Get the most recent post
    if latest["id"] != last_seen_id:
        print(f"🆕 New post found: {latest['title']}")
        save_last_post_id(latest['id'])

        channel = bot.get_channel(CHANNEL_ID)
        if channel:
            message = f"**{latest['title']}**\n{latest['url']}"
            await channel.send(message, allowed_mentions=discord.AllowedMentions.none())
        else:
            print("⚠️ Discord channel not found.")
    else:
        print("✅ No new posts.")

# Discord bot events
@bot.event
async def on_ready():
    print(f'Bot logged in as {bot.user}')
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.send("Bot started successfully! Testing Discord connection.")
    else:
        print("Channel not found! Check CHANNEL_ID.")
    check_for_new_post.start()  # Start the periodic check

# Run the bot
if __name__ == "__main__":
    print("Starting bot...")
    bot.run(os.getenv('DISCORD_TOKEN'))

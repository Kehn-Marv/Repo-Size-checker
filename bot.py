import os
import re
import requests
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure requests session with automatic retries for 504 errors
session = requests.Session()
retry = Retry(total=3, backoff_factor=1, status_forcelist=[502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retry))

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

def format_size(size_kb: int) -> str:
    """Format size from KB to MB and GB"""
    size_mb = size_kb / 1024
    size_gb = size_mb / 1024
    
    return (
        f"• *{size_kb:,.0f} KB*\n"
        f"• *{size_mb:,.2f} MB*\n"
        f"• *{size_gb:,.2f} GB*"
    )

def extract_repo_info(url: str) -> tuple[str, str] | None:
    """Extract owner and repo from a GitHub URL"""
    # Pattern to match github.com/owner/repo ignoring queries, hashes, or sub-paths
    pattern = r"github\.com/([^/]+)/([^/?#]+)"
    match = re.search(pattern, url)
    if match:
        owner = match.group(1)
        repo = match.group(2)
        # Strip .git if it was included
        if repo.endswith(".git"):
            repo = repo[:-4]
        return owner, repo
    return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    welcome_message = (
        "👋 Hello! I am a GitHub Repo Size Checker bot.\n\n"
        "Just send me a GitHub repository link (e.g., `https://github.com/torvalds/linux`) "
        "and I'll tell you its exact size in KB, MB, and GB."
    )
    await update.message.reply_text(welcome_message)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming messages and check for GitHub URLs."""
    text = update.message.text
    
    # Check if there is a github link
    if "github.com/" not in text:
        await update.message.reply_text("❌ That doesn't look like a GitHub link. Please send a valid GitHub repository URL (e.g., `https://github.com/torvalds/linux`).")
        return

    repo_info = extract_repo_info(text.strip())
    if not repo_info:
        await update.message.reply_text("❌ Could not extract a valid repository name from that URL. Please make sure it's a valid GitHub repo URL.")
        return

    owner, repo = repo_info
    
    # Send typing action
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    # Fetch data from GitHub API
    api_url = f"https://api.github.com/repos/{owner}/{repo}"
    
    try:
        response = session.get(api_url)
        response.raise_for_status()
        data = response.json()
        
        size_kb = data.get("size")
        if size_kb is None:
            await update.message.reply_text("❌ The repository exists, but its size is not available.")
            return
            
        default_branch = data.get("default_branch", "main")
        
        # Calculate snapshot size
        snapshot_kb = None
        tree_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{default_branch}?recursive=1"
        try:
            tree_response = session.get(tree_url)
            tree_response.raise_for_status()
            tree_data = tree_response.json()
            tree_items = tree_data.get("tree", [])
            # Sum sizes of all blob objects in bytes, then convert to KB
            snapshot_bytes = sum(item.get("size", 0) for item in tree_items if item.get("type") == "blob")
            snapshot_kb = snapshot_bytes / 1024
        except Exception as e:
            logger.warning(f"Could not fetch snapshot size for {owner}/{repo}: {e}")
            
        reply_text = f"*{owner}/{repo}*\n\n"
        if snapshot_kb is not None:
            reply_text += f"📦 *Snapshot Size (ZIP / Shallow Clone)*\n{format_size(snapshot_kb)}\n\n"
            
        reply_text += f"📚 *Full Repository Size (Standard Clone)*\n{format_size(size_kb)}"
        
        reply_text += (
            "\n\n---\n"
            "💡 *Understanding these sizes:*\n\n"
            "• Snapshot Size: This is the raw, uncompressed size of the files. This is exactly what you get when you download the repo as a ZIP or do a shallow clone.\n\n"
            "• Full Repository Size: This is how much space the repository (and all its history) takes up on GitHub's servers. GitHub stores this using 'bare packfiles' which are heavily compressed. A standard `git clone` downloads this entire history.\n\n"
            "(Note: The .zip file itself might appear slightly smaller because it's compressed, but the bot calculates the true, uncompressed size of the code you are getting!)"
        )
        
        await update.message.reply_markdown(reply_text)
        
    except requests.exceptions.HTTPError as e:
        if response.status_code == 404:
             await update.message.reply_text("❌ Repository not found. Please double-check your link. If the repository is private, I cannot access it.")
        elif response.status_code == 403:
             await update.message.reply_text("❌ Rate limit exceeded for GitHub API.")
        else:
             await update.message.reply_text(f"❌ Could not check the repo size. HTTP Error: {response.status_code}")
    except Exception as e:
        logger.error(f"Error processing URL {text}: {e}")
        await update.message.reply_text("❌ An unexpected error occurred while processing your request. Please try again.")

import sys

def main() -> None:
    """Start the bot."""
    # Fetch token dynamically so it picks up Fly.io secrets at runtime
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not bot_token or bot_token == "your_bot_token_here":
        print("ERROR: Please set your TELEGRAM_BOT_TOKEN securely via fly secrets")
        sys.exit(1)  # Important: Exit with code 1 so Fly.io knows it failed and restarts it

    application = Application.builder().token(bot_token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run the bot until the user presses Ctrl-C
    print("Bot is running! Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()

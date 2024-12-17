import os
import logging
import threading
import requests
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from config import Config  # Ensure you have this file for your bot's config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Pyrogram Client
bot = Client(
    "catbox_uploader",
    bot_token=Config.BOT_TOKEN,
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
)

# Initialize Flask App
flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    """Health check route for Flask."""
    return "Flask app is running!"

def run_flask():
    """Run Flask app in a separate thread."""
    flask_app.run(host="0.0.0.0", port=8000)

def upload_file(file_path):
    """Upload the file to Catbox."""
    url = "https://catbox.moe/user/api.php"
    data = {"reqtype": "fileupload", "json": "true"}
    
    try:
        with open(file_path, "rb") as file:
            files = {"fileToUpload": file}
            response = requests.post(url, data=data, files=files)
        
        logger.info("Response from Catbox: %s", response.text)

        if response.status_code == 200:
            try:
                response_json = response.json()
                return True, response_json.get("url", "")
            except ValueError:
                return True, response.text.strip()
        else:
            return False, f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return False, f"Exception occurred: {str(e)}"

@bot.on_message(filters.command("start"))
async def start_command(_, message: Message) -> None:
    """Handles /start command."""
    welcome_text = (
        "👋 Welcome to the Media Uploader Bot!\n\n"
        "Send me a photo or video to upload!"
    )
    keyboard = [[InlineKeyboardButton("Join", url="https://t.me/BABY09_WORLD")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await message.reply_text(welcome_text, reply_markup=reply_markup)

@bot.on_message((filters.photo | filters.video) & filters.incoming & filters.private)
async def media_handler(_, message: Message) -> None:
    """Handles incoming photo or video messages by uploading to Catbox.moe."""
    media = message.photo or message.video
    file_size = media.file_size if media else 0

    if file_size > 200 * 1024 * 1024:  # File size limit (200MB)
        return await message.reply_text("Pʟᴇᴀsᴇ ᴘʀᴏᠧᴠɪᴅᴇ ᴀ ᴍᴇᴅɪᴀ ғɪʟᴇ ᴜɴᴅᴇʀ 200MB.")

    try:
        text = await message.reply("Processing...")

        # Download media
        local_path = await message.download()
        await text.edit_text("Uploading 100%...")

        # Upload file
        success, upload_url = upload_file(local_path)

        if success:
            await text.edit_text(
                f"❍ | [ʜᴏʟᴅ ᴛʜᴇ ʟɪɴᴋ]({upload_url})",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "❍ ᴄʀᴇᴀᴛᴇ ʙʏ ˹ ʙᴀʙʏ-ᴍᴜsɪᴄ ™˼𓅂",
                                url="https://t.me/BABY09_WORLD",
                            )
                        ]
                    ]
                ),
            )
        else:
            await text.edit_text("❍ ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ ᴡʜɪʟᴇ ᴜᴘʟᴏᴀᴅɪɴɢ.")

        os.remove(local_path)  # Clean up local file
    except Exception as e:
        await message.reply_text(f"An error occurred: {str(e)}")


# Main entry point
if __name__ == "__main__":
    # Start Flask in a separate thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Run the bot in the main thread
    bot.run()

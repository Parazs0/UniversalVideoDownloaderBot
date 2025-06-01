import os
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from flask import Flask, request
from dotenv import load_dotenv
import yt_dlp

# Load BOT_TOKEN from .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Logging
logging.basicConfig(level=logging.INFO)

# Flask App for Render
app = Flask(__name__)

# Telegram Updater & Dispatcher
updater = Updater(BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Video extract function
def get_direct_video_url(video_page_url):
    ydl_opts = {
    'quiet': True,
    'skip_download': True,
    'format': 'best[ext=mp4]/best',
    'nocheckcertificate': True,
}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_page_url, download=False)
        video_url = info.get('url')
        if not video_url and 'formats' in info:
            formats = info['formats']
            mp4_formats = [f for f in formats if f.get('ext') == 'mp4']
            if mp4_formats:
                best_mp4 = sorted(mp4_formats, key=lambda x: x.get('height', 0), reverse=True)[0]
                video_url = best_mp4.get('url')
        return video_url

# Handlers
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "🎬 Welcome! Send a YouTube, Twitter, Instagram, or Facebook video link to get the direct video URL."
    )

def handle_message(update: Update, context: CallbackContext):
    url = update.message.text.strip()
    supported_sites = ["youtube.com", "youtu.be", "twitter.com", "x.com", "instagram.com", "facebook.com"]
    if any(site in url.lower() for site in supported_sites):
        update.message.reply_text("🔄 Fetching direct video URL, please wait...")
        try:
            direct_url = get_direct_video_url(url)
            if direct_url:
                update.message.reply_text(f"✅ Here is your direct video URL:\n\n{direct_url}")
            else:
                update.message.reply_text("⚠️ Sorry, could not extract a direct video URL.")
        except Exception as e:
            update.message.reply_text(f"❌ Error: {str(e)}")
    else:
        update.message.reply_text("❌ Unsupported URL. Please send a YouTube, Instagram, Twitter, or Facebook link.")

# Register handlers
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

# Flask routes
@app.route('/')
def home():
    return "✅ Bot is alive!"

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), updater.bot)
    dispatcher.process_update(update)
    return "ok"

# Run app
if __name__ == "__main__":
    PORT = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=PORT)

import logging
import requests
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Load environment variables
load_dotenv()

# ===== CONFIG =====
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")
MODEL_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2"

# Check if tokens are loaded
if not TELEGRAM_BOT_TOKEN or not HF_TOKEN:
    raise ValueError("Missing required environment variables. Please check your .env file.")

headers = {"Authorization": f"Bearer {HF_TOKEN}"}

# ===== LOGGING =====
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    level=logging.INFO)

# ===== IMAGE GENERATION =====
def generate_image(prompt: str):
    payload = {"inputs": prompt}
    response = requests.post(MODEL_URL, headers=headers, json=payload)
    if response.status_code != 200:
        print("Error:", response.text)
        return None
    return response.content

# ===== BOT COMMANDS =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello, I am your free AI image bot. Use /generate <prompt>")

async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Please provide a prompt.\nExample: /generate a cat in armor")
        return

    prompt = " ".join(context.args)
    await update.message.reply_text(f"🎨 Generating: {prompt} ... please wait...")

    image_bytes = generate_image(prompt)

    if image_bytes:
        await update.message.reply_photo(photo=image_bytes)
    else:
        await update.message.reply_text("⚠️ Failed to generate image. Try again later.")

# ===== MAIN =====
def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("generate", generate))
    app.run_polling()

if __name__ == "__main__":
    main()
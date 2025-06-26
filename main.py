from dotenv import load_dotenv
load_dotenv()

import os
import re
import threading
import logging
from fpdf import FPDF
from flask import Flask, send_from_directory, request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    ContextTypes,
)

# 🔐 Environment Variables
TELEGRAM_TOKEN = "7933453858:AAEZAHEZ6PbsEM3ZGVKaX1AGJFoPodF8A8Q"

print("DEBUG TELEGRAM_TOKEN:", TELEGRAM_TOKEN)

if not TELEGRAM_TOKEN:
    raise ValueError("❌ TELEGRAM_TOKEN not found in .env")

# 🔥 Flask Web Server
app = Flask(__name__, static_folder='static')

# 🧠 States
NAME, EMAIL, PHONE, EDUCATION, SKILLS, SUMMARY = range(6)
user_data = {}

# 🌐 Telegram Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("/start triggered by", update.effective_user.username)
    await update.message.reply_text("Welcome to JobGenieBot! Let's build your ATS-friendly resume.\nWhat is your full name?")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data['name'] = update.message.text
    await update.message.reply_text("Great! What's your email?")
    return EMAIL

async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data['email'] = update.message.text
    await update.message.reply_text("Your phone number?")
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data['phone'] = update.message.text
    await update.message.reply_text("Mention your education details:")
    return EDUCATION

async def get_education(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data['education'] = update.message.text
    await update.message.reply_text("List your top skills (comma-separated):")
    return SKILLS

async def get_skills(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data['skills'] = update.message.text
    await update.message.reply_text("Write a 2–3 line professional summary:")
    return SUMMARY

async def get_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data['summary'] = update.message.text
    name = user_data['name']
    email = user_data['email']
    phone = user_data['phone']
    education = user_data['education']
    skills = user_data['skills']
    summary = user_data['summary']

    # 📄 Create PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=name, ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Email: {email} | Phone: {phone}", ln=True)
    pdf.multi_cell(200, 10, txt=f"\nSummary:\n{summary}")
    pdf.multi_cell(200, 10, txt=f"\nEducation:\n{education}")
    pdf.multi_cell(200, 10, txt=f"\nSkills:\n{skills}")

    filename = f"static/{name.replace(' ', '_')}_Resume.pdf"
    pdf.output(filename)

    link = f"http://localhost:5000/download?file={name.replace(' ', '_')}_Resume.pdf"
    await update.message.reply_text(f"✅ Your resume is ready!\nDownload it here: {link}")

    await update.message.reply_text("\ud83d\ude80 *Sponsored*: Want job-ready courses? Check out Internshala's certification programs!\nVisit: https://internshala.com", parse_mode='Markdown')
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Resume creation cancelled.")
    return ConversationHandler.END

# 🏡 Flask Route
@app.route("/download")
def download():
    filename = request.args.get("file")
    return send_from_directory("static", filename, as_attachment=True)

# 🚀 Launch Everything
def start_flask():
    app.run(host="0.0.0.0", port=5000)

def main():
    app_telegram = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_email)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            EDUCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_education)],
            SKILLS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_skills)],
            SUMMARY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_summary)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app_telegram.add_handler(conv_handler)

    # Start Flask in background
    threading.Thread(target=start_flask, daemon=True).start()

    # Run Telegram bot in main thread
    app_telegram.run_polling()

if __name__ == "__main__":
    main()

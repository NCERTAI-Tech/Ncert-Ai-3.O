import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from openai import OpenAI

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is missing.")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is missing.")

client = OpenAI(api_key=OPENAI_API_KEY)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

SYSTEM_PROMPT = """
You are ncertify.ai, a study assistant for students.

Your main focus is:
- NCERT
- JKBOSE
- Class 11 and Class 12
- Physics
- Chemistry
- Botany
- Zoology
- NEET-oriented concepts when relevant

Answer clearly, accurately, and simply.

Normally keep answers short: around 1-3 sentences or a few clean lines.
For difficult concepts, explain them step-by-step.
Do not add unnecessary headings, filler, repetition, or long textbook-style explanations.
Give an example only when it actually helps.

If the student asks a school/board question, prioritize NCERT and JKBOSE-level explanations.
If you are unsure about a fact, say so instead of inventing an answer.

Your name is ncertify.ai.
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hey! I’m ncertify.ai 📚\n\n"
        "Ask me anything from NCERT Class 11–12 Physics, Chemistry, Botany, or Zoology."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Send me any NCERT study question.\n\n"
        "I can help with Physics, Chemistry, Botany, and Zoology for Class 11–12."
    )


async def answer_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    question = update.message.text.strip()

    if not question:
        return

    try:
        response = client.responses.create(
            model="gpt-5-mini",
            instructions=SYSTEM_PROMPT,
            input=question
        )

        answer = response.output_text.strip()

        if not answer:
            answer = "Sorry, I couldn't generate an answer. Try asking the question again."

        await update.message.reply_text(answer)

    except Exception as e:
        logging.error("OpenAI error: %s", e)
        await update.message.reply_text(
            "Sorry, something went wrong. Please try again."
        )


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, answer_question)
    )

    print("ncertify.ai is running...")
    app.run_polling()


if __name__ == "__main__":
    main()

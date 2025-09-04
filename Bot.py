import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# 🔑 BOT TOKENNI shu yerga yozing
TOKEN = "8292790285:AAGZkhTopFcUkE0cTlB52HDOij7s8oCkI7E"

# --- Flask server ---
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Bot is running on PythonAnywhere!"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

# --- Darslar ro'yxati ---
LESSONS = [
    ("Alphabet (Alifbo)", "A – ey\nB – bi:\nC – si:\nD – di:\nE – i:"),
    ("Ranglar", "🔴 Red – Qizil\n🔵 Blue – Ko‘k\n🟢 Green – Yashil\n🟡 Yellow – Sariq"),
    ("Raqamlar", "1 – one\n2 – two\n3 – three\n4 – four\n5 – five"),
    ("Hayvonlar", "🐶 Dog – It\n🐱 Cat – Mushuk\n🐭 Mouse – Sichqon\n🐰 Rabbit – Quyon"),
    ("Salomlashish", "Hello! – Salom!\nGoodbye! – Xayr!\nThank you! – Rahmat!"),
]

# --- Quiz savollar ---
QUIZ = [
    {"uz": "🔵 Bu qaysi rang?", "en": "Blue", "options": ["Red", "Blue", "Green"]},
    {"uz": "🐶 Bu nima?", "en": "Dog", "options": ["Dog", "Cat", "Mouse"]},
    {"uz": "2 soni inglizchada?", "en": "Two", "options": ["One", "Two", "Three"]},
    {"uz": "👋 Hello! tarjimasi?", "en": "Salom", "options": ["Salom", "Rahmat", "Xayr"]},
]

# --- /start komandasi ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [
        [InlineKeyboardButton("📚 Darslarni boshlash", callback_data="lesson:0")],
        [InlineKeyboardButton("🧠 Viktorina", callback_data="quiz:0")],
        [InlineKeyboardButton("ℹ️ Yordam", callback_data="help")]
    ]
    await update.message.reply_text(
        "👋 Assalomu alaykum!\n"
        "Men sizga ingliz tilini 0 dan o‘rgataman.\n\n"
        "Quyidagilardan birini tanlang:",
        reply_markup=InlineKeyboardMarkup(kb)
    )

# --- Darslarni ko‘rsatish ---
async def show_lesson(update: Update, context: ContextTypes.DEFAULT_TYPE, idx: int):
    title, body = LESSONS[idx]
    kb = []
    if idx + 1 < len(LESSONS):
        kb.append([InlineKeyboardButton("▶️ Keyingi dars", callback_data=f"lesson:{idx+1}")])
    else:
        kb.append([InlineKeyboardButton("🧠 Viktorina", callback_data="quiz:0")])
    await update.callback_query.edit_message_text(
        f"📚 *{title}*\n\n{body}", parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(kb)
    )

# --- Quizni yuborish ---
async def send_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE, idx: int):
    if idx >= len(QUIZ):
        await update.callback_query.edit_message_text("🎉 Viktorina tugadi! Zo‘r ishladingiz 👏")
        return
    item = QUIZ[idx]
    buttons = [[InlineKeyboardButton(opt, callback_data=f"ans:{idx}:{opt}")] for opt in item["options"]]
    await update.callback_query.edit_message_text(
        f"🧠 Savol {idx+1}:\n{item['uz']}",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# --- Tugmalarni boshqarish ---
async def on_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    data = q.data
    await q.answer()

    # Darslar
    if data.startswith("lesson:"):
        idx = int(data.split(":")[1])
        await show_lesson(update, context, idx)

    # Quiz
    elif data.startswith("quiz:"):
        idx = int(data.split(":")[1])
        await send_quiz(update, context, idx)

    # Javob
    elif data.startswith("ans:"):
        _, idx, ans = data.split(":")
        idx = int(idx)
        correct = QUIZ[idx]["en"]
        if ans == correct:
            await q.edit_message_text(f"✅ To‘g‘ri! Javob: {correct}")
        else:
            await q.edit_message_text(f"❌ Noto‘g‘ri. To‘g‘ri javob: {correct}")
        # Keyingi savol
        if idx + 1 < len(QUIZ):
            await send_quiz(update, context, idx + 1)
        else:
            await q.message.reply_text("🎉 Viktorina tugadi! 👏 Yaxshi ishladingiz.")

    # Yordam
    elif data == "help":
        await q.edit_message_text(
            "📖 Buyruqlar:\n"
            "/start – Menyu\n"
            "📚 Darslarni ketma-ket o‘qish\n"
            "🧠 Viktorina orqali o‘yin shaklida o‘rganish"
        )

# --- Asosiy funksiya ---
def run_bot():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(on_button))
    print("🤖 Bot ishlayapti...")
    app.run_polling()

if __name__ == "__main__":
    # Botni boshqa oqimda ishga tushiramiz
    threading.Thread(target=run_bot).start()
    # Flaskni ham ishga tushiramiz
    run_flask()

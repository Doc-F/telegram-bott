import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler, CallbackQueryHandler

# ADMIN ID (bu yerga o'z Telegram user ID raqamingizni yozing)
ADMIN_ID = 1642006814  # <-- Buni o'zingiznikiga almashtiring!

# Har bir foydalanuvchi uchun ID ni saqlash
user_message_map = {}

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("📨 Savol yo‘llash", callback_data="ask_question")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Savolingizni yuborish uchun tugmani bosing:", reply_markup=reply_markup)

# Callback tugmasi
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "ask_question":
        await query.message.reply_text("Savolingizni yuboring (matn, rasm, ovoz, fayl, va boshqalar)")
        context.user_data["awaiting_question"] = True

# Xabarlarni ushlash
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_question", False):
        user_id = update.message.from_user.id
        username = update.message.from_user.username or update.message.from_user.first_name
        user_message_map[update.message.message_id] = user_id

        # Forward to admin
        caption = f"✉️ Yangi savol\n👤 @{username} (ID: {user_id})"
        sent_msg = await update.message.forward(chat_id=ADMIN_ID)
        keyboard = [[InlineKeyboardButton("✏️ Javob berish", callback_data=f"reply_{sent_msg.message_id}")]]
        await context.bot.send_message(chat_id=ADMIN_ID, text=caption, reply_markup=InlineKeyboardMarkup(keyboard))

        context.user_data["awaiting_question"] = False
    elif update.message.chat_id == ADMIN_ID:
        # Javob yozish rejimida
        reply_to_id = context.user_data.get("reply_to")
        if reply_to_id:
            await context.bot.send_message(chat_id=reply_to_id, text=f"👨‍⚕️ Admin javobi:\n{update.message.text}")
            context.user_data["reply_to"] = None
        else:
            await update.message.reply_text("Javob berish uchun tugmani bosing.")

# Javob berish tugmasi bosilganda
async def handle_reply_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("reply_"):
        msg_id = int(query.data.split("_")[1])
        user_id = user_message_map.get(msg_id)

        if user_id:
            context.user_data["reply_to"] = user_id
            await query.message.reply_text("Endi foydalanuvchiga javob yozishingiz mumkin.")
        else:
            await query.message.reply_text("Foydalanuvchini topib bo‘lmadi.")

# Asosiy funksiya
def main():
    TOKEN = os.environ.get("BOT_TOKEN")  # Render.com'da token muhit o'zgaruvchisi sifatida beriladi
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(CallbackQueryHandler(handle_reply_button, pattern="^reply_"))
    app.add_handler(MessageHandler(filters.ALL, handle_message))

    print("Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()

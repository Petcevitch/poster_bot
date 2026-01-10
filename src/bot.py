import logging
from telegram import Update, InputFile, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    MessageHandler, filters, ConversationHandler, CallbackQueryHandler
)
from config import BOT_TOKEN, FONT_PATH
from image_utils import overlay_text_on_image

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Этапы разговора
(
    TEXT_A, COLOR_CHOICE_A,
    TEXT_B_CHOICE, TEXT_B, COLOR_CHOICE_B,
    PHOTO
) = range(6)

# Готовые варианты текста нижнего текста
ROUND_CHOICES = [
    "ПЕРВЫЙ РАУНД",
    "ВТОРОЙ РАУНД ВЕРХ",
    "ВТОРОЙ РАУНД НИЗ",
    "ТРЕТИЙ РАУНД НИЗ",
    "ЧЕТВЕРТЬФИНАЛ",
    "ПОЛУФИНАЛ",
    "ФИНАЛ",
    "СВОЙ ТЕКСТ"
]

COLOR_CHOICES = [
    ("Красный", "red"),
    ("Жёлтый", "yellow"),
    ("Зелёный", "green"),
    ("Коричневый", "brown"),
    ("Синий", "blue"),
    ("Розовый", "pink"),
    ("Чёрный", "black")
]

# -------------------
# /start
# -------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введите текст для верхней надписи:")
    return TEXT_A

# -------------------
# Верхний текст
# -------------------
async def get_text_a(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["text_a"] = update.message.text
    # выбор цвета плашки верхнего текста
    keyboard = []
    for i in range(0, len(COLOR_CHOICES), 2):
        row = [InlineKeyboardButton(COLOR_CHOICES[i][0], callback_data=COLOR_CHOICES[i][1])]
        if i+1 < len(COLOR_CHOICES):
            row.append(InlineKeyboardButton(COLOR_CHOICES[i+1][0], callback_data=COLOR_CHOICES[i+1][1]))
        keyboard.append(row)
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите цвет плашки для верхнего текста:", reply_markup=reply_markup)
    return COLOR_CHOICE_A

async def color_choice_a_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["bg_color_a"] = query.data

    # Далее нижний текст
    keyboard = []
    for i in range(0, len(ROUND_CHOICES), 2):
        row = [InlineKeyboardButton(ROUND_CHOICES[i], callback_data=ROUND_CHOICES[i])]
        if i+1 < len(ROUND_CHOICES):
            row.append(InlineKeyboardButton(ROUND_CHOICES[i+1], callback_data=ROUND_CHOICES[i+1]))
        keyboard.append(row)
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("Выберите текст для нижней надписи:", reply_markup=reply_markup)
    return TEXT_B_CHOICE

# -------------------
# Нижний текст
# -------------------
async def text_b_choice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choice = query.data
    if choice == "СВОЙ ТЕКСТ":
        await query.message.reply_text("Введите свой текст для нижней надписи:")
        return TEXT_B
    else:
        context.user_data["text_b"] = choice
        await show_color_choice_b(update=query, context=context)
        return COLOR_CHOICE_B

async def get_text_b(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["text_b"] = update.message.text
    await show_color_choice_b(update=update, context=context)
    return COLOR_CHOICE_B

# -------------------
# Выбор цвета нижней плашки
# -------------------
async def show_color_choice_b(update, context):
    keyboard = []
    for i in range(0, len(COLOR_CHOICES), 2):
        row = [InlineKeyboardButton(COLOR_CHOICES[i][0], callback_data=COLOR_CHOICES[i][1])]
        if i+1 < len(COLOR_CHOICES):
            row.append(InlineKeyboardButton(COLOR_CHOICES[i+1][0], callback_data=COLOR_CHOICES[i+1][1]))
        keyboard.append(row)
    reply_markup = InlineKeyboardMarkup(keyboard)
    if hasattr(update, "message"):
        await update.message.reply_text("Выберите цвет плашки для нижнего текста:", reply_markup=reply_markup)
    else:
        await update.edit_message_text("Выберите цвет плашки для нижнего текста:", reply_markup=reply_markup)

async def color_choice_b_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["bg_color_b"] = query.data
    await query.message.reply_text("Теперь отправьте фото для генерации постера:")
    return PHOTO

# -------------------
# Получение фото
# -------------------
async def get_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_file = await update.message.photo[-1].get_file()
    photo_path = "temp.jpg"
    await photo_file.download_to_drive(photo_path)

    text_a = context.user_data.get("text_a", "")
    text_b = context.user_data.get("text_b", "")
    bg_color_a = context.user_data.get("bg_color_a", None)
    bg_color_b = context.user_data.get("bg_color_b", None)

    image_bytes = overlay_text_on_image(
        photo_path,
        text_a,
        text_b,
        font_path=FONT_PATH,
        font_size_a=50,
        font_size_b=100,
        bg_color_a=bg_color_a,
        bg_color_b=bg_color_b,
        padding=35
    )

    await update.message.reply_photo(photo=InputFile(image_bytes, filename="poster.png"))
    return ConversationHandler.END

# -------------------
# /cancel
# -------------------
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Создание постера отменено.")
    return ConversationHandler.END

# -------------------
# main
# -------------------
def main():
    if not BOT_TOKEN:
        logger.error("Не найден токен бота. Добавьте BOT_TOKEN в .env")
        return

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            TEXT_A: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_text_a)],
            COLOR_CHOICE_A: [CallbackQueryHandler(color_choice_a_handler)],
            TEXT_B_CHOICE: [CallbackQueryHandler(text_b_choice_handler)],
            TEXT_B: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_text_b)],
            COLOR_CHOICE_B: [CallbackQueryHandler(color_choice_b_handler)],
            PHOTO: [MessageHandler(filters.PHOTO, get_photo)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    logger.info("Бот запущен...")
    app.run_polling()


if __name__ == "__main__":
    main()

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
TEXT_A, TEXT_B, COLOR_CHOICE, PHOTO = range(4)

COLOR_CHOICES = [
    ("Красный", "red"),
    ("Жёлтый", "yellow"),
    ("Зелёный", "green"),
    ("Коричневый", "brown"),
    ("Синий", "blue"),
    ("Розовый", "pink"),
    ("Чёрный", "black")
]

# Стартовый обработчик
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Давай создадим твой постер.\nВведите текст A (вверху):")
    return TEXT_A

# Ввод текста A
async def get_text_a(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["text_a"] = update.message.text
    await update.message.reply_text("Отлично! Теперь введи текст B (внизу):")
    return TEXT_B

# Ввод текста B
async def get_text_b(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["text_b"] = update.message.text

    # Инлайн-кнопки для выбора цвета плашки
    keyboard = []
    for i in range(0, len(COLOR_CHOICES), 2):
        row = [InlineKeyboardButton(COLOR_CHOICES[i][0], callback_data=COLOR_CHOICES[i][1])]
        if i+1 < len(COLOR_CHOICES):
            row.append(InlineKeyboardButton(COLOR_CHOICES[i+1][0], callback_data=COLOR_CHOICES[i+1][1]))
        keyboard.append(row)

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите цвет плашки для нижнего текста:", reply_markup=reply_markup)
    return COLOR_CHOICE

# Обработка выбора цвета
async def color_choice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["bg_color"] = query.data
    await query.edit_message_text(text=f"Выбран цвет: {query.data}")

    # Запрос фото
    await query.message.reply_text("Теперь отправь фото для генерации постера:")
    return PHOTO

# Получение фото и генерация постера
async def get_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_file = await update.message.photo[-1].get_file()
    photo_path = "temp.jpg"
    await photo_file.download_to_drive(photo_path)

    text_a = context.user_data.get("text_a", "Текст сверху")
    text_b = context.user_data.get("text_b", "Текст снизу")
    bg_color = context.user_data.get("bg_color", None)

    from image_utils import overlay_text_on_image
    image_bytes = overlay_text_on_image(
        photo_path,
        text_a,
        text_b,
        font_path=FONT_PATH,
        font_size_a=60,
        font_size_b=100,
        bg_color=bg_color,
        padding=35  # увеличенный отступ
    )

    await update.message.reply_photo(photo=InputFile(image_bytes, filename="poster.png"))
    return ConversationHandler.END

# Команда /cancel
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Создание постера отменено.")
    return ConversationHandler.END

# Основная функция запуска бота
def main():
    if not BOT_TOKEN:
        logger.error("Не найден токен бота. Добавьте BOT_TOKEN в .env")
        return

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            TEXT_A: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_text_a)],
            TEXT_B: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_text_b)],
            COLOR_CHOICE: [CallbackQueryHandler(color_choice_handler)],
            PHOTO: [MessageHandler(filters.PHOTO, get_photo)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)

    logger.info("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()

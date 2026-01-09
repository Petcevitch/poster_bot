import logging
import os
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler
from config import BOT_TOKEN, FONT_PATH
from image_utils import overlay_text_on_image

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Этапы разговора
TEXT_A, TEXT_B, PHOTO = range(3)

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
    await update.message.reply_text("Отправь фото, на которое нужно наложить тексты:")
    return PHOTO

# Получение фото и генерация постера
async def get_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Берем последнее фото
    photo_file = await update.message.photo[-1].get_file()
    photo_path = "temp.jpg"
    
    # Сохраняем на диск
    await photo_file.download_to_drive(photo_path)

    text_a = context.user_data.get("text_a", "Текст сверху")
    text_b = context.user_data.get("text_b", "Текст снизу")

    image_bytes = overlay_text_on_image(photo_path, text_a, text_b, font_path=FONT_PATH)

    await update.message.reply_photo(photo=InputFile(image_bytes, filename="poster.png"))
    return ConversationHandler.END


# Команда /cancel
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Создание постера отменено.")
    return ConversationHandler.END

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
            PHOTO: [MessageHandler(filters.PHOTO, get_photo)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)

    logger.info("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()

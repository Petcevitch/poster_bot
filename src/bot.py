import logging
import asyncio
import nest_asyncio

from telegram import (
    Update,
    InputFile,
    BotCommand,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

from config import BOT_TOKEN, FONT_PATH
from image_utils import overlay_text_on_image

nest_asyncio.apply()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

(TEXT_A, COLOR_A, TEXT_B_CHOICE, TEXT_B, COLOR_B, PHOTO) = range(6)

ROUND_CHOICES = [
    "ПЕРВЫЙ РАУНД",
    "ВТОРОЙ РАУНД ВЕРХ",
    "ВТОРОЙ РАУНД НИЗ",
    "ТРЕТИЙ РАУНД НИЗ",
    "ЧЕТВЕРТЬФИНАЛ",
    "ПОЛУФИНАЛ",
    "ФИНАЛ",
    "СВОЙ ТЕКСТ",
]

COLORS = [
    ("Красный", "red"),
    ("Жёлтый", "yellow"),
    ("Зелёный", "green"),
    ("Коричневый", "brown"),
    ("Синий", "blue"),
    ("Розовый", "pink"),
    ("Чёрный", "black"),
]


# =====================
# /start
# =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Введите верхний текст.\n\n"
        "Если верхняя плашка не нужна — введите:\n"
        "??"
    )
    return TEXT_A


# =====================
# ВЕРХНИЙ ТЕКСТ
# =====================
async def get_text_a(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["text_a"] = update.message.text

    if update.message.text == "??":
        context.user_data["bg_color_a"] = None
        return await ask_text_b(update)

    return await ask_color_a(update)


async def ask_color_a(update):
    keyboard = make_color_keyboard()
    await update.message.reply_text(
        "Выберите цвет плашки для верхнего текста:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return COLOR_A


async def color_a_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["bg_color_a"] = query.data
    return await ask_text_b(query)


# =====================
# НИЖНИЙ ТЕКСТ
# =====================
async def ask_text_b(update):
    keyboard = make_round_keyboard()
    await update.message.reply_text(
        "Выберите текст для нижней надписи:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return TEXT_B_CHOICE


async def text_b_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "СВОЙ ТЕКСТ":
        await query.message.reply_text("Введите текст для нижней надписи:")
        return TEXT_B

    context.user_data["text_b"] = query.data
    return await ask_color_b(query)


async def get_text_b(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["text_b"] = update.message.text
    return await ask_color_b(update)


async def ask_color_b(update):
    keyboard = make_color_keyboard()
    await update.message.reply_text(
        "Выберите цвет плашки для нижнего текста:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return COLOR_B


async def color_b_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["bg_color_b"] = query.data
    await query.message.reply_text("Отправьте фото:")
    return PHOTO


# =====================
# ФОТО
# =====================
async def get_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.photo[-1].get_file()
    path = "temp.jpg"
    await file.download_to_drive(path)

    image = overlay_text_on_image(
        path,
        text_a=context.user_data.get("text_a", ""),
        text_b=context.user_data.get("text_b", ""),
        font_path=FONT_PATH,
        font_size_a=50,
        font_size_b=100,
        bg_color_a=context.user_data.get("bg_color_a"),
        bg_color_b=context.user_data.get("bg_color_b"),
        padding_a=17,
        padding_b=30,
        bg_opacity=180,
    )

    await update.message.reply_photo(
        photo=InputFile(image, filename="poster.png")
    )

    return TEXT_A


# =====================
# HELP
# =====================
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Этот бот создаёт постеры для турниров.\n\n"
        "Порядок работы:\n"
        "1. Введите верхний текст\n"
        "   • или ?? — чтобы скрыть верхнюю плашку\n"
        "2. Выберите цвет верхней плашки\n"
        "3. Выберите или введите нижний текст\n"
        "4. Выберите цвет нижней плашки\n"
        "5. Отправьте фото\n\n"
        "Команды:\n"
        "/start — новый баннер\n"
        "/cancel — отмена\n"
        "/help — помощь"
    )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Создание отменено.")
    return ConversationHandler.END


# =====================
# КЛАВИАТУРЫ
# =====================
def make_color_keyboard():
    rows = []
    for i in range(0, len(COLORS), 2):
        row = [InlineKeyboardButton(COLORS[i][0], callback_data=COLORS[i][1])]
        if i + 1 < len(COLORS):
            row.append(InlineKeyboardButton(COLORS[i + 1][0], callback_data=COLORS[i + 1][1]))
        rows.append(row)
    return rows


def make_round_keyboard():
    rows = []
    for i in range(0, len(ROUND_CHOICES), 2):
        row = [InlineKeyboardButton(ROUND_CHOICES[i], callback_data=ROUND_CHOICES[i])]
        if i + 1 < len(ROUND_CHOICES):
            row.append(InlineKeyboardButton(ROUND_CHOICES[i + 1], callback_data=ROUND_CHOICES[i + 1]))
        rows.append(row)
    return rows


# =====================
# MAIN
# =====================
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    await app.bot.set_my_commands([
        BotCommand("start", "Новый баннер"),
        BotCommand("help", "Помощь"),
        BotCommand("cancel", "Отмена"),
    ])

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            TEXT_A: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_text_a)],
            COLOR_A: [CallbackQueryHandler(color_a_handler)],
            TEXT_B_CHOICE: [CallbackQueryHandler(text_b_choice)],
            TEXT_B: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_text_b)],
            COLOR_B: [CallbackQueryHandler(color_b_handler)],
            PHOTO: [MessageHandler(filters.PHOTO, get_photo)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv)
    app.add_handler(CommandHandler("help", help_cmd))

    logger.info("Бот запущен")
    await app.run_polling()


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())

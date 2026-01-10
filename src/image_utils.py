from PIL import Image, ImageDraw, ImageFont, ImageColor
import io

def overlay_text_on_image(
    image_path,
    text_a,
    text_b,
    font_path="assets/fonts/Roboto-Regular.ttf",
    font_size_a=50,
    font_size_b=100,
    bg_color_a=None,
    bg_color_b=None,
    padding_a=17,
    padding_b=30,
    bg_opacity=200  # прозрачность плашки 0-255
):
    """
    Добавляет верхний и нижний текст с плашками на изображение.
    Если text_a == '??', верхняя плашка и текст не рисуются.
    """

    # если верхний текст '??', отключаем его полностью
    if text_a == "??":
        text_a = ""
        bg_color_a = None

    # открываем изображение
    image = Image.open(image_path).convert("RGBA")
    width, height = image.size

    draw = ImageDraw.Draw(image)

    # ----------------------
    # Верхний текст и плашка
    # ----------------------
    if text_a and bg_color_a:
        font_a = ImageFont.truetype(font_path, font_size_a)
        bbox = draw.textbbox((0, 0), text_a, font=font_a, stroke_width=2)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # плашка
        rect_x0 = padding_a
        rect_y0 = padding_a
        rect_x1 = width - padding_a
        rect_y1 = padding_a + text_height + padding_a

        draw.rectangle(
            [rect_x0, rect_y0, rect_x1, rect_y1],
            fill=(*ImageColor.getrgb(bg_color_a), bg_opacity)
        )

        # текст по центру плашки
        text_x = (width - text_width) / 2
        text_y = rect_y0 + (rect_y1 - rect_y0 - text_height) / 2
        draw.text(
            (text_x, text_y),
            text_a,
            font=font_a,
            fill="white",
            stroke_width=2,
            stroke_fill="black"
        )

    # ----------------------
    # Нижний текст и плашка
    # ----------------------
    if text_b and bg_color_b:
        font_b = ImageFont.truetype(font_path, font_size_b)
        bbox = draw.textbbox((0, 0), text_b, font=font_b, stroke_width=2)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        rect_x0 = padding_b
        rect_y0 = height - text_height - padding_b*2
        rect_x1 = width - padding_b
        rect_y1 = height - padding_b

        draw.rectangle(
            [rect_x0, rect_y0, rect_x1, rect_y1],
            fill=(*ImageColor.getrgb(bg_color_b), bg_opacity)
        )

        # текст по центру плашки
        text_x = (width - text_width) / 2
        text_y = rect_y0 + (rect_y1 - rect_y0 - text_height) / 2
        draw.text(
            (text_x, text_y),
            text_b,
            font=font_b,
            fill="white",
            stroke_width=2,
            stroke_fill="black"
        )

    # ----------------------
    # Возврат результата в виде BytesIO
    # ----------------------
    output = io.BytesIO()
    image.save(output, format="PNG")
    output.seek(0)
    return output

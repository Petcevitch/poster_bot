from PIL import Image, ImageDraw, ImageFont, ImageColor
import io


def overlay_text_on_image(
    image_path,
    text_a,
    text_b,
    y_a_percent=8,
    y_b_percent=80,
    font_path="assets/fonts/Roboto-Regular.ttf",
    font_size_a=50,   # размер в два раза меньше
    font_size_b=100,
    fill_color="white",
    stroke_width=2,
    stroke_fill="black",
    bg_color_a=None,  # цвет плашки верхнего текста
    bg_color_b=None,  # цвет плашки нижнего текста
    bg_opacity=180,
    padding=35
):
    """
    Генерация постера с двумя текстовыми блоками с плашками.
    Нижний и верхний текст центрированы по высоте плашки.
    """

    img = Image.open(image_path).convert("RGBA")
    width, height = img.size
    draw = ImageDraw.Draw(img)

    # -------------------
    # Верхний текст (A)
    # -------------------
    if text_a:
        font_a = ImageFont.truetype(font_path, font_size_a)
        ascent, descent = font_a.getmetrics()
        text_vheight = ascent + descent
        bbox_a = draw.textbbox((0, 0), text_a, font=font_a)
        text_width_a = bbox_a[2] - bbox_a[0]

        block_height_a = text_vheight + padding * 2
        block_center_y_a = height * (y_a_percent / 100)
        rect_y0_a = block_center_y_a - block_height_a / 2
        rect_y1_a = rect_y0_a + block_height_a
        rect_x0_a = (width - text_width_a) / 2 - padding
        rect_x1_a = rect_x0_a + text_width_a + padding * 2

        # плашка верхнего текста
        if bg_color_a:
            overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            overlay_draw.rectangle(
                [rect_x0_a, rect_y0_a, rect_x1_a, rect_y1_a],
                fill=(*ImageColor.getrgb(bg_color_a), bg_opacity)
            )
            img = Image.alpha_composite(img, overlay)
            draw = ImageDraw.Draw(img)

        # текст по центру плашки
        x_a = (width - text_width_a) / 2
        y_a = rect_y0_a + (block_height_a - text_vheight) / 2
        draw.text(
            (x_a, y_a),
            text_a,
            font=font_a,
            fill=fill_color,
            stroke_width=stroke_width,
            stroke_fill=stroke_fill
        )

    # -------------------
    # Нижний текст (B)
    # -------------------
    if text_b:
        font_b = ImageFont.truetype(font_path, font_size_b)
        ascent, descent = font_b.getmetrics()
        text_vheight = ascent + descent
        bbox_b = draw.textbbox((0, 0), text_b, font=font_b)
        text_width_b = bbox_b[2] - bbox_b[0]

        block_height_b = text_vheight + padding * 2
        block_center_y_b = height * (y_b_percent / 100)
        rect_y0_b = block_center_y_b - block_height_b / 2
        rect_y1_b = rect_y0_b + block_height_b
        rect_x0_b = (width - text_width_b) / 2 - padding
        rect_x1_b = rect_x0_b + text_width_b + padding * 2

        # плашка нижнего текста
        if bg_color_b:
            overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            overlay_draw.rectangle(
                [rect_x0_b, rect_y0_b, rect_x1_b, rect_y1_b],
                fill=(*ImageColor.getrgb(bg_color_b), bg_opacity)
            )
            img = Image.alpha_composite(img, overlay)
            draw = ImageDraw.Draw(img)

        # текст по центру плашки
        x_b = (width - text_width_b) / 2
        y_b = rect_y0_b + (block_height_b - text_vheight) / 2
        draw.text(
            (x_b, y_b),
            text_b,
            font=font_b,
            fill=fill_color,
            stroke_width=stroke_width,
            stroke_fill=stroke_fill
        )

    # -------------------
    # OUTPUT
    # -------------------
    output = io.BytesIO()
    img.save(output, format="PNG")
    output.seek(0)
    return output

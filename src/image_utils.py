from PIL import Image, ImageDraw, ImageFont, ImageColor
import io


def overlay_text_on_image(
    image_path,
    text_a,
    text_b,
    y_a_percent=8,
    y_b_percent=80,
    font_path="assets/fonts/Roboto-Regular.ttf",
    font_size_a=60,
    font_size_b=100,
    fill_color="white",
    stroke_width=2,
    stroke_fill="black",
    bg_color=None,
    bg_opacity=180,
    padding=35
):
    """
    Накладывает текст A (верх) и текст B (низ с плашкой).
    Нижний текст визуально центрируется внутри плашки.
    """

    img = Image.open(image_path).convert("RGBA")
    width, height = img.size
    draw = ImageDraw.Draw(img)

    # -------------------
    # Верхний текст (A)
    # -------------------
    font_a = ImageFont.truetype(font_path, font_size_a)
    bbox_a = draw.textbbox((0, 0), text_a, font=font_a)
    text_width_a = bbox_a[2] - bbox_a[0]

    x_a = (width - text_width_a) / 2
    y_a = height * (y_a_percent / 100)

    draw.text(
        (x_a, y_a),
        text_a,
        font=font_a,
        fill=fill_color,
        stroke_width=stroke_width,
        stroke_fill=stroke_fill
    )

    # -------------------
    # Нижний текст (B) + плашка
    # -------------------
    font_b = ImageFont.truetype(font_path, font_size_b)
    ascent, descent = font_b.getmetrics()
    text_vheight = ascent + descent

    bbox_b = draw.textbbox((0, 0), text_b, font=font_b)
    text_width_b = bbox_b[2] - bbox_b[0]

    block_height = text_vheight + padding * 2
    block_center_y = height * (y_b_percent / 100)
    rect_y0 = block_center_y - block_height / 2
    rect_y1 = rect_y0 + block_height
    rect_x0 = (width - text_width_b) / 2 - padding
    rect_x1 = rect_x0 + text_width_b + padding * 2

    # Плашка
    if bg_color:
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        overlay_draw.rectangle(
            [rect_x0, rect_y0, rect_x1, rect_y1],
            fill=(*ImageColor.getrgb(bg_color), bg_opacity)
        )
        img = Image.alpha_composite(img, overlay)
        draw = ImageDraw.Draw(img)

    # Визуальное центрирование текста в плашке
    x_b = (width - text_width_b) / 2
    y_b = rect_y0 + (block_height - text_vheight) / 2

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

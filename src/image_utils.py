from PIL import Image, ImageDraw, ImageFont
import io

def overlay_text_on_image(image_path, text_a, text_b, y_a_percent=8, y_b_percent=80,
                          font_path="assets/fonts/Roboto-Regular.ttf",
                          font_size_a=60, font_size_b=100,
                          fill_color="white", stroke_width=2, stroke_fill="black",
                          bg_color=None, padding=10):
    """
    Накладывает две надписи на изображение с плашкой под нижним текстом.
    Текст и плашка полностью центрированы.
    """
    img = Image.open(image_path).convert("RGBA")
    width, height = img.size
    draw = ImageDraw.Draw(img)

    font_a = ImageFont.truetype(font_path, font_size_a)
    font_b = ImageFont.truetype(font_path, font_size_b)

    y_a = height * (y_a_percent / 100)
    y_b = height * (y_b_percent / 100)

    # Текст сверху (без плашки)
    text_bbox_a = draw.textbbox((0,0), text_a, font=font_a)
    text_width_a = text_bbox_a[2] - text_bbox_a[0]
    x_a = (width - text_width_a) / 2
    draw.text((x_a, y_a), text_a, font=font_a, fill=fill_color,
              stroke_width=stroke_width, stroke_fill=stroke_fill)

    # Текст снизу с плашкой
    text_bbox_b = draw.textbbox((0,0), text_b, font=font_b)
    text_width_b = text_bbox_b[2] - text_bbox_b[0]
    text_height_b = text_bbox_b[3] - text_bbox_b[1]
    x_b = (width - text_width_b) / 2
    y_b_top = y_b

    if bg_color:
        rect_x0 = x_b - padding
        rect_y0 = y_b_top - padding
        rect_x1 = x_b + text_width_b + padding
        rect_y1 = y_b_top + text_height_b + padding
        draw.rectangle([rect_x0, rect_y0, rect_x1, rect_y1], fill=bg_color)

    draw.text((x_b, y_b_top), text_b, font=font_b, fill=fill_color,
              stroke_width=stroke_width, stroke_fill=stroke_fill)

    output = io.BytesIO()
    img.save(output, format="PNG")
    output.seek(0)
    return output

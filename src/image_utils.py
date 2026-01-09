from PIL import Image, ImageDraw, ImageFont
import io

def overlay_text_on_image(image_path, text_a, text_b, y_a_percent=8, y_b_percent=80,
                          font_path="assets/fonts/Roboto-Regular.ttf", font_size_a=60, font_size_b=420,
                          fill_color="white", stroke_width=2, stroke_fill="black"):
    img = Image.open(image_path).convert("RGBA")
    width, height = img.size

    draw = ImageDraw.Draw(img)

    font_a = ImageFont.truetype(font_path, font_size_a)
    font_b = ImageFont.truetype(font_path, font_size_b)

    y_a = height * (y_a_percent / 100)
    y_b = height * (y_b_percent / 100)

    def draw_centered(text, y, font):
        text_bbox = draw.textbbox((0,0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        x = (width - text_width) / 2
        draw.text((x, y), text, font=font, fill=fill_color, stroke_width=stroke_width, stroke_fill=stroke_fill)

    # draw_centered(text_a, y_a, font_a)
    draw_centered(text_b, y_b, font_b)

    output = io.BytesIO()
    img.save(output, format="PNG")
    output.seek(0)
    return output

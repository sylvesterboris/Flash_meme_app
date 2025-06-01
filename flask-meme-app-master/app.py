from flask import Flask, render_template, request, send_file, redirect, url_for, session
import requests
from PIL import Image, ImageDraw, ImageFont
import io
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management

# Manual dictionary for translations (supports English, Spanish, French, German)
translations = {
    "en": {
        "generate": "Generate New Meme",
        "top_text": "Top Text",
        "bottom_text": "Bottom Text",
        "watermark_text": "Watermark",
        "watermark_position": "Watermark Position",
        "watermark_opacity": "Watermark Opacity (0-255)",
        "submit": "Generate Meme",
        "language": "Language",
        "category": "Category",
        "meme_generator": "Meme Generator",
        "Download Meme": "Download Meme",
        "Auto-generate every minute": "Auto-generate every minute",
        "Saved Memes": "Saved Memes",
        "Font Style": "Font Style"
    },
    "es": {
        "generate": "Generar Nuevo Meme",
        "top_text": "Texto Superior",
        "bottom_text": "Texto Inferior",
        "watermark_text": "Marca de agua",
        "watermark_position": "Posición de marca de agua",
        "watermark_opacity": "Opacidad de marca de agua (0-255)",
        "submit": "Generar Meme",
        "language": "Idioma",
        "category": "Categoría",
        "meme_generator": "Generador de Memes",
        "download_meme": "Descargar Meme",
        "auto_generate": "Auto-generar cada minuto",
        "saved_memes": "Memes Guardados",
        "font_style": "Estilo de Fuente"
    },
    "fr": {
        "generate": "Générer un Nouveau Mème",
        "top_text": "Texte Supérieur",
        "bottom_text": "Texte Inférieur",
        "watermark_text": "Filigrane",
        "watermark_position": "Position du Filigrane",
        "watermark_opacity": "Opacité du Filigrane (0-255)",
        "submit": "Générer le Mème",
        "language": "Langue",
        "category": "Catégorie",
        "meme_generator": "Générateur de Memes",
        "download_meme": "Télécharger le Meme",
        "auto_generate": "Générer automatiquement chaque minute",
        "saved_memes": "Memes Sauvegardés",
        "font_style": "Style de Police"
    },
    "de": {
        "generate": "Neues Meme Erstellen",
        "top_text": "Oberer Text",
        "bottom_text": "Unterer Text",
        "watermark_text": "Wasserzeichen",
        "watermark_position": "Wasserzeichen-Position",
        "watermark_opacity": "Wasserzeichen-Deckkraft (0-255)",
        "submit": "Meme Erstellen",
        "language": "Sprache",
        "category": "Kategorie",
        "meme_generator": "Meme-Generator",
        "download_meme": "Meme Herunterladen",
        "auto_generate": "Automatisch jede Minute generieren",
        "saved_memes": "Gespeicherte Memes",
        "font_style": "Schriftstil"
    }
}

# Default Language
def get_locale():
    return session.get("language", "en")

# Function to fetch a random meme
def get_random_meme():
    try:
        response = requests.get("https://api.imgflip.com/get_memes")
        data = response.json()
        if data.get("success"):
            memes = data.get("data", {}).get("memes", [])
            if memes:
                return random.choice(memes)["url"]
    except requests.exceptions.RequestException as e:
        print("Error fetching meme:", e)
    return None

# Function to overlay text and watermark on meme
# Function to overlay text and watermark on meme
def generate_meme(image_url, top_text, bottom_text, watermark_text, watermark_position="bottom-right", opacity=128):
    print(f"Watermark params - Text: '{watermark_text}', Position: {watermark_position}, Opacity: {opacity}") 
    response = requests.get(image_url)
    img = Image.open(io.BytesIO(response.content)).convert("RGBA")  # Ensure RGBA mode

    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("impact.ttf", size=int(img.width / 10))
    except:
        font = ImageFont.truetype("arial.ttf", size=int(img.width / 10))

    def draw_text(draw, text, position):
        """Draws text with shadow for better visibility"""
        bbox = draw.textbbox((0, 0), text, font=font)  # Corrected usage
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (img.width - text_width) / 2  # Center text horizontally
        y = position

        # Shadow effect
        draw.text((x + 2, y + 2), text, font=font, fill="black")
        draw.text((x, y), text, font=font, fill="white")

        return text_height  # Return height for bottom text positioning

    # Draw top text
    if top_text:
        text_height = draw_text(draw, top_text.upper(), 10)  # Position at top

    # Draw bottom text
    if bottom_text:
        text_height = draw_text(draw, bottom_text.upper(), img.height - text_height - 50)  # Adjusted position

    # Watermark Feature
    if watermark_text and watermark_text.strip():
        if watermark_text and watermark_text.strip():
            try:
                watermark_font = ImageFont.truetype("arial.ttf", size=int(img.width / 20))
            except:
                watermark_font = ImageFont.truetype("arial.ttf", size=20)

            bbox = draw.textbbox((0, 0), watermark_text, font=watermark_font)
            watermark_width = bbox[2] - bbox[0]
            watermark_height = bbox[3] - bbox[1]

            # Set watermark position with padding
            padding = 20
            positions = {
                "top-left": (padding, padding),
                "top-right": (img.width - watermark_width - padding, padding),
                "bottom-left": (padding, img.height - watermark_height - padding),
                "bottom-right": (img.width - watermark_width - padding, img.height - watermark_height - padding),        }
            pos = positions.get(watermark_position, positions["bottom-right"])

            # Create semi-transparent watermark
            watermark_img = Image.new("RGBA", img.size, (255, 255, 255, 0))
            watermark_draw = ImageDraw.Draw(watermark_img)
            watermark_draw.text(
                pos, 
                watermark_text, 
                font=watermark_font, 
                fill=(255, 255, 255, int(opacity)))
            
        img = Image.alpha_composite(img.convert("RGBA"), watermark_img)

    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    return img_io


'''def draw_text(draw, text, position):
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (img.width - text_width) / 2
        y = position
        draw.text((x+2, y+2), text, font=font, fill="black")
        draw.text((x, y), text, font=font, fill="white")

        if top_text:
            draw_text(draw, top_text.upper(), 10)

        if bottom_text:
            bbox = draw.textbbox((0, 0), bottom_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            draw_text(draw, bottom_text.upper(), img.height - text_height - 10)

        # Watermark Feature
        if watermark_text:
            try:
                watermark_font = ImageFont.truetype("arial.ttf", size=int(img.width / 20))
            except:
                watermark_font = ImageFont.truetype("arial.ttf", size=20)

            watermark_width, watermark_height = draw.textbbox(watermark_text, font=watermark_font)

        # Set watermark position
        positions = {
            "top-left": (10, 10),
            "top-right": (img.width - watermark_width - 10, 10),
            "bottom-left": (10, img.height - watermark_height - 10),
            "bottom-right": (img.width - watermark_width - 10, img.height - watermark_height - 10),
        }
        pos = positions.get(watermark_position, positions["bottom-right"])

        # Draw semi-transparent watermark
        watermark_img = Image.new("RGBA", img.size, (255, 255, 255, 0))
        watermark_draw = ImageDraw.Draw(watermark_img)
        watermark_draw.text(pos, watermark_text, font=watermark_font, fill=(255, 255, 255, opacity))
        img = Image.alpha_composite(img.convert("RGBA"), watermark_img)

        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        return img_io
'''
@app.route("/get_meme")
def get_meme_api():
    meme_url = get_random_meme()
    return {"meme_url": meme_url}
@app.route("/", methods=["GET", "POST"])
def index():
    meme_url = get_random_meme()
    lang = get_locale()
    text = translations.get(lang, translations["en"])

    if request.method == "POST":
        top_text = request.form.get("topText", "")
        bottom_text = request.form.get("bottomText", "")
        watermark_text = request.form.get("watermarkText", "DEFAULT_WATERMARK")
        watermark_position =  request.form.get("watermarkPosition", "bottom-right")
        opacity = int(request.form.get("watermarkOpacity", 128))

        meme_img = generate_meme(meme_url, top_text, bottom_text, watermark_text, watermark_position, opacity)
        return send_file(meme_img, mimetype="image/png", as_attachment=True, download_name="meme.png")

    return render_template("index.html", meme_url=meme_url, text=text, languages=translations.keys(), current_language=lang)

@app.route("/set_language/<language>")
def set_language(language):
    if language in translations:
        session['language'] = language
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

import os
from reportlab.pdfgen import canvas
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = "docs"
TOURS = {
    "paris": {
        "broschuere_eiffelturm.pdf": "Broschüre zum Eiffelturm mit Öffnungszeiten.",
        "postkarte_montmartre.jpg": "Liebe Grüße aus Montmartre!",
        "rechnung_bistro_steak.pdf": "Rechnung über 34,50 € vom Bistro Steak.",
        "speisekarte_cafe_raclette.pdf": "Speisekarte des Cafés Raclette mit Spezialitäten.",
        "ticket_louvre.pdf": "Eintrittskarte für den Louvre, gültig am 10.07.2025.",
        "tagebuch_paris_tag1.txt": "Mein erster Tag in Paris war fantastisch..."
    },
    "kyoto": {
        "broschuere_kiyomizudera.pdf": "Broschüre zum Kiyomizu-dera mit Öffnungszeiten.",
        "postkarte_gion.jpg": "Liebe Grüße aus dem Viertel Gion in Kyoto!",
        "rechnung_matcha_cafe.pdf": "Rechnung über 850 Yen im Matcha Café.",
        "speisekarte_kaiseki.pdf": "Speisekarte eines traditionellen Kaiseki-Restaurants.",
        "ticket_ryoanji.pdf": "Eintrittskarte zum Ryoanji-Zen-Garten, gültig am 12.10.2024.",
        "tagebuch_kyoto_tag1.txt": "Heute bin ich durch Kyoto geschlendert. Die Kirschblüten waren in voller Blüte.",
        "broschuere_kiyomizu_tempel.pdf": "Broschüre zum Kiyomizu-Tempel mit Öffnungszeiten.",
        "ticket_zen_garten.pdf": "Eintrittskarte zum Zen-Garten, gültig am 12.10.2024."
    },
    "berlin": {
        "broschuere_museuminsel.pdf": "Broschüre zur Museumsinsel in Berlin.",
        "postkarte_fernsehturm.jpg": "Viele Grüße vom Fernsehturm!",
        "rechnung_curry36.pdf": "Rechnung über 7,90 € bei Curry 36.",
        "speisekarte_kiezkneipe.pdf": "Speisekarte mit Berliner Spezialitäten.",
        "ticket_berliner_dom.pdf": "Eintrittskarte für den Berliner Dom, gültig am 21.06.2025.",
        "tagebuch_berlin_tag1.txt": "Erster Tag in Berlin. Street Art und Spree-Spaziergang.",
        "broschuere_berliner_mauer.pdf": "Broschüre zur Berliner Mauer.",
        "ticket_museuminsel.pdf": "Eintrittskarte für die Museumsinsel, gültig am 21.06.2025.",
        "postkarte_brandenburger_tor.jpg": "Viele Grüße vom Brandenburger Tor!",
        "speisekarte_berliner_kneipe.pdf": "Speisekarte mit Berliner Spezialitäten.",
    },
    "wien": {
        "broschuere_schloss_schoenbrunn.pdf": "Broschüre zum Schloss Schönbrunn mit Führungshinweisen.",
        "postkarte_prater.jpg": "Herzliche Grüße vom Prater!",
        "rechnung_sachertorte.pdf": "Rechnung über 5,60 € für eine Sachertorte.",
        "speisekarte_beisl.pdf": "Österreichische Klassiker vom Beisl.",
        "ticket_opernhaus.pdf": "Eintrittskarte für die Wiener Staatsoper.",
        "tagebuch_wien_tag1.txt": "Ein Café nach dem anderen. Sachertorte ist himmlisch.",
        "postkarte_stephansdom.jpg": "Herzliche Grüße vom Stephansdom!",
        "speisekarte_kaffeehaus.pdf": "Österreichische Klassiker aus dem Kaffeehaus.",
    }
}


def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def create_pdf(path, text):
    c = canvas.Canvas(path)
    c.drawString(100, 750, text)
    c.save()

def create_jpg(path, text):
    img = Image.new("RGB", (600, 400), color=(255, 255, 240))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    draw.text((20, 180), text, font=font, fill=(0, 0, 0))
    img.save(path)

def create_txt(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

def create_dummy_files():
    for city, files in TOURS.items():
        city_path = os.path.join(BASE_DIR, city)
        ensure_dir(city_path)
        for filename, content in files.items():
            file_path = os.path.join(city_path, filename)
            ext = os.path.splitext(filename)[1].lower()
            if ext == ".pdf":
                create_pdf(file_path, content)
            elif ext == ".jpg":
                create_jpg(file_path, content)
            elif ext == ".txt":
                create_txt(file_path, content)
            print(f"[✔] Erstellt: {file_path}")

if __name__ == "__main__":
    create_dummy_files()

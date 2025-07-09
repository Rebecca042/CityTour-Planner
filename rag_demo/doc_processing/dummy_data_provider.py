# dummy_data_provider.py
import os

def get_dummy_text(file_path: str) -> str:
    name = os.path.basename(file_path).lower()
    if "matcha" in name:
        return "Rechnung über 850 Yen im Matcha Café."
    elif "kaiseki" in name:
        return "Speisekarte eines traditionellen Kaiseki-Restaurants."
    elif "kiyomizu" in name:
        return "Broschüre zum Kiyomizu-dera mit Öffnungszeiten."
    elif "gion" in name:
        return "Liebe Grüße aus dem Viertel Gion in Kyoto!"
    elif "zen" in name:
        return "Eintrittskarte zum Ryoanji-Zen-Garten, gültig am 12.10.2024."
    elif "tagebuch_kyoto" in name:
        return "Heute bin ich durch Kyoto geschlendert. Die Kirschblüten waren in voller Blüte."
    elif "curry36" in name:
        return "Rechnung über 7,80 € bei Curry36."
    elif "berliner_mauer" in name:
        return "Broschüre zur Berliner Mauer mit historischen Informationen."
    elif "museuminsel" in name:
        return "Eintrittskarte zur Museumsinsel, gültig am 03.08.2025."
    elif "postkarte_brandenburger_tor" in name:
        return "Viele Grüße vom Brandenburger Tor!"
    elif "speisekarte_berliner_kneipe" in name:
        return "Speisekarte mit Berliner Spezialitäten."
    elif "tagebuch_berlin" in name:
        return "Erster Tag in Berlin. Street Art und Spree-Spaziergang."
    elif "sacher" in name:
        return "Rechnung über 12,00 € für eine Sachertorte."
    elif "schloss_schoenbrunn" in name:
        return "Broschüre zu Schloss Schönbrunn mit Gartenkarte."
    elif "staatsoper" in name:
        return "Ticket für die Wiener Staatsoper, Sitzplatz A12."
    elif "postkarte_stephansdom" in name:
        return "Herzliche Grüße vom Stephansdom!"
    elif "speisekarte_kaffeehaus" in name:
        return "Österreichische Klassiker aus dem Kaffeehaus."
    elif "tagebuch_wien" in name:
        return "Ein Café nach dem anderen. Sachertorte ist himmlisch."
    elif "rechnung_bistro_steak" in name:
        return "Rechnung über 34,50 € vom Bistro Steak."
    elif "ticket_louvre" in name:
        return "Eintrittskarte für den Louvre, gültig am 10.07.2025."
    elif "tagebuch_paris" in name:
        return "Mein erster Tag in Paris war fantastisch..."
    elif "postkarte_montmartre" in name:
        return "Liebe Grüße aus Montmartre!"
    elif "broschuere_eiffelturm" in name:
        return "Broschüre zum Eiffelturm mit Öffnungszeiten."
    elif "speisekarte_cafe_raclette" in name:
        return "Speisekarte des Cafés Raclette mit Spezialitäten."
    else:
        return "Unbekanntes Dokument."

def get_dummy_metadata(file_path: str) -> dict:
    name = os.path.basename(file_path).lower()
    if "matcha" in name:
        return {"betrag": "850 ¥", "ort": "Kyoto", "datum": "2024-04-03"}
    elif "kaiseki" in name:
        return {"lokal": "Kaiseki Gion", "ort": "Kyoto"}
    elif "kiyomizu" in name:
        return {"ort": "Kiyomizu-dera", "sprache": "japanisch"}
    elif "gion" in name:
        return {"absender": "Yuki", "ort": "Gion"}
    elif "zen" in name:
        return {"ort": "Ryoanji", "datum": "2024-10-12"}
    elif "tagebuch_kyoto" in name:
        return {"autor": "Hannah", "datum": "2024-04-03"}
    elif "curry36" in name:
        return {"betrag": "7,80 €", "ort": "Berlin", "datum": "2025-05-10"}
    elif "berliner_mauer" in name:
        return {"ort": "Berlin", "sprache": "deutsch"}
    elif "museuminsel" in name:
        return {"ort": "Museuminsel", "datum": "2025-08-03"}
    elif "postkarte_brandenburger_tor" in name:
        return {"absender": "Tim", "ort": "Brandenburger Tor"}
    elif "speisekarte_berliner_kneipe" in name:
        return {"lokal": "Berliner Kneipe"}
    elif "tagebuch_berlin" in name:
        return {"autor": "Anna", "datum": "2025-05-10"}
    elif "sacher" in name:
        return {"betrag": "12,00 €", "ort": "Wien", "datum": "2025-06-01"}
    elif "schloss_schoenbrunn" in name:
        return {"ort": "Schloss Schönbrunn", "sprache": "deutsch"}
    elif "staatsoper" in name:
        return {"ort": "Wiener Staatsoper", "datum": "2025-06-02"}
    elif "postkarte_stephansdom" in name:
        return {"absender": "Eva", "ort": "Stephansdom"}
    elif "speisekarte_kaffeehaus" in name:
        return {"lokal": "Wiener Kaffeehaus"}
    elif "tagebuch_wien" in name:
        return {"autor": "Lukas", "datum": "2025-06-01"}
    elif "rechnung_bistro_steak" in name:
        return {"betrag": "34,50 €", "ort": "Bistro Steak", "datum": "2025-07-05"}
    elif "ticket_louvre" in name:
        return {"ort": "Louvre", "datum": "2025-07-10"}
    elif "tagebuch_paris" in name:
        return {"autor": "Max Mustermann", "datum": "2025-07-01"}
    elif "postkarte_montmartre" in name:
        return {"absender": "Marie", "ort": "Montmartre"}
    elif "broschuere_eiffelturm" in name:
        return {"ort": "Eiffelturm", "sprache": "deutsch"}
    elif "speisekarte_cafe_raclette" in name:
        return {"lokal": "Café Raclette"}
    else:
        return {}

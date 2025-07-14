# 🚀 RAG-Demo: Retrieval-Augmented Generation Proof-of-Concept

Dieses Projekt zeigt, wie man Large Language Models lokal (ohne Cloud-API) mit Vektordatenbanken (FAISS) kombiniert, um Dokumente (PDFs, Bilder etc.) effizient zu durchsuchen und darauf basierende Antworten zu generieren.

---

## 🛠 Technologien

* 🧐 LangChain
* 🤗 HuggingFace Transformers
* 📚 FAISS Vektorindex
* 📄 PyPDFLoader
* 🖼️ Tesseract-OCR / EasyOCR (für Bildverarbeitung)
* 🥪 OpenCV / PIL für Bildvorverarbeitung

---

## ⚙️ Installation

```bash
pip install -r requirements.txt
```

### Zusätzlich (nur bei OCR-Verwendung):

* [Tesseract-OCR installieren](https://github.com/tesseract-ocr/tesseract)
* `TESSDATA_PREFIX` und `tesseract_cmd` korrekt setzen (siehe `ocr_demo.py`)

---

## 📂 Vorbereitung

Lege z. B. ein Beispiel-PDF oder Bild wie `MotivationLLM.pdf` oder `postkarte_montmartre3.png` in den Projektordner (bzw. `docs/paris` für CityTour).

---

## ▶️ Nutzung

```bash
python rag_demo_minimal.py
```

Dies führt eine Beispiel-Abfrage aus:
**„Welche Erfahrungen hat Rebecca mit LLMs?“**

---

## 🤪 Tests

```bash
pytest test_rag_demo.py
python -m unittest test_citytour_loading.py
```

---

## ✨ Update: Proof-of-Concept für OCR-gestützte Reiseerzählung abgeschlossen

Dieses Update bringt die erste vollständige Version des modularen **CityTour Planner** Prototyps:

### 🧩 Komponenten

* 💾 **OCR-Decorator erweitert**: Erkennt gescannte Dokumente (JPG, PNG) automatisch und führt eine fallback-basierte Textextraktion durch. OCR wird nur dann verwendet, wenn nötig (inkl. Caching & Metadaten).

* 🔍 **Bild-Vorverarbeitung (Demo)**: `ocr_demo.py` demonstriert mehrere Pipelines zur Verbesserung der OCR-Erkennung (adaptive Thresholds, CLAHE, Upscaling usw.).

* 🧠 **LLM-Narration**: Mit `Summary_Strategy` und `Storytelling_Strategy` werden strukturierte oder erzählerische Zusammenfassungen generiert.

* 🔧 **Dummy-Daten & Simulation**: Erste Tests laufen mit realitätsnahen Beispieldaten (PDF + OCR-Postkarten), modular vorbereitet für echte Reisenotizen.

* 📆 **Erweiterbare Architektur**: Factory-, Strategie- und Prozessor-Pattern erlauben einfache Erweiterung für weitere Dokumenttypen, Sprachen, Engines oder Erzählformen.

---
### 📊 OCR Evaluations-Demo

Die eigenständige Demo befindet sich in `demo_test_tesseract.py` und ermöglicht:

- Vergleich von **Tesseract** und **EasyOCR**  
- Testen verschiedener **Vorverarbeitungs-Pipelines** (CLAHE, adaptive Thresholds, Hochskalierung)  
- Visualisierung von Zwischenstufen der Bilder (Graustufen, entrauscht, Schwellenwert, etc.)  
- Experimentieren mit unterschiedlichen OCR-Konfigurationen (z.B. `--psm 6`, Sprachwahl)  

Beispielhafte Nutzung:

```bash
python demo_test_tesseract.py
```
👉 Eingabebild: `docs/paris/postkarte_montmartre3.png` (Beispiel inklusive)
🗪 Ausgabe: OCR-Ergebnisse werden gedruckt, Zwischenergebnisse als Bilddateien gespeichert (z.B. `gray.jpg`, `resized.jpg`)


--- 

## 🛠️ Nächste Schritte

* ✅ Test mit echten Reisedokumenten (z. B. eingescannten Karten, PDFs)
* ✅ Aktivierung der vollständigen OCR-Pipeline mit Tesseract / EasyOCR
* ↻ Integration in interaktive RAG-Demo
* 🌍 Multilinguale Unterstützung (z. B. französische Postkarten)

---

## 💬 Feedback & Austausch

Dieses Projekt verbindet klassische Softwareentwicklung (Modularität, Testbarkeit) mit kreativen Möglichkeiten generativer KI. Ich freue mich über Ideen, Erfahrungen oder Verbesserungsvorschläge! 😊

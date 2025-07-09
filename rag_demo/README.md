# 🚀 RAG-Demo: Retrieval-Augmented Generation Proof-of-Concept

Dieses Projekt zeigt, wie man Large Language Models lokal (ohne Cloud-API) mit Vektordatenbanken (FAISS) kombiniert, um Dokumente (PDFs) effizient zu durchsuchen und darauf basierende Antworten zu generieren.

## 🛠 Technologien

- 🧠 LangChain  
- 🤗 HuggingFace Transformers  
- 📚 FAISS Vektorindex  
- 📄 PyPDFLoader  

## ⚙️ Installation

```bash
pip install -r requirements.txt
```

## 📂 Vorbereitung

Lege das Beispiel-PDF `MotivationLLM.pdf` in den Projektordner.

## ▶️ Nutzung

```bash
python rag_demo_minimal.py
```

Dies führt eine Beispiel-Abfrage aus:
„Welche Erfahrungen hat Rebecca mit LLMs?“

## 🧪 Test

```bash
pytest test_rag_demo.py
```

## 🔮 Zukünftige Verbesserungen / TODOs

- CLI-Interface für flexible Abfragen (z.B. `python rag_demo.py --query "Deine Frage"`)  
- Unterstützung weiterer Dokumentformate (z.B. DOCX, TXT)  
- Verbesserte Fehlerbehandlung und Logging  
- Integration in bestehende CityTour Planner App als Modul  
- Automatisierte Tests mit verschiedenen PDFs und Queries  
- Optionaler Cloud-Support für größere Modelle  

## ✨ Update: Proof-of-Concept für OCR-gestützte Reiseerzählung abgeschlossen

Dieses Update bringt die erste vollständige Version des modularen **CityTour Planner** Prototyps:

- 📄 **OCR-Integration vorbereitet**: Die erweiterbare `DocProcessorFactory` erkennt gescannte Reisedokumente und kann optional mit Tesseract-OCR kombiniert werden (`OCRDecorator`). So lassen sich auch komplexe Pipelines einfach testen und austauschen.

- 🧠 **LLM-Narration implementiert**: Auf Basis der zusammengefassten Inhalte generieren verschiedene Strategien wie `Summary_Strategy` oder `Storytelling_Strategy` lebendige, personalisierte Reiseerzählungen.

- 🔧 **Dummy-Daten & Simulation**: Zum initialen Testlauf wird ein realitätsnaher Dummy-Datensatz verwendet – das OCR-Verhalten ist modular vorbereitet und kann später durch echte gescannte Dokumente ersetzt werden.

- 📦 **Modular & erweiterbar**: Die Architektur folgt dem Prinzip der Trennung von Verantwortung (Factory, Strategie, Processing). Neue Dokumenttypen, Analysepfade oder Erzählstrategien lassen sich einfach integrieren.

---

## 🛠️ Nächste Schritte

- Test mit echten Reisedokumenten (JPG)

- Aktivierung der echten Tesseract-OCR-Pipeline

- Anbindung an das RAG-Demo-Modul zur interaktiven Q&A

---

## 💬 Feedback & Austausch

Dieses Projekt verbindet klassische Softwareentwicklung (APIs, Modularität, Testbarkeit) mit kreativen Möglichkeiten generativer KI. Ich freue mich über Ideen, Fragen und jedes konstruktive Feedback! 😊
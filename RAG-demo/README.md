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
python rag_demo.py
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

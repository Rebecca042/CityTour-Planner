# 🚀 RAG-Demo: Retrieval-Augmented Generation Proof of Concept

This project demonstrates how to combine Large Language Models (LLMs) with vector databases (FAISS) locally (without using a cloud API) to efficiently search documents (PDFs, images, etc.) and generate responses based on them.

---

## 🔧 Technologies

- 🤮 LangChain
- 🤗 HuggingFace Transformers
- 📚 FAISS Vector Index
- 📄 PyPDFLoader
- 🖼️ Tesseract-OCR / EasyOCR (for image processing)
- 🥪 OpenCV / PIL for image preprocessing

---

## ⚙️ Installation

```bash
pip install -r requirements.txt
```

### Additionally (for OCR usage):

- [Install Tesseract-OCR](https://github.com/tesseract-ocr/tesseract)
- Set `TESSDATA_PREFIX` and `tesseract_cmd` correctly (see `ocr_demo.py`)

---

## 📂 Preparation

Place an example PDF or image (e.g., `MotivationLLM.pdf` or `postkarte_montmartre3.png`) into the project folder (`docs/paris` for CityTour).

---

## ▶️ Usage

```bash
python rag_demo_minimal.py
```

This runs a sample query:\
**"What experience does Rebecca have with LLMs?"**

---

## 🤪 Tests

```bash
pytest test_rag_demo.py
python -m unittest test_citytour_loading.py
```

---

## ✨ Update: OCR-powered Travel Storytelling Proof-of-Concept Complete

This update delivers the first complete version of the modular **CityTour Planner** prototype:

### 🧹 Components

- 📂 **OCR Decorator Extended**: Automatically detects scanned documents (JPG, PNG) and performs fallback-based text extraction. OCR is only used when necessary (with caching & metadata tagging).

- 🔍 **Image Preprocessing Demo**: `ocr_demo.py` demonstrates various pipelines to enhance OCR recognition (adaptive thresholds, CLAHE, upscaling, etc.).

- 🤠 **LLM-Based Narration**: Structured or narrative summaries are generated using `Summary_Strategy` and `Storytelling_Strategy`.

- 🔧 **Dummy Data & Simulation**: Initial tests use realistic sample data (PDF + OCR postcards), modularly prepared for real travel logs.

- 📆 **Extensible Architecture**: Factory, Strategy, and Processor patterns allow easy extensions for more document types, languages, engines, or storytelling forms.

### 📊 OCR Evaluation Demo

Located in `demo_test_tesseract.py`, this standalone demo allows you to:

- Compare **Tesseract** vs **EasyOCR**
- Test multiple **preprocessing pipelines** (CLAHE, adaptive thresholding, upscaling)
- Visualize intermediate image stages (grayscale, denoised, thresholded, etc.)
- Experiment with different OCR configs (e.g., `--psm 6`, language selection)

Example usage:

```bash
python demo_test_tesseract.py
```

👉 Input image: `docs/paris/postkarte_montmartre3.png` (sample included)\
🗪 Output: printed OCR results, plus saved intermediate images (e.g. `gray.jpg`, `resized.jpg`)

---

## ⚙️ Next Steps

- ✅ Test with real travel documents (e.g., scanned cards, PDFs)
- ✅ Enable full OCR pipeline with Tesseract / EasyOCR
- ↻ Integrate with the interactive RAG demo
- 🌍 Add multilingual support (e.g., French postcards)

---

## 💬 Feedback & Exchange

This project combines traditional software design (modularity, testability) with the creative potential of generative AI. I welcome ideas, questions, and constructive feedback! 😊


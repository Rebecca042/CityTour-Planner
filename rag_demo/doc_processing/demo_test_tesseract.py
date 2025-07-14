import os

import cv2
from PIL import Image

# Set environment variable before importing pytesseract
os.environ['TESSDATA_PREFIX'] = r"C:\Program Files\Tesseract-OCR\tessdata"

import pytesseract
import easyocr

# Set tesseract executable path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def preprocess_image(image_path):
    img_cv = cv2.imread(img_path)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

    # Denoise
    denoised = cv2.medianBlur(gray, 3)

    # Adaptive Threshold
    adaptive_thresh = cv2.adaptiveThreshold(
        denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 11, 2
    )

    # Resize for better OCR
    scale_percent = 150
    width = int(adaptive_thresh.shape[1] * scale_percent / 100)
    height = int(adaptive_thresh.shape[0] * scale_percent / 100)
    dim = (width, height)
    resized = cv2.resize(adaptive_thresh, dim, interpolation=cv2.INTER_LINEAR)

    cv2.imwrite('gray.jpg', gray)
    cv2.imwrite('denoised.jpg', denoised)
    cv2.imwrite('thresh.jpg', adaptive_thresh)
    cv2.imwrite('resized.jpg', resized)

    img_pil_proc = Image.fromarray(resized)
    return Image.fromarray(resized)
def preprocess_cursive(image_path):
    img_cv = cv2.imread(image_path)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

    # Resize first (scale up)
    scale_percent = 150
    width = int(gray.shape[1] * scale_percent / 100)
    height = int(gray.shape[0] * scale_percent / 100)
    dim = (width, height)
    resized = cv2.resize(gray, dim, interpolation=cv2.INTER_CUBIC)

    # Apply CLAHE to improve local contrast
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(resized)

    # Optional: bilateral filter to smooth while preserving edges
    filtered = cv2.bilateralFilter(enhanced, d=9, sigmaColor=75, sigmaSpace=75)

    # Try Otsu's threshold (or comment out threshold to test without it)
    _, thresh = cv2.threshold(filtered, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)



    # Or just return filtered or enhanced directly if threshold loses info
    return Image.fromarray(thresh)  # or Image.fromarray(filtered)
def preprocess_skip_threshold(image_path):
    img_cv = cv2.imread(image_path)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

    # Optional: Enhance contrast with CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)

    # Resize (upscale) to help OCR
    scale_percent = 150
    width = int(enhanced.shape[1] * scale_percent / 100)
    height = int(enhanced.shape[0] * scale_percent / 100)
    dim = (width, height)
    resized = cv2.resize(enhanced, dim, interpolation=cv2.INTER_CUBIC)
    cv2.imwrite('gray2.jpg', gray)
    cv2.imwrite('clahe_enhanced2.jpg', enhanced)
    cv2.imwrite('resized.jpg', resized)
    return Image.fromarray(resized)

def ocr_tesseract(image, lang='fra'):
    return pytesseract.image_to_string(image, lang=lang)

def ocr_tesseract_advanced(image, lang='fra'):#config='--psm 6'
    return pytesseract.image_to_string(image, lang=lang)


def ocr_easyocr(image_path, lang_list=['fr']):
    reader = easyocr.Reader(lang_list, gpu=False)
    results = reader.readtext(image_path, detail=0)
    return "\n".join(results)


if __name__ == "__main__":
    img_path = "C:/Users/Rebecca/PycharmProjects/CityTour-Planner/rag_demo/docs/paris/postkarte_montmartre3.png"

    # 1. OCR without preprocessing
    print("=== Tesseract OCR without preprocessing ===")
    image = Image.open(img_path)
    text_raw = ocr_tesseract(image)
    print(text_raw)

    # 1. OCR without preprocessing
    print("=== EasyOCR without preprocessing ===")
    text_raw = ocr_easyocr(img_path)
    print(text_raw)

    # 2. OCR with preprocessing
    print("\n=== Tesseract OCR with preprocessing ===")
    image_preprocessed = preprocess_skip_threshold(img_path)
    text_preprocessed = ocr_tesseract_advanced(image_preprocessed)
    print(text_preprocessed)

    # 3. OCR with EasyOCR
    print("\n=== EasyOCR result ===")
    text_easyocr = ocr_easyocr(img_path)
    print(text_easyocr)

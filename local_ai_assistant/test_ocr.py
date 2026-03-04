from PIL import Image
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

img = Image.open(r"documents/ChatGPT Image Feb 15, 2026, 05_17_27 PM.png")

text = pytesseract.image_to_string(img)

print(text)

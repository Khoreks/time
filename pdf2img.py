import fitz  # PyMuPDF
import cv2
import numpy as np

def pdf_to_image(pdf_path, output_size=(1920, 1080)):
    doc = fitz.open(pdf_path)
    page = doc.load_page(0)  # первая страница
    
    # Рендерим с высоким DPI (рассчитываем zoom для ~1920x1080)
    zoom = max(output_size) / max(page.rect.width, page.rect.height)
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)
    
    # Конвертируем в numpy array
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)  # fitz использует RGB, OpenCV — BGR
    
    # Ресайз до точного размера
    img = cv2.resize(img, output_size)
    return img

import cv2
import numpy as np

import fitz  # PyMuPDF
import cv2
import numpy as np

def pdf_to_image_original_size(pdf_path):
    """
    Рендерит первую страницу PDF в исходном разрешении (1:1 пиксель/точку).
    Возвращает изображение в формате OpenCV (numpy array).
    """
    doc = fitz.open(pdf_path)
    page = doc.load_page(0)  # Первая страница

    # Рендерим с матрицей 1:1 (без масштабирования)
    mat = fitz.Matrix(1.0, 1.0)  # 1.0 = 72 DPI (стандарт PDF)
    pix = page.get_pixmap(matrix=mat, alpha=False)

    # Конвертируем в numpy array (OpenCV BGR)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    doc.close()
    return img


def preprocess_logo(logo):
    gray = cv2.cvtColor(logo, cv2.COLOR_BGR2GRAY)
    # Дополнительная обработка, если нужно (бинаризация, blur)
    return gray

def find_logo_in_image(image, logos, threshold=0.8):
    gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    found_positions = []

    for logo in logos:
        preprocessed_logo = preprocess_logo(logo)
        w, h = preprocessed_logo.shape[::-1]

        # Метод TM_CCOEFF_NORMED обычно лучше всего работает для логотипов
        res = cv2.matchTemplate(gray_img, preprocessed_logo, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= threshold)

        for pt in zip(*loc[::-1]):
            found_positions.append({
                'logo': logo,
                'position': pt,
                'size': (w, h),
                'confidence': res[pt[1], pt[0]]
            })

    return found_positions

def draw_results(image, found):
    output = image.copy()
    for item in found:
        pt = item['position']
        w, h = item['size']
        cv2.rectangle(output, pt, (pt[0] + w, pt[1] + h), (0,255,0), 2)
    return output

# Загрузка эталонных логотипов
logos = [cv2.imread(f'logo{i}.png') for i in range(5)]
preprocessed_logos = [preprocess_logo(logo) for logo in logos]

# Конвертация PDF
image = pdf_to_image('document.pdf')

# Поиск
found = find_logo_in_image(image, preprocessed_logos, threshold=0.75)

# Визуализация
if found:
    result_image = draw_results(image, found)
    cv2.imwrite('result.jpg', result_image)
else:
    print("Логотипы не найдены")

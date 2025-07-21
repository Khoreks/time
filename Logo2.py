import cv2
import numpy as np

def generate_logo_scales(logo, scales=[0.5, 0.75, 1.0, 1.25, 1.5, 2.0]):
    """Генерирует логотип в разных масштабах."""
    scaled_logos = []
    for scale in scales:
        width = int(logo.shape[1] * scale)
        height = int(logo.shape[0] * scale)
        resized_logo = cv2.resize(logo, (width, height), interpolation=cv2.INTER_AREA)
        scaled_logos.append(resized_logo)
    return scaled_logos

def find_best_logo_match(image, logo_scales, threshold=0.8):
    """Ищет логотип в разных масштабах и возвращает лучший результат."""
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    best_match = None
    best_confidence = -1

    for logo in logo_scales:
        gray_logo = cv2.cvtColor(logo, cv2.COLOR_BGR2GRAY)
        res = cv2.matchTemplate(gray_image, gray_logo, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)

        if max_val > best_confidence and max_val >= threshold:
            best_confidence = max_val
            best_match = {
                "logo": logo,
                "position": max_loc,
                "confidence": max_val,
                "scale": logo.shape[1] / logo_scales[0].shape[1]  # исходный scale
            }

    return best_match if best_confidence != -1 else None

# Загружаем PDF и логотип
pdf_image = pdf_to_image("document.pdf")  # исходное или масштабированное изображение
logo = cv2.imread("logo.png")  # эталонный логотип (например, 64x64)

# Генерируем масштабы логотипа
scaled_logos = generate_logo_scales(logo)

# Ищем лучший вариант
best_match = find_best_logo_match(pdf_image, scaled_logos, threshold=0.7)

if best_match:
    print(f"Логотип найден! Scale: {best_match['scale']:.2f}, Confidence: {best_match['confidence']:.2f}")
    # Рисуем bounding box
    x, y = best_match["position"]
    w, h = best_match["logo"].shape[1], best_match["logo"].shape[0]
    cv2.rectangle(pdf_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
    cv2.imwrite("result.jpg", pdf_image)
else:
    print("Логотип не найден :(")

import math

def auto_scales(base_scale=1.0, min_scale=0.2, max_scale=3.0, steps=10):
    """Генерирует логарифмические scale-ы для более плавного поиска."""
    scales = np.logspace(math.log10(min_scale), math.log10(max_scale), steps)
    return scales * base_scale

def multi_scale_template_matching(image, logo, max_scale=2.0, threshold=0.7):
    """Поиск логотипа с пирамидой изображений."""
    best_match = None
    for scale in np.linspace(0.5, max_scale, 10):
        resized_image = cv2.resize(image, None, fx=scale, fy=scale)
        res = cv2.matchTemplate(resized_image, logo, cv2.TM_CCOEFF_NORMED)
        _, confidence, _, max_loc = cv2.minMaxLoc(res)
        if confidence > threshold and (best_match is None or confidence > best_match["confidence"]):
            best_match = {
                "position": (int(max_loc[0] / scale), int(max_loc[1] / scale)),
                "confidence": confidence,
                "scale": scale
            }
    return best_match

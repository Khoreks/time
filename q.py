from collections import defaultdict

def aggregate_scores(titles, scores):
    # Словарь для хранения суммы и количества повторений
    score_dict = defaultdict(lambda: {'sum': 0, 'count': 0})
    
    # Собираем суммы и количество повторений
    for title, score in zip(titles, scores):
        score_dict[title]['sum'] += score
        score_dict[title]['count'] += 1
    
    # Вычисляем среднее для каждого title
    aggregated = {
        title: score_data['sum'] / score_data['count']
        for title, score_data in score_dict.items()
    }
    
    return aggregated


import fitz  # PyMuPDF
from PIL import Image
import io

def pixmap_to_pil_with_white_bg(pix):
    """
    Конвертирует fitz.Pixmap в PIL.Image, заменяя прозрачный фон на белый.
    """
    # Конвертируем в RGB, если есть альфа-канал
    if pix.alpha:
        # Создаём новый pixmap в режиме RGB (без альфы)
        pix = fitz.Pixmap(fitz.csRGB, pix)  # теряем прозрачность, но оставляем цвета

    # Получаем байты в формате PNG (можно и JPEG, но PNG безопаснее для качества)
    img_bytes = pix.tobytes("png")
    pil_img = Image.open(io.BytesIO(img_bytes))

    # Убедимся, что изображение в RGB (на всякий случай)
    if pil_img.mode in ("RGBA", "LA", "P"):
        # Создаём белый фон
        background = Image.new("RGB", pil_img.size, (255, 255, 255))
        if pil_img.mode in ("RGBA", "LA"):
            background.paste(pil_img, mask=pil_img.split()[-1])  # используем альфа-канал как маску
        else:
            # режим 'P' (палитра) — просто конвертируем
            pil_img = pil_img.convert("RGB")
            background = pil_img
        pil_img = background

    return pil_img



from PIL import Image
import io

def pixmap_to_pil_with_white_bg(pix):
    """
    Конвертирует fitz.Pixmap в PIL.Image с белым фоном.
    Даже если pix.alpha == 0 — всё равно делает RGB.
    """
    # Если есть альфа — конвертируем в RGB с наложением на белый фон
    if pix.alpha:
        pix = fitz.Pixmap(fitz.csRGB, pix)  # теряем альфа-канал, сохраняя цвета

    # Конвертируем в байты PNG
    img_data = pix.tobytes("png")
    pil_img = Image.open(io.BytesIO(img_data))

    # Если вдруг PIL открыл как RGBA (например, если pix.alpha был проигнорирован) — конвертируем
    if pil_img.mode in ("RGBA", "LA", "P"):
        background = Image.new("RGB", pil_img.size, (255, 255, 255))
        if pil_img.mode in ("RGBA", "LA"):
            background.paste(pil_img, mask=pil_img.split()[-1])
        else:
            pil_img = pil_img.convert("RGB")
            background = pil_img
        pil_img = background

    return pil_img

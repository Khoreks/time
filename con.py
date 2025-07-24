def align_document(img, document_contour):
    # Упорядочиваем углы (top-left, top-right, bottom-right, bottom-left)
    points = document_contour.reshape(4, 2)
    rect = np.zeros((4, 2), dtype="float32")
    
    s = points.sum(axis=1)
    rect[0] = points[np.argmin(s)]  # top-left (min сумма)
    rect[2] = points[np.argmax(s)]  # bottom-right (max сумма)
    
    diff = np.diff(points, axis=1)
    rect[1] = points[np.argmin(diff)]  # top-right (min разность)
    rect[3] = points[np.argmax(diff)]  # bottom-left (max разность)
    
    # Задаём новые координаты для выравнивания
    (tl, tr, br, bl) = rect
    width = max(np.linalg.norm(tr - tl), np.linalg.norm(br - bl))
    height = max(np.linalg.norm(bl - tl), np.linalg.norm(br - tr))
    
    dst = np.array([
        [0, 0],
        [width - 1, 0],
        [width - 1, height - 1],
        [0, height - 1]
    ], dtype="float32")
    
    # Применяем преобразование
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(img, M, (int(width), int(height)))
    
    return warped

img = cv2.imread("passport.jpg")
edged = preprocess_image(img)
document_contour = find_document_contour(edged)

if document_contour is not None:
    aligned = align_document(img, document_contour)
    cv2.imshow("Aligned", aligned)
    cv2.waitKey(0)
else:
    print("Документ не найден!")

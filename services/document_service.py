import cv2
import numpy as np

RESCALE_HEIGHT = 500
BLUR_KERNEL_SIZE = (7, 7)
MORPH_KERNEL_SIZE = (9, 9)
CANNY_LOWER = 0
CANNY_UPPER = 84
APPROX_POLY_FACTOR = 0.02
NUM_TOP_CONTOURS = 5
ADAPTIVE_BLOCK_SIZE = 11
ADAPTIVE_CONSTANT = 10

def _convert_image_buffer_to_image_mat(image_buffer):
    img_arr = np.frombuffer(image_buffer, np.uint8)
    img = cv2.imdecode(img_arr, cv2.IMREAD_COLOR)
    return img

def _encode_to_png(image_mat):
    _, encoded_bytes = cv2.imencode('.png', img=image_mat)
    return encoded_bytes.tobytes()

def _order_points(pts):
    """Order points clockwise starting from top-left"""
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect

def _four_point_transform(image, pts):
    """Apply perspective transform given 4 corner points"""
    rect = _order_points(pts)
    (tl, tr, br, bl) = rect
    
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))
    
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))
    
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype="float32")
    
    M = cv2.getPerspectiveTransform(_order_points(pts).astype("float32"), dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
    return warped

def _detect_contours(image):
    rescaled = cv2.resize(image, (int(image.shape[1] * RESCALE_HEIGHT / image.shape[0]), RESCALE_HEIGHT))
    img_area = rescaled.shape[0] * rescaled.shape[1]

    gray = cv2.cvtColor(rescaled, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, BLUR_KERNEL_SIZE, 0)

    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, MORPH_KERNEL_SIZE)
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    opened = cv2.morphologyEx(closed, cv2.MORPH_OPEN, kernel)

    cnts, _ = cv2.findContours(opened, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:NUM_TOP_CONTOURS]

    screenCnt = None
    for c in cnts:
        if cv2.contourArea(c) > 0.05 * img_area:
            hull = cv2.convexHull(c)
            hull_peri = cv2.arcLength(hull, True)
            approx_hull = cv2.approxPolyDP(hull, APPROX_POLY_FACTOR * hull_peri, True)
            if len(approx_hull) == 4:
                screenCnt = approx_hull
                break

            if len(approx_hull) in [5, 6, 7]:
                rect = cv2.minAreaRect(hull)
                box = cv2.boxPoints(rect)
                approx_box = np.intp(box) 
                
                if cv2.contourArea(approx_box) > 0.08 * img_area:
                    screenCnt = approx_box
                    break

    if screenCnt is None and len(cnts) > 0:
        print("No contour found - using fallback")
        screenCnt = np.array([[[0, 0]], [[rescaled.shape[1], 0]], 
                          [[rescaled.shape[1], rescaled.shape[0]]], [[0, rescaled.shape[0]]]])

    return rescaled, screenCnt

def draw_contours(image_buffer):
    img = _convert_image_buffer_to_image_mat(image_buffer)
    rescaled, screenCnt = _detect_contours(img)
    
    cv2.drawContours(rescaled, [screenCnt], -1, (0, 255, 0), 2)
    return _encode_to_png(rescaled)

def warp_image(image_buffer):
    img = _convert_image_buffer_to_image_mat(image_buffer)
    ratio = img.shape[0] / RESCALE_HEIGHT
    _, screenCnt = _detect_contours(img)
    warped = _four_point_transform(img, screenCnt.reshape(4, 2) * ratio)

    gray = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, ADAPTIVE_BLOCK_SIZE, ADAPTIVE_CONSTANT)

    return _encode_to_png(thresh)

def grayscale_image(image_buffer):
    img = _convert_image_buffer_to_image_mat(image_buffer)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return _encode_to_png(img)

def lighten_image(image_buffer):
    img = _convert_image_buffer_to_image_mat(image_buffer)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, ADAPTIVE_BLOCK_SIZE, ADAPTIVE_CONSTANT)

    return _encode_to_png(thresh)


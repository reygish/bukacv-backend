from datetime import datetime
from io import BytesIO
import img2pdf
from flask import Blueprint, request, send_file
from services.document_service import grayscale_image, draw_contours, warp_image, lighten_image

api_bp = Blueprint("api", __name__)


@api_bp.post("/grayscale")
def convert_grayscale_image():
    if 'image' not in request.files:
        return 'No image provided', 400
    
    file = request.files['image']
    image_data = file.stream.read()
    
    gray_bytes = grayscale_image(image_data)
    
    return send_file(
        BytesIO(gray_bytes),
        mimetype='image/png'
    )

@api_bp.post("/contours")
def detect_contours_image():
    if 'image' not in request.files:
        return 'No image provided', 400
    
    file = request.files['image']
    image_data = file.stream.read()
    
    image_bytes = draw_contours(image_data)
    
    return send_file(
        BytesIO(image_bytes),
        mimetype='image/png'
    )
    
@api_bp.post("/warp")
def warp_document_image():
    if 'image' not in request.files:
        return 'No image provided', 400
    
    file = request.files['image']
    image_data = file.stream.read()
    
    image_bytes = warp_image(image_data)
    
    return send_file(
        BytesIO(image_bytes),
        mimetype='image/png'
    )

@api_bp.post("/lighten")
def lighten_document_image():
    if 'image' not in request.files:
        return 'No image provided', 400
    
    file = request.files['image']
    image_data = file.stream.read()
    
    image_bytes = lighten_image(image_data)
    
    return send_file(
        BytesIO(image_bytes),
        mimetype='image/png'
    )

@api_bp.post("/pdf")
def save_as_pdf():
    if 'image' not in request.files:
        return 'No image provided', 400

    file = request.files['image']
    image_data = file.stream.read()

    pdf_bytes = img2pdf.convert(image_data)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"document_{timestamp}.pdf"

    return send_file(
        BytesIO(pdf_bytes),
        mimetype='application/pdf',
        download_name=filename
    )
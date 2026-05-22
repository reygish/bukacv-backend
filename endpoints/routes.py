from datetime import datetime
from io import BytesIO
import os
import img2pdf
from flask import Blueprint, request, send_file, jsonify, Response
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

PDF_STORAGE_FOLDER = 'downloads'
os.makedirs(PDF_STORAGE_FOLDER, exist_ok=True)

@api_bp.route("/pdf", methods=["POST"])
def save_as_pdf():
    files = request.files.getlist('images')
    
    if not files or files[0].filename == '':
        return 'No images provided', 400

    try:
        image_bytes_list = [file.stream.read() for file in files]
        pdf_bytes = img2pdf.convert(image_bytes_list)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"bukacv_{timestamp}.pdf"
        filepath = os.path.join(PDF_STORAGE_FOLDER, filename)

        with open(filepath, 'wb') as f:
            f.write(pdf_bytes)

        return jsonify({"success": True, "filename": filename}), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Create a route to serve the saved PDFs
@api_bp.route("/download/<filename>", methods=["GET"])
def download_pdf(filename):
    filepath = os.path.join(PDF_STORAGE_FOLDER, filename)
    if not os.path.exists(filepath):
        return "File not found", 404
    
    try:
        with open(filepath, 'rb') as f:
            pdf_data = f.read()
        
        os.remove(filepath)
        print(f"Windows safely deleted physical file: {filepath}")

        return Response(
            pdf_data,
            mimetype='application/pdf',
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Length": str(len(pdf_data))
            }
        )

    except Exception as e:
        print(f"Error handling cleanup download: {str(e)}")
        return f"Internal Error: {str(e)}", 500

# @api_bp.post("/pdf")
# def save_as_pdf():
#     files = request.files.getlist('images')
    
#     if not files or files[0].filename == '':
#         return 'No images provided', 400

#     try:
#         # Read the raw byte data of every image file sent in the request
#         image_bytes_list = [file.stream.read() for file in files]

#         # img2pdf automatically compiles an array of image bytes into a single multi-page PDF!
#         pdf_bytes = img2pdf.convert(image_bytes_list)

#         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#         filename = f"document_{timestamp}.pdf"

#         return send_file(
#             BytesIO(pdf_bytes),
#             mimetype='application/pdf',
#             download_name=filename,
#             as_attachment=True # Ensures mobile apps receive it cleanly as a downloadable file
#         )
#     except Exception as e:
#         return f"PDF conversion failed: {str(e)}", 500
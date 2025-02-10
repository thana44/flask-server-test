from flask import Flask, request, jsonify
import easyocr
import fitz
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["*"], supports_credentials=True)

reader = easyocr.Reader(["th", "en"], gpu=False)

if not os.path.exists("uploads"):
    os.makedirs("uploads")

@app.route("/uploads/api/upload-image", methods=["POST"])
def upload_file():

    if "file" not in request.files:
        return jsonify({
            "error" : "No file uploaded."
        }), 404
    
    file = request.files["file"]

    if file.filename == "":
        return jsonify({
            "message": "No selectd file"
        }), 400
    
    # ตรวจสอบประเภทไฟล์ (ในที่นี้คาดว่าเป็น .png, .jpg, .jpeg)
    if not file.filename.lower().endswith((".png", ".jpg", ".jpeg", ".pdf")):
        return jsonify({
            "error": "Invalid file type. Only PNG, JPG, JPEG and PDF are allowed."
        }), 400
    
    new_filename = "imageName." + file.filename.split(".")[1]

     # ตรวจสอบว่าไฟล์ที่อัพโหลดเป็น PDF หรือไม่
    if new_filename.endswith(".pdf"):
        # เปิดไฟล์ PDF
        pdf = fitz.open(stream=file.read(), filetype="pdf")

        # อ่านข้อความจากทุกหน้าในไฟล์ PDF
        text = ""
        for page_num in range(pdf.page_count):
            page = pdf.load_page(page_num)
            text += page.get_text()

        return jsonify({
            "text": text
        })
    
    file_path = os.path.join("uploads", new_filename)
    file.save(file_path)

    try:
        result = reader.readtext(file_path)

        extracted_text = "\n".join([item[1] for item in result])

        os.remove(file_path)

        return jsonify({
            "text" : extracted_text
        })
    except Exception as e:
        return jsonify({
            "message": f"Error processing image -> {str(e)}"
        }), 500
    

@app.route("/uploads/api/upload-image", methods=["GET"])
def displayText():

    return jsonify({
        "text": "This is get methods"
    })


if __name__ == "__main__":
    app.run(debug=True)
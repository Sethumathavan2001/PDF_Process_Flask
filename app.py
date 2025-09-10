# app.py
import os
import uuid
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory, abort
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

app = Flask(__name__)

PDF_DIR = os.path.join(os.path.dirname(__file__), "generated_pdfs")
os.makedirs(PDF_DIR, exist_ok=True)

def make_pdf(filepath, month, chit, extra_text=None):
    """Simple PDF generator — replace this with your actual backend process output."""
    c = canvas.Canvas(filepath, pagesize=A4)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, 800, "Generated PDF")
    c.setFont("Helvetica", 12)
    c.drawString(72, 770, f"Month: {month}")
    c.drawString(72, 750, f"CHIT: {chit}")
    c.drawString(72, 730, f"Generated at: {datetime.now().isoformat()}")
    if extra_text:
        c.drawString(72, 710, f"Notes: {extra_text}")
    c.showPage()
    c.save()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/process", methods=["POST"])
def process():
    """
    Expects JSON: { "month": "30", "chit": "some text" }
    Returns: { "success": True, "file_id": "<uuid>" }
    """
    data = request.get_json(force=True)
    month = data.get("month")
    chit = data.get("chit", "").strip()

    # Basic validation
    if month not in ("21", "30", "31"):
        return jsonify({"success": False, "error": "Invalid month value"}), 400
    if not chit:
        return jsonify({"success": False, "error": "CHIT is required"}), 400

    # --- PLACEHOLDER: Put your real backend processing here ---
    # For now we just make a small pdf containing the inputs.
    file_id = str(uuid.uuid4())
    filename = f"{file_id}.pdf"
    filepath = os.path.join(PDF_DIR, filename)
    make_pdf(filepath, month, chit, extra_text="Demo PDF — replace with real output")
    # ---------------------------------------------------------

    return jsonify({"success": True, "file_id": file_id}), 200

@app.route("/download/<file_id>", methods=["GET"])
def download(file_id):
    # Sanitize + ensure file exists
    if not file_id or "/" in file_id:
        abort(404)
    filename = f"{file_id}.pdf"
    path = os.path.join(PDF_DIR, filename)
    if not os.path.exists(path):
        abort(404)
    return send_from_directory(PDF_DIR, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

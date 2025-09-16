# app.py
import os
import uuid
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory, abort
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from datetime import datetime
from reportlab.pdfgen import canvas
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from datetime import datetime
import os
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen.canvas import Canvas
from datetime import datetime
import os
import os
import threading
import time
import json
from flask import Flask
app = Flask(__name__)
project_root = os.path.dirname(__file__)
PDF_DIR = os.path.join(project_root, "generated_pdfs")
os.makedirs(PDF_DIR, exist_ok=True)
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER

def empty_folder(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)  # delete file or symlink
            elif os.path.isdir(file_path):
                import shutil
                shutil.rmtree(file_path)  # delete subdirectory
        except Exception as e:
            print(f"[Cleanup Error] Failed to delete {file_path}: {e}")

def cleanup_task():
    while True:
        time.sleep(60)  # Sleep for 1 hour
        print(f"[Cleanup] Emptying folder: {PDF_DIR}")
        empty_folder(PDF_DIR)

# Start background cleanup thread
cleanup_thread = threading.Thread(target=cleanup_task, daemon=True)
cleanup_thread.start()

# Register Tamil font (place TTF file in assets/fonts/)
pdfmetrics.registerFont(TTFont('TamilFont', os.path.join(project_root,'fonts','vanavil_avvaiyar.ttf')))

# Define a paragraph style for Tamil text
tamil_style = ParagraphStyle(
    name='TamilStyle',
    fontName='TamilFont',
    fontSize=11,
    leading=14,
    spaceAfter=4,
    alignment=TA_CENTER
)


def draw_watermark_and_header(canvas: Canvas, doc):
    width, height = A4
    canvas.setFont("TamilFont", 14)
    canvas.drawString(297.63,820,"c")
    logo_path = os.path.join(project_root,"images","logo.jpg")
    if os.path.exists(logo_path):
        logo_width = 450
        logo_height = 450
        x = (width - logo_width) / 2
        y = (height - logo_height) / 2
        canvas.saveState()
        canvas.setFillAlpha(0.1)
        canvas.drawImage(logo_path, x, y, width=logo_width, height=logo_height, mask='auto')
        canvas.restoreState()

def format_indian_number(n):
    s = str(n)[::-1]
    parts = [s[:3]]  # first 3 digits
    s = s[3:]
    while s:
        parts.append(s[:2])
        s = s[2:]
    return ','.join(parts)[::-1]

def make_pdf(filepath, month, chit, extra_text=None):
    # Save metadata for potential use in header/footer
    extra_text = "c"
    draw_watermark_and_header.month = month
    draw_watermark_and_header.chit = chit
    draw_watermark_and_header.extra_text = extra_text

    doc = SimpleDocTemplate(filepath, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Build Tamil table using Paragraphs for wrapping
    data = []

    # First two merged rows
    data.append([Paragraph("thœf tsKl‹", tamil_style)] + [""] * 3)
    data.append([Paragraph(f"{chit} Ó£L {month} khj§fŸ", tamil_style)] + [""] * 3)

    # Header row
    data.append([
        Paragraph("jtiz", tamil_style),
        Paragraph("vL¡F« K‹ f£l nt©oa bjhif", tamil_style),
        Paragraph("vL¡F« jtizæš »il¡F« bjhif", tamil_style),
        Paragraph("vL¤j Ã‹ f£l nt©oa bjhif", tamil_style)
    ])

    # Fill 31 rows with "Sethu"
    
    with open(os.path.join(project_root,'json',f'{month}.json'),'r') as f:
        json_data = json.loads(f.read())
    for i in json_data:
        # data.append(["Sethu"] * 4)
        data.append([
    i.get('instalment', ""),
    format_indian_number(i.get('paid_before_collection', "") * int(chit)),
    format_indian_number(i.get('received_in_installments', "") * int(chit)),
    format_indian_number(i.get('paid_after_withdrawal', "") * int(chit))
])


    # Table with equal column widths
    col_width = (A4[0] - 2*inch) / 4  # equal columns with some margin
    print(A4,inch)
    row_height = 19
    row_height = (A4[1] - 4*inch) / int(month)
    table = Table(data, colWidths=[col_width] * 4,rowHeights=[row_height,row_height,29]+[row_height]*int(month))

    # Table style
    style = TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('SPAN', (0, 0), (3, 0)),
        ('ALIGN', (0, 0), (3, 0), 'CENTER'),
        ('SPAN', (0, 1), (3, 1)),
        ('ALIGN', (0, 1), (3, 1), 'CENTER'),
        ('BACKGROUND', (0, 0), (3, 1), colors.lightgrey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ])
    style = TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),

        # Merged row styles
        ('SPAN', (0, 0), (3, 0)),
        ('SPAN', (0, 1), (3, 1)),
        ('BACKGROUND', (0, 0), (3, 1), colors.lightgrey),

        # Center align ALL cells (horizontal + vertical)
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ])

    table.setStyle(style)
    elements.append(table)

    # Build the PDF
    doc.build(elements, onFirstPage=draw_watermark_and_header)


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
    file_id = f"{chit} CHIT {month} MONTHS"
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
    app.run(debug=True, host="0.0.0.0")
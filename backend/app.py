import os
import time
import pandas as pd
from flask import Flask, request, send_file, jsonify, render_template_string
from flask_cors import CORS
import subprocess
import tempfile
import shutil
import io
import traceback

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

@app.route('/')
def index():
    return send_file('../frontend/index.html')

def find_edge_binary():
    # Common paths for Edge
    paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    # Check PATH first
    if shutil.which("msedge"):
        return "msedge"
        
    for path in paths:
        if os.path.exists(path):
            return path
    return None

def generate_html_pdf(df, output_path, exam_name='Exam Name'):
    # HTML Template
    template = """
    <!DOCTYPE html>
    <html lang="hi">
    <head>
        <meta charset="UTF-8">
        <style>
            @font-face {
                font-family: 'Tiro Hindi';
                src: url('{{ font_path_regular }}') format('truetype');
                font-weight: normal;
                font-style: normal;
            }
            @font-face {
                font-family: 'Tiro Hindi';
                src: url('{{ font_path_italic }}') format('truetype');
                font-weight: normal;
                font-style: italic;
            }
            
            @page {
                margin: 40px;
                size: A4;
            }

            body { 
                font-family: 'Tiro Hindi', 'Mangal', 'Nirmala UI', sans-serif;
                margin: 0;
                padding: 0;
                font-size: 14px;
            }
            
            /* Table for Layout Control */
            table {
                width: 100%;
                border-collapse: collapse;
            }
            
            /* Header */
            thead th {
                border: none;
                text-align: right;
                font-weight: bold;
                font-size: 16px;
                padding-bottom: 10px;
                border-bottom: 2px solid #000;
            }
            
            /* Footer */
            tfoot td {
                border: none;
                text-align: center;
                font-size: 12px;
                font-weight: bold;
                color: #666;
                padding-top: 10px;
                border-top: 1px solid #ccc;
            }
            
            /* Questions Layout */
            .two-column-layout {
                column-count: 2;
                column-gap: 40px;
                column-rule: 1px solid #ccc;
                text-align: left;
                margin-top: 0; /* Removing margin as we now use spacer row in thead */
            }
            
            .question-block {
                break-inside: avoid;
                margin-bottom: 15px;
                padding-right: 10px;
            }
            
            .q-text { font-weight: bold; margin-bottom: 5px; }
            
            .options {
                margin-left: 20px;
            }
            .option { margin-bottom: 2px; }
            
            .answer-key-section {
                break-before: page;
                column-count: 1;
                margin-top: 20px;
            }
            
            .ans-item { margin-bottom: 10px; }
            .explanation { font-style: italic; color: #333; margin-left: 10px; }
            
            h1 { text-align: center; margin-bottom: 5px; }
            .meta { text-align: center; margin-bottom: 20px; font-size: 12px; color: #555; }
            
            /* Watermark */
            .watermark {
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%) rotate(0deg);
                opacity: 0.1;
                z-index: -1;
                width: 60%;
                max-width: 500px;
            }
        </style>
    </head>
    <body>
        <!-- Watermark -->
        <img class="watermark" src="{{ watermark_url }}" alt="Watermark">
        
        <table>
            <thead>
                <tr>
                    <th>
                        {{ exam_name }}
                    </th>
                </tr>
                <!-- Spacer Row: Repeats on every page to give breathing room -->
                <tr style="height: 30px;">
                    <th style="border: none;"></th>
                </tr>
            </thead>
            <tfoot>
                <tr>
                    <td>
                        Download app on play Store - Rankup Test
                    </td>
                </tr>
            </tfoot>
            <tbody>
                <tr>
                    <td>
                        <!-- Main Content -->
                        <div class="two-column-layout">
                            {% for row in questions %}
                            <div class="question-block">
                                <div class="q-text">{{ loop.index }}. {{ row.question }}</div>
                                <div class="options">
                                    <div class="option">A) {{ row.optionA }}</div>
                                    <div class="option">B) {{ row.optionB }}</div>
                                    <div class="option">C) {{ row.optionC }}</div>
                                    <div class="option">D) {{ row.optionD }}</div>
                                </div>
                            </div>
                            {% endfor %}
                        </div>

                        <div class="answer-key-section">
                            <h2>Answer Key & Explanations</h2>
                            <div style="border-bottom: 1px solid #000; margin-bottom: 20px;"></div>
                            {% for row in questions %}
                            <div class="ans-item">
                                <b>Q{{ loop.index }}:</b> {{ row.correctAnswer }}
                                {% if row.explanation %}
                                <div class="explanation">Exp: {{ row.explanation }}</div>
                                {% endif %}
                            </div>
                            {% endfor %}
                        </div>
                    </td>
                </tr>
            </tbody>
        </table>
    </body>
    </html>
    """
    
    # Absolute font paths for rendering
    base_dir = os.path.abspath(os.path.dirname(__file__))
    font_reg = os.path.join(base_dir, 'fonts', 'TiroDevanagariHindi-Regular.ttf').replace('\\', '/')
    font_it = os.path.join(base_dir, 'fonts', 'TiroDevanagariHindi-Italic.ttf').replace('\\', '/')
    
    # Prepare data
    records = df.to_dict('records')
    # Filter out NaN
    for r in records:
        for k, v in r.items():
            if pd.isna(v):
                r[k] = ""
    
    # Watermark logic
    watermark_path = os.path.join(base_dir, 'watermark.png')
    # If watermark file exists, use it. Otherwise use a placeholder (or empty)
    watermark_url = ''
    if os.path.exists(watermark_path):
        watermark_url = 'file:///' + watermark_path.replace('\\', '/')
    
    html_content = render_template_string(
        template, 
        questions=records, 
        exam_name=exam_name,
        date=pd.Timestamp.now().strftime("%Y-%m-%d"),
        font_path_regular='file:///' + font_reg,
        font_path_italic='file:///' + font_it,
        watermark_url=watermark_url
    )
    
    # Write to temp file
    fd, html_file = tempfile.mkstemp(suffix=".html")
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        f.write(html_content)
        
    edge_bin = find_edge_binary()
    if not edge_bin:
        raise Exception("Microsoft Edge not found. Please install Edge to generate PDFs.")
        
    # Convert Windows path to a proper file URI so Edge can load it reliably
    html_file_url = f"file:///{html_file.replace(os.sep, '/')}"
    
    # Create a temporary user data dir to isolate this Edge instance
    # This prevents Edge from delegating to an already running foreground process and exiting instantly
    user_data_dir = tempfile.mkdtemp(prefix="edge_temp_")
    
    # Edge Command
    # --print-to-pdf: Output file
    # --no-pdf-header-footer: Removes URL/Time from top/bottom
    cmd = [
        edge_bin,
        '--headless=new',
        '--disable-gpu',
        '--no-sandbox',
        '--no-first-run',
        '--no-pdf-header-footer',
        '--allow-file-access-from-files',  # Allows loading local fonts and watermark
        '--disable-extensions',
        '--disable-background-networking',
        '--disable-sync',
        '--disable-default-apps',
        '--disable-component-update',
        '--disable-features=msEdgeEnableNurturingFramework,RendererCodeIntegrity,msUndersideButton',
        f'--user-data-dir={user_data_dir}', # Isolates the process
        f'--print-to-pdf={output_path}',
        html_file_url
    ]
    
    try:
        # Provide CREATE_NO_WINDOW flag on Windows to detach from the parent console
        creation_flags = 0x08000000 if os.name == 'nt' else 0
        print(f"DEBUG: Running Edge command: {' '.join(cmd)}")
        result = subprocess.run(
            cmd, capture_output=True, text=True,
            creationflags=creation_flags, timeout=60
        )
        print(f"DEBUG: Edge exit code: {result.returncode}")
        if result.stdout:
            print(f"DEBUG: Edge stdout: {result.stdout}")
        if result.stderr:
            print(f"DEBUG: Edge stderr: {result.stderr}")
        
        # Edge may delegate the print job asynchronously — poll for the PDF
        max_wait = 15  # seconds
        poll_interval = 0.5
        waited = 0
        while waited < max_wait:
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                break
            time.sleep(poll_interval)
            waited += poll_interval
        
        pdf_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0
        print(f"DEBUG: PDF at {output_path}, size: {pdf_size} bytes (waited {waited}s)")
        
        if pdf_size == 0:
            err_msg = result.stderr or result.stdout or "No output from Edge"
            raise Exception(f"Edge PDF generation failed. Edge output: {err_msg}")
    finally:
        if os.path.exists(html_file):
            os.remove(html_file)
        try:
            shutil.rmtree(user_data_dir, ignore_errors=True)
        except Exception:
            pass

@app.route('/convert', methods=['POST'])
def convert_to_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        try:
            # Read Excel
            df = pd.read_excel(file)
            
            # Basic validation
            required_cols = ['question', 'optionA', 'optionB', 'optionC', 'optionD', 'correctAnswer']
            if not all(col in df.columns for col in required_cols):
                return jsonify({'error': f'Missing columns. Required: {required_cols}'}), 400
            
            # Generate PDF via Edge
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_pdf:
                pdf_path = tmp_pdf.name
                
            exam_name = request.form.get('exam_name', 'Exam Name')
            generate_html_pdf(df, pdf_path, exam_name)
            
            # Print file size for debugging
            print(f"DEBUG: PDF generated at {pdf_path}, size: {os.path.getsize(pdf_path)} bytes")
            
            # Send file and then delete (requires some tricky cleanup in Flask usually, 
            # using clean up callback or byteio if file is small. 
            # For simplicity, we read to memory and delete.)
            with open(pdf_path, 'rb') as f:
                data = io.BytesIO(f.read())
            
            os.remove(pdf_path)
            
            return send_file(
                data,
                as_attachment=True,
                download_name='question_paper.pdf',
                mimetype='application/pdf'
            )
            
        except Exception as e:
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)

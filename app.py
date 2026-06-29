import os
import re
import json
import shutil
import traceback
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from werkzeug.utils import secure_filename
from modules.pdf_extractor import PDFExtractor
from modules.ai_analyzer import AIAnalyzer
from modules.export_generator import ExportGenerator

# App configuration
app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['OUTPUT_FOLDER'] = os.path.join('outputs')

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'pdf'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file part'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'})
        
        if file and allowed_file(file.filename):
            # Clean old uploads
            for f in os.listdir(app.config['UPLOAD_FOLDER']):
                try:
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], f))
                except Exception:
                    pass
            
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Extract basic info
            extractor = PDFExtractor()
            info = extractor.get_pdf_info(filepath)
            
            return jsonify({
                'success': True,
                'filename': filename,
                'filepath': filepath,
                'info': info
            })
        else:
            return jsonify({'success': False, 'error': 'Invalid file type. Only PDF files are allowed.'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/extract', methods=['POST'])
def extract_data():
    try:
        data = request.get_json()
        filepath = data.get('filepath')
        extract_type = data.get('extract_type', 'all')
        
        if not filepath or not os.path.exists(filepath):
            return jsonify({'success': False, 'error': 'File not found'})
        
        extractor = PDFExtractor()
        result = extractor.extract(filepath, extract_type)
        
        return jsonify({'success': True, 'data': result})
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        filepath = data.get('filepath')
        prompt = data.get('prompt', '')
        extract_type = data.get('extract_type', 'all')
        
        if not filepath or not os.path.exists(filepath):
            return jsonify({'success': False, 'error': 'File not found'})
        
        if not prompt.strip():
            return jsonify({'success': False, 'error': 'Please provide a prompt for analysis'})
        
        # Extract data from PDF
        extractor = PDFExtractor()
        extracted_data = extractor.extract(filepath, extract_type)
        
        # Analyze with AI-like processing
        analyzer = AIAnalyzer()
        analysis_result = analyzer.analyze(extracted_data, prompt)
        
        return jsonify({
            'success': True,
            'analysis': analysis_result,
            'extracted_data': extracted_data
        })
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


@app.route('/export', methods=['POST'])
def export_file():
    try:
        data = request.get_json()
        filepath = data.get('filepath')
        output_format = data.get('format', 'pdf')
        analysis_result = data.get('analysis', {})
        extracted_data = data.get('extracted_data', {})
        
        if not filepath or not os.path.exists(filepath):
            return jsonify({'success': False, 'error': 'File not found'})
        
        generator = ExportGenerator()
        output_path = generator.generate(
            filepath,
            output_format,
            analysis_result,
            extracted_data,
            app.config['OUTPUT_FOLDER']
        )
        
        if not os.path.exists(output_path):
            return jsonify({'success': False, 'error': 'Failed to generate output file'})
        
        filename = os.path.basename(output_path)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'download_url': f'/download/{filename}',
            'output_path': output_path
        })
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


@app.route('/download/<filename>')
def download_file(filename):
    try:
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        if not os.path.exists(output_path):
            return jsonify({'success': False, 'error': 'File not found'})
        
        return send_file(output_path, as_attachment=True)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/preview/<filename>')
def preview_file(filename):
    try:
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        if not os.path.exists(output_path):
            return jsonify({'success': False, 'error': 'File not found'})
        
        ext = filename.rsplit('.', 1)[1].lower()
        
        if ext == 'png':
            return send_file(output_path, mimetype='image/png')
        elif ext == 'pdf':
            return send_file(output_path, mimetype='application/pdf')
        elif ext == 'xlsx':
            return send_file(output_path, as_attachment=True, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        elif ext == 'docx':
            return send_file(output_path, as_attachment=True, mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        elif ext == 'pptx':
            return send_file(output_path, as_attachment=True, mimetype='application/vnd.openxmlformats-officedocument.presentationml.presentation')
        else:
            return send_file(output_path, as_attachment=True)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/cleanup', methods=['POST'])
def cleanup():
    try:
        # Clean uploads and outputs older than 1 hour
        cutoff = datetime.now().timestamp() - 3600
        
        for folder in [app.config['UPLOAD_FOLDER'], app.config['OUTPUT_FOLDER']]:
            for f in os.listdir(folder):
                path = os.path.join(folder, f)
                try:
                    if os.path.getmtime(path) < cutoff:
                        os.remove(path)
                except Exception:
                    pass
        
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

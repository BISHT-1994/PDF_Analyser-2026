# PDF Analyzer - Smart PDF Extraction & Analysis Tool

A complete web application for extracting, analyzing, and exporting data from PDF files. Built with Flask and a modern interactive UI.

## Features

- **PDF Upload** - Drag & drop or browse to upload PDF files (up to 50MB)
- **Smart Extraction** - Extract text, tables, numbers, code, headers, and images
- **AI Analysis** - Natural language prompts to analyze PDF content
- **Multi-Format Export** - Export results as PDF, DOCX, Excel, PPT, or PNG
- **Interactive UI** - Modern, responsive, user-friendly interface
- **Download** - One-click download of generated output files

## Extraction Types

| Type | Description |
|------|-------------|
| All Data | Extract everything from the PDF |
| Text | All text content, paragraphs, sentences |
| Tables | Structured data tables with headers |
| Numbers | Statistics, percentages, dates, currencies |
| Code | Code blocks, scripts, technical content |
| Structure | Document outline, headers, sections |

## Analysis Capabilities

- **Summarize** - Get key points and document overview
- **Extract** - Pull specific data (emails, dates, numbers)
- **Find** - Search for keywords and phrases
- **Calculate** - Compute statistics on numerical data
- **Compare** - Compare tables or sections
- **Organize** - Structure data by sections
- **Filter** - Select specific content based on criteria

## Export Formats

| Format | Use Case |
|--------|----------|
| PDF | Professional report |
| DOCX | Editable Word document |
| Excel | Data tables and statistics |
| PPT | Presentation slides |
| PNG | Image infographic |

## Project Structure

```
pdf-analyzer/
├── app.py                  # Flask backend entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── modules/
│   ├── __init__.py
│   ├── pdf_extractor.py   # PDF extraction engine
│   ├── ai_analyzer.py     # AI analysis logic
│   └── export_generator.py # Export generators
├── templates/
│   └── index.html         # Main UI template
├── static/
│   ├── css/
│   │   └── style.css      # Application styles
│   ├── js/
│   │   └── app.js         # Frontend application logic
│   └── uploads/           # Uploaded PDF files
└── outputs/               # Generated output files
```

## Setup & Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

> Note: For table extraction with `camelot-py`, you may need to install `ghostscript` and `tkinter` on your system.

### 2. Run the Application

```bash
python app.py
```

The application will start at `http://localhost:5000`

### 3. Open in VS Code

1. Open VS Code
2. Go to **File > Open Folder...**
3. Select the `pdf-analyzer` directory
4. Use the built-in terminal to run `python app.py`

## Usage Guide

### Step 1: Upload PDF
- Drag and drop a PDF file or click to browse
- Wait for upload confirmation

### Step 2: Select Extraction Type
- Choose what type of data to extract from the PDF
- Options: All Data, Text, Tables, Numbers, Code, Structure

### Step 3: Enter Your Prompt
- Type what you want to do with the PDF data
- Use quick suggestion chips for common tasks
- Examples:
  - "Summarize the key points and extract all financial data"
  - "Find all email addresses and phone numbers"
  - "Extract tables with sales data and calculate totals"
  - "Organize the document by sections and find all dates"

### Step 4: Export Results
- Select output format (PDF, DOCX, Excel, PPT, PNG)
- Click download to save the generated file

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main application UI |
| `/upload` | POST | Upload a PDF file |
| `/extract` | POST | Extract data from uploaded PDF |
| `/analyze` | POST | Analyze data with natural language prompt |
| `/export` | POST | Generate output file in selected format |
| `/download/<filename>` | GET | Download generated file |
| `/preview/<filename>` | GET | Preview generated file |
| `/cleanup` | POST | Clean old files |

## Dependencies

- **Flask** - Web framework
- **PyPDF2** - PDF reading
- **pdfplumber** - Text and table extraction
- **PyMuPDF (fitz)** - Advanced PDF processing and image extraction
- **camelot-py** - Table extraction (requires ghostscript)
- **pandas** - Data processing
- **openpyxl** - Excel generation
- **python-docx** - Word document generation
- **python-pptx** - PowerPoint generation
- **reportlab** - PDF generation
- **Pillow** - Image generation
- **pdf2image** - PDF to image conversion

## Tips

- For best table extraction, ensure PDFs contain text-based tables rather than scanned images
- Use specific prompts for better analysis results
- Large PDFs may take longer to process
- Exported files are stored in the `outputs/` directory and cleaned up periodically

## License

This project is open source and free to use.

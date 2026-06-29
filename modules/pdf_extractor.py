import os
import re
import json
import traceback
from typing import Dict, List, Any, Optional

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

try:
    import pandas as pd
except ImportError:
    pd = None

try:
    import camelot
except ImportError:
    camelot = None

try:
    from pdf2image import convert_from_path
except ImportError:
    convert_from_path = None


class PDFExtractor:
    """Extract various types of data from PDF files"""

    def _require_pdfplumber(self):
        if pdfplumber is None:
            raise ImportError("pdfplumber is required. Install it with: pip install pdfplumber")

    def _require_pymupdf(self):
        if fitz is None:
            raise ImportError("PyMuPDF (fitz) is required. Install it with: pip install pymupdf")

    def _require_camelot(self):
        if camelot is None:
            raise ImportError("camelot-py is required for table extraction. Install it with: pip install camelot-py")

    def get_pdf_info(self, filepath: str) -> Dict:
        """Get basic PDF information"""
        try:
            self._require_pdfplumber()
            with pdfplumber.open(filepath) as pdf:
                info = {
                    'pages': len(pdf.pages),
                    'file_size': os.path.getsize(filepath),
                    'file_size_human': self._human_readable_size(os.path.getsize(filepath))
                }

                # Try to get metadata
                if pdf.metadata:
                    info['title'] = pdf.metadata.get('Title', 'N/A')
                    info['author'] = pdf.metadata.get('Author', 'N/A')
                    info['creator'] = pdf.metadata.get('Creator', 'N/A')
                    info['producer'] = pdf.metadata.get('Producer', 'N/A')

                return info
        except ImportError as e:
            return {'pages': 'Unknown', 'error': str(e)}
        except Exception as e:
            return {'pages': 'Unknown', 'error': str(e)}
    
    def _human_readable_size(self, size_bytes: int) -> str:
        """Convert bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def extract(self, filepath: str, extract_type: str = 'all') -> Dict:
        """Extract data from PDF based on type"""
        result = {}
        
        if extract_type in ('all', 'text', 'content'):
            result['text'] = self._extract_text(filepath)
        
        if extract_type in ('all', 'tables', 'data'):
            result['tables'] = self._extract_tables(filepath)
        
        if extract_type in ('all', 'numbers', 'stats'):
            result['numbers'] = self._extract_numbers(filepath)
        
        if extract_type in ('all', 'code', 'scripts'):
            result['code'] = self._extract_code(filepath)
        
        if extract_type in ('all', 'headers', 'structure'):
            result['headers'] = self._extract_headers(filepath)
        
        if extract_type in ('all', 'images', 'media'):
            result['images'] = self._extract_image_info(filepath)
        
        if extract_type == 'all':
            result['metadata'] = self.get_pdf_info(filepath)
        
        return result
    
    def _extract_text(self, filepath: str) -> Dict:
        """Extract all text content from PDF"""
        try:
            self._require_pdfplumber()
            full_text = []
            page_texts = []
            
            with pdfplumber.open(filepath) as pdf:
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text:
                        page_texts.append({
                            'page': i + 1,
                            'text': text,
                            'length': len(text)
                        })
                        full_text.append(text)
            
            all_text = '\n\n'.join(full_text)
            
            # Extract paragraphs
            paragraphs = [p.strip() for p in all_text.split('\n\n') if p.strip()]
            
            # Extract sentences (rough)
            sentences = re.split(r'(?<=[.!?])\s+', all_text)
            sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
            
            return {
                'full_text': all_text[:10000] + ('...' if len(all_text) > 10000 else ''),
                'pages': page_texts,
                'paragraph_count': len(paragraphs),
                'sentence_count': len(sentences),
                'word_count': len(all_text.split()),
                'character_count': len(all_text),
                'paragraphs': paragraphs[:50],  # First 50 paragraphs
                'sentences': sentences[:100]    # First 100 sentences
            }
        
        except Exception as e:
            return {'error': str(e), 'full_text': ''}
    
    def _extract_tables(self, filepath: str) -> List[Dict]:
        """Extract tables from PDF using multiple methods"""
        tables = []
        
        # Method 1: pdfplumber
        try:
            self._require_pdfplumber()
            with pdfplumber.open(filepath) as pdf:
                for i, page in enumerate(pdf.pages):
                    page_tables = page.extract_tables()
                    for j, table in enumerate(page_tables):
                        if table and len(table) > 1:
                            # Convert to structured format
                            headers = table[0] if table[0] else [f'Col_{k}' for k in range(len(table[0]))]
                            data_rows = table[1:] if len(table) > 1 else []
                            
                            tables.append({
                                'page': i + 1,
                                'table_index': j + 1,
                                'method': 'pdfplumber',
                                'headers': headers,
                                'rows': data_rows,
                                'row_count': len(data_rows),
                                'column_count': len(headers)
                            })
        except Exception as e:
            print(f"pdfplumber table extraction error: {e}")
        
        # Method 2: camelot (if available)
        try:
            self._require_camelot()
            camelot_tables = camelot.read_pdf(filepath, pages='all', flavor='lattice')
            if len(camelot_tables) == 0:
                camelot_tables = camelot.read_pdf(filepath, pages='all', flavor='stream')
            
            for i, table in enumerate(camelot_tables):
                df = table.df
                if not df.empty and len(df) > 1:
                    headers = df.iloc[0].tolist()
                    data_rows = df.iloc[1:].values.tolist()
                    
                    tables.append({
                        'page': table.page,
                        'table_index': i + 1,
                        'method': 'camelot',
                        'headers': headers,
                        'rows': data_rows,
                        'row_count': len(data_rows),
                        'column_count': len(headers)
                    })
        except Exception as e:
            print(f"Camelot table extraction error: {e}")
        
        # Deduplicate tables (basic check)
        seen = set()
        unique_tables = []
        for t in tables:
            key = (t['page'], t['row_count'], t['column_count'])
            if key not in seen:
                seen.add(key)
                unique_tables.append(t)
        
        return unique_tables[:20]  # Limit to 20 tables
    
    def _extract_numbers(self, filepath: str) -> Dict:
        """Extract numbers, statistics, and numerical data from PDF"""
        try:
            text_data = self._extract_text(filepath)
            all_text = text_data.get('full_text', '')
            
            # Extract various number patterns
            # Integers and decimals
            all_numbers = re.findall(r'-?\d{1,3}(?:,\d{3})*\.?\d*', all_text)
            all_numbers = [n.replace(',', '') for n in all_numbers]
            
            # Percentages
            percentages = re.findall(r'(\d+\.?\d*)\s*%', all_text)
            
            # Currency values
            currencies = re.findall(r'[\$€£¥]\s*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)', all_text)
            
            # Dates
            dates = re.findall(r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2})\b', all_text)
            
            # Phone numbers
            phones = re.findall(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', all_text)
            
            # Email addresses
            emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', all_text)
            
            # URLs
            urls = re.findall(r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?', all_text)
            
            # Extract statistics keywords
            stat_keywords = re.findall(r'(?:average|mean|median|total|sum|count|maximum|minimum|max|min|std|deviation|variance|percentage|ratio|growth|decline|increase|decrease)[\s\w:]*(?:\d+\.?\d*)', all_text, re.IGNORECASE)
            
            return {
                'numbers_count': len(all_numbers),
                'numbers_sample': all_numbers[:50],
                'percentages': percentages[:30],
                'currencies': currencies[:30],
                'dates': dates[:30],
                'phone_numbers': phones[:20],
                'emails': emails[:20],
                'urls': urls[:20],
                'statistical_mentions': stat_keywords[:30],
                'all_numbers': all_numbers[:100]
            }
        
        except Exception as e:
            return {'error': str(e)}
    
    def _extract_code(self, filepath: str) -> Dict:
        """Extract code blocks, scripts, and structured text from PDF"""
        try:
            text_data = self._extract_text(filepath)
            all_text = text_data.get('full_text', '')
            
            # Look for code-like patterns
            code_blocks = []
            
            # Indentation-based code blocks (4+ spaces or tabs)
            lines = all_text.split('\n')
            current_block = []
            for line in lines:
                if line.startswith('    ') or line.startswith('\t'):
                    current_block.append(line)
                else:
                    if len(current_block) >= 3:
                        code_blocks.append('\n'.join(current_block))
                    current_block = []
            
            if len(current_block) >= 3:
                code_blocks.append('\n'.join(current_block))
            
            # Look for common code patterns
            code_patterns = {
                'python': re.findall(r'(?:def\s+\w+|class\s+\w+|import\s+\w+|from\s+\w+\s+import|print\(|if\s+\w+\s*:|for\s+\w+\s+in\s+|while\s+\w+)', all_text),
                'javascript': re.findall(r'(?:function\s+\w+|const\s+\w+|let\s+\w+|var\s+\w+|=>\s*\{|document\.|window\.|console\.)', all_text),
                'sql': re.findall(r'(?:SELECT\s+.*FROM|INSERT\s+INTO|UPDATE\s+\w+\s+SET|DELETE\s+FROM|CREATE\s+TABLE|JOIN\s+\w+)', all_text, re.IGNORECASE),
                'json': re.findall(r'(?:\{\s*"\w+":|"\w+":\s*"\w+")', all_text),
                'xml_html': re.findall(r'(?:<\w+>.*</\w+>|<\w+\s+\w+=|<\w+\s*/?>)', all_text),
                'bash': re.findall(r'(?:#!/bin/|sudo\s|chmod\s|ls\s|cd\s|grep\s|awk\s|cat\s)', all_text)
            }
            
            # Detect code snippets in backticks (Markdown style)
            backtick_code = re.findall(r'`([^`]+)`', all_text)
            
            # Detect triple backtick code blocks
            triple_backtick = re.findall(r'```(?:\w+)?\n(.*?)```', all_text, re.DOTALL)
            
            return {
                'code_blocks_found': len(code_blocks),
                'code_blocks': code_blocks[:10],
                'language_patterns': {k: len(v) for k, v in code_patterns.items()},
                'language_matches': {k: v[:10] for k, v in code_patterns.items()},
                'inline_code': backtick_code[:20],
                'fenced_code_blocks': triple_backtick[:5],
                'detected_languages': [lang for lang, matches in code_patterns.items() if len(matches) > 0]
            }
        
        except Exception as e:
            return {'error': str(e)}
    
    def _extract_headers(self, filepath: str) -> Dict:
        """Extract headers, titles, and document structure"""
        try:
            self._require_pdfplumber()
            with pdfplumber.open(filepath) as pdf:
                headers = []
                structure = []
                
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if not text:
                        continue
                    
                    lines = text.split('\n')
                    page_structure = []
                    
                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue
                        
                        # Detect headers based on patterns
                        header_level = None
                        
                        # Numbered headers (1., 1.1, 1.1.1, etc.)
                        if re.match(r'^\d+(\.\d+)*\s+', line):
                            header_level = 1 if line.startswith('1.') or re.match(r'^\d+\s+', line) else 2
                        
                        # Chapter/Section headers
                        elif re.match(r'^(Chapter|Section|Part|Appendix)\s+\d+', line, re.IGNORECASE):
                            header_level = 1
                        
                        # ALL CAPS short lines (likely headers)
                        elif line.isupper() and len(line) < 100 and len(line) > 3:
                            header_level = 2
                        
                        # Lines with specific formatting (bold-like in PDF)
                        elif line.endswith(':') and len(line) < 80 and len(line) > 3:
                            header_level = 3
                        
                        # Bullet points
                        elif re.match(r'^[\-\*•\+]\s+', line):
                            page_structure.append({'type': 'bullet', 'text': line, 'level': 1})
                            continue
                        
                        # Numbered lists
                        elif re.match(r'^\d+\.\s+', line):
                            page_structure.append({'type': 'numbered', 'text': line, 'level': 1})
                            continue
                        
                        if header_level:
                            header_info = {
                                'page': i + 1,
                                'level': header_level,
                                'text': line,
                                'type': 'header'
                            }
                            headers.append(header_info)
                            page_structure.append(header_info)
                        else:
                            page_structure.append({'type': 'text', 'text': line[:100]})
                    
                    structure.append({
                        'page': i + 1,
                        'elements': page_structure[:20]  # Limit per page
                    })
                
                return {
                    'headers': headers,
                    'header_count': len(headers),
                    'structure': structure[:5],  # First 5 pages
                    'toc_candidates': [h for h in headers if h['level'] == 1]
                }
        
        except Exception as e:
            return {'error': str(e)}
    
    def _extract_image_info(self, filepath: str) -> Dict:
        """Extract image information from PDF"""
        try:
            self._require_pymupdf()
            doc = fitz.open(filepath)
            images = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                image_list = page.get_images()
                
                for img_index, img in enumerate(image_list, start=1):
                    xref = img[0]
                    pix = fitz.Pixmap(doc, xref)
                    
                    image_info = {
                        'page': page_num + 1,
                        'index': img_index,
                        'width': pix.width,
                        'height': pix.height,
                        'colorspace': pix.colorspace.name if pix.colorspace else 'unknown',
                        'format': 'png' if pix.n < 4 else 'jpeg'
                    }
                    
                    images.append(image_info)
            
            doc.close()
            
            return {
                'total_images': len(images),
                'images': images[:20],
                'pages_with_images': len(set(img['page'] for img in images))
            }
        
        except Exception as e:
            return {'error': str(e)}

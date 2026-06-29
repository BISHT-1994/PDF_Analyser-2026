import re
import json
import random
from typing import Dict, Any, List


class AIAnalyzer:
    """AI-like analyzer that processes PDF data based on user prompts"""
    
    def __init__(self):
        self.analysis_templates = self._load_templates()
    
    def _load_templates(self):
        return {
            'summary': self._summarize,
            'extract': self._extract_specific,
            'compare': self._compare_data,
            'find': self._find_items,
            'calculate': self._calculate_stats,
            'organize': self._organize_data,
            'filter': self._filter_data,
            'convert': self._convert_format,
            'default': self._default_analysis
        }
    
    def analyze(self, extracted_data: Dict, prompt: str) -> Dict:
        """Analyze extracted data based on user prompt"""
        prompt_lower = prompt.lower()
        
        # Determine analysis type from prompt
        analysis_type = self._detect_analysis_type(prompt_lower)
        
        # Route to appropriate analyzer
        handler = self.analysis_templates.get(analysis_type, self._default_analysis)
        result = handler(extracted_data, prompt)
        
        return {
            'analysis_type': analysis_type,
            'prompt': prompt,
            'result': result,
            'data_summary': self._create_data_summary(extracted_data)
        }
    
    def _detect_analysis_type(self, prompt: str) -> str:
        """Detect the type of analysis requested"""
        if any(w in prompt for w in ['summary', 'summarize', 'overview', 'brief', 'recap']):
            return 'summary'
        elif any(w in prompt for w in ['extract', 'pull out', 'get', 'retrieve', 'collect', 'gather']):
            return 'extract'
        elif any(w in prompt for w in ['compare', 'versus', 'vs', 'difference', 'similarity', 'contrast']):
            return 'compare'
        elif any(w in prompt for w in ['find', 'search', 'locate', 'look for', 'identify', 'spot']):
            return 'find'
        elif any(w in prompt for w in ['calculate', 'compute', 'sum', 'average', 'total', 'count', 'statistics', 'stats']):
            return 'calculate'
        elif any(w in prompt for w in ['organize', 'sort', 'arrange', 'structure', 'group', 'categorize']):
            return 'organize'
        elif any(w in prompt for w in ['filter', 'only', 'select', 'specific', 'certain', 'particular']):
            return 'filter'
        elif any(w in prompt for w in ['convert', 'transform', 'change', 'turn into', 'make it', 'format as']):
            return 'convert'
        else:
            return 'default'
    
    def _create_data_summary(self, data: Dict) -> Dict:
        """Create a summary of available data"""
        summary = {}
        for key, value in data.items():
            if isinstance(value, list):
                summary[key] = {'type': 'list', 'count': len(value)}
            elif isinstance(value, dict):
                summary[key] = {'type': 'dict', 'keys': list(value.keys())}
            elif isinstance(value, str):
                summary[key] = {'type': 'text', 'length': len(value)}
            else:
                summary[key] = {'type': 'other'}
        return summary
    
    def _summarize(self, data: Dict, prompt: str) -> Dict:
        """Generate a summary of the PDF content"""
        text_data = data.get('text', {})
        full_text = text_data.get('full_text', '')
        
        # Extract key sentences (simple heuristic)
        sentences = text_data.get('sentences', [])
        
        # Get first sentence of each paragraph as key points
        paragraphs = text_data.get('paragraphs', [])
        key_points = []
        for p in paragraphs[:10]:
            sentences_in_p = re.split(r'(?<=[.!?])\s+', p)
            if sentences_in_p:
                key_points.append(sentences_in_p[0])
        
        # Get headers for structure
        headers_data = data.get('headers', {})
        headers = headers_data.get('headers', [])
        
        return {
            'operation': 'Summary',
            'key_points': key_points[:15],
            'document_structure': [h['text'] for h in headers[:20]],
            'statistics': {
                'total_pages': len(data.get('text', {}).get('pages', [])),
                'paragraphs': text_data.get('paragraph_count', 0),
                'sentences': text_data.get('sentence_count', 0),
                'words': text_data.get('word_count', 0),
                'tables_found': len(data.get('tables', [])),
                'images_found': data.get('images', {}).get('total_images', 0)
            },
            'summary_text': self._generate_summary_text(full_text, headers, key_points)
        }
    
    def _extract_specific(self, data: Dict, prompt: str) -> Dict:
        """Extract specific items based on prompt"""
        text_data = data.get('text', {})
        full_text = text_data.get('full_text', '')
        
        # Extract what user is looking for
        target_types = []
        if any(w in prompt.lower() for w in ['email', 'emails', 'e-mail']):
            target_types.append('emails')
        if any(w in prompt.lower() for w in ['phone', 'contact', 'telephone']):
            target_types.append('phones')
        if any(w in prompt.lower() for w in ['date', 'dates', 'time', 'deadline']):
            target_types.append('dates')
        if any(w in prompt.lower() for w in ['number', 'numbers', 'amount', 'value', 'price']):
            target_types.append('numbers')
        if any(w in prompt.lower() for w in ['url', 'link', 'website', 'web']):
            target_types.append('urls')
        if any(w in prompt.lower() for w in ['name', 'names', 'person']):
            target_types.append('names')
        if any(w in prompt.lower() for w in ['table', 'tables', 'data', 'spreadsheet']):
            target_types.append('tables')
        
        if not target_types:
            # Default: extract all structured data
            target_types = ['emails', 'phones', 'dates', 'numbers', 'urls']
        
        extracted = {}
        numbers_data = data.get('numbers', {})
        
        for target in target_types:
            if target == 'emails':
                extracted['emails'] = numbers_data.get('emails', [])
            elif target == 'phones':
                extracted['phone_numbers'] = numbers_data.get('phone_numbers', [])
            elif target == 'dates':
                extracted['dates'] = numbers_data.get('dates', [])
            elif target == 'numbers':
                extracted['numbers'] = numbers_data.get('all_numbers', [])
            elif target == 'urls':
                extracted['urls'] = numbers_data.get('urls', [])
            elif target == 'tables':
                extracted['tables'] = data.get('tables', [])
        
        return {
            'operation': 'Specific Extraction',
            'target_types': target_types,
            'extracted_data': extracted,
            'total_items': sum(len(v) if isinstance(v, list) else 0 for v in extracted.values())
        }
    
    def _find_items(self, data: Dict, prompt: str) -> Dict:
        """Find specific items or keywords in the document"""
        text_data = data.get('text', {})
        full_text = text_data.get('full_text', '')
        
        # Extract keywords from prompt (words after 'find' or 'search for')
        keywords = self._extract_keywords_from_prompt(prompt)
        
        if not keywords:
            # Try to find important words in the prompt itself
            words = re.findall(r'\b\w{4,}\b', prompt.lower())
            keywords = [w for w in words if w not in ['find', 'search', 'look', 'document', 'this', 'that', 'with', 'from', 'have', 'need']]
        
        results = {}
        for keyword in keywords:
            matches = []
            # Search in text
            pattern = re.compile(r'[^.]*\b' + re.escape(keyword) + r'\b[^.]*\.', re.IGNORECASE)
            sentences_with_keyword = pattern.findall(full_text)
            
            # Search in headers
            headers = data.get('headers', {}).get('headers', [])
            matching_headers = [h for h in headers if keyword.lower() in h['text'].lower()]
            
            # Search in tables
            tables = data.get('tables', [])
            matching_tables = []
            for t in tables:
                for row in t.get('rows', []):
                    if any(keyword.lower() in str(cell).lower() for cell in row):
                        matching_tables.append({
                            'table_index': t['table_index'],
                            'page': t['page'],
                            'row': row
                        })
                        break
            
            results[keyword] = {
                'sentences': sentences_with_keyword[:10],
                'headers': [{'text': h['text'], 'page': h['page']} for h in matching_headers[:5]],
                'tables': matching_tables[:5],
                'total_occurrences': len(sentences_with_keyword)
            }
        
        return {
            'operation': 'Search/Find',
            'keywords': keywords,
            'results': results,
            'total_matches': sum(r['total_occurrences'] for r in results.values())
        }
    
    def _extract_keywords_from_prompt(self, prompt: str) -> List[str]:
        """Extract search keywords from a natural language prompt"""
        # Look for quoted phrases
        quoted = re.findall(r'"([^"]+)"', prompt)
        if quoted:
            return quoted
        
        # Look for words after prepositions
        after_patterns = [
            r'(?:find|search|look)\s+for\s+([\w\s]+?)(?:\s+in\s+|\s+the\s+|$)',
            r'(?:find|search|look)\s+([\w\s]+?)(?:\s+in\s+|\s+the\s+|$)',
            r'(?:about|regarding|concerning|related to)\s+([\w\s]+?)(?:\s+in\s+|$)',
        ]
        
        for pattern in after_patterns:
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                return [match.group(1).strip()]
        
        return []
    
    def _calculate_stats(self, data: Dict, prompt: str) -> Dict:
        """Calculate statistics from extracted numerical data"""
        numbers_data = data.get('numbers', {})
        numbers = numbers_data.get('all_numbers', [])
        
        # Convert to floats where possible
        numeric_values = []
        for n in numbers:
            try:
                numeric_values.append(float(n))
            except ValueError:
                pass
        
        if not numeric_values:
            return {'operation': 'Statistics', 'error': 'No numeric values found'}
        
        # Calculate statistics
        import statistics
        
        stats = {
            'operation': 'Statistics',
            'count': len(numeric_values),
            'sum': round(sum(numeric_values), 4),
            'mean': round(statistics.mean(numeric_values), 4) if len(numeric_values) > 0 else 0,
            'median': round(statistics.median(numeric_values), 4) if len(numeric_values) > 0 else 0,
            'min': round(min(numeric_values), 4),
            'max': round(max(numeric_values), 4),
            'range': round(max(numeric_values) - min(numeric_values), 4),
            'std_dev': round(statistics.stdev(numeric_values), 4) if len(numeric_values) > 1 else 0,
            'values_sample': numeric_values[:20]
        }
        
        # Check for table data that might contain numbers
        tables = data.get('tables', [])
        table_stats = []
        for table in tables:
            for row in table.get('rows', [])[:10]:
                numeric_row = []
                for cell in row:
                    try:
                        numeric_row.append(float(str(cell).replace(',', '')))
                    except ValueError:
                        numeric_row.append(None)
                table_stats.append(numeric_row)
        
        stats['table_data'] = table_stats[:5]
        
        return stats
    
    def _compare_data(self, data: Dict, prompt: str) -> Dict:
        """Compare data across different sections or tables"""
        tables = data.get('tables', [])
        text_data = data.get('text', {})
        
        if len(tables) >= 2:
            # Compare tables
            comparison = []
            for i, table in enumerate(tables[:5]):
                comparison.append({
                    'table_index': i + 1,
                    'page': table['page'],
                    'headers': table['headers'],
                    'row_count': table['row_count'],
                    'column_count': table['column_count'],
                    'sample_row': table['rows'][0] if table['rows'] else []
                })
            
            return {
                'operation': 'Comparison',
                'type': 'Table Comparison',
                'tables_compared': len(comparison),
                'comparison_data': comparison
            }
        
        else:
            # Compare page content
            pages = text_data.get('pages', [])
            page_comparison = []
            for page in pages[:5]:
                page_comparison.append({
                    'page': page['page'],
                    'text_length': page['length'],
                    'word_count': len(page['text'].split())
                })
            
            return {
                'operation': 'Comparison',
                'type': 'Page Comparison',
                'pages_compared': len(page_comparison),
                'comparison_data': page_comparison
            }
    
    def _organize_data(self, data: Dict, prompt: str) -> Dict:
        """Organize data into a structured format"""
        tables = data.get('tables', [])
        text_data = data.get('text', {})
        
        organized = {
            'operation': 'Organization',
            'sections': []
        }
        
        # Organize by headers
        headers = data.get('headers', {}).get('headers', [])
        if headers:
            current_section = None
            for h in headers:
                if h['level'] == 1:
                    current_section = {
                        'title': h['text'],
                        'page': h['page'],
                        'subsections': []
                    }
                    organized['sections'].append(current_section)
                elif current_section and h['level'] == 2:
                    current_section['subsections'].append({
                        'title': h['text'],
                        'page': h['page']
                    })
        
        # Add table organization
        if tables:
            organized['tables'] = []
            for t in tables:
                organized['tables'].append({
                    'page': t['page'],
                    'headers': t['headers'],
                    'row_count': t['row_count'],
                    'data': t['rows'][:5]
                })
        
        # Add text organization by page
        pages = text_data.get('pages', [])
        organized['pages'] = []
        for p in pages[:10]:
            organized['pages'].append({
                'page': p['page'],
                'content_preview': p['text'][:200] + '...' if len(p['text']) > 200 else p['text']
            })
        
        return organized
    
    def _filter_data(self, data: Dict, prompt: str) -> Dict:
        """Filter data based on criteria"""
        text_data = data.get('text', {})
        full_text = text_data.get('full_text', '')
        
        # Determine filter criteria from prompt
        criteria = self._detect_filter_criteria(prompt)
        
        filtered = {
            'operation': 'Filter',
            'criteria': criteria,
            'results': []
        }
        
        paragraphs = text_data.get('paragraphs', [])
        
        for p in paragraphs:
            match = False
            for criterion in criteria:
                if criterion.lower() in p.lower():
                    match = True
                    break
            
            if match:
                filtered['results'].append(p)
        
        # Filter tables
        tables = data.get('tables', [])
        filtered_tables = []
        for t in tables:
            for row in t.get('rows', []):
                for cell in row:
                    for criterion in criteria:
                        if str(criterion).lower() in str(cell).lower():
                            filtered_tables.append(t)
                            break
                    else:
                        continue
                    break
        
        filtered['matching_tables'] = filtered_tables[:5]
        filtered['total_matches'] = len(filtered['results'])
        
        return filtered
    
    def _detect_filter_criteria(self, prompt: str) -> List[str]:
        """Detect filter criteria from prompt"""
        criteria = []
        
        # Look for quoted terms
        quoted = re.findall(r'"([^"]+)"', prompt)
        criteria.extend(quoted)
        
        # Look for "only" or "with" patterns
        only_match = re.search(r'only\s+([\w\s]+?)(?:\s+and\s+|\s+or\s+|$)', prompt, re.IGNORECASE)
        if only_match:
            criteria.append(only_match.group(1).strip())
        
        # Look for specific keywords that might be criteria
        if not criteria:
            words = re.findall(r'\b\w{4,}\b', prompt.lower())
            keywords = [w for w in words if w not in ['only', 'filter', 'show', 'with', 'that', 'have', 'data', 'from', 'this', 'document', 'extract', 'give', 'please', 'need', 'want']]
            if keywords:
                criteria.extend(keywords[:3])
        
        return criteria if criteria else ['all']
    
    def _convert_format(self, data: Dict, prompt: str) -> Dict:
        """Prepare data for format conversion"""
        return {
            'operation': 'Format Conversion',
            'available_data': list(data.keys()),
            'data_ready': True
        }
    
    def _default_analysis(self, data: Dict, prompt: str) -> Dict:
        """Default analysis when no specific type is detected"""
        text_data = data.get('text', {})
        full_text = text_data.get('full_text', '')
        
        # Perform a general analysis
        key_sentences = []
        sentences = text_data.get('sentences', [])
        
        # Find sentences that might be relevant to the prompt
        prompt_words = set(re.findall(r'\b\w{4,}\b', prompt.lower()))
        prompt_words = {w for w in prompt_words if w not in ['what', 'does', 'this', 'document', 'have', 'tell', 'about', 'show', 'give', 'me', 'please', 'need', 'want', 'from', 'with', 'have', 'that', 'which', 'where', 'when', 'how', 'why', 'who']}
        
        for s in sentences[:100]:
            s_lower = s.lower()
            if any(w in s_lower for w in prompt_words):
                key_sentences.append(s)
        
        # If no specific matches, provide general insights
        if not key_sentences and sentences:
            key_sentences = sentences[:15]
        
        return {
            'operation': 'General Analysis',
            'analysis': 'Based on your request, here is the analysis of the document.',
            'key_sentences': key_sentences[:20],
            'document_type': self._detect_document_type(data),
            'main_topics': self._extract_topics(data)
        }
    
    def _detect_document_type(self, data: Dict) -> str:
        """Try to detect the type of document"""
        text_data = data.get('text', {})
        full_text = text_data.get('full_text', '')[:5000].lower()
        
        doc_types = {
            'invoice': ['invoice', 'bill', 'payment', 'total amount', 'due date'],
            'resume': ['resume', 'cv', 'experience', 'skills', 'education', 'profile'],
            'report': ['report', 'analysis', 'findings', 'conclusion', 'executive summary'],
            'scientific': ['abstract', 'introduction', 'methodology', 'results', 'conclusion', 'references'],
            'manual': ['manual', 'guide', 'instruction', 'step', 'how to', 'procedure'],
            'contract': ['agreement', 'contract', 'terms', 'conditions', 'party', 'hereby'],
            'financial': ['financial', 'balance sheet', 'income statement', 'revenue', 'expenses', 'profit', 'loss']
        }
        
        scores = {}
        for doc_type, keywords in doc_types.items():
            score = sum(1 for kw in keywords if kw in full_text)
            scores[doc_type] = score
        
        if scores:
            best_type = max(scores, key=scores.get)
            if scores[best_type] > 0:
                return best_type
        
        return 'general document'
    
    def _extract_topics(self, data: Dict) -> List[str]:
        """Extract main topics from the document"""
        headers = data.get('headers', {}).get('headers', [])
        if headers:
            return [h['text'] for h in headers[:10]]
        
        # Fallback: use first words of paragraphs
        paragraphs = data.get('text', {}).get('paragraphs', [])
        topics = []
        for p in paragraphs[:10]:
            words = p.split()[:5]
            if words:
                topics.append(' '.join(words))
        
        return topics[:10]
    
    def _generate_summary_text(self, text: str, headers: List, key_points: List) -> str:
        """Generate a natural language summary"""
        summary_parts = []
        
        if headers:
            summary_parts.append(f"This document contains {len(headers)} main sections including: {', '.join([h['text'] for h in headers[:5]])}.")
        
        if key_points:
            summary_parts.append(f"Key points include: {key_points[0]}")
            if len(key_points) > 1:
                summary_parts.append(f"Additionally: {key_points[1]}")
        
        text_preview = text[:500] if text else ''
        if text_preview:
            summary_parts.append(f"The document begins with: {text_preview}...")
        
        return ' '.join(summary_parts)

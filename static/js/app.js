// PDF Analyzer - Main Application JavaScript

// Global state
const state = {
    uploadedFile: null,
    extractedData: null,
    analysisResult: null,
    selectedType: 'all',
    selectedFormat: null
};

// DOM Elements
const elements = {
    uploadZone: document.getElementById('upload-zone'),
    fileInput: document.getElementById('file-input'),
    uploadContent: document.getElementById('upload-content'),
    uploadProgress: document.getElementById('upload-progress'),
    fileInfo: document.getElementById('file-info'),
    fileName: document.getElementById('file-name'),
    fileMeta: document.getElementById('file-meta'),
    removeFile: document.getElementById('remove-file'),
    typeSection: document.getElementById('type-section'),
    promptSection: document.getElementById('prompt-section'),
    resultsSection: document.getElementById('results-section'),
    typeCards: document.querySelectorAll('.type-card'),
    promptInput: document.getElementById('prompt-input'),
    analyzeBtn: document.getElementById('analyze-btn'),
    suggestionChips: document.querySelectorAll('.suggestion-chip'),
    resultsLoading: document.getElementById('results-loading'),
    resultsContent: document.getElementById('results-content'),
    analysisResult: document.getElementById('analysis-result'),
    extractedData: document.getElementById('extracted-data'),
    previewArea: document.getElementById('preview-area'),
    tabButtons: document.querySelectorAll('.tab-btn'),
    tabContents: document.querySelectorAll('.tab-content'),
    formatButtons: document.querySelectorAll('.format-btn'),
    exportProgress: document.getElementById('export-progress'),
    exportResult: document.getElementById('export-result'),
    downloadBtn: document.getElementById('download-btn'),
    previewBtn: document.getElementById('preview-btn'),
    toastContainer: document.getElementById('toast-container')
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initUploadHandlers();
    initTypeSelection();
    initPromptHandlers();
    initTabHandlers();
    initExportHandlers();
});

// ============================================
// Upload Handlers
// ============================================
function initUploadHandlers() {
    // Click on upload zone
    elements.uploadZone.addEventListener('click', (e) => {
        if (!e.target.closest('.btn-icon')) {
            elements.fileInput.click();
        }
    });

    // File input change
    elements.fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileUpload(e.target.files[0]);
        }
    });

    // Drag and drop
    elements.uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        elements.uploadZone.classList.add('dragover');
    });

    elements.uploadZone.addEventListener('dragleave', () => {
        elements.uploadZone.classList.remove('dragover');
    });

    elements.uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        elements.uploadZone.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileUpload(files[0]);
        }
    });

    // Remove file
    elements.removeFile.addEventListener('click', () => {
        resetUpload();
    });
}

async function handleFileUpload(file) {
    if (!file.name.toLowerCase().endsWith('.pdf')) {
        showToast('Please upload a PDF file', 'error');
        return;
    }

    // Show progress
    elements.uploadContent.hidden = true;
    elements.uploadProgress.hidden = false;

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            state.uploadedFile = data;
            showFileInfo(file, data.info);
            showToast('File uploaded successfully!', 'success');
            
            // Show next sections
            elements.typeSection.hidden = false;
            elements.promptSection.hidden = false;
            elements.resultsSection.hidden = false;
            
            // Scroll to next section
            elements.typeSection.scrollIntoView({ behavior: 'smooth' });
        } else {
            throw new Error(data.error || 'Upload failed');
        }
    } catch (error) {
        showToast(error.message, 'error');
        elements.uploadContent.hidden = false;
        elements.uploadProgress.hidden = true;
    }
}

function showFileInfo(file, info) {
    elements.fileName.textContent = file.name;
    elements.fileMeta.textContent = `${info.pages} pages | ${info.file_size_human || (file.size / 1024 / 1024).toFixed(1) + ' MB'}`;
    
    elements.uploadZone.hidden = true;
    elements.fileInfo.hidden = false;
}

function resetUpload() {
    state.uploadedFile = null;
    state.extractedData = null;
    state.analysisResult = null;
    
    elements.fileInput.value = '';
    elements.uploadZone.hidden = false;
    elements.fileInfo.hidden = true;
    elements.uploadContent.hidden = false;
    elements.uploadProgress.hidden = true;
    
    elements.typeSection.hidden = true;
    elements.promptSection.hidden = true;
    elements.resultsSection.hidden = true;
    
    elements.analysisResult.innerHTML = '';
    elements.extractedData.innerHTML = '';
    elements.previewArea.innerHTML = '';
    
    elements.exportResult.hidden = true;
    elements.selectedFormat = null;
    elements.formatButtons.forEach(btn => btn.classList.remove('active'));
}

// ============================================
// Type Selection
// ============================================
function initTypeSelection() {
    elements.typeCards.forEach(card => {
        card.addEventListener('click', () => {
            elements.typeCards.forEach(c => c.classList.remove('active'));
            card.classList.add('active');
            state.selectedType = card.dataset.type;
        });
    });
}

// ============================================
// Prompt Handlers
// ============================================
function initPromptHandlers() {
    // Suggestion chips
    elements.suggestionChips.forEach(chip => {
        chip.addEventListener('click', () => {
            elements.promptInput.value = chip.dataset.prompt;
            elements.analyzeBtn.disabled = false;
        });
    });

    // Prompt input
    elements.promptInput.addEventListener('input', () => {
        elements.analyzeBtn.disabled = elements.promptInput.value.trim() === '';
    });

    // Analyze button
    elements.analyzeBtn.addEventListener('click', handleAnalyze);

    // Enter key in textarea (Ctrl+Enter to submit)
    elements.promptInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && e.ctrlKey) {
            if (!elements.analyzeBtn.disabled) {
                handleAnalyze();
            }
        }
    });
}

async function handleAnalyze() {
    const prompt = elements.promptInput.value.trim();
    if (!prompt || !state.uploadedFile) return;

    // Show loading
    elements.resultsLoading.hidden = false;
    elements.resultsContent.style.display = 'none';
    elements.analysisResult.innerHTML = '';
    elements.extractedData.innerHTML = '';

    // Update loading status
    const loadingStatus = document.getElementById('loading-status');
    loadingStatus.textContent = 'Extracting data from PDF...';

    try {
        // Step 1: Extract data
        const extractResponse = await fetch('/extract', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                filepath: state.uploadedFile.filepath,
                extract_type: state.selectedType
            })
        });

        const extractData = await extractResponse.json();
        if (!extractData.success) {
            throw new Error(extractData.error || 'Extraction failed');
        }

        state.extractedData = extractData.data;
        loadingStatus.textContent = 'Analyzing with AI...';

        // Step 2: Analyze
        const analyzeResponse = await fetch('/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                filepath: state.uploadedFile.filepath,
                prompt: prompt,
                extract_type: state.selectedType
            })
        });

        const analyzeData = await analyzeResponse.json();
        if (!analyzeData.success) {
            throw new Error(analyzeData.error || 'Analysis failed');
        }

        state.analysisResult = analyzeData.analysis;
        state.extractedData = analyzeData.extracted_data;

        // Display results
        displayAnalysisResults(analyzeData.analysis);
        displayExtractedData(analyzeData.extracted_data);
        
        elements.resultsLoading.hidden = true;
        elements.resultsContent.style.display = 'block';
        
        showToast('Analysis complete!', 'success');
        
        // Scroll to results
        elements.resultsSection.scrollIntoView({ behavior: 'smooth' });

    } catch (error) {
        elements.resultsLoading.hidden = true;
        elements.resultsContent.style.display = 'block';
        showToast(error.message, 'error');
    }
}

// ============================================
// Display Results
// ============================================
function displayAnalysisResults(analysis) {
    const container = elements.analysisResult;
    container.innerHTML = '';

    const result = analysis.result || {};
    const analysisType = analysis.analysis_type || 'default';

    // Analysis type badge
    const typeBadge = document.createElement('div');
    typeBadge.className = 'result-card';
    typeBadge.innerHTML = `
        <h4><i class="fas fa-brain" style="color: #4299e1; margin-right: 8px;"></i>Analysis Type: ${analysisType.replace('_', ' ').toUpperCase()}</h4>
        <p>Your prompt: "${analysis.prompt || ''}"</p>
    `;
    container.appendChild(typeBadge);

    // Display based on analysis type
    if (analysisType === 'summary') {
        displaySummaryResults(container, result);
    } else if (analysisType === 'extract') {
        displayExtractResults(container, result);
    } else if (analysisType === 'find') {
        displayFindResults(container, result);
    } else if (analysisType === 'calculate') {
        displayCalculateResults(container, result);
    } else if (analysisType === 'compare') {
        displayCompareResults(container, result);
    } else if (analysisType === 'organize') {
        displayOrganizeResults(container, result);
    } else {
        displayGeneralResults(container, result);
    }
}

function displaySummaryResults(container, result) {
    if (result.summary_text) {
        const section = document.createElement('div');
        section.className = 'result-section';
        section.innerHTML = `
            <h3><i class="fas fa-align-left"></i> Summary</h3>
            <div class="result-card">${escapeHtml(result.summary_text)}</div>
        `;
        container.appendChild(section);
    }

    if (result.key_points && result.key_points.length > 0) {
        const section = document.createElement('div');
        section.className = 'result-section';
        section.innerHTML = `
            <h3><i class="fas fa-key"></i> Key Points</h3>
            <div class="result-card">
                <ul class="result-list">
                    ${result.key_points.map(p => `<li>${escapeHtml(p)}</li>`).join('')}
                </ul>
            </div>
        `;
        container.appendChild(section);
    }

    if (result.statistics) {
        const section = document.createElement('div');
        section.className = 'result-section';
        section.innerHTML = `
            <h3><i class="fas fa-chart-bar"></i> Document Statistics</h3>
            <div class="result-stats">
                ${Object.entries(result.statistics).map(([k, v]) => `
                    <div class="stat-box">
                        <div class="stat-value">${v}</div>
                        <div class="stat-label">${k.replace(/_/g, ' ')}</div>
                    </div>
                `).join('')}
            </div>
        `;
        container.appendChild(section);
    }

    if (result.document_structure && result.document_structure.length > 0) {
        const section = document.createElement('div');
        section.className = 'result-section';
        section.innerHTML = `
            <h3><i class="fas fa-sitemap"></i> Document Structure</h3>
            <div class="result-card">
                <ul class="result-list">
                    ${result.document_structure.map(s => `<li>${escapeHtml(s)}</li>`).join('')}
                </ul>
            </div>
        `;
        container.appendChild(section);
    }
}

function displayExtractResults(container, result) {
    const extracted = result.extracted_data || {};
    
    for (const [key, values] of Object.entries(extracted)) {
        if (Array.isArray(values) && values.length > 0) {
            const section = document.createElement('div');
            section.className = 'result-section';
            section.innerHTML = `
                <h3><i class="fas fa-database"></i> ${key.replace(/_/g, ' ').toUpperCase()}</h3>
                <div class="result-card">
                    <p><strong>Found ${values.length} items:</strong></p>
                    <ul class="result-list">
                        ${values.slice(0, 20).map(v => `<li>${escapeHtml(String(v))}</li>`).join('')}
                        ${values.length > 20 ? `<li><em>... and ${values.length - 20} more</em></li>` : ''}
                    </ul>
                </div>
            `;
            container.appendChild(section);
        }
    }
}

function displayFindResults(container, result) {
    const results = result.results || {};
    
    for (const [keyword, data] of Object.entries(results)) {
        const section = document.createElement('div');
        section.className = 'result-section';
        
        let content = `<h3><i class="fas fa-search"></i> Results for "${escapeHtml(keyword)}"</h3>`;
        content += `<div class="result-card"><p><strong>${data.total_occurrences || 0} occurrences found</strong></p>`;
        
        if (data.sentences && data.sentences.length > 0) {
            content += `<p style="margin-top: 10px;"><strong>Matching sentences:</strong></p><ul class="result-list">`;
            content += data.sentences.map(s => `<li>${escapeHtml(s)}</li>`).join('');
            content += `</ul>`;
        }
        
        if (data.headers && data.headers.length > 0) {
            content += `<p style="margin-top: 10px;"><strong>Matching headers:</strong></p><ul class="result-list">`;
            content += data.headers.map(h => `<li>${escapeHtml(h.text)} (Page ${h.page})</li>`).join('');
            content += `</ul>`;
        }
        
        content += `</div>`;
        section.innerHTML = content;
        container.appendChild(section);
    }
}

function displayCalculateResults(container, result) {
    const stats = { ...result };
    delete stats.operation;
    delete stats.table_data;
    delete stats.values_sample;

    const section = document.createElement('div');
    section.className = 'result-section';
    section.innerHTML = `
        <h3><i class="fas fa-calculator"></i> Statistical Analysis</h3>
        <div class="result-stats">
            ${Object.entries(stats).map(([k, v]) => `
                <div class="stat-box">
                    <div class="stat-value">${v}</div>
                    <div class="stat-label">${k.replace(/_/g, ' ')}</div>
                </div>
            `).join('')}
        </div>
    `;
    container.appendChild(section);
}

function displayCompareResults(container, result) {
    const comparison = result.comparison_data || [];
    
    const section = document.createElement('div');
    section.className = 'result-section';
    section.innerHTML = `
        <h3><i class="fas fa-balance-scale"></i> Comparison Results</h3>
        ${comparison.map(item => `
            <div class="result-card">
                <h4>Item ${item.table_index || item.page || ''}</h4>
                <ul class="result-list">
                    ${Object.entries(item).map(([k, v]) => `<li><strong>${k}:</strong> ${escapeHtml(String(v))}</li>`).join('')}
                </ul>
            </div>
        `).join('')}
    `;
    container.appendChild(section);
}

function displayOrganizeResults(container, result) {
    const sections = result.sections || [];
    
    if (sections.length > 0) {
        const section = document.createElement('div');
        section.className = 'result-section';
        section.innerHTML = `
            <h3><i class="fas fa-folder-tree"></i> Organized Sections</h3>
            ${sections.map(s => `
                <div class="result-card">
                    <h4>${escapeHtml(s.title || 'Section')}</h4>
                    <ul class="result-list">
                        ${(s.subsections || []).map(sub => `
                            <li>${escapeHtml(sub.title || '')} (Page ${sub.page || 'N/A'})</li>
                        `).join('')}
                    </ul>
                </div>
            `).join('')}
        `;
        container.appendChild(section);
    }

    const tables = result.tables || [];
    if (tables.length > 0) {
        const section = document.createElement('div');
        section.className = 'result-section';
        section.innerHTML = `<h3><i class="fas fa-table"></i> Organized Tables</h3>`;
        
        tables.forEach(t => {
            section.innerHTML += renderTable(t.headers, t.data || t.rows || []);
        });
        
        container.appendChild(section);
    }
}

function displayGeneralResults(container, result) {
    if (result.analysis) {
        const section = document.createElement('div');
        section.className = 'result-section';
        section.innerHTML = `
            <h3><i class="fas fa-info-circle"></i> Analysis</h3>
            <div class="result-card">${escapeHtml(result.analysis)}</div>
        `;
        container.appendChild(section);
    }

    if (result.key_sentences && result.key_sentences.length > 0) {
        const section = document.createElement('div');
        section.className = 'result-section';
        section.innerHTML = `
            <h3><i class="fas fa-quote-left"></i> Key Sentences</h3>
            <div class="result-card">
                <ul class="result-list">
                    ${result.key_sentences.map(s => `<li>${escapeHtml(s)}</li>`).join('')}
                </ul>
            </div>
        `;
        container.appendChild(section);
    }

    if (result.document_type) {
        const section = document.createElement('div');
        section.className = 'result-section';
        section.innerHTML = `
            <h3><i class="fas fa-file-alt"></i> Detected Document Type</h3>
            <div class="result-card">
                <div class="stat-box" style="display: inline-block; min-width: 200px;">
                    <div class="stat-value" style="font-size: 18px; text-transform: capitalize;">${result.document_type}</div>
                </div>
            </div>
        `;
        container.appendChild(section);
    }

    if (result.main_topics && result.main_topics.length > 0) {
        const section = document.createElement('div');
        section.className = 'result-section';
        section.innerHTML = `
            <h3><i class="fas fa-tags"></i> Main Topics</h3>
            <div class="result-card">
                <ul class="result-list">
                    ${result.main_topics.map(t => `<li>${escapeHtml(t)}</li>`).join('')}
                </ul>
            </div>
        `;
        container.appendChild(section);
    }
}

function displayExtractedData(data) {
    const container = elements.extractedData;
    container.innerHTML = '';

    // Display tables
    if (data.tables && data.tables.length > 0) {
        const section = document.createElement('div');
        section.innerHTML = `<h3><i class="fas fa-table"></i> Extracted Tables (${data.tables.length})</h3>`;
        
        data.tables.forEach((table, i) => {
            section.innerHTML += `
                <p style="margin: 10px 0; font-weight: 600; color: var(--primary);">
                    Table ${i + 1} - Page ${table.page} (${table.method})
                </p>
            `;
            section.innerHTML += renderTable(table.headers, table.rows || []);
        });
        
        container.appendChild(section);
    }

    // Display text
    if (data.text) {
        const section = document.createElement('div');
        section.innerHTML = `
            <h3 style="margin-top: 20px;"><i class="fas fa-font"></i> Text Content</h3>
            <div class="result-card">
                <p><strong>Pages:</strong> ${data.text.pages ? data.text.pages.length : 0}</p>
                <p><strong>Words:</strong> ${data.text.word_count || 0}</p>
                <p><strong>Sentences:</strong> ${data.text.sentence_count || 0}</p>
                <p><strong>Paragraphs:</strong> ${data.text.paragraph_count || 0}</p>
            </div>
        `;
        container.appendChild(section);
    }

    // Display numbers
    if (data.numbers) {
        const section = document.createElement('div');
        section.innerHTML = `
            <h3 style="margin-top: 20px;"><i class="fas fa-hashtag"></i> Numbers & Data</h3>
            <div class="result-card">
                <p><strong>Numbers found:</strong> ${data.numbers.numbers_count || 0}</p>
                <p><strong>Percentages:</strong> ${(data.numbers.percentages || []).length}</p>
                <p><strong>Currencies:</strong> ${(data.numbers.currencies || []).length}</p>
                <p><strong>Dates:</strong> ${(data.numbers.dates || []).length}</p>
                <p><strong>Emails:</strong> ${(data.numbers.emails || []).length}</p>
                <p><strong>Phone numbers:</strong> ${(data.numbers.phone_numbers || []).length}</p>
                <p><strong>URLs:</strong> ${(data.numbers.urls || []).length}</p>
            </div>
        `;
        container.appendChild(section);
    }

    // Display code
    if (data.code) {
        const section = document.createElement('div');
        section.innerHTML = `
            <h3 style="margin-top: 20px;"><i class="fas fa-code"></i> Code Detection</h3>
            <div class="result-card">
                <p><strong>Code blocks:</strong> ${data.code.code_blocks_found || 0}</p>
                <p><strong>Detected languages:</strong> ${(data.code.detected_languages || []).join(', ') || 'None'}</p>
                <p><strong>Language patterns:</strong></p>
                <ul class="result-list">
                    ${Object.entries(data.code.language_patterns || {}).map(([k, v]) => `<li>${k}: ${v} matches</li>`).join('')}
                </ul>
            </div>
        `;
        container.appendChild(section);
    }

    // Display headers
    if (data.headers) {
        const section = document.createElement('div');
        section.innerHTML = `
            <h3 style="margin-top: 20px;"><i class="fas fa-heading"></i> Document Structure</h3>
            <div class="result-card">
                <p><strong>Headers found:</strong> ${data.headers.header_count || 0}</p>
                <ul class="result-list">
                    ${(data.headers.headers || []).slice(0, 20).map(h => `<li>Page ${h.page} [Level ${h.level}]: ${escapeHtml(h.text)}</li>`).join('')}
                </ul>
            </div>
        `;
        container.appendChild(section);
    }
}

function renderTable(headers, rows) {
    if (!headers || headers.length === 0) return '';
    
    return `
        <div class="data-table-container">
            <table class="data-table">
                <thead>
                    <tr>${headers.map(h => `<th>${escapeHtml(String(h || ''))}</th>`).join('')}</tr>
                </thead>
                <tbody>
                    ${rows.slice(0, 20).map(row => `
                        <tr>${row.map(cell => `<td>${escapeHtml(String(cell || ''))}</td>`).join('')}</tr>
                    `).join('')}
                    ${rows.length > 20 ? `<tr><td colspan="${headers.length}"><em>... and ${rows.length - 20} more rows</em></td></tr>` : ''}
                </tbody>
            </table>
        </div>
    `;
}

// ============================================
// Tab Handlers
// ============================================
function initTabHandlers() {
    elements.tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabName = btn.dataset.tab;
            
            elements.tabButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            elements.tabContents.forEach(content => {
                content.classList.add('hidden');
            });
            document.getElementById(`tab-${tabName}`).classList.remove('hidden');
        });
    });
}

// ============================================
// Export Handlers
// ============================================
function initExportHandlers() {
    elements.formatButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            if (!state.analysisResult || !state.uploadedFile) {
                showToast('Please analyze a document first', 'warning');
                return;
            }
            
            elements.formatButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            const format = btn.dataset.format;
            handleExport(format);
        });
    });

    elements.previewBtn.addEventListener('click', () => {
        if (state.lastDownloadUrl) {
            window.open(state.lastDownloadUrl, '_blank');
        }
    });
}

async function handleExport(format) {
    elements.exportProgress.hidden = false;
    elements.exportResult.hidden = true;

    try {
        const response = await fetch('/export', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                filepath: state.uploadedFile.filepath,
                format: format,
                analysis: state.analysisResult,
                extracted_data: state.extractedData
            })
        });

        const data = await response.json();

        if (data.success) {
            state.lastDownloadUrl = data.download_url;
            state.lastFilename = data.filename;
            
            elements.downloadBtn.href = data.download_url;
            elements.downloadBtn.download = data.filename;
            
            elements.exportProgress.hidden = true;
            elements.exportResult.hidden = false;
            
            // Update preview based on format
            updatePreview(format, data.download_url);
            
            showToast(`File exported as ${format.toUpperCase()}!`, 'success');
        } else {
            throw new Error(data.error || 'Export failed');
        }
    } catch (error) {
        elements.exportProgress.hidden = true;
        showToast(error.message, 'error');
    }
}

function updatePreview(format, url) {
    const previewArea = elements.previewArea;
    previewArea.innerHTML = '';
    
    if (format === 'png') {
        previewArea.innerHTML = `<img src="${url}?preview=1" alt="Preview">`;
    } else if (format === 'pdf') {
        previewArea.innerHTML = `<iframe src="${url}?preview=1" type="application/pdf"></iframe>`;
    } else {
        previewArea.innerHTML = `
            <div class="result-card" style="text-align: center; padding: 40px;">
                <i class="fas fa-file-${format === 'xlsx' ? 'excel' : format === 'docx' ? 'word' : 'powerpoint'}" 
                   style="font-size: 64px; color: var(--primary-light);"></i>
                <p style="margin-top: 16px; font-size: 16px;">Preview for ${format.toUpperCase()} files is available via download.</p>
                <p style="color: var(--text-light); font-size: 14px;">Click "Download File" to open the file.</p>
            </div>
        `;
    }
}

// ============================================
// Utility Functions
// ============================================
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
    };
    
    toast.innerHTML = `
        <i class="fas ${icons[type] || icons.info}"></i>
        <span class="toast-message">${escapeHtml(message)}</span>
        <button class="toast-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    elements.toastContainer.appendChild(toast);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (toast.parentElement) {
            toast.style.animation = 'fadeOut 0.3s ease forwards';
            setTimeout(() => toast.remove(), 300);
        }
    }, 5000);
}

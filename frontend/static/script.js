const navDashboardBtn = document.getElementById('navDashboardBtn');
const navUploadBtn = document.getElementById('navUploadBtn');
const goUploadBtn = document.getElementById('goUploadBtn');
const uploadBackBtn = document.getElementById('uploadBackBtn');
const resultsDashboardBtn = document.getElementById('resultsDashboardBtn');
const resultsUploadBtn = document.getElementById('resultsUploadBtn');
const browseBtn = document.getElementById('browseBtn');
const fileInput = document.getElementById('fileInput');
const clearFileBtn = document.getElementById('clearFileBtn');
const startProcessBtn = document.getElementById('startProcessBtn');
const selectedFileName = document.getElementById('selectedFileName');
const selectedFileMeta = document.getElementById('selectedFileMeta');
const filePreview = document.getElementById('filePreview');
const globalAlert = document.getElementById('globalAlert');
const uploadArea = document.getElementById('uploadArea');

const dashboardSection = document.getElementById('dashboardSection');
const uploadSection = document.getElementById('uploadSection');
const processingSection = document.getElementById('processingSection');
const resultsSection = document.getElementById('resultsSection');

const dashboardUploads = document.getElementById('dashboardUploads');
const dashboardRows = document.getElementById('dashboardRows');
const dashboardValid = document.getElementById('dashboardValid');
const dashboardInvalid = document.getElementById('dashboardInvalid');
const historyList = document.getElementById('historyList');

const processingMessage = document.getElementById('processingMessage');

const resultTotalRows = document.getElementById('resultTotalRows');
const resultValidRows = document.getElementById('resultValidRows');
const resultInvalidRows = document.getElementById('resultInvalidRows');
const resultSummaryBody = document.getElementById('resultSummaryBody');
const resultErrorBody = document.getElementById('resultErrorBody');
const resultCleanBtn = document.getElementById('resultCleanBtn');
const resultErrorBtn = document.getElementById('resultErrorBtn');
const resultChunkBtn = document.getElementById('resultChunkBtn');
const resultsSuccess = document.getElementById('resultsSuccess');

let pendingFile = null;
let currentUploadId = null;
let processingTimer = null;
let processingIndex = 0;
const processingSteps = [
    'Uploading file...',
    'Validating phone numbers...',
    'Checking date formats...',
    'Generating reports...',
    'Preparing downloads...'
];

browseBtn.addEventListener('click', () => fileInput.click());
clearFileBtn.addEventListener('click', clearSelectedFile);
fileInput.addEventListener('change', handleFileSelect);
// Drag & drop handlers: prevent navigation and wire dropped file into input
if (uploadArea) {
    ['dragenter', 'dragover'].forEach((ev) => {
        uploadArea.addEventListener(ev, (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });
    });

    ['dragleave', 'dragend', 'drop'].forEach((ev) => {
        uploadArea.addEventListener(ev, (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
        });
    });

    window.addEventListener('dragover', (e) => e.preventDefault());
    window.addEventListener('drop', (e) => e.preventDefault());

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        const dt = e.dataTransfer;
        if (!dt || !dt.files || dt.files.length === 0) return;
        const first = dt.files[0];
        // Accept only CSV
        if (!first.name || !first.name.toLowerCase().endsWith('.csv')) {
            showAlert('danger', 'Only CSV files are supported.');
            return;
        }
        // Use DataTransfer to assign files to the file input
        try {
            const dataTransfer = new DataTransfer();
            for (let i = 0; i < dt.files.length; i++) dataTransfer.items.add(dt.files[i]);
            fileInput.files = dataTransfer.files;
            // Trigger change handler
            const ev = new Event('change', { bubbles: true });
            fileInput.dispatchEvent(ev);
        } catch (err) {
            // Fallback: set pendingFile directly
            pendingFile = first;
            showFilePreview(first);
            startProcessBtn.classList.remove('disabled');
            startProcessBtn.disabled = false;
        }
    });
}
uploadBackBtn.addEventListener('click', () => navigateTo('/'));
resultsDashboardBtn.addEventListener('click', () => navigateTo('/'));
resultsUploadBtn.addEventListener('click', () => navigateTo('/upload'));
goUploadBtn.addEventListener('click', () => navigateTo('/upload'));
navDashboardBtn.addEventListener('click', () => navigateTo('/'));
navUploadBtn.addEventListener('click', () => navigateTo('/upload'));
startProcessBtn.addEventListener('click', () => navigateTo('/processing'));

window.addEventListener('popstate', () => routeTo(window.location.pathname));
window.addEventListener('load', () => routeTo(window.location.pathname || '/'));

function routeTo(path) {
    const trimmed = path.replace(/\/+$/, '') || '/';

    hideAlert();
    hideAllSections();

    if (trimmed === '/' || trimmed === '/dashboard') {
        showSection(dashboardSection);
        renderDashboard();
        return;
    }

    if (trimmed === '/upload') {
        showSection(uploadSection);
        renderUploadScreen();
        return;
    }

    if (trimmed === '/processing') {
        showSection(processingSection);
        startProcessing();
        return;
    }

    if (trimmed.startsWith('/results/')) {
        const uploadId = trimmed.split('/')[2];
        showSection(resultsSection);
        loadResult(uploadId);
        return;
    }

    navigateTo('/');
}

function navigateTo(path, replace = false) {
    if (replace) {
        history.replaceState({}, '', path);
    } else {
        history.pushState({}, '', path);
    }
    routeTo(path);
}

function hideAllSections() {
    [dashboardSection, uploadSection, processingSection, resultsSection].forEach((section) => {
        section.classList.add('d-none');
    });
}

function showSection(section) {
    section.classList.remove('d-none');
}

function renderDashboard() {
    fetch('/api/history')
        .then((response) => response.json())
        .then((history) => {
            const uploads = Array.isArray(history) ? history : [];
            dashboardUploads.textContent = uploads.length;
            dashboardRows.textContent = uploads.reduce((sum, item) => sum + (item.total_rows || 0), 0);
            dashboardValid.textContent = uploads.reduce((sum, item) => sum + (item.valid_rows || 0), 0);
            dashboardInvalid.textContent = uploads.reduce((sum, item) => sum + (item.invalid_rows || 0), 0);
            renderHistoryCards(uploads);
        })
        .catch(() => {
            showAlert('danger', 'Unable to load upload history.');
        });
}

function renderHistoryCards(uploads) {
    historyList.innerHTML = '';
    if (!uploads.length) {
        historyList.innerHTML = '<div class="col-12"><div class="card p-4 text-center text-muted">No uploads yet. Start by uploading a CSV file.</div></div>';
        return;
    }
    uploads.forEach((upload) => {
        const card = document.createElement('div');
        card.className = 'col-12 col-md-6 col-xl-4';
        const title = 'CSV Upload';
        const when = formatUploadTimestamp(upload.timestamp);
        const total = upload.total_rows || 0;
        const valid = upload.valid_rows || 0;
        const invalid = upload.invalid_rows || 0;

        card.innerHTML = `
            <div class="card history-card h-100 p-3">
                <div class="d-flex justify-content-between align-items-start mb-2">
                    <div>
                        <h6 class="mb-1">${escapeHtml(title)}</h6>
                        <p class="text-muted small mb-0">${escapeHtml(when)}</p>
                    </div>
                    <div class="text-end">
                        <span class="badge bg-light text-muted">${escapeHtml(total)} rows</span>
                    </div>
                </div>
                <div class="row mb-3 gx-2 gy-2">
                    <div class="col-4">
                        <div class="small text-muted">Processed</div>
                        <div class="fw-bold">${escapeHtml(total)}</div>
                    </div>
                    <div class="col-4">
                        <div class="small text-muted">Valid</div>
                        <div class="fw-bold text-success">${escapeHtml(valid)}</div>
                    </div>
                    <div class="col-4">
                        <div class="small text-muted">Invalid</div>
                        <div class="fw-bold text-danger">${escapeHtml(invalid)}</div>
                    </div>
                </div>
                <button class="btn btn-primary btn-sm w-100" data-upload-id="${escapeHtml(upload.upload_id)}">View Results</button>
            </div>
        `;
        const button = card.querySelector('button');
        button.addEventListener('click', () => navigateTo(`/results/${encodeURIComponent(upload.upload_id)}`));
        historyList.appendChild(card);
    });
}

function formatUploadTimestamp(timestamp) {
    if (!timestamp || typeof timestamp !== 'string') return 'Unknown date';
    const match = timestamp.match(/^(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})$/);
    if (!match) return timestamp;
    const [, year, month, day, hour, minute] = match;
    const date = new Date(`${year}-${month}-${day}T${hour}:${minute}:00`);
    return date.toLocaleString(undefined, {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
    });
}

function renderUploadScreen() {
    if (pendingFile) {
        showFilePreview(pendingFile);
    }
    if (!pendingFile) {
        clearSelectedFile();
    }
}

function handleFileSelect() {
    const file = fileInput.files[0];
    if (!file) return;

    if (!file.name.toLowerCase().endsWith('.csv')) {
        showAlert('danger', 'Please select a valid CSV file.');
        startProcessBtn.classList.add('disabled');
        startProcessBtn.disabled = true;
        return;
    }

    pendingFile = file;
    showFilePreview(file);
    startProcessBtn.classList.remove('disabled');
    startProcessBtn.disabled = false;
    hideAlert();
}

function showFilePreview(file) {
    filePreview.classList.remove('d-none');
    selectedFileName.textContent = file.name;
    selectedFileMeta.textContent = `${Math.round(file.size / 1024)} KB • ${file.type || 'CSV'}`;
}

function clearSelectedFile() {
    fileInput.value = '';
    pendingFile = null;
    filePreview.classList.add('d-none');
    selectedFileName.textContent = '';
    selectedFileMeta.textContent = '';
    startProcessBtn.classList.add('disabled');
    startProcessBtn.disabled = true;
}

function startProcessing() {
    if (!pendingFile) {
        showAlert('danger', 'No file selected for processing.');
        navigateTo('/upload');
        return;
    }

    processingIndex = 0;
    updateProcessingMessage();
    processingTimer = window.setInterval(() => {
        processingIndex = (processingIndex + 1) % processingSteps.length;
        updateProcessingMessage();
    }, 1800);

    const formData = new FormData();
    formData.append('file', pendingFile);

    fetch('/upload', { method: 'POST', body: formData })
        .then(async (response) => {
            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.detail || 'Upload failed. Please try again.');
            }
            return data;
        })
        .then((data) => {
            stopProcessingAnimation();
            currentUploadId = data.upload_id;
            pendingFile = null;
            navigateTo(`/results/${data.upload_id}`);
        })
        .catch((error) => {
            stopProcessingAnimation();
            showAlert('danger', error.message || 'Processing failed.');
            navigateTo('/upload');
        });
}

function stopProcessingAnimation() {
    if (processingTimer) {
        window.clearInterval(processingTimer);
        processingTimer = null;
    }
}

function updateProcessingMessage() {
    processingMessage.textContent = processingSteps[processingIndex] || 'Processing...';
}

function loadResult(uploadId) {
    resultsSuccess.classList.add('d-none');
    fetch(`/api/results/${encodeURIComponent(uploadId)}`)
        .then(async (response) => {
            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.detail || 'Unable to load results.');
            }
            return data;
        })
        .then((data) => {
            currentUploadId = uploadId;
            renderResults(data);
            resultsSuccess.classList.remove('d-none');
        })
        .catch((error) => {
            showAlert('danger', error.message || 'Failed to load results.');
            navigateTo('/');
        });
}

function renderResults(data) {
    resultTotalRows.textContent = data.total_rows || 0;
    resultValidRows.textContent = data.valid_rows || 0;
    resultInvalidRows.textContent = data.invalid_rows || 0;
    renderSummaryTable(data.validation_summary || []);
    renderErrorPreview(data.error_preview || []);
    renderResultDownloads(data);
}

function renderSummaryTable(summary) {
    resultSummaryBody.innerHTML = '';
    if (!summary.length) {
        resultSummaryBody.innerHTML = '<tr><td colspan="2" class="text-muted">No validation issues found.</td></tr>';
        return;
    }
    summary.forEach((item) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${escapeHtml(item.type)}</td>
            <td>${escapeHtml(item.count)}</td>
        `;
        resultSummaryBody.appendChild(row);
    });
}

function renderErrorPreview(errors) {
    resultErrorBody.innerHTML = '';
    if (!errors.length) {
        resultErrorBody.innerHTML = '<tr><td colspan="3" class="text-muted">No validation errors found.</td></tr>';
        return;
    }
    errors.forEach((error) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${escapeHtml(error.row_number)}</td>
            <td>${escapeHtml(error.order_id)}</td>
            <td>${escapeHtml(error.error_reason)}</td>
        `;
        resultErrorBody.appendChild(row);
    });
}

function renderResultDownloads(data) {
    resultCleanBtn.href = data.clean_file || '#';
    resultErrorBtn.href = data.error_file || '#';
    resultCleanBtn.setAttribute('download', data.clean_file ? data.clean_file.split('/').pop() : 'cleaned_transactions.csv');
    resultErrorBtn.setAttribute('download', data.error_file ? data.error_file.split('/').pop() : 'validation_errors.csv');

    if (data.chunk_zip) {
        resultChunkBtn.classList.remove('d-none');
        resultChunkBtn.href = data.chunk_zip;
        resultChunkBtn.setAttribute('download', data.chunk_zip.split('/').pop());
    } else {
        resultChunkBtn.classList.add('d-none');
    }
}

function showAlert(type, message) {
    globalAlert.className = `alert alert-${type}`;
    globalAlert.textContent = message;
    globalAlert.classList.remove('d-none');
}

function hideAlert() {
    globalAlert.classList.add('d-none');
    globalAlert.textContent = '';
}

function escapeHtml(value) {
    if (value === null || value === undefined) return '';
    return String(value)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}


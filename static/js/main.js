/**
 * Event Horizon Lab - Job Scraper
 * Main JavaScript file
 */

let currentJobData = null;

/**
 * Scrape job posting from URL
 */
async function scrapeJob() {
    const url = document.getElementById('jobUrl').value.trim();

    if (!url) {
        showToast('Please enter a URL', 'error');
        return;
    }

    if (!url.startsWith('http')) {
        showToast('Invalid URL format. URL must start with http:// or https://', 'error');
        return;
    }

    // Pre-fill apply link with the URL user entered
    document.getElementById('apply_link').value = url;

    // Show loading state
    showLoading(true);
    updateLoadingMessage('Accessing webpage...');

    try {
        // Call scrape API
        const response = await fetch('/api/scrape', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: url })
        });

        const result = await response.json();

        if (result.success) {
            currentJobData = result.data;
            populateForm(currentJobData);
            showResult(true);
            showToast('✅ Successfully scraped! Please review the information', 'success');
        } else {
            showToast('❌ Scrape failed: ' + result.error, 'error');
            showLoading(false);
        }

    } catch (error) {
        console.error('Error:', error);
        showToast('❌ Network error, please try again', 'error');
        showLoading(false);
    }
}

/**
 * Populate form with extracted data
 */
function populateForm(data) {
    // Map field names
    const fieldMap = {
        'company': 'company',
        'title': 'title',
        'industry': 'industry',
        'location': 'location',
        'type': 'type',
        'degree': 'degree',
        'visa_sponsorship': 'visa_sponsorship',
        'deadline': 'deadline',
        'target_year': 'target_year',
        'salary': 'salary',
        'apply_link': 'apply_link',
        'description': 'description',
        'status': 'status'
    };

    // Fill form fields
    for (const [key, value] of Object.entries(fieldMap)) {
        const element = document.getElementById(key);
        if (element) {
            // Special handling for apply_link: keep user's URL if AI didn't find one
            if (key === 'apply_link' && (!data[value] || data[value] === '')) {
                // Keep the URL that was pre-filled
                continue;
            }
            // Only set if data exists
            if (data[value]) {
                element.value = data[value];
            }
        }
    }

    // Special handling for preferred_major (array field)
    const majorElement = document.getElementById('preferred_major');
    if (majorElement && data['preferred_major'] && Array.isArray(data['preferred_major'])) {
        // Join array with comma for display
        majorElement.value = data['preferred_major'].join(', ');
    }

    // Update confidence score
    if (data.confidence_score) {
        const scoreElement = document.getElementById('confidenceScore');
        const score = data.confidence_score;

        scoreElement.textContent = score + '%';
        scoreElement.className = 'text-2xl font-bold ' + getConfidenceClass(score);
    }
}

/**
 * Get confidence score color class
 */
function getConfidenceClass(score) {
    if (score >= 90) return 'text-green-600';
    if (score >= 70) return 'text-yellow-600';
    return 'text-red-600';
}

/**
 * Save job to Google Sheets
 */
async function saveJob(event) {
    // Prevent default form submission if event exists
    if (event) {
        event.preventDefault();
    }

    if (!currentJobData) {
        showToast('No data to save', 'error');
        return;
    }

    // Gather form data
    const formData = {
        company: document.getElementById('company').value,
        title: document.getElementById('title').value,
        industry: document.getElementById('industry').value,
        location: document.getElementById('location').value,
        type: document.getElementById('type').value,
        degree: document.getElementById('degree').value,
        visa_sponsorship: document.getElementById('visa_sponsorship').value,
        deadline: document.getElementById('deadline').value,
        target_year: document.getElementById('target_year').value,
        salary: document.getElementById('salary').value,
        apply_link: document.getElementById('apply_link').value,
        description: document.getElementById('description').value,
    };

    // Validate required fields
    const required = ['company', 'title', 'location', 'visa_sponsorship', 'deadline', 'apply_link'];
    for (const field of required) {
        if (!formData[field]) {
            showToast(`Please fill required field: ${field}`, 'error');
            return;
        }
    }

    // Get the save button (from event or find it in DOM)
    let saveBtn;
    if (event && event.target) {
        saveBtn = event.target;
    } else {
        // Fallback: find the button in the form
        const buttons = document.querySelectorAll('button[onclick*="saveJob"]');
        saveBtn = buttons[buttons.length - 1]; // Get the last save button
    }

    // Show loading
    if (saveBtn) {
        saveBtn.disabled = true;
        saveBtn.textContent = '⏳ Saving...';
    }

    try {
        const response = await fetch('/api/save', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        const result = await response.json();

        if (result.success) {
            document.getElementById('rowNumber').textContent = result.row_number;
            showSuccess(true);
            showToast('🎉 Successfully saved to Google Sheets!', 'success');
        } else {
            if (result.duplicate_row) {
                showToast('⚠️ Job already exists (row ' + result.duplicate_row + ')', 'warning');
            } else {
                showToast('❌ Save failed: ' + result.error, 'error');
            }
            if (saveBtn) {
                saveBtn.disabled = false;
                saveBtn.textContent = '✅ Confirm & Save';
            }
        }

    } catch (error) {
        console.error('Error:', error);
        showToast('❌ Network error, please try again', 'error');
        if (saveBtn) {
            saveBtn.disabled = false;
            saveBtn.textContent = '✅ Confirm & Save';
        }
    } finally {
        // Always ensure button is re-enabled if we haven't shown success
        if (saveBtn && !document.getElementById('successState').classList.contains('fade-in')) {
            saveBtn.disabled = false;
            saveBtn.textContent = '✅ Confirm & Save';
        }
    }
}

/**
 * Show/hide loading state
 */
function showLoading(show) {
    const loadingState = document.getElementById('loadingState');
    const scrapeBtn = document.getElementById('scrapeBtn');
    const resultState = document.getElementById('resultState');
    const successState = document.getElementById('successState');

    if (show) {
        loadingState.classList.remove('hidden');
        scrapeBtn.disabled = true;
        scrapeBtn.textContent = '⏳ Scraping...';
        resultState.classList.add('hidden');
        successState.classList.add('hidden');
    } else {
        loadingState.classList.add('hidden');
        scrapeBtn.disabled = false;
        scrapeBtn.textContent = '🔍 Scrape Job';
    }
}

/**
 * Update loading message
 */
function updateLoadingMessage(message) {
    document.getElementById('loadingMessage').textContent = message;
}

/**
 * Show/hide result form
 */
function showResult(show) {
    const loadingState = document.getElementById('loadingState');
    const resultState = document.getElementById('resultState');
    const scrapeBtn = document.getElementById('scrapeBtn');

    showLoading(false);

    if (show) {
        resultState.classList.remove('hidden');
        resultState.classList.add('fade-in');
        scrapeBtn.textContent = '🔄 Scrape New Job';
    } else {
        resultState.classList.add('hidden');
    }
}

/**
 * Show/hide success message
 */
function showSuccess(show) {
    const resultState = document.getElementById('resultState');
    const successState = document.getElementById('successState');

    if (show) {
        resultState.classList.add('hidden');
        successState.classList.remove('hidden');
        successState.classList.add('fade-in');
    } else {
        successState.classList.add('hidden');
        successState.classList.remove('fade-in');
    }
}

/**
 * Reset form to initial state
 */
function resetForm() {
    // Clear form
    document.getElementById('jobUrl').value = '';
    document.getElementById('jobForm').reset();

    // Hide states
    showResult(false);
    showSuccess(false);

    // Reset button
    const scrapeBtn = document.getElementById('scrapeBtn');
    scrapeBtn.disabled = false;
    scrapeBtn.textContent = '🔍 Scrape Job';

    // Clear data
    currentJobData = null;

    showToast('Ready to scrape a new job', 'info');
}

/**
 * Cancel operation
 */
function cancelForm() {
    if (confirm('Are you sure you want to cancel? All scraped data will be lost.')) {
        resetForm();
    }
}

/**
 * Switch to URL mode after successful save
 */
function switchToUrlMode() {
    resetForm();
    setInputMode('url');
    showToast('Ready to scrape from URL', 'info');
}

/**
 * Switch to text mode after successful save
 */
function switchToTextMode() {
    resetForm();
    setInputMode('text');
    showToast('Ready to extract from text', 'info');
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info') {
    // Remove existing toasts
    const existingToasts = document.querySelectorAll('.toast-notification');
    existingToasts.forEach(toast => toast.remove());

    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast-notification toast show`;

    // Set color based on type
    const bgColor = {
        'success': 'bg-green-500',
        'error': 'bg-red-500',
        'warning': 'bg-yellow-500',
        'info': 'bg-blue-500'
    }[type] || 'bg-blue-500';

    toast.innerHTML = `
        <div class="toast-header ${bgColor} text-white">
            <strong class="me-auto">${type.charAt(0).toUpperCase() + type.slice(1)}</strong>
            <button type="button" class="btn-close btn-close-white" onclick="this.parentElement.parentElement.parentElement.remove()"></button>
        </div>
        <div class="toast-body">
            ${message}
        </div>
    `;

    document.body.appendChild(toast);

    // Auto remove after 5 seconds
    setTimeout(() => {
        toast.remove();
    }, 5000);
}

/**
 * Toggle between URL and text input modes
 */
function setInputMode(mode) {
    const urlMode = document.getElementById('urlMode');
    const textMode = document.getElementById('textMode');
    const urlModeBtn = document.getElementById('urlModeBtn');
    const textModeBtn = document.getElementById('textModeBtn');

    if (mode === 'url') {
        urlMode.classList.remove('hidden');
        textMode.classList.add('hidden');
        urlModeBtn.className = 'px-4 py-2 rounded-lg font-semibold bg-blue-600 text-white';
        textModeBtn.className = 'px-4 py-2 rounded-lg font-semibold bg-gray-200 text-gray-700';
    } else {
        urlMode.classList.add('hidden');
        textMode.classList.remove('hidden');
        urlModeBtn.className = 'px-4 py-2 rounded-lg font-semibold bg-gray-200 text-gray-700';
        textModeBtn.className = 'px-4 py-2 rounded-lg font-semibold bg-purple-600 text-white';
    }
}

/**
 * Extract job information from pasted text
 */
async function extractFromText() {
    const text = document.getElementById('jobText').value.trim();
    const url = document.getElementById('jobUrlForText').value.trim();

    if (!text) {
        showToast('Please paste job description text', 'error');
        return;
    }

    // Pre-fill apply link with the URL user entered (if any)
    if (url) {
        document.getElementById('apply_link').value = url;
    }

    // Show loading state
    showLoading(true);
    updateLoadingMessage('Analyzing text content...');

    try {
        // Call extract-from-text API
        const response = await fetch('/api/extract-from-text', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text: text, url: url })
        });

        const result = await response.json();

        if (result.success) {
            currentJobData = result.data;
            populateForm(currentJobData);
            showResult(true);
            showToast('✅ Successfully extracted! Please review the information', 'success');
        } else {
            showToast('❌ Extraction failed: ' + result.error, 'error');
            showLoading(false);
        }

    } catch (error) {
        console.error('Error:', error);
        showToast('❌ Network error, please try again', 'error');
        showLoading(false);
    }
}

/**
 * Handle Enter key in URL input
 */
document.addEventListener('DOMContentLoaded', function() {
    const urlInput = document.getElementById('jobUrl');
    if (urlInput) {
        urlInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                scrapeJob();
            }
        });
    }
});

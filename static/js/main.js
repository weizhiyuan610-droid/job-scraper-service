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

    // Show loading state
    showLoading(true);
    updateLoadingMessage('正在访问网页...');

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
            showToast('✅ 抓取成功！请检查信息', 'success');
        } else {
            showToast('❌ 抓取失败：' + result.error, 'error');
            showLoading(false);
        }

    } catch (error) {
        console.error('Error:', error);
        showToast('❌ 网络错误，请稍后重试', 'error');
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
        'description': 'description'
    };

    // Fill form fields
    for (const [key, value] of Object.entries(fieldMap)) {
        const element = document.getElementById(key);
        if (element && data[value]) {
            element.value = data[value];
        }
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
async function saveJob() {
    if (!currentJobData) {
        showToast('没有数据可保存', 'error');
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
            showToast(`请填写必填字段: ${field}`, 'error');
            return;
        }
    }

    // Show loading
    const saveBtn = event.target;
    saveBtn.disabled = true;
    saveBtn.textContent = '⏳ 保存中...';

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
            showToast('🎉 成功保存到 Google Sheets!', 'success');
        } else {
            if (result.duplicate_row) {
                showToast('⚠️ 该职位已存在（第 ' + result.duplicate_row + ' 行）', 'warning');
            } else {
                showToast('❌ 保存失败：' + result.error, 'error');
            }
            saveBtn.disabled = false;
            saveBtn.textContent = '✅ 确认写入';
        }

    } catch (error) {
        console.error('Error:', error);
        showToast('❌ 网络错误，请稍后重试', 'error');
        saveBtn.disabled = false;
        saveBtn.textContent = '✅ 确认写入';
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
        scrapeBtn.textContent = '⏳ 抓取中...';
        resultState.classList.add('hidden');
        successState.classList.add('hidden');
    } else {
        loadingState.classList.add('hidden');
        scrapeBtn.disabled = false;
        scrapeBtn.textContent = '🔍 开始抓取';
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
        scrapeBtn.textContent = '🔄 重新抓取';
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
    scrapeBtn.textContent = '🔍 开始抓取';

    // Clear data
    currentJobData = null;

    showToast('已重置，可以抓取新职位', 'info');
}

/**
 * Cancel operation
 */
function cancelForm() {
    if (confirm('确定要取消吗？已抓取的数据将丢失。')) {
        resetForm();
    }
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

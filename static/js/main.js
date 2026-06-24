/**
 * Event Horizon Lab - Job Scraper
 * Main JavaScript file
 */

let currentJobData = null;

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
        'deadline': 'deadline',
        'target_year': 'target_year',
        'salary': 'salary',
        'apply_link': 'apply_link',
        'description': 'description',
        'status': 'status',
        'department': 'department',
        'job_level': 'job_level',
        'work_mode': 'work_mode',
        'target_audience': 'target_audience'
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

    // NEW: Map degree_min to degree select (convert values)
    const degreeElement = document.getElementById('degree');
    if (degreeElement && data['degree_min']) {
        const degreeMap = {
            'bachelor': 'Bachelor',
            'master': 'Master',
            'phd': 'PhD',
            'any': 'Any'
        };
        const mappedValue = degreeMap[data['degree_min']] || 'Any';
        degreeElement.value = mappedValue;
    }

    // NEW: Map visa_sponsorship + visa_mentioned to visa_sponsorship select
    const visaElement = document.getElementById('visa_sponsorship');
    if (visaElement && data['visa_sponsorship'] !== undefined) {
        if (data['visa_mentioned'] === 'case_by_case') {
            visaElement.value = 'Case by case';
        } else if (data['visa_sponsorship'] === true) {
            visaElement.value = 'Yes';
        } else if (data['visa_sponsorship'] === false) {
            visaElement.value = data['visa_mentioned'] === 'not_mentioned' ? 'Not mentioned' : 'No';
        }
    }

    // Special handling for preferred_major (array field)
    const majorElement = document.getElementById('preferred_major');
    if (majorElement && data['preferred_major'] && Array.isArray(data['preferred_major'])) {
        // Join array with comma for display
        majorElement.value = data['preferred_major'].join(', ');
    }

    // Special handling for skills_tags (array field)
    const skillsElement = document.getElementById('skills_tags');
    if (skillsElement && data['skills_tags'] && Array.isArray(data['skills_tags'])) {
        // Join array with comma for display
        skillsElement.value = data['skills_tags'].join(', ');
    }

    // NEW: Special handling for perks (array field)
    const perksElement = document.getElementById('perks');
    if (perksElement && data['perks'] && Array.isArray(data['perks'])) {
        perksElement.value = data['perks'].join(', ');
    }

    // NEW: Handle requirements field
    if (data['requirements']) {
        document.getElementById('requirements').value = data['requirements'];
    }

    // NEW: Handle visa_source and visa_likelihood (hidden fields)
    if (data['visa_source']) {
        document.getElementById('visa_source').value = data['visa_source'];
    }
    if (data['visa_likelihood']) {
        document.getElementById('visa_likelihood').value = data['visa_likelihood'];
    }

    // NEW: Display visa info badge if from company history
    if (data['visa_source'] === 'company_history') {
        displayVisaInfoBadge(data);
    }

    // Update confidence score
    if (data.confidence_score) {
        const scoreElement = document.getElementById('confidenceScore');
        const score = data.confidence_score;

        scoreElement.textContent = score + '%';
        scoreElement.className = 'text-2xl font-bold ' + getConfidenceClass(score);
    }

    // Display company info if available
    if (data.company_info) {
        displayCompanyInfo(data.company_info);
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
    const degreeValue = document.getElementById('degree').value;
    const visaValue = document.getElementById('visa_sponsorship').value;

    // Map degree values to backend format
    const degreeMap = {
        'Any': 'any',
        'Bachelor': 'bachelor',
        'Master': 'master',
        'MBA': 'master',
        'PhD': 'phd',
        'Preferred': ''
    };

    // Map visa values to backend format
    let visaSponsorshipBool = false;
    let visaMentionedValue = 'not_mentioned';

    if (visaValue === 'Yes') {
        visaSponsorshipBool = true;
        visaMentionedValue = 'explicit_yes';
    } else if (visaValue === 'No') {
        visaSponsorshipBool = false;
        visaMentionedValue = 'explicit_no';
    } else if (visaValue === 'Case by case') {
        visaSponsorshipBool = true;
        visaMentionedValue = 'case_by_case';
    } else if (visaValue === 'Not mentioned') {
        visaSponsorshipBool = false;
        visaMentionedValue = 'not_mentioned';
    }

    const formData = {
        company: document.getElementById('company').value,
        title: document.getElementById('title').value,
        industry: document.getElementById('industry').value,
        location: document.getElementById('location').value,
        type: document.getElementById('type').value,
        // NEW: Map degree to degree_min
        degree_min: degreeMap[degreeValue] || 'any',
        degree_preferred: '', // Will be filled if user adds separate preferred field
        // NEW: Map visa to boolean + visa_mentioned
        visa_sponsorship: visaSponsorshipBool,
        visa_mentioned: visaMentionedValue,
        deadline: document.getElementById('deadline').value,
        target_year: document.getElementById('target_year').value,
        salary: document.getElementById('salary').value,
        apply_link: document.getElementById('apply_link').value,
        description: document.getElementById('description').value,
        // New fields
        department: document.getElementById('department').value,
        job_level: document.getElementById('job_level').value,
        work_mode: document.getElementById('work_mode').value,
        target_audience: document.getElementById('target_audience').value,
        // NEW: requirements and perks
        requirements: document.getElementById('requirements').value,
        visa_source: document.getElementById('visa_source').value,
        visa_likelihood: document.getElementById('visa_likelihood').value,
    };

    // Handle skills_tags (comma-separated to array)
    const skillsValue = document.getElementById('skills_tags').value;
    if (skillsValue && skillsValue.trim()) {
        formData.skills_tags = skillsValue.split(',').map(s => s.trim()).filter(s => s);
    } else {
        formData.skills_tags = [];
    }

    // Handle preferred_major (comma-separated to array)
    const majorValue = document.getElementById('preferred_major').value;
    if (majorValue && majorValue.trim()) {
        formData.preferred_major = majorValue.split(',').map(s => s.trim()).filter(s => s);
    } else {
        formData.preferred_major = [];
    }

    // NEW: Handle perks (comma-separated to array)
    const perksValue = document.getElementById('perks').value;
    if (perksValue && perksValue.trim()) {
        formData.perks = perksValue.split(',').map(s => s.trim()).filter(s => s);
    } else {
        formData.perks = [];
    }

    // Add company info if available
    const companyCard = document.getElementById('companyInfoCard');
    if (!companyCard.classList.contains('hidden')) {
        formData.company_info = {
            size_category: document.getElementById('display_size_category').textContent,
            tier: document.getElementById('display_tier').textContent,
            employee_count: document.getElementById('display_employee_count').textContent,
            funding_stage: document.getElementById('display_funding_stage').textContent,
            hq_location: document.getElementById('display_hq_location').textContent,
            year_founded: document.getElementById('display_year_founded').textContent,
            company_website: document.getElementById('display_company_website').textContent,
            domain: document.getElementById('company_domain').value,
            source: document.getElementById('companySourceBadge').textContent.includes('数据库') ? 'database' : 'user_edited',
            confidence: 100
        };
    }

    // Validate required fields
    const required = ['company', 'title', 'location', 'deadline', 'apply_link'];
    for (const field of required) {
        if (!formData[field]) {
            showToast(`Please fill required field: ${field}`, 'error');
            return;
        }
    }

    // Special validation for visa_sponsorship (boolean field)
    if (formData['visa_sponsorship'] === undefined || formData['visa_sponsorship'] === null) {
        showToast('Please fill required field: visa_sponsorship', 'error');
        return;
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
    const resultState = document.getElementById('resultState');
    const successState = document.getElementById('successState');

    if (show) {
        loadingState.classList.remove('hidden');
        resultState.classList.add('hidden');
        successState.classList.add('hidden');
    } else {
        loadingState.classList.add('hidden');
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

    showLoading(false);

    if (show) {
        resultState.classList.remove('hidden');
        resultState.classList.add('fade-in');

        // Reset save button state
        const saveBtn = document.querySelector('#resultState button[onclick*="saveJob"]');
        if (saveBtn) {
            saveBtn.disabled = false;
            saveBtn.textContent = '✅ Confirm & Save';
        }
    } else {
        resultState.classList.add('hidden');
        resultState.classList.remove('fade-in');
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
    // Clear text input
    document.getElementById('jobText').value = '';
    document.getElementById('jobUrlForText').value = '';
    document.getElementById('jobForm').reset();

    // Hide states
    showResult(false);
    showSuccess(false);

    // Hide company info card
    const companyCard = document.getElementById('companyInfoCard');
    if (companyCard) {
        companyCard.classList.add('hidden');
    }

    // Clear data
    currentJobData = null;

    showToast('Ready to extract a new job', 'info');
}

/**
 * Cancel operation
 */
function cancelForm() {
    if (confirm('Are you sure you want to cancel? All extracted data will be lost.')) {
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
 * Display company information card
 */
function displayCompanyInfo(companyInfo) {
    const card = document.getElementById('companyInfoCard');
    if (!card) return;

    // Show the card
    card.classList.remove('hidden');

    // Update display fields
    document.getElementById('display_size_category').textContent = companyInfo.size_category || '-';
    document.getElementById('display_tier').textContent = companyInfo.tier || '-';
    document.getElementById('display_employee_count').textContent = companyInfo.employee_count || '-';
    document.getElementById('display_funding_stage').textContent = companyInfo.funding_stage || '-';
    document.getElementById('display_hq_location').textContent = companyInfo.hq_location || '-';
    document.getElementById('display_year_founded').textContent = companyInfo.year_founded || '';

    // Update website link
    const websiteLink = document.getElementById('display_company_website');
    if (companyInfo.company_website) {
        websiteLink.href = companyInfo.company_website;
        websiteLink.textContent = companyInfo.company_website;
    } else {
        websiteLink.href = '#';
        websiteLink.textContent = '-';
    }

    // Update source badge
    const badge = document.getElementById('companySourceBadge');
    updateSourceBadge(badge, companyInfo.source, companyInfo.confidence);

    // Update edit fields
    document.getElementById('edit_size_category').value = companyInfo.size_category || 'Mid';
    document.getElementById('edit_tier').value = companyInfo.tier || 'Unknown';
    document.getElementById('edit_employee_count').value = companyInfo.employee_count || '';
    document.getElementById('edit_funding_stage').value = companyInfo.funding_stage || 'Private';
    document.getElementById('edit_hq_location').value = companyInfo.hq_location || '';
    document.getElementById('edit_year_founded').value = companyInfo.year_founded || '';
    document.getElementById('edit_company_website').value = companyInfo.company_website || '';
    document.getElementById('company_domain').value = companyInfo.domain || '';
}

/**
 * NEW: Display visa information badge
 */
function displayVisaInfoBadge(jobData) {
    const display = document.getElementById('visaInfoDisplay');
    if (!display) return;

    const visaSource = jobData.visa_source || 'unknown';
    const visaLikelihood = jobData.visa_likelihood || 'unknown';

    // Source labels
    const sourceLabels = {
        'jd_explicit': 'JD明确说明',
        'company_history': '公司历史数据',
        'unknown': '未知'
    };

    // Likelihood labels
    const likelihoodLabels = {
        'high': '高可能性',
        'medium': '中等可能性',
        'low': '低可能性',
        'unknown': '未知'
    };

    // Colors
    const likelihoodColors = {
        'high': 'text-green-600',
        'medium': 'text-yellow-600',
        'low': 'text-red-600',
        'unknown': 'text-gray-600'
    };

    const sourceLabel = sourceLabels[visaSource] || visaSource;
    const likelihoodLabel = likelihoodLabels[visaLikelihood] || visaLikelihood;
    const likelihoodColor = likelihoodColors[visaLikelihood] || 'text-gray-600';

    // Build HTML
    let html = '<div class="flex items-center space-x-2">';
    html += `<span class="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">${sourceLabel}</span>`;

    if (visaLikelihood !== 'unknown') {
        html += `<span class="text-xs ${likelihoodColor} px-2 py-1 rounded">${likelihoodLabel}</span>`;
    }

    if (visaSource === 'company_history' && jobData.visa_note) {
        html += `<span class="text-xs text-gray-500 italic">${jobData.visa_note}</span>`;
    }

    html += '</div>';

    display.innerHTML = html;
    display.parentElement.classList.remove('hidden'); // Show the display div
}

/**
 * Update source badge styling
 */
function updateSourceBadge(badge, source, confidence) {
    const sourceConfig = {
        'database': { text: '数据库 ✓', class: 'bg-green-100 text-green-800' },
        'ai_inferred': { text: 'AI 推断', class: 'bg-blue-100 text-blue-800' },
        'ai_low_confidence': { text: 'AI 推断 ⚠️', class: 'bg-yellow-100 text-yellow-800' },
        'unknown': { text: '未知', class: 'bg-gray-100 text-gray-800' }
    };

    const config = sourceConfig[source] || sourceConfig['unknown'];
    badge.textContent = config.text;
    badge.className = `ml-2 px-2 py-1 text-xs font-medium rounded-full ${config.class}`;

    // Add confidence if AI inferred
    if (source.startsWith('ai') && confidence > 0) {
        badge.textContent += ` (${confidence}%)`;
    }
}

/**
 * Toggle company info edit mode
 */
function toggleCompanyEdit() {
    const display = document.getElementById('companyInfoDisplay');
    const edit = document.getElementById('companyInfoEdit');

    if (edit.classList.contains('hidden')) {
        display.classList.add('hidden');
        edit.classList.remove('hidden');
    } else {
        display.classList.remove('hidden');
        edit.classList.add('hidden');
    }
}

/**
 * Save company info edits
 */
function saveCompanyEdit() {
    // Get edited values
    const editedInfo = {
        size_category: document.getElementById('edit_size_category').value,
        tier: document.getElementById('edit_tier').value,
        employee_count: document.getElementById('edit_employee_count').value,
        funding_stage: document.getElementById('edit_funding_stage').value,
        hq_location: document.getElementById('edit_hq_location').value,
        year_founded: document.getElementById('edit_year_founded').value,
        company_website: document.getElementById('edit_company_website').value,
        domain: document.getElementById('company_domain').value,
        source: 'user_edited',
        confidence: 100  // User edited = 100% confidence
    };

    // Update display
    displayCompanyInfo(editedInfo);

    // Update current job data
    if (currentJobData) {
        currentJobData.company_info = editedInfo;
    }

    // Switch back to display mode
    toggleCompanyEdit();

    showToast('公司信息已更新', 'success');
}

/**
 * Cancel company info edits
 */
function cancelCompanyEdit() {
    // Revert to original values from currentJobData
    if (currentJobData && currentJobData.company_info) {
        displayCompanyInfo(currentJobData.company_info);
    }

    // Switch back to display mode
    toggleCompanyEdit();
}

/**
 * Validate all job application links
 */
async function validateLinks(offset = 0) {
    const btn = document.getElementById('checkLinksBtn');
    const badge = document.getElementById('linkCheckBadge');
    const resultsDiv = document.getElementById('linkCheckResults');

    // Show loading state
    btn.disabled = true;
    btn.textContent = '⏳ 检查中...';
    btn.className = 'w-full bg-gray-400 text-white font-medium py-2 px-4 rounded-lg cursor-not-allowed';

    badge.classList.remove('hidden');
    badge.textContent = '检查中...';
    badge.className = 'px-2 py-1 text-xs font-medium rounded-full bg-yellow-100 text-yellow-800';

    resultsDiv.classList.add('hidden');

    try {
        const url = offset > 0 ? `/api/validate-links?offset=${offset}` : '/api/validate-links';
        const response = await fetch(url);
        const result = await response.json();

        if (result.success) {
            displayLinkCheckResults(result);
            showToast(`检查完成！${result.summary.valid}/${result.summary.total} 个链接有效`, result.summary.invalid > 0 ? 'warning' : 'success');
        } else {
            showToast('检查失败: ' + result.error, 'error');
            badge.textContent = '检查失败';
            badge.className = 'px-2 py-1 text-xs font-medium rounded-full bg-red-100 text-red-800';
        }

    } catch (error) {
        console.error('Error:', error);
        showToast('网络错误，请重试', 'error');
        badge.textContent = '网络错误';
        badge.className = 'px-2 py-1 text-xs font-medium rounded-full bg-red-100 text-red-800';
    } finally {
        btn.disabled = false;
        btn.textContent = '重新检查';
        btn.className = 'w-full bg-blue-600 text-white font-medium py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors';
    }
}

/**
 * Continue checking next batch of links
 */
function continueLinkCheck() {
    const nextOffset = document.getElementById('nextOffset').value;
    if (nextOffset) {
        validateLinks(parseInt(nextOffset));
    }
}

/**
 * Display link check results
 */
function displayLinkCheckResults(result) {
    const summary = result.summary;
    const results = result.results;
    const badge = document.getElementById('linkCheckBadge');
    const resultsDiv = document.getElementById('linkCheckResults');

    // Update badge with progress
    const progressText = summary.total_jobs ? ` (${summary.progress})` : '';
    badge.textContent = `${summary.valid}/${summary.total} 有效${progressText}`;
    if (summary.invalid === 0) {
        badge.className = 'px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800';
    } else {
        badge.className = 'px-2 py-1 text-xs font-medium rounded-full bg-red-100 text-red-800';
    }

    // Show results
    resultsDiv.classList.remove('hidden');

    // Display summary cards
    const summaryDiv = document.getElementById('linkCheckSummary');
    summaryDiv.innerHTML = `
        <div class="bg-blue-50 rounded-lg p-4 text-center">
            <div class="text-2xl font-bold text-blue-600">${summary.total_jobs || summary.total}</div>
            <div class="text-sm text-gray-600">总职位数</div>
        </div>
        <div class="bg-green-50 rounded-lg p-4 text-center">
            <div class="text-2xl font-bold text-green-600">${summary.valid}</div>
            <div class="text-sm text-gray-600">✅ 有效</div>
        </div>
        <div class="bg-red-50 rounded-lg p-4 text-center">
            <div class="text-2xl font-bold text-red-600">${summary.invalid}</div>
            <div class="text-sm text-gray-600">❌ 失效</div>
        </div>
        <div class="bg-purple-50 rounded-lg p-4 text-center">
            <div class="text-2xl font-bold text-purple-600">${summary.remaining}</div>
            <div class="text-sm text-gray-600">⏳ 待检查</div>
        </div>
    `;

    // Add continue button if there are remaining jobs
    const existingContinueBtn = document.getElementById('continueCheckBtn');
    if (existingContinueBtn) {
        existingContinueBtn.remove();
    }

    if (summary.remaining > 0) {
        const summaryDivContainer = document.getElementById('linkCheckSummary');
        const continueBtnDiv = document.createElement('div');
        continueBtnDiv.className = 'col-span-4 text-center mt-4';
        continueBtnDiv.innerHTML = `
            <button id="continueCheckBtn" onclick="continueLinkCheck()" class="bg-purple-600 text-white font-medium py-2 px-6 rounded-lg hover:bg-purple-700 transition-colors">
                📋 继续检查下一批 (${summary.remaining} 个剩余)
            </button>
            <input type="hidden" id="nextOffset" value="${summary.next_offset}">
        `;
        summaryDivContainer.appendChild(continueBtnDiv);
    } else if (summary.total_jobs > 0) {
        // All done - show completion message
        const summaryDivContainer = document.getElementById('linkCheckSummary');
        const completeDiv = document.createElement('div');
        completeDiv.className = 'col-span-4 text-center mt-4';
        completeDiv.innerHTML = `
            <div class="text-green-600 font-medium">
                ✅ 全部检查完成！共检查 ${summary.total_jobs} 个职位
            </div>
        `;
        summaryDivContainer.appendChild(completeDiv);
    }

    // Separate valid and invalid links
    const invalidLinks = results.filter(r => !r.valid);
    const validLinks = results.filter(r => r.valid);

    // Display invalid links
    const invalidSection = document.getElementById('invalidLinksSection');
    const invalidList = document.getElementById('invalidLinksList');

    if (invalidLinks.length > 0) {
        invalidSection.classList.remove('hidden');
        invalidList.innerHTML = invalidLinks.map(link => `
            <div class="bg-red-50 border border-red-200 rounded-lg p-3">
                <div class="flex items-start justify-between">
                    <div class="flex-1">
                        <div class="font-medium text-gray-900">${link.company} - ${link.title}</div>
                        <div class="text-sm text-gray-600 mt-1">
                            <span class="text-gray-400">行 ${link.row}:</span>
                            <a href="${link.url}" target="_blank" class="text-blue-600 hover:underline break-all">${link.url.substring(0, 60)}${link.url.length > 60 ? '...' : ''}</a>
                        </div>
                        <div class="text-xs text-red-600 mt-1">
                            ${link.status}: ${link.error || 'Unknown error'}
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    } else {
        invalidSection.classList.add('hidden');
    }

    // Display valid links (collapsible)
    const validSection = document.getElementById('validLinksSection');
    const validList = document.getElementById('validLinksList');
    const validCount = document.getElementById('validLinksCount');

    if (validLinks.length > 0) {
        validSection.classList.remove('hidden');
        validCount.textContent = validLinks.length;
        validList.innerHTML = validLinks.map(link => `
            <div class="bg-green-50 border border-green-200 rounded-lg p-3">
                <div class="flex items-start justify-between">
                    <div class="flex-1">
                        <div class="font-medium text-gray-900">${link.company} - ${link.title}</div>
                        <div class="text-sm text-gray-600 mt-1">
                            <span class="text-gray-400">行 ${link.row}:</span>
                            <a href="${link.url}" target="_blank" class="text-blue-600 hover:underline break-all">${link.url.substring(0, 60)}${link.url.length > 60 ? '...' : ''}</a>
                        </div>
                        <div class="text-xs text-green-600 mt-1">
                            ✅ ${link.status} (${link.status_code})
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    } else {
        validSection.classList.add('hidden');
    }
}

/**
 * Toggle valid links visibility
 */
function toggleValidLinks() {
    const validList = document.getElementById('validLinksList');
    const toggle = document.getElementById('validLinksToggle');

    if (validList.classList.contains('hidden')) {
        validList.classList.remove('hidden');
        toggle.textContent = '▼️';
    } else {
        validList.classList.add('hidden');
        toggle.textContent = '▶️';
    }
}

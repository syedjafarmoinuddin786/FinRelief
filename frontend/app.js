// Central API URL Configuration
const API_BASE_URL = `http://${window.location.hostname}:8000/api`;

// Utility for fetching with Auth
async function authFetch(endpoint, options = {}) {
    const token = localStorage.getItem('finrelief_token');
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers
    });
    
    if (response.status === 401) {
        logout();
        throw new Error('Session expired. Please login again.');
    }
    
    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.detail || 'An error occurred');
    }
    return data;
}


// Theme logic
function toggleTheme() {
    const isDark = document.getElementById('theme-toggle').checked;
    if (isDark) {
        document.body.classList.add('dark-mode');
        localStorage.setItem('finrelief_theme', 'dark');
    } else {
        document.body.classList.remove('dark-mode');
        localStorage.setItem('finrelief_theme', 'light');
    }
    if (localStorage.getItem('finrelief_token')) {
        authFetch('/settings', {
            method: 'PUT',
            body: JSON.stringify({
                theme: isDark ? 'dark' : 'light',
                currency: 'USD',
                language: 'en',
                notifications_enabled: true
            })
        }).catch(e => console.error("Failed to save theme to backend", e));
    }
}

function loadTheme() {
    const theme = localStorage.getItem('finrelief_theme') || 'light';
    const toggle = document.getElementById('theme-toggle');
    if (theme === 'dark') {
        document.body.classList.add('dark-mode');
        if(toggle) toggle.checked = true;
    } else {
        document.body.classList.remove('dark-mode');
        if(toggle) toggle.checked = false;
    }
}
loadTheme();

// ---------------------------------
// Core App Logic
// ---------------------------------
function showSection(sectionId) {
    document.querySelectorAll('main > section').forEach(sec => sec.classList.add('hidden'));
    document.getElementById(sectionId).classList.remove('hidden');
    
    const token = localStorage.getItem('finrelief_token');
    const isAuthenticated = !!token;
    if (isAuthenticated) {
        document.getElementById('nav-unauth').classList.add('hidden');
        document.getElementById('nav-auth').classList.remove('hidden');
        
        try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            if (payload.sub === 'admin@example.com') {
                document.getElementById('nav-admin-btn').classList.remove('hidden');
            }
        } catch(e) {}
        
        if (sectionId === 'dashboard-section') loadDashboard();
        if (sectionId === 'settings-section') loadSettings();
    } else {
        document.getElementById('nav-unauth').classList.remove('hidden');
        document.getElementById('nav-auth').classList.add('hidden');
        if (!['login-section', 'signup-section', 'forgot-password-section', 'reset-password-section', '2fa-verify-section'].includes(sectionId)) {
            showSection('login-section'); // Force login
        }
    }
}

async function loadAdmin() {
    showSection('admin-section');
    const container = document.getElementById('admin-stats-container');
    container.innerHTML = '<div class="spinner"></div>';
    try {
        const data = await authFetch('/admin/stats');
        container.innerHTML = `
            <div class="summary-card">
                <h4>Total Users</h4>
                <p class="value">${data.total_users}</p>
            </div>
            <div class="summary-card">
                <h4>Total Loans</h4>
                <p class="value">${data.total_loans}</p>
            </div>
            <div class="summary-card" style="border-color: red;">
                <h4>Total System Debt</h4>
                <p class="value text-critical">$${data.total_system_debt.toFixed(2)}</p>
            </div>
        `;
    } catch(err) {
        container.innerHTML = `<p class="error-message">Not authorized or error: ${err.message}</p>`;
    }
}

function logout() {
    localStorage.removeItem('finrelief_token');
    showSection('login-section');
}

// Form Handlers
document.getElementById('signup-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = document.getElementById('signup-btn');
    const err = document.getElementById('signup-error');
    err.classList.add('hidden');
    btn.disabled = true;
    btn.innerText = 'Creating account...';

    const payload = {
        name: document.getElementById('signup-name').value,
        email: document.getElementById('signup-email').value,
        password: document.getElementById('signup-password').value,
        income: parseFloat(document.getElementById('signup-income').value),
        expenses: parseFloat(document.getElementById('signup-expenses').value)
    };

    try {
        const data = await authFetch('/signup', { method: 'POST', body: JSON.stringify(payload) });
        localStorage.setItem('finrelief_token', data.access_token);
        showSection('dashboard-section');
    } catch (error) {
        err.innerText = error.message;
        err.classList.remove('hidden');
    } finally {
        btn.disabled = false;
        btn.innerText = 'Sign Up';
    }
});

document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = document.getElementById('login-btn');
    const err = document.getElementById('login-error');
    err.classList.add('hidden');
    btn.disabled = true;
    btn.innerText = 'Logging in...';

    const formData = new URLSearchParams();
    formData.append('username', document.getElementById('login-email').value);
    formData.append('password', document.getElementById('login-password').value);

    try {
        const response = await fetch(`${API_BASE_URL}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData.toString()
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || 'Login failed');
        
        if (data.requires_2fa) {
            localStorage.setItem('temp_2fa_token', data.access_token);
            showSection('2fa-verify-section');
            return;
        }
        
        localStorage.setItem('finrelief_token', data.access_token);
        showSection('dashboard-section');
    } catch (error) {
        err.innerText = error.message;
        err.classList.remove('hidden');
    } finally {
        btn.disabled = false;
        btn.innerText = 'Login';
    }
});

document.getElementById('add-loan-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = document.getElementById('loan-btn');
    const err = document.getElementById('loan-error');
    err.classList.add('hidden');
    btn.disabled = true;
    btn.innerText = 'Saving...';

    let lenderName = document.getElementById('loan-lender').value;
    if (lenderName === 'Other') lenderName = document.getElementById('loan-lender-other').value;
    
    let loanType = document.getElementById('loan-type').value;
    if (loanType === 'Other') loanType = document.getElementById('loan-type-other').value;

    const payload = {
        lender_name: lenderName,
        loan_type: loanType,
        outstanding_amount: parseFloat(document.getElementById('loan-amount').value),
        interest_rate: parseFloat(document.getElementById('loan-rate').value),
        emi: parseFloat(document.getElementById('loan-emi').value),
        overdue_months: parseInt(document.getElementById('loan-overdue').value),
        start_date: document.getElementById('loan-start').value || null,
        due_date: document.getElementById('loan-due').value || null,
        status: document.getElementById('loan-status').value
    };

    const loanId = document.getElementById('loan-id-hidden').value;

    try {
        if (loanId) {
            await authFetch(`/loans/${loanId}`, { method: 'PUT', body: JSON.stringify(payload) });
        } else {
            await authFetch('/loans', { method: 'POST', body: JSON.stringify(payload) });
        }
        showSection('dashboard-section');
        document.getElementById('add-loan-form').reset();
        document.getElementById('loan-id-hidden').value = '';
    } catch (error) {
        err.innerText = error.message;
        err.classList.remove('hidden');
    } finally {
        btn.disabled = false;
        btn.innerText = 'Save Loan';
    }
});

// Dashboard Data
let allLoans = [];

async function loadDashboard() {
    try {
        const data = await authFetch('/dashboard');
        
        // Profile
        const pContainer = document.getElementById('profile-content');
        if (data.profile) {
            const riskClass = `badge-${data.profile.StressLevel.toLowerCase()}`;
            pContainer.innerHTML = `
                <p><strong>Monthly Surplus:</strong> $${data.profile.MonthlySurplus}</p>
                <p><strong>EMI Ratio:</strong> ${(data.profile.EMI_Ratio * 100).toFixed(1)}%</p>
                <p><strong>DTI Ratio:</strong> ${(data.profile.DTI_Ratio * 100).toFixed(1)}%</p>
                <p><strong>Stress Level:</strong> <span class="badge ${riskClass}">${data.profile.StressLevel}</span></p>
            `;
        } else {
            pContainer.innerHTML = `<p>No profile data yet. Add a loan and run analysis to build your profile.</p>`;
        }

        // Fetch full loans array for filtering/editing
        allLoans = await authFetch('/loans');
        
        // Merge latest predictions from dashboard data
        const predictionsMap = {};
        data.loans.forEach(l => { predictionsMap[l.LoanID] = l.LatestSettlementPrediction; });
        allLoans.forEach(l => { l.LatestSettlementPrediction = predictionsMap[l.LoanID]; });

        // Update Summary Cards
        if (data.summary) {
            document.getElementById('summary-total-debt').innerText = '$' + data.summary.total_debt.toLocaleString(undefined, {minimumFractionDigits: 2});
            document.getElementById('summary-total-emi').innerText = '$' + data.summary.total_emi.toLocaleString(undefined, {minimumFractionDigits: 2});
            document.getElementById('summary-total-interest').innerText = '$' + data.summary.total_interest.toLocaleString(undefined, {minimumFractionDigits: 2});
            document.getElementById('summary-monthly-surplus').innerText = '$' + data.summary.monthly_surplus.toLocaleString(undefined, {minimumFractionDigits: 2});
            document.getElementById('summary-loan-counts').innerText = `${data.summary.active_loans} / ${data.summary.overdue_loans}`;
            
            const stressEl = document.getElementById('summary-stress-level');
            stressEl.innerText = data.summary.stress_level;
            stressEl.className = 'value badge-' + data.summary.stress_level.toLowerCase();
            if (data.summary.stress_level === "Unknown") {
                stressEl.style.color = "var(--text-muted)";
            }
        }

        renderDashboard();
        renderCharts(allLoans);
    } catch (error) {
        console.error("Dashboard error", error);
    }
}

function renderDashboard() {
    const lContainer = document.getElementById('loans-container');
    const searchQ = (document.getElementById('loan-search')?.value || '').toLowerCase();
    const statusF = document.getElementById('loan-filter-status')?.value || '';

    let filtered = allLoans;
    if (searchQ) {
        filtered = filtered.filter(l => l.LenderName.toLowerCase().includes(searchQ) || l.LoanType.toLowerCase().includes(searchQ));
    }
    if (statusF) {
        filtered = filtered.filter(l => l.Status === statusF);
    }

    if (filtered.length > 0) {
        lContainer.innerHTML = filtered.map(loan => `
            <div class="loan-card">
                <h3>${loan.LenderName} <span style="font-size:0.8rem; font-weight:normal; color:var(--text-muted);">(${loan.Status})</span>
                <div class="flex gap-2">
                    <button class="btn-secondary" style="font-size:0.8rem; padding:0.2rem 0.5rem;" onclick="openEditLoan(${loan.LoanID})">Edit</button>
                    <button class="btn-secondary" style="font-size:0.8rem; padding:0.2rem 0.5rem; color: var(--status-critical); border-color: var(--status-critical);" onclick="deleteLoan(${loan.LoanID})">Delete</button>
                    <button class="btn-primary" style="font-size:0.8rem; padding:0.2rem 0.5rem;" onclick="analyzeLoan(${loan.LoanID})">Analyze</button>
                </div>
                </h3>
                <p>Outstanding: $${loan.OutstandingAmount} | EMI: $${loan.EMI}</p>
                <p>Rate: ${loan.InterestRate}% | Overdue: ${loan.OverdueMonths} months</p>
                ${loan.LatestSettlementPrediction ? `<p style="color:var(--success); font-weight:600;">Prediction: $${loan.LatestSettlementPrediction}</p>` : ''}
            </div>
        `).join('');
    } else {
        lContainer.innerHTML = '<p>No loans found.</p>';
    }
    
    // Also re-render charts when filter changes
    renderCharts(filtered);
}

// Chart Instances
let chartInstances = {};

function renderCharts(loansData) {
    if (typeof Chart === 'undefined') return;

    // Destroy existing charts to prevent overlap
    Object.keys(chartInstances).forEach(key => {
        if (chartInstances[key]) chartInstances[key].destroy();
    });

    // 1. Debt Distribution
    const debtCtx = document.getElementById('debtDistributionChart');
    if (debtCtx) {
        chartInstances['debt'] = new Chart(debtCtx, {
            type: 'pie',
            data: {
                labels: loansData.map(l => l.LenderName),
                datasets: [{
                    data: loansData.map(l => l.OutstandingAmount),
                    backgroundColor: ['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6'],
                    borderWidth: 0
                }]
            },
            options: { responsive: true, plugins: { legend: { position: 'bottom' } } }
        });
    }

    // 2. EMI Breakdown
    const emiCtx = document.getElementById('emiBreakdownChart');
    if (emiCtx) {
        chartInstances['emi'] = new Chart(emiCtx, {
            type: 'doughnut',
            data: {
                labels: loansData.map(l => l.LenderName),
                datasets: [{
                    data: loansData.map(l => l.EMI),
                    backgroundColor: ['#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6', '#10b981'],
                    borderWidth: 0
                }]
            },
            options: { responsive: true, plugins: { legend: { position: 'bottom' } } }
        });
    }

    // 3. Monthly Cash Flow (Dummy Income/Expenses vs EMI)
    const cfCtx = document.getElementById('cashFlowChart');
    if (cfCtx) {
        const totalEMI = loansData.reduce((sum, l) => sum + (l.EMI || 0), 0);
        // We need income from summary, but let's grab it from the DOM for simplicity
        const incomeStr = document.getElementById('summary-monthly-surplus').innerText.replace('$', '').replace(',', '');
        const surplus = parseFloat(incomeStr) || 0;
        
        chartInstances['cf'] = new Chart(cfCtx, {
            type: 'bar',
            data: {
                labels: ['Outflow (EMI)', 'Remaining (Surplus)'],
                datasets: [{
                    label: 'Amount ($)',
                    data: [totalEMI, surplus],
                    backgroundColor: ['#ef4444', '#10b981'],
                    borderRadius: 4
                }]
            },
            options: { responsive: true, scales: { y: { beginAtZero: true } }, plugins: { legend: { display: false } } }
        });
    }

    // 4. Loan Status
    const statusCtx = document.getElementById('loanStatusChart');
    if (statusCtx) {
        const statusCounts = {};
        loansData.forEach(l => {
            statusCounts[l.Status] = (statusCounts[l.Status] || 0) + 1;
        });
        
        chartInstances['status'] = new Chart(statusCtx, {
            type: 'doughnut',
            data: {
                labels: Object.keys(statusCounts),
                datasets: [{
                    data: Object.values(statusCounts),
                    backgroundColor: ['#10b981', '#f59e0b', '#6b7280'],
                    borderWidth: 0
                }]
            },
            options: { responsive: true, plugins: { legend: { position: 'bottom' } } }
        });
    }
}

// AI Interactions
let currentActiveLoanId = null;

async function runSettlement(loanId) {
    currentActiveLoanId = loanId;
    showSection('ai-result-section');
    document.getElementById('ai-result-title').innerText = 'Settlement Recommendation';
    document.getElementById('ai-loading').classList.remove('hidden');
    document.getElementById('ai-error').classList.add('hidden');
    document.getElementById('ai-content').innerHTML = '';
    document.getElementById('negotiation-actions').classList.add('hidden');

    try {
        const data = await authFetch(`/loans/${loanId}/settlement-recommendation`, { method: 'POST' });
        // A05: Sanitize markdown
        const rawHtml = marked.parse(data.narrative);
        const cleanHtml = DOMPurify.sanitize(rawHtml);
        
        let headerContent = `<div class="glass-panel mb-4" style="background:var(--bg-dark);">
            <div class="flex justify-between">
                <div><label>Suggested Settlement</label> <h2 style="color:var(--status-low);">$${data.suggested_settlement}</h2></div>
                <div class="text-center"><label>Risk Category</label> <span class="badge badge-${data.stress_level.toLowerCase()}">${data.stress_level}</span></div>
            </div>
        </div>`;
        
        document.getElementById('ai-content').innerHTML = headerContent + cleanHtml;
        document.getElementById('negotiation-actions').classList.remove('hidden');
    } catch (error) {
        document.getElementById('ai-error').innerText = error.message;
        document.getElementById('ai-error').classList.remove('hidden');
    } finally {
        document.getElementById('ai-loading').classList.add('hidden');
    }
}

async function generateLetter(tone) {
    if (!currentActiveLoanId) return;
    
    document.getElementById('ai-result-title').innerText = `Drafting ${tone} Letter...`;
    document.getElementById('ai-loading').classList.remove('hidden');
    document.getElementById('ai-error').classList.add('hidden');
    document.getElementById('ai-content').innerHTML = '';
    document.getElementById('negotiation-actions').classList.add('hidden');

    try {
        const data = await authFetch(`/loans/${currentActiveLoanId}/negotiation-letter`, { 
            method: 'POST',
            body: JSON.stringify({ tone })
        });
        
        // A05: Sanitize markdown
        const cleanStrategy = DOMPurify.sanitize(marked.parse(data.strategy));
        const cleanLetter = DOMPurify.sanitize(marked.parse(data.letter));
        
        document.getElementById('ai-content').innerHTML = `
            <h3>Strategy Notes</h3>
            <div style="background:var(--inner-glass); padding:1rem; border-radius:8px; margin-bottom:1.5rem; border-left:4px solid var(--accent);">
                ${cleanStrategy}
            </div>
            <div class="flex justify-between align-center mb-2">
                <h3>Negotiation Letter</h3>
                <button class="btn-primary" style="width: auto; padding: 0.3rem 0.8rem;" onclick="window.print()">🖨️ Save as PDF</button>
            </div>
            <div id="printable-letter" style="background:#fff; color:#000; padding:2rem; border-radius:8px; font-family:serif; white-space: pre-wrap;">
                ${cleanLetter}
            </div>
        `;
        
        document.getElementById('ai-result-title').innerText = `Generated ${tone.charAt(0).toUpperCase() + tone.slice(1)} Letter`;
    } catch (error) {
        document.getElementById('ai-error').innerText = error.message;
        document.getElementById('ai-error').classList.add('hidden');
        document.getElementById('ai-result-title').innerText = 'Error';
    } finally {
        document.getElementById('ai-loading').classList.add('hidden');
    }
}

window.onload = () => {
    if (localStorage.getItem('finrelief_token')) {
        showSection('dashboard-section');
    } else {
        showSection('login-section');
    }
};

// Listeners for "Other" custom inputs
document.getElementById('loan-lender').addEventListener('change', (e) => {
    const otherInput = document.getElementById('loan-lender-other');
    if (e.target.value === 'Other') {
        otherInput.classList.remove('hidden');
        otherInput.required = true;
    } else {
        otherInput.classList.add('hidden');
        otherInput.required = false;
        otherInput.value = '';
    }
});

document.getElementById('loan-type').addEventListener('change', (e) => {
    const otherInput = document.getElementById('loan-type-other');
    if (e.target.value === 'Other') {
        otherInput.classList.remove('hidden');
        otherInput.required = true;
    } else {
        otherInput.classList.add('hidden');
        otherInput.required = false;
        otherInput.value = '';
    }
});

// Security Logic
document.getElementById('forgot-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = document.getElementById('forgot-btn');
    const err = document.getElementById('forgot-error');
    err.classList.add('hidden');
    btn.disabled = true;

    const email = document.getElementById('forgot-email').value;

    try {
        const response = await fetch(`${API_BASE_URL}/forgot-password`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: email })
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || 'Failed to send request');
        
        // Setup state for the reset screen
        document.getElementById('reset-email-hidden').value = email;
        document.getElementById('forgot-email').value = '';
        showSection('reset-password-section');
    } catch (error) {
        err.innerText = error.message;
        err.classList.remove('hidden');
    } finally {
        btn.disabled = false;
    }
});

document.getElementById('reset-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = document.getElementById('reset-btn');
    const err = document.getElementById('reset-error');
    err.classList.add('hidden');
    btn.disabled = true;

    try {
        const response = await fetch(`${API_BASE_URL}/reset-password`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                email: document.getElementById('reset-email-hidden').value,
                code: document.getElementById('reset-code').value,
                new_password: document.getElementById('reset-password').value
            })
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || 'Reset failed');
        alert("Password reset successfully! You can now log in.");
        document.getElementById('reset-form').reset();
        showSection('login-section');
    } catch (error) {
        err.innerText = error.message;
        err.classList.remove('hidden');
    } finally {
        btn.disabled = false;
    }
});

document.getElementById('2fa-verify-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const err = document.getElementById('2fa-verify-error');
    err.classList.add('hidden');
    const code = document.getElementById('2fa-verify-code').value;
    const tempToken = localStorage.getItem('temp_2fa_token');

    try {
        const response = await fetch(`${API_BASE_URL}/2fa/verify`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token: tempToken, code: code })
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || 'Invalid code');
        
        localStorage.removeItem('temp_2fa_token');
        localStorage.setItem('finrelief_token', data.access_token);
        showSection('dashboard-section');
    } catch (error) {
        err.innerText = error.message;
        err.classList.remove('hidden');
    }
});

async function setup2FA() {
    try {
        const data = await authFetch('/2fa/setup', { method: 'POST' });
        document.getElementById('2fa-qr-code').src = data.qr_code;
        document.getElementById('2fa-setup-area').classList.remove('hidden');
        document.getElementById('enable-2fa-btn').classList.add('hidden');
    } catch (error) {
        alert("Error setting up 2FA: " + error.message);
    }
}

async function confirm2FA() {
    const code = document.getElementById('2fa-setup-code').value;
    const err = document.getElementById('2fa-setup-error');
    err.classList.add('hidden');
    try {
        await authFetch('/2fa/enable', { 
            method: 'POST',
            body: JSON.stringify({ token: "dummy", code: code })
        });
        document.getElementById('2fa-setup-area').innerHTML = '<p style="color:var(--status-low); margin-top:1rem; font-weight:bold;">2FA Enabled Successfully!</p>';
    } catch (error) {
        err.innerText = error.message;
        err.classList.remove('hidden');
    }
}

// Security Logic - Change Password
document.getElementById('change-password-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = document.getElementById('change-pwd-btn');
    const msg = document.getElementById('settings-message');
    msg.classList.add('hidden');
    btn.disabled = true;

    try {
        await authFetch('/change-password', {
            method: 'POST',
            body: JSON.stringify({
                old_password: document.getElementById('old-password').value,
                new_password: document.getElementById('new-password').value
            })
        });
        msg.innerText = "Password updated successfully!";
        msg.style.color = "var(--status-low)";
        msg.style.background = "rgba(34, 197, 94, 0.1)";
        msg.classList.remove('hidden');
        document.getElementById('change-password-form').reset();
    } catch (error) {
        msg.innerText = error.message;
        msg.style.color = "var(--status-critical)";
        msg.style.background = "rgba(248, 113, 113, 0.1)";
        msg.classList.remove('hidden');
    } finally {
        btn.disabled = false;
    }
});

// Profile & Loan Management Additions

async function loadEditProfile() {
    try {
        const profile = await authFetch('/profile');
        document.getElementById('prof-name').value = profile.Name || '';
        document.getElementById('prof-income').value = profile.MonthlyIncome || '';
        document.getElementById('prof-expenses').value = profile.MonthlyExpenses || '';
        document.getElementById('prof-savings').value = profile.Savings || '';
        document.getElementById('prof-credit').value = profile.CreditScore || '';
        if (profile.EmploymentStatus) {
            document.getElementById('prof-employment').value = profile.EmploymentStatus;
        }
        document.getElementById('prof-goals').value = profile.FinancialGoals || '';
        showSection('edit-profile-section');
    } catch (error) {
        alert("Error loading profile: " + error.message);
    }
}

document.getElementById('edit-profile-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = document.getElementById('save-profile-btn');
    const err = document.getElementById('profile-error');
    err.classList.add('hidden');
    btn.disabled = true;

    try {
        await authFetch('/profile', {
            method: 'PUT',
            body: JSON.stringify({
                name: document.getElementById('prof-name').value,
                income: parseFloat(document.getElementById('prof-income').value),
                expenses: parseFloat(document.getElementById('prof-expenses').value),
                savings: parseFloat(document.getElementById('prof-savings').value) || 0,
                credit_score: parseInt(document.getElementById('prof-credit').value) || null,
                employment_status: document.getElementById('prof-employment').value,
                financial_goals: document.getElementById('prof-goals').value
            })
        });
        showSection('dashboard-section');
        loadDashboard(); // Refresh dashboard data
    } catch (error) {
        err.innerText = error.message;
        err.classList.remove('hidden');
    } finally {
        btn.disabled = false;
    }
});

function openAddLoan() {
    document.getElementById('add-loan-form').reset();
    document.getElementById('loan-id-hidden').value = '';
    document.getElementById('loan-form-title').innerText = 'Add New Loan';
    document.getElementById('loan-lender-other').classList.add('hidden');
    document.getElementById('loan-type-other').classList.add('hidden');
    showSection('add-loan-section');
}

function openEditLoan(loanId) {
    const loan = allLoans.find(l => l.LoanID === loanId);
    if (!loan) return;
    
    document.getElementById('loan-id-hidden').value = loan.LoanID;
    document.getElementById('loan-form-title').innerText = 'Edit Loan';
    
    const lenderSelect = document.getElementById('loan-lender');
    const typeSelect = document.getElementById('loan-type');
    
    if (Array.from(lenderSelect.options).some(o => o.value === loan.LenderName)) {
        lenderSelect.value = loan.LenderName;
        document.getElementById('loan-lender-other').classList.add('hidden');
    } else {
        lenderSelect.value = 'Other';
        document.getElementById('loan-lender-other').value = loan.LenderName;
        document.getElementById('loan-lender-other').classList.remove('hidden');
    }

    if (Array.from(typeSelect.options).some(o => o.value === loan.LoanType)) {
        typeSelect.value = loan.LoanType;
        document.getElementById('loan-type-other').classList.add('hidden');
    } else {
        typeSelect.value = 'Other';
        document.getElementById('loan-type-other').value = loan.LoanType;
        document.getElementById('loan-type-other').classList.remove('hidden');
    }

    document.getElementById('loan-amount').value = loan.OutstandingAmount;
    document.getElementById('loan-rate').value = loan.InterestRate;
    document.getElementById('loan-emi').value = loan.EMI;
    document.getElementById('loan-overdue').value = loan.OverdueMonths;
    document.getElementById('loan-start').value = loan.StartDate ? loan.StartDate.split('T')[0] : '';
    document.getElementById('loan-due').value = loan.DueDate ? loan.DueDate.split('T')[0] : '';
    document.getElementById('loan-status').value = loan.Status || 'Active';

    showSection('add-loan-section');
}

async function deleteLoan(loanId) {
    if (!confirm("Are you sure you want to delete this loan?")) return;
    try {
        await authFetch(`/loans/${loanId}`, { method: 'DELETE' });
        loadDashboard();
    } catch (error) {
        alert("Failed to delete loan: " + error.message);
    }
}

// AI History
async function loadAIHistory() {
    try {
        const history = await authFetch('/ai-history');
        const container = document.getElementById('ai-history-container');
        
        if (history.length === 0) {
            container.innerHTML = '<p>No AI history found. Run some analysis first!</p>';
        } else {
            container.innerHTML = history.map(item => `
                <div class="glass-panel mb-4" style="text-align: left;">
                    <div class="flex justify-between align-center mb-2">
                        <span class="badge badge-medium" style="background:var(--accent); color:white;">${item.QueryType}</span>
                        <span style="font-size:0.8rem; color:var(--text-muted);">${new Date(item.Timestamp).toLocaleString()}</span>
                    </div>
                    <div class="markdown-content" style="font-size:0.95rem; line-height:1.6;">
                        ${typeof marked !== 'undefined' ? DOMPurify.sanitize(marked.parse(item.GeneratedContent)) : item.GeneratedContent}
                    </div>
                </div>
            `).join('');
        }
        
        showSection('ai-history-section');
    } catch (error) {
        alert("Error loading AI history: " + error.message);
    }
}

// ---------------------------------
// AI Payoff Planner
// ---------------------------------
async function loadPayoffPlanner() {
    const container = document.getElementById('payoff-planner-content');
    container.innerHTML = '<div class="spinner"></div>';
    
    try {
        const data = await authFetch('/payoff-planner');
        
        container.innerHTML = `
            <div class="summary-card text-center" style="grid-column: 1 / -1; margin-bottom: 1rem;">
                <h4>Monthly Surplus Used: $${data.surplus_used.toFixed(2)}</h4>
            </div>
            <div class="summary-card">
                <h4>❄️ Debt Snowball (Lowest Balance First)</h4>
                <p>Months to Debt Free: <strong>${data.snowball.months} months</strong></p>
                <p>Total Interest Paid: <strong>$${data.snowball.total_interest_paid.toFixed(2)}</strong></p>
            </div>
            <div class="summary-card">
                <h4>⛰️ Debt Avalanche (Highest Interest First)</h4>
                <p>Months to Debt Free: <strong>${data.avalanche.months} months</strong></p>
                <p>Total Interest Paid: <strong>$${data.avalanche.total_interest_paid.toFixed(2)}</strong></p>
            </div>
        `;
    } catch (error) {
        container.innerHTML = `<p class="error-message">Error loading planner: ${error.message}</p>`;
    }
}

async function exportCSV() {
    try {
        const data = await authFetch('/dashboard');
        let csvContent = "data:text/csv;charset=utf-8,";
        csvContent += "Lender Name,Loan Type,Outstanding Amount,EMI,Interest Rate,Overdue Months,Status\n";
        
        data.loans.forEach(loan => {
            const row = `"${loan.LenderName}","${loan.LoanType}",${loan.OutstandingAmount},${loan.EMI},${loan.InterestRate || 0},${loan.OverdueMonths},"${loan.Status}"`;
            csvContent += row + "\n";
        });
        
        const encodedUri = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", "finrelief_financial_health.csv");
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    } catch(err) {
        alert("Error exporting CSV: " + err.message);
    }
}

// ---------------------------------
// Loan CRUD
// ---------------------------------
// AI Chatbot Logic
// ---------------------------------
function toggleChatbot() {
    const chatbot = document.getElementById('chatbot-container');
    if (chatbot.classList.contains('hidden')) {
        chatbot.classList.remove('hidden');
    } else {
        chatbot.classList.add('hidden');
    }
}

async function sendChatMessage() {
    const inputField = document.getElementById('chatbot-input-field');
    const msg = inputField.value.trim();
    if (!msg) return;

    inputField.value = '';
    const messagesContainer = document.getElementById('chatbot-messages');
    
    // Add user msg
    const userDiv = document.createElement('div');
    userDiv.className = 'chat-msg user-msg';
    userDiv.innerText = msg;
    messagesContainer.appendChild(userDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    // Add loading
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'chat-msg bot-msg';
    loadingDiv.innerHTML = '<div class="spinner" style="width:16px; height:16px;"></div>';
    messagesContainer.appendChild(loadingDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    try {
        const data = await authFetch('/chat', {
            method: 'POST',
            body: JSON.stringify({ message: msg })
        });
        
        messagesContainer.removeChild(loadingDiv);
        
        const botDiv = document.createElement('div');
        botDiv.className = 'chat-msg bot-msg markdown-content';
        botDiv.innerHTML = DOMPurify.sanitize(marked.parse(data.response));
        messagesContainer.appendChild(botDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        
    } catch (error) {
        messagesContainer.removeChild(loadingDiv);
        const errDiv = document.createElement('div');
        errDiv.className = 'chat-msg bot-msg';
        errDiv.style.color = 'var(--status-critical)';
        errDiv.innerText = "Error: " + error.message;
        messagesContainer.appendChild(errDiv);
    }
}

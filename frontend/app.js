document.addEventListener("DOMContentLoaded", () => {
    // DOM Elements
    const healthStatusEl = document.getElementById("health-status");
    const form = document.getElementById("financial-form");
    const submitBtn = document.getElementById("analyze-btn");
    const loadingSpinner = document.getElementById("loading-spinner");
    const resultsContainer = document.getElementById("results-container");
    const errorContainer = document.getElementById("error-container");
    const errorMessageEl = document.getElementById("error-message");
    const adviceContent = document.getElementById("ai-advice-content");
    
    // Auth DOM Elements
    const authModal = document.getElementById("auth-modal");
    const closeModalBtn = document.getElementById("close-modal");
    const navLoginBtn = document.getElementById("nav-login-btn");
    const navUserInfo = document.getElementById("nav-user-info");
    const logoutBtn = document.getElementById("logout-btn");
    
    const authForm = document.getElementById("auth-form");
    const authTitle = document.getElementById("auth-title");
    const authToggleLink = document.getElementById("auth-toggle-link");
    const authToggleText = document.getElementById("auth-toggle-text");
    const nameGroup = document.getElementById("name-group");
    const signupExtraFields = document.getElementById("signup-extra-fields");
    const authError = document.getElementById("auth-error");
    const authSubmitBtn = document.getElementById("auth-submit-btn");

    let isLoginMode = true;
    let currentToken = localStorage.getItem("finrelief_token");

    // Ping the backend API for health
    fetch("http://localhost:8000/health")
        .then(response => {
            if (!response.ok) throw new Error("Network response was not ok");
            return response.json();
        })
        .then(data => {
            if (data.status === "healthy") {
                healthStatusEl.textContent = "✅ Connected to backend successfully!";
                healthStatusEl.style.color = "#4ade80";
            }
        })
        .catch(error => {
            healthStatusEl.textContent = "❌ Cannot reach backend (ensure FastAPI is running on port 8000)";
            healthStatusEl.style.color = "#f87171";
            console.error("API Health Check Failed:", error);
        });

    // Update UI based on auth state
    function updateAuthState() {
        if (currentToken) {
            navLoginBtn.classList.add("hidden");
            navUserInfo.classList.remove("hidden");
        } else {
            navLoginBtn.classList.remove("hidden");
            navUserInfo.classList.add("hidden");
        }
    }
    updateAuthState();

    // Modal Toggles
    navLoginBtn.addEventListener("click", () => {
        authModal.classList.remove("hidden");
    });

    closeModalBtn.addEventListener("click", () => {
        authModal.classList.add("hidden");
    });

    logoutBtn.addEventListener("click", (e) => {
        e.preventDefault();
        currentToken = null;
        localStorage.removeItem("finrelief_token");
        updateAuthState();
        resultsContainer.classList.add("hidden");
        errorContainer.classList.add("hidden");
    });

    authToggleLink.addEventListener("click", (e) => {
        e.preventDefault();
        isLoginMode = !isLoginMode;
        authError.classList.add("hidden");
        if (isLoginMode) {
            authTitle.textContent = "Log In";
            nameGroup.classList.add("hidden");
            signupExtraFields.classList.add("hidden");
            authSubmitBtn.textContent = "Log In";
            authToggleText.textContent = "Don't have an account? ";
            authToggleLink.textContent = "Sign Up";
        } else {
            authTitle.textContent = "Sign Up";
            nameGroup.classList.remove("hidden");
            signupExtraFields.classList.remove("hidden");
            authSubmitBtn.textContent = "Sign Up";
            authToggleText.textContent = "Already have an account? ";
            authToggleLink.textContent = "Log In";
        }
    });

    // Auth Form Submission
    authForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        authError.classList.add("hidden");
        authSubmitBtn.disabled = true;

        const email = document.getElementById("auth-email").value;
        const password = document.getElementById("auth-password").value;

        try {
            let response;
            if (isLoginMode) {
                // OAuth2 uses application/x-www-form-urlencoded
                const formData = new URLSearchParams();
                formData.append("username", email);
                formData.append("password", password);

                response = await fetch("http://localhost:8000/api/login", {
                    method: "POST",
                    headers: { "Content-Type": "application/x-www-form-urlencoded" },
                    body: formData
                });
            } else {
                const name = document.getElementById("auth-name").value;
                const income = parseFloat(document.getElementById("auth-income").value) || 0;
                const expenses = parseFloat(document.getElementById("auth-expenses").value) || 0;

                response = await fetch("http://localhost:8000/api/signup", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ name, email, password, income, expenses })
                });
            }

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || "Authentication failed");
            }

            const data = await response.json();
            currentToken = data.access_token;
            localStorage.setItem("finrelief_token", currentToken);
            
            updateAuthState();
            authModal.classList.add("hidden");
            authForm.reset();

        } catch (error) {
            authError.textContent = error.message;
            authError.classList.remove("hidden");
        } finally {
            authSubmitBtn.disabled = false;
        }
    });

    // Handle financial form submission
    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        
        if (!currentToken) {
            authModal.classList.remove("hidden");
            return;
        }

        // Get values
        const totalDebt = parseFloat(document.getElementById("total-debt").value);
        const monthlyIncome = parseFloat(document.getElementById("monthly-income").value);
        const monthlyExpenses = parseFloat(document.getElementById("monthly-expenses").value);

        // UI Updates
        submitBtn.disabled = true;
        submitBtn.textContent = "Analyzing...";
        resultsContainer.classList.add("hidden");
        errorContainer.classList.add("hidden");
        loadingSpinner.classList.remove("hidden");
        adviceContent.innerHTML = "";

        const payload = {
            total_debt: totalDebt,
            monthly_income: monthlyIncome,
            monthly_expenses: monthlyExpenses
        };

        // Create AbortController for timeout (e.g. 30 seconds)
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 30000);

        try {
            const response = await fetch("http://localhost:8000/api/analyze-debt", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${currentToken}`
                },
                body: JSON.stringify(payload),
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                if (response.status === 401) {
                    // Token expired or invalid
                    currentToken = null;
                    localStorage.removeItem("finrelief_token");
                    updateAuthState();
                    authModal.classList.remove("hidden");
                    throw new Error("Your session has expired. Please log in again.");
                }
                const errData = await response.json();
                throw new Error(errData.detail || `Server Error: ${response.status}`);
            }

            const data = await response.json();
            
            adviceContent.innerHTML = marked.parse(data.advice);
            loadingSpinner.classList.add("hidden");
            resultsContainer.classList.remove("hidden");

        } catch (error) {
            console.error("Error analyzing debt:", error);
            clearTimeout(timeoutId);
            
            loadingSpinner.classList.add("hidden");
            errorContainer.classList.remove("hidden");
            
            if (error.name === 'AbortError') {
                errorMessageEl.textContent = "The request timed out. The AI service might be experiencing high demand. Please try again.";
            } else {
                errorMessageEl.textContent = error.message;
            }
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = "Generate AI Plan";
        }
    });
});

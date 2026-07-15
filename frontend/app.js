document.addEventListener("DOMContentLoaded", () => {
    const healthStatusEl = document.getElementById("health-status");
    const form = document.getElementById("financial-form");
    const submitBtn = document.getElementById("analyze-btn");
    const loadingSpinner = document.getElementById("loading-spinner");
    const resultsContainer = document.getElementById("results-container");
    const adviceContent = document.getElementById("ai-advice-content");

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

    // Handle form submission
    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        // Get values
        const totalDebt = parseFloat(document.getElementById("total-debt").value);
        const monthlyIncome = parseFloat(document.getElementById("monthly-income").value);
        const monthlyExpenses = parseFloat(document.getElementById("monthly-expenses").value);

        // UI Updates: Show loading, hide previous results
        submitBtn.disabled = true;
        submitBtn.textContent = "Analyzing...";
        resultsContainer.classList.add("hidden");
        loadingSpinner.classList.remove("hidden");
        adviceContent.innerHTML = "";

        // Prepare payload (using a random session ID for this iteration)
        const payload = {
            total_debt: totalDebt,
            monthly_income: monthlyIncome,
            monthly_expenses: monthlyExpenses,
            session_id: crypto.randomUUID()
        };

        try {
            const response = await fetch("http://localhost:8000/api/analyze-debt", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || `Server Error: ${response.status}`);
            }

            const data = await response.json();
            
            // Render markdown using the 'marked' library included in index.html
            adviceContent.innerHTML = marked.parse(data.advice);
            
            // Hide loading, show results
            loadingSpinner.classList.add("hidden");
            resultsContainer.classList.remove("hidden");

        } catch (error) {
            console.error("Error analyzing debt:", error);
            adviceContent.innerHTML = `<p style="color: #f87171;">An error occurred while generating your plan: ${error.message}</p><p>Is the backend running and the Gemini API key set?</p>`;
            loadingSpinner.classList.add("hidden");
            resultsContainer.classList.remove("hidden");
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = "Generate AI Plan";
        }
    });
});

// Cyberbullying Detection System - Frontend JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('predictionForm');
    
    // Check if form exists (for new template compatibility)
    if (!form) {
        console.log('Using new template with inline handlers');
        return;
    }
    
    const textInput = document.getElementById('textInput');
    const sourceType = document.getElementById('sourceType');
    const analyzeBtn = form.querySelector('button[type="submit"]');
    const resultCard = document.getElementById('resultCard');
    const errorCard = document.getElementById('errorCard');

    // Form submission
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const text = textInput.value.trim();
        if (!text) {
            showError('Please enter some text to analyze');
            return;
        }

        // Show loading state
        setLoading(true);
        hideResults();

        try {
            const response = await fetch('/api/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: text,
                    source_type: sourceType.value
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Prediction failed');
            }

            displayResult(data);
        } catch (error) {
            showError(error.message);
        } finally {
            setLoading(false);
        }
    });

    function displayResult(data) {
        // Hide error card
        errorCard.style.display = 'none';

        // Handle both basic and enhanced API response formats
        const label = data.ensemble_label || data.label || 'Unknown';
        const confidence = data.ensemble_confidence !== undefined ? data.ensemble_confidence : data.confidence;
        const prediction = data.ensemble_prediction !== undefined ? data.ensemble_prediction : data.prediction;
        const sourceType = data.ml_source || data.source_type || 'auto';
        const text = data.text || '';
        const latency = data.total_latency_ms || data.latency_ms || 0;

        // Update result label
        const resultLabel = document.getElementById('resultLabel');
        resultLabel.textContent = label;
        
        // Set color based on prediction
        if (prediction === 0) {
            resultLabel.className = 'result-label safe';
        } else {
            resultLabel.className = 'result-label danger';
        }

        // Update source type
        const resultSource = document.getElementById('resultSource');
        if (resultSource) {
            resultSource.textContent = `Source: ${capitalizeFirst(sourceType)}`;
        }

        // Update confidence bar
        const confidenceBar = document.getElementById('confidenceBar');
        const confidenceValue = document.getElementById('confidenceValue');
        const confidencePercent = confidence !== undefined && !isNaN(confidence) ? (confidence * 100).toFixed(1) : '0.0';
        
        confidenceBar.style.width = confidencePercent + '%';
        confidenceValue.textContent = confidencePercent + '%';

        // Update details
        document.getElementById('analyzedText').textContent = text;
        document.getElementById('latency').textContent = latency.toFixed(2) + ' ms';

        // Show result card with animation
        resultCard.style.display = 'block';
        resultCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    // Make displayResult available globally for enhanced template
    window.displayResult = displayResult;

    function showError(message) {
        resultCard.style.display = 'none';
        errorCard.style.display = 'block';
        document.getElementById('errorMessage').textContent = message;
        errorCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    // Make showError available globally for enhanced template
    window.showError = showError;

    function hideResults() {
        resultCard.style.display = 'none';
        errorCard.style.display = 'none';
    }

    function setLoading(isLoading) {
        if (!analyzeBtn) return;
        
        const btnText = analyzeBtn.querySelector('.btn-text');
        const spinner = analyzeBtn.querySelector('.spinner');
        
        if (btnText && spinner) {
            if (isLoading) {
                btnText.style.display = 'none';
                spinner.style.display = 'inline-block';
                analyzeBtn.disabled = true;
            } else {
                btnText.style.display = 'inline';
                spinner.style.display = 'none';
                analyzeBtn.disabled = false;
            }
        }
    }

    function capitalizeFirst(str) {
        if (!str || typeof str !== 'string') return 'Unknown';
        return str.charAt(0).toUpperCase() + str.slice(1);
    }
});

// Fill example text
function fillExample(text, source) {
    document.getElementById('textInput').value = text;
    document.getElementById('sourceType').value = source;
    
    // Scroll to form
    document.getElementById('predictionForm').scrollIntoView({ 
        behavior: 'smooth', 
        block: 'start' 
    });
    
    // Focus on textarea
    setTimeout(() => {
        document.getElementById('textInput').focus();
    }, 500);
}

// Check API health on load
async function checkAPIHealth() {
    try {
        const response = await fetch('/api/health');
        const data = await response.json();
        console.log('API Status:', data);
    } catch (error) {
        console.error('API health check failed:', error);
    }
}

checkAPIHealth();

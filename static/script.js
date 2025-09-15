document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('run-form');
    const runButton = document.getElementById('run-button');
    const resultsContainer = document.getElementById('results-container');
    
    let statusInterval;

    const loadingStatuses = [
        "Connecting to Deep Space Network...",
        "Calibrating Graviton Detectors...",
        "Querying Gamma-Ray Burst Catalog...",
        "Aggregating Neutrino Event Streams...",
        "Compiling Spacetime Coordinates...",
        "Running Correlation Matrix...",
        "Analyzing Probability Manifolds...",
        "Rendering Sky Map..."
    ];

    function showLoadingStatus() {
        let statusIndex = 0;
        resultsContainer.innerHTML = `<div class="status-message" id="status-text"></div>`;
        const statusElement = document.getElementById('status-text');
        
        statusElement.textContent = loadingStatuses[statusIndex];
        
        statusInterval = setInterval(() => {
            statusIndex = (statusIndex + 1) % loadingStatuses.length;
            statusElement.textContent = loadingStatuses[statusIndex];
        }, 1500);
    }

    function stopLoadingStatus() {
        clearInterval(statusInterval);
    }

    form.addEventListener('submit', async function(event) {
        event.preventDefault();
        runButton.disabled = true;
        runButton.querySelector('.button-text').textContent = 'PROCESSING...';
        showLoadingStatus();

        const payload = {
            noiseEvents: document.getElementById('noise-events').value,
            truePairs: document.getElementById('true-pairs').value,
            timeWindow: document.getElementById('time-window').value,
            angleSep: document.getElementById('angle-sep').value,
        };

        try {
            const response = await fetch('/run', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });
            
            const data = await response.json();
            stopLoadingStatus();

            if (!response.ok) {
                throw new Error(data.error || `A communications uplink error occurred [${response.status}]`);
            }
            
            displayResults(data);

        } catch (error) {
            stopLoadingStatus();
            resultsContainer.innerHTML = `
                <div class="status-message error-message">
                    <p>// FATAL ERROR //</p>
                    <p>${error.message}</p>
                </div>`;
            console.error('System Error:', error);
        } finally {
            runButton.disabled = false;
            runButton.querySelector('.button-text').textContent = 'INITIATE SCAN';
        }
    });

    function displayResults(data) {
        resultsContainer.innerHTML = '';
        const timestamp = new Date().getTime();

        const skyMapSection = document.createElement('div');
        skyMapSection.className = 'result-section';
        skyMapSection.innerHTML = `
            <h2 class="panel-title">ALL-SKY DATA STREAM</h2>
            <img src="${data.all_sky_plot_url}?t=${timestamp}" alt="All-sky map of events">
        `;
        resultsContainer.appendChild(skyMapSection);

        const correlationsSection = document.createElement('div');
        correlationsSection.className = 'result-section';
        const count = data.correlations.length;
        correlationsSection.innerHTML = `<h2 class="panel-title">CORRELATION SIGNALS DETECTED: ${count}</h2>`;
        
        if (count > 0) {
            data.correlations.forEach((corr, index) => {
                const card = document.createElement('div');
                card.className = 'correlation-card';
                card.style.setProperty('--animation-delay', `${0.5 + index * 0.1}s`);
                
                card.innerHTML = `
                    <h3>Signal Pair #${corr.id + 1} // Confidence: ${corr.probability}</h3>
                    <p>
                        <b>Source A:</b> ${corr.event1_id} (${corr.event1_source})<br>
                        <b>Source B:</b> ${corr.event2_id} (${corr.event2_source})<br>
                        <b>Δt:</b> ${corr.time_sep_hrs} hrs | <b>Δθ:</b> ${corr.ang_sep_deg}°
                    </p>
                    <img src="${corr.detail_plot_url}?t=${timestamp}" alt="Correlation detail plot">
                `;
                correlationsSection.appendChild(card);
            });
        } else {
            correlationsSection.innerHTML += `<p class="status-message">No significant cross-messenger correlations found in data stream.</p>`;
        }
        resultsContainer.appendChild(correlationsSection);
    }
});
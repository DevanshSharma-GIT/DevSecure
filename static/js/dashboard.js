document.getElementById('scan-form').addEventListener('submit', async function(event) {
    event.preventDefault();
    const url = document.getElementById('url-input').value;
    const resultsDiv = document.getElementById('results');
    
    // Display scanning message
    resultsDiv.innerHTML = '<p class="scanning-message">Scanning...</p>';
    document.getElementById('download-report').style.display = 'none';
    
    try {
        console.log('Sending scan request for:', url);
        const response = await fetch('/scan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url })
        });
        
        console.log('Response status:', response.status);
        const result = await response.json();
        console.log('Raw scan result:', result);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        if (result.error) {
            throw new Error(result.error);
        }
        
        // Validate results format
        if (!result || typeof result !== 'object' || Object.keys(result).length === 0) {
            throw new Error('Invalid or empty scan results');
        }
        
        let html = '<table class="results-table"><tr><th>Check</th><th>Status</th><th>Details</th></tr>';
        for (const [check, data] of Object.entries(result)) {
            if (data && typeof data === 'object' && 'status' in data && 'details' in data) {
                console.log(`Rendering check: ${check}`, data);
                html += `<tr><td>${check}</td><td class="${data.status.toLowerCase()}">${data.status}</td><td>${data.details}</td></tr>`;
            } else {
                console.warn(`Skipping invalid check: ${check}`, data);
            }
        }
        html += '</table>';
        
        if (html.includes('<tr>')) {
            resultsDiv.innerHTML = html;
            document.getElementById('download-report').style.display = 'block';
        } else {
            throw new Error('No valid checks to display');
        }
    } catch (error) {
        console.error('Scan error:', error);
        resultsDiv.innerHTML = `<p class="error-message">Error scanning URL: ${error.message}. Please check the URL and try again.</p>`;
    }
});

document.getElementById('download-report').addEventListener('click', async function() {
    const url = document.getElementById('url-input').value;
    const resultsDiv = document.getElementById('results');
    
    try {
        console.log('Sending download request for:', url);
        const response = await fetch('/download', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url })
        });
        
        console.log('Download response status:', response.status);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const blob = await response.blob();
        const link = document.createElement('a');
        link.href = window.URL.createObjectURL(blob);
        link.download = 'scan_report.pdf';
        link.click();
        console.log('PDF download initiated');
    } catch (error) {
        console.error('Download error:', error);
        resultsDiv.innerHTML = `<p class="error-message">Error generating report: ${error.message}. Please try again.</p>`;
    }
});
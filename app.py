from flask import Flask, render_template, request, jsonify, send_file
import io
import logging
import traceback
from scanner.scanner import scan_website
from scanner.report import generate_pdf_report

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/scan', methods=['POST'])
def scan():
    data = request.get_json()
    url = data.get('url')
    if not url:
        logger.error("No URL provided in scan request")
        return jsonify({'error': 'URL is required'}), 400
    
    # Basic URL validation
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        results = scan_website(url)
        if not results:
            logger.error("No results returned from scan_website")
            return jsonify({'error': 'No results returned from scan'}), 500
        logger.debug(f"Scan results for {url}: {results}")
        return jsonify(results)
    except Exception as e:
        logger.error(f"Scan failed for {url}: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': f'Scan failed: {str(e)}'}), 500

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    url = data.get('url')
    if not url:
        logger.error("No URL provided in download request")
        return jsonify({'error': 'URL is required'}), 400
    
    # Basic URL validation
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        results = scan_website(url)
        if not results:
            logger.error("No results returned from scan_website for download")
            return jsonify({'error': 'No results returned from scan'}), 500
        pdf = generate_pdf_report(results, url)
        logger.debug(f"PDF generated for {url}")
        return send_file(
            io.BytesIO(pdf),
            mimetype='application/pdf',
            as_attachment=True,
            download_name='scan_report.pdf'
        )
    except Exception as e:
        logger.error(f"Download failed for {url}: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': f'Report generation failed: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
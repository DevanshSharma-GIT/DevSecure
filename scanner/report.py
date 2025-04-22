from weasyprint import HTML
import logging

logging.basicConfig(level=logging.DEBUG)

def generate_pdf_report(results, url):
    """
    Generate a PDF report from scan results using WeasyPrint.
    """
    try:
        logging.debug(f"Generating PDF for URL: {url}")
        html = """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                h1 { color: #00ff88; text-align: center; }
                table { width: 100%; border-collapse: collapse; margin-top: 20px; }
                th, td { border: 1px solid #444; padding: 10px; text-align: left; }
                th { background: #00ff88; color: #1a1a1a; }
                .safe { color: #00ff88; }
                .warning { color: #ffbb33; }
                .critical { color: #ff4444; }
            </style>
        </head>
        <body>
        """
        html += f"<h1>Scan Report for {url}</h1>"
        html += "<table><tr><th>Check</th><th>Status</th><th>Details</th></tr>"
        for check, data in results.items():
            status_class = data['status'].lower()
            html += f"<tr><td>{check}</td><td class='{status_class}'>{data['status']}</td><td>{data['details']}</td></tr>"
        html += "</table></body></html>"
        
        pdf = HTML(string=html).write_pdf()
        logging.debug("PDF generated successfully")
        return pdf
    except Exception as e:
        logging.error(f"PDF generation failed: {str(e)}")
        raise
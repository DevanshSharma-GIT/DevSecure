import requests
import ssl
import socket
from urllib.parse import urlparse
import logging

logging.basicConfig(level=logging.DEBUG)

def scan_website(url):
    """
    Perform basic website security scans: HTTP status, headers, and SSL verification.
    Returns a dictionary with check results.
    """
    results = {}
    parsed_url = urlparse(url)
    hostname = parsed_url.netloc or parsed_url.path  # Extract hostname (e.g., example.com)
    
    try:
        logging.debug(f"Scanning URL: {url}")
        
        # HTTP Status and Headers
        try:
            response = requests.get(url, timeout=10)
            results["HTTP Status"] = {
                "status": "Safe" if response.status_code == 200 else "Warning",
                "details": f"Status code: {response.status_code}"
            }
            
            # Check for critical security headers
            headers = response.headers
            missing_headers = []
            for header in ["X-Frame-Options", "X-Content-Type-Options", "Content-Security-Policy"]:
                if header not in headers:
                    missing_headers.append(header)
            results["Security Headers"] = {
                "status": "Safe" if not missing_headers else "Warning",
                "details": "All headers present" if not missing_headers else f"Missing: {', '.join(missing_headers)}"
            }
        except requests.RequestException as e:
            results["HTTP Status"] = {"status": "Critical", "details": f"HTTP request failed: {str(e)}"}
            results["Security Headers"] = {"status": "Critical", "details": "Unable to check headers"}
        
        # SSL Verification
        try:
            context = ssl.create_default_context()
            with socket.create_connection((hostname, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    issuer = cert.get('issuer', [[['', 'Unknown']]])[-1][-1][1]
                    results["SSL"] = {
                        "status": "Safe",
                        "details": f"SSL certificate valid (Issuer: {issuer})"
                    }
        except (ssl.SSLError, socket.timeout, socket.gaierror) as e:
            results["SSL"] = {"status": "Critical", "details": f"SSL check failed: {str(e)}"}
        
        logging.debug(f"Scan results: {results}")
        return results
    
    except Exception as e:
        logging.error(f"Error in scan_website: {str(e)}")
        raise Exception(f"Scan failed: {str(e)}")
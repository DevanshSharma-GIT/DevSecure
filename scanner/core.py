import requests
import socket
import ssl
import whois
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re
from datetime import datetime

def scan_website(url):
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    parsed_url = urlparse(url)
    hostname = parsed_url.hostname
    
    results = {
        'url': url,
        'timestamp': datetime.now().isoformat(),
        'headers': scan_headers(url),
        'ports': port_scan(hostname),
        'ssl': ssl_check(url, hostname),
        'sqli_xss': sql_xss_checker(url),
        'whois': whois_lookup(hostname),
        'exposed_files': check_exposed_files(url)
    }
    return results

def scan_headers(url):
    try:
        response = requests.get(url, timeout=5)
        headers = response.headers
        issues = []
        security_headers = {
            'Content-Security-Policy': 'Missing CSP header',
            'X-Content-Type-Options': 'Missing X-Content-Type-Options header',
            'X-Frame-Options': 'Missing X-Frame-Options header',
            'Strict-Transport-Security': 'Missing HSTS header'
        }
        for header, message in security_headers.items():
            if header not in headers:
                issues.append({'severity': 'medium', 'message': message})
        return {'status': 'safe' if not issues else 'warning', 'issues': issues}
    except:
        return {'status': 'error', 'issues': [{'severity': 'critical', 'message': 'Failed to fetch headers'}]}

def port_scan(hostname):
    common_ports = [21, 22, 23, 25, 80, 443, 445, 3389]
    open_ports = []
    for port in common_ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((hostname, port))
            if result == 0:
                open_ports.append({'port': port, 'status': 'open', 'severity': 'high'})
            sock.close()
        except:
            continue
    return {'status': 'safe' if not open_ports else 'critical', 'ports': open_ports}

def ssl_check(url, hostname):
    try:
        response = requests.get(url, timeout=5)
        if not url.startswith('https://'):
            return {'status': 'critical', 'message': 'Site does not use HTTPS'}
        
        context = ssl.create_default_context()
        with socket.create_connection((hostname, 443)) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                expiry = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                if expiry < datetime.now():
                    return {'status': 'critical', 'message': 'SSL certificate expired'}
        return {'status': 'safe', 'message': 'Valid SSL certificate'}
    except:
        return {'status': 'error', 'message': 'SSL check failed'}

def sql_xss_checker(url):
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        forms = soup.find_all('form')
        issues = []
        
        # Basic SQLi check
        for form in forms:
            action = form.get('action', '')
            if any(param in action.lower() for param in ['id=', 'user=', 'search=']):
                issues.append({'severity': 'high', 'message': 'Potential SQLi vulnerability in form action'})
        
        # Basic XSS check
        scripts = soup.find_all('script')
        for script in scripts:
            if 'alert(' in script.text:
                issues.append({'severity': 'critical', 'message': 'Potential XSS vulnerability detected'})
        
        return {'status': 'safe' if not issues else 'critical', 'issues': issues}
    except:
        return {'status': 'error', 'issues': [{'severity': 'critical', 'message': 'Failed to check SQLi/XSS'}]}

def whois_lookup(hostname):
    try:
        w = whois.whois(hostname)
        return {'status': 'safe', 'data': {
            'domain': w.domain_name,
            'registrar': w.registrar,
            'creation_date': str(w.creation_date)
        }}
    except:
        return {'status': 'error', 'data': {}}

def check_exposed_files(url):
    files_to_check = ['.git/config', '.env', 'phpinfo.php']
    issues = []
    for file in files_to_check:
        try:
            response = requests.get(f"{url}/{file}", timeout=5)
            if response.status_code == 200:
                issues.append({'severity': 'critical', 'message': f'Exposed file: {file}'})
        except:
            continue
    return {'status': 'safe' if not issues else 'critical', 'issues': issues}
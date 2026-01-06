import streamlit as st
from dotenv import load_dotenv
import os
import requests
import nmap
import socket
import ssl
from urllib.parse import urlparse

# Load environment variables
load_dotenv()
XAI_API_KEY = os.getenv("XAI_API_KEY")

if not XAI_API_KEY:
    st.error("XAI_API_KEY not found in .env file. Please add it.")
    st.stop()

# Function to call xAI Grok API for remediation or threat intelligence
def get_grok_response(prompt):
    api_url = "https://api.x.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {XAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "grok-4-latest",
        "messages": [
            {"role": "system", "content": "You are a security expert providing concise remediation steps or threat intelligence."},
            {"role": "user", "content": prompt}
        ]
    }
    try:
        response = requests.post(api_url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error calling Grok API: {str(e)}"

# Function to perform basic passive scan
def scan_url(input_url):
    parsed_url = urlparse(input_url)
    host = parsed_url.hostname if parsed_url.hostname else input_url

    findings = []

    findings.append("**Disclaimer**: This is a basic passive scanner using Nmap for port scanning and simple HTTP/HTTPS checks. It does not perform active vulnerability testing like injecting payloads for SQLi or XSS, as that requires explicit permission and can be illegal without it. For comprehensive testing, use tools like OWASP ZAP or sqlmap with permission. Open ports may indicate potential exposure, but further manual assessment is needed.")

    try:
        nm = nmap.PortScanner()
        nm.scan(host, arguments='-p 1-1024 -sV --open')
        if host in nm.all_hosts() and 'tcp' in nm[host]:
            open_ports = nm[host]['tcp']
            if open_ports:
                port_info = "\n".join([f"Port {port}: {details['name']} ({details['version'] if 'version' in details else 'unknown'})" for port, details in open_ports.items()])
                findings.append(f"Open ports found (potential exposure, e.g., if database ports like 3306 are open, it could lead to SQL injection risks if not secured):\n{port_info}")
            else:
                findings.append("No open ports found in range 1-1024.")
        else:
            findings.append("No hosts or TCP ports found.")
    except Exception as e:
        findings.append(f"Error during Nmap scan: {str(e)}. Ensure nmap is installed and accessible.")

    try:
        https_url = f"https://{host}"
        res = requests.get(https_url, timeout=5)
        findings.append("Site supports HTTPS.")

        headers = res.headers
        missing_headers = []
        security_headers = {
            'Content-Security-Policy': 'CSP (helps prevent XSS)',
            'X-Frame-Options': 'Prevents clickjacking',
            'X-XSS-Protection': 'XSS protection (legacy but useful)',
            'Strict-Transport-Security': 'HSTS (enforces HTTPS)'
        }
        for header, desc in security_headers.items():
            if header not in headers:
                missing_headers.append(f"{header} ({desc})")
        if missing_headers:
            findings.append(f"Missing security headers (potential XSS or other risks):\n" + "\n".join(missing_headers))
        else:
            findings.append("All checked security headers are present.")
    except requests.exceptions.SSLError:
        findings.append("SSL/TLS error - possible weak or invalid certificate.")
    except:
        findings.append("Site does not support HTTPS or is unreachable over HTTPS (weak encryption risk - recommend enabling HTTPS).")

    try:
        context = ssl.create_default_context()
        with socket.create_connection((host, 443)) as sock:
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                tls_version = ssock.version()
                if tls_version in ['TLSv1.0', 'TLSv1.1']:
                    findings.append(f"Weak TLS version detected: {tls_version} (recommend upgrading to TLSv1.2 or higher).")
                else:
                    findings.append(f"TLS version: {tls_version} (acceptable).")
    except Exception as e:
        findings.append(f"Error checking TLS version: {str(e)}.")

    return findings

# Streamlit App
st.title("Automated Web Vulnerability Auditor")

st.write("Enter a website URL to perform a basic passive scan for common security issues. A report with findings, remediation steps, and current threat intelligence will be generated.")

url = st.text_input("Website URL (e.g., example.com)")

if st.button("Scan"):
    if url:
        with st.spinner("Scanning..."):
            findings = scan_url(url)
        
        st.subheader("Scan Findings")
        for finding in findings:
            st.write(finding)
            
            if finding.startswith("Open ports found") or finding.startswith("Missing security headers") or finding.startswith("Weak TLS version") or finding.startswith("Site does not support HTTPS") or finding.startswith("SSL/TLS error"):
                rem_prompt = f"Provide concise remediation steps for the following web security issue: {finding}"
                remediation = get_grok_response(rem_prompt)
                st.write("**Remediation Steps:**")
                st.write(remediation)
                
                threat_prompt = f"Provide current threat intelligence related to the following web security issue: {finding[:100]}..."
                threat_intel = get_grok_response(threat_prompt)
                st.write("**Current Threat Intelligence (via Grok):**")
                st.write(threat_intel)
    else:
        st.error("Please enter a URL.")

# Advanced section - Fixed with multiple st.write() calls to avoid triple-quote issues
st.header("Advanced: API Integrations for Continuous Monitoring")

st.write("For continuous monitoring, this app can be extended with scheduling tools. Here's a basic example of how to integrate:")

st.markdown("""
1. Use a tool like **cron** (on Linux/Mac) or **Task Scheduler** (Windows) to run a Python script periodically that calls the scan function and sends reports via email or webhook.

2. Example script for continuous monitoring (save as `monitor.py` and run with `python monitor.py`):
""")

st.code("""
import time
import smtplib  # For email alerts, configure accordingly
from email.mime.text import MIMEText

# Assume scan_url and get_grok_response defined as above

def monitor_url(url, interval_hours=24):
    while True:
        findings = scan_url(url)
        # Generate report
        report = '\\n'.join(findings)
        # Add remediation and intel as needed
        # Send email or log
        print(report)  # Replace with email/send to API
        time.sleep(interval_hours * 3600)

if __name__ == '__main__':
    monitor_url('example.com')
""", language="python")

st.markdown("""
3. For API integrations, consider wrapping the scan in a **FastAPI** endpoint for external calls, but that's beyond this basic Streamlit app. You can deploy this app on Streamlit Community Cloud and use webhooks for alerts.
""")

st.write("This setup builds on open-source tools like Nmap and leverages Grok for up-to-date intelligence, ideal for small teams.")
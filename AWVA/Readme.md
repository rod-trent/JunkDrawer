# Introducing the Automated Web Vulnerability Auditor (AWVA): A Simple Tool for Basic Web Security Scanning

Hey everyone! If you're into cybersecurity, web development, or just keeping your online presence secure, I've got something cool to share. Today, I'm excited to talk about a little project called the **Automated Web Vulnerability Auditor (AWVA)**. It's a straightforward Python-based app built with Streamlit that performs basic passive scans on websites to identify common security issues. But it doesn't stop there—it integrates with the xAI Grok API to provide remediation steps and up-to-date threat intelligence. Think of it as a quick-and-dirty auditor for spotting potential vulnerabilities without getting too invasive.

This app lives in my GitHub repo's "JunkDrawer" folder (because, let's be honest, that's where all the fun experiments end up). You can check it out, fork it, or contribute here: [https://github.com/rod-trent/JunkDrawer/tree/main/AWVA](https://github.com/rod-trent/JunkDrawer/tree/main/AWVA). (Note: The link you might see floating around is for editing, but head to the tree view for the full files.)

Let's dive into what this app is all about, why it's useful, and how you can get it running on your own machine.

## What Is AWVA?

AWVA is a web-based tool (powered by Streamlit) designed to audit websites for basic security flaws. It's not a full-fledged penetration testing suite like Burp Suite or Metasploit—it's more of a passive scanner that checks for things you can detect without actively probing or exploiting the site. This makes it legal and ethical to use on sites you own or have permission to scan, as it avoids actions like injecting payloads that could be seen as attacks.

The core of the app uses:
- **Nmap** for port scanning (checking open ports in the 1-1024 range).
- **Requests and SSL libraries** for inspecting HTTPS support, security headers, and TLS versions.
- **xAI Grok API** (via their chat completions endpoint) to generate concise remediation advice and current threat intelligence based on the findings.

There's also a section on extending it for continuous monitoring, like scheduling scans and sending alerts.

Important disclaimer right from the app: This is **basic and passive**. It won't test for things like SQL injection (SQLi) or cross-site scripting (XSS) by injecting code—that requires tools like OWASP ZAP or sqlmap, and explicit permission. It's meant for initial checks, like seeing if your site has open ports that could expose databases or missing headers that invite XSS risks.

## What Does It Do?

Here's a breakdown of the app's functionality:

1. **User Input**: You enter a website URL (e.g., "example.com") into a simple text box.

2. **Passive Scanning**:
   - **Port Scanning**: Uses Nmap to scan for open ports (1-1024) and reports services/versions. Open ports might indicate risks, like an exposed MySQL port (3306) that could lead to SQLi if not firewalled.
   - **HTTPS Check**: Verifies if the site supports HTTPS. If not, it flags weak encryption risks.
   - **Security Headers Inspection**: Looks for missing headers like Content-Security-Policy (CSP), X-Frame-Options, X-XSS-Protection, and Strict-Transport-Security (HSTS). These help prevent XSS, clickjacking, and more.
   - **TLS Version Check**: Ensures the site isn't using outdated TLS versions (e.g., 1.0 or 1.1), which are vulnerable to attacks like POODLE.

3. **Findings Report**: Displays results in a clean Streamlit interface, including any issues found.

4. **AI-Powered Insights**:
   - For each major finding (e.g., missing headers or weak TLS), it queries the Grok API for:
     - **Remediation Steps**: Concise, actionable advice from a "security expert" persona.
     - **Threat Intelligence**: Current info on related threats (e.g., recent exploits targeting weak TLS).

5. **Advanced Features**: The app includes guidance on setting up continuous monitoring, like using cron jobs or Task Scheduler to run scans periodically and send reports via email or webhooks. There's even a sample script for this.

In action, scanning a site might output something like:
- "Open ports found: Port 80: http (unknown)"
- "Missing security headers: Content-Security-Policy (helps prevent XSS)"
- Followed by Grok's response: "To add CSP, include this header in your server config: Content-Security-Policy: default-src 'self';"

## Why Is It Useful?

In a world where web vulnerabilities are rampant (think Log4Shell or the endless stream of XSS exploits), tools like AWVA are handy for:
- **Quick Audits**: Developers or small teams can scan their sites during development or after deployments to catch low-hanging fruit.
- **Education**: It's a great learning tool—see real-world issues and get AI-generated explanations/remedies.
- **Compliance and Best Practices**: Helps ensure basics like HTTPS and security headers are in place, which is crucial for GDPR, PCI-DSS, or just good hygiene.
- **Threat Awareness**: The Grok integration pulls in fresh intel, keeping you informed about evolving threats without manual research.
- **Non-Invasive**: Perfect for shared hosting or sites where you can't run aggressive scans.

For small businesses or hobbyists, it's a free way to dip your toes into security auditing without investing in enterprise tools. Plus, it's extensible—add more checks or integrate with other APIs as needed.

## Requirements

To run AWVA, you'll need:
- **Python 3.8+**: The code uses standard libraries plus some extras.
- **Dependencies** (install via pip):
  - `streamlit`: For the web interface.
  - `python-dotenv`: To load environment variables.
  - `requests`: For HTTP checks and API calls.
  - `python-nmap`: For port scanning (note: you also need the Nmap binary installed on your system).
  - `urllib3`: Comes with requests, but ensure it's up to date for SSL handling.
- **Nmap**: Download and install from [nmap.org](https://nmap.org). It's essential for the port scan.
- **xAI API Key**: Sign up at xAI (api.x.ai) and get a free/paid key. Store it in a `.env` file as `XAI_API_KEY=your_key_here`.
- **Operating System**: Works on Linux, Mac, or Windows (with Nmap installed).

No fancy hardware needed—just a machine with internet access for the API calls.

## How to Implement and Customize

The code is in a single file: `awva.py`. Here's how to get started:

1. **Clone the Repo**:
   ```
   git clone https://github.com/rod-trent/JunkDrawer.git
   cd JunkDrawer/AWVA
   ```

2. **Install Dependencies**:
   ```
   pip install streamlit python-dotenv requests python-nmap
   ```
   (Install Nmap separately via your package manager, e.g., `sudo apt install nmap` on Ubuntu.)

3. **Set Up .env**:
   Create a `.env` file in the directory:
   ```
   XAI_API_KEY=your_api_key_here
   ```

4. **Customize**:
   - Add more scans: Extend `scan_url()` with checks for cookies (e.g., Secure flag) or WHOIS lookups.
   - Enhance AI Prompts: Tweak the system prompt in `get_grok_response()` for more detailed responses.
   - Integrate Alerts: In the monitoring script, replace `print(report)` with SMTP code for emails.
   - Deploy: Use Streamlit Community Cloud for hosting—upload to GitHub and deploy with one click.

For the advanced monitoring:
- Save the sample `monitor.py` script.
- Customize the `monitor_url()` function with your URL and interval.
- Run it in the background (e.g., with `nohup python monitor.py &`).

If you want to turn it into an API, wrap it in FastAPI for external triggering.

## How to Run It

1. **Local Run**:
   ```
   streamlit run awva.py
   ```
   This launches a local web server (usually at http://localhost:8501). Enter a URL and hit "Scan."

2. **Testing**:
   - Try a safe site like "httpbin.org" or your own domain.
   - If Nmap errors out, check permissions (it might need sudo for some scans, but the code uses non-privileged args).

3. **Continuous Mode**:
   Run the monitoring script:
   ```
   python monitor.py
   ```
   It'll scan every 24 hours (configurable) and output reports.

## Final Thoughts

AWVA is a fun, practical project that bridges basic scanning with AI-driven insights. It's not meant to replace professional pentests, but it's a solid starting point for staying secure. If you try it out, let me know what you think—issues, PRs, or suggestions are welcome on GitHub!

Stay safe out there, and happy auditing! 🚀

*Posted on January 6, 2026*

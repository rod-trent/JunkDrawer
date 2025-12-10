#!/usr/bin/env python3
"""
Microsoft Patch Tuesday AI Agent – ULTIMATE FINAL VERSION
→ Always latest (Dec 2025 etc.)
→ Full CVE description (in YAML + AI email)
→ Direct Microsoft CVE URL (clickable)
→ MITRE ATT&CK + inference + URLs
→ Grok AI executive summary + beautiful HTML email
"""

import os
import re
import time
import schedule
import requests
import yaml
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()

# === CONFIG FROM .env ===
GROK_API_KEY = os.getenv("GROK_API_KEY")
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECIPIENTS = [r.strip() for r in os.getenv("EMAIL_RECIPIENT", "").split(",") if r.strip()]
RUN_TIME = os.getenv("RUN_TIME", "09:00")

if not all([GROK_API_KEY, EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECIPIENTS]):
    raise SystemExit("Missing required values in .env file!")

client = OpenAI(api_key=GROK_API_KEY, base_url="https://api.x.ai/v1")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
    "Referer": "https://msrc.microsoft.com/update-guide",
}

def safe_get_value(obj):
    if isinstance(obj, dict): return obj.get("Value", "")
    if isinstance(obj, list) and obj: return safe_get_value(obj[0])
    if isinstance(obj, str): return obj
    return ""

# === GET LATEST RELEASE ===
def get_latest_data():
    s = requests.Session()
    s.headers.update(HEADERS)
    r = s.get("https://api.msrc.microsoft.com/updates", timeout=30)
    r.raise_for_status()
    updates = r.json().get("value", [])
    latest = sorted(updates, key=lambda x: x.get("InitialReleaseDate", ""), reverse=True)[0]
    month_id = latest["ID"]
    print(f"Latest Patch Tuesday: {month_id}")
    cvrf = s.get(f"https://api.msrc.microsoft.com/cvrf/v2.0/cvrf/{month_id}", timeout=60)
    cvrf.raise_for_status()
    return cvrf.json(), month_id

# === EXTRACTORS ===
def extract_cvss(scores):
    if not scores: return None
    for s in scores:
        if s.get("Type") == 5:
            val = safe_get_value(s.get("Value") or s.get("Description", ""))
            parts = val.split()
            if parts: return parts[-1]
    return None

def extract_description(notes):
    if not notes: return "No description available."
    for n in notes:
        if n.get("Type") == 3:
            return safe_get_value(n).strip()
    for n in notes:
        txt = safe_get_value(n).strip()
        if len(txt) > 50: return txt
    return "No description available."

def extract_affected_products(remediations):
    products = set()
    for r in remediations:
        if r.get("Type") != 0: continue
        for pid in (r.get("ProductID") or []):
            if pid: products.add(str(pid).strip())
        desc = safe_get_value(r.get("Description", ""))
        quick = ["Windows 11", "Windows 10", "Windows Server 2022", "Windows Server 2019",
                 "Microsoft Edge", "Microsoft Office", ".NET", "Azure", "Exchange Server"]
        for p in quick:
            if p in desc:
                products.add(p)
                break
    return sorted(products) or ["Unknown"]

def extract_kbs(remediations):
    kbs = set()
    for r in remediations:
        if r.get("Type") != 0: continue
        desc = safe_get_value(r.get("Description", ""))
        kbs.update(re.findall(r"KB\d{7,}", desc))
    return sorted(kbs)

def infer_attack_mapping(title, desc):
    text = f"{title} {desc}".lower()
    if any(x in text for x in ["elevation of privilege", "eop"]): return ["T1068"]
    if any(x in text for x in ["remote code execution", "rce"]): return ["T1203"]
    if "denial of service" in text: return ["T1499"]
    if "information disclosure" in text: return ["T1005"]
    if "spoofing" in text: return ["T1566"]
    return None

def extract_mitre(acks, title, desc):
    found = set()
    for a in (acks or []):
        text = safe_get_value(a)
        found.update(re.findall(r"T\d{4}(?:\.\d{3,4})?", text))
    if found: return sorted(found)
    inferred = infer_attack_mapping(title, desc)
    return inferred or "Not mapped"

# === PARSER – DESCRIPTION INCLUDED & PROMINENT ===
def parse_vulnerabilities(cvrf):
    vulns = []
    for v in cvrf.get("Vulnerability", []):
        cve = v.get("CVE", "N/A")
        title = safe_get_value(v.get("Title", "No title"))
        description = extract_description(v.get("Notes", []))  # Always full description

        severity = exploit_status = "Unknown"
        for t in v.get("Threats", []):
            if t.get("Type") == 0: severity = safe_get_value(t.get("Description", ""))
            if t.get("Type") == 3: exploit_status = safe_get_value(t.get("Description", ""))

        mitre = extract_mitre(v.get("Acknowledgements", []), title, description)

        vulns.append({
            "cve": cve,
            "title": title,
            "description": description,  # Full CVE description
            "severity": severity,
            "exploit_status": exploit_status,
            "cvss_base_score": extract_cvss(v.get("Scores", [])),
            "affected_products": extract_affected_products(v.get("Remediations", [])),
            "kb_articles": extract_kbs(v.get("Remediations", [])),
            "mitre_attack": mitre,
            "microsoft_cve_url": f"https://msrc.microsoft.com/update-guide/vulnerability/{cve}",
            "nvd_url": f"https://nvd.nist.gov/vuln/detail/{cve}",
            "cve_mitre_url": f"https://cve.mitre.org/cgi-bin/cvename.cgi?name={cve}",
            "mitre_attack_urls": [
                f"https://attack.mitre.org/techniques/{t}/" for t in mitre
            ] if isinstance(mitre, list) else [],
        })
    return vulns

# === AI SUMMARY – NOW USES FULL DESCRIPTION ===
def generate_ai_summary(yaml_path: Path) -> str:
    data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    top_vulns = [v for v in data["vulnerabilities"] if v["severity"] == "Critical" or "Exploitation" in v["exploit_status"]][:10]

    prompt = f"""
You are a senior security analyst. Write a concise executive summary for Microsoft Patch Tuesday {data['release_month']} ({data['total_cves']} CVEs).

For each top CVE include:
• CVE + Title
• Description (full sentence from Microsoft)
• CVSS score
• Microsoft CVE URL
• MITRE ATT&CK (if any)
• Why it matters + recommended action

End with prioritized patching list.
Professional tone. Max 650 words.
"""

    response = client.chat.completions.create(
        model="grok-4-1-fast-reasoning",
        messages=[{"role": "user", "content": prompt + "\n\nData:\n" + yaml.dump(top_vulns)}],
        max_tokens=1400,
        temperature=0.5,
    )
    return response.choices[0].message.content.strip()

# === EMAIL – DESCRIPTION FRONT AND CENTER ===
def send_email(summary: str, month: str):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_SENDER
    msg["To"] = ", ".join(EMAIL_RECIPIENTS)
    msg["Subject"] = f"Patch Tuesday AI Report – {month} (with CVE Descriptions)"

    html = f"""
    <html>
    <body style="font-family:Segoe UI,Arial,sans-serif;line-height:1.6;color:#333;">
    <h2 style="color:#0078d4;">Microsoft Patch Tuesday – {month}</h2>
    <div style="background:#f8f8f8;padding:20px;border-left:6px solid #0078d4;border-radius:4px;">
    <pre style="white-space:pre-wrap;font-size:14px;margin:0;">{summary}</pre>
    </div>
    <br>
    <p><strong>Full dataset saved:</strong><br>
       <code>{Path.cwd() / f"microsoft-patches-{month.lower()}.yaml"}</code></p>
    <hr>
    <small>AI Security Agent • {datetime.utcnow():%Y-%m-%d %H:%M UTC}</small>
    </body>
    </html>
    """
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
    print("Email sent with full CVE descriptions!")

# === DAILY TASK ===
def daily_task():
    print(f"\n[{datetime.utcnow().isoformat()}Z] Starting Patch Tuesday AI Agent...")
    try:
        cvrf_data, month = get_latest_data()
        vulns = parse_vulnerabilities(cvrf_data)

        yaml_file = Path(f"microsoft-patches-{month.lower()}.yaml")
        yaml_file.write_text(yaml.safe_dump({
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "release_month": month,
            "total_cves": len(vulns),
            "vulnerabilities": vulns
        }, sort_keys=False, indent=2, allow_unicode=True), encoding="utf-8")

        print(f"SUCCESS → {yaml_file.name} ({len(vulns)} CVEs with full descriptions)")

        summary = generate_ai_summary(yaml_file)
        send_email(summary, month)

    except Exception as e:
        print(f"Agent failed: {e}")
        import traceback; traceback.print_exc()

# === SCHEDULER ===
schedule.every().day.at(RUN_TIME).do(daily_task)

if __name__ == "__main__":
    print(f"Patch Tuesday AI Agent ready – next run at {RUN_TIME} UTC")
    daily_task()  # Run immediately
    while True:
        schedule.run_pending()
        time.sleep(60)
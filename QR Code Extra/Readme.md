# QR Code Generator with Logo

A simple, modern **Streamlit** web app that lets you create QR codes — with optional centered logo overlay, customizable colors, error correction, and module size.

![App screenshot](https://github.com/rod-trent/JunkDrawer/blob/main/QR%20Code%20Extra/qrcodegen.jpg)  


## Features

- Generate QR codes from any text or URL
- Optional logo overlay (PNG with transparency works best)
- Choose error correction level (Low → High – important when adding logo)
- Customize module size, quiet zone (border), foreground & background colors
- Instant preview
- Download as PNG
- Clean, mobile-friendly interface

## How to Run Locally

```bash
# 1. Clone or download the repository
git clone https://github.com/yourusername/qr-code-generator-streamlit.git
cd qr-code-generator-streamlit
(or just download BuildQRCode.py to a directory on your computer)

# 2. (Recommended) Create virtual environment
python -m venv venv
source venv/bin/activate    # Linux / macOS
venv\Scripts\activate       # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run BuildQRCode.py


# QR Code Generator with Logo

A simple, modern **Streamlit** web app that lets you create QR codes — with optional centered logo overlay, customizable colors, error correction, and module size.

![App screenshot](https://via.placeholder.com/800x500/2d3748/ffffff?text=QR+Code+Generator+Screenshot)  
*(replace with real screenshot when you deploy)*

## Features

- Generate QR codes from any text or URL
- Optional logo overlay (PNG with transparency works best)
- Choose error correction level (Low → High – important when adding logo)
- Customize module size, quiet zone (border), foreground & background colors
- Instant preview
- Download as PNG
- Clean, mobile-friendly interface

## Demo

Live app:  
→ [https://your-app-name.streamlit.app](https://your-app-name.streamlit.app)  
*(update link once deployed)*

## Screenshots

<p align="center">
  <img src="https://via.placeholder.com/600x400/4a5568/ffffff?text=With+Logo+Example" alt="QR with logo" width="45%"/>
  <img src="https://via.placeholder.com/600x400/4a5568/ffffff?text=Plain+Color+Custom+QR" alt="Custom colors" width="45%"/>
</p>

## How to Run Locally

```bash
# 1. Clone or download the repository
git clone https://github.com/yourusername/qr-code-generator-streamlit.git
cd qr-code-generator-streamlit

# 2. (Recommended) Create virtual environment
python -m venv venv
source venv/bin/activate    # Linux / macOS
venv\Scripts\activate       # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run BuildQRCode.py
# or
streamlit run qr_code_generator_with_logo_fixed.py

# Deepfake Detection Tool

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io/)

A simple, powerful web application that uses **xAI's Grok Vision** (via the xAI API) to detect potential deepfake manipulation in images and videos.

Upload an image or video, or paste a direct URL, and get an AI-assisted analysis with a confidence score, verdict, and detailed reasoning.

## Features

- Supports **images** (JPG, PNG, WEBP) and **videos** (MP4, MOV, AVI)
- Input via file upload **or** direct media URL
- Extracts key frames from videos for temporal consistency checks
- Structured output:
  - Confidence Score (0–100)
  - Verdict: Real | Likely Real | Uncertain | Likely Deepfake | Deepfake
  - Detailed bullet-point reasoning
- User-friendly Streamlit interface
- Caches analysis results for faster repeated checks
- Built with privacy in mind – media is processed locally before being sent to the API

> **Important**: This tool provides AI-assisted detection and is **not 100% accurate**. Deepfake technology evolves rapidly. Always cross-verify with multiple sources and professional tools when needed.

## Screenshots

<img width="3024" height="1770" alt="image" src="https://github.com/user-attachments/assets/c94d77a0-4732-40ee-b1db-5063fd51c0a3" />


## Requirements

- Python 3.8 or higher
- An **xAI API key** (sign up at [x.ai](https://x.ai))
- Internet connection (for API calls)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/rod-trent/JunkDrawer.git
cd JunkDrawer/Deepfake\ Detection\ Tool
```

2. (Recommended) Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate    # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install streamlit python-dotenv openai pillow requests moviepy
```

4. Create a `.env` file in the project root:

```env
XAI_API_KEY=your_xai_api_key_here
```

Replace `your_xai_api_key_here` with your actual xAI API key.

## Usage

Run the app locally:

```bash
streamlit run DFDT.py
```

Open your browser and go to `http://localhost:8501`.

### Tips for Best Results

- Use high-quality, well-lit media
- Videos generally provide better detection accuracy than single images
- Focus on media containing clear faces
- Keep videos reasonably short (under a few minutes) for faster processing

## Technical Details

- **Model**: `grok-4` (vision-capable model as of January 2026).  
  If you encounter "model not found" errors, check available models in the xAI Console and update the `MODEL` variable in `DFDT.py` (common alternatives: `grok-4-fast-reasoning`).
- **Video Processing**: Uses MoviePy (v2+) to extract up to 10 evenly spaced key frames.
- **API**: OpenAI-compatible client pointed at `https://api.x.ai/v1`.

## Limitations

- No audio analysis (visual only)
- Performance depends on video length and hardware
- Detection accuracy varies with deepfake sophistication
- API usage incurs costs based on your xAI plan

## Contributing

Contributions, issues, and feature requests are welcome! Feel free to fork the repo and submit pull requests.

## License

This project is open source and available under the [MIT License](LICENSE).

## Author

Rod Trent  
GitHub: [@rod-trent](https://github.com/rod-trent)

---

Stay vigilant in the age of generative AI! 🚀

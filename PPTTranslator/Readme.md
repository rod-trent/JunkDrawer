# PowerPoint Translator 🌐

A Streamlit-based web application that translates PowerPoint presentations using xAI's Grok API. Upload a .pptx file, select your target language, and download the translated version with all formatting preserved.

## Features

- 🌍 **Multi-language Support**: Translate between multiple languages including English, Spanish, French, German, Italian, Portuguese, Chinese, Japanese, Korean, Russian, and Arabic
- 📊 **Comprehensive Translation**: Translates text in slides, shapes, and tables
- 🎨 **Format Preservation**: Maintains original formatting and layout
- 🚀 **Powered by xAI**: Uses Grok API for high-quality translations
- 📥 **Easy Download**: Get your translated presentation instantly
- 🔄 **Progress Tracking**: Visual progress bar during translation

## Prerequisites

- Python 3.8 or higher
- xAI API key ([Get one here](https://console.x.ai/))

## Installation

1. **Clone or download this repository**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your xAI API key**:
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` and add your xAI API key:
     ```
     XAI_API_KEY=your_actual_api_key_here
     ```

## Usage

1. **Start the application**:
   ```bash
   streamlit run app.py
   ```

2. **Open your browser**: The app will automatically open at `http://localhost:8501`

3. **Translate your presentation**:
   - Upload your PowerPoint file (.pptx)
   - Select source language (or use auto-detect)
   - Select target language
   - Click "Translate Presentation"
   - Download the translated file

## How It Works

The application:
1. Loads your PowerPoint presentation
2. Iterates through all slides, shapes, and tables
3. Extracts text content
4. Sends text to xAI's Grok API for translation
5. Replaces original text with translations
6. Preserves all formatting, layouts, and styles
7. Generates a downloadable translated presentation

## Supported Content

✅ **Translated**:
- Text in slides
- Text in shapes and text boxes
- Text in tables
- Multiple slides

❌ **Not Translated**:
- Images with embedded text
- Charts and diagrams
- Speaker notes (can be added if needed)

## Customization

### Adding More Languages

Edit the language lists in `app.py`:
```python
source_language = st.selectbox(
    "Source Language",
    ["auto-detect", "English", "YourLanguage", ...]
)
```

### Changing the AI Model

Modify the model parameter in the `translate_text` function:
```python
response = client.chat.completions.create(
    model="grok-3",  # Change to another xAI model
    ...
)
```

### Adjusting Translation Quality

Modify the `temperature` parameter (0.0-1.0):
- Lower values (0.1-0.3): More consistent, literal translations
- Higher values (0.5-0.8): More creative, natural translations

## Project Structure

```
pptx-translator/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variable template
├── .env                  # Your API key (create this)
└── README.md             # This file
```

## Troubleshooting

### "XAI_API_KEY not found in .env file"
- Ensure you've created a `.env` file (not `.env.example`)
- Verify your API key is correctly formatted
- Restart the Streamlit app after updating `.env`

### Translation errors
- Check your xAI API key is valid
- Ensure you have sufficient API credits
- Verify your internet connection

### File upload issues
- Only .pptx files are supported (not .ppt)
- Check file isn't corrupted
- Ensure file size is reasonable

## API Costs

Translation costs depend on:
- Number of slides
- Amount of text per slide
- xAI API pricing

Monitor your usage at [xAI Console](https://console.x.ai/)

## Future Enhancements

Potential features to add:
- [ ] Batch processing multiple files
- [ ] Translation of speaker notes
- [ ] Custom terminology glossaries
- [ ] Translation memory to avoid re-translating
- [ ] Support for .ppt files
- [ ] Image text OCR and translation

## License

This project is open source and available for personal and commercial use.

## Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

## Credits

Built with:
- [Streamlit](https://streamlit.io/) - Web framework
- [python-pptx](https://python-pptx.readthedocs.io/) - PowerPoint manipulation
- [xAI Grok](https://x.ai/) - AI translation engine

---

**Note**: This tool requires an active xAI API key. Translation quality and speed depend on the xAI service.

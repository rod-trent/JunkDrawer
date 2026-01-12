# qr_code_generator_with_logo_fixed.py
import streamlit as st
import qrcode
from io import BytesIO
from PIL import Image

st.set_page_config(page_title="QR Code Generator + Logo", page_icon="🖼️", layout="centered")

st.title("QR Code Generator with Optional Logo")
st.write("Enter text/URL and optionally upload a square logo (PNG with transparency works best)")

# Input
url = st.text_input(
    "Text or URL to encode",
    placeholder="https://example.com",
    value="https://",
    help="URLs, plain text, Wi-Fi strings, vCards, etc."
)

# Logo upload
uploaded_file = st.file_uploader(
    "Upload logo (PNG/JPG, square recommended, transparent PNG ideal)",
    type=["png", "jpg", "jpeg"]
)

# Customization
with st.expander("Customize (optional)"):
    col1, col2 = st.columns(2)
    with col1:
        box_size = st.slider("Module size (pixels)", 5, 20, 10)
    with col2:
        border = st.slider("Quiet zone (border modules)", 2, 8, 4)

    error_level = st.selectbox(
        "Error correction",
        ["Low (7%)", "Medium (15%)", "Quartile (25%)", "High (30%)"],
        index=3 if uploaded_file else 1
    )

    error_map = {
        "Low (7%)": qrcode.constants.ERROR_CORRECT_L,
        "Medium (15%)": qrcode.constants.ERROR_CORRECT_M,
        "Quartile (25%)": qrcode.constants.ERROR_CORRECT_Q,
        "High (30%)": qrcode.constants.ERROR_CORRECT_H,
    }
    error_correction = error_map[error_level]

    col3, col4 = st.columns(2)
    with col3:
        fill_color = st.color_picker("QR color", "#000000")
    with col4:
        back_color = st.color_picker("Background", "#FFFFFF")

# Generate
if st.button("Generate QR Code", type="primary", use_container_width=True):
    if not url.strip():
        st.error("Please enter text or a URL.")
    else:
        with st.spinner("Generating..."):
            try:
                qr = qrcode.QRCode(
                    version=None,
                    error_correction=error_correction,
                    box_size=box_size,
                    border=border,
                )
                qr.add_data(url.strip())
                qr.make(fit=True)

                # Base QR image (always RGBA for logo compositing)
                qr_img = qr.make_image(
                    fill_color=fill_color,
                    back_color=back_color
                ).convert("RGBA")

                # Logo handling
                if uploaded_file is not None:
                    try:
                        logo = Image.open(uploaded_file).convert("RGBA")
                        qr_w, qr_h = qr_img.size

                        # Logo size: ~25–30% of QR width (common sweet spot)
                        logo_size = int(qr_w * 0.25)
                        logo = logo.resize((logo_size, logo_size), Image.LANCZOS)

                        # Center
                        pos = ((qr_w - logo_size) // 2, (qr_h - logo_size) // 2)

                        # Paste with transparency mask
                        qr_img.paste(logo, pos, logo)

                    except Exception as e:
                        st.warning(f"Logo processing failed ({e}) — showing QR without logo.")

                # Convert back to RGB for display/save
                final_img = qr_img.convert("RGB")

                # Show
                st.image(final_img, caption="Your QR Code", use_container_width=True)

                # Download prep
                buf = BytesIO()
                final_img.save(buf, format="PNG")
                byte_data = buf.getvalue()

                st.download_button(
                    label="⬇️ Download PNG",
                    data=byte_data,
                    file_name="qrcode.png",
                    mime="image/png",
                    use_container_width=True
                )

            except Exception as e:
                st.error(f"Generation failed: {str(e)}")

st.markdown("---")
st.caption("Streamlit • python-qrcode • Pillow | High error correction recommended with logo")
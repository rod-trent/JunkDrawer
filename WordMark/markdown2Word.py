import streamlit as st
import markdown
from htmldocx import HtmlToDocx
import io
import mammoth

st.set_page_config(page_title="Markdown ↔ Word Converter", layout="wide")
st.title("Bidirectional Markdown ↔ Microsoft Word Converter")

st.markdown("""
This app allows you to:
- Convert **Markdown** to a downloadable **Word (.docx)** file
- Convert an uploaded **Word (.docx)** file to **Markdown** (with clean direct conversion!)
- Preview the rendered content in real-time
""")

# Markdown extensions
md_extensions = ['extra', 'tables', 'fenced_code', 'codehilite']

tab1, tab2 = st.tabs(["Markdown → Word", "Word → Markdown"])

# ==================== Markdown to Word ====================
with tab1:
    st.header("Markdown to Word")
    
    md_text = st.text_area("Paste your Markdown here", height=400, key="md_input")
    
    file_name = st.text_input("Output Word file name", value="converted.docx", key="docx_filename")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Live Preview (Rendered Markdown)")
        if md_text.strip():
            preview_html = markdown.markdown(md_text, extensions=md_extensions)
            st.markdown(preview_html, unsafe_allow_html=True)
        else:
            st.info("Enter Markdown text to see the preview.")
    
    with col2:
        st.subheader("Convert & Download")
        if st.button("Convert to Word", key="convert_md_to_docx"):
            if not md_text.strip():
                st.warning("Please enter some Markdown text.")
            else:
                with st.spinner("Converting..."):
                    try:
                        html = markdown.markdown(md_text, extensions=md_extensions)
                        parser = HtmlToDocx()
                        doc = parser.parse_html_string(html)
                        
                        buffer = io.BytesIO()
                        doc.save(buffer)
                        buffer.seek(0)
                        
                        download_name = file_name if file_name.endswith('.docx') else file_name + '.docx'
                        
                        st.download_button(
                            label="Download Word File (.docx)",
                            data=buffer,
                            file_name=download_name,
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                        st.success("Conversion complete! Download using the button above.")
                    except Exception as e:
                        st.error(f"Error during conversion: {str(e)}")

# ==================== Word to Markdown ====================
with tab2:
    st.header("Word to Markdown")
    
    uploaded_file = st.file_uploader("Upload a .docx file", type=["docx"], key="docx_upload")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Converted Markdown")
    
    with col2:
        st.subheader("Rendered Preview")
    
    if uploaded_file:
        docx_bytes = uploaded_file.getvalue()
        
        # Enhanced validation and helpful error messages
        if len(docx_bytes) == 0:
            st.error("The uploaded file is empty.")
        elif not docx_bytes.startswith(b'PK\x03\x04'):
            st.error("Invalid .docx file: It does not appear to be a valid ZIP archive.")
            st.markdown("""
**Common causes:**
- The file has a **Confidential** or **Highly Confidential** sensitivity label applied (these often encrypt the file, preventing tools like this app from reading it).
- The file is an old .doc format (not modern .docx).
- The file is corrupted or incomplete.
- It was saved incorrectly (e.g., as "Strict Open XML Document" or with protection).

**Solution:** Open the document in Microsoft Word → **File > Info > Protect Document > Manage Sensitivity** → Change the label to **Public**, **General**, or **Non-Business** (no encryption). Then **Save As** a new .docx file and upload that version.
            """)
            st.info("Test with a simple new document created in Word with no sensitivity label to confirm the app works.")
        else:
            try:
                with st.spinner("Converting DOCX directly to Markdown..."):
                    # Use mammoth's excellent built-in Markdown conversion
                    result = mammoth.convert_to_markdown(io.BytesIO(docx_bytes))
                    converted_md = result.value
                    
                    # Separate call for clean HTML preview
                    html_result = mammoth.convert_to_html(io.BytesIO(docx_bytes))
                    html_for_preview = html_result.value
                
                with col1:
                    st.text_area(
                        "Markdown output (copy this)",
                        value=converted_md,
                        height=400,
                        key="md_output"
                    )
                    
                    # Download Markdown file
                    md_buffer = io.BytesIO(converted_md.encode('utf-8'))
                    md_filename = uploaded_file.name.rsplit('.', 1)[0] + '.md'
                    st.download_button(
                        label="Download Markdown File (.md)",
                        data=md_buffer,
                        file_name=md_filename,
                        mime="text/markdown"
                    )
                
                with col2:
                    st.markdown(html_for_preview, unsafe_allow_html=True)
                
                # Show any warnings from mammoth
                all_messages = result.messages + html_result.messages
                if all_messages:
                    st.warning("Conversion notes/warnings:\n" + "\n".join(all_messages))
                    
            except Exception as e:
                st.error(f"Error during conversion: {str(e)}")
                st.info("If the file opens normally in Word, the issue is likely a sensitivity label with encryption. Change it to a non-encrypting label (Public/General/Non-Business) and re-save.")
    else:
        with col1:
            st.info("Upload a .docx file to convert.")
        with col2:
            st.info("Preview will appear here after conversion.")
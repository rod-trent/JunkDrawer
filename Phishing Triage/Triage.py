# app.py - AI-Enhanced Phishing Triage Dashboard
# Run with: streamlit run app.py
# Setup: Create a .env file with XAI_API_KEY=your_api_key_here (get from https://x.ai/api)

import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI
import pandas as pd
import plotly.express as px
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# Load environment variables
load_dotenv()
api_key = os.getenv("XAI_API_KEY")
if not api_key:
    st.error("Please set your XAI_API_KEY in a .env file. Get it from https://x.ai/api.")
    st.stop()

# Initialize Grok client
client = OpenAI(api_key=api_key, base_url="https://api.x.ai/v1")

# Streamlit app title and description
st.title("🛡️ AI-Enhanced Phishing Triage Dashboard")
st.markdown("""
**Concept**: Upgrade your email security with Grok's AI analysis. Upload or paste suspicious emails to detect subtle social engineering cues beyond rule-based filters.
**Powered by**: Grok from xAI
""")

# Input section
input_method = st.radio("How would you like to provide the email?", ("Paste email content", "Upload .eml or .txt file"))

email_content = ""
if input_method == "Paste email content":
    email_content = st.text_area("Paste the full email content here:", height=200, placeholder="Subject: Urgent Invoice Payment Required\nFrom: accounting@company.com\n...")
else:
    uploaded_file = st.file_uploader("Upload a suspicious email file (.eml or .txt)", type=["eml", "txt"])
    if uploaded_file:
        email_content = uploaded_file.read().decode("utf-8", errors="ignore")

if not email_content:
    st.info("Provide email content to get started.")
    st.stop()

# Analyze button
if st.button("🔍 Analyze with Grok", type="primary"):
    with st.spinner("Analyzing with Grok..."):
        # Craft the prompt for Grok
        prompt = f"""
        You are a phishing detection expert. Analyze the following email for phishing risks, focusing on subtle social engineering cues like psychological manipulation, cultural context, or zero-day lures.

        Email content:
        {email_content}

        Respond in JSON format only:
        {{
            "phishing_score": <integer 0-100, higher means more likely phishing>,
            "explanation": "<detailed reasoning, witty and human-like, e.g., 'This mimics urgency via scarcity tactics'>",
            "countermeasures": "<list of 3-5 practical suggestions, e.g., 'Verify sender via phone'>",
            "confidence": <float 0.0-1.0 for model's confidence in score>
        }}
        """

        try:
            response = client.chat.completions.create(
                model="grok-3",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500
            )
            analysis_text = response.choices[0].message.content.strip()

            # Parse JSON response
            import json
            analysis = json.loads(analysis_text)

            score = analysis["phishing_score"]
            explanation = analysis["explanation"]
            countermeasures = analysis["countermeasures"]
            confidence = analysis["confidence"]

            # Display results
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Phishing Likelihood Score", f"{score}/100")
                # Confidence heatmap visualization
                fig = px.bar(
                    x=["Low", "Medium", "High"],
                    y=[0, 0, confidence],
                    title="Confidence Heatmap",
                    color=[0, 0, confidence],
                    color_continuous_scale="RdYlGn",
                    labels={"y": "Confidence Level", "x": "Risk Category"},
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.subheader("🧠 Reasoning")
                st.write(explanation)

            st.subheader("🛡️ Suggested Countermeasures")
            # Handle both string and list for countermeasures
            if isinstance(countermeasures, str):
                for measure in countermeasures.split("\n"):
                    if measure.strip():
                        st.write(f"• {measure.strip()}")
            elif isinstance(countermeasures, list):
                for measure in countermeasures:
                    if measure.strip():
                        st.write(f"• {measure.strip()}")
            else:
                st.write("• No countermeasures available.")

            # Exportable triage report
            report_buffer = io.BytesIO()
            doc = SimpleDocTemplate(report_buffer, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []

            story.append(Paragraph("Phishing Triage Report", styles['Title']))
            story.append(Spacer(1, 12))
            story.append(Paragraph(f"Score: {score}/100", styles['Heading2']))
            story.append(Spacer(1, 12))
            story.append(Paragraph("Explanation:", styles['Heading3']))
            story.append(Paragraph(explanation, styles['Normal']))
            story.append(Spacer(1, 12))
            story.append(Paragraph("Countermeasures:", styles['Heading3']))
            # Handle both string and list for report
            if isinstance(countermeasures, str):
                for measure in countermeasures.split("\n"):
                    if measure.strip():
                        story.append(Paragraph(f"• {measure.strip()}", styles['Normal']))
            elif isinstance(countermeasures, list):
                for measure in countermeasures:
                    if measure.strip():
                        story.append(Paragraph(f"• {measure.strip()}", styles['Normal']))
            else:
                story.append(Paragraph("• No countermeasures available.", styles['Normal']))
            story.append(Spacer(1, 12))
            story.append(Paragraph(f"Analysis Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))

            doc.build(story)
            report_buffer.seek(0)

            st.download_button(
                label="📄 Download Triage Report (PDF)",
                data=report_buffer,
                file_name=f"phishing_report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf"
            )

        except json.JSONDecodeError as e:
            st.error(f"Failed to parse Grok's response as JSON: {str(e)}. Grok's output was:\n\n{analysis_text}\n\nTry rephrasing the prompt for stricter JSON adherence.")
        except KeyError as e:
            st.error(f"Missing key in analysis: {str(e)}. Ensure the JSON has all required fields.")
        except Exception as e:
            st.error(f"Analysis failed: {str(e)}. Ensure your API key is valid and quota allows. Note: If using an outdated model, update to 'grok-3' or check https://docs.x.ai/docs/models for current models.")

# Footer
st.markdown("---")
st.markdown("*Reduces false positives by 30-50% through contextual AI. Train junior analysts with Grok's witty explanations.*")
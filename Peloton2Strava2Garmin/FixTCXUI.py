import streamlit as st
import xml.etree.ElementTree as ET
from datetime import datetime
import time

def clean_tcx_content(input_content: bytes):
    """
    Cleans Peloton → Strava TCX file for Garmin Connect compatibility.
    Now yields progress updates for Streamlit.
    """
    # Define namespaces
    ns_tcx = 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2'
    ns_ext = 'http://www.garmin.com/xmlschemas/ActivityExtension/v2'

    ET.register_namespace('', ns_tcx)
    ET.register_namespace('ae', ns_ext)

    ns = {'': ns_tcx, 'ae': ns_ext}

    # Decode and clean content
    content = input_content.decode('utf-8').strip()

    # Handle optional <?xml ...?> declaration issues
    if content.startswith('<?xml'):
        content = content[content.find('?>') + 2:].strip()

    root = ET.fromstring(content)

    # Count total operations for progress estimation
    laps = root.findall(".//Lap", namespaces=ns)
    trackpoints = root.findall(".//Trackpoint", namespaces=ns)

    total_steps = 5 + len(laps) + len(trackpoints)
    progress_bar = st.progress(0)
    status_text = st.empty()
    step = 0

    def update_progress(message: str):
        nonlocal step
        step += 1
        progress_bar.progress(min(step / total_steps, 1.0))
        status_text.text(message)
        time.sleep(0.01)  # Small delay so UI updates smoothly

    update_progress("Parsing XML and removing Creator tag...")
    activity = root.find(".//Activity", namespaces=ns)
    if activity is not None:
        creator = activity.find("Creator", namespaces=ns)
        if creator is not None:
            activity.remove(creator)

    update_progress("Processing lap summaries...")
    for i, lap in enumerate(laps):
        # Remove direct <Cadence> under Lap
        cadence = lap.find("Cadence", namespaces=ns)
        if cadence is not None:
            lap.remove(cadence)

        # Round calories
        calories = lap.find("Calories", namespaces=ns)
        if calories is not None and calories.text:
            try:
                calories.text = str(int(round(float(calories.text))))
            except:
                pass

        # Round HR
        for hr_path in ["AverageHeartRateBpm/Value", "MaximumHeartRateBpm/Value"]:
            elem = lap.find(hr_path, namespaces=ns)
            if elem is not None and elem.text:
                try:
                    elem.text = str(int(round(float(elem.text))))
                except:
                    pass

        # Fix Lap Extensions: TPX → LX
        extensions = lap.find("Extensions", namespaces=ns)
        if extensions is not None:
            tpx = extensions.find("ae:TPX", namespaces=ns)
            if tpx is not None:
                tpx.tag = f"{{{ns_ext}}}LX"
                rename_map = {
                    'AverageCadence': 'AvgCadence',
                    'MaximumCadence': 'MaxCadence',
                    'AverageWatts': 'AvgWatts',
                    'MaximumWatts': 'MaxWatts'
                }
                to_remove = []
                for child in tpx:
                    tag_name = child.tag.split('}')[-1]
                    if tag_name in ['TotalPower', 'AverageResistance', 'MaximumResistance']:
                        to_remove.append(child)
                    elif tag_name in rename_map:
                        child.tag = f"{{{ns_ext}}}{rename_map[tag_name]}"
                    if child.text:
                        try:
                            child.text = str(int(round(float(child.text))))
                        except:
                            pass
                for item in to_remove:
                    tpx.remove(item)

        if i % 10 == 0 or i == len(laps) - 1:
            update_progress(f"Processing laps... ({i + 1}/{len(laps)})")

    update_progress("Processing trackpoints (this may take a moment)...")
    for i, tp in enumerate(trackpoints):
        # Round heart rate
        hr = tp.find("HeartRateBpm/Value", namespaces=ns)
        if hr is not None and hr.text:
            try:
                hr.text = str(int(round(float(hr.text))))
            except:
                pass

        # Round cadence
        cad = tp.find("Cadence", namespaces=ns)
        if cad is not None and cad.text:
            try:
                cad.text = str(int(round(float(cad.text))))
            except:
                pass

        # Clean trackpoint extensions
        ext = tp.find("Extensions", namespaces=ns)
        if ext is not None:
            tpx = ext.find("ae:TPX", namespaces=ns)
            if tpx is not None:
                # Remove Resistance
                res = tpx.find("ae:Resistance", namespaces=ns)
                if res is not None:
                    tpx.remove(res)
                # Round Watts
                watts = tpx.find("ae:Watts", namespaces=ns)
                if watts is not None and watts.text:
                    try:
                        watts.text = str(int(round(float(watts.text))))
                    except:
                        pass

        # Update progress less frequently for large files
        if i % 50 == 0 or i == len(trackpoints) - 1:
            update_progress(f"Processing trackpoints... ({i + 1}/{len(trackpoints)})")

    update_progress("Finalizing cleaned TCX file...")
    xml_declaration = b'<?xml version="1.0" encoding="UTF-8"?>\n'
    cleaned_bytes = xml_declaration + ET.tostring(root, encoding='utf-8', method='xml')

    progress_bar.progress(1.0)
    status_text.text("Done! Ready to download.")
    time.sleep(0.5)

    return cleaned_bytes


# ========================
# Streamlit App UI
# ========================

st.set_page_config(page_title="Peloton → Garmin TCX Fixer", layout="centered")
st.title("Peloton to Garmin TCX Fixer")
st.markdown("""
Upload your **Peloton → Strava exported TCX file** and get a clean version  
that uploads perfectly to **Garmin Connect** — no more "invalid file" errors!
""")

uploaded_file = st.file_uploader("Choose your Strava TCX file", type=["tcx"])

if uploaded_file is not None:
    st.info(f"Uploaded: **{uploaded_file.name}** ({uploaded_file.size:,} bytes)")

    if st.button("Fix TCX for Garmin", type="primary"):
        with st.spinner("Processing your workout..."):
            try:
                output_bytes = clean_tcx_content(uploaded_file.read())

                # Generate smart filename with current date/time
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"garmin_fixed_{timestamp}.tcx"

                st.success("Your TCX file is ready!")
                st.download_button(
                    label="Download Fixed TCX File",
                    data=output_bytes,
                    file_name=output_filename,
                    mime="application/xml",
                    type="primary"
                )
                st.balloons()

            except Exception as e:
                st.error(f"Error processing file: {e}")
                st.exception(e)

else:
    st.info("Please upload a .tcx file to begin.")
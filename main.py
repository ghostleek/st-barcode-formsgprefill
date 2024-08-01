import streamlit as st
import cv2
import numpy as np
from PIL import Image
from pyzbar.pyzbar import decode
import webbrowser

# Read base URL and prefill IDs from secrets
base_url = st.secrets.get("base_url", "https://example.com")
prefill_id = st.secrets.get("prefill_id", "prefillid1")
prefill_id2 = st.secrets.get("prefill_id2", "field2")

# Function to get query parameters
def get_query_params():
    return st.query_params

# Read query parameters
query_params = get_query_params()

# Prefill values from query parameters
field2_value = query_params.get(prefill_id2, [''])[0]

# Initialize session state
if 'barcode_value' not in st.session_state:
    st.session_state.barcode_value = None

# Title of the app
st.title("Barcode Scanner and URL Generator")

# Check if zbar shared library is available
try:
    from ctypes import cdll
    cdll.LoadLibrary('libzbar.so.0')  # For Unix-based systems
    st.write("zbar library loaded successfully.")
except OSError:
    st.error("Unable to load zbar shared library. Please ensure it is installed.")

# Active barcode scanner using the webcam
FRAME_WINDOW = st.image([])
cap = cv2.VideoCapture(0)

if cap.isOpened():
    st.write("Camera is on")
    while True:
        ret, frame = cap.read()
        if not ret:
            st.error("Failed to capture image")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        barcodes = decode(gray)

        for barcode in barcodes:
            barcode_data = barcode.data.decode('utf-8')
            st.session_state.barcode_value = barcode_data
            st.success(f"Barcode found: {barcode_data}")
            
            # Draw a bounding box around the barcode
            (x, y, w, h) = barcode.rect
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cap.release()
            break

        FRAME_WINDOW.image(frame, channels='BGR')

        if st.session_state.barcode_value:
            break

cap.release()

# Display the scanned barcode value
if st.session_state.barcode_value:
    st.write("Scanned Barcode Value: ", st.session_state.barcode_value)

# Streamlit form
with st.form("my_form"):
    field1 = st.text_input(f"Field 1 ({prefill_id})", value=st.session_state.barcode_value, disabled=True)
    field2 = st.text_input(f"Field 2 ({prefill_id2})", value=field2_value, disabled=True)
    
    submit_button = st.form_submit_button(label='Submit')

# Construct URL and redirect on submit
if submit_button and st.session_state.barcode_value and field2_value:
    constructed_url = f"{base_url}/{prefill_id}?={st.session_state.barcode_value}&{prefill_id2}?={field2_value}"
    st.write("Constructed URL:")
    st.write(constructed_url)
    webbrowser.open(constructed_url)

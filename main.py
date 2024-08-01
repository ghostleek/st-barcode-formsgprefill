import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
import numpy as np
from pyzbar.pyzbar import decode
import cv2
import webbrowser
import os

# Set the library path for macOS
if 'DYLD_LIBRARY_PATH' not in os.environ:
    os.environ['DYLD_LIBRARY_PATH'] = '/opt/homebrew/lib:/opt/homebrew/opt/zbar/lib'


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

if 'field2_value' not in st.session_state:
    st.session_state.field2_value = field2_value

# Title of the app
st.title("Barcode Scanner and URL Generator")

# Check if zbar shared library is available
try:
    from ctypes import cdll
    cdll.LoadLibrary('libzbar.so.0')  # For Unix-based systems
    st.write("zbar library loaded successfully.")
except OSError as e:
    st.error(f"Unable to load zbar shared library. Please ensure it is installed. Error: {e}")

# Define a video transformer class
class VideoTransformer(VideoTransformerBase):
    def __init__(self):
        self.barcode_detected = False

    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        barcodes = decode(gray)

        for barcode in barcodes:
            barcode_data = barcode.data.decode('utf-8')
            st.session_state.barcode_value = barcode_data
            st.success(f"Barcode found: {barcode_data}")

            # Draw a bounding box around the barcode
            (x, y, w, h) = barcode.rect
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            self.barcode_detected = True

        return img

# Initialize the webrtc streamer
webrtc_ctx = webrtc_streamer(key="example", video_transformer_factory=VideoTransformer)

# Display the scanned barcode value
if st.session_state.barcode_value:
    st.write("Scanned Barcode Value: ", st.session_state.barcode_value)

# Streamlit form
with st.form("my_form"):
    field1 = st.text_input(f"Field 1 ({prefill_id})", value=st.session_state.barcode_value, disabled=True)
    field2 = st.text_input(f"Field 2 ({prefill_id2})", value=st.session_state.field2_value, disabled=True)

    submit_button = st.form_submit_button(label='Submit')

# Construct URL and redirect on submit
if submit_button and st.session_state.barcode_value and st.session_state.field2_value:
    constructed_url = f"{base_url}/{prefill_id}?={st.session_state.barcode_value}&{prefill_id2}?={st.session_state.field2_value}"
    st.write("Constructed URL:")
    st.write(constructed_url)
    webbrowser.open(constructed_url)

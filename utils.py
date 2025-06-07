import streamlit as st
import json
import pandas as pd
import math
from PIL import Image
import io
import requests

# Function to load the image from URL with error handling
def load_image_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        return Image.open(io.BytesIO(response.content))
    except Exception as e:
        st.warning(f"Could not load image: {url}")
        return None

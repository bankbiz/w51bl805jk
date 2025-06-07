import streamlit as st
import json
import pandas as pd
import os
from PIL import Image
import io
import requests
import math

# Set page configuration
st.set_page_config(
    page_title="Pizza Image Annotations Viewer",
    page_icon="🍕",
    layout="wide",
)

# Path to the JSON file
JSON_PATH = "label-v1-2-clean.json"
IMAGE_PREFIX = "https://graffity-public-assets.s3.ap-southeast-1.amazonaws.com/ronn-temp/label_images/"
ITEMS_PER_PAGE = 100

# Function to load JSON data
@st.cache_data
def load_json_data():
    try:
        with open(JSON_PATH, 'r') as file:
            data = json.load(file)
        return data
    except Exception as e:
        st.error(f"Error loading JSON file: {e}")
        return []

# Function to extract annotation data
def extract_annotation_data(data):
    annotation_data = []
    
    for item in data:
        # Skip items that don't have the required structure
        if not isinstance(item, dict):
            continue
        
        if 'data' not in item or 'annotations' not in item:
            continue
            
        # Get image path
        image_path = None
        if 'image' in item.get('data', {}):
            image_filename = item['data']['image']
            image_path = f"{IMAGE_PREFIX}{image_filename}"
        
        # Process annotations
        annotations = item.get('annotations', [])
        
        # Default values
        image_quality = "N/A"
        pizza_quality = "N/A"
        pizza_quality_reason = "N/A"
        comments = "N/A"
        
        # If there are annotations, extract the relevant fields
        if annotations:
            for annotation in annotations:
                if 'result' in annotation:
                    for result in annotation['result']:
                        from_name = result.get('from_name', '')
                        
                        # Extract image_quality
                        if from_name == 'image_quality' and 'value' in result and 'choices' in result['value']:
                            image_quality = ", ".join(result['value']['choices'])
                        
                        # Extract pizza_quality
                        elif from_name == 'pizza_quality' and 'value' in result and 'choices' in result['value']:
                            pizza_quality = ", ".join(result['value']['choices'])
                        
                        # Extract pizza_quality_reason
                        elif from_name == 'pizza_quality_reason' and 'value' in result and 'choices' in result['value']:
                            pizza_quality_reason = ", ".join(result['value']['choices'])
                        
                        # Extract comments
                        elif from_name == 'comments' and 'value' in result and 'text' in result['value']:
                            comments = result['value']['text']
        
        # Only add items that have an image path
        if image_path:
            annotation_data.append({
                'image': image_path,
                'image_filename': image_filename if 'image_filename' in locals() else "N/A",
                'image_quality': image_quality,
                'pizza_quality': pizza_quality,
                'pizza_quality_reason': pizza_quality_reason,
                'comments': comments
            })
    
    return annotation_data

# Main function
def main():
    st.title("🍕 Pizza Image Annotations Viewer")
    
    # Load data
    with st.spinner("Loading annotation data..."):
        data = load_json_data()
    
    # Extract annotation data
    annotation_data = extract_annotation_data(data)
    
    # Display total number of images
    st.write(f"Total number of images: {len(annotation_data)}")
    
    # Pagination
    total_pages = math.ceil(len(annotation_data) / ITEMS_PER_PAGE)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        page_num = st.number_input("Page", min_value=1, max_value=total_pages, value=1, step=1)
    
    # Calculate start and end indices for the current page
    start_idx = (page_num - 1) * ITEMS_PER_PAGE
    end_idx = min(start_idx + ITEMS_PER_PAGE, len(annotation_data))
    
    # Get the data for the current page
    current_page_data = annotation_data[start_idx:end_idx]
    
    # Convert to DataFrame for display
    df = pd.DataFrame(current_page_data)
    
    # Search functionality
    search_term = st.text_input("Search by filename or annotation content:", "")
    if search_term:
        df = df[
            df['image_filename'].str.contains(search_term, case=False, na=False) | 
            df['image_quality'].str.contains(search_term, case=False, na=False) |
            df['pizza_quality'].str.contains(search_term, case=False, na=False) |
            df['pizza_quality_reason'].str.contains(search_term, case=False, na=False) |
            df['comments'].str.contains(search_term, case=False, na=False)
        ]
    
    # Display the dataframe with image thumbnails
    st.subheader(f"Showing images {start_idx + 1} to {end_idx} out of {len(annotation_data)}")
    
    # Create an expander for viewing settings
    with st.expander("View Settings", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            show_images = st.checkbox("Show Image Thumbnails", value=True)
        with col2:
            image_size = st.slider("Thumbnail Size", min_value=50, max_value=300, value=150)
    
    # Prepare the data for display
    if show_images:
        # Create a custom dataframe display with images
        for i, row in df.iterrows():
            col1, col2 = st.columns([1, 3])
            
            with col1:
                # Display image
                st.image(row['image'], width=image_size, caption=row['image_filename'])
            
            with col2:
                # Display annotations
                st.write(f"**Image Quality:** {row['image_quality']}")
                st.write(f"**Pizza Quality:** {row['pizza_quality']}")
                st.write(f"**Quality Reason:** {row['pizza_quality_reason']}")
                st.write(f"**Comments:** {row['comments']}")
            
            # Add separator
            st.markdown("---")
    else:
        # Remove the image column for table display
        table_df = df.drop(columns=['image'])
        st.table(table_df)
    
    # Pagination navigation
    st.write("")
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    
    with col1:
        if st.button("⏪ First Page"):
            st.session_state.page_num = 1
            st.rerun()
    
    with col2:
        if st.button("◀️ Previous Page") and page_num > 1:
            st.session_state.page_num = page_num - 1
            st.rerun()
    
    with col3:
        if st.button("Next Page ▶️") and page_num < total_pages:
            st.session_state.page_num = page_num + 1
            st.rerun()
    
    with col4:
        if st.button("Last Page ⏩"):
            st.session_state.page_num = total_pages
            st.rerun()
    
    # Footer
    st.write("")
    st.write("")
    st.markdown("---")
    st.caption("Pizza Image Annotations Viewer © 2025")

# Run the application
if __name__ == "__main__":
    main()

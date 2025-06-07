#!/usr/bin/env python3
import os
import json
import shutil
import re

def extract_image_names_from_json(json_file_path):
    """Extract image names from the JSON file"""
    image_names = []
    
    print(f"Opening JSON file: {json_file_path}")
    with open(json_file_path, 'r') as f:
        json_content = f.read()
    
    print(f"JSON file size: {len(json_content)} bytes")
    
    # Try to load the entire JSON
    try:
        data = json.loads(json_content)
        print(f"Successfully parsed JSON data. Found {len(data)} top-level items.")
        
        # Process the parsed JSON data
        for idx, item in enumerate(data):
            if isinstance(item, dict) and 'data' in item and 'image' in item.get('data', {}):
                image_url = item['data']['image']
                # Extract the filename from the URL by splitting on '/'
                parts = image_url.split('/')
                # Get the last part which should be the filename
                if parts:
                    # Remove query parameters (everything after '?')
                    filename = parts[-1].split('?')[0]
                    if any(ext in filename.lower() for ext in ['.jpg', '.jpeg', '.png']):
                        image_names.append(filename)
                        if len(image_names) <= 5 or len(image_names) % 100 == 0:
                            print(f"Extracted image name: {filename}")
    except (json.JSONDecodeError, TypeError) as e:
        print(f"Error parsing JSON: {e}")
        # Fall back to regex pattern matching if JSON parsing fails
        pattern = r'"image"\s*:\s*"[^"]*\/([^"\/\?]+\.(?:jpg|jpeg|png))(?:\?[^"]*)?"'
        print("Falling back to regex pattern matching...")
        image_names = re.findall(pattern, json_content)
        print(f"Found {len(image_names)} image names using regex.")
    
    return image_names

def recursive_search_and_copy(source_dir, target_dir, image_names):
    """Recursively search for images and copy them to the target directory"""
    # Create target directory if it doesn't exist
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        print(f"Created directory: {target_dir}")
    
    found_images = set()
    
    print(f"Searching for {len(image_names)} images in {source_dir}...")
    
    # Walk through all directories and files in the source directory
    for root, _, files in os.walk(source_dir):
        for file in files:
            # Check if the file is an image file
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                # Check if any of the image names from JSON is a substring of the file
                for image_name in image_names:
                    if image_name in file:
                        source_path = os.path.join(root, file)
                        target_path = os.path.join(target_dir, file)
                        
                        # Copy the file to the target directory
                        try:
                            shutil.copy2(source_path, target_path)
                            found_images.add(image_name)
                            print(f"Copied: {file}")
                        except Exception as e:
                            print(f"Error copying {file}: {e}")
                        break  # Break once we've found a match for this file
    
    # Report any images that weren't found
    not_found = set(image_names) - found_images
    if not_found:
        print(f"\nWarning: {len(not_found)} images were not found:")
        for i, image in enumerate(sorted(list(not_found))):
            if i < 20:  # Limit output to first 20 missing images
                print(f"- {image}")
            else:
                print(f"... and {len(not_found) - 20} more")
                break
    
    print(f"\nFound and copied {len(found_images)} out of {len(image_names)} images.")

def main():
    # Get the current directory of the script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Source directory to search
    source_dir = '/Volumes/Bank-1TB-SSD/Bitnpix and Ronin/sh-ronin-pizza/pre-process-images/cropped_pizzas_manual_remove_1+2'
    
    # Check if source directory exists
    if not os.path.isdir(source_dir):
        print(f"Error: Source directory does not exist: {source_dir}")
        return
    
    # Target directory - create "label_images" subfolder in the current directory
    target_dir = os.path.join(current_dir, "label_images")
    
    # JSON file path
    json_file_path = os.path.join(current_dir, "label-v1-2.json")
    
    # Check if JSON file exists
    if not os.path.isfile(json_file_path):
        print(f"Error: JSON file does not exist: {json_file_path}")
        return
    
    print(f"Reading image names from {json_file_path}...")
    
    # Extract image names from JSON file
    image_names = extract_image_names_from_json(json_file_path)
    
    if not image_names:
        print("No image names extracted from JSON data.")
        return
    
    print(f"Found {len(image_names)} image names in JSON.")
    
    # Search for images and copy them to the target directory
    recursive_search_and_copy(source_dir, target_dir, image_names)
    
    print(f"\nProcess completed. Images copied to: {target_dir}")

if __name__ == "__main__":
    main()

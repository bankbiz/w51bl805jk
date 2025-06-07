#!/usr/bin/env python3
import os
import json
import re

def clean_image_paths_in_json(json_file_path, output_file_path):
    """
    Reads a JSON file, cleans the image paths to contain only the filename,
    and writes the modified JSON to a new file.
    """
    print(f"Opening JSON file: {json_file_path}")
    with open(json_file_path, 'r') as f:
        json_content = f.read()
    
    print(f"JSON file size: {len(json_content)} bytes")
    
    # Try to load the entire JSON
    try:
        data = json.loads(json_content)
        print(f"Successfully parsed JSON data. Found {len(data)} top-level items.")
        
        # Counter for modified items
        modified_count = 0
        
        # Process the parsed JSON data
        for idx, item in enumerate(data):
            if isinstance(item, dict) and 'data' in item and 'image' in item.get('data', {}):
                image_url = item['data']['image']
                
                # Extract just the filename from the URL
                if '/' in image_url:
                    parts = image_url.split('/')
                    # Get the last part which should be the filename
                    filename = parts[-1]
                    # Remove query parameters (everything after '?')
                    if '?' in filename:
                        filename = filename.split('?')[0]
                    
                    # Update the image path to just the filename
                    item['data']['image'] = filename
                    modified_count += 1
                    
                    # Show progress
                    if modified_count <= 5 or modified_count % 100 == 0:
                        print(f"Modified image path to: {filename}")
        
        print(f"\nModified {modified_count} image paths in the JSON data.")
        
        # Write the modified JSON to a new file
        print(f"Writing modified JSON to: {output_file_path}")
        with open(output_file_path, 'w') as f:
            json.dump(data, f, indent=4)
        
        print(f"Done! Modified JSON saved to: {output_file_path}")
        
    except (json.JSONDecodeError, TypeError) as e:
        print(f"Error parsing JSON: {e}")
        # If JSON parsing fails, we can try to modify the file using regex
        print("JSON parsing failed. Attempting to modify using regex...")
        
        # This regex will find "image": "azure-blob://pizza-image/FILENAME.jpg?QUERY" patterns
        # and replace them with "image": "FILENAME.jpg"
        pattern = r'"image"\s*:\s*"[^"]*\/([^"\/\?]+\.(?:jpg|jpeg|png))(?:\?[^"]*)?"'
        replacement = r'"image": "\1"'
        
        modified_content = re.sub(pattern, replacement, json_content)
        
        # Write the modified content to the new file
        with open(output_file_path, 'w') as f:
            f.write(modified_content)
        
        print(f"Done! Modified JSON saved to: {output_file_path}")
        # We can't accurately count modifications when using regex

def main():
    # Get the current directory of the script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Input JSON file path
    json_file_path = os.path.join(current_dir, "label-v1-2.json")
    
    # Output JSON file path
    output_file_path = os.path.join(current_dir, "label-v1-2-clean.json")
    
    # Check if JSON file exists
    if not os.path.isfile(json_file_path):
        print(f"Error: JSON file does not exist: {json_file_path}")
        return
    
    print(f"Reading JSON from {json_file_path}...")
    print(f"Will write cleaned JSON to {output_file_path}")
    
    # Clean the image paths
    clean_image_paths_in_json(json_file_path, output_file_path)

if __name__ == "__main__":
    main()

import streamlit as st
import os
import requests
from typing import Optional, Dict, Any, Union
from pathlib import Path
import base64
import json
import re
from io import BytesIO
from PIL import Image

# Import from main file
from lucy_AI_mock_client import call_lucy_api, fetch_openapi_spec, API_ENDPOINT, API_KEY, AI_MODELS

# Create directory paths
FILE_EXTRACTOR_DIR = Path("examples/sources/file_extractor")

# Create directories if they don't exist
FILE_EXTRACTOR_DIR.mkdir(parents=True, exist_ok=True)

def file_extractor_page():
    """Handle file extraction processing.
    
    Allows users to:
    - Select image files from examples/sources/file_extractor/
    - Upload image files if none exist in source directory
    - Convert images to base64 for API processing
    - Extract information using selected model
    - Display extracted information as a JSON code block
    """
    st.header("File Extractor")
    
    # Use shared model and initialize cache
    model_id = st.session_state.selected_model
    if "image_cache" not in st.session_state:
        st.session_state.image_cache = {}
        
    # Discover available file extractor endpoints
    available_endpoints = {}
    openapi_spec = fetch_openapi_spec()
    
    if openapi_spec and "paths" in openapi_spec:
        for path, methods in openapi_spec["paths"].items():
            if path.startswith("/file_extractor"):
                # Extract a friendly name from the path
                endpoint_name = path.replace("/file_extractor", "").replace("/", "").replace("_", " ").title()
                if not endpoint_name:
                    endpoint_name = "Standard Extractor"
                available_endpoints[endpoint_name] = path
    
    # If no endpoints found or OpenAPI unavailable, use defaults
    if not available_endpoints:
        available_endpoints = {
            "Drivers Licence": "/file_extractor/drivers_licence",
        }
    
    # Add toggle for extraction type in a more compact layout
    extraction_type = st.radio(
        "Extraction method:",
        options=list(available_endpoints.keys()),
        horizontal=True,
        help="Different extraction methods for different document types."
    )
    
    # File selection
    image_files = (list(FILE_EXTRACTOR_DIR.glob("*.jpg")) + 
                   list(FILE_EXTRACTOR_DIR.glob("*.jpeg")) + 
                   list(FILE_EXTRACTOR_DIR.glob("*.png")) + 
                   list(FILE_EXTRACTOR_DIR.glob("*.gif")) + 
                   list(FILE_EXTRACTOR_DIR.glob("*.webp")))
    if not image_files:
        st.warning("No image files found in examples/sources/file_extractor/")
        # Allow file upload
        uploaded_file = st.file_uploader("Upload Image File", type=["jpg", "jpeg", "png", "gif", "webp"])
        if uploaded_file:
            # Create a unique key for the uploaded file
            cache_key = f"{uploaded_file.name}:{uploaded_file.size}"
            if cache_key not in st.session_state.image_cache:
                with st.spinner("Processing uploaded image..."):
                    # Read the file as bytes and convert to base64
                    img_bytes = uploaded_file.getvalue()
                    img_base64 = base64.b64encode(img_bytes).decode('utf-8')
                    st.session_state.image_cache[cache_key] = img_base64
                    
                    # Save the uploaded file to the source directory
                    with open(f"{FILE_EXTRACTOR_DIR}/{uploaded_file.name}", "wb") as f:
                        f.write(img_bytes)
            else:
                img_base64 = st.session_state.image_cache[cache_key]
            filename = uploaded_file.name
            
            # Display the uploaded image
            st.image(Image.open(BytesIO(img_bytes)), caption=filename)
    else:
        selected_file = st.selectbox(
            "Select Image File",
            options=image_files,
            format_func=lambda x: x.name
        )
        
        if selected_file:
            # Use file path as cache key
            cache_key = str(selected_file)
            if cache_key not in st.session_state.image_cache:
                with st.spinner("Loading and processing image..."):
                    with open(selected_file, "rb") as f:
                        img_bytes = f.read()
                    img_base64 = base64.b64encode(img_bytes).decode('utf-8')
                    st.session_state.image_cache[cache_key] = img_base64
            else:
                img_base64 = st.session_state.image_cache[cache_key]
            filename = selected_file.name
            
            # Display the selected image
            st.image(Image.open(selected_file), caption=filename)
    
    # Process image
    if 'img_base64' in locals() and img_base64:
        # Process image
        if st.button("Extract Information", type="primary"):
            with st.spinner("Extracting information..."):
                data = {
                    "image_base64": img_base64,
                    "model": model_id
                }
                
                # Choose endpoint based on extraction type
                endpoint = available_endpoints[extraction_type]
                
                response = call_lucy_api(endpoint, method="POST", data=data)
                
                if "content" in response:
                    # Display the raw JSON response
                    st.subheader("Extracted Information")
                    
                    # Try to parse the content as JSON if it's string JSON
                    content = response["content"]
                    try:
                        if isinstance(content, str):
                            # Try to parse as JSON
                            parsed_json = json.loads(content)
                            # Format with indentation for display
                            formatted_json = json.dumps(parsed_json, indent=2)
                            st.code(formatted_json, language="json")
                        else:
                            # Already a dict or other object, just display as JSON
                            st.code(json.dumps(content, indent=2), language="json")
                    except json.JSONDecodeError:
                        # If it's not valid JSON, display as plain text
                        st.code(content)
                    
                    # Display usage metadata if available
                    if "usage_metadata" in response:
                        st.info(f"Usage: {response['usage_metadata']}")
                else:
                    st.error(f"Failed to extract information using endpoint: {endpoint}")
import streamlit as st
import os
import requests
from typing import Optional, Dict, Any, Union
from pathlib import Path
import PyPDF2
from dotenv import load_dotenv
import re
import base64
from PIL import Image
from io import BytesIO, StringIO
import json

# Load environment variables
load_dotenv()

# Configuration
API_ENDPOINT = os.getenv('API_ENDPOINT', 'http://localhost:8000')
API_KEY = os.getenv('API_KEY', '')

# Available AI models
AI_MODELS = {
    "anthropic:claude-3-7-sonnet-latest": "Claude 3.7 Sonnet (Anthropic)",
    "anthropic:claude-3-5-haiku-latest": "Claude 3.5 Haiku (Anthropic)",
    "openai:gpt-4.1": "GPT 4.1 (OpenAI)",
    "openai:gpt-4.1-mini": "GPT 4.1 Mini (OpenAI)",
    "google_genai:gemini-2.0-flash": "Gemini 2.0 Flash (Google)",
    "google_genai:gemini-2.5-flash-preview-04-17": "Gemini 2.5 Flash Preview (Google)",
    "groq:meta-llama/llama-4-maverick-17b-128e-instruct": "Llama 4 Maverick (Groq)",
    "groq:meta-llama/llama-4-scout-17b-16e-instruct": "Llama 4 Scout (Groq)"
}

# Directory paths
TRANSCRIPTS_DIR = Path("examples/sources/transcripts")
GAME_PLANS_DIR = Path("examples/sources/game_plans")
FILE_EXTRACTOR_DIR = Path("examples/sources/file_extractor")
SUMMARY_OUTPUT_DIR = Path("examples/output/meeting_summary")
REVIEW_OUTPUT_DIR = Path("examples/output/game_plan_review")
BID_NOTES_OUTPUT_DIR = Path("examples/output/BID_notes")

# Create directories if they don't exist
for dir_path in [TRANSCRIPTS_DIR, GAME_PLANS_DIR, FILE_EXTRACTOR_DIR, SUMMARY_OUTPUT_DIR, REVIEW_OUTPUT_DIR, BID_NOTES_OUTPUT_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

def call_lucy_api(endpoint: str, method: str = "GET", data: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None, return_text: bool = False, text_data: str = None, empty_body: bool = False) -> Union[Dict[str, Any], str]:
    """Make API calls to Lucy AI server with consistent error handling.
    
    Args:
        endpoint: API endpoint path (e.g., '/status', '/template')
        method: HTTP method (GET, POST, PUT)
        data: JSON data for POST/PUT requests
        params: Query parameters for the request
        return_text: Return response as text instead of JSON
        text_data: Plain text data for PUT requests (e.g., template content)
        empty_body: If True, send empty body for POST requests
        
    Returns:
        Response data as JSON dict or text string, empty dict/string on error
    """
    
    url = f"{API_ENDPOINT}{endpoint}"
    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    
    # Change content type for text data
    if text_data is not None:
        headers["Content-Type"] = "text/plain"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=params, allow_redirects=True)
        elif method == "POST":
            if empty_body:
                response = requests.post(url, headers=headers, data='', params=params, allow_redirects=True)
            else:
                response = requests.post(url, headers=headers, json=data, params=params, allow_redirects=True)
        elif method == "PUT":
            if text_data is not None:
                response = requests.put(url, headers=headers, data=text_data, params=params, allow_redirects=True)
            else:
                response = requests.put(url, headers=headers, json=data, allow_redirects=True)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        response.raise_for_status()
        
        if return_text:
            return response.text
        else:
            return response.json()
    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP Error {e.response.status_code}: {str(e)}"
        
        # Try to get more details from response
        try:
            error_detail = e.response.json()
            if isinstance(error_detail, dict) and "detail" in error_detail:
                error_msg += f" - {error_detail['detail']}"
            else:
                error_msg += f" - {error_detail}"
        except Exception:
            if e.response.text:
                error_msg += f" - {e.response.text[:200]}"  # Limit response text length
        
        # Special handling for 404 errors on known endpoints
        if e.response.status_code == 404:
            if endpoint == "/interview/transcript_to_summary":
                new_endpoint = "/interview/initial_broker_interview/transcript_to_summary"
                st.warning(f"The API endpoint has changed. Retrying with new endpoint: {new_endpoint}")
                return call_lucy_api(new_endpoint, method, data, params, return_text, text_data, empty_body)
            elif endpoint.startswith("/game_plan_review"):
                new_endpoint = "/game_plan/review" + endpoint.replace("/game_plan_review", "")
                st.warning(f"The API endpoint has changed. Retrying with new endpoint: {new_endpoint}")
                return call_lucy_api(new_endpoint, method, data, params, return_text, text_data, empty_body)
        
        st.error(error_msg)
        return {} if not return_text else ""
    except requests.exceptions.RequestException as e:
        st.error(f"API Connection Error: {str(e)}")
        return {} if not return_text else ""
    except Exception as e:
        st.error(f"Unexpected Error: {str(e)}")
        return {} if not return_text else ""

def check_server_status() -> bool:
    """Check if Lucy AI server is available.
    
    Makes a GET request to the /status endpoint to verify server connectivity.
    
    Returns:
        True if server is accessible, False otherwise
    """
    try:
        response = call_lucy_api("/status")
        return bool(response)  # Just check if we got a response
    except Exception:
        return False

def fetch_openapi_spec() -> Optional[Dict[str, Any]]:
    """Fetch OpenAPI specification from Lucy AI server.
    
    Retrieves the OpenAPI JSON spec from /openapi.json endpoint.
    Used to discover available endpoints and their parameters.
    
    Returns:
        OpenAPI spec as dict if successful, None on error
    """
    try:
        response = requests.get(f"{API_ENDPOINT}/openapi.json")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.warning(f"Failed to fetch OpenAPI spec: {str(e)}")
        return None

def extract_pdf_text(pdf_file) -> str:
    """Extract text from uploaded PDF file.
    
    Uses PyPDF2 to extract all text content from a PDF file.
    Handles both uploaded files and file objects.
    
    Args:
        pdf_file: File object or uploaded file to extract text from
        
    Returns:
        Extracted text content, empty string on error
    """
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except PyPDF2.errors.PdfReadError as e:
        st.error(f"PDF Read Error: {str(e)}")
        return ""
    except Exception as e:
        error_msg = str(e)
        if "PyCryptodome is required" in error_msg:
            st.error("This PDF is encrypted. Please run: pip install pycryptodome")
        else:
            st.error(f"Unexpected Error reading PDF: {error_msg}")
        return ""

def welcome_page():
    """Display welcome page with feature overview.
    
    Shows an introduction to the application features and provides
    a server status check button that displays available API endpoints
    from the OpenAPI spec when clicked.
    """
    st.title("Welcome to Lucy AI Mock Client")
    st.write("""This application provides mortgage professionals with AI-powered tools to:
    
    - Process meeting transcripts into actionable summaries
    - Review mortgage game plans for compliance issues
    - Generate BID notes analysis from game plans
    
    Set your model and select a feature from the navigation menu to get started.""")
    
    # Check server status
    if st.button("Check Server Status"):
        if check_server_status():
            st.success("Lucy AI server is online and ready!")
            
            # Fetch and display OpenAPI info
            openapi_spec = fetch_openapi_spec()
            if openapi_spec:
                with st.expander("Available API Endpoints", expanded=False):
                    if "paths" in openapi_spec:
                        for path, methods in openapi_spec["paths"].items():
                            st.write(f"**{path}**")
                            for method, details in methods.items():
                                if isinstance(details, dict) and "summary" in details:
                                    st.write(f"- {method.upper()}: {details['summary']}")
                            st.write("")
        else:
            st.error("Cannot connect to Lucy AI server. Please check your configuration.")

def meeting_summary_page():
    """Handle meeting summary processing.
    
    Allows users to:
    - Select transcript files from examples/sources/transcripts/
    - View transcript content in an expandable section
    - Generate AI summaries using selected model
    - Save summaries to examples/output/meeting_summary/
    - Display usage metadata from the API response
    """
    st.header("Meeting Transcript Summary")
    
    # Use shared model from session state
    model_id = st.session_state.selected_model
    
    # File selection
    transcript_files = list(TRANSCRIPTS_DIR.glob("*.md"))
    if not transcript_files:
        st.warning("No transcript files found in {TRANSCRIPTS_DIR}.")
        uploaded_file = st.file_uploader(
            "Upload Transcript File", type=["md", "txt"], accept_multiple_files=False
        )

        if uploaded_file is not None:
            file_string = StringIO(uploaded_file.getvalue().decode("utf-8")).read()

            with open(f"{TRANSCRIPTS_DIR}/{uploaded_file.name}", "w") as file:
                file.write(file_string)
                st.rerun()
        return
    
    selected_file = st.selectbox(
        "Select Transcript File",
        options=transcript_files,
        format_func=lambda x: x.name
    )
    
    # Display transcript
    if selected_file:
        with open(selected_file, "r") as f:
            transcript_content = f.read()
        
        with st.expander("View Transcript", expanded=False):
            st.markdown(transcript_content)
    
    # Process transcript
    if st.button("Generate Summary", type="primary"):
        with st.spinner("Processing transcript..."):
            data = {
                "input_text": transcript_content,
                "model": model_id
            }
            
            response = call_lucy_api("/interview/initial_broker_interview/transcript_to_summary", method="POST", data=data)
            
            if "content" in response:
                # Display summary
                # Escape dollar signs for markdown
                escaped_content = re.sub(r'(?<!\\)\$', r'\$', response["content"])
                st.markdown(escaped_content)
                
                # Display usage metadata if available
                if "usage_metadata" in response:
                    st.info(f"Usage: {response['usage_metadata']}")
                
                # Save summary
                safe_model_id = model_id.replace('/', '-').replace(':', '-')
                output_filename = f"{selected_file.stem}_{safe_model_id}.md"
                output_path = SUMMARY_OUTPUT_DIR / output_filename
                
                with open(output_path, "w") as f:
                    f.write(response["content"])
                
                # Create repository URL for the output file - encode spaces and special characters
                url_path = f"examples/output/meeting_summary/{output_filename}"
                encoded_path = url_path.replace(" ", "%20").replace(":", "%3A").replace("/", "%2F")
                repo_url = f"https://github.com/Kevin-McIsaac/lucy_mock_client/blob/main/{encoded_path}"
                st.success(f"Summary saved to [examples/output/meeting_summary/{output_filename}]({repo_url})")
                st.markdown(f"<small>Repository URL: {repo_url}</small>", unsafe_allow_html=True)
            else:
                st.error("Failed to generate summary")

def game_plan_review_page():
    """Handle game plan review processing.
    
    Allows users to:
    - Select PDF files from examples/sources/game_plans/
    - Upload PDF files if none exist in source directory
    - Extract and cache PDF text for performance
    - Generate compliance reviews using selected model
    - Save reviews to examples/output/game_plan_review/
    - Display usage metadata from the API response
    """
  
    st.header("Game Plan Review")
    
    # Use shared model and initialize cache
    model_id = st.session_state.selected_model
    if "pdf_cache" not in st.session_state:
        st.session_state.pdf_cache = {}
        
    # Discover available game plan review endpoints
    available_endpoints = {}
    openapi_spec = fetch_openapi_spec()
    
    if openapi_spec and "paths" in openapi_spec:
        for path, methods in openapi_spec["paths"].items():
            if path.startswith("/game_plan/review"):
                # Extract a friendly name from the path
                endpoint_name = path.replace("/game_plan/review", "").replace("/", "").replace("_", " ").title()
                if not endpoint_name:
                    endpoint_name = "Standard Review"
                available_endpoints[endpoint_name] = path
    
    # If no endpoints found or OpenAPI unavailable, use defaults
    if not available_endpoints:
        available_endpoints = {
            "Standard Review": "/game_plan/review",
        }
    
    # Add toggle for review type in a more compact layout
    review_type = st.radio(
        "Review method:",
        options=list(available_endpoints.keys()),
        horizontal=True,
        help="Different review methods provide different types of analysis for your game plan."
    )
    
    # File selection
    game_plan_files = list(GAME_PLANS_DIR.glob("*.pdf"))
    if not game_plan_files:
        st.warning("No game plan files found in examples/sources/game_plans/")
        # Allow file upload
        uploaded_file = st.file_uploader("Upload PDF Game Plan", type="pdf")
        if uploaded_file:
            # Create a unique key for the uploaded file
            cache_key = f"{uploaded_file.name}:{uploaded_file.size}"
            if cache_key not in st.session_state.pdf_cache:
                with st.spinner("Extracting text from uploaded PDF..."):
                    pdf_text = extract_pdf_text(uploaded_file)
                    st.session_state.pdf_cache[cache_key] = pdf_text
            else:
                pdf_text = st.session_state.pdf_cache[cache_key]
            filename = uploaded_file.name
    else:
        selected_file = st.selectbox(
            "Select Game Plan File",
            options=game_plan_files,
            format_func=lambda x: x.name
        )
        
        if selected_file:
            # Use file path as cache key
            cache_key = str(selected_file)
            if cache_key not in st.session_state.pdf_cache:
                with st.spinner("Loading and extracting PDF..."):
                    with open(selected_file, "rb") as f:
                        pdf_text = extract_pdf_text(f)
                    st.session_state.pdf_cache[cache_key] = pdf_text
            else:
                pdf_text = st.session_state.pdf_cache[cache_key]
            filename = selected_file.name
    
    # Display extracted text
    if 'pdf_text' in locals() and pdf_text:
        with st.expander("View Extracted Text", expanded=False):
            st.text(pdf_text)
        
        # Process game plan
        if st.button("Review Game Plan", type="primary"):
            with st.spinner("Analyzing game plan..."):
                data = {
                    "input_text": pdf_text,
                    "model": model_id
                }
                
                # Choose endpoint based on review type
                endpoint = available_endpoints[review_type]
                
                # Endpoint should already be using the correct format since discovery is based on paths
                
                response = call_lucy_api(endpoint, method="POST", data=data)
                
                if "content" in response:
                    # Display review
                    # Escape dollar signs for markdown
                    escaped_content = re.sub(r'(?<!\\)\$', r'\$', response["content"])
                    st.markdown(escaped_content)
                    
                    # Display usage metadata if available
                    if "usage_metadata" in response:
                        st.info(f"Usage: {response['usage_metadata']}")
                    
                    # Save review
                    safe_model_id = model_id.replace('/', '-').replace(':', '-')
                    # Create suffix from endpoint name
                    endpoint_suffix = "_" + review_type.lower().replace(" ", "_") if review_type != "Standard Review" else ""
                    output_filename = f"{Path(filename).stem}_{safe_model_id}{endpoint_suffix}.md"
                    output_path = REVIEW_OUTPUT_DIR / output_filename
                    
                    with open(output_path, "w") as f:
                        f.write(response["content"])
                    
                    # Create repository URL for the output file - encode spaces and special characters
                    url_path = f"examples/output/game_plan_review/{output_filename}"
                    encoded_path = url_path.replace(" ", "%20").replace(":", "%3A").replace("/", "%2F")
                    repo_url = f"https://github.com/Kevin-McIsaac/lucy_mock_client/blob/main/{encoded_path}"
                    st.success(f"Review saved to [examples/output/game_plan_review/{output_filename}]({repo_url})")
                    st.markdown(f"<small>Repository URL: {repo_url}</small>", unsafe_allow_html=True)
                else:
                    st.error(f"Failed to generate review using endpoint: {endpoint}")

def bid_notes_page():
    """Handle BID notes processing.
    
    Allows users to:
    - Select PDF files from examples/sources/game_plans/
    - Upload PDF files if none exist in source directory
    - Extract and cache PDF text for performance
    - Generate BID notes using selected model
    - Save notes to examples/output/BID_notes/
    - Display usage metadata from the API response
    """
    
    st.header("BID Notes")
    
    # Use shared model and initialize cache
    model_id = st.session_state.selected_model
    if "pdf_cache" not in st.session_state:
        st.session_state.pdf_cache = {}
        
    # Discover available BID notes endpoints
    available_endpoints = {}
    openapi_spec = fetch_openapi_spec()
    
    if openapi_spec and "paths" in openapi_spec:
        for path, methods in openapi_spec["paths"].items():
            if path.startswith("/BID_notes"):
                # Extract a friendly name from the path
                endpoint_name = path.replace("/BID_notes", "").replace("/", "").replace("_", " ").title()
                if not endpoint_name:
                    endpoint_name = "Standard Notes"
                available_endpoints[endpoint_name] = path
    
    # If no endpoints found or OpenAPI unavailable, use defaults
    if not available_endpoints:
        available_endpoints = {
            "Standard Notes": "/BID_notes",
        }
    
    # Add toggle for review type in a more compact layout
    notes_type = st.radio(
        "Notes method:",
        options=list(available_endpoints.keys()),
        horizontal=True,
        help="Different methods provide different types of analysis for your BID notes."
    )
    
    # File selection
    game_plan_files = list(GAME_PLANS_DIR.glob("*.pdf"))
    if not game_plan_files:
        st.warning("No game plan files found in examples/sources/game_plans/")
        # Allow file upload
        uploaded_file = st.file_uploader("Upload PDF Game Plan", type="pdf")
        if uploaded_file:
            # Create a unique key for the uploaded file
            cache_key = f"{uploaded_file.name}:{uploaded_file.size}"
            if cache_key not in st.session_state.pdf_cache:
                with st.spinner("Extracting text from uploaded PDF..."):
                    pdf_text = extract_pdf_text(uploaded_file)
                    st.session_state.pdf_cache[cache_key] = pdf_text
            else:
                pdf_text = st.session_state.pdf_cache[cache_key]
            filename = uploaded_file.name
    else:
        selected_file = st.selectbox(
            "Select Game Plan File",
            options=game_plan_files,
            format_func=lambda x: x.name
        )
        
        if selected_file:
            # Use file path as cache key
            cache_key = str(selected_file)
            if cache_key not in st.session_state.pdf_cache:
                with st.spinner("Loading and extracting PDF..."):
                    with open(selected_file, "rb") as f:
                        pdf_text = extract_pdf_text(f)
                    st.session_state.pdf_cache[cache_key] = pdf_text
            else:
                pdf_text = st.session_state.pdf_cache[cache_key]
            filename = selected_file.name
    
    # Display extracted text
    if 'pdf_text' in locals() and pdf_text:
        with st.expander("View Extracted Text", expanded=False):
            st.text(pdf_text)
        
        # Process game plan
        if st.button("Generate BID Notes", type="primary"):
            with st.spinner("Analyzing document..."):
                data = {
                    "input_text": pdf_text,
                    "model": model_id
                }
                
                # Choose endpoint based on notes type
                endpoint = available_endpoints[notes_type]
                
                response = call_lucy_api(endpoint, method="POST", data=data)
                
                if "content" in response:
                    # Display notes
                    # Escape dollar signs for markdown
                    escaped_content = re.sub(r'(?<!\\)\$', r'\$', response["content"])
                    st.markdown(escaped_content)
                    
                    # Display usage metadata if available
                    if "usage_metadata" in response:
                        st.info(f"Usage: {response['usage_metadata']}")
                    
                    # Save notes
                    safe_model_id = model_id.replace('/', '-').replace(':', '-')
                    # Create suffix from endpoint name
                    endpoint_suffix = "_" + notes_type.lower().replace(" ", "_") if notes_type != "Standard Notes" else ""
                    output_filename = f"{Path(filename).stem}_{safe_model_id}{endpoint_suffix}.md"
                    output_path = BID_NOTES_OUTPUT_DIR / output_filename
                    
                    with open(output_path, "w") as f:
                        f.write(response["content"])
                    
                    # Create repository URL for the output file - encode spaces and special characters
                    url_path = f"examples/output/BID_notes/{output_filename}"
                    encoded_path = url_path.replace(" ", "%20").replace(":", "%3A").replace("/", "%2F")
                    repo_url = f"https://github.com/Kevin-McIsaac/lucy_mock_client/blob/main/{encoded_path}"
                    st.success(f"BID Notes saved to [examples/output/BID_notes/{output_filename}]({repo_url})")
                    st.markdown(f"<small>Repository URL: {repo_url}</small>", unsafe_allow_html=True)
                else:
                    st.error(f"Failed to generate BID Notes using endpoint: {endpoint}")

def template_management_page():
    """Handle template viewing and editing.
    
    Provides interface for managing Lucy AI templates:
    - Fetches available templates from /template/list endpoint as a list of filenames
    - Creates display names from filename stems
    - Loads template content for viewing/editing
    - Saves modified templates back to server
    - Uses session state for template caching
    """
    st.header("Template Management")
    
    # Initialize template storage in session state
    if "templates" not in st.session_state:
        st.session_state.templates = {}
    
    # Get list of templates from the API
    template_list_response = call_lucy_api("/template/list", method="GET")
    
    if template_list_response and isinstance(template_list_response, list):  # Check if we got a list response
        # Create a mapping from display names to filenames
        template_mapping = {}
        
        # Process the list of filenames
        for filename in template_list_response:
            # Create a user-friendly display name from the filename
            display_name = Path(filename).stem.replace("_", " ").title()
            template_mapping[display_name] = filename
        
        if template_mapping:  # Only proceed if we have templates
            # Select template by display name, start with no selection
            selected_display = st.selectbox(
                "Select Template",
                options=["Select a template..."] + list(template_mapping.keys())
            )
            
            # Get the actual filename for the selected template if a real template is selected
            if selected_display != "Select a template...":
                template_name = template_mapping[selected_display]
                
                # Automatically load template when selection changes
                if template_name not in st.session_state.templates:
                    params = {"file_name": template_name}
                    response = call_lucy_api("/template", params=params, return_text=True)
                    if response:
                        st.session_state.templates[template_name] = response
                    else:
                        st.error("Failed to load template")
            else:
                template_name = None
        else:
            st.warning("No templates found in the response list")
            template_name = None
    else:
        st.error("Failed to fetch template list or response is not in expected list format")
        template_name = None
    
    if template_name:
        # Display and edit template if it's in session state
        if template_name in st.session_state.templates:
            template_content = st.text_area(
                "Template Content",
                value=st.session_state.templates[template_name],
                height=300
            )
            
            # Save template
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Save Template", type="primary"):
                    params = {"file_name": template_name}
                    response = call_lucy_api("/template", method="PUT", params=params, text_data=template_content, return_text=True)
                    
                    if response is not None:  # Check for None specifically since empty string might be valid
                        st.success("Template saved successfully!")
                        st.session_state.templates[template_name] = template_content
                    else:
                        st.error("Failed to save template")
            
            with col2:
                if st.button("Pull Request", type="secondary"):
                    params = {"file_name": template_name}
                    response = call_lucy_api("/template", method="POST", params=params, empty_body=True)
                    
                    if response:
                        st.success("Pull request created successfully!")
                        # Display response details if available
                        if isinstance(response, dict):
                            if "message" in response:
                                st.info(response["message"])
                            elif "detail" in response:
                                st.info(response["detail"])
                    else:
                        st.error("Failed to create pull request")
    else:
        pass  # No template selected

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
    
    # Check if model is supported for file extraction
    supported_models = ["anthropic:claude-3-7-sonnet-latest", "anthropic:claude-3-5-sonnet-latest", 
                         "openai:gpt-4.1", "openai:gpt-4.1-mini"]
    
    if model_id not in supported_models:
        st.warning(f"File extractor only works with Claude Sonnet or GPT-4 models. Current model ({AI_MODELS[model_id]}) may not work properly.")
        supported_model_names = [AI_MODELS[m] for m in supported_models if m in AI_MODELS]
        st.info(f"Supported models: {', '.join(supported_model_names)}")
        
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
                    # Read the file as bytes
                    img_bytes = uploaded_file.getvalue()
                    
                    # Load image for display
                    img = Image.open(BytesIO(img_bytes))
                    
                    # Display image size info
                    img_byte_size = len(img_bytes)
                    st.info(f"Image size: {img_byte_size/1024:.1f} KB, dimensions: {img.width}x{img.height}")
                    
                    # Store the image in session state for persistent display
                    st.session_state.current_image = img
                    st.session_state.current_caption = uploaded_file.name
                    
                    # Convert to base64
                    img_base64 = base64.b64encode(img_bytes).decode('utf-8')
                    st.session_state.image_cache[cache_key] = img_base64
                    
                    # Save the processed file to the source directory
                    with open(f"{FILE_EXTRACTOR_DIR}/{uploaded_file.name}", "wb") as f:
                        f.write(img_bytes)
            else:
                img_base64 = st.session_state.image_cache[cache_key]
                # Still need to load and display the image even if base64 is cached
                img_bytes = uploaded_file.getvalue()
                
                # Load image for display
                img = Image.open(BytesIO(img_bytes))
                
                # Display image size info
                img_byte_size = len(img_bytes)
                st.info(f"Image size: {img_byte_size/1024:.1f} KB, dimensions: {img.width}x{img.height}")
                
                # Update the image in session state for persistent display
                st.session_state.current_image = img
                st.session_state.current_caption = uploaded_file.name
            filename = uploaded_file.name
            
            # Image will be displayed in the comparison section
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
                    
                    # Load image for display
                    img = Image.open(BytesIO(img_bytes))
                    
                    # Display image size info
                    img_byte_size = len(img_bytes)
                    st.info(f"Image size: {img_byte_size/1024:.1f} KB, dimensions: {img.width}x{img.height}")
                    
                    # Store the image in session state for persistent display
                    st.session_state.current_image = img
                    st.session_state.current_caption = selected_file.name
                    
                    # Convert to base64
                    img_base64 = base64.b64encode(img_bytes).decode('utf-8')
                    st.session_state.image_cache[cache_key] = img_base64
            else:
                img_base64 = st.session_state.image_cache[cache_key]
                # Still need to load and display the image even if base64 is cached
                with open(selected_file, "rb") as f:
                    img_bytes = f.read()
                
                # Load image for display
                img = Image.open(BytesIO(img_bytes))
                
                # Display image size info
                img_byte_size = len(img_bytes)
                st.info(f"Image size: {img_byte_size/1024:.1f} KB, dimensions: {img.width}x{img.height}")
                
                # Update the image in session state for persistent display
                st.session_state.current_image = img
                st.session_state.current_caption = selected_file.name
            filename = selected_file.name
            
            # Image will be displayed in the comparison section
    
    # Process image
    if 'img_base64' in locals() and img_base64:
        # Display the current image if it's in session state
        if 'current_image' in st.session_state and 'current_caption' in st.session_state:
            # This ensures the image stays visible after button clicks
            st.image(st.session_state.current_image, width=350, caption=st.session_state.current_caption)
        
        # Process image
        if st.button("Extract Information", type="primary"):
            # Before processing, verify the model is supported
            if model_id not in supported_models:
                # Auto-select a fallback model
                fallback_model = "anthropic:claude-3-7-sonnet-latest" if "anthropic:claude-3-7-sonnet-latest" in AI_MODELS else "openai:gpt-4.1"
                st.warning(f"Switching to {AI_MODELS[fallback_model]} for file extraction as the selected model is not supported.")
                extraction_model = fallback_model
            else:
                extraction_model = model_id
                
            with st.spinner("Extracting information..."):
                # Looking at the OpenAPI schema:
                # 1. The file_extractor endpoints expect a FileExtractorRequest object with:
                #    - image_base64: string (required)
                #    - model: string (with default)
                # This matches exactly what we're sending
                data = {
                    "image_base64": img_base64,
                    "model": extraction_model
                }
                
                # Choose endpoint based on extraction type
                endpoint = available_endpoints[extraction_type]
                
                # Make API call with base64 image data
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

def main():
    """Main application entry point.
    
    Configures Streamlit app with:
    - Wide layout and page title/icon
    - Session state initialization
    - Sidebar with global model selection
    - Multi-page navigation using st.navigation
    - Persistent model selection across pages
    """
    st.set_page_config(
        page_title="Lucy AI Mock Client",
        page_icon="🏠",
        layout="wide"
    )
    
    # Initialize session state for model selection
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = list(AI_MODELS.keys())[0]
    
    # Shared sidebar for all pages
    with st.sidebar:
        st.header("Settings")
        st.session_state.selected_model = st.selectbox(
            "Select AI Model", 
            options=list(AI_MODELS.keys()),
            format_func=lambda x: AI_MODELS[x],
            key="global_model_selector",
            index=list(AI_MODELS.keys()).index(st.session_state.selected_model)
        )
    
    # Pages configuration
    pages = [
        st.Page(welcome_page, title="Welcome", icon="🏠"),
        st.Page(meeting_summary_page, title="Meeting Summary", icon="📝"),
        st.Page(game_plan_review_page, title="Game Plan Review", icon="📋"),
        st.Page(bid_notes_page, title="BID Notes", icon="📊"),
        st.Page(file_extractor_page, title="File Extractor", icon="🖼️"),
        st.Page(template_management_page, title="Template Management", icon="⚙️")
    ]
    
    # Navigation
    nav = st.navigation(pages)
    nav.run()

if __name__ == "__main__":
    main()
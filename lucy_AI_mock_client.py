import streamlit as st
import os
import json
import requests
from typing import Optional, Dict, Any
from pathlib import Path
import PyPDF2
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Configuration
LUCY_API_URL = os.getenv('API_ENDPOINT', 'http://localhost:8000')
LUCY_API_KEY = os.getenv('API_KEY', '')

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

# No mapping needed - using full model IDs directly

# Directory paths
TRANSCRIPTS_DIR = Path("examples/sources/transcripts")
GAME_PLANS_DIR = Path("examples/sources/game_plans")
SUMMARY_OUTPUT_DIR = Path("examples/output/meeting_summary")
REVIEW_OUTPUT_DIR = Path("examples/output/game_plan_review")

# Create directories if they don't exist
for dir_path in [TRANSCRIPTS_DIR, GAME_PLANS_DIR, SUMMARY_OUTPUT_DIR, REVIEW_OUTPUT_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

def call_lucy_api(endpoint: str, method: str = "GET", data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Make API calls to Lucy AI server."""
    # Ensure endpoint has trailing slash if it's just the endpoint name
    if endpoint and not endpoint.endswith('/'):
        endpoint += '/'
    
    url = f"{LUCY_API_URL}{endpoint}"
    headers = {
        "x-api-key": LUCY_API_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, allow_redirects=True)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, allow_redirects=True)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data, allow_redirects=True)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        st.error(f"HTTP Error {e.response.status_code}: {str(e)}")
        # Try to get more details from response
        try:
            error_detail = e.response.json()
            st.error(f"Error details: {error_detail}")
        except:
            st.error(f"Response text: {e.response.text}")
        return {}
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return {}

def check_server_status() -> bool:
    """Check if Lucy AI server is available."""
    try:
        response = call_lucy_api("/status")
        return bool(response)  # Just check if we got a response
    except:
        return False

def extract_pdf_text(pdf_file) -> str:
    """Extract text from uploaded PDF file."""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return ""

def welcome_page():
    """Display welcome page with feature overview."""
    st.title("Welcome to Lucy AI Mock Client")
    st.write("""This application provides mortgage professionals with AI-powered tools to:
    
    - Process meeting transcripts into actionable summaries
    - Review mortgage game plans for compliance issues
    
    Please select a feature from the navigation menu to get started.""")
    
    # Check server status
    if st.button("Check Server Status"):
        if check_server_status():
            st.success("Lucy AI server is online and ready!")
        else:
            st.error("Cannot connect to Lucy AI server. Please check your configuration.")

def meeting_summary_page():
    """Handle meeting summary processing."""
    st.title("Meeting Summary Generator")
    
    # Model selection
    model_id = st.selectbox(
        "Select AI Model", 
        options=list(AI_MODELS.keys()),
        format_func=lambda x: AI_MODELS[x],
        key="meeting_model"
    )
    
    # File selection
    transcript_files = list(TRANSCRIPTS_DIR.glob("*.md"))
    if not transcript_files:
        st.warning("No transcript files found in examples/sources/transcripts/")
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
            
            response = call_lucy_api("/interview/transcript_to_summary", method="POST", data=data)
            
            if "content" in response:
                st.success("Summary generated successfully!")
                
                # Display summary
                st.markdown("### Meeting Summary")
                st.markdown(response["content"])
                
                # Save summary
                output_filename = f"{selected_file.stem}_{model_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                output_path = SUMMARY_OUTPUT_DIR / output_filename
                
                with open(output_path, "w") as f:
                    f.write(response["content"])
                
                st.success(f"Summary saved to {output_path}")
            else:
                st.error("Failed to generate summary")

def game_plan_review_page():
    """Handle game plan review processing."""
    st.title("Game Plan Review")
    
    # Model selection
    model_id = st.selectbox(
        "Select AI Model", 
        options=list(AI_MODELS.keys()),
        format_func=lambda x: AI_MODELS[x],
        key="review_model"
    )
    
    # File selection
    game_plan_files = list(GAME_PLANS_DIR.glob("*.pdf"))
    if not game_plan_files:
        st.warning("No game plan files found in examples/sources/game_plans/")
        # Allow file upload
        uploaded_file = st.file_uploader("Upload PDF Game Plan", type="pdf")
        if uploaded_file:
            pdf_text = extract_pdf_text(uploaded_file)
            filename = uploaded_file.name
    else:
        selected_file = st.selectbox(
            "Select Game Plan File",
            options=game_plan_files,
            format_func=lambda x: x.name
        )
        
        if selected_file:
            with open(selected_file, "rb") as f:
                pdf_text = extract_pdf_text(f)
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
                
                response = call_lucy_api("/game_plan_review", method="POST", data=data)
                
                if "content" in response:
                    st.success("Review completed successfully!")
                    
                    # Display review
                    st.markdown("### Game Plan Review")
                    st.markdown(response["content"])
                    
                    # Save review
                    output_filename = f"{Path(filename).stem}_{model_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                    output_path = REVIEW_OUTPUT_DIR / output_filename
                    
                    with open(output_path, "w") as f:
                        f.write(response["content"])
                    
                    st.success(f"Review saved to {output_path}")
                else:
                    st.error("Failed to generate review")

def template_management_page():
    """Handle template viewing and editing."""
    st.title("Template Management")
    
    template_type = st.selectbox(
        "Select Template Type",
        options=["meeting_summary", "game_plan_review"]
    )
    
    # Get current template
    if st.button("Load Template"):
        response = call_lucy_api(f"/template/{template_type}")
        if "template" in response:
            st.session_state[f"current_template_{template_type}"] = response["template"]
        else:
            st.error("Failed to load template")
    
    # Display and edit template
    if f"current_template_{template_type}" in st.session_state:
        template_content = st.text_area(
            "Template Content",
            value=st.session_state[f"current_template_{template_type}"],
            height=400
        )
        
        # Save template
        if st.button("Save Template", type="primary"):
            data = {"template": template_content}
            response = call_lucy_api(f"/template/{template_type}", method="PUT", data=data)
            
            if response.get("status") == "success":
                st.success("Template saved successfully!")
                st.session_state[f"current_template_{template_type}"] = template_content
            else:
                st.error("Failed to save template")

def main():
    """Main application entry point."""
    st.set_page_config(
        page_title="Lucy AI Mock Client",
        page_icon="🏠",
        layout="wide"
    )
    
    # Pages configuration
    pages = [
        st.Page(welcome_page, title="Welcome", icon="🏠"),
        st.Page(meeting_summary_page, title="Meeting Summary", icon="📝"),
        st.Page(game_plan_review_page, title="Game Plan Review", icon="📋"),
        st.Page(template_management_page, title="Template Management", icon="⚙️")
    ]
    
    # Navigation
    nav = st.navigation(pages)
    nav.run()

if __name__ == "__main__":
    main()
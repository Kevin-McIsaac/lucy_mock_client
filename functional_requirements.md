# Lucy AI Mock Client - Functional Requirements

## 1. Executive Summary

The Lucy AI Mock Client is a Streamlit-based web application that serves as a frontend interface for the Lucy AI server. It provides mortgage professionals with tools to process meeting transcripts and review mortgage game plans. The application  supports multiple AI models for processing.

## 2. System Overview

### 2.1 Purpose
To provide a user-friendly interface for processing mortgage-related documents using AI-powered analysis, enabling professionals to:
- Convert meeting transcripts into actionable summaries 
- Review mortgage game plans for compliance issues

### 2.2 Architecture
- **Frontend**: Streamlit web application with multi-page navigation based on st.navigation build
- **Backend**: Lucy AI server API (external dependency)
- **Implementation**: Single Python file (lucy_AI_mock_client.py) with functional programming approach

## 3. Functional Requirements

### 3.1 Core Features

#### 3.1.1 Meeting Summary Processing
- **Upload Meeting Transcripts**: Let the user select markdown files containing meeting transcripts from examples/sources/transcripts. Display the transcript in st.markdown that is inside a closed expander
- **Generate Meeting Summaries**: Process transcripts through Lucy AI API to create structured meeting summaries. Display the review as formatted markdown
- **Export Capabilities**: Save summaries to the folder examples/output/meeting_summary using the filename from the transcript
- **File Naming**: Include source filename, model ID, and timestamp in output names

#### 3.1.2 Game Plan Review
- **Upload PDF Game Plans**: Let the user select PDF files containing mortgage game plans from examples/sources/game_plans
- **File Upload Alternative**: Allow direct PDF upload when no files exist in the source directory  
- **Extract Text**: Convert PDF content to text for processing and show in closed expander
- **Review**: Analyze game plans using Lucy AI. Display the review as formatted markdown
- **Save Reviews**: Save reviews to the folder examples/output/game_plan_review using the filename from the game plan
- **File Naming**: Include source filename, model ID, and timestamp in output names

### 3.2 User Interface Components

#### 3.2.1 Navigation
- Multi-page application with sidebar navigation.
- Two main pages: Meeting Summary and Game Plan Review
- Welcome page with overview of available features

#### 3.2.2 Common Controls
- **Model Selection**: Choose from multiple AI models for processing. 
- **Template Editor**: Modify templates used for summaries and reviews
- **File Upload**: Upload documents for processing
- **Process Buttons**: Initiate AI processing of documents
- **Save Functions**: Export results to local file system
- **Server Status Check**: Verify Lucy AI server connectivity

### 3.3 AI Model Support
Support for the following AI models:
- Anthropic Claude models (3.7 Sonnet, 3.5 Haiku)
- OpenAI GPT models (4.1, 4.1-mini)
- Google Gemini models (2.0 Flash, 2.5 Flash Preview)
- Groq Llama models (4 Maverick, 4 Scout)

### 3.4 Template Management
- **View Templates**: Display current templates for summaries and reviews. Use lucy_ai_server API to get templates
- **Edit Templates**: Modify templates.
- **Save Templates**: Persist template changes to the server Use lucy_ai_server API to get templates


### 3.5 File Management
- **Input Files**: markdown (transcripts) and PDF (game plans)
- **Output Directory Structure**: Organized storage in `examples/output/`
  - `meeting_summary/`: Processed transcript summaries
  - `game_plan_review/`: Game plan compliance reviews
- **File Naming**: Include source filename and model used in output names

### 3.6 Session State Management
- Preserve user preferences (model selection)

### 3.7 Error Handling
- Display appropriate error messages
- Provide user guidance for error resolution

### 3.8 Integration Requirements

#### 3.8.1 Lucy AI Server API
- **Endpoints**:
  - `/interview/transcript_to_summary/`: Generate meeting summaries
  - `/game_plan_review/`: Analyze game plans for compliance
  - `/template/`: GET/PUT template management
  - `/status/`: Server health check
- **Authentication**: API key-based authentication using x-api-key header
- **Data Format**: JSON request/response with markdown content
- **Request Parameters**: 
  - Use `model_slug` for model selection
  - Use `transcript` for meeting summary input
  - Use `game_plan` for game plan review input


### 3.9 Performance Requirements
- Responsive UI during API calls (loading spinners)
- Progress indicators for long-running operations

### 3.10 Security Requirements
- Environment variable storage for sensitive configuration
- API key management through headers
- Use .env file with API_ENDPOINT and API_KEY variables

## 4. Non-Functional Requirements

### 4.1 Usability
- Clean, intuitive interface with clear navigation
- Tooltips and help text for guidance

### 4.2 Compatibility
- Python 3.13.3 
- streamlit 1.45.1

### 4.3 Environment
- Virtual environment support through setup.sh script
- Requirements file for dependency management

### 4.4 Extensibility
- Single Python file implementation (lucy_AI_mock_client.py)
- Functions for common features (calling Lucy APIs, file handling)
- Model configuration dictionary for easy additions

### 4.5 Documentation
- Code documentation with docstrings
- Type hints based on Python 3.13.3
- README.md with setup and usage instructions
- Configuration guidance in CLAUDE.md

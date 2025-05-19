# Lucy AI Mock Client - Functional Requirements

## 1. Executive Summary

The Lucy AI Mock Client is a Streamlit-based web application that serves as a frontend interface for the Lucy AI server. It provides mortgage professionals with tools to process meeting transcripts and review mortgage game plans. The application  supports multiple AI models for processing.

## 2. System Overview

### 2.1 Purpose
To provide a user-friendly interface for processing mortgage-related documents using AI-powered analysis, enabling professionals to:
- Summarise meeting transcripts into actionable meeting summaries 
- Review mortgage game plans for compliance issues

### 2.2 Architecture
- **Frontend**: Streamlit web application with multi-page navigation using st.navigation and st.Page
- **Backend**: Lucy AI server API (external dependency)
- **Implementation**: Single Python file (lucy_AI_mock_client.py) with functional programming approach
- **State Management**: Streamlit session state for caching and user preferences

## 3. Functional Requirements

### 3.1 Core Features

#### 3.1.1 Meeting Summary Processing
- **Upload Meeting Transcripts**: Let the user select markdown files containing meeting transcripts from examples/sources/transcripts. Display the transcript in st.markdown that is inside a closed expander
- **Generate Meeting Summaries**: Process transcripts through Lucy AI API to create structured meeting summaries. Display the content as formatted markdown with escaped dollar signs to avoid formatting issues.
- **Usage Metadata**: Display model usage information in st.info after the summary content
- **Export Capabilities**: Save summaries to the folder examples/output/meeting_summary using the filename from the transcript
- **File Naming**: Format: `{original_filename}_{model_id}.md` (no timestamps)

#### 3.1.2 Game Plan Review
- **Upload PDF Game Plans**: Let the user select PDF files containing mortgage game plans from examples/sources/game_plans
- **Extract Text**: Convert PDF content to text for processing and show in closed expander with caching
- **Review Type Selection**: Allow users to choose from dynamically discovered review endpoints
  - Automatically discover all available `/game_plan_review/*` endpoints from OpenAPI spec
  - Provide user-friendly names for each endpoint
  - Fall back to standard endpoints if OpenAPI is unavailable
- **Review**: Analyze game plans using selected endpoint. Display the content as formatted markdown with escaped dollar signs to avoid formatting issues.
- **Usage Metadata**: Display model usage information in st.info after the review content
- **Save Reviews**: Save reviews to the folder examples/output/game_plan_review using the filename from the game plan
- **File Naming**: 
  - Standard review: `{original_filename}_{model_id}.md`
  - Alternative endpoints: `{original_filename}_{model_id}_{endpoint_type}.md`

### 3.2 User Interface Components

#### 3.2.1 Navigation
- Multi-page application using st.navigation and st.Page
- Four main pages: Welcome, Meeting Summary, Game Plan Review, Template Management
- Sidebar with global model selection that persists across pages

#### 3.2.2 Common Controls
- **Model Selection**: Choose from multiple AI models in sidebar (shared across pages)
- **Template Editor**: View and modify templates with dynamic list from API
- **File Upload**: Upload documents for processing (PDF support, including encrypted)
- **Process Buttons**: Primary buttons for initiating AI processing
- **Save Functions**: Automatic export to local file system
- **Server Status Check**: Verify Lucy AI server connectivity and display OpenAPI endpoints
- **Dollar Sign Escaping**: Automatic escaping using regex pattern for proper markdown rendering
- **Process Cleanup**: Automatic cleanup of existing processes to prevent port conflicts 

### 3.3 AI Model Support
Support for the following AI models with specific identifiers:
- **Anthropic Claude models**:
  - Claude 3.7 Sonnet Latest (`anthropic:claude-3-7-sonnet-latest`)
  - Claude 3.5 Haiku Latest (`anthropic:claude-3-5-haiku-latest`)
- **OpenAI GPT models**:
  - GPT 4.1 (`openai:gpt-4.1`)
  - GPT 4.1 Mini (`openai:gpt-4.1-mini`)
- **Google Gemini models**:
  - Gemini 2.0 Flash (`google_genai:gemini-2.0-flash`)
  - Gemini 2.5 Flash Preview (`google_genai:gemini-2.5-flash-preview-04-17`)
- **Groq Llama models**:
  - Llama 4 Maverick (`groq:meta-llama/llama-4-maverick-17b-128e-instruct`)
  - Llama 4 Scout (`groq:meta-llama/llama-4-scout-17b-16e-instruct`)

### 3.4 Template Management
- **List Templates**: Dynamically fetch available templates from `/template/list/` API
- **View Templates**: Display current templates with user-friendly names
- **Edit Templates**: Modify templates using text area with configurable height
- **Save Templates**: Persist template changes to server via PUT with plain text body
- **Load Templates**: GET with `file_name` query parameter, returns plain text
- **Template Display**: Convert API keys to human-readable names (e.g., "/game_plan_review/" → "Game Plan Review")
- **Pull Request**: Create pull request via POST to `/template/` with `file_name` as query parameter and empty body


### 3.5 File Management
- **Input Files**: markdown (transcripts) and PDF (game plans)
- **Output Directory Structure**: Organized storage in `examples/output/`
  - `meeting_summary/`: Processed transcript summaries
  - `game_plan_review/`: Game plan compliance reviews
- **File Naming**: 
  - Standard format: `{original_filename}_{model_id}.md` (no timestamps)
  - Alternative game plan endpoints: `{original_filename}_{model_id}_{endpoint_type}.md`
- **PDF Caching**: Extracted PDF text is cached in session state to avoid reprocessing

### 3.6 Session State Management
- Preserve user preferences (model selection)
- Template caching using simple dictionary structure
- PDF text caching to avoid re-extraction

### 3.7 Error Handling
- Display appropriate error messages
- Provide user guidance for error resolution
- Consistent error handling with structured exception catching
- Detailed error messages including HTTP status codes and API responses

### 3.8 Integration Requirements

#### 3.8.1 Lucy AI Server API
Lucy AI server provides an OpenAPI JSON description of 
each endpoint at `http://localhost:8000/openapi.json`. This should 
take precedence over the specifications below. The client now fetches
and displays available endpoints from the OpenAPI spec.
- **Endpoints**:
  - Use `API_ENDPOINT` from .env as the base of the API url
  - `/interview/transcript_to_summary/`: Generate meeting summaries
  - `/game_plan_review/`: Analyze game plans for compliance (standard review)
  - `/game_plan_review/*`: Additional game plan review endpoints (dynamically discovered)
  - `/template/`: GET/PUT/POST template management with `file_name` query parameter
  - `/template/list/`: GET list of available templates
  - `/status/`: Server health check
- **Authentication**: API key-based authentication using x-api-key header found in .env as `API_KEY`
- **Data Format**: 
  - JSON request/response for main endpoints
  - Plain text response for template GET
  - Plain text body for template PUT
  - Empty body for template POST (Pull Request)
  - All responses contain `content` field with generated text
  - Responses may include `usage_metadata` field with model usage information
- **Request Parameters**: 
  - Use `model` for model selection (full model ID with provider prefix)
  - Use `input_text` for both meeting summary and game plan review input
  - Use `file_name` as query parameter for template operations
- **Endpoint Format**: All endpoints require trailing slashes


### 3.9 Performance Requirements
- Responsive UI during API calls (loading spinners)
- Progress indicators for long-running operations
- Cache PDF text extraction

### 3.10 Security Requirements
- Environment variable storage for sensitive configuration
- API key management through headers
- Use .env file with API_ENDPOINT and API_KEY variables
- Support for encrypted PDF files with PyCryptodome

## 4. Non-Functional Requirements

### 4.1 Usability
- Clean, intuitive interface with clear navigation
- Tooltips and help text for guidance
- Simple top to bottom flow of UI to match streamlit model

### 4.2 Compatibility
- Python 3.13.3 
- streamlit 1.45.1

### 4.3 Environment
- Virtual environment support through setup.sh script
- Requirements file for dependency management
- Cleanup script for handling process conflicts
- Launch script with robust error handling

### 4.4 Extensibility
- Single Python file implementation (lucy_AI_mock_client.py)
- Functions for common features (calling Lucy APIs, file handling)
- Model configuration dictionary for easy additions

### 4.5 Documentation
- Code documentation with comprehensive docstrings
- Type hints based on Python 3.13.3
- README.md with setup and usage instructions
- Configuration guidance in CLAUDE.md
- Detailed function documentation including arguments and return values

# Claude Configuration Guide

## Project Overview

This is a Streamlit application that interfaces with the Lucy AI server for processing mortgage documents.

## Key Components

1. **lucy_AI_mock_client.py**: Main application file containing all functionality
   - Improved error handling with consistent exception catching
   - Enhanced documentation with comprehensive docstrings
   - Simplified session state management
   - OpenAPI integration for endpoint discovery
2. **requirements.txt**: Python dependencies (streamlit, requests, python-dotenv, PyPDF2, pycryptodome)
3. **.env**: Environment variables for API configuration (API_ENDPOINT, API_KEY)
4. **setup.sh**: Virtual environment setup script
5. **launch_lucy_ai.sh**: Script to launch both Lucy AI server and mock client
6. **cleanup_processes.sh**: Script to handle port conflicts and kill stuck processes

## Environment Variables

The following environment variables must be set in `.env`:
```
API_ENDPOINT=http://localhost:8000
API_KEY=your-api-key-here
```

## Testing Commands

When working on this project, run these commands to verify code quality:

```bash
# Type checking (if mypy is installed)
mypy lucy_AI_mock_client.py

# Code formatting (if black is installed)
black lucy_AI_mock_client.py

# Linting (if ruff is installed)
ruff check lucy_AI_mock_client.py
```

## API Integration

The app integrates with Lucy AI server endpoints:
- `/interview/transcript_to_summary/`: Process meeting transcripts
- `/game_plan_review/`: Analyze game plans (standard review)
- `/game_plan_review/*`: Additional game plan review endpoints (dynamically discovered from OpenAPI spec)
- `/template/`: Manage templates (GET/PUT/POST with `file_name` query parameter)
- `/template/list/`: Get available templates
- `/status/`: Check server health

Note: All endpoints require trailing slashes.

### API Request Format
- Authentication: `x-api-key` header
- Model parameter: `model` (full model ID with provider prefix)
- Meeting summary input: `input_text` key
- Game plan input: `input_text` key
- Template operations: `file_name` as query parameter

### API Response Format
- Content field: `content` contains generated text
- Usage metadata: `usage_metadata` field with model usage information
- Template list: Returns a list of template filenames
- Template GET: Returns plain text
- Template PUT: Accepts plain text body
- Template POST: Accepts empty body for Pull Request creation

## Development Notes

- Uses Python 3.13.3 with type hints
- Simple single-file architecture (no classes, just functions)
- Streamlit st.navigation for multi-page setup using st.Page objects
- Page headers use st.header instead of st.title for more compact layout
- Session state for user preferences, template management, and PDF caching
- Virtual environment: `.venv` directory
- UI elements: st.info for usage metadata, escaped dollar signs for markdown
- No visual dividers between content sections
- Comprehensive docstrings with Args and Returns documentation
- Consistent error handling with structured exception catching
- Simplified session state management using dictionaries
- Custom CSS applied to reduce page spacing and create a more compact UI

## Common Operations

1. Add new AI model:
   - Update `AI_MODELS` dictionary in lucy_AI_mock_client.py
   - Use consistent model ID format (e.g., "claude-3.7-sonnet")

2. Change API endpoint:
   - Update `API_ENDPOINT` in .env (not `LUCY_API_URL`)
   - Ensure trailing slashes on endpoints

3. Debug API calls:
   - Check `call_lucy_api()` function
   - Enhanced error messages with HTTP status codes
   - Uses `allow_redirects=True` for handling redirects
   - Improved error handling with detailed responses
   - Supports `empty_body` parameter for POST requests with empty payload

4. File handling:
   - Transcripts: Markdown files in `examples/sources/transcripts/`
   - Game plans: PDF files in `examples/sources/game_plans/`
   - Outputs saved with model ID (format: `{original_filename}_{model_id}.md`)
   - Game plan reviews with alternative endpoints include endpoint suffix: `{original_filename}_{model_id}_{endpoint_type}.md`

5. Template management:
   - Templates list: `/template/list/` returns a list of template filenames
   - Load template: GET request with `file_name` query parameter 
   - Save template: PUT request with plain text body and `file_name` query parameter
   - Pull Request: POST request with empty body and `file_name` query parameter
   - UI uses two-column layout for Save Template (primary) and Pull Request (secondary) buttons
   - Auto-loading templates when selected from dropdown

## Error Handling

Common issues and solutions:
- 401 Unauthorized: Check API_KEY in .env
- 422 Unprocessable Entity: Verify `model` parameter
- 307 Redirect: Endpoints require trailing slashes
- PDF errors: Handled separately with specific error messages
- Connection errors: Display clear messages about API connectivity issues

## Project Structure

```
lucy_mock_client/
├── lucy_AI_mock_client.py   # Main application
├── setup.sh                 # Setup script
├── requirements.txt         # Dependencies
├── .env                     # API configuration
├── examples/
│   ├── sources/
│   │   ├── transcripts/     # Input markdown files
│   │   └── game_plans/      # Input PDF files
│   └── output/
│       ├── meeting_summary/ # Generated summaries
│       └── game_plan_review/# Generated reviews
└── .venv/                   # Virtual environment
```

## OpenAPI Integration

- Fetches and uses the openapi.json definitions from http://localhost:8000/openapi.json
- Displays available endpoints in the welcome page status check
- Uses OpenAPI spec for endpoint discovery and validation
- Dynamically discovers game plan review endpoints (paths starting with `/game_plan_review/`)
- Provides user-friendly names for discovered endpoints

## Utility Scripts

1. **setup.sh** - Sets up the virtual environment and installs dependencies
2. **launch_lucy_ai.sh** - Starts both Lucy AI server and mock client
   - Automatically cleans up existing processes before starting
   - Handles proper shutdown with signal trapping
   - Stores PIDs for process management
3. **cleanup_processes.sh** - Kills existing processes and frees port 8000
   - Finds processes by port number
   - Force kills stuck processes
   - Verifies port is free before exiting
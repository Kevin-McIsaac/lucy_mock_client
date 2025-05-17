# Claude Configuration Guide

## Project Overview

This is a Streamlit application that interfaces with the Lucy AI server for processing mortgage documents.

## Key Components

1. **lucy_AI_mock_client.py**: Main application file containing all functionality
2. **requirements.txt**: Python dependencies (streamlit, requests, python-dotenv, PyPDF2)
3. **.env**: Environment variables for API configuration
4. **setup.sh**: Virtual environment setup script
5. **launch_lucy_ai.sh**: Script to launch both Lucy AI server and mock client

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
- `/game_plan_review/`: Analyze game plans
- `/template/`: Manage templates (GET/PUT with `file_name` query parameter)
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
- Template GET: Returns plain text
- Template PUT: Accepts plain text body

## Development Notes

- Uses Python 3.13.3 with type hints
- Simple single-file architecture (no classes, just functions)
- Streamlit st.navigation for multi-page setup using st.Page objects
- Session state for user preferences, template management, and PDF caching
- Virtual environment: `.venv` directory
- UI elements: st.info for usage metadata, escaped dollar signs for markdown
- No visual dividers between content sections

## Common Operations

1. Add new AI model:
   - Update `AI_MODELS` dictionary in lucy_AI_mock_client.py
   - Use consistent model ID format (e.g., "claude-3.7-sonnet")

2. Change API endpoint:
   - Update `API_ENDPOINT` in .env (not `LUCY_API_URL`)
   - Ensure trailing slashes on endpoints

3. Debug API calls:
   - Check `call_lucy_api()` function
   - Note: function adds trailing slashes automatically
   - Uses `allow_redirects=True` for handling redirects

4. File handling:
   - Transcripts: Markdown files in `examples/sources/transcripts/`
   - Game plans: PDF files in `examples/sources/game_plans/`
   - Outputs saved with timestamp and model ID

## Error Handling

Common issues and solutions:
- 401 Unauthorized: Check API_KEY in .env
- 422 Unprocessable Entity: Verify `model_slug` parameter
- 307 Redirect: Endpoints require trailing slashes

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

- Use the openapi.json definitions of the lucy_ai_server from the URL http://localhost:8000/openapi.json
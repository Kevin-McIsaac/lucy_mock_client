# Lucy AI Mock Client

A Streamlit-based web application for processing mortgage documents using AI-powered analysis with a compact, streamlined UI.

## Features

- Process meeting transcripts into actionable summaries
- Review mortgage game plans for compliance issues
- Generate BID notes from game plans for enhanced analysis
- Support for multiple AI models (Claude, GPT, Gemini, Llama)
- Template management with automatic template loading
- Compact UI with optimized spacing and layout
- Shared model selection across all pages
- Server status checking with OpenAPI spec display
- PDF text extraction and caching (supports encrypted PDFs)
- Enhanced error handling with detailed messages
- Automatic process cleanup to prevent port conflicts

## Prerequisites

- Python 3.13.3 or higher
- Lucy AI server running (typically at http://localhost:8000)
- PyCryptodome for encrypted PDF support

## Setup

1. Create and activate virtual environment:
```bash
chmod +x setup.sh
./setup.sh
source .venv/bin/activate
```

2. Configure environment variables in `.env`:
```
API_ENDPOINT=http://localhost:8000
API_KEY=your-api-key-here
```

3. Run the application:
```bash
streamlit run lucy_AI_mock_client.py
```

### Alternative: Launch Both Server and Client

Use the provided launch script to start both components:
```bash
chmod +x launch_lucy_ai.sh
./launch_lucy_ai.sh
```

If you encounter port conflicts, use the cleanup script:
```bash
chmod +x cleanup_processes.sh
./cleanup_processes.sh
```

## Usage

### Meeting Summary Generator

1. Place transcript files (.md) in `examples/sources/transcripts/`
2. Select a transcript file from the dropdown
3. Click "Generate Summary"
4. View the generated summary with escaped dollar signs for proper markdown rendering
5. Usage metadata displays in an info box after the content
6. Results are saved to `examples/output/meeting_summary/` with clickable GitHub repository links

### Game Plan Review

1. Place game plan files (.pdf) in `examples/sources/game_plans/`
   - Or upload a PDF directly if no files exist
2. Select a review type from available endpoints
   - Automatically discovers all available `/game_plan/review/*` endpoints from the OpenAPI spec
   - Falls back to standard endpoints if OpenAPI is unavailable
3. Select a file from the dropdown
4. PDF text is extracted and cached automatically
5. Click "Review Game Plan"
6. View the review with escaped dollar signs for proper markdown rendering
7. Usage metadata displays in an info box after the content
8. Results are saved to `examples/output/game_plan_review/` with appropriate suffixes based on review type and clickable GitHub repository links

### BID Notes Generation

1. Place game plan files (.pdf) in `examples/sources/game_plans/`
   - Or upload a PDF directly if no files exist
2. Select a notes type from available endpoints
   - Automatically discovers all available `/BID_notes/*` endpoints from the OpenAPI spec
   - Falls back to standard endpoints if OpenAPI is unavailable
3. Select a file from the dropdown
4. PDF text is extracted and cached automatically
5. Click "Generate BID Notes"
6. View the notes with escaped dollar signs for proper markdown rendering
7. Usage metadata displays in an info box after the content
8. Results are saved to `examples/output/BID_notes/` with appropriate suffixes based on notes type and clickable GitHub repository links

### Template Management

1. Navigate to Template Management page
2. Templates are dynamically loaded from `/template/list/` as a list of filenames
3. Select a template from the dropdown (displaying user-friendly names created from filename stems)
4. Template content is automatically loaded when a template is selected
5. Edit the template content in the text area
6. Click "Save Template" to update (sends plain text body with file_name query parameter)
7. Click "Pull Request" to create a pull request (sends POST with empty body and file_name parameter)

### Model Selection

- AI model selection is available in the sidebar
- Selected model persists across all pages
- Model choice applies to both meeting summaries and game plan reviews

## Directory Structure

```
examples/
├── sources/
│   ├── transcripts/      # Meeting transcript markdown files
│   └── game_plans/       # Game plan PDF files
└── output/
    ├── meeting_summary/  # Generated meeting summaries
    ├── game_plan_review/ # Generated game plan reviews
    └── BID_notes/        # Generated BID notes
```

Output files are named with format: `{original_filename}_{model_id}.md`
Game plan reviews and BID notes with alternative endpoints include a suffix: `{original_filename}_{model_id}_{endpoint_type}.md`

## Available AI Models

- **Anthropic**: 
  - Claude 3.7 Sonnet Latest (`anthropic:claude-3-7-sonnet-latest`)
  - Claude 3.5 Haiku Latest (`anthropic:claude-3-5-haiku-latest`)
- **OpenAI**: 
  - GPT 4.1 (`openai:gpt-4.1`)
  - GPT 4.1 Mini (`openai:gpt-4.1-mini`)
- **Google**: 
  - Gemini 2.0 Flash (`google_genai:gemini-2.0-flash`)
  - Gemini 2.5 Flash Preview (`google_genai:gemini-2.5-flash-preview-04-17`)
- **Groq**: 
  - Llama 4 Maverick (`groq:meta-llama/llama-4-maverick-17b-128e-instruct`)
  - Llama 4 Scout (`groq:meta-llama/llama-4-scout-17b-16e-instruct`)

## API Integration

### Request Parameters
- Meeting Summary: `input_text` (transcript content) and `model` (model ID)
- Game Plan Review: `input_text` (PDF text) and `model` (model ID)
- BID Notes: `input_text` (PDF text) and `model` (model ID)
- Templates: `file_name` as query parameter

### Response Format
- All content responses return a `content` field containing the generated text
- Responses may include `usage_metadata` field with model usage information
- Template operations return plain text responses

## Development

See [CLAUDE.md](CLAUDE.md) for development guidelines and troubleshooting.

## Troubleshooting

### Common Issues

1. **401 Unauthorized**: Check that your API_KEY in `.env` is correct
2. **422 Unprocessable Entity**: Verify request parameters are correct
3. **Connection Error**: Ensure Lucy AI server is running at the configured endpoint
4. **PDF Loading Spinner**: PDF text is cached after first extraction to avoid re-processing
5. **Dollar Sign Display**: Dollar signs in responses are automatically escaped for markdown
6. **Encrypted PDFs**: Install pycryptodome if you see "PyCryptodome is required" error
7. **Port Already in Use**: Run `./cleanup_processes.sh` to kill existing processes

### API Endpoints

The application connects to the following Lucy AI server endpoints:
- `/status/` - Health check
- `/interview/initial_broker_interview/transcript_to_summary/` - Meeting summary generation
- `/game_plan/review/` - Game plan analysis (standard review)
- `/game_plan/review/*` - Additional game plan review endpoints (automatically discovered)
- `/BID_notes/` - BID notes generation (standard notes)
- `/BID_notes/*` - Additional BID notes endpoints (automatically discovered)
- `/file_extractor/drivers_licence/` - Extracts information from driver's license images
- `/template/` - Template load/save/pull request with `file_name` query parameter
  - GET: Load template (returns plain text)
  - PUT: Save template (accepts plain text body)
  - POST: Create pull request (accepts empty body)
- `/template/list/` - Get available templates (returns a list of filenames)
- `/openapi.json` - OpenAPI specification for endpoint discovery

Notes: 
- All endpoints use trailing slashes (except /openapi.json)
- File extractor only works with Claude Sonnet or GPT-4 models
- Application includes backwards compatibility handling for old endpoint paths


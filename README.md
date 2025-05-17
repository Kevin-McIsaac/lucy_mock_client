# Lucy AI Mock Client

A Streamlit-based web application for processing mortgage documents using AI-powered analysis.

## Features

- Process meeting transcripts into actionable summaries
- Review mortgage game plans for compliance issues
- Support for multiple AI models (Claude, GPT, Gemini, Llama)
- Template management with dynamic template selection
- Shared model selection across all pages
- Server status checking
- PDF text extraction and caching

## Prerequisites

- Python 3.13.3 or higher
- Lucy AI server running (typically at http://localhost:8000)

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

## Usage

### Meeting Summary Generator

1. Place transcript files (.md) in `examples/sources/transcripts/`
2. Select a transcript file from the dropdown
3. Click "Generate Summary"
4. View the generated summary with escaped dollar signs for proper markdown rendering
5. Results are saved to `examples/output/meeting_summary/`

### Game Plan Review

1. Place game plan files (.pdf) in `examples/sources/game_plans/`
   - Or upload a PDF directly if no files exist
2. Select a file from the dropdown
3. PDF text is extracted and cached automatically
4. Click "Review Game Plan"
5. View the review with escaped dollar signs for proper markdown rendering
6. Results are saved to `examples/output/game_plan_review/`

### Template Management

1. Navigate to Template Management page
2. Templates are dynamically loaded from `/template/list/`
3. Select a template from the dropdown (displaying user-friendly names)
4. Click "Load Template" to view current template content
5. Edit the template content in the text area
6. Click "Save Template" to update

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
    └── game_plan_review/ # Generated game plan reviews
```

Output files are named with format: `{original_filename}_{model_id}.md`

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
- Templates: `file_name` as query parameter

### Response Format
- All content responses return a `content` field containing the generated text
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

### API Endpoints

The application connects to the following Lucy AI server endpoints:
- `/status/` - Health check
- `/interview/transcript_to_summary/` - Meeting summary generation
- `/game_plan_review/` - Game plan analysis
- `/template/` - Template load/save with `file_name` query parameter
- `/template/list/` - Get available templates

Note: All endpoints use trailing slashes.

## License

[Add your license information here]
# Lucy AI Mock Client

A Streamlit-based web application for processing mortgage documents using AI.

## Features

- Process meeting transcripts into actionable summaries
- Review mortgage game plans for compliance issues
- Support for multiple AI models (Claude, GPT, Gemini, Llama)
- Template management for customizable outputs
- Server status checking

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
3. Choose an AI model
4. Click "Generate Summary"
5. Results are saved to `examples/output/meeting_summary/`

### Game Plan Review

1. Place game plan files (.pdf) in `examples/sources/game_plans/`
   - Or upload a PDF directly if no files exist
2. Select a file from the dropdown
3. Choose an AI model
4. Click "Review Game Plan"
5. Results are saved to `examples/output/game_plan_review/`

### Template Management

1. Navigate to Template Management page
2. Select template type (meeting_summary or game_plan_review)
3. Click "Load Template" to view current template
4. Edit the template content
5. Click "Save Template" to update

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

## Available AI Models

- **Anthropic**: Claude 3.7 Sonnet, Claude 3.5 Haiku
- **OpenAI**: GPT 4.1, GPT 4.1 Mini
- **Google**: Gemini 2.0 Flash, Gemini 2.5 Flash Preview
- **Groq**: Llama 4 Maverick, Llama 4 Scout

## Development

See [CLAUDE.md](CLAUDE.md) for development guidelines and troubleshooting.

## Troubleshooting

### Common Issues

1. **401 Unauthorized**: Check that your API_KEY in `.env` is correct
2. **422 Unprocessable Entity**: Ensure you're using supported model IDs
3. **Connection Error**: Verify Lucy AI server is running at the correct endpoint
4. **No transcript files found**: Place .md files in `examples/sources/transcripts/`
5. **No game plan files found**: Place .pdf files in `examples/sources/game_plans/`

### API Endpoints

The application connects to the following Lucy AI server endpoints:
- `/status/` - Health check
- `/interview/transcript_to_summary/` - Meeting summary generation
- `/game_plan_review/` - Game plan analysis
- `/template/` - Template management

Note: All endpoints require trailing slashes.

## License

[Add your license information here]
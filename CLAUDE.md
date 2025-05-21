# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Streamlit application that interfaces with the Lucy AI server for processing mortgage documents, including meeting transcript summaries, game plan reviews, BID notes generation, and file extraction.

## Key Components

1. **lucy_AI_mock_client.py**: Main application file containing all functionality
   - Single-file architecture with function-based organization
   - OpenAPI integration for dynamic endpoint discovery
   - Session state for user preferences and file caching
   - Multi-page navigation with shared model selection
   - File handling for transcripts, PDFs, and images

2. **Utility Scripts**:
   - **setup.sh**: Virtual environment setup
   - **launch_lucy_ai.sh**: Script to launch both server and client
   - **cleanup_processes.sh**: Handles port conflicts and process cleanup
   - **file_extractor_helper.py**: Helper for file extraction functionality

## Development Commands

```bash
# Setup environment
./setup.sh
source .venv/bin/activate

# Run application
streamlit run lucy_AI_mock_client.py

# Launch both server and client
./launch_lucy_ai.sh

# Clean up processes if port conflicts occur
./cleanup_processes.sh

# Install development tools (optional)
pip install ruff mypy black

# Code quality verification
ruff check lucy_AI_mock_client.py
ruff format lucy_AI_mock_client.py  # Optional: auto-format code
mypy lucy_AI_mock_client.py  # Optional: type checking (requires mypy installation)
black lucy_AI_mock_client.py  # Optional: code formatting (requires black installation)
```

## Environment Configuration

Required environment variables in `.env`:
```
API_ENDPOINT=http://localhost:8000
API_KEY=your-api-key-here
```

## API Integration

The application integrates with several Lucy AI server endpoints:

| Endpoint | Purpose | Request Format | Response Format |
|----------|---------|---------------|-----------------|
| `/interview/initial_broker_interview/transcript_to_summary` | Process meeting transcripts | `input_text`, `model` | `content`, `usage_metadata` |
| `/game_plan/review` | Standard game plan review | `input_text`, `model` | `content`, `usage_metadata` |
| `/game_plan/review/*` | Specialized game plan reviews | `input_text`, `model` | `content`, `usage_metadata` |
| `/BID_notes` | Standard BID notes | `input_text`, `model` | `content`, `usage_metadata` |
| `/BID_notes/*` | Specialized BID notes | `input_text`, `model` | `content`, `usage_metadata` |
| `/file_extractor/drivers_licence` | Extract info from license images | `image_base64`, `model` | `content` (JSON) |
| `/template` | Manage templates | `file_name` (query param) | Various |
| `/template/list` | List templates | None | Template filename list |
| `/status` | Server health check | None | Status response |

Notes:
- All endpoints now use paths without trailing slashes
- Authentication via `x-api-key` header
- Model parameter uses full model ID with provider prefix
- File extractor only works with Claude Sonnet or GPT-4.1 models (auto-fallback implemented)
- Error handling includes automatic retrying with new endpoint paths if old paths return 404

## Implementation Guidelines

### File Structure
- Source files in `examples/sources/` (transcripts, game_plans, file_extractor)
- Output files in `examples/output/` (meeting_summary, game_plan_review, BID_notes)
- Output naming: `{original_filename}_{model_id}.md` or `{original_filename}_{model_id}_{endpoint_type}.md`

### Adding New Functionality
1. Follow existing patterns for page creation
2. Maintain consistent error handling with `call_lucy_api()`
3. Use Streamlit session state for caching and preferences
4. Follow OpenAPI integration pattern for endpoint discovery
5. Keep UI consistent with existing pages
6. Add appropriate directory structure for new file types

### Error Handling
- Use `call_lucy_api()` for consistent error responses
- Handle API errors with detailed status codes and messages
- Add file-specific error handling when needed (e.g., PDF errors)
- Verify API connectivity with clear error messages

### OpenAPI Integration
- Fetch specifications from `/openapi.json`
- Dynamically discover endpoints with common prefixes
- Create user-friendly names from endpoint paths
- Use for both UI display and endpoint validation
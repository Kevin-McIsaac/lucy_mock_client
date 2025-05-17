# Lucy AI MCP (Model Context Protocol) Configuration

This directory contains the MCP configuration for integrating with Lucy AI server.

## Files

- `lucy_ai.json` - MCP tool definitions and configuration
- `config.json` - MCP server configuration for Claude
- `mcp_lucy_ai.py` - Python implementation of the MCP server
- `README.md` - This documentation

## Setup

1. Ensure your `.env` file contains:
   ```
   API_ENDPOINT=http://localhost:8000
   API_KEY=your-api-key-here
   ```

2. Register the MCP server with Claude:
   ```bash
   claude mcp add /path/to/lucy_mock_client/mcp/config.json
   ```

3. The MCP server will be available in Claude with the following tools:
   - `lucy_ai.status` - Check server status
   - `lucy_ai.transcript_to_summary` - Generate meeting summaries
   - `lucy_ai.game_plan_review` - Review game plans
   - `lucy_ai.get_template` - Retrieve templates
   - `lucy_ai.update_template` - Update templates

## Available Tools

### status
Check if Lucy AI server is online and responsive.

### transcript_to_summary
Generate a meeting summary from a transcript.
- Parameters:
  - `transcript` (string): The meeting transcript text
  - `model_slug` (string): AI model identifier (e.g., "claude-3.7-sonnet")

### game_plan_review
Review a game plan for compliance issues.
- Parameters:
  - `game_plan` (string): The game plan text
  - `model_slug` (string): AI model identifier

### get_template
Retrieve a template for summaries or reviews.
- Parameters:
  - `template_type` (string): Either "meeting_summary" or "game_plan_review"

### update_template
Update a template.
- Parameters:
  - `template_type` (string): Either "meeting_summary" or "game_plan_review"
  - `template` (string): New template content

## Model IDs

Available model slugs:
- `claude-3.7-sonnet`
- `claude-3.5-haiku`
- `gpt-4.1`
- `gpt-4.1-mini`
- `gemini-2.0-flash`
- `gemini-2.5-flash-preview`
- `llama-4-maverick`
- `llama-4-scout`
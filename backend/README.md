# RepoLens Backend

A simplified FastAPI backend that provides AI-powered code analysis capabilities.

## Architecture

This backend now focuses solely on AI analysis features, while code parsing and repository analysis are handled by the [RepoLens Agent](../repolens-agent) - a high-performance Rust-based binary.

## Features

- **AI Code Analysis**: Analyze codebases using OpenAI's GPT models
- **Function Analysis**: Get AI insights on specific functions
- **Codebase Q&A**: Ask questions about your codebase
- **Caching**: Intelligent caching of AI analysis results

## API Endpoints

### AI Analysis

- `POST /ai/analyze` - Analyze entire codebase
- `POST /ai/analyze-function` - Analyze specific function
- `POST /ai/ask` - Ask questions about codebase
- `GET /ai/status` - Get AI service status
- `GET /ai/cache/stats` - Get cache statistics
- `POST /ai/cache/clear` - Clear analysis cache

## Setup

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Set environment variables:

   ```bash
   export OPENAI_API_KEY="your-openai-api-key"
   export OPENAI_MODEL="gpt-4"  # Optional, defaults to gpt-4
   ```

3. Run the server:
   ```bash
   uvicorn app.main:app --reload
   ```

## Dependencies Removed

The following components were removed as they're now handled by the Rust agent:

- Tree-sitter parsing logic
- Git repository cloning
- File system operations for code analysis
- Repository structure parsing
- Code dependency analysis

## Integration

This backend works in conjunction with:

- **RepoLens Agent**: Handles all code parsing and repository analysis
- **RepoLens Frontend**: Provides the user interface

The frontend communicates with the agent for repository operations and this backend for AI analysis.

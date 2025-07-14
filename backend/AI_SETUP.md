# AI Analysis Setup Guide

## Prerequisites

1. **OpenAI API Key**: You need an OpenAI API key to use the AI analysis features.
   - Sign up at [OpenAI](https://platform.openai.com/)
   - Create an API key in your dashboard
   - The AI analysis uses GPT-4 by default

## Configuration

Create a `.env` file in the backend directory with the following variables:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4

# AI Analysis Configuration
AI_ANALYSIS_ENABLED=true
AI_MAX_TOKENS=4000
AI_TEMPERATURE=0.1

# Application Configuration
DEBUG=false
LOG_LEVEL=INFO
```

## Installation

1. Install the new dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Start the backend server:
   ```bash
   python -m uvicorn app.main:app --reload
   ```

## Features

The AI Analysis provides:

### 📊 **Overview Dashboard**

- Overall code quality score (1-10)
- Individual scores for:
  - Complexity
  - Security
  - Maintainability
  - Architecture
  - Code Quality

### 🔍 **Detailed Analysis**

- Comprehensive analysis of each aspect
- AI-generated insights and recommendations
- Code structure evaluation

### 🛡️ **Security & Vulnerabilities**

- Security assessment
- Vulnerability detection
- Risk analysis
- Security recommendations

### ⚠️ **Issues & Recommendations**

- Code smells identification
- Anti-patterns detection
- Refactoring suggestions
- Best practices recommendations

## API Endpoints

- `POST /ai/analyze` - Analyze entire codebase
- `POST /ai/analyze-function` - Analyze specific function
- `GET /ai/status` - Check AI service status

## Usage

1. Start the application
2. Upload a repository
3. Switch to "🤖 AI Analysis" tab
4. View comprehensive AI-powered insights

## Troubleshooting

### AI Analysis Disabled

- Check that `OPENAI_API_KEY` is set correctly
- Verify the API key is valid and has credits
- Ensure `AI_ANALYSIS_ENABLED=true`

### Analysis Fails

- Check OpenAI API rate limits
- Verify network connectivity
- Check backend logs for detailed error messages

### Performance Issues

- Reduce `AI_MAX_TOKENS` for faster analysis
- Use `gpt-3.5-turbo` instead of `gpt-4` for cost savings
- Increase `AI_TEMPERATURE` for more creative analysis

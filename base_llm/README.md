# Base LLM Module

This module provides a unified interface for integrating Large Language Models (LLMs) with Odoo.

## Features

- **Multi-provider support**: Groq, OpenAI, Anthropic, and custom providers
- **Unified API**: Single interface for all LLM providers
- **Secure configuration**: API keys stored securely
- **Connection testing**: Built-in test functionality
- **Company-specific**: Support for multi-company environments

## Supported Providers

### Groq
- Fast inference with LPU technology
- Cost-effective solution
- Multiple model options

### OpenAI
- GPT models support
- Industry standard API
- High-quality responses

### Anthropic
- Claude models support
- Advanced reasoning capabilities
- Safety-focused AI

## Installation

1. Install the module through Odoo Apps
2. Configure your LLM provider in Settings > LLM > LLM Providers
3. Add your API key and test the connection

## Configuration

### Basic Configuration
1. Go to **LLM > Configuration > LLM Providers**
2. Create a new provider or edit the default one
3. Fill in the required fields:
   - **Name**: Display name for the provider
   - **Provider Type**: Select your LLM provider
   - **API Key**: Your provider's API key
   - **Model Name**: The model to use

### Advanced Configuration
- **Endpoint**: Custom API endpoint (auto-filled for known providers)
- **Max Tokens**: Maximum tokens per request
- **Temperature**: Response creativity (0.0 = deterministic, 1.0 = creative)

## Usage

The module provides a `process_prompt()` method that can be used by other modules:

```python
# Get the default LLM provider
llm_provider = self.env['llm.provider'].get_default_provider()

# Process a prompt
result = llm_provider.process_prompt(
    "Your prompt here",
    max_tokens=1000,
    temperature=0.1,
    response_format={"type": "json_object"}  # Optional
)

if result.get('success'):
    content = result['content']
else:
    error = result['error']
```

## Dependencies

- **Python packages**: `requests`
- **Odoo modules**: `base`, `mail`

## Security

- API keys are stored securely in Odoo
- Only authorized users can access LLM configuration
- Connection testing validates credentials safely

## Troubleshooting

### Common Issues

1. **Connection Failed**
   - Verify your API key is correct
   - Check your internet connection
   - Ensure the endpoint URL is correct

2. **Invalid Response**
   - Check if you have sufficient credits/quota
   - Verify the model name is correct
   - Review the request parameters

3. **Permission Denied**
   - Ensure you have the correct access rights
   - Contact your system administrator

## Support

For support and bug reports, please contact your system administrator or the module maintainer.
# GitHub Copilot Project Guidelines

## Security
- **Never** share `.env` contents or secrets with Copilot
- Use environment variables: `os.getenv('VARIABLE_NAME')`
- Do not paste API keys, passwords, tokens, or connection strings in prompts

## Code Standards
- PEP 8 formatting
- Type hints for functions
- Unit tests for new features


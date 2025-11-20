# GitHub Copilot Quick Start

## Getting Access

GitHub Copilot is available for free via GitHub Education benefits. Check your eligibility at:
**https://github.com/settings/education/benefits**

## Installation

### PyCharm
1. Open Preferences (Cmd+,)
2. Go to Plugins
3. Search "GitHub Copilot" and click Install
4. Restart PyCharm
5. Tools → GitHub Copilot → Sign in (GitHub browser login)

### VS Code
1. Open Extensions marketplace
2. Search "GitHub Copilot" and click Install
3. Command Palette (Cmd+Shift+P) → "GitHub Copilot: Sign in"
4. Complete GitHub browser login

## Usage

- Write code → Press **Tab** for inline suggestions
- Press **Cmd+Shift+A** to open Chat

## Best Practices

✅ **Do's**
- Always review code before committing
- Generate and run tests locally
- Ask specific questions: "Write unit tests for function X"

❌ **Don'ts**
- **NEVER paste `.env` contents, API keys, tokens, or passwords**
- **NEVER share connection strings or credentials**
- Don't blindly accept suggestions
- Don't share any sensitive data

## Common Prompts

**Generate Unit Tests**
```
"Generate unit tests for the calculate_discount function"
```

**Refactor Code**
```
"Refactor this code to follow PEP 8 and add type hints"
```

**Add Documentation**
```
"Generate a Google-style docstring for this function"
```

## Loading Secrets Correctly

```python
# ✅ CORRECT
import os
api_key = os.getenv('AZURE_OPENAI_API_KEY')
endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
db_connection = os.getenv('DATABASE_CONNECTION_STRING')

# ❌ WRONG - Never do this
# Don't paste: API_KEY = 'a308bd28adc946938b358796f11c44c6'
# Don't paste: postgresql+pg8000://postgres:password@localhost:5432/...
# Don't share: SLACK_WEBHOOK_URL values
```

## Tips for Better Results

- Ask specific questions instead of generic ones
- Let Copilot follow your existing code style
- Use smaller prompts instead of large ones


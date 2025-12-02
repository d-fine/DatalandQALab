# General Rules
- **Security:** Never output secrets, API keys, or real credentials. Always imply the use of environment variables (e.g., `os.getenv` or `.env` files).

# Python Development
- **Style:** Strictly follow **PEP 8** standards for code formatting.
- **Testing:** When generating or running tests, always use `pdm run pytest`.

# 🤖 GitHub Copilot Developer Guide

This guide provides a quick start, best practices, and security rules for using GitHub Copilot in our project.

## 1. Access & Setup

### Prerequisites
Ensure you have an active GitHub Copilot subscription.
- **Students/Education:** [Get access via GitHub Education](https://github.com/settings/education/benefits)

### IDE Configuration

| IDE | Installation Steps |
| :--- | :--- |
| **PyCharm** | 1. Go to `Settings` → `Plugins`<br>2. Install **"GitHub Copilot"**<br>3. Restart IDE<br>4. Click the Copilot icon (bottom right or sidebar) to sign in. |
| **VS Code** | 1. Open Extensions (`Cmd+Shift+X`)<br>2. Install **"GitHub Copilot"**<br>3. Follow the prompt to sign in via GitHub. |

---

## 2. How to Use

### 👻 Ghost Text (Inline Suggestions)
As you type in the editor, Copilot suggests code in gray text.
- **Accept:** Press `Tab`
- **Partial Accept:** Press `Cmd + →` (Mac) or `Ctrl + →` (Win) to accept word-by-word.
- **Reject:** Press `Esc` or keep typing.

### 💬 Copilot Chat (The Assistant)
Use the chat for explanations, refactoring, or generating logic.
- **VS Code:** Press `Cmd + I` (Mac) / `Ctrl + I` (Win) for Inline Chat, or open the Sidebar.
- **PyCharm:** Open the "GitHub Copilot" tool window.

---

## 3. 🛡️ Security & Privacy (CRITICAL)

> ⚠️ **WARNING:** Copilot snippets are processed in the cloud. Never expose sensitive data in your code or chat prompts.

### ❌ ABSOLUTE DON'TS
- **NEVER** paste real **API Keys, Passwords, or Tokens** into the chat.
- **NEVER** paste real **Database Connection Strings** (even if local).
- **NEVER** paste customer PII (Personally Identifiable Information).

### ✅ CORRECT WAY: Secrets Handling
Always reference environment variables. Copilot understands this pattern.


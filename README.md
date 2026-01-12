# Healing Space 🌿

A mental health companion desktop application with AI therapy, mood tracking, CBT tools, and gamification features.

## Features

- 🤖 **AI Therapy Sessions** - Talk to an AI therapist with persistent memory
- 📊 **Mood Tracking** - Log mood, sleep, medications, and activities
- 🧠 **CBT Tools** - Cognitive Behavioral Therapy exercises and thought records
- 📈 **Progress Insights** - Clinical scales (PHQ-9), data visualization, and progress reports
- 🐾 **Pet Companion** - Gamified self-care with a virtual pet that reflects your wellbeing
- 🔒 **Privacy & Security** - End-to-end encryption, local SQLite storage
- 📋 **FHIR Export** - Export medical data in standardized FHIR format
- 🚨 **Crisis Detection** - Safety monitoring with automatic alerts

## Architecture

- **Desktop GUI**: Python with Tkinter + CustomTkinter
- **Database**: SQLite (local storage)
- **AI Integration**: Groq API (LLM)
- **Security**: Fernet encryption, Argon2/bcrypt password hashing
- **Optional Integrations**: HashiCorp Vault, SFTP, webhooks

## Quick Start

### Prerequisites

- Python 3.8+
- pip package manager

### Installation

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd python-chat-bot
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your keys
   ```

4. **Generate encryption keys**:
   ```bash
   # Generate ENCRYPTION_KEY
   python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   
   # Generate PIN_SALT
   python3 -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

5. **Run the application**:
   ```bash
   export DEBUG=1
   export PIN_SALT=your_generated_salt
   export ENCRYPTION_KEY=your_generated_key
   export GROQ_API_KEY=your_groq_key
   python3 main.py
   ```

## Development

### Project Structure

```
.
├── main.py                 # Main application entry point
├── pet_game.py            # Gamification module
├── secrets_manager.py     # Vault/environment secret handling
├── fhir_export.py         # FHIR medical data export
├── secure_transfer.py     # SFTP upload helper
├── audit.py               # Audit logging
├── tests/
│   └── test_app.py       # Unit tests
├── backups/               # Auto-generated DB backups
└── .github/
    └── copilot-instructions.md  # Developer guide
```

### Running Tests

```bash
pip install pytest
export DEBUG=1
export PIN_SALT=testsalt
export ENCRYPTION_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
pytest -v
```

### Key Concepts

- **Password Hashing**: Argon2 (preferred) → bcrypt → PBKDF2 fallback
- **Optional Dependencies**: Code gracefully handles missing packages (argon2, bcrypt, paramiko, hvac)
- **Debug Mode**: `DEBUG=1` enables permissive fallbacks for development
- **UI Patches**: CustomTkinter is monkeypatched for better UX (topmost windows, Escape to close)

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions on:
- GitHub repository setup
- Railway deployment (web conversion needed)
- Environment variable configuration
- Database persistence strategies
- Desktop distribution with PyInstaller

**Note**: This is a desktop GUI application. For cloud deployment, consider converting to a web app or distributing executables via GitHub Releases.

## Configuration

### Required Environment Variables

- `GROQ_API_KEY` - API key for Groq LLM
- `ENCRYPTION_KEY` - Fernet key for data encryption
- `PIN_SALT` - Salt for PIN hashing

### Optional Environment Variables

- `DEBUG` - Set to `1` for development mode
- `VAULT_ADDR` - HashiCorp Vault address
- `VAULT_TOKEN` - Vault authentication token
- `SFTP_HOST` - SFTP server for exports
- `ALERT_WEBHOOK_URL` - Webhook for crisis alerts

## Security

- All user data encrypted at rest with Fernet
- Passwords hashed with Argon2 (or bcrypt/PBKDF2 fallback)
- Automatic migration of legacy password hashes
- Best-effort audit logging
- Crisis detection with automatic escalation
- HMAC-signed FHIR exports

## Contributing

1. Read `.github/copilot-instructions.md` for architecture overview
2. Run tests before submitting PRs
3. Follow existing patterns for optional dependencies
4. Add audit logs for sensitive operations
5. Update tests for new features

## License

[Add your license here]

## Support

For development questions, see:
- [.github/copilot-instructions.md](.github/copilot-instructions.md) - Developer guide
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment guide
- [tests/test_app.py](tests/test_app.py) - Code examples

## Disclaimer

This application is designed as a mental health companion tool and should not replace professional medical care. If you are experiencing a mental health crisis, please contact emergency services or a crisis helpline immediately.

# Changelog

All notable changes to the MemeBot project will be documented in this file.

## [Unreleased]

## [0.0.1] 2025-07-15

**Initial release** of MemeBot maubot plugin

### 🚀 Core Functionality
1. Image promotion via `!promote` and `!p` commands
2. Command validation
3. Image upload to external server via HTTP POST
4. Success emoji reaction

### 🏗️ Architecture and Code Quality
- **Modular Architecture:** Mixin-based design with separation of concerns
  - `CommandMixin` for command parsing and validation
  - `ImageMixin` for image download and processing
  - `CooldownMixin` for spam protection and rate limiting
  - `ServerMixin` for external API communication
  - Type-safe protocols in `mixins/types.py`
- **Code Standards:**
  - 100-character line length with Black formatting
  - Full type annotations using modern Python syntax (3.10+)
  - Comprehensive error handling and logging
  - Clean separation of business logic and infrastructure

### 🔒 Security
- **Authentication:** API token-based authentication for external server
- **Validation:** 
  - File size validation to prevent DoS attacks
  - Image format validation for security
  - Input sanitization and validation
- **Encryption:** Full support for encrypted Matrix rooms

### ⚙️ Configuration
- Default configuration template in `base-config.yaml`
  - Toggle `auto_join`
  - Configurable promotion commands (default `!promote` and `!p`)
  - Customizable server URL and API token
  - Customizable cooldown settings (global and per-user)
  - File size limits and format validation
  - Toggle if the bot should reply in a thread
  - The default config user-facing messages (defaults in German)
- Automatic validation with detailed error reporting

### 🛠️ Development Tools
- Build and deployment automation script (`maubot-dev.py`)
- Instance management and monitoring tools (`maubot-api.py`)

---

[0.0.1]: https://github.com/olivierlacan/keep-a-changelog/releases/tag/v0.0.1
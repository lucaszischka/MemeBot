# MemeBot Development Guide

This guide covers development setup, building, testing, and contributing to the MemeBot project.

## 📑 Table of Contents

- [MemeBot Development Guide](#memebot-development-guide)
  - [📑 Table of Contents](#-table-of-contents)
  - [📊 Technical Specification](#-technical-specification)
  - [🏗️ Architecture](#️-architecture)
  - [📏 Code Standards](#-code-standards)
  - [📝 Contributing](#-contributing)
  - [🛠️ Development Setup](#️-development-setup)
    - [📋 Prerequisites](#-prerequisites)
    - [🚀 Setup Steps](#-setup-steps)
  - [🏗️ Building](#️-building)
  - [⚙️ Commands \& Testing](#️-commands--testing)
    - [🔧 Development (`maubot-dev.py`)](#-development-maubot-devpy)
    - [🌐 Instance Management (`maubot-api.py`)](#-instance-management-maubot-apipy)
    - [💡 Testing Tips](#-testing-tips)
    - [⚠️ Common Issues](#️-common-issues)
  - [📋 Changelog Guidelines](#-changelog-guidelines)

## 📊 Technical Specification

- **Minimum Python Version**: 3.10+
- **Framework**: [Maubot](https://docs.mau.fi/maubot/) with [mautrix-python](https://github.com/mautrix/python)
- **Image Processing**: PIL-based with format validation
- **HTTP Client**: aiohttp for async server communication
- **Configuration**: YAML-based with validation code
- **Logging**: Comprehensive logging with configurable levels

## 🏗️ Architecture

The plugin is built with a modular mixin-based architecture for maintainability and extensibility:
- **`CommandMixin`**: Handles command parsing and validation
- **`ImageMixin`**: Manages image downloading and processing
- **`CooldownMixin`**: Implements spam protection with user and global cooldowns
- **`ServerMixin`**: Handles communication with the promotion server
- **`MixinHost`**: Base class defining the interface for type safety

```
MemeBot/
├── __init__.py           # Main plugin class
├── config.py             # Configuration management and validation
└── mixins/               # Modular functionality
    ├── __init__.py
    ├── command_mixin.py  # Command parsing and validation
    ├── cooldown_mixin.py # Spam protection
    ├── image_mixin.py    # Image download and processing
    ├── server_mixin.py   # External server communication
    └── types.py          # Defines the MixinHost interface for type safety
```

## 📏 Code Standards

- **Style**: Black formatting (100 characters), isort imports
- **Type Safety**: Full type annotations using modern Python syntax and `MixinHost`
- **Naming**: PascalCase classes, snake_case functions, UPPER_SNAKE_CASE constants
- **Error Handling**: Explicit error handling with proper logging
- **Architecture**: Follow mixin separation patterns

## 📝 Contributing

1. **Fork the repository** and create a feature branch
2. **Set up development environment** following the setup guide above
3. **Make your changes** following the code standards below
   1. Identify the appropriate mixin
   2. Update configuration (`base-config.yaml`) and validation (`config.py`)
   3. Add type annotations
   4. Update documentation in README.md and CHANGELOG.md
4. **Test thoroughly** using the debugging tools
5. **Submit a pull request** with a clear description

## 🛠️ Development Setup

### 📋 Prerequisites

- Python 3.10 or higher
- [uv](https://docs.astral.sh/uv/) package manager (recommended)
- [Maubot](https://github.com/maubot/maubot) server instance for testing
- Matrix account for the bot

### 🚀 Setup Steps

```bash
# 1. Clone the repository
git clone https://github.com/lucaszischka/MemeBot.git
cd MemeBot

# 2. Setup dependencies and environment
./maubot-dev.py setup

# 3. Authenticate with your maubot server
.venv/bin/python -m maubot.cli login --server "https://your-maubot-server.example.com"
# Example: .venv/bin/python -m maubot.cli login --server "https://conduit-test.fs-info.de"
```

## 🏗️ Building

```bash
# Build plugin package (creates .mbp file)
./maubot-dev.py build

# Upload to maubot server (or via Web UI)
./maubot-dev.py upload

# Build and upload in one step
./maubot-dev.py build-upload

# Full deployment with Maubot instance update (or via Web UI)
./maubot-dev.py deploy -i <instance-id>
```

In the **Maubot Web-UI** you can *upload* the build plugin, *configure instances* and *monitor logs*.

## ⚙️ Commands & Testing

> ⚠️ **LLM Warning**: Please note that `maubot-dev.py` and `maubot-api.py` are LLM generated and i haven't read most of the code, but it seems to work.

### 🔧 Development (`maubot-dev.py`)

| Command | Purpose | Details |
|---------|---------|---------|
| `./maubot-dev.py setup` | Initialize development environment | Sets up dependencies with UV or pip |
| `./maubot-dev.py build` | Build plugin package | Creates `.mbp` file and moves to builds/ |
| `./maubot-dev.py upload` | Upload existing build to server | Uploads latest `.mbp` file to maubot |
| `./maubot-dev.py build-upload` | Build and upload in one step | Combines build + upload + verification |
| `./maubot-dev.py deploy -i <id>` | Full deployment to instance | Build, upload, and update specific instance |
| `./maubot-dev.py status` | Comprehensive health check | Checks version, builds, tools, git, server |

### 🌐 Instance Management (`maubot-api.py`)

| Command | Purpose | Details |
|---------|---------|---------|
| `./maubot-api.py status` | Quick server status summary | Shows running/stopped/disabled instance counts |
| `./maubot-api.py list` | List all plugins and instances | YAML-formatted overview with status icons |
| `./maubot-api.py instances` | Detailed instance information | Full configuration and database details |
| `./maubot-api.py config <id>` | Show instance configuration | Display YAML config with syntax highlighting |
| `./maubot-api.py enable <id>` | Enable an instance | Activates instance without starting |
| `./maubot-api.py disable <id>` | Disable an instance | Deactivates and stops instance |
| `./maubot-api.py delete <id>` | Delete an instance | Permanently removes instance (with confirmation) |
| `./maubot-api.py update <id> <plugin>` | Update instance plugin type | Changes instance to use different plugin |

### 💡 Testing Tips

1. **Create a test room** and invite your bot
2. **Test with different image formats** (PNG, JPEG, GIF, WEBP)
3. **Monitor Maubot Web UI logs** for real-time feedback
4. **Test error scenarios** (large files, invalid formats)

### ⚠️ Common Issues

| Problem | Solution |
|---------|----------|
| **Build failures** | • Run `./maubot-dev.py status` for diagnostics<br>• Ensure dependencies: `uv sync --dev`<br>• Check Python version compatibility (≥3.10) |
| **Import errors** | • Check Python 3.10+<br>• Run `uv sync --dev`<br>• Restart language server |
| **Runtime errors** | • Check maubot logs<br>• Validate config<br>• Test mixins individually |
| **Connection issues** | • Verify URLs/tokens<br>• Check network/firewall/VPN |

## 📋 Changelog Guidelines

1. **Keep entries in reverse chronological order** (newest first)
2. **Update the [Unreleased] section** during development
3. **Include release dates** in ISO format (`YYYY-MM-DD`)
4. **Reference issue/PR numbers** when applicable (e.g., `(#123)`)
5. **Include relevant technical details**
6. **Follow semantic versioning** (MAJOR.MINOR.PATCH)
7. **Use standard categories** (🎉 Added, 🔄 Changed, ⚠️ Deprecated, 🗑️ Removed, 🐛 Fixed, 🔒 Security)

**Example Entry:**
```markdown
## [1.2.0] - 2025-07-15

### 🎉 Added
- **Multi-language support:** Added English and French translations (#42)
- **Image transformations:** Resize and format conversion options (#45)

### 🔄 Changed
- **Performance improvement:** Reduced image processing time by 40% (#48)
- **Configuration:** Simplified setup process for new users (#50)

### 🐛 Fixed
- **Encryption bug:** Fixed issue with E2E encrypted rooms (#47)
```

---

For user documentation and installation instructions, see [README.md](README.md).
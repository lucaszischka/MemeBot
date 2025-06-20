# MemeBot Maubot Plugin

A powerful Maubot plugin that promotes images to external servers when commanded in Matrix rooms. Simply reply to any image with `!promote` or `!p` to forward it to your configured promotion server.

[![Version](https://img.shields.io/badge/version-0.0.1-blue.svg)](CHANGELOG.md)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)

## 📑 Table of Contents

- [MemeBot Maubot Plugin](#memebot-maubot-plugin)
  - [📑 Table of Contents](#-table-of-contents)
  - [🚀 Features](#-features)
  - [🎯 Usage](#-usage)
    - [Basic Usage](#basic-usage)
    - [Example Workflow](#example-workflow)
  - [📦 Installation \& Setup](#-installation--setup)
    - [Prerequisites](#prerequisites)
    - [Installation Steps](#installation-steps)
  - [⚙️ Configuration](#️-configuration)
    - [🌐 Server API Requirements](#-server-api-requirements)
  - [🔍 Troubleshooting](#-troubleshooting)
    - [Common Issues](#common-issues)
  - [🔧 Development \& Contributing](#-development--contributing)
  - [📄 License](#-license)
  - [📋 Changelog](#-changelog)

## 🚀 Features

- 🖼️ **Image Promotion**: Reply to images with promotion commands to send them to an external server
- 🔐 **E2E Encryption Support**: Works seamlessly with both encrypted and unencrypted Matrix rooms
- 🤖 **Auto-join**: Automatically joins rooms when invited (configurable)
- ⏱️ **Smart Cooldowns**: User-specific and global cooldowns to prevent spam
- 🎛️ **Flexible Configuration**: Fully customizable commands, messages, and server settings
- 🏞️ **Image Validation**: File size limits and format restrictions (PNG, JPEG, GIF, WEBP)
- 🎉 **Random Success Reactions**: Bot celebrates successful promotions with random emoji reactions
- 🎨 **Modular Architecture**: Clean separation of concerns with mixins for different functionalities
- 🛡️ **Security**: API token authentication, file validation, and proper encryption handling

## 🎯 Usage

### Basic Usage

1. **Invite the bot**: Invite MemeBot to your Matrix room
2. **Reply to images**: Reply to any image message with `!promote` or `!p`
3. **Automatic processing**: The bot will download, validate, and forward the image to your configured server

### Example Workflow

```
[User uploads image] 
    ↓
[Another user replies with "!promote"]
    ↓ 
[Bot validates image and cooldowns]
    ↓
[Bot forwards image to promotion server] → [Promotion server displays image]
    ↓
[Bot reacts with success emoji]
```

## 📦 Installation & Setup

### Prerequisites

- A running [Maubot](https://github.com/maubot/maubot) server
- Matrix account for the bot
- External server to receive promoted images

### Installation Steps

1. **Download** the latest `.mbp` file from the [releases page](https://github.com/lucaszischka/MemeBot/releases) or [build from source](DEVELOPMENT.md)
2. **Upload** the plugin file to your Maubot server via the web interface
3. **Create a new instance** with your bot's Matrix credentials
4. **Configure** the plugin settings (see configuration section below)
5. **Invite the bot** to your Matrix rooms and start promoting images!

## ⚙️ Configuration

Configure the plugin through your Maubot web interface:

| Setting | Description | Default | Required |
|---------|-------------|---------|----------|
| `auto_join` | Automatically join rooms when invited | `true` | Yes |
| `commands` | Available promotion commands | `["!promote", "!p"]` | Yes |
| `promotion.server_url` | Target server for image uploads | - | Yes |
| `promotion.api_token` | Authentication token for server | - | No (`""`) |
| `cooldowns.global` | Global cooldown between any promotions (seconds) | `60` | No (`0`) |
| `cooldowns.user` | Per-user cooldown between promotions (seconds) | `90` | No (`0`) |
| `image.maximum_file_size_bytes` | Maximum image file size | `10485760` (10MB) | Yes |
| `image.allowed_image_formats` | Supported image formats | `["PNG", "JPEG", "JPG", "GIF", "WEBP"]` | Yes |
| `messages.reply_in_thread` | Bot replies in threads vs. main chat | `true` | Yes |

> 📝 **Note**: All user-facing messages are in German and can be fully customized in the configuration.

> ⚠️ **Security Warning**: If your promotion server is publicly accessible on the internet, always configure an API token! Without authentication, anyone could spam your server with images. 🌍🔓

For complete configuration options and their default values, see [`base-config.yaml`](base-config.yaml).

### 🌐 Server API Requirements

Your promotion server should accept HTTP POST requests with the following specification:

```
POST {promotion.server_url} # Config value
Content-Type: multipart/form-data
Authorization: Bearer {promotion.api_token} # Config value

Body:
- image: [binary image data]
- filename: [original filename or "meme" if not available]
- content_type: application/octet-stream
```

**Expected Response:**
- `200 OK`: Image successfully processed
- `4xx/5xx`: Error (bot will report failure to user)

## 🔍 Troubleshooting

### Common Issues

| Problem | Solution |
|---------|----------|
| **Plugin not responding** | • Check instance status in Maubot web interface<br>• Verify bot has proper room permissions<br>• Check maubot server logs |
| **Encryption issues** | • Test with unencrypted images first<br>• Ensure bot has access to room keys<br>• Check encryption setup in maubot |
| **Auto-join not working** | • Verify `auto_join: true` in configuration<br>• Check bot's Matrix account permissions<br>• Review server logs for join attempts |
| **Images not uploading** | • Verify promotion server URL and API token<br>• Check server logs for connection errors<br>• Test server endpoint manually |

For development and debugging tools, see [DEVELOPMENT.md](DEVELOPMENT.md).

## 🔧 Development & Contributing

This project welcomes contributions! For development setup, building from source, and contribution guidelines, please see [DEVELOPMENT.md](DEVELOPMENT.md).

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📋 Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed history of changes and releases.

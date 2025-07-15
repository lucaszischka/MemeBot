from __future__ import annotations

# Mautrix imports
from mautrix.util.config import BaseProxyConfig, ConfigUpdateHelper


class Config(BaseProxyConfig):
    """Configuration class with enhanced validation."""
    
    # Constants for validation
    REQUIRED_MESSAGES: tuple[str, ...] = (
        "missing_promotion_target", "missing_replied_message", "encrypted_image_url_missing",
        "encrypted_image_decrypt_failed", "image_download_failed", "image_missing", 
        "image_size_exceeded", "image_format_unsupported", "image_format_invalid",
        "promotion_server_error", "global_cooldown_message", "user_cooldown_message"
    )
    
    REQUIRED_TIME_FORMATS: tuple[str, ...] = (
        "minutes_only_format", "seconds_only_format", "minutes_and_seconds_format"
    )
    
    
    def do_update(self, helper: ConfigUpdateHelper) -> None:
        """Update configuration with all required fields."""
        for field in ("auto_join", "commands", "cooldowns", "promotion", "image", "messages"):
            helper.copy(field)
        
    def check_config_values(self) -> list[str]:
        """
        Validate all configuration values and return a list of invalid configurations.
        
        Returns:
            List of strings describing invalid configuration values.
            If the list is empty, the configuration is valid.
        """
        invalid_configs = []
        
        # Validate auto_join (boolean)
        if not isinstance(self["auto_join"], bool):
            invalid_configs.append("auto_join must be a boolean value (true or false)")
        
        # Validate commands (list of strings)
        if not isinstance(self["commands"], list) or not all(isinstance(cmd, str) for cmd in self["commands"]):
            invalid_configs.append("commands must be a list of strings")
        elif not self["commands"]:
            invalid_configs.append("at least one command must be defined")

        # Validate promotion settings
        if not isinstance(self["promotion"], dict):
            invalid_configs.append("promotion settings must be a dictionary")
        else:
            # Validate server_url (non-empty string)
            if "server_url" not in self["promotion"]:
                invalid_configs.append("promotion.server_url is required")
            elif not isinstance(self["promotion"]["server_url"], str) or not self["promotion"]["server_url"].strip():
                invalid_configs.append("promotion.server_url must be a non-empty string")
            
            # Validate api_token (non-empty string)
            if "api_token" not in self["promotion"]:
                invalid_configs.append("promotion.api_token is required")
            elif not isinstance(self["promotion"]["api_token"], str):
                invalid_configs.append("promotion.api_token must be a string")
        
        # Validate cooldown settings
        if not isinstance(self["cooldowns"], dict):
            invalid_configs.append("cooldowns settings must be a dictionary")
        else:
            # Validate global cooldown (positive number)
            if "global" not in self["cooldowns"]:
                invalid_configs.append("cooldowns.global is required")
            elif not isinstance(self["cooldowns"]["global"], (int, float)) or self["cooldowns"]["global"] < 0:
                invalid_configs.append("cooldowns.global must be a positive number")
                
            # Validate user cooldown (positive number)
            if "user" not in self["cooldowns"]:
                invalid_configs.append("cooldowns.user is required")
            elif not isinstance(self["cooldowns"]["user"], (int, float)) or self["cooldowns"]["user"] < 0:
                invalid_configs.append("cooldowns.user must be a positive number")
        
        # Validate image settings
        if not isinstance(self["image"], dict):
            invalid_configs.append("image settings must be a dictionary")
        else:
            # Validate maximum_file_size_bytes (positive integer)
            if "maximum_file_size_bytes" not in self["image"]:
                invalid_configs.append("image.maximum_file_size_bytes is required")
            elif not isinstance(self["image"]["maximum_file_size_bytes"], int) or self["image"]["maximum_file_size_bytes"] <= 0:
                invalid_configs.append("image.maximum_file_size_bytes must be a positive integer")
                
            # Validate allowed_image_formats (non-empty list of strings)
            if "allowed_image_formats" not in self["image"]:
                invalid_configs.append("image.allowed_image_formats is required")
            elif not isinstance(self["image"]["allowed_image_formats"], list) or not self["image"]["allowed_image_formats"]:
                invalid_configs.append("image.allowed_image_formats must be a non-empty list of strings")
            elif not all(isinstance(fmt, str) for fmt in self["image"]["allowed_image_formats"]):
                invalid_configs.append("image.allowed_image_formats must contain only strings")
        
        # Validate user message settings
        if not isinstance(self["messages"], dict):
            invalid_configs.append("messages settings must be a dictionary")
        else:
            # Validate reply_in_thread (boolean)
            if "reply_in_thread" not in self["messages"]:
                invalid_configs.append("messages.reply_in_thread is required")
            elif not isinstance(self["messages"]["reply_in_thread"], bool):
                invalid_configs.append("messages.reply_in_thread must be a boolean value (true or false)")
            
            # Validate required message templates
            for msg_key in self.REQUIRED_MESSAGES:
                if msg_key not in self["messages"]:
                    invalid_configs.append(f"messages.{msg_key} is required")
                elif not isinstance(self["messages"][msg_key], str):
                    invalid_configs.append(f"messages.{msg_key} must be a string")
            
            # Validate time_display_formats
            if "time_display_formats" not in self["messages"]:
                invalid_configs.append("messages.time_display_formats is required")
            elif not isinstance(self["messages"]["time_display_formats"], dict):
                invalid_configs.append("messages.time_display_formats must be a dictionary")
            else:
                for fmt in self.REQUIRED_TIME_FORMATS:
                    if fmt not in self["messages"]["time_display_formats"]:
                        invalid_configs.append(f"messages.time_display_formats.{fmt} is required")
                    elif not isinstance(self["messages"]["time_display_formats"][fmt], str):
                        invalid_configs.append(f"messages.time_display_formats.{fmt} must be a string")
            
            # Validate success_reaction_emojis
            if "success_reaction_emojis" not in self["messages"]:
                invalid_configs.append("messages.success_reaction_emojis is required")
            elif not isinstance(self["messages"]["success_reaction_emojis"], list) or not self["messages"]["success_reaction_emojis"]:
                invalid_configs.append("messages.success_reaction_emojis must be a non-empty list")
            elif not all(isinstance(emoji, str) for emoji in self["messages"]["success_reaction_emojis"]):
                invalid_configs.append("messages.success_reaction_emojis must contain only strings")
            
            # Validate easter_eggs settings
            if "easter_eggs" not in self["messages"]:
                invalid_configs.append("messages.easter_eggs is required")
            elif not isinstance(self["messages"]["easter_eggs"], dict):
                invalid_configs.append("messages.easter_eggs must be a dictionary")
            else:
                # Validate rare_message_probability
                if "rare_message_probability" not in self["messages"]["easter_eggs"]:
                    invalid_configs.append("messages.easter_eggs.rare_message_probability is required")
                elif not isinstance(self["messages"]["easter_eggs"]["rare_message_probability"], (int, float)):
                    invalid_configs.append("messages.easter_eggs.rare_message_probability must be a number")
                elif not (0.0 <= self["messages"]["easter_eggs"]["rare_message_probability"] <= 1.0):
                    invalid_configs.append("messages.easter_eggs.rare_message_probability must be between 0.0 and 1.0")
                
                # Validate rare_messages
                if "rare_messages" not in self["messages"]["easter_eggs"]:
                    invalid_configs.append("messages.easter_eggs.rare_messages is required")
                elif not isinstance(self["messages"]["easter_eggs"]["rare_messages"], list) or not self["messages"]["easter_eggs"]["rare_messages"]:
                    invalid_configs.append("messages.easter_eggs.rare_messages must be a non-empty list")
                elif not all(isinstance(msg, str) for msg in self["messages"]["easter_eggs"]["rare_messages"]):
                    invalid_configs.append("messages.easter_eggs.rare_messages must contain only strings")
        
        return invalid_configs

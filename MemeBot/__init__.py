from __future__ import annotations

from logging import Logger
import time

# Maubot and Mautrix imports
from maubot.plugin_base import Plugin
from maubot.matrix import MaubotMessageEvent, MaubotMatrixClient
from maubot.handlers import event
from mautrix.types import EventType, StateEvent, MemberStateEventContent
from mautrix.util.config import BaseProxyConfig

# Local imports
from MemeBot.config import Config
from MemeBot.mixins import CommandMixin, ImageMixin, CooldownMixin, ServerMixin


class MemeBot(Plugin, CommandMixin, ImageMixin, CooldownMixin, ServerMixin):
    """
    Matrix bot that promotes images to an external server when users use promotion commands.
    Usage: Reply to an image with !promote or !p, or upload an image with the command as caption.
    """
    PLUGIN_VERSION: str = "v0.0.1"
    DEFAULT_IMAGE_FILENAME: str = "meme"
    
    # Type hints for attributes provided by the maubot framework at runtime
    config: Config
    client: MaubotMatrixClient
    log: Logger
    
    # Plugin state - controls whether functionality is enabled
    _config_valid: bool = True
    
    # Cooldown tracking
    next_global_promotion_time: float = time.time()  # Timestamp when next global promotion is allowed
    user_promotion_cooldowns: dict[str, float] = {}  # User ID -> timestamp when next promotion is allowed for that user

    @classmethod
    def get_config_class(cls) -> type[BaseProxyConfig]:
        return Config
    
    async def start(self) -> None:
        """Initialize the plugin and validate configuration."""
        await super().start()
        self.config.load_and_update()
        
        self.log.info(f"🚀 Starting MemeBot plugin {self.PLUGIN_VERSION}")
        self.log.info(f"📋 Configuration: commands={self.config['commands']}, auto_join={self.config['auto_join']}")
        self.log.info(f"🌐 Promotion server: {self.config['promotion']['server_url']}")
        self.log.info(f"⏱️ Cooldowns: global={self.config['cooldowns']['global']}s, user={self.config['cooldowns']['user']}s")
        self.log.info(f"🖼️ Image settings: max_size={self.config['image']['maximum_file_size_bytes']:,} bytes, formats={self.config['image']['allowed_image_formats']}")
        
        # Validate configuration and disable functionality if invalid
        if self._validate_and_update_config_status():
            self.log.info(f"✅ Successfully started")

    def on_external_config_update(self) -> None:
        """Called when configuration is updated externally via maubot admin interface"""
        super().on_external_config_update()
        # Revalidate configuration when it's updated
        if self._validate_and_update_config_status():
            self.log.info("✅ Configuration validation passed. Plugin functionality is now enabled.")

    async def stop(self) -> None:
        """Clean shutdown with usage statistics."""
        self.log.info(f"🛑 Stopping MemeBot plugin {self.PLUGIN_VERSION}")
        self.log.info(f"📊 Promoted images from {len(self.user_promotion_cooldowns)} unique users")
        self.log.info(f"✅ MemeBot plugin {self.PLUGIN_VERSION} stopped successfully")


    @event.on(EventType.ROOM_MEMBER)  # type: ignore
    async def handle_room_invitation(self, room_member_event: StateEvent) -> None:
        """Auto-join rooms when invited (if enabled in config)."""

        # Ignore events as long as the configuration is invalid
        if not self._config_valid:
            return

        # Only process invites for this bot
        if room_member_event.state_key != self.client.mxid:
            return
            
        # Ensure this is a member state event
        if not isinstance(room_member_event.content, MemberStateEventContent):
            return
            
        # Check if the event is "invite"
        if room_member_event.content.membership != "invite":
            return
        
        self.log.info(f"📩 Room invite received from {room_member_event.sender} for room: {room_member_event.room_id}")

        # Handle the invitation
        if self.config["auto_join"]:
            try:
                await self.client.join_room(room_member_event.room_id)
                self.log.info(f"✅ Bot successfully joined room")
            except Exception as error:
                self.log.error(f"❌ Failed to join room: error: {type(error).__name__}: {error}")
        else:
            self.log.info(f"ℹ️ Auto join is disabled in config. Ignoring invite to room")


    @event.on(EventType.ROOM_MESSAGE)  # type: ignore
    async def handle_message(self, message_event: MaubotMessageEvent) -> None:
        """Main message handler: processes promotion commands and uploads images."""

        # Ignore events as long as the configuration is invalid
        if not self._config_valid:
            return

        # Special response
        if await self._handle_special_responses(message_event):
            return

        # Step 1: Check if the message is a promote command
        if not self._is_promote_command(message_event):
            return
        # Step 2: Get the target image (either from reply or the message itself)
        target_image_message, target_image_event_id = await self._get_target_image_message(message_event)
        if not target_image_message or not target_image_event_id:
            return
        # Step 3: Check cooldowns early to avoid unnecessary image processing
        if not await self._check_cooldowns(message_event):
            return
        # Step 4: Download and decrypt the image if needed
        image_filename: str = getattr(target_image_message.content, 'body', self.DEFAULT_IMAGE_FILENAME)
        if not (image_bytes := await self._download_image(message_event, target_image_message, image_filename)):
            return
        # Step 5: Validate the image
        if not (image_format := await self._validate_image(message_event, image_bytes, image_filename)):
            return
        self.log.info(f"🖼️ Downloaded a valid image: filename='{image_filename}', format={image_format}, size={len(image_bytes):,} bytes")
        # Step 6: Promote the image to the configured server
        if not await self._promote_image(message_event, target_image_event_id, image_filename, image_bytes):
            return
        # Step 7: Update cooldowns
        self._update_cooldowns(message_event.sender)

    def _validate_and_update_config_status(self) -> bool:
        """Check if the configuration is valid and update plugin status."""
        
        if configuration_validation_errors := self.config.check_config_values():
            self._config_valid = False
            self.log.error(f"❌ Invalid configuration detected ({len(configuration_validation_errors)} errors). Plugin functionality disabled.")
            for error_index, validation_error in enumerate(configuration_validation_errors, 1):
                self.log.error(f"Config error #{error_index}: {validation_error}")
            return False
        else:
            self._config_valid = True
            return True
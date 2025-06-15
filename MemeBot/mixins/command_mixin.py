"""
Command processing mixin for MemeBot.
Handles promotion command detection and caching.
"""
from __future__ import annotations

from functools import lru_cache
from maubot.matrix import MaubotMessageEvent
from mautrix.types import MessageType, MessageEvent, EventID
from .types import MixinHost


class CommandMixin(MixinHost):
    """Mixin for command processing functionality."""
    
    @lru_cache(maxsize=1)
    def _get_cached_promote_commands(self) -> tuple[str, ...]:
        """Cache promote commands for performance."""
        return tuple(command.lower() for command in self.config["commands"])

    def _is_promote_command(self, message_event: MaubotMessageEvent) -> bool:
        """Check if message is a valid promotion command."""
        # Ignore bot's own messages to prevent loops
        if message_event.sender == self.client.mxid:
            return False
        # Only process text messages
        if message_event.content.msgtype != MessageType.TEXT:
            return False
        # Get and normalize the message text
        message_text: str = message_event.content.body.strip().lower() if isinstance(message_event.content.body, str) else ""
        # Check if the message is a promote command using cached commands
        return any(message_text.startswith(command) for command in self._get_cached_promote_commands())

    async def _get_replied_message(self, message_event: MaubotMessageEvent) -> tuple[MessageEvent | None, EventID | None]:
        """Check if the message is a reply, get the replied message and check if its an image."""
        # Check if message is a reply
        if not (hasattr(message_event.content, 'relates_to') and 
                hasattr(message_event.content.relates_to, 'in_reply_to') and
                (target_event_id := getattr(message_event.content.relates_to.in_reply_to, 'event_id', None))):
            await message_event.respond(self.config["messages"]["missing_image_reply"], in_thread=self.config["messages"]["reply_in_thread"])
            return None, None
        # Fetch the replied message
        try:
            target_message: MessageEvent = await message_event.client.get_event(message_event.room_id, target_event_id)
            self.log.info(f"✅ Successfully fetched replied message")
        except Exception as error:
            self.log.error(f"❌ Failed to fetch replied message: message_id={target_event_id}, room={message_event.room_id}, user={message_event.sender}: {error}")
            await message_event.respond(self.config["messages"]["missing_replied_message"], in_thread=self.config["messages"]["reply_in_thread"])
            return None, None
        # Verify it's an image
        if target_message.content.msgtype != MessageType.IMAGE:
            await message_event.respond(self.config["messages"]["missing_image_reply"], in_thread=self.config["messages"]["reply_in_thread"])
            return None, None

        return target_message, target_event_id

    @staticmethod
    def _has_reply_content(content: object) -> bool:
        """Type guard to check if message has reply content."""
        return (hasattr(content, 'relates_to') and 
                hasattr(getattr(content, 'relates_to'), 'in_reply_to'))

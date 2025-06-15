"""
Cooldown management mixin for MemeBot.
Handles global and user-specific cooldowns.
"""
from __future__ import annotations

import time
from maubot.matrix import MaubotMessageEvent
from .types import MixinHost


class CooldownMixin(MixinHost):
    """Mixin for cooldown management functionality."""

    async def _check_cooldowns(self, message_event: MaubotMessageEvent) -> bool:
        """Verify both global and user cooldowns before allowing promotion."""
        current_time: float = time.time()
        # Check global cooldown
        if current_time < self.next_global_promotion_time:
            wait_time_seconds: float = self.next_global_promotion_time - current_time
            self.log.info(f"⏱️ Global cooldown for {wait_time_seconds:.1f}s active")
            await self._send_cooldown_message(
                message_event, 
                wait_time_seconds,
                self.config["messages"]["global_cooldown_message"]
            )
            return False
        # Check user cooldown
        user_promotion_cooldown_end: float = self.user_promotion_cooldowns.get(message_event.sender, 0)
        if current_time < user_promotion_cooldown_end:
            wait_time_seconds: float = user_promotion_cooldown_end - current_time
            self.log.info(f"⏱️ User cooldown for {wait_time_seconds:.1f}s active")
            await self._send_cooldown_message(
                message_event,
                wait_time_seconds,
                self.config["messages"]["user_cooldown_message"]
            )
            return False
        
        self.log.info(f"✅ Cooldown check passed")
        return True

    async def _send_cooldown_message(self, message_event: MaubotMessageEvent, wait_time_seconds: float, message_template: str) -> None:
        """Format and send cooldown notification to user."""
        remaining_minutes: int = int(wait_time_seconds // 60)
        remaining_seconds: int = int(wait_time_seconds % 60)
        # Format time display using config templates
        match (remaining_minutes, remaining_seconds):
            case (0, seconds):
                formatted_time: str = self.config["messages"]["time_display_formats"]["seconds_only_format"].format(seconds=seconds)
            case (minutes, 0):
                formatted_time = self.config["messages"]["time_display_formats"]["minutes_only_format"].format(minutes=minutes)
            case (minutes, seconds):
                formatted_time = self.config["messages"]["time_display_formats"]["minutes_and_seconds_format"].format(minutes=minutes, seconds=seconds)
        cooldown_message: str = message_template.format(time=formatted_time)
        await message_event.respond(cooldown_message, in_thread=self.config["messages"]["reply_in_thread"])

    def _update_cooldowns(self, user_id: str) -> None:
        """Update global and user cooldowns after successful promotion."""
        current_timestamp: float = time.time()
        # Calculate new cooldown timestamps
        next_global_promotion_timestamp = current_timestamp + self.config["cooldowns"]["global"]
        next_user_promotion_timestamp = current_timestamp + self.config["cooldowns"]["user"]
        # Update cooldown timestamps
        self.next_global_promotion_time = next_global_promotion_timestamp
        self.user_promotion_cooldowns[user_id] = next_user_promotion_timestamp
        self.log.info(f"⏱️ Cooldowns updated: next_global_promotion={time.strftime('%H:%M:%S', time.localtime(next_global_promotion_timestamp))}, next_user_promotion={time.strftime('%H:%M:%S', time.localtime(next_user_promotion_timestamp))}")

"""
Server communication mixin for MemeBot.
Handles image upload and server interactions.
"""
from __future__ import annotations

import time
import random
import aiohttp
from maubot.matrix import MaubotMessageEvent
from mautrix.types import EventID
from .types import MixinHost


class ServerMixin(MixinHost):
    """Mixin for server communication functionality."""

    async def _promote_image(self, message_event: MaubotMessageEvent, target_image_event_id: EventID, image_filename: str, image_data: bytes) -> bool:
        """Upload image to promotion server and handle response."""
        # Ensure server URL has protocol
        promotion_server: str = self.config["promotion"]["server_url"]
        if not promotion_server.startswith(("http://", "https://")):
            promotion_server = f"http://{promotion_server}"
        # POST image to the configured server
        if await self._upload_image_to_server(image_data, image_filename, promotion_server):
            await self._add_success_reaction(message_event, target_image_event_id)
            return True
        else:
            await message_event.respond(self.config["messages"]["promotion_server_error"], in_thread=self.config["messages"]["reply_in_thread"])
            return False

    async def _upload_image_to_server(self, image_data: bytes, image_filename: str, promotion_server: str) -> bool:
        """POST image to the promotion server via HTTP form upload."""
        try:
            # Prepare headers with API token
            headers = {
                'Authorization': f'Bearer {self.config["promotion"]["api_token"]}'
            }
            
            async with aiohttp.ClientSession(headers=headers) as session:
                # Create the data payload for the POST request
                form_data: aiohttp.FormData = aiohttp.FormData()
                form_data.add_field('image', 
                                image_data,
                                filename=image_filename,
                                content_type='application/octet-stream')
                # Send the POST request to the promotion server
                upload_start_time = time.time()
                async with session.post(promotion_server, data=form_data) as response:
                    upload_time = time.time() - upload_start_time
                    
                    if response.status == 200:
                        self.log.info(f"🚀 Upload successful: server={promotion_server}, upload_time={upload_time:.2f}s, response_status={response.status}")
                        return True
                    else:
                        response_body = await response.text() if response.content_length and response.content_length < 1000 else "Response too large to log"
                        self.log.error(f"❌🌐 Upload failed: server={promotion_server}, upload_time={upload_time:.2f}s, status={response.status}, response='{response_body[:200]}'")
                        return False
        except Exception as error:
            self.log.error(f"❌🌐 Upload error: filename='{image_filename}', server={promotion_server}: {error}")
            return False

    async def _add_success_reaction(self, message_event: MaubotMessageEvent, target_image_event_id: EventID) -> None:
        """Add a random success emoji reaction to the promoted image."""
        try:
            # Choose a random emoji from the configured options
            available_emoji_options: list[str] = self.config["messages"]["success_reaction_emojis"]
            randomly_selected_emoji: str = random.choice(available_emoji_options)
            # Add the reaction to the replied message
            await message_event.client.react(message_event.room_id, target_image_event_id, randomly_selected_emoji)
            self.log.info(f"{randomly_selected_emoji} Added reaction to promoted image")
        except Exception as reaction_error:
            self.log.error(f"❌ Failed to add reaction emoji '{randomly_selected_emoji if randomly_selected_emoji in locals() else "unknown"}': {reaction_error}")

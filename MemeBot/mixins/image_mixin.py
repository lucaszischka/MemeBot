"""
Image processing mixin for MemeBot.
Handles image download, validation, and format checking with caching.
"""
from __future__ import annotations

from functools import lru_cache
from io import BytesIO
from PIL import Image
from maubot.matrix import MaubotMessageEvent
from mautrix.types import MessageEvent, EncryptedFile, ContentURI
from mautrix.crypto.attachments import decrypt_attachment
from .types import MixinHost


class ImageMixin(MixinHost):
    """Mixin for image processing functionality."""
    
    @lru_cache(maxsize=1) 
    def _get_cached_supported_image_formats(self) -> tuple[str, ...]:
        """Cache supported image formats."""
        return tuple(image_format.upper() for image_format in self.config["image"]["allowed_image_formats"])

    async def _download_image(self, message_event: MaubotMessageEvent, target_image_message: MessageEvent, image_filename: str) -> bytes | None:
        """Download image data, handling both encrypted and unencrypted files."""
        encryption_info: EncryptedFile | None = getattr(target_image_message.content, 'file', None)
        media_url: ContentURI | None = getattr(target_image_message.content, 'url', None)
        # Encrypted file
        if encryption_info:
            return await self._download_encrypted_image(message_event, encryption_info, image_filename)
        # Unencrypted file
        elif media_url: 
            return await self._download_unencrypted_image(message_event, media_url)
        else:
            self.log.error(f"❌🔗 No image URL found in replied message: filename='{image_filename}', user={message_event.sender}, message_id={target_image_message.event_id}")
            await message_event.respond(self.config["messages"]["image_missing"], in_thread=self.config["messages"]["reply_in_thread"])
            return None

    async def _download_encrypted_image(self, message_event: MaubotMessageEvent, encryption_info: EncryptedFile, image_filename: str) -> bytes | None:
        """Download and decrypt an encrypted image."""
        media_url: ContentURI | None = encryption_info.url
        if not media_url:
            self.log.error(f"❌🔗 No MXC URL found in encrypted file metadata: filename='{image_filename}'")
            await message_event.respond(self.config["messages"]["encrypted_image_url_missing"], in_thread=self.config["messages"]["reply_in_thread"])
            return None
        try:
            # Download and decrypt the encrypted file
            encrypted_data: bytes = await message_event.client.download_media(media_url)
            # Decrypt using the metadata from the event
            image_bytes: bytes = decrypt_attachment(
                ciphertext=encrypted_data,
                key=encryption_info.key.key,
                hash=encryption_info.hashes["sha256"],
                iv=encryption_info.iv
            )
            return image_bytes
        except Exception as error:
            self.log.error(f"❌🔐 Decryption of file '{image_filename}' failed: {error}")
            await message_event.respond(self.config["messages"]["encrypted_image_decrypt_failed"], in_thread=self.config["messages"]["reply_in_thread"])
            return None

    async def _download_unencrypted_image(self, message_event: MaubotMessageEvent, media_url: ContentURI) -> bytes | None:
        """Download an unencrypted image."""
        try:
            return await message_event.client.download_media(media_url)
        except Exception as error:
            self.log.error(f"❌📥 Download failed: url={media_url}: {error}")
            await message_event.respond(self.config["messages"]["image_download_failed"], in_thread=self.config["messages"]["reply_in_thread"])
            return None

    async def _validate_image(self, message_event: MaubotMessageEvent, image_bytes: bytes, image_filename: str) -> str | None:
        """Validate image data, size, and format. Returns the image format if valid, None otherwise."""
        # Validate we have image data
        if not image_bytes:
            self.log.error(f"❌📁 No image bytes found for file: {image_filename}")
            await message_event.respond(self.config["messages"]["image_download_failed"], in_thread=self.config["messages"]["reply_in_thread"])
            return None
        # Validate file size
        if not await self._validate_image_size(image_bytes, message_event):
            return None
        # Validate image format and return the format
        return await self._validate_image_format(image_bytes, image_filename, message_event)

    async def _validate_image_size(self, image_bytes: bytes, message_event: MaubotMessageEvent) -> bool:
        """Check if image size is within configured limits."""
        maximum_allowed_file_size: int = self.config["image"]["maximum_file_size_bytes"]
        actual_image_size: int = len(image_bytes)
        if actual_image_size > maximum_allowed_file_size:
            self.log.warning(f"📏 Image size exceeded limit: size={actual_image_size:,} bytes, max={maximum_allowed_file_size:,} bytes")
            await message_event.respond(self.config["messages"]["image_size_exceeded"], in_thread=self.config["messages"]["reply_in_thread"])
            return False
        return True

    async def _validate_image_format(self, image_bytes: bytes, image_filename: str, message_event: MaubotMessageEvent) -> str | None:
        """Validate image format against allowed formats. Returns the image format if valid, None otherwise."""
        try:
            with Image.open(BytesIO(image_bytes)) as image_object:
                # Get the image format
                detected_image_format: str | None = image_object.format
                if not detected_image_format:
                    self.log.warning(f"❓ Could not determine image format: filename='{image_filename}', size={len(image_bytes):,} bytes")
                    await message_event.respond(self.config["messages"]["image_format_invalid"], in_thread=self.config["messages"]["reply_in_thread"])
                    return None
                # Check if the format is supported using cached formats
                supported_image_formats = self._get_cached_supported_image_formats()
                if detected_image_format.upper() not in supported_image_formats:
                    self.log.warning(f"🚫 Unsupported image format: format={detected_image_format}, supported_formats={list(supported_image_formats)}, filename='{image_filename}'")
                    await message_event.respond(self.config["messages"]["image_format_unsupported"], in_thread=self.config["messages"]["reply_in_thread"])
                    return None
                return detected_image_format
        except Exception as error:
            self.log.error(f"❌🖼️ Image format validation failed: filename='{image_filename}', size={len(image_bytes):,} bytes: {error}")
            await message_event.respond(self.config["messages"]["image_format_invalid"], in_thread=self.config["messages"]["reply_in_thread"])
            return None

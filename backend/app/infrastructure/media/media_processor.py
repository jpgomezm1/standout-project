"""Media processor — downloads and pre-processes media files from channels."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domain.interfaces.channel_adapter import IChannelAdapter

logger = logging.getLogger(__name__)


class MediaProcessor:
    """Downloads media files through the channel adapter and returns metadata.

    This class acts as a thin orchestration layer that iterates over file
    references attached to an inbound message, downloads each one via the
    injected :class:`IChannelAdapter`, and returns a list of result dicts
    containing the raw bytes together with metadata.

    Parameters
    ----------
    channel_adapter:
        The channel adapter used to fetch media from the originating
        platform (e.g. Telegram).
    """

    def __init__(self, channel_adapter: IChannelAdapter) -> None:
        self.channel_adapter = channel_adapter

    async def download_and_process(
        self,
        file_references: list[dict],
    ) -> list[dict]:
        """Download all referenced media files and return result metadata.

        Parameters
        ----------
        file_references:
            A list of dicts, each containing at least a ``file_id`` key and
            optionally a ``type`` key (e.g. ``"photo"``, ``"voice"``).

        Returns
        -------
        list[dict]
            One dict per successfully downloaded file with keys:
            ``file_id``, ``type``, ``data`` (raw bytes), and ``size``.
            Files that fail to download are logged and skipped.
        """
        results: list[dict] = []

        for ref in file_references:
            file_id = ref.get("file_id")
            if not file_id:
                logger.warning("Skipping file reference with no file_id: %s", ref)
                continue

            file_type = ref.get("type", "unknown")
            try:
                data = await self.channel_adapter.download_media(file_id)
                results.append(
                    {
                        "file_id": file_id,
                        "type": file_type,
                        "data": data,
                        "size": len(data),
                    }
                )
                logger.debug(
                    "Downloaded media file_id=%s type=%s size=%d",
                    file_id,
                    file_type,
                    len(data),
                )
            except Exception:
                logger.exception(
                    "Failed to download media file_id=%s type=%s",
                    file_id,
                    file_type,
                )

        logger.info(
            "Media processing complete: %d/%d files downloaded",
            len(results),
            len(file_references),
        )
        return results

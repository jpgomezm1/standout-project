from __future__ import annotations

from pydantic import BaseModel


class MediaReference(BaseModel, frozen=True):
    """Immutable reference to a media file attached to an inbound message.

    ``file_id`` is the platform-specific identifier (e.g. Telegram file_id).
    ``file_url`` and ``local_path`` are populated as the media progresses
    through download and local caching stages.
    """

    file_id: str
    file_type: str
    file_url: str | None = None
    local_path: str | None = None

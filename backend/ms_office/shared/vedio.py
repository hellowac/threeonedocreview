""" 视频部件的封装 """

from __future__ import annotations

from .parts import VideoPart


class Video:
    """视频部件的封装"""

    def __init__(self, part: VideoPart) -> None:
        self.part = part

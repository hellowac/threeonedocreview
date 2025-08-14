from __future__ import annotations

from .parts import PresentationPropertiesPart


class PresentationProperties:
    """演示文稿特性"""

    def __init__(self, part: PresentationPropertiesPart) -> None:
        self.part = part
        self.oxml = part.oxml

    @property
    def color_mru(self):
        """用户最近使用的颜色"""

        return self.oxml.color_mru

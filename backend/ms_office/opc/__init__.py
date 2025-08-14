# opc 相关的部件注册

from ..part import PART_TYPE_MAP
from .constants import CONTENT_TYPE as OCT
from .parts import CorePropertiesPart, ImagePart

# 注册OPC的不同类型的部件的构造对象

PART_TYPE_MAP.update(
    {
        OCT.CORE_PROPERTIES: CorePropertiesPart,
        OCT.JPEG: ImagePart,
        OCT.JPG: ImagePart,
        OCT.PNG: ImagePart,
        OCT.GIF: ImagePart,
        OCT.JPEG: ImagePart,
        OCT.JPEG: ImagePart,
    }
)

from __future__ import annotations

import colorsys
import logging
import math
from enum import Enum
from typing import NamedTuple, Union

import numpy

from ms_office.dml.style.color import (
    ColorMapping,
    ColorScheme,
    ColorTransformBase,
    ColorTypes,
    ColorTypesRequire,
    HslColor,
    PresetColor,
    SchemeColor,
    ScrgbColor,
    SrgbColor,
    SystemColor,
)
from ms_office.oxml.dml.main import (
    ST_ColorSchemeIndex,
    ST_SchemeColorVal,
    to_ST_PositiveFixedPercentage,
)
from ms_office.pml.slide import Slide
from ms_office.pml.slide_layout import SlideLayout
from ms_office.pml.slide_master import SlideMaster

from .common import ThemeTool

logger = logging.getLogger(__name__)


SlideTypes = Union[Slide, SlideLayout, SlideMaster]


class BaseEnumType(Enum):
    """参考:

    合法的枚举成员和属性

    https://docs.python.org/zh-cn/3.10/library/enum.html#allowed-members-and-attributes-of-enumerations
    """

    @classmethod
    def has_value(cls, value: str):
        """判断是否拥有某个值"""

        return value in [e.value for e in cls]


class RGBAColor(NamedTuple):
    """RGB 颜色

    所有浏览器都支持 RGB 颜色值。

    RGB 颜色值通过以下方式指定:

    rgb(red, green, blue)

    每个参数（红色、绿色和蓝色）定义颜色的强度，其值介于 0 到 255 之间。

    例如，rgb(255, 0, 0) 显示为红色，因为红色设置为其最高值 (255)，而其他两个（绿色和蓝色）设置为 0。

    另一个例子，rgb(0, 255, 0) 显示为绿色，因为绿色设置为其最高值 (255)，而其他两个（红色和蓝色）设置为 0。

    要显示黑色，请将所有颜色参数设置为 0，如下所示: rgb(0, 0, 0)。

    要显示白色，请将所有颜色参数设置为 255，如下所示: rgb(255, 255, 255)。
    """

    r: numpy.uint8  # 0-255
    g: numpy.uint8  # 0-255
    b: numpy.uint8  # 0-255
    a: numpy.float_ = numpy.float_(1.0)  # 0-1

    def __str__(self):
        """返回十六进制字符串 rgb 值，例如 '3C2F80'"""

        if self.a == 1:
            return f"{self.r:02X}{self.g:02X}{self.b:02X}"

        alpha = int(255 * self.a)
        return f"{self.r:02X}{self.g:02X}{self.b:02X}{alpha:02X}"

    @classmethod
    def from_string(cls, rgb_hex_str):
        """从 RGB 颜色十六进制字符串(如“3C2F80”)返回一个新实例。"""
        r = numpy.uint8(int(rgb_hex_str[:2], 16))
        g = numpy.uint8(int(rgb_hex_str[2:4], 16))
        b = numpy.uint8(int(rgb_hex_str[4:], 16))
        return cls(r, g, b)

    @property
    def rgb_html(self):
        return f"#{self.r:02X}{self.g:02X}{self.b:02X}"


class HSLAColor(NamedTuple):
    """HSL 颜色

    - Hue

        色调是色轮上从 0 到 360 的度数。0（或 360）是红色，120 是绿色，240 是蓝色。

    - Saturation:

        饱和度可以描述为颜色的强度。 它是从 0% 到 100% 的百分比值。

        100% 是全彩，没有灰色阴影。

        50%是50%灰色，但你仍然可以看到颜色。

        0%是完全灰色的； 你再也看不到颜色了。

    - Lightness:

        颜色的明度可以描述为您想要赋予该颜色多少光，其中0%表示没有光（暗），50%表示50%光（既不暗也不亮），100%表示全亮。
    """

    h: numpy.uint16  # 0-360
    s: numpy.float_  # 0-1 百分比
    l: numpy.float_  # 0-1 百分比
    a: numpy.float_ = numpy.float_(1.0)  # 0-1

    def __str__(self):
        """返回十六进制字符串 hsl 值，例如 '3C2F80'"""

        if self.a == 1:
            return f"hsl({self.h} {self.s*100}% {self.l*100}%)"

        alpha = self.a * 255
        return f"hsla({self.h} {self.s*100}% {self.l*100}% {alpha:X})"


class PresetColorValues(BaseEnumType):
    """预置颜色的rgb值

    参考:

    http://192.168.2.53:8001/openxml/ecma-part1/chapter20/main/simple_types/#2011048-st_presetcolorval-预设颜色值
    """

    aliceBlue = RGBAColor(
        numpy.uint8(240), numpy.uint8(248), numpy.uint8(255)
    )  # 爱丽丝蓝
    antiqueWhite = RGBAColor(
        numpy.uint8(250), numpy.uint8(235), numpy.uint8(215)
    )  # 古董白
    aqua = RGBAColor(numpy.uint8(0), numpy.uint8(255), numpy.uint8(255))  # 水绿
    aquamarine = RGBAColor(numpy.uint8(127), numpy.uint8(255), numpy.uint8(212))  # 碧绿
    azure = RGBAColor(numpy.uint8(240), numpy.uint8(255), numpy.uint8(255))  # 天蓝
    beige = RGBAColor(numpy.uint8(245), numpy.uint8(245), numpy.uint8(220))  # 米色
    bisque = RGBAColor(numpy.uint8(255), numpy.uint8(228), numpy.uint8(196))  # 橙黄
    black = RGBAColor(numpy.uint8(0), numpy.uint8(0), numpy.uint8(0))  # 黑色
    blanchedAlmond = RGBAColor(
        numpy.uint8(255), numpy.uint8(235), numpy.uint8(205)
    )  # 杏仁白
    blue = RGBAColor(numpy.uint8(0), numpy.uint8(0), numpy.uint8(255))  # 蓝色
    blueViolet = RGBAColor(numpy.uint8(138), numpy.uint8(43), numpy.uint8(226))
    brown = RGBAColor(numpy.uint8(165), numpy.uint8(42), numpy.uint8(42))
    burlyWood = RGBAColor(numpy.uint8(222), numpy.uint8(184), numpy.uint8(135))
    cadetBlue = RGBAColor(numpy.uint8(95), numpy.uint8(158), numpy.uint8(160))
    chartreuse = RGBAColor(numpy.uint8(127), numpy.uint8(255), numpy.uint8(0))
    chocolate = RGBAColor(numpy.uint8(210), numpy.uint8(105), numpy.uint8(30))
    coral = RGBAColor(numpy.uint8(255), numpy.uint8(127), numpy.uint8(80))
    cornflowerBlue = RGBAColor(numpy.uint8(100), numpy.uint8(149), numpy.uint8(237))
    cornsilk = RGBAColor(numpy.uint8(255), numpy.uint8(248), numpy.uint8(220))
    crimson = RGBAColor(numpy.uint8(220), numpy.uint8(20), numpy.uint8(60))
    cyan = RGBAColor(numpy.uint8(0), numpy.uint8(255), numpy.uint8(255))
    darkBlue = RGBAColor(numpy.uint8(0), numpy.uint8(0), numpy.uint8(139))
    darkCyan = RGBAColor(numpy.uint8(0), numpy.uint8(139), numpy.uint8(139))
    darkGoldenrod = RGBAColor(numpy.uint8(184), numpy.uint8(134), numpy.uint8(11))
    darkGray = RGBAColor(numpy.uint8(169), numpy.uint8(169), numpy.uint8(169))
    darkGreen = RGBAColor(numpy.uint8(0), numpy.uint8(100), numpy.uint8(0))
    darkGrey = RGBAColor(numpy.uint8(169), numpy.uint8(169), numpy.uint8(169))
    darkKhaki = RGBAColor(numpy.uint8(189), numpy.uint8(183), numpy.uint8(107))
    darkMagenta = RGBAColor(numpy.uint8(139), numpy.uint8(0), numpy.uint8(139))
    darkOliveGreen = RGBAColor(numpy.uint8(85), numpy.uint8(107), numpy.uint8(47))
    darkOrange = RGBAColor(numpy.uint8(255), numpy.uint8(140), numpy.uint8(0))
    darkOrchid = RGBAColor(numpy.uint8(153), numpy.uint8(50), numpy.uint8(204))
    darkRed = RGBAColor(numpy.uint8(139), numpy.uint8(0), numpy.uint8(0))
    darkSalmon = RGBAColor(numpy.uint8(233), numpy.uint8(150), numpy.uint8(122))
    darkSeaGreen = RGBAColor(numpy.uint8(143), numpy.uint8(188), numpy.uint8(143))
    darkSlateBlue = RGBAColor(numpy.uint8(72), numpy.uint8(61), numpy.uint8(139))
    darkSlateGray = RGBAColor(numpy.uint8(47), numpy.uint8(79), numpy.uint8(79))
    darkSlateGrey = RGBAColor(numpy.uint8(47), numpy.uint8(79), numpy.uint8(79))
    darkTurquoise = RGBAColor(numpy.uint8(0), numpy.uint8(206), numpy.uint8(209))
    darkViolet = RGBAColor(numpy.uint8(148), numpy.uint8(0), numpy.uint8(211))
    deepPink = RGBAColor(numpy.uint8(255), numpy.uint8(20), numpy.uint8(147))
    deepSkyBlue = RGBAColor(numpy.uint8(0), numpy.uint8(191), numpy.uint8(255))
    dimGray = RGBAColor(numpy.uint8(105), numpy.uint8(105), numpy.uint8(105))
    dimGrey = RGBAColor(numpy.uint8(105), numpy.uint8(105), numpy.uint8(105))
    dkBlue = RGBAColor(numpy.uint8(0), numpy.uint8(0), numpy.uint8(139))
    dkCyan = RGBAColor(numpy.uint8(0), numpy.uint8(139), numpy.uint8(139))
    dkGoldenrod = RGBAColor(numpy.uint8(184), numpy.uint8(134), numpy.uint8(11))
    dkGray = RGBAColor(numpy.uint8(169), numpy.uint8(169), numpy.uint8(169))
    dkGreen = RGBAColor(numpy.uint8(0), numpy.uint8(100), numpy.uint8(0))
    dkGrey = RGBAColor(numpy.uint8(169), numpy.uint8(169), numpy.uint8(169))
    dkKhaki = RGBAColor(numpy.uint8(189), numpy.uint8(183), numpy.uint8(107))
    dkMagenta = RGBAColor(numpy.uint8(139), numpy.uint8(0), numpy.uint8(139))
    dkOliveGreen = RGBAColor(numpy.uint8(85), numpy.uint8(107), numpy.uint8(47))
    dkOrange = RGBAColor(numpy.uint8(255), numpy.uint8(140), numpy.uint8(0))
    dkOrchid = RGBAColor(numpy.uint8(153), numpy.uint8(50), numpy.uint8(204))
    dkRed = RGBAColor(numpy.uint8(139), numpy.uint8(0), numpy.uint8(0))
    dkSalmon = RGBAColor(numpy.uint8(233), numpy.uint8(150), numpy.uint8(122))
    dkSeaGreen = RGBAColor(numpy.uint8(143), numpy.uint8(188), numpy.uint8(139))
    dkSlateBlue = RGBAColor(numpy.uint8(72), numpy.uint8(61), numpy.uint8(139))
    dkSlateGray = RGBAColor(numpy.uint8(47), numpy.uint8(79), numpy.uint8(79))
    dkSlateGrey = RGBAColor(numpy.uint8(47), numpy.uint8(79), numpy.uint8(79))
    dkTurquoise = RGBAColor(numpy.uint8(0), numpy.uint8(206), numpy.uint8(209))
    dkViolet = RGBAColor(numpy.uint8(148), numpy.uint8(0), numpy.uint8(211))
    dodgerBlue = RGBAColor(numpy.uint8(30), numpy.uint8(144), numpy.uint8(255))
    firebrick = RGBAColor(numpy.uint8(178), numpy.uint8(34), numpy.uint8(34))
    floralWhite = RGBAColor(numpy.uint8(255), numpy.uint8(250), numpy.uint8(240))
    forestGreen = RGBAColor(numpy.uint8(34), numpy.uint8(139), numpy.uint8(34))
    fuchsia = RGBAColor(numpy.uint8(255), numpy.uint8(0), numpy.uint8(255))
    gainsboro = RGBAColor(numpy.uint8(220), numpy.uint8(220), numpy.uint8(220))
    ghostWhite = RGBAColor(numpy.uint8(248), numpy.uint8(248), numpy.uint8(255))
    gold = RGBAColor(numpy.uint8(255), numpy.uint8(215), numpy.uint8(0))
    goldenrod = RGBAColor(numpy.uint8(218), numpy.uint8(165), numpy.uint8(32))
    gray = RGBAColor(numpy.uint8(128), numpy.uint8(128), numpy.uint8(128))
    green = RGBAColor(numpy.uint8(0), numpy.uint8(128), numpy.uint8(0))
    greenYellow = RGBAColor(numpy.uint8(173), numpy.uint8(255), numpy.uint8(47))
    grey = RGBAColor(numpy.uint8(128), numpy.uint8(128), numpy.uint8(128))
    honeydew = RGBAColor(numpy.uint8(240), numpy.uint8(255), numpy.uint8(240))
    hotPink = RGBAColor(numpy.uint8(255), numpy.uint8(105), numpy.uint8(180))
    indianRed = RGBAColor(numpy.uint8(205), numpy.uint8(92), numpy.uint8(92))
    indigo = RGBAColor(numpy.uint8(75), numpy.uint8(0), numpy.uint8(130))
    ivory = RGBAColor(numpy.uint8(255), numpy.uint8(255), numpy.uint8(240))
    khaki = RGBAColor(numpy.uint8(240), numpy.uint8(230), numpy.uint8(140))
    lavender = RGBAColor(numpy.uint8(230), numpy.uint8(230), numpy.uint8(250))
    lavenderBlush = RGBAColor(numpy.uint8(255), numpy.uint8(240), numpy.uint8(245))
    lawnGreen = RGBAColor(numpy.uint8(124), numpy.uint8(252), numpy.uint8(0))
    lemonChiffon = RGBAColor(numpy.uint8(255), numpy.uint8(250), numpy.uint8(205))
    lightBlue = RGBAColor(numpy.uint8(173), numpy.uint8(216), numpy.uint8(230))
    lightCoral = RGBAColor(numpy.uint8(240), numpy.uint8(128), numpy.uint8(128))
    lightCyan = RGBAColor(numpy.uint8(224), numpy.uint8(255), numpy.uint8(255))
    lightGoldenrodYellow = RGBAColor(
        numpy.uint8(250), numpy.uint8(250), numpy.uint8(210)
    )
    lightGray = RGBAColor(numpy.uint8(211), numpy.uint8(211), numpy.uint8(211))
    lightGreen = RGBAColor(numpy.uint8(144), numpy.uint8(238), numpy.uint8(144))
    lightGrey = RGBAColor(numpy.uint8(211), numpy.uint8(211), numpy.uint8(211))
    lightPink = RGBAColor(numpy.uint8(255), numpy.uint8(182), numpy.uint8(193))
    lightSalmon = RGBAColor(numpy.uint8(255), numpy.uint8(160), numpy.uint8(122))
    lightSeaGreen = RGBAColor(numpy.uint8(32), numpy.uint8(178), numpy.uint8(170))
    lightSkyBlue = RGBAColor(numpy.uint8(135), numpy.uint8(206), numpy.uint8(250))
    lightSlateGray = RGBAColor(numpy.uint8(119), numpy.uint8(136), numpy.uint8(153))
    lightSlateGrey = RGBAColor(numpy.uint8(119), numpy.uint8(136), numpy.uint8(153))
    lightSteelBlue = RGBAColor(numpy.uint8(176), numpy.uint8(196), numpy.uint8(222))
    lightYellow = RGBAColor(numpy.uint8(255), numpy.uint8(255), numpy.uint8(224))
    lime = RGBAColor(numpy.uint8(0), numpy.uint8(255), numpy.uint8(0))
    limeGreen = RGBAColor(numpy.uint8(50), numpy.uint8(205), numpy.uint8(50))
    linen = RGBAColor(numpy.uint8(250), numpy.uint8(240), numpy.uint8(230))
    ltBlue = RGBAColor(numpy.uint8(173), numpy.uint8(216), numpy.uint8(230))
    ltCoral = RGBAColor(numpy.uint8(240), numpy.uint8(128), numpy.uint8(128))
    ltCyan = RGBAColor(numpy.uint8(224), numpy.uint8(255), numpy.uint8(255))
    ltGoldenrodYellow = RGBAColor(numpy.uint8(250), numpy.uint8(250), numpy.uint8(120))
    ltGray = RGBAColor(numpy.uint8(211), numpy.uint8(211), numpy.uint8(211))
    ltGreen = RGBAColor(numpy.uint8(144), numpy.uint8(238), numpy.uint8(144))
    ltGrey = RGBAColor(numpy.uint8(211), numpy.uint8(211), numpy.uint8(211))
    ltPink = RGBAColor(numpy.uint8(255), numpy.uint8(182), numpy.uint8(193))
    ltSalmon = RGBAColor(numpy.uint8(255), numpy.uint8(160), numpy.uint8(122))
    ltSeaGreen = RGBAColor(numpy.uint8(32), numpy.uint8(178), numpy.uint8(170))
    ltSkyBlue = RGBAColor(numpy.uint8(135), numpy.uint8(206), numpy.uint8(250))
    ltSlateGray = RGBAColor(numpy.uint8(119), numpy.uint8(136), numpy.uint8(153))
    ltSlateGrey = RGBAColor(numpy.uint8(119), numpy.uint8(136), numpy.uint8(153))
    ltSteelBlue = RGBAColor(numpy.uint8(176), numpy.uint8(196), numpy.uint8(222))
    ltYellow = RGBAColor(numpy.uint8(255), numpy.uint8(255), numpy.uint8(224))
    magenta = RGBAColor(numpy.uint8(255), numpy.uint8(0), numpy.uint8(255))
    maroon = RGBAColor(numpy.uint8(128), numpy.uint8(0), numpy.uint8(0))
    medAquamarine = RGBAColor(numpy.uint8(102), numpy.uint8(205), numpy.uint8(170))
    medBlue = RGBAColor(numpy.uint8(0), numpy.uint8(0), numpy.uint8(205))
    mediumAquamarine = RGBAColor(numpy.uint8(102), numpy.uint8(205), numpy.uint8(170))
    mediumBlue = RGBAColor(numpy.uint8(0), numpy.uint8(0), numpy.uint8(205))
    mediumOrchid = RGBAColor(numpy.uint8(186), numpy.uint8(85), numpy.uint8(211))
    mediumPurple = RGBAColor(numpy.uint8(147), numpy.uint8(112), numpy.uint8(219))
    mediumSeaGreen = RGBAColor(numpy.uint8(60), numpy.uint8(179), numpy.uint8(113))
    mediumSlateBlue = RGBAColor(numpy.uint8(123), numpy.uint8(104), numpy.uint8(238))
    mediumSpringGreen = RGBAColor(numpy.uint8(0), numpy.uint8(250), numpy.uint8(154))
    mediumTurquoise = RGBAColor(numpy.uint8(72), numpy.uint8(209), numpy.uint8(204))
    mediumVioletRed = RGBAColor(numpy.uint8(199), numpy.uint8(21), numpy.uint8(133))
    medOrchid = RGBAColor(numpy.uint8(186), numpy.uint8(85), numpy.uint8(211))
    medPurple = RGBAColor(numpy.uint8(147), numpy.uint8(112), numpy.uint8(219))
    medSeaGreen = RGBAColor(numpy.uint8(60), numpy.uint8(179), numpy.uint8(113))
    medSlateBlue = RGBAColor(numpy.uint8(123), numpy.uint8(104), numpy.uint8(238))
    medSpringGreen = RGBAColor(numpy.uint8(0), numpy.uint8(250), numpy.uint8(154))
    medTurquoise = RGBAColor(numpy.uint8(72), numpy.uint8(209), numpy.uint8(204))
    medVioletRed = RGBAColor(numpy.uint8(199), numpy.uint8(21), numpy.uint8(133))
    midnightBlue = RGBAColor(numpy.uint8(25), numpy.uint8(25), numpy.uint8(112))
    mintCream = RGBAColor(numpy.uint8(245), numpy.uint8(255), numpy.uint8(250))
    mistyRose = RGBAColor(numpy.uint8(255), numpy.uint8(228), numpy.uint8(225))
    moccasin = RGBAColor(numpy.uint8(255), numpy.uint8(228), numpy.uint8(181))
    navajoWhite = RGBAColor(numpy.uint8(255), numpy.uint8(222), numpy.uint8(173))
    navy = RGBAColor(numpy.uint8(0), numpy.uint8(0), numpy.uint8(128))
    oldLace = RGBAColor(numpy.uint8(253), numpy.uint8(245), numpy.uint8(230))
    olive = RGBAColor(numpy.uint8(128), numpy.uint8(128), numpy.uint8(0))
    oliveDrab = RGBAColor(numpy.uint8(107), numpy.uint8(142), numpy.uint8(35))
    orange = RGBAColor(numpy.uint8(255), numpy.uint8(165), numpy.uint8(0))
    orangeRed = RGBAColor(numpy.uint8(255), numpy.uint8(69), numpy.uint8(0))
    orchid = RGBAColor(numpy.uint8(218), numpy.uint8(112), numpy.uint8(214))
    paleGoldenrod = RGBAColor(numpy.uint8(238), numpy.uint8(232), numpy.uint8(170))
    paleGreen = RGBAColor(numpy.uint8(152), numpy.uint8(251), numpy.uint8(152))
    paleTurquoise = RGBAColor(numpy.uint8(175), numpy.uint8(238), numpy.uint8(238))
    paleVioletRed = RGBAColor(numpy.uint8(219), numpy.uint8(112), numpy.uint8(147))
    papayaWhip = RGBAColor(numpy.uint8(255), numpy.uint8(239), numpy.uint8(213))
    peachPuff = RGBAColor(numpy.uint8(255), numpy.uint8(218), numpy.uint8(185))
    peru = RGBAColor(numpy.uint8(205), numpy.uint8(133), numpy.uint8(63))
    pink = RGBAColor(numpy.uint8(255), numpy.uint8(192), numpy.uint8(203))
    plum = RGBAColor(numpy.uint8(221), numpy.uint8(160), numpy.uint8(221))
    powderBlue = RGBAColor(numpy.uint8(176), numpy.uint8(224), numpy.uint8(230))
    purple = RGBAColor(numpy.uint8(128), numpy.uint8(0), numpy.uint8(128))
    red = RGBAColor(numpy.uint8(255), numpy.uint8(0), numpy.uint8(0))
    rosyBrown = RGBAColor(numpy.uint8(188), numpy.uint8(143), numpy.uint8(143))
    royalBlue = RGBAColor(numpy.uint8(65), numpy.uint8(105), numpy.uint8(225))
    saddleBrown = RGBAColor(numpy.uint8(139), numpy.uint8(69), numpy.uint8(19))
    salmon = RGBAColor(numpy.uint8(250), numpy.uint8(128), numpy.uint8(114))
    sandyBrown = RGBAColor(numpy.uint8(244), numpy.uint8(164), numpy.uint8(96))
    seaGreen = RGBAColor(numpy.uint8(46), numpy.uint8(139), numpy.uint8(87))
    seaShell = RGBAColor(numpy.uint8(255), numpy.uint8(245), numpy.uint8(238))
    sienna = RGBAColor(numpy.uint8(160), numpy.uint8(82), numpy.uint8(45))
    silver = RGBAColor(numpy.uint8(192), numpy.uint8(192), numpy.uint8(192))
    skyBlue = RGBAColor(numpy.uint8(135), numpy.uint8(206), numpy.uint8(235))
    slateBlue = RGBAColor(numpy.uint8(106), numpy.uint8(90), numpy.uint8(205))
    slateGray = RGBAColor(numpy.uint8(112), numpy.uint8(128), numpy.uint8(144))
    slateGrey = RGBAColor(numpy.uint8(112), numpy.uint8(128), numpy.uint8(144))
    snow = RGBAColor(numpy.uint8(255), numpy.uint8(250), numpy.uint8(250))
    springGreen = RGBAColor(numpy.uint8(0), numpy.uint8(255), numpy.uint8(127))
    steelBlue = RGBAColor(numpy.uint8(70), numpy.uint8(130), numpy.uint8(180))
    tan = RGBAColor(numpy.uint8(210), numpy.uint8(180), numpy.uint8(140))
    teal = RGBAColor(numpy.uint8(0), numpy.uint8(128), numpy.uint8(128))
    thistle = RGBAColor(numpy.uint8(216), numpy.uint8(191), numpy.uint8(216))
    tomato = RGBAColor(numpy.uint8(255), numpy.uint8(99), numpy.uint8(71))
    turquoise = RGBAColor(numpy.uint8(64), numpy.uint8(224), numpy.uint8(208))
    violet = RGBAColor(numpy.uint8(238), numpy.uint8(130), numpy.uint8(238))
    wheat = RGBAColor(numpy.uint8(245), numpy.uint8(222), numpy.uint8(179))
    white = RGBAColor(numpy.uint8(255), numpy.uint8(255), numpy.uint8(255))
    whiteSmoke = RGBAColor(numpy.uint8(245), numpy.uint8(245), numpy.uint8(245))
    yellow = RGBAColor(numpy.uint8(255), numpy.uint8(255), numpy.uint8(0))
    yellowGreen = RGBAColor(numpy.uint8(154), numpy.uint8(205), numpy.uint8(50))


class ColorTool:
    """颜色工具类"""

    @classmethod
    def extract_schema_color(cls, color: SchemeColor, slide: SlideTypes):
        """提取schema color 的值

        1. 从 slide > layout > master 中依次获取颜色映射: color_map
        2. 然后根据 schema_color 的值，找到schem_color 在 颜色方案(color_schema) 中的索引
        3. 根据 索引，获取 主题覆盖(theme_override) 或 主题(theme) 中的具体的颜色。
        """

        # logger.debug(f"主题(schema)颜色key为 {color.value.value =}")

        color_map = ThemeTool.choice_color_map(slide)
        color_schema = ThemeTool.choice_color_schema(slide)

        # logger.debug(f"颜色方案(color Schema)名称为: {color_schema.name = }")

        schema_color = cls.extract_schema_index(color_map, color_schema, color.value)

        # logger.debug(f"主题(schema)颜色: {schema_color = }")

        return schema_color

    @classmethod
    def extract_schema_index(
        cls,
        color_map: ColorMapping,
        color_schema: ColorScheme,
        schema_color_value: ST_SchemeColorVal,
    ):
        # logger.info(f"{color_map = }")
        # logger.info(f"{schema_color_value = }")
        # logger.info(color_map.oxml.xml)

        scheme_idx: ST_ColorSchemeIndex | None = None

        index_map: dict[ST_SchemeColorVal, ST_ColorSchemeIndex | None] = {
            ST_SchemeColorVal.Background1: color_map.bg1,
            ST_SchemeColorVal.Background2: color_map.bg2,
            ST_SchemeColorVal.Text1: color_map.tx1,
            ST_SchemeColorVal.Text2: color_map.tx2,
            ST_SchemeColorVal.Accent1: color_map.accent1,
            ST_SchemeColorVal.Accent2: color_map.accent2,
            ST_SchemeColorVal.Accent3: color_map.accent3,
            ST_SchemeColorVal.Accent4: color_map.accent4,
            ST_SchemeColorVal.Accent5: color_map.accent5,
            ST_SchemeColorVal.Accent6: color_map.accent6,
            ST_SchemeColorVal.Hyperlink: color_map.hlink,
            ST_SchemeColorVal.FollowedHyperlink: color_map.folHlink,
            ST_SchemeColorVal.Dark1: ST_ColorSchemeIndex.Dark1,
            ST_SchemeColorVal.Dark2: ST_ColorSchemeIndex.Dark2,
            ST_SchemeColorVal.Light1: ST_ColorSchemeIndex.Light1,
            ST_SchemeColorVal.Light2: ST_ColorSchemeIndex.Light2,
            # 占位符颜色特殊处理, 会报错
            ST_SchemeColorVal.Placeholder: None,
        }

        scheme_idx = index_map.get(schema_color_value)

        # logger.debug(f"颜色: {scheme_idx = }")

        if scheme_idx is None:
            raise ValueError(
                f"获取方案颜色索引(schema color index) 失败: {schema_color_value = }"
            )

        if scheme_idx == ST_ColorSchemeIndex.Dark1:
            return color_schema.dk1

        elif scheme_idx == ST_ColorSchemeIndex.Dark2:
            return color_schema.dk2

        elif scheme_idx == ST_ColorSchemeIndex.Light1:
            return color_schema.lt1

        elif scheme_idx == ST_ColorSchemeIndex.Light2:
            return color_schema.lt2

        elif scheme_idx == ST_ColorSchemeIndex.Accent1:
            return color_schema.accent1

        elif scheme_idx == ST_ColorSchemeIndex.Accent2:
            return color_schema.accent2

        elif scheme_idx == ST_ColorSchemeIndex.Accent3:
            return color_schema.accent3

        elif scheme_idx == ST_ColorSchemeIndex.Accent4:
            return color_schema.accent4

        elif scheme_idx == ST_ColorSchemeIndex.Accent5:
            return color_schema.accent5

        elif scheme_idx == ST_ColorSchemeIndex.Accent6:
            return color_schema.accent6

        elif scheme_idx == ST_ColorSchemeIndex.Hyperlink:
            return color_schema.hlink

        elif scheme_idx == ST_ColorSchemeIndex.Followed_hyperlink:
            return color_schema.folHlink

        raise ValueError(f"获取方案颜色(schema color) 失败: {scheme_idx = }")

    @classmethod
    def ph_color_value(
        cls, raw_color: ColorTypes, ph_color: SchemeColor, slide: SlideTypes
    ):
        """处理占位符颜色以及相关的变换

        - raw_color: 要使用的颜色，定义的原始颜色值
        - ph_color: 占位符颜色, 为主题颜色(SchemaColor)，并且 color.value 为 phClr, 这里传进来，主要是要应用该颜色下面的其他属性, 比如: tint, mod, off, 等等属性

        """

        ph_color_mode = cls.color_mode(raw_color, slide)

        # 对颜色有更改/变换，比如色调，亮度，对比度等等
        has_color_transform = bool(raw_color.oxml.countchildren())  # type: ignore

        if has_color_transform and isinstance(ph_color_mode, (RGBAColor, HSLAColor)):
            logger.info(f"#{ph_color_mode = } 需要变换...")
            ph_color_mode = cls.transform_color(ph_color_mode, ph_color)

        if isinstance(ph_color_mode, RGBAColor):
            return f"#{ph_color_mode}"
        elif isinstance(ph_color_mode, HSLAColor):
            return str(ph_color_mode)
        else:
            return ph_color_mode

    @classmethod
    def color_mode(
        cls, color: ColorTypes, slide: SlideTypes, default: str = "transparent"
    ):
        """将颜色转换为str类型"""

        color_val: RGBAColor | HSLAColor | str = default

        if isinstance(color, ScrgbColor):
            color_val = RGBAColor(
                numpy.uint8(color.r * 100),
                numpy.uint8(color.g * 100),
                numpy.uint8(color.b * 100),
            )

        elif isinstance(color, HslColor):
            """html的hsl颜色值"""
            color_val = HSLAColor(
                numpy.uint16(color.attr_hue),
                numpy.float_(color.attr_sat),
                numpy.float_(color.attr_lum),
            )

        elif isinstance(color, SrgbColor):
            color_val = RGBAColor.from_string(color.value)

        elif isinstance(color, PresetColor):
            color_val = PresetColorValues[color.value.value].value

        elif isinstance(color, SystemColor):
            if color.last_color is not None:
                color_val = RGBAColor.from_string(color.last_color)

        elif isinstance(color, SchemeColor):
            # logger.debug(f"color为Schema(主题颜色): {color = }")

            if color.value == ST_SchemeColorVal.Placeholder:
                # 不处理占位符的颜色
                raise ValueError(
                    f"占位符颜色: {color}， 请使用ColorTool.ph_color_vale方法"
                )

            # 预期这里返回的color实例不是SchemeColor,
            # 也就是主题当中定义非 SchemeColor 的 其他类型Color
            color = cls.extract_schema_color(color, slide)
            color_val = cls.color_mode(color, slide)  # 回调，

        else:
            logger.warning(f"获取颜色值失败: {type(color) = } {color = }")
            color_val = default

        return color_val

    @classmethod
    def color_val(
        cls, color: ColorTypesRequire, slide: SlideTypes, default: str = "transparent"
    ):
        color_val = cls.color_mode(color, slide, default)

        # 对颜色有更改/变换，比如色调，亮度，对比度等等
        has_color_transform = bool(color.oxml.countchildren())  # type: ignore

        # 颜色要进行变换，
        if has_color_transform and isinstance(color_val, (RGBAColor, HSLAColor)):
            color_val = cls.transform_color(color_val, color)

        return color_val

    @classmethod
    def color_html(
        cls, color: ColorTypes, slide: SlideTypes, default: str = "transparent"
    ) -> str:
        """将 color 转化为 html 中 可用的值"""

        if color is None:
            return default

        color_val = cls.color_val(color, slide, default)

        if isinstance(color_val, RGBAColor):
            return f"#{color_val}"
        elif isinstance(color_val, HSLAColor):
            return str(color_val)
        else:
            return color_val

    @classmethod
    def color_svg(
        cls, color: ColorTypes, slide: SlideTypes, default: str = "transparent"
    ):
        """将 color 转化为 html 中 可用的值"""

        if color is None:
            return default

        color_val = cls.color_val(color, slide, default)

        if isinstance(color_val, RGBAColor):
            return color_val
        elif isinstance(color_val, HSLAColor):
            return TransformTool.hsl_to_rgb(color_val)
        else:
            return color_val

    @classmethod
    def transform_color(
        cls, color: RGBAColor | HSLAColor, raw_color: ColorTransformBase
    ):
        """变换颜色"""

        # logger.info(f"变换颜色: 【{color = }】 => {color}")
        # logger.info(raw_color.oxml.xml)

        result_color = color

        if raw_color.tint is not None:
            # 与 CT_PositiveFixedPercentage 类 表示的 tint 节点有冲突
            # 所以这里的值，通过 attrib["val"] 获取
            tint_raw_val = raw_color.tint.attrib["val"]
            tint_val = to_ST_PositiveFixedPercentage(str(tint_raw_val))
            result_color = TransformTool.tint(result_color, tint_val)

        if raw_color.shade is not None:
            result_color = TransformTool.shade(result_color, raw_color.shade.value)

        if raw_color.comp is not None:
            result_color = TransformTool.comp(result_color)

        if raw_color.inv is not None:
            result_color = TransformTool.inv(result_color)

        if raw_color.gray is not None:
            result_color = TransformTool.gray(result_color)

        if raw_color.alpha is not None:
            result_color = TransformTool.alpha(result_color, raw_color.alpha.value)

        if raw_color.alpha_mod is not None:
            result_color = TransformTool.alphaMod(
                result_color, raw_color.alpha_mod.value
            )

        if raw_color.alpha_off is not None:
            result_color = TransformTool.alphaOff(
                result_color, raw_color.alpha_off.value
            )

        if raw_color.red is not None:
            result_color = TransformTool.red(result_color, raw_color.red.value)

        if raw_color.red_mod is not None:
            result_color = TransformTool.redMod(result_color, raw_color.red_mod.value)

        if raw_color.red_off is not None:
            result_color = TransformTool.redOff(result_color, raw_color.red_off.value)

        if raw_color.green is not None:
            result_color = TransformTool.green(result_color, raw_color.green.value)

        if raw_color.green_mod is not None:
            result_color = TransformTool.greenMod(
                result_color, raw_color.green_mod.value
            )

        if raw_color.green_off is not None:
            result_color = TransformTool.greenOff(
                result_color, raw_color.green_off.value
            )

        if raw_color.blue is not None:
            result_color = TransformTool.blue(result_color, raw_color.blue.value)

        if raw_color.blue_mod is not None:
            result_color = TransformTool.blueMod(result_color, raw_color.blue_mod.value)

        if raw_color.blue_off is not None:
            result_color = TransformTool.blueOff(result_color, raw_color.blue_off.value)

        if raw_color.hue is not None:
            result_color = TransformTool.hue(
                result_color, numpy.uint16(raw_color.hue.value)
            )

        if raw_color.hue_mod is not None:
            result_color = TransformTool.hueMod(result_color, raw_color.hue_mod.value)

        if raw_color.hue_off is not None:
            result_color = TransformTool.hueOff(
                result_color, int(raw_color.hue_off.value)
            )

        if raw_color.sat is not None:
            result_color = TransformTool.sat(result_color, raw_color.sat.value)

        if raw_color.sat_mod is not None:
            result_color = TransformTool.satMod(result_color, raw_color.sat_mod.value)

        if raw_color.sat_off is not None:
            result_color = TransformTool.satOff(
                result_color, int(raw_color.sat_off.value)
            )

        if raw_color.lum is not None:
            result_color = TransformTool.lum(result_color, raw_color.lum.value)

        if raw_color.lum_mod is not None:
            result_color = TransformTool.lumMod(result_color, raw_color.lum_mod.value)

        if raw_color.lum_off is not None:
            result_color = TransformTool.lumOff(result_color, raw_color.lum_off.value)

        if raw_color.gamma is not None:
            result_color = TransformTool.gamma(result_color)

        if raw_color.inv_gamma is not None:
            result_color = TransformTool.invGamma(result_color)

        # logger.info(f"变换结果: 【{result_color = }】 => {result_color}")

        return result_color


class TransformTool:
    @classmethod
    def rgb_to_hsl(cls, color: RGBAColor):
        r, g, b, a = color

        r /= 255.0
        g /= 255.0
        b /= 255.0
        h, l, s = colorsys.rgb_to_hls(r, g, b)  # type: ignore
        h = numpy.uint16(h * 360)  # 将色相值从小数转换为0到360之间的整数
        # s = numpy.float_(s * 100)  # 将饱和度值从小数转换为0到100之间的整数
        # l = numpy.float_(l * 100)  # 将亮度值从小数转换为0到100之间的整数
        s = numpy.float_(s)  # 将饱和度值从小数转换为0到100之间的整数
        l = numpy.float_(l)  # 将亮度值从小数转换为0到100之间的整数
        return HSLAColor(h, s, l, a)

    @classmethod
    def hsl_to_rgb(cls, color: HSLAColor):
        h, s, l, a = color
        h /= 360.0
        # s /= 100.0
        # l /= 100.0
        r, g, b = colorsys.hls_to_rgb(h, l, s)  # type: ignore
        r = numpy.uint8(r * 255)  # 将红色分量值从小数转换为0到255之间的整数
        g = numpy.uint8(g * 255)  # 将绿色分量值从小数转换为0到255之间的整数
        b = numpy.uint8(b * 255)  # 将蓝色分量值从小数转换为0到255之间的整数
        return RGBAColor(r, g, b, a)

    @classmethod
    def _rgb(cls, color: RGBAColor | HSLAColor):
        if isinstance(color, HSLAColor):
            return cls.hsl_to_rgb(color)

        return color

    @classmethod
    def _hsl(cls, color: RGBAColor | HSLAColor):
        if isinstance(color, RGBAColor):
            return cls.rgb_to_hsl(color)

        return color

    @classmethod
    def tint(cls, color: RGBAColor | HSLAColor, val: float):
        """颜色的浅色版本

        参考: http://192.168.2.53:8001/openxml/ecma-part1/chapter20/main/basics/#2012334-tint-色调
        """

        r, g, b, a = cls._rgb(color)

        r = numpy.uint8(r * val + (1 - val) * 255)  # ff 白色
        g = numpy.uint8(g * val + (1 - val) * 255)
        b = numpy.uint8(b * val + (1 - val) * 255)

        return RGBAColor(r, g, b, a)

    @classmethod
    def shade(cls, color: RGBAColor | HSLAColor, val: float):
        """颜色的深色版本

        参考: http://192.168.2.53:8001/openxml/ecma-part1/chapter20/main/basics/#2012334-tint-色调
        """

        r, g, b, a = cls._rgb(color)

        r = numpy.uint8(r * val + (1 - val) * 0)  ## 00 黑色
        g = numpy.uint8(g * val + (1 - val) * 0)
        b = numpy.uint8(b * val + (1 - val) * 0)

        return RGBAColor(r, g, b, a)

    @classmethod
    def comp(cls, color: RGBAColor | HSLAColor):
        """颜色的补色"""

        rgb_color = cls._rgb(color)

        r = rgb_color.b
        g = rgb_color.r + rgb_color.b - rgb_color.g
        b = rgb_color.r

        return RGBAColor(r, g, b)

    @classmethod
    def inv(cls, color: RGBAColor | HSLAColor):
        """颜色的反色"""

        rgb_color = cls._rgb(color)

        percent_r = rgb_color.r / 255.0
        percent_g = rgb_color.g / 255.0
        percent_b = rgb_color.b / 255.0

        r = numpy.uint8(255 * abs(1.0 - percent_r))
        g = numpy.uint8(255 * abs(1.0 - percent_g))
        b = numpy.uint8(255 * abs(1.0 - percent_b))

        return RGBAColor(r, g, b)

    @classmethod
    def gray(cls, color: RGBAColor | HSLAColor):
        """颜色的灰度

        参考: https://www.cnblogs.com/ryzen/p/16370464.html#1680685485
        """

        rgb_color = cls._rgb(color)

        # 灰度系数
        gray = math.pow(
            math.pow(rgb_color.r, 2.2) * 0.2126
            + math.pow(rgb_color.g, 2.2) * 0.7152
            + math.pow(rgb_color.b, 2.2) * 0.0722,
            1 / 2.2,
        )

        gray_result = numpy.uint8(round(gray, 0))

        return RGBAColor(gray_result, gray_result, gray_result)

    @classmethod
    def alpha(cls, color: RGBAColor | HSLAColor, alpha: float):
        """颜色的透明度"""

        r, g, b, a = cls._rgb(color)

        return RGBAColor(r, g, b, numpy.float_(alpha))

    @classmethod
    def alphaMod(cls, color: RGBAColor | HSLAColor, percent: float):
        """蓝色调制"""

        r, g, b, a = cls._rgb(color)

        a *= percent

        if a > 1:  # 透明度 不会大于 1
            a = numpy.float_(1.0)

        if a < 0:  # 透明度 不会小于 0
            a = numpy.float_(0.0)

        return RGBAColor(r, g, b, a)

    @classmethod
    def alphaOff(cls, color: RGBAColor | HSLAColor, percent: float):
        """蓝色偏移"""

        r, g, b, a = cls._rgb(color)

        a += percent

        if a > 1:  # 透明度 不会大于 1
            a = numpy.float_(1.0)

        if a < 0:  # 透明度 不会小于 0
            a = numpy.float_(0.0)

        a = numpy.float_(a)

        return RGBAColor(r, g, b, a)

    @classmethod
    def red(cls, color: RGBAColor | HSLAColor, percent: float):
        """红色替换"""

        r, g, b, a = cls._rgb(color)

        return RGBAColor(numpy.uint8(255 * percent), g, b, a)

    @classmethod
    def redMod(cls, color: RGBAColor | HSLAColor, percent: float):
        """红色调制"""

        r, g, b, a = cls._rgb(color)

        r *= percent

        if r > 255:  # 红色不会超过 255
            r = 255

        if r < 0:  # 红色不会底于 0
            r = 0

        r = numpy.uint8(r)

        return RGBAColor(r, g, b, a)

    @classmethod
    def redOff(cls, color: RGBAColor | HSLAColor, percent: float):
        """红色偏移"""

        r, g, b, a = cls._rgb(color)

        r += r * percent

        if r > 255:  # 红色不会超过 255
            r = 255

        if r < 0:  # 红色不会底于 0
            r = 0

        r = numpy.uint8(r)

        return RGBAColor(r, g, b, a)

    @classmethod
    def green(cls, color: RGBAColor | HSLAColor, green: float):
        """蓝色替换"""

        r, g, b, a = cls._rgb(color)

        return RGBAColor(r, numpy.uint8(255 * green), b, a)

    @classmethod
    def greenMod(cls, color: RGBAColor | HSLAColor, percent: float):
        """绿色调制"""

        r, g, b, a = cls._rgb(color)

        g *= percent

        if g > 255:  # 绿色不会超过 255
            g = 255

        if g < 0:  # 绿色不会底于 0
            g = 0

        g = numpy.uint8(g)

        return RGBAColor(r, g, b, a)

    @classmethod
    def greenOff(cls, color: RGBAColor | HSLAColor, percent: float):
        """绿色偏移"""

        r, g, b, a = cls._rgb(color)

        g += g * percent

        if g > 255:  # 绿色不会超过 255
            g = 255

        if g < 0:  # 绿色不会底于 0
            g = 0

        g = numpy.uint8(g)

        return RGBAColor(r, g, b, a)

    @classmethod
    def blue(cls, color: RGBAColor | HSLAColor, percent: float):
        """蓝色替换"""

        r, g, b, a = cls._rgb(color)

        return RGBAColor(r, g, numpy.uint8(255 * percent), a)

    @classmethod
    def blueMod(cls, color: RGBAColor | HSLAColor, percent: float):
        """蓝色调制"""

        r, g, b, a = cls._rgb(color)

        b *= percent

        if b > 255:  # 蓝色不会超过 255
            b = 255

        if b < 0:  # 蓝色不会底于 0
            b = 0

        b = numpy.uint8(b)

        return RGBAColor(r, g, b, a)

    @classmethod
    def blueOff(cls, color: RGBAColor | HSLAColor, percent: float):
        """蓝色偏移"""

        r, g, b, a = cls._rgb(color)

        b += b * percent

        if b > 255:  # 蓝色不会超过 255
            b = 255

        if b < 0:  # 蓝色不会底于 0
            b = 0

        b = numpy.uint8(b)

        return RGBAColor(r, g, b, a)

    @classmethod
    def hue(cls, color: RGBAColor | HSLAColor, hue: numpy.uint16):
        """颜色的色调 mod"""

        h, s, l, a = cls._hsl(color)

        return cls._rgb(HSLAColor(hue, s, l, a))

    @classmethod
    def hueMod(cls, color: RGBAColor | HSLAColor, mod: float):
        """色调调试"""

        h, s, l, a = cls._hsl(color)

        h *= mod

        if h > 360:  # 角度不会大于360
            h = 360

        if h < 0:  # 角度不会小于0
            h = 0

        h = numpy.uint16(h)

        return cls._rgb(HSLAColor(h, s, l, a))

    @classmethod
    def hueOff(cls, color: RGBAColor | HSLAColor, off: int):
        """色调偏移"""

        h, s, l, a = cls._hsl(color)

        h += off

        if h > 360:  # 角度不会大于360
            h = 360

        if h < 0:  # 角度不会小于0
            h = 0

        h = numpy.uint16(h)

        return cls._rgb(HSLAColor(h, s, l, a))

    @classmethod
    def sat(cls, color: RGBAColor | HSLAColor, percent: float):
        """颜色的亮度 mod"""

        h, s, l, a = cls._hsl(color)

        return cls._rgb(HSLAColor(h, numpy.float_(percent), l, a))

    @classmethod
    def satMod(cls, color: RGBAColor | HSLAColor, percent: float):
        """颜色的亮度 mod"""

        h, s, l, a = cls._hsl(color)

        s *= percent

        if s > 1:  # 亮度不会超过100
            s = 1

        if s < 0:  # 亮度不会底于0
            s = 0

        return cls._rgb(HSLAColor(h, numpy.float_(s), l, a))

    @classmethod
    def satOff(cls, color: RGBAColor | HSLAColor, percent: float):
        """颜色的亮度 mod"""

        h, s, l, a = cls._hsl(color)

        s += percent

        if s > 1:  # 亮度不会超过100
            s = 1

        if s < 0:  # 亮度不会底于0%
            s = 0

        return cls._rgb(HSLAColor(h, numpy.float_(s), l, a))

    @classmethod
    def lum(cls, color: RGBAColor | HSLAColor, percent: float):
        """颜色的亮度替换"""

        h, s, l, a = cls._hsl(color)

        return cls._rgb(HSLAColor(h, s, numpy.float_(percent), a))

    @classmethod
    def lumMod(cls, color: RGBAColor | HSLAColor, percent: float):
        """颜色的亮度 mod"""

        # logger.info(f"lumMod: {percent = }")

        h, s, l, a = cls._hsl(color)

        l *= percent

        if l > 1:  # 亮度不会超过100
            l = 1

        if l < 0:  # 亮度不会底于0%
            l = 0

        return cls._rgb(HSLAColor(h, s, numpy.float_(l), a))

    @classmethod
    def lumOff(cls, color: RGBAColor | HSLAColor, percent: float):
        """颜色的亮度 mod"""

        # logger.info(f"lumOff: {percent = }")

        h, s, l, a = cls._hsl(color)

        l += percent

        if l > 1:  # 亮度不会超过100
            l = 1

        if l < 0:  # 亮度不会底于0
            l = 0

        return cls._rgb(HSLAColor(h, s, numpy.float_(l), a))

    @classmethod
    def gamma(cls, color: RGBAColor | HSLAColor):
        """伽马矫正"""

        rgb_color = cls._rgb(color)

        r = math.pow(rgb_color.r / 255.0, 1 / 2.2)
        g = math.pow(rgb_color.g / 255.0, 1 / 2.2)
        b = math.pow(rgb_color.b / 255.0, 1 / 2.2)

        return RGBAColor(numpy.uint8(r), numpy.uint8(g), numpy.uint8(b), rgb_color.a)

    @classmethod
    def invGamma(cls, color: RGBAColor | HSLAColor):
        rgb_color = cls._rgb(color)

        r = math.pow(rgb_color.r / 255.0, 2.2)
        g = math.pow(rgb_color.g / 255.0, 2.2)
        b = math.pow(rgb_color.b / 255.0, 2.2)

        return RGBAColor(numpy.uint8(r), numpy.uint8(g), numpy.uint8(b), rgb_color.a)

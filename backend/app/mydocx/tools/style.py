from typing import Any

from loguru import logger

from ms_office.oxml.shared.common_simple_types import ST_VerticalAlignRun
from ms_office.oxml.wml.main import (
    # 边框
    CT_Border,
    CT_PPrBase,
    # 表格样式
    CT_Tbl,
    CT_TblPrBase,
    # 宽度单位
    CT_TblWidth,
    # 单元格样式
    CT_TcPr,
    # 行(Row)样式
    CT_TrPr,
    EG_RPrContent,
    ST_Border,
    ST_Em,
    ST_HeightRule,
    ST_HexColorAuto,
    ST_HighlightColor,
    ST_Jc,
    ST_JcTable,
    ST_LineSpacingRule,
    # 单元格合并类型
    ST_Merge,
    ST_StyleType,
    ST_TblStyleOverrideType,
    ST_TblWidth,
    # 文本方向
    ST_TextDirection,
    # 垂直对齐方式
    ST_VerticalJc,
)
from ms_office.wml.styles import Styles

# ----------- 边框样式转换 -------------


def ct_tblwidth2html(width: CT_TblWidth):
    """将宽度转换为html值"""

    val = "0"

    if width.type == ST_TblWidth.dxa and width.w is not None:
        _w = int(width.w)
        if _w:
            val = f"{int(width.w) / 20}pt"
        else:
            val = None

    elif width.type == ST_TblWidth.auto:
        val = "auto"

    elif width.type == ST_TblWidth.pct and width.w is not None:
        val = width.w

    elif width.type == ST_TblWidth.nil:
        val = "0%"

    return val


def ct_boder2html(bdr: CT_Border):
    """转换边框样式

    https://developer.mozilla.org/en-US/docs/Web/CSS/border
    """

    if bdr.val_border is None:
        return "none"

    # 无边框
    if bdr.val_border in (ST_Border.Nil, ST_Border.none):
        return "none"

    bdr_width = "0.25pt"
    bdr_style = "solid"
    bdr_color = "black"

    # 边框样式

    # https://developer.mozilla.org/en-US/docs/Web/CSS/line-style
    if bdr.val_border == ST_Border.Single:
        bdr_style = "solid"

    elif bdr.val_border in (ST_Border.DotDash, ST_Border.DotDotDash, ST_Border.Dotted):
        bdr_style = "dotted"

    elif bdr.val_border in (
        ST_Border.DashDotStroked,
        ST_Border.Dashed,
        ST_Border.DashSmallGap,
    ):
        bdr_style = "dashed"

    elif bdr.val_border in (ST_Border.Double, ST_Border.Double, ST_Border.DashSmallGap):
        bdr_style = "double"

    else:
        bdr_style = "solid"

    # 边框宽度
    if bdr.size is not None:
        bdr_width = f"{bdr.size / 8}pt"

    # 边框颜色
    if bdr.color is not None:
        if bdr.color == ST_HexColorAuto.Auto:
            bdr_color = "black"  # "auto"
        else:
            bdr_color = f"#{bdr.color}"

    return f"{bdr_width} {bdr_style} {bdr_color}"


# ------------ 段落样式转换 ------------


def paragraph_ct_style2html(
    ppr: CT_PPrBase,
    character_styles: dict[str, Any],
    paragraph_styles: dict[str, Any] | None = None,
):
    """将xml的段落样式转化为html支持的样式"""

    if paragraph_styles is None:
        paragraph_styles = {}

    # 段落对齐方式
    # https://developer.mozilla.org/en-US/docs/Web/CSS/text-align
    if ppr.jc is not None:
        if ppr.jc.val_jc.value == ST_Jc.both.value:
            paragraph_styles["text-align"] = "justify"  # 段落的字体位置分布

        else:
            paragraph_styles["text-align"] = ppr.jc.val_jc.value

    # 段落间距
    if ppr.spacing is not None:
        # 行高， 段落的行高要传递给子元素，但是本身不保留
        # https://developer.mozilla.org/en-US/docs/Web/CSS/line-height
        if ppr.spacing.line is not None and ppr.spacing.line != 0:
            if ppr.spacing.lineRule == ST_LineSpacingRule.auto:
                # logger.info(f"自动行高{ppr.spacing.line = }")
                # logger.info(f"自动行高{ppr.spacing.line / 12 = }")
                # <w:spacing w:line="360" w:lineRule="auto"/>
                paragraph_styles["line-height"] = f"{ppr.spacing.line / 12}"
            elif ppr.spacing.lineRule == ST_LineSpacingRule.exact:
                paragraph_styles["line-height"] = f"{ppr.spacing.line}pt"
            elif ppr.spacing.lineRule == ST_LineSpacingRule.atLeast:
                paragraph_styles["min-line-height"] = f"{ppr.spacing.line}pt"

        # 段前间距， 使用margin表示，因为margin空间共享，
        # “该段落的第一行上方必须至少有 80 个点的间距，尽管实际间距可以由行间距或前一个段落的最后一行下方的间距中的较大者确定。”
        if ppr.spacing.before is not None:
            paragraph_styles["margin-top"] = f"{ppr.spacing.before}pt"

            if ppr.spacing.beforeLines:
                font_size = character_styles.get("font-size", "12pt")
                line_height = paragraph_styles.get("line-height", "12pt")

                base_val = max((float(font_size[0:-2]), float(line_height[0:-2])))

                # logger.info(f"{ppr.spacing.beforeLines = }")

                befoe_lines = base_val * (ppr.spacing.beforeLines / 100)

                paragraph_styles["margin-top"] = f"{befoe_lines}pt"

            if ppr.spacing.beforeAutospacing:
                paragraph_styles["margin-top"] = "auto"

        # 段后间距， margin可以应用两个两个段落之间最大间距者确定
        if ppr.spacing.after is not None:
            paragraph_styles["margin-bottom"] = f"{ppr.spacing.after}pt"

            if ppr.spacing.afterLines:
                font_size = character_styles.get("font-size", "12pt")
                line_height = paragraph_styles.get("line-height", "12pt")

                base_val = max((float(font_size[0:-2]), float(line_height[0:-2])))

                befoe_lines = base_val * (ppr.spacing.afterLines / 100)

                paragraph_styles["margin-bottom"] = f"{befoe_lines}pt"

            if ppr.spacing.afterAutospacing:
                paragraph_styles["margin-bottom"] = "auto"

    # 段落缩进
    if ppr.ind is not None:
        # 段落开始缩进， 左边距
        if ppr.ind.start:
            paragraph_styles["padding-top"] = f"{ppr.ind.start}pt"

        # 段落结束缩进， 右边距
        if ppr.ind.end:
            paragraph_styles["padding-bottom"] = f"{ppr.ind.end}pt"

        # 段落开始缩进， 左边距
        # 段落缩进
        if ppr.ind.left:
            padding_left = ppr.ind.left

            if ppr.ind.hanging:
                padding_left = ppr.ind.left - ppr.ind.hanging

            paragraph_styles["padding-left"] = f"{padding_left}pt"

            if ppr.ind.leftChars is not None:
                if ppr.ind.leftChars == 0:
                    paragraph_styles.pop("padding-left")
                else:
                    paragraph_styles["padding-left"] = f"{ppr.ind.leftChars / 20}pt"

        # 段落开始缩进， 右边距
        if ppr.ind.right:
            paragraph_styles["padding-right"] = f"{ppr.ind.right}pt"

        # 首行缩进, 跟三个属性相关，分别是: firstLine, firstLineChars, hanging
        # https://developer.mozilla.org/en-US/docs/Web/CSS/text-indent
        # <w:ind w:firstLine="883" w:firstLineChars="200"/>

        if ppr.ind.firstLine is not None:
            text_indent = ppr.ind.firstLine

            if ppr.ind.hanging:
                text_indent = ppr.ind.firstLine - ppr.ind.hanging

            paragraph_styles["text-indent"] = f"{text_indent}pt"

        # firstLineChars 可以覆盖 firstLine 的值
        if ppr.ind.firstLineChars is not None:
            # logger.info(f"段落首行缩进: {ppr.ind.firstLineChars = }")
            if ppr.ind.firstLineChars in (0, 0.0):
                # logger.info(f"段落首行无缩进: {ppr.ind.firstLineChars = }")
                paragraph_styles.pop("text-indent", None)
            else:
                font_size = character_styles.get("font-size", "12pt")
                chars = ppr.ind.firstLineChars / 100
                # logger.info(f"段落首行缩进: {chars = }")
                text_indent = f"{float(font_size[:-2]) * chars}pt"
                paragraph_styles["text-indent"] = text_indent

    # 段落边框
    if ppr.pBdr is not None:
        if ppr.pBdr.top is not None:
            paragraph_styles["border-top"] = ct_boder2html(ppr.pBdr.top)

        if ppr.pBdr.right is not None:
            paragraph_styles["border-right"] = ct_boder2html(ppr.pBdr.right)

        if ppr.pBdr.bottom is not None:
            paragraph_styles["border-bottom"] = ct_boder2html(ppr.pBdr.bottom)

        if ppr.pBdr.left is not None:
            paragraph_styles["border-left"] = ct_boder2html(ppr.pBdr.left)

    # 上下文边距, 针对列表
    # http://192.168.2.53:8001/openxml/ecma-part1/chapter17/03paragraphs/#17319-contextualspacing-使用相同样式时忽略上方和下方的间距
    # 这里后续要特殊处理.
    if ppr.contextualSpacing is not None:
        paragraph_styles["contextualSpacing"] = ppr.contextualSpacing.is_on

    # 段落底纹(背景)
    if ppr.shd is not None and ppr.shd.color is not None:
        paragraph_styles["background-color"] = f"#{ppr.shd.color}"

    # 段落边框
    if ppr.pBdr is not None:
        if ppr.pBdr.top is not None:
            paragraph_styles["border-top"] = ct_boder2html(ppr.pBdr.top)

        if ppr.pBdr.right is not None:
            paragraph_styles["border-right"] = ct_boder2html(ppr.pBdr.right)

        if ppr.pBdr.bottom is not None:
            paragraph_styles["border-bottom"] = ct_boder2html(ppr.pBdr.bottom)

        if ppr.pBdr.left is not None:
            paragraph_styles["border-left"] = ct_boder2html(ppr.pBdr.left)

    # 上下文边距, 针对列表
    # http://192.168.2.53:8001/openxml/ecma-part1/chapter17/03paragraphs/#17319-contextualspacing-使用相同样式时忽略上方和下方的间距
    # 这里后续要特殊处理.
    if ppr.contextualSpacing is not None:
        paragraph_styles["contextualSpacing"] = ppr.contextualSpacing.is_on

    # 段落底纹(背景)
    if ppr.shd is not None and ppr.shd.color is not None:
        paragraph_styles["background-color"] = f"#{ppr.shd.color}"

    # 段落边框
    if ppr.pBdr is not None:
        if ppr.pBdr.top is not None:
            paragraph_styles["border-top"] = ct_boder2html(ppr.pBdr.top)

        if ppr.pBdr.right is not None:
            paragraph_styles["border-right"] = ct_boder2html(ppr.pBdr.right)

        if ppr.pBdr.bottom is not None:
            paragraph_styles["border-bottom"] = ct_boder2html(ppr.pBdr.bottom)

        if ppr.pBdr.left is not None:
            paragraph_styles["border-left"] = ct_boder2html(ppr.pBdr.left)

    # 上下文边距, 针对列表
    # http://192.168.2.53:8001/openxml/ecma-part1/chapter17/03paragraphs/#17319-contextualspacing-使用相同样式时忽略上方和下方的间距
    # 这里后续要特殊处理.
    if ppr.contextualSpacing is not None:
        paragraph_styles["contextualSpacing"] = ppr.contextualSpacing.is_on

    # 段落底纹(背景)
    if ppr.shd is not None and ppr.shd.color is not None:
        paragraph_styles["background-color"] = f"#{ppr.shd.color}"

    # 其他段落属性，css不支持.

    return paragraph_styles


def character_ct_style2html(rpr: EG_RPrContent, styles: dict[str, Any] | None = None):
    """将xml的字符(run)样式转化为html支持的样式"""

    if styles is None:
        styles = {}

    # 引用的字符样式， 要从docx.styles 中获取并解析
    # if rpr.rStyle is not None:
    #     logger.info(f"未处理的字符样式引用！")

    # 字体名称, 可能浏览器不支持，先忽略
    if rpr.rFonts is not None:
        font_family = rpr.rFonts.eastAsia or rpr.rFonts.ascii

        if font_family:
            styles["font-family"] = font_family

    # 粗体
    # https://developer.mozilla.org/en-US/docs/Web/CSS/font-weight
    if rpr.bold is not None:
        if rpr.bold.is_on:
            styles["font-weight"] = "bold"

        if rpr.bold.is_off:
            styles["font-weight"] = "normal"

    # 斜体
    # https://developer.mozilla.org/en-US/docs/Web/CSS/font-style
    if rpr.italic is not None:
        if rpr.italic.is_on:
            styles["font-style"] = "italic"

        if rpr.italic.is_off:
            styles["font-style"] = "normal"

    # 全大写
    # https://developer.mozilla.org/en-US/docs/Web/CSS/text-transform
    if rpr.caps is not None:
        if rpr.caps.is_on:
            styles["text-transform"] = "uppercase"

        if rpr.caps.is_off:
            styles["text-transform"] = "none"

    # 小号大写
    # https://developer.mozilla.org/en-US/docs/Web/CSS/font-variant
    if rpr.smallCaps is not None:
        if rpr.smallCaps.is_on:
            styles["font-variant"] = "small-caps"

        if rpr.smallCaps.is_off:
            styles["font-variant"] = "none"

    # 删除线
    # https://developer.mozilla.org/en-US/docs/Web/CSS/text-decoration-line

    text_decoration_line = []

    if rpr.strike is not None:
        if rpr.strike.is_on:
            # styles["text-decoration-line"] = 'line-through'
            text_decoration_line.append("line-through")

        # if rpr.strike.is_off:
        #     text_decoration_line.remove('line-through', )

    # 双删除线
    # https://developer.mozilla.org/en-US/docs/Web/CSS/text-decoration-style
    # 这里共用 css 属性 text-decoration-line 可能会导致问题
    # 比如:
    # <p style="text-decoration-line: line-through underline; text-decoration-style: double; "> this is test text</p>

    if rpr.dstrike is not None:
        if rpr.dstrike.is_on:
            styles["text-decoration-style"] = "double"

        if rpr.dstrike.is_off:
            styles["text-decoration-style"] = "solid"

    # 显示文字边框
    # css 不支持
    if rpr.outline is not None:
        ...

    # 文字阴影
    # https://developer.mozilla.org/en-US/docs/Web/CSS/text-shadow
    if rpr.shadow is not None:
        if rpr.shadow.is_on:
            # /* offset-x | offset-y | blur-radius | color */
            styles["text-shadow"] = "1px 1px 2px black"

        if rpr.shadow.is_off:
            styles["text-shadow"] = "none"

    # 浮雕效果
    # css 不支持
    if rpr.emboss is not None:
        ...

    # 压印效果
    # css 不支持
    if rpr.imprint is not None:
        ...

    # 不检查拼写
    # qn("w:noProof"),  # CT_OnOff
    if rpr.noProof is not None:
        ...

    # 使用文档网格设置来设置字符间距
    # qn("w:snapToGrid"),  # CT_OnOff
    if rpr.snapToGrid is not None:
        ...

    # 隐藏文本
    # qn("w:vanish"),  # CT_OnOff
    # https://developer.mozilla.org/en-US/docs/Web/CSS/content-visibility
    if rpr.vanish is not None:
        if rpr.vanish.is_on:
            styles["content-visibility"] = "hidden"
        elif rpr.vanish.is_off:
            styles["content-visibility"] = "visible"

    # 网页隐藏文本
    # qn("w:webHidden"),  # CT_OnOff
    if rpr.webHidden is not None:
        ...

    # 字体颜色
    # qn("w:color"),  # CT_Color
    # https://developer.mozilla.org/en-US/docs/Web/CSS/color
    if rpr.color is not None:
        styles["color"] = (
            f"#{rpr.color.val}" if rpr.color.val != ST_HexColorAuto.Auto else "black"
        )

    # 字符间距
    # qn("w:spacing"),  # CT_SignedTwipsMeasure
    # https://developer.mozilla.org/en-US/docs/Web/CSS/letter-spacing
    if rpr.spacing is not None:
        # 当字符间距小于0时， html渲染容易让很多字在1个位置堆着
        if rpr.spacing.val and rpr.spacing.val > 0:
            # logger.info(f"{rpr.spacing.xml}  => {rpr.spacing.val}pt")
            styles["letter-spacing"] = f"{rpr.spacing.val}pt"

    # 字符大小扩展
    # css 不支持
    # https://developer.mozilla.org/zh-CN/docs/Web/CSS/text-size-adjust
    # qn("w:w"),  # CT_TextScale
    if rpr.w is not None:
        ...

    # 字体字距调整
    # qn("w:kern"),  # CT_HpsMeasure
    # https://developer.mozilla.org/en-US/docs/Web/CSS/font-kerning
    if rpr.kern is not None:
        styles["font-kerning"] = "normal"

    # 垂直升高或降低文本
    # qn("w:position"),  # CT_SignedHpsMeasure
    # https://developer.mozilla.org/en-US/docs/Web/CSS/vertical-align
    if rpr.position is not None:
        ...

    # 非复杂脚本字体大小
    # qn("w:sz"),  # CT_HpsMeasure
    # https://developer.mozilla.org/en-US/docs/Web/CSS/font-size
    if rpr.size is not None:
        styles["font-size"] = f"{rpr.size.val_hps_measure}pt"

    # qn("w:szCs"),  # CT_HpsMeasure

    # 文本突出显示(高亮显示颜色)
    # qn("w:highlight"),  # CT_Highlight
    # https://developer.mozilla.org/en-US/docs/Web/CSS/background-color
    if rpr.highlight is not None:
        if rpr.highlight.val.value == ST_HighlightColor.DarkYellow:
            styles["background-color"] = "#808000"
        else:
            styles["background-color"] = f"{rpr.highlight.val.value}"

    # 下划线
    # qn("w:u"),  # CT_Underline
    # https://developer.mozilla.org/en-US/docs/Web/CSS/text-decoration-line
    if rpr.underline is not None:
        text_decoration_line.append("underline")

    # 封装跟下划线相关的属性
    if text_decoration_line:
        styles["text-decoration-line"] = " ".join(text_decoration_line)

    # 字符效果
    # qn("w:effect"),  # CT_TextEffect
    # css 不支持
    if rpr.effect is not None:
        ...

    # 边框
    # qn("w:bdr"),  # CT_Border
    # https://developer.mozilla.org/en-US/docs/Web/CSS/border
    if rpr.border is not None:
        border_styles = []
        if rpr.border.size is not None:
            border_styles.append(f"{rpr.border.size / 8}pt")
            border_styles.append("solid")

        if rpr.border.color and rpr.border.color != ST_HexColorAuto.Auto:
            border_styles.append(f"#{rpr.border.color}")

        if border_styles:
            styles["border-style"] = " ".join(border_styles)

    # 底纹图案着色
    # qn("w:shd"),  # CT_Shd
    # css 不支持
    if rpr.shd is not None:
        ...

    # 手动运行宽度
    # qn("w:fitText"),  # CT_FitText
    if rpr.fitText is not None:
        ...

    # 下标/上标文本
    # qn("w:vertAlign"),  # CT_VerticalAlignRun
    if rpr.vertAlign is not None:
        if rpr.vertAlign.val == ST_VerticalAlignRun.Superscript:
            styles["vertical-align"] = "supper"
        elif rpr.vertAlign.val == ST_VerticalAlignRun.Subscript:
            styles["vertical-align"] = "sub"

        elif rpr.vertAlign.val == ST_VerticalAlignRun.Baseline:
            styles["vertical-align"] = "baseline"

    # 文本方向
    # qn("w:rtl"),  # CT_OnOff
    # https://developer.mozilla.org/en-US/docs/Glossary/RTL
    # https://developer.mozilla.org/en-US/docs/Web/CSS/direction
    if rpr.rtl is not None:
        if rpr.rtl.is_on:
            styles["direction"] = "rtl"
        elif rpr.rtl.is_off:
            styles["direction"] = "ltr"

    # 在运行时使用复杂的脚本格式
    # qn("w:cs"),  # CT_OnOff
    if rpr.cs is not None:
        ...

    # 强调标记
    # qn("w:em"),  # CT_Em
    # https://developer.mozilla.org/en-US/docs/Web/CSS/text-emphasis
    if rpr.em is not None:
        if rpr.em.val == ST_Em.none:
            styles["text-emphasis"] = "none"

        elif rpr.em.val == ST_Em.Circle:
            styles["text-emphasis"] = "circle red"

        elif rpr.em.val == ST_Em.Comma:
            styles["text-emphasis"] = "sesame red"

        elif rpr.em.val == ST_Em.Dot:
            styles["text-emphasis"] = "dot red"

        elif rpr.em.val == ST_Em.UnderDot:
            styles["text-emphasis"] = "dot red"
            styles["text-emphasis-position"] = "under"

    # 运行内容的语言
    # qn("w:lang"),  # CT_Language
    # https://developer.mozilla.org/zh-CN/docs/Web/CSS/font-language-override
    if rpr.lang is not None:
        ...

    # 东亚版式设置
    # qn("w:eastAsianLayout"),  # CT_EastAsianLayout
    if rpr.eastAsianLayout is not None:
        ...

    # 段落标记始终隐藏
    # qn("w:specVanish"),  # CT_OnOff
    if rpr.specVanish is not None:
        ...

    # Office Open XML 数学
    # qn("w:oMath"),  # CT_OnOff
    if rpr.oMath is not None:
        ...

    return styles


# -------- 段落、字符样式提取 -----------


def get_docx_default_paragraph_style(styls: Styles, character_styles: dict[str, Any]):
    """获取文档的默认段落样式"""

    paragrah_styles: dict[str, Any] = {}

    if (
        styls.doc_defaults is not None
        and styls.doc_defaults.pPrDefault is not None
        and styls.doc_defaults.pPrDefault.pPr is not None
    ):
        paragraph_ct_style2html(
            styls.doc_defaults.pPrDefault.pPr, character_styles, paragrah_styles
        )

    # <style>标签的默认段落样式
    if (
        styls.paragrah_style_default is not None
        and styls.paragrah_style_default.pPr is not None
    ):
        paragraph_ct_style2html(
            styls.paragrah_style_default.pPr, character_styles, paragrah_styles
        )

    return paragrah_styles


def get_docx_default_character_style(styls: Styles):
    """获取文档的默认字符(run)样式"""

    html_styles: dict[str, Any] = {}

    if (
        styls.doc_defaults is not None
        and styls.doc_defaults.rPrDefault is not None
        and styls.doc_defaults.rPrDefault.rPr is not None
    ):
        character_ct_style2html(styls.doc_defaults.rPrDefault.rPr, html_styles)

    # <style>标签的默认字符样式
    if (
        styls.paragrah_style_default is not None
        and styls.paragrah_style_default.rPr is not None
    ):
        character_ct_style2html(styls.paragrah_style_default.rPr, html_styles)

    # <style>标签的默认字符样式
    if (
        styls.character_style_default is not None
        and styls.character_style_default.rPr is not None
    ):
        character_ct_style2html(styls.character_style_default.rPr, html_styles)

    return html_styles


def get_paragraph_styles_from_define(
    styles: Styles,
    style_id: str,
    character_styles: dict[str, Any],
    paragrah_styles: dict[str, Any] | None = None,
):
    """获取段落样式树中的最终样式"""

    # logger.info(f"获取样式ID为: { style_id } 的样式")

    ct_styles = styles.get_styles(style_id)

    if paragrah_styles is None:
        paragrah_styles = {}

    for ct_style in ct_styles:
        if ct_style.type != ST_StyleType.paragraph:
            logger.info(f"忽略非段落样式: {ct_style}")
            continue

        # 处理继承的样式
        if ct_style.basedOn is not None:
            parent_style_id = ct_style.basedOn.val_str
            get_paragraph_styles_from_define(
                styles, parent_style_id, character_styles, paragrah_styles
            )
            # logger.info(f"处理父样式: {[parent_style_id]} -> {paragrah_styles}")

        if ct_style.pPr is not None:
            paragraph_ct_style2html(ct_style.pPr, character_styles, paragrah_styles)

        else:
            if ct_style.name is not None:
                # logger.info(f"忽略段落样式: {ct_style.name.val_str or ''}")
                ...
            else:
                # logger.info(f"忽略段落样式: {ct_style.xml}")
                ...

    # logger.info(f"样式ID为: { style_id } 的样式: {paragrah_styles}")

    return paragrah_styles


def get_character_styles_from_define(
    styles: Styles, style_id: str, character_styles: dict[str, Any] | None = None
):
    """获取字符样式树中的最终样式"""

    ct_styles = styles.get_styles(style_id)

    if character_styles is None:
        character_styles = {}

    for ct_style in ct_styles:
        if ct_style.type not in (ST_StyleType.paragraph, ST_StyleType.character):
            logger.info(f"忽略非字符段落样式: {ct_style}")
            continue

        if ct_style.rPr is not None:
            character_ct_style2html(ct_style.rPr, character_styles)

        else:
            if ct_style.name is not None:
                # logger.info(f"忽略字符样式: {ct_style.name.val_str or ''}")
                ...
            else:
                # logger.info(f"忽略字符样式: {ct_style.xml}")
                ...

    # logger.info(f"样式ID为: { style_id } 的字符(run)样式: {character_styles}")

    return character_styles


# ---- 表格样式 -----


def get_table_styles_from_define(
    styles: Styles, style_id: str, html_styles: dict[str, Any] | None = None
):
    """获取表格样式树中的表格样式"""

    # logger.info(f"获取样式ID为: { style_id } 的样式")

    ct_styles = styles.get_styles(style_id)

    # 表格(Table)的样式
    if html_styles is None:
        html_styles = {
            # https://developer.mozilla.org/zh-CN/docs/Web/CSS/border-spacing
            "border-spacing": "0",  # 浏览器默认边框间距设为0
            # https://developer.mozilla.org/zh-CN/docs/Web/CSS/border-collapse
            "border-collapse": "collapse",  # 表格边框属于合并还是分开模式, 浏览器默认分开模式.
        }

    for ct_style in ct_styles:
        if ct_style.type != ST_StyleType.table:
            logger.info(f"忽略非表格样式: {ct_style}")
            continue

        if ct_style.tblPr is not None:
            get_table_styles(ct_style.tblPr, html_styles)

    # logger.info(f"表格样式ID为: { style_id } 的table样式: {html_styles}")

    return html_styles


def get_cell_styles_from_define(
    styles: Styles, style_id: str, html_styles: dict[str, Any] | None = None
):
    """获取单元格的样式"""

    # logger.info(f"获取样式ID为: { style_id } 的单元格样式")

    ct_styles = styles.get_styles(style_id)

    # 表格(Table)的样式
    if html_styles is None:
        html_styles = {}

    for ct_style in ct_styles:
        if ct_style.type != ST_StyleType.table:
            logger.info(f"忽略非表格样式: {ct_style}")
            continue

        if ct_style.tblPr is not None:
            get_table_cell_default_styls(ct_style.tblPr, html_styles)

    # logger.info(f"表格样式ID为: { style_id } 的cell样式: {html_styles}")

    return html_styles


def get_table_paragraph_styles_from_define(
    styles: Styles,
    style_id: str,
    character_styles: dict[str, Any],
    html_styles: dict[str, Any] | None = None,
):
    """获取表格中的段落样式"""

    # logger.info(f"获取表格样式ID为: { style_id } 的段落样式")

    ct_styles = styles.get_styles(style_id)

    # 表格(Table)的样式
    if html_styles is None:
        html_styles = {}

    for ct_style in ct_styles:
        if ct_style.type != ST_StyleType.table:
            logger.info(f"忽略非表格样式: {ct_style}")
            continue

        if ct_style.pPr is not None:
            paragraph_ct_style2html(ct_style.pPr, character_styles, html_styles)

    # logger.info(f"表格样式ID为: { style_id } 的段落样式: {html_styles}")

    return html_styles


def get_table_character_styles_from_define(
    styles: Styles, style_id: str, html_styles: dict[str, Any] | None = None
):
    """获取表格中的字符样式"""

    # logger.info(f"获取表格样式ID为: { style_id } 的字符样式")

    ct_styles = styles.get_styles(style_id)

    # 表格(Table)的样式
    if html_styles is None:
        html_styles = {}

    for ct_style in ct_styles:
        if ct_style.type != ST_StyleType.table:
            # logger.info(f"忽略非表格样式: {ct_style}")
            continue

        if ct_style.rPr is not None:
            character_ct_style2html(ct_style.rPr, html_styles)

    # logger.info(f"表格样式ID为: { style_id } 的字符样式: {html_styles}")

    return html_styles


def get_firstrow_styles_from_define(
    styles: Styles,
    style_id: str,
    paragraph_styles: dict[str, Any] | None = None,
    character_styles: dict[str, Any] | None = None,
    row_styles: dict[str, Any] | None = None,
    cell_styles: dict[str, Any] | None = None,
):
    """获取表格中第一行的段落样式

    <w:style w:type="table" w:styleId="LightList-Accent1">
        ...
        <w:pPr>
            ...
        </w:pPr>
        <w:tblPr>
            ...
        </w:tblPr>
        <w:tblStylePr w:type="firstRow">
            <w:pPr>
                ...
            </w:pPr>
            <w:rPr
                ...
            </w:rPr>
            <w:tblPr/>
            <w:tcPr>
                ...
            </w:tcPr>
        </w:tblStylePr>
        <w:tblStylePr w:type="lastRow">
            ...
        </w:tblStylePr>
        <w:tblStylePr w:type="firstCol">
            ...
        </w:tblStylePr>
        <w:tblStylePr w:type="lastCol">
            ...
        </w:tblStylePr>
        <w:tblStylePr w:type="band1Vert">
            ...
        </w:tblStylePr>
        <w:tblStylePr w:type="band1Horz">
            ...
        </w:tblStylePr>
    </w:style>
    """

    # logger.info(f"获取表格第一行样式ID为: { style_id } 的段落样式")

    ct_styles = styles.get_styles(style_id)

    # 段落样式
    if paragraph_styles is None:
        paragraph_styles = {}

    # 字符样式
    if character_styles is None:
        character_styles = {}

    # 行样式
    if row_styles is None:
        row_styles = {}

    # 单元格样式
    if cell_styles is None:
        cell_styles = {}

    for ct_style in ct_styles:
        if ct_style.type != ST_StyleType.table:
            logger.info(f"忽略非表格样式: {ct_style}")
            continue

        for tblstylepr in ct_style.tblStylePr:
            if tblstylepr.type == ST_TblStyleOverrideType.firstRow:
                if tblstylepr.rPr is not None:
                    character_ct_style2html(tblstylepr.rPr, character_styles)

                if tblstylepr.pPr is not None:
                    paragraph_ct_style2html(
                        tblstylepr.pPr, character_styles, paragraph_styles
                    )

                if tblstylepr.trPr is not None:
                    get_table_row_styles(tblstylepr.trPr, row_styles)

                if tblstylepr.tcPr is not None:
                    get_table_cell_styles(tblstylepr.tcPr, cell_styles)

    # logger.info(f"获取表格第一行样式ID为: { style_id } 的段落样式: {paragraph_styles}")

    return paragraph_styles, character_styles, row_styles, cell_styles


def get_table_styles(tblpr: CT_TblPrBase, styles: dict[str, Any] | None = None):
    """获取表格的样式"""

    # 表格(Table)的样式
    if styles is None:
        styles = {
            # https://developer.mozilla.org/zh-CN/docs/Web/CSS/border-spacing
            "border-spacing": "0",  # 浏览器默认边框间距设为0
            # https://developer.mozilla.org/zh-CN/docs/Web/CSS/border-collapse
            "border-collapse": "collapse",  # 表格边框属于合并还是分开模式, 浏览器默认分开模式.
        }

    # <xsd:element name="tblStyle" type="CT_String" minOccurs="0"/>
    # <xsd:element name="tblpPr" type="CT_TblPPr" minOccurs="0" maxOccurs="1"/>
    # <xsd:element name="tblOverlap" type="CT_TblOverlap" minOccurs="0" maxOccurs="1"/>
    # <xsd:element name="bidiVisual" type="CT_OnOff" minOccurs="0" maxOccurs="1"/>
    # <xsd:element name="tblStyleRowBandSize" type="CT_DecimalNumber" minOccurs="0" maxOccurs="1"/>
    # <xsd:element name="tblStyleColBandSize" type="CT_DecimalNumber" minOccurs="0" maxOccurs="1"/>
    # <xsd:element name="tblW" type="CT_TblWidth" minOccurs="0" maxOccurs="1"/>
    # <xsd:element name="jc" type="CT_JcTable" minOccurs="0" maxOccurs="1"/>
    # <xsd:element name="tblCellSpacing" type="CT_TblWidth" minOccurs="0" maxOccurs="1"/>
    # <xsd:element name="tblInd" type="CT_TblWidth" minOccurs="0" maxOccurs="1"/>
    # <xsd:element name="tblBorders" type="CT_TblBorders" minOccurs="0" maxOccurs="1"/>
    # <xsd:element name="shd" type="CT_Shd" minOccurs="0" maxOccurs="1"/>
    # <xsd:element name="tblLayout" type="CT_TblLayoutType" minOccurs="0" maxOccurs="1"/>
    # <xsd:element name="tblCellMar" type="CT_TblCellMar" minOccurs="0" maxOccurs="1"/>
    # <xsd:element name="tblLook" type="CT_TblLook" minOccurs="0" maxOccurs="1"/>
    # <xsd:element name="tblCaption" type="CT_String" minOccurs="0" maxOccurs="1"/>
    # <xsd:element name="tblDescription" type="CT_String" minOccurs="0" maxOccurs="1"/>

    # 浮动表定位
    if tblpr.tblpPr is not None:
        ...

    # 浮动表允许其他表重叠
    if tblpr.tblOverlap is not None:
        ...

    # 视觉上从右到左的表格
    # https://developer.mozilla.org/en-US/docs/Web/HTML/Element/table
    # https://developer.mozilla.org/en-US/docs/Web/CSS/direction
    if tblpr.bidiVisual is not None:
        if tblpr.bidiVisual.is_on:
            styles["direction"] = "rtl"

    # 行带中的行数
    if tblpr.tblStyleRowBandSize is not None:
        ...

    # 列带中的列数
    if tblpr.tblStyleColBandSize is not None:
        ...

    # 首选表格宽度
    if tblpr.tblW is not None:
        w = ct_tblwidth2html(tblpr.tblW)
        if w:
            styles["width"] = w

    # 表格对齐 方式
    # https://developer.mozilla.org/en-US/docs/Web/HTML/Element/table
    # https://developer.mozilla.org/zh-CN/docs/Web/HTML/Element/table
    if tblpr.jc is not None:
        # align 属性已删除，使用css的 margin-inline-start 属性实现类似效果
        # 靠右
        if tblpr.jc.val_jc_table in (ST_JcTable.end, ST_JcTable.right):
            styles["margin-inline-start"] = "auto"

        # align 属性已删除，使用css的 margin-inline-end 属性实现类似效果
        # 靠左
        if tblpr.jc.val_jc_table in (ST_JcTable.start, ST_JcTable.left):
            styles["margin-inline-end"] = "auto"

        # 水平居中
        if tblpr.jc.val_jc_table == ST_JcTable.center:
            styles["margin-inline-start"] = "auto"
            styles["margin-inline-end"] = "auto"

    # 表格行单元格间距
    # https://developer.mozilla.org/en-US/docs/Web/API/HTMLTableElement/cellSpacing
    # 使用 border-spacing 替代
    # https://developer.mozilla.org/en-US/docs/Web/CSS/border-spacing
    if tblpr.tblCellSpacing is not None:
        space = ct_tblwidth2html(tblpr.tblCellSpacing)
        if space:
            styles["border-spacing"] = space

    # 表格从前导边距缩进
    # http://192.168.2.53:8001/openxml/ecma-part1/chapter17/04tabls/#17450-tblind-表格从前导边距缩进
    if tblpr.tblInd is not None:
        if tblpr.jc is not None and tblpr.jc.val_jc_table in (
            ST_JcTable.end,
            ST_JcTable.right,
        ):
            styles["margin-right"] = ct_tblwidth2html(tblpr.tblInd) or "0pt"
        else:
            ind = ct_tblwidth2html(tblpr.tblInd)

            if ind:
                styles["margin-left"] = ind
            else:
                # 表格自动 剧中对齐
                styles["margin-left"] = "auto"
                styles["margin-right"] = "auto"

    # 表格边框
    if tblpr.tblBorders is not None:
        if tblpr.tblBorders.top is not None:
            styles["border-top"] = ct_boder2html(tblpr.tblBorders.top)

        if tblpr.tblBorders.bottom is not None:
            styles["border-bottom"] = ct_boder2html(tblpr.tblBorders.bottom)

        if tblpr.tblBorders.left is not None:
            styles["border-left"] = ct_boder2html(tblpr.tblBorders.left)

        if tblpr.tblBorders.right is not None:
            styles["border-right"] = ct_boder2html(tblpr.tblBorders.right)

    # 表格底纹
    if tblpr.shd is not None:
        if tblpr.shd.fill is not None:
            styles["background-color"] = f"#{tblpr.shd.fill}"

    # 表格布局
    if tblpr.tblLayout is not None:
        ...

    # 表格单元格边距默认值
    # 这里要在处理单元格边距时处理
    if tblpr.tblCellMar is not None:
        ...

    # 表格样式条件格式设置
    # 先忽略，这里要结合索引单独设置行和单元格的样式
    if tblpr.tblLook is not None:
        ...

    return styles


# ---- 表格行(Row)样式 -----


def get_table_row_styles(trpr: CT_TrPr, styles: dict[str, Any] | None = None):
    """获取表格行的样式"""

    # 行(Row)的样式
    if styles is None:
        styles = {}

    # <xsd:element name="cnfStyle" type="CT_Cnf" minOccurs="0" maxOccurs="1"/>
    # <xsd:element name="divId" type="CT_DecimalNumber" minOccurs="0"/>
    # <xsd:element name="gridBefore" type="CT_DecimalNumber" minOccurs="0"/>
    # <xsd:element name="gridAfter" type="CT_DecimalNumber" minOccurs="0"/>
    # <xsd:element name="wBefore" type="CT_TblWidth" minOccurs="0" maxOccurs="1"/>
    # <xsd:element name="wAfter" type="CT_TblWidth" minOccurs="0" maxOccurs="1"/>
    # <xsd:element name="cantSplit" type="CT_OnOff" minOccurs="0"/>
    # <xsd:element name="trHeight" type="CT_Height" minOccurs="0"/>
    # <xsd:element name="tblHeader" type="CT_OnOff" minOccurs="0"/>
    # <xsd:element name="tblCellSpacing" type="CT_TblWidth" minOccurs="0" maxOccurs="1"/>
    # <xsd:element name="jc" type="CT_JcTable" minOccurs="0" maxOccurs="1"/>
    # <xsd:element name="hidden" type="CT_OnOff" minOccurs="0"/>

    # trpr.cnfStyle

    # 行高
    if trpr.trHeight is not None:
        # https://developer.mozilla.org/en-US/docs/Web/CSS/min-height
        if trpr.trHeight.hRule == ST_HeightRule.AtLeast:
            # 在tr中min-height貌似不起作用: https://github.com/w3c/csswg-drafts/issues/477
            # styles["min-height"] = f"{trpr.trHeight.val}pt"
            styles["height"] = f"{trpr.trHeight.val}pt"

        # https://developer.mozilla.org/en-US/docs/Web/CSS/height
        elif trpr.trHeight.hRule == ST_HeightRule.Exact:
            styles["height"] = f"{trpr.trHeight.val}pt"

        elif trpr.trHeight.hRule == ST_HeightRule.Auto:
            styles["height"] = "auto"

    # 行内单元格边距
    # css 中设置margin或padding不能体现，忽略
    # trpr.tblCellSpacing

    # 隐藏行
    if trpr.hidden is not None:
        if trpr.hidden.is_on:
            styles["display"] = "none"

    return styles


# ---- 表格单元格样式 -----


def get_table_cell_default_styls(
    tblpr: CT_TblPrBase, styles: dict[str, Any] | None = None
):
    # 表格给予单元格的默认的样式

    if styles is None:
        styles = {}

    # 表格边框
    if tblpr.tblBorders is not None:
        if tblpr.tblBorders.top is not None:
            styles["border-top"] = ct_boder2html(tblpr.tblBorders.top)

        if tblpr.tblBorders.bottom is not None:
            styles["border-bottom"] = ct_boder2html(tblpr.tblBorders.bottom)

        if tblpr.tblBorders.left is not None:
            styles["border-left"] = ct_boder2html(tblpr.tblBorders.left)

        if tblpr.tblBorders.right is not None:
            styles["border-right"] = ct_boder2html(tblpr.tblBorders.right)

    # 表格单元格边距默认值
    # 先忽略，这里要在处理单元格边距时处理
    if tblpr.tblCellMar is not None:
        if tblpr.tblCellMar.top is not None:
            styles["padding-top"] = ct_tblwidth2html(tblpr.tblCellMar.top) or "0pt"

        if tblpr.tblCellMar.bottom is not None:
            styles["padding-bottom"] = (
                ct_tblwidth2html(tblpr.tblCellMar.bottom) or "0pt"
            )

        if tblpr.tblCellMar.left is not None:
            styles["padding-left"] = ct_tblwidth2html(tblpr.tblCellMar.left) or "0pt"

        if tblpr.tblCellMar.right is not None:
            styles["padding-right"] = ct_tblwidth2html(tblpr.tblCellMar.right) or "0pt"

    return styles


def get_table_cell_styles(tcpr: CT_TcPr, styles: dict[str, Any] | None = None):
    """获取表格单元格的样式"""

    # 单元格的样式
    if styles is None:
        styles = {}

    # tcpr.cnfStyle

    # <xsd:element name="cnfStyle" type="CT_Cnf" minOccurs="0" maxOccurs="1"/>
    # <xsd:element name="tcW" type="CT_TblWidth" minOccurs="0" maxOccurs="1"/>
    # <xsd:element name="gridSpan" type="CT_DecimalNumber" minOccurs="0"/>
    # <xsd:element name="hMerge" type="CT_HMerge" minOccurs="0"/>
    # <xsd:element name="vMerge" type="CT_VMerge" minOccurs="0"/>
    # <xsd:element name="tcBorders" type="CT_TcBorders" minOccurs="0" maxOccurs="1"/>
    # <xsd:element name="shd" type="CT_Shd" minOccurs="0"/>
    # <xsd:element name="noWrap" type="CT_OnOff" minOccurs="0"/>
    # <xsd:element name="tcMar" type="CT_TcMar" minOccurs="0" maxOccurs="1"/>
    # <xsd:element name="textDirection" type="CT_TextDirection" minOccurs="0" maxOccurs="1"/>
    # <xsd:element name="tcFitText" type="CT_OnOff" minOccurs="0" maxOccurs="1"/>
    # <xsd:element name="vAlign" type="CT_VerticalJc" minOccurs="0"/>
    # <xsd:element name="hideMark" type="CT_OnOff" minOccurs="0"/>
    # <xsd:element name="headers" type="CT_Headers" minOccurs="0"/>

    # 首选的表格单元格宽度
    # https://developer.mozilla.org/en-US/docs/Web/CSS/width
    if tcpr.tcW is not None:
        styles["width"] = ct_tblwidth2html(tcpr.tcW) or "auto"

    # 表格单元格边框合集
    if tcpr.tcBorders is not None:
        if tcpr.tcBorders.top is not None:
            styles["border-top"] = ct_boder2html(tcpr.tcBorders.top)

        if tcpr.tcBorders.bottom is not None:
            styles["border-bottom"] = ct_boder2html(tcpr.tcBorders.bottom)

        if tcpr.tcBorders.left is not None:
            styles["border-left"] = ct_boder2html(tcpr.tcBorders.left)

        if tcpr.tcBorders.right is not None:
            styles["border-right"] = ct_boder2html(tcpr.tcBorders.right)

    # 底纹, 背景
    if tcpr.shd is not None:
        if tcpr.shd.fill is not None:
            styles["background-color"] = f"#{tcpr.shd.fill}"

    # 不要包裹单元格内容
    if tcpr.noWrap is not None:
        ...

    # 单个表格单元格边距
    # 先不处理，遇到再说，貌似是用padding体现.
    if tcpr.tcMar is not None:
        ...

    # 文本方向
    # https://developer.mozilla.org/en-US/docs/Web/CSS/writing-mode
    if tcpr.textDirection is not None:
        if tcpr.textDirection.val == ST_TextDirection.tb:
            styles["writing-mode"] = "horizontal-tb"

        elif tcpr.textDirection.val == ST_TextDirection.rl:
            styles["writing-mode"] = "vertical-rl"

        elif tcpr.textDirection.val == ST_TextDirection.lr:
            styles["writing-mode"] = "vertical-lr"

        else:
            logger.info(f"未知的文本流动方向: {tcpr.textDirection.val}")

    # 适合单元格内的文本
    # 先不处理，遇到再说
    if tcpr.tcFitText is not None:
        ...

    # 垂直对齐方式
    # https://developer.mozilla.org/en-US/docs/Web/CSS/vertical-align
    if tcpr.vAlign is not None:
        if tcpr.vAlign.val == ST_VerticalJc.top:
            styles["vertical-align"] = "top"

        elif tcpr.vAlign.val == ST_VerticalJc.center:
            styles["vertical-align"] = "middle"

        elif tcpr.vAlign.val == ST_VerticalJc.bottom:
            styles["vertical-align"] = "bottom"

        else:
            logger.info(f"未知的文本垂直对齐方式: {tcpr.vAlign.val}")

    return styles


def get_table_cell_colspan(tcpr: CT_TcPr):
    """获取单元格的列合并数"""

    colspan = 1

    # 当前表格单元格跨越的网格列
    if tcpr.gridSpan is not None and tcpr.gridSpan.val_dec_num > 1:
        colspan = tcpr.gridSpan.val_dec_num

    return colspan


def get_table_cell_rowspan1(
    row_col_matrix: list[list[CT_TcPr | None]], ridx: int, cidx: int
):
    """获取单元格的行合并数

    row_col_matrix: 行和列的矩阵
    ridx: 行索引, 从 0 开始
    cidx: 列索引, 从 0 开始
    """

    rowspan = 1

    row_lenth = len(row_col_matrix)

    # 遍历后面每一行该列位置的单元格合并类型
    for idx in range(ridx + 1, row_lenth):
        current_cell_pr = row_col_matrix[idx][cidx]

        # 终止计算合并的行数
        if current_cell_pr is None:
            break

        # 终止计算合并的行数
        if current_cell_pr.vMerge is None:
            break

        # 重新开始计算合并行或继续计算合并的函数
        elif current_cell_pr.vMerge is not None:
            # 终止计算合并的行数
            if current_cell_pr.vMerge.val == ST_Merge.restart:
                break

            # 说明与上一行合并
            elif current_cell_pr.vMerge.val == ST_Merge.Continue:
                rowspan += 1

    return rowspan


def get_table_cell_rowspan(
    row_col_matrix: list[list[CT_TcPr | None]], ridx: int, cidx: int
):
    """获取单元格的行合并数

    row_col_matrix: 行和列的矩阵
    ridx: 行索引, 从 0 开始
    cidx: 列索引, 从 0 开始
    """

    rowspan = 1

    row_lenth = len(row_col_matrix)
    # logger.info(f"search: {ridx}:{cidx}")

    # 遍历后面每一行该列位置的单元格合并类型
    for idx in range(ridx + 1, row_lenth):
        current_row = row_col_matrix[idx]

        need_break = False

        really_cell_idx = 0

        # 这里单元格可能会跨多列，所以某一个单元格可能是占了n列的纵向位置，
        # 所以这里需要遍历手动计算cellidx，而不是用二维数组表示就行.
        for _idx, current_cell_pr in enumerate(current_row):
            if really_cell_idx == cidx:
                # logger.info(f"{idx}:{_idx} == {idx}:{cidx}")
                # 终止计算合并的行数
                if current_cell_pr is None:
                    need_break = True
                    break

                # 终止计算合并的行数
                if current_cell_pr.vMerge is None:
                    need_break = True
                    break

                # 重新开始计算合并行或继续计算合并的函数
                elif current_cell_pr.vMerge is not None:
                    # 终止计算合并的行数
                    if current_cell_pr.vMerge.val == ST_Merge.restart:
                        need_break = True
                        break

                    # 说明与上一行合并
                    elif current_cell_pr.vMerge.val == ST_Merge.Continue:
                        rowspan += 1

            if current_cell_pr is None:
                # logger.info(f"cell is None")
                really_cell_idx += 1
            else:
                gridspan = get_table_cell_colspan(current_cell_pr)
                # logger.info(f"cell is not None: {idx}:{gridspan}")
                really_cell_idx += gridspan

        if need_break:
            break

    return rowspan


def gen_table_tcpr_matrix(tbl: CT_Tbl):
    """生成表格的单元格属性的矩阵.

    n x m 的矩阵

    n: 行数
    m: 列数
    """

    tr_arr: list[list[CT_TcPr | None]] = []

    for tr in tbl.tr_lst:
        td_arr: list[CT_TcPr | None] = []

        for td in tr.tc_lst:
            td_arr.append(td.tcPr)

        tr_arr.append(td_arr)

    return tr_arr

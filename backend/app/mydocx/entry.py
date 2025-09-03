from __future__ import annotations  # 支持类型注解

import copy
import html
import json
import os
import shutil
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Any, BinaryIO, Literal
from urllib.parse import quote, unquote

from loguru import logger

from ms_office.api import open_docx
from ms_office.oxml.dml.main import (
    namespace_c,  # 图表: 柱状图, 饼图...
    namespace_dgm,  # 智能图形
    namespace_pic,  # 图片
    namespace_tb,  # 表格
)
from ms_office.oxml.dml.picture import CT_Picture as pct_CT_Picture
from ms_office.oxml.dml.word_drawing import (
    CT_Anchor as wp_CT_Anchor,
)
from ms_office.oxml.dml.word_drawing import (
    CT_Inline as wp_CT_Inline,
)
from ms_office.oxml.pml.core import (
    CT_MC_AlternateContent,
)
from ms_office.oxml.vml.main import (
    CT_ImageData as v_CT_ImageData,
)
from ms_office.oxml.vml.main import (
    CT_Shape as v_CT_shape,
)
from ms_office.oxml.wml.main import (
    # 段落,文本
    CT_P,
    CT_R,
    CT_Br,  # 换行
    # 绘制对象
    CT_Drawing,
    CT_Hyperlink,
    CT_NumPr,  # 编号属性
    CT_Object,
    # 图片
    CT_Picture,
    CT_Row,
    CT_SdtRun,  # 内联级结构化文档标签
    # 表格
    CT_Tbl,
    CT_Tc,
    CT_TcPr,
    CT_Text,  # 文本
    ST_DecimalNumber,
    ST_Merge,
    Union_CT_SdtCellRowRunBlock,
    Union_CT_TabStop,  # tab
    qn,
)
from ms_office.units import Emu
from ms_office.wml.number import Numbering
from ms_office.wml.wordprocessing import WordProcessing

from .exceptions import ChartDrawingException, ParseException, ReviewException

# 标题支持
from .tools.consts import FileType, HeadingType, HeadingTypeTagMap
from .tools.convert import ImageTool

# 云盘支持
from .tools.oss import OssTool
from .tools.struct import HtmlParagraph, HtmlRun

# 解析样式支持
from .tools.style import (
    character_ct_style2html,
    # 表格单元格跨列，跨行
    gen_table_tcpr_matrix,
    get_cell_styles_from_define,
    get_character_styles_from_define,
    get_docx_default_character_style,
    get_docx_default_paragraph_style,
    get_firstrow_styles_from_define,
    get_paragraph_styles_from_define,
    get_table_cell_colspan,
    get_table_cell_default_styls,
    get_table_cell_rowspan,
    get_table_cell_styles,
    get_table_character_styles_from_define,
    get_table_paragraph_styles_from_define,
    get_table_row_styles,
    # 表格样式
    get_table_styles,
    # 表格定义样式
    get_table_styles_from_define,
    paragraph_ct_style2html,
)

# 生成html内容支持
from .tools.utils import (
    gen_html_paragraph,
    gen_paragraph_html,
    gen_paragraph_shtml,
    gen_paragraph_txt,
    gen_random_characters,
    gen_shtml_paragraph,
    gen_txt_paragraph,
    get_wh_from_vml_sp_style,
)


class RenderFormat(StrEnum):
    txt = "txt"
    html = "html"
    shtml = "shtml"  # simple html 没有多余的样式信息


class Extract:
    """提取类"""

    def __init__(
        self,
        doc_path: str | BinaryIO,
        use_oss: bool = True,
        debug: bool = False,  # 是否为debug模式
    ):
        """解析pptx的对象"""

        # 解析过程中，生成的临时文件收集器
        self.need_rm_files: list[str] = []

        # 保存docx字节为临时文件
        if isinstance(doc_path, str):
            self.ppt_path = Path(doc_path).resolve()
            self.doc_name: str = quote(self.ppt_path.name)[0:255]  # 文件名称转义
            shutil.copyfile(doc_path, self.doc_name)
            self.docx_temp_path = self.doc_name
        else:
            now = datetime.now()
            self.doc_name = f"doc{now.strftime('%Y%m%d%H%M%S')}.docx"
            self.ppt_path = self.doc_name
            self.docx_temp_path = self.doc_name

            with open(self.doc_name, "wb") as fw:
                fw.write(doc_path.read())

            # 恢复到一开始的位置
            doc_path.seek(0)

        self.docx: WordProcessing = open_docx(doc_path)  # 打开ppt文件
        self.need_rm_files.append(self.docx_temp_path)

        # 当前解析的数据，调试使用
        self._current_slide: int = 0  # 当前解析的幻灯片索引
        self._current_shape_level: int = (
            0  # 当前解析的图形级别， 1最高级，2是1的子级别，3是2的子级别，以此类推...
        )
        self._current_shape_stack: list = [1]  # 当前解析的图形索引
        self._shape_name: str = ""
        self._shape_type: str = ""
        self._shape_text: str = ""
        self._is_parse_master_shape: bool = False  # 解析母板中的图形模式(第一优先级)
        self._is_parse_layout_shape: bool = (
            False  # 解析母板的布局中的图形模式(第二优先级)
        )
        # 幻灯片页面本身自己的才是第三优先级

        # 图片上传是否使用oss
        self.use_oss = use_oss

        # 渲染格式
        self.render_format: RenderFormat = RenderFormat.html

        # 调试查看xml目录
        self._debug_dir = None
        if debug:
            self._debug_dir = (
                Path().resolve()
                / "unzipxml"
                / unquote(self.doc_name.replace(".docx", ""))
            )

            # 删除之前程序生成的文件
            if self._debug_dir.exists():
                shutil.rmtree(self._debug_dir)

            # 重新创建当前目录
            os.makedirs(self._debug_dir, exist_ok=True)

    def debug_write(self, filename: str, xml: str) -> None:
        """调试时将xml写入文件"""

        if self._debug_dir:
            with open(self._debug_dir / filename, "w") as fw:
                fw.write(xml)

    def __del__(self) -> None:
        """删除对象之前，先删除生成的临时文件"""

        logger.info("删除提取类....")

        for file in self.need_rm_files:
            Path.unlink(Path(file), missing_ok=True)

    def close(self) -> None:
        """ """

        self.docx.close()
        del self.docx

    def parse(self, render_format: RenderFormat = RenderFormat.html) -> str:
        # 解析docx文件入口

        self.render_format = render_format

        _body = self.docx.body

        if _body is None:
            raise ParseException("文件内容为空，无法解析。")

        if self.docx.is_review:
            raise ReviewException("文档处于修订模式，无法解析。")

        total_pragrahs = len(_body.block_level_elts)
        logger.info(f"docx共有{total_pragrahs}个段落")

        # 调试输出 document.xml
        if self._debug_dir:
            # document.xml
            self.debug_write(self.docx.part.part_name.filename, self.docx.part.oxml.xml)
            # document.xml.rels
            if self.docx.part.rels.xml is not None:
                self.debug_write(
                    self.docx.part.part_name.filename + ".rels.xml",
                    self.docx.part.rels.xml.decode(),
                )
            # styles.xml
            self.debug_write(
                self.docx.styles.part.part_name.filename, self.docx.styles.part.oxml.xml
            )
            # numbering.xml
            if self.docx.number is not None:
                self.debug_write(
                    self.docx.number.part.part_name.filename,
                    self.docx.number.part.oxml.xml,
                )

            # numbering.xml
            if self.docx.theme is not None:
                self.debug_write(
                    self.docx.theme.part.part_name.filename,
                    self.docx.theme.part.oxml.xml,
                )

        paragraph_arr: list[HtmlParagraph | str] = []

        # 获取文档默认段落样式
        character_styles = get_docx_default_character_style(self.docx.styles)
        logger.info(f"docx字符默认样式: {character_styles}")

        paragraph_styles = get_docx_default_paragraph_style(
            self.docx.styles, character_styles
        )
        logger.info(f"docx段落默认样式: {paragraph_styles}")

        for block_no, block_ele in enumerate(_body.block_level_elts, start=1):
            # logger.info(f"{block_no} -> {type(block_ele) = }: {block_ele.text = }")
            # logger.info(f"处理段落: {block_no}/{total_pragrahs} ...")

            # 目录模块判断
            # 三措文档没有目录块
            if isinstance(block_ele, Union_CT_SdtCellRowRunBlock):
                continue

            # 段落内容
            if isinstance(block_ele, CT_P):
                html_p = self.parse_paragraph(
                    block_ele, paragraph_styles.copy(), character_styles.copy()
                )
                paragraph_arr.extend(html_p)
                continue

            # 表格内容
            elif isinstance(block_ele, CT_Tbl):
                html_table = self.parse_table(block_ele)
                paragraph_arr.append(html_table)

            else:
                # logger.info(f"[{block_no}]忽略段落块级内容: {type(block_ele)}")
                ...

            # 清除lxml建立的xml树，释放内存
            # block_ele.clear()  # type: ignore

        # 清除lxml建立的xml树，释放内存
        # _body.clear()  # type: ignore

        # 渲染为html格式
        rendered_text = self.render_paragraph(paragraph_arr)

        return rendered_text

    # --- 正文段落块 ----
    def parse_paragraph(
        self,
        ele: CT_P,
        paragraph_styles: dict[str, Any] | None = None,
        character_styles: dict[str, Any] | None = None,
        paragraph_tag: str = "p",
    ) -> list[HtmlParagraph | str]:
        # 段落属性
        # ele.pPr

        # 段落内容, 数组， 内容元素
        # ele.p_content

        # 项目符号编号
        number_text = ""

        span_arr: list[HtmlRun | str | None] = []

        # 解析样式
        style_id: str = ""
        style_name: str = ""

        paragraph_styles = {} if paragraph_styles is None else paragraph_styles
        character_styles = {} if character_styles is None else character_styles

        # 获取使用的指定样式
        if ele.pPr is not None:
            # 样式表中的样式
            if ele.pPr.pStyle is not None:
                style_id = ele.pPr.pStyle.val_str

                # logger.info(f"段落获取文档指定({style_id})的样式...")
                get_character_styles_from_define(
                    self.docx.styles, style_id, character_styles
                )
                get_paragraph_styles_from_define(
                    self.docx.styles, style_id, character_styles, paragraph_styles
                )

                # logger.info(f"[{style_id}]样式表中的段落样式: {paragraph_styles}")

                ct_style = self.docx.styles.style_map.get(style_id)

                if ct_style is not None and ct_style.name is not None:
                    style_name = ct_style.name.val_str
                    # logger.info(f"样式ID: {style_id} -> {style_name}")

                # 从样式表中的样式中获取编号
                if (
                    self.docx.number is not None
                    and ct_style is not None
                    and ct_style.pPr is not None
                    and ct_style.pPr.numPr is not None
                ):
                    number_text = self.parse_number_text(
                        self.docx.number,
                        ct_style.pPr.numPr,
                    )

            # 编号中的段落样式以及编号
            if ele.pPr.numPr is not None and self.docx.number is not None:
                # logger.info(ele.pPr.xml)
                number_text = self.parse_number_text(self.docx.number, ele.pPr.numPr)

            # 段落自定义字符样式
            if ele.pPr.rPr is not None:
                # logger.info(f"段落获取自定义字符样式...")

                if ele.pPr.rPr.rStyle is not None:
                    r_style_id = ele.pPr.rPr.rStyle.val_str

                    get_character_styles_from_define(
                        self.docx.styles, r_style_id, character_styles
                    )

                character_ct_style2html(ele.pPr.rPr, character_styles)

            # 段落自定义样式
            paragraph_ct_style2html(ele.pPr, character_styles, paragraph_styles)

        # logger.info(f"[{style_id}][{style_name}]段落样式: {paragraph_styles}")
        # logger.info(f"[{style_id}][{style_name}]字符样式: {character_styles}")

        # 处理段落中需要传递给子元素的样式，
        lh_key = "line-height"
        if lh_key in paragraph_styles and paragraph_styles[lh_key].endswith("pt"):
            paragraph_line_height = paragraph_styles.pop(lh_key)

            if paragraph_line_height and lh_key not in character_styles:
                character_styles[lh_key] = paragraph_line_height

            # 处理段落中的最小行高:
            paragraph_min_line_height = paragraph_styles.pop("min-line-height", None)
            font_size = character_styles.get("font-size", "12pt")
            if paragraph_min_line_height and lh_key not in character_styles:
                new_line_height = f"{max(float(paragraph_min_line_height[0:-2]), float(font_size[0:-2]))}pt"
                character_styles[lh_key] = new_line_height

        # 处理段落的子元素，比如, span, drawing, img
        for content_no, content_ele in enumerate(ele.p_content, start=1):
            if isinstance(content_ele, CT_R):
                # <span> 或 <vue-img> 标签
                # 这里copy样式字典，防止污染后续别的文本
                span_or_img_tag = self.parse_paragraph_run(
                    content_ele, character_styles.copy()
                )
                span_arr.extend(span_or_img_tag) if span_or_img_tag is not None else ""

            elif isinstance(content_ele, CT_Hyperlink):
                a_tag = self.parse_paragraph_hyperlink(
                    content_ele, character_styles.copy()
                )
                span_arr.append(a_tag) if a_tag is not None else ""

            elif isinstance(content_ele, CT_SdtRun):
                span_arr.extend(
                    self.parse_paragraph_sdtrun(content_ele, character_styles.copy())
                )

            else:
                # logger.info(f"[{content_no}]忽略段落内容: {type(content_ele)}")
                ...

        # logger.info(f"合并前: {span_arr = }")

        if self.render_format == RenderFormat.html:
            merged_span_arr = self.merge_same_style_run(span_arr)

        elif self.render_format == RenderFormat.shtml:
            merged_span_arr = self.merge_same_style_run_shtml(span_arr)

        else:
            # 合并相同样式的run内容，不带样式
            merged_span_arr = self.merge_same_style_run_txt(span_arr)

        # logger.info(f"合并后: {merged_span_arr = }")

        # 编号前缀处理封装
        if number_text:
            number_text = self.parse_paragrah_run_text_4_number_text(
                number_text, character_styles.copy()
            )

        # 锚点获取
        # html格式，锚点才有意义
        anchor_id = None
        anchors: list[str] = []
        if self.render_format == RenderFormat.html:
            if len(ele.bookmarkStart) > 0:
                anchors = [mk.name for mk in ele.bookmarkStart]
                anchor_id = anchors[0]

            if len(anchors) > 1:
                for anchor in anchors[1:]:
                    merged_span_arr.insert(0, f'<span id="{anchor.lower()}"></span>')

        # 标题封装段落标签, p 或 h1..h6 标签
        paragraph_tag = paragraph_tag or "p"

        # logger.info(f"[{span_arr}] {style_id = } {style_name=}")

        # 根据ID判断
        if HeadingType.have_value(style_id):
            paragraph_tag = HeadingTypeTagMap[HeadingType(style_id)]

        # 根据名称判断
        elif HeadingType.have_value(style_name):
            # logger.info(f"{style_name = }")
            paragraph_tag = HeadingTypeTagMap[HeadingType(style_name)]

        # 段落数组
        paragraph_arr: list[HtmlParagraph | str] = []

        # 常规处理段落标签
        if self.render_format == RenderFormat.html:
            paragraph_arr.append(
                gen_html_paragraph(
                    merged_span_arr,
                    paragraph_tag,
                    style_id,
                    number_text,
                    anchor_id,
                    paragraph_styles,
                )
            )
        elif self.render_format == RenderFormat.shtml:
            paragraph_arr.append(
                gen_shtml_paragraph(
                    merged_span_arr,
                    paragraph_tag,
                    style_id,
                    number_text,
                    anchor_id,
                    paragraph_styles,
                )
            )
        else:
            paragraph_arr.append(
                gen_txt_paragraph(
                    merged_span_arr,
                    paragraph_tag,
                    style_id,
                    number_text,
                    anchor_id,
                    paragraph_styles,
                )
            )

        return paragraph_arr

    def parse_number_text(self, numbering: Numbering, numPr: CT_NumPr) -> str:
        """解析编号文本"""

        number_text = ""

        lvl_style = numbering.get_lvl_style(numPr)

        # 计算编号文本
        if lvl_style is not None:
            number_text = numbering.get_numbering_text(numPr)

            # logger.info(f"编号文本为: {number_text}")
            # logger.info(f"\n\n ------------- \n\n")

        return number_text

    def parse_paragraph_hyperlink(
        self, ele: CT_Hyperlink, character_styles: dict[str, Any] | None = None
    ) -> str:
        """解析段落中的超链接"""

        a_tag_content = ""

        if len(ele.r) > 0:
            runs: list[HtmlRun | str | None] = []
            for r in ele.r:
                runs.extend(self.parse_paragraph_run(r))

            txts = []
            for _r in runs:
                if _r is None:
                    continue

                if isinstance(_r, str):
                    txts.append(_r)

                else:
                    if self.render_format == RenderFormat.html:
                        txts.append(f"<span style='{_r.style}'>{_r.content}</span>")
                    else:
                        txts.append(_r.content)

            a_tag_content = "\n".join(txts)

        # a标签属性
        a_tag_attr: dict[str, Any] = {}

        if ele.tooltip is not None:
            a_tag_attr["title"] = ele.tooltip

        # 外部连接
        if ele.r_id is not None:
            a_tag_attr["href"] = self.docx.get_hayperlink_target(ele.r_id)

        # 内部锚点
        if ele.anchor is not None:
            a_tag_attr["href"] = f"#{ele.anchor.lower()}"

        # 构造a标签属性字符串
        a_tag_attr_str = ""
        if a_tag_attr:
            a_tag_attr_str = " ".join(
                [f'{name}="{val}"' for name, val in a_tag_attr.items()]
            )

        return f"<a {a_tag_attr_str}>{a_tag_content}</a>"

    def parse_paragraph_sdtrun(
        self, ele: CT_SdtRun, character_styles: dict[str, Any] | None = None
    ) -> list[HtmlRun | str | None]:
        """内联级结构化文档标签"""

        # ele.sdtPr
        span_arr: list[HtmlRun | str | None] = []

        if ele.sdtContent_run is None:
            return span_arr

        for ele_conent in ele.sdtContent_run.p_content:
            if isinstance(ele_conent, CT_R):
                span_or_img_tag = self.parse_paragraph_run(ele_conent, character_styles)
                span_arr.extend(span_or_img_tag)

            else:
                # logger.info(f"[{content_no}]忽略sdtRun运行内容: {type(content_ele)}")
                ...

        return span_arr

    def parse_paragraph_run(
        self, ele: CT_R, character_styles: dict[str, Any] | None = None
    ) -> list[HtmlRun | str | None]:
        # 运行属性
        # ele.rPr

        # 运行内容, 数组， 内容元素
        # ele.run_inner_content

        run_content: list[HtmlRun | str | None] = []

        # 字符样式
        if character_styles is None:
            character_styles = {}

        # 获取自定义样式
        if ele.rPr is not None:
            if ele.rPr.rStyle is not None:
                r_style_id = ele.rPr.rStyle.val_str

                get_character_styles_from_define(
                    self.docx.styles, r_style_id, character_styles
                )

            character_ct_style2html(ele.rPr, character_styles)

        # 如果包含webHidden，则返回，不处理此run元素
        if ele.rPr is not None and ele.rPr.webHidden is not None:
            # ele.rPr.noProof is not None # 不检查拼写或语法
            return run_content

        # line-height 和 font-size 对比, 如果字体比行高要大，则删除行高。
        line_height = character_styles.get("line-height", None)
        font_size = character_styles.get("font-size", None)

        if line_height and font_size and font_size > line_height:
            character_styles.pop("line-height", None)

        # 获取文本，绘制对象(图片, ...)
        for content_no, content_ele in enumerate(ele.run_inner_content, start=1):
            # 换行
            if isinstance(content_ele, CT_Br):
                if self.render_format == RenderFormat.html:
                    run_content.append("<br/>")
                elif self.render_format == RenderFormat.shtml:
                    run_content.append("<br/>")
                else:
                    run_content.append("\n")

            # 常规文本
            elif isinstance(content_ele, CT_Text) and content_ele.local_tagname == "t":
                # <span>...</span> 标签

                span_text = self.parse_paragrah_run_text(content_ele, character_styles)
                run_content.append(span_text)

            # 文本
            elif isinstance(content_ele, CT_Text):
                # <span>...</span> 标签
                # logger.info(content_ele.xml)
                ...

            # tab => 4个空格
            elif (
                isinstance(content_ele, Union_CT_TabStop)
                and content_ele.local_tagname == "tab"
            ):
                # <span>...</span> 标签
                # run_content.append("<span>&emsp;</span>")

                # HTML格式才能展示
                if self.render_format == RenderFormat.html:
                    run_content.append(HtmlRun("&emsp;", True, ""))

                elif self.render_format == RenderFormat.shtml:
                    run_content.append(HtmlRun("&emsp;", True, ""))

                else:
                    run_content.append(HtmlRun("    ", True, ""))

            # 绘制对象
            elif isinstance(content_ele, CT_Drawing):
                # <vue-img>...</vue-img> 标签
                try:
                    # HTML格式才能展示图片
                    if self.render_format == RenderFormat.html:
                        picture = self.parse_drawing(content_ele)
                        run_content.append(picture) if picture is not None else ""

                except ChartDrawingException:
                    continue

            # Object对象
            elif isinstance(content_ele, CT_Object):
                # HTML格式才能展示图片
                if self.render_format == RenderFormat.html:
                    # <vue-img>...</vue-img> 标签
                    picture = self.parse_object(content_ele)

                    run_content.append(picture) if picture is not None else ""

            # 替代内容
            elif isinstance(content_ele, CT_MC_AlternateContent):
                # HTML格式才能展示图片
                if self.render_format == RenderFormat.html:
                    # <mc:AlternateContent> ... </mc:AlternateContent> 标签
                    logger.info("[替换内容]...")
                    picture = self.parse_alternateContent(content_ele)
                    run_content.append(picture) if picture is not None else ""

            else:
                # logger.info(
                #     f"[{content_no}]忽略运行内容: {content_ele.local_tagname} => {type(content_ele)}"
                # )
                ...

        return run_content

    def merge_same_style_run(
        self, run_content: list[HtmlRun | str | None]
    ) -> list[str]:
        """合并相同样式的run内容"""

        # 针对【同一段样式】的run内容做合并操作
        run_str_content: list[str] = []

        prev_run: HtmlRun | None = None

        for index, current_run in enumerate(run_content):
            if current_run is None:
                continue

            elif isinstance(current_run, str):
                # 将prev_run 添加到前面
                if prev_run is not None:
                    run_str_content.append(
                        f"<span style='{prev_run.style};'>{prev_run.content}</span>"
                    )
                    prev_run = None

                run_str_content.append(current_run)

            else:
                # 上一个run为空，且当前为空格
                if prev_run is None:
                    if current_run.only_space:
                        run_str_content.append(current_run.content)
                        continue

                    # 上一个run为空，且当前为非空格
                    else:
                        prev_run = current_run
                        continue

                # 上一个run不为空，且当前为空格
                elif prev_run is not None:
                    if current_run.only_space:
                        # 但前run为空格，采用前一个的样式
                        prev_run = HtmlRun(
                            prev_run.content + current_run.content,
                            False,
                            prev_run.style,
                        )
                        continue

                    # 上一个run不为空，且当前为非空格
                    else:
                        # 合并相同样式的字符
                        if current_run.style == prev_run.style:
                            # logger.info(
                            #     f"样式相同: {prev_run.content} + {current_run.content} => {current_run.style =} "
                            # )
                            prev_run = HtmlRun(
                                prev_run.content + current_run.content,
                                False,
                                current_run.style,
                            )

                        # 不合并字符，但将之前的字符加入到字符串中
                        # 同志将prev_run 指向 当前run
                        else:
                            run_str_content.append(
                                f"<span style='{prev_run.style};'>{prev_run.content}</span>"
                            )
                            prev_run = current_run

        # 处理最后一个run
        if prev_run is not None:
            run_str_content.append(
                f"<span style='{prev_run.style};'>{prev_run.content}</span>"
            )

        return run_str_content

    def merge_same_style_run_txt(
        self, run_content: list[HtmlRun | str | None]
    ) -> list[str]:
        """合并相同样式的run内容"""

        # 针对【同一段样式】的run内容做合并操作
        run_str_content: list[str] = []

        prev_run: HtmlRun | None = None

        for index, current_run in enumerate(run_content):
            if current_run is None:
                continue

            elif isinstance(current_run, str):
                # 将prev_run 添加到前面
                if prev_run is not None:
                    run_str_content.append(prev_run.content)
                    prev_run = None

                run_str_content.append(current_run)

            else:
                # 上一个run为空，且当前为空格
                if prev_run is None:
                    if current_run.only_space:
                        run_str_content.append(current_run.content)
                        continue

                    # 上一个run为空，且当前为非空格
                    else:
                        prev_run = current_run
                        continue

                # 上一个run不为空，且当前为空格
                elif prev_run is not None:
                    if current_run.only_space:
                        # 但前run为空格，采用前一个的样式
                        prev_run = HtmlRun(
                            prev_run.content + current_run.content,
                            False,
                            prev_run.style,
                        )
                        continue

                    # 上一个run不为空，且当前为非空格
                    else:
                        # 合并相同样式的字符
                        if current_run.style == prev_run.style:
                            # logger.info(
                            #     f"样式相同: {prev_run.content} + {current_run.content} => {current_run.style =} "
                            # )
                            prev_run = HtmlRun(
                                prev_run.content + current_run.content,
                                False,
                                current_run.style,
                            )

                        # 不合并字符，但将之前的字符加入到字符串中
                        # 同志将prev_run 指向 当前run
                        else:
                            run_str_content.append(prev_run.content)
                            prev_run = current_run

        # 处理最后一个run
        if prev_run is not None:
            run_str_content.append(prev_run.content)

        return run_str_content

    def merge_same_style_run_shtml(
        self, run_content: list[HtmlRun | str | None]
    ) -> list[str]:
        """合并相同样式的run内容"""

        # 针对【同一段样式】的run内容做合并操作
        run_str_content: list[str] = []

        prev_run: HtmlRun | None = None

        for index, current_run in enumerate(run_content):
            if current_run is None:
                continue

            elif isinstance(current_run, str):
                # 将prev_run 添加到前面
                if prev_run is not None:
                    run_str_content.append(prev_run.content)
                    prev_run = None

                run_str_content.append(current_run)

            else:
                # 上一个run为空，且当前为空格
                if prev_run is None:
                    if current_run.only_space:
                        run_str_content.append(current_run.content)
                        continue

                    # 上一个run为空，且当前为非空格
                    else:
                        prev_run = current_run
                        continue

                # 上一个run不为空，且当前为空格
                elif prev_run is not None:
                    if current_run.only_space:
                        # 但前run为空格，采用前一个的样式
                        prev_run = HtmlRun(
                            prev_run.content + current_run.content,
                            False,
                            prev_run.style,
                        )
                        continue

                    # 上一个run不为空，且当前为非空格
                    else:
                        # 合并相同样式的字符
                        if current_run.style == prev_run.style:
                            # logger.info(
                            #     f"样式相同: {prev_run.content} + {current_run.content} => {current_run.style =} "
                            # )
                            prev_run = HtmlRun(
                                prev_run.content + current_run.content,
                                False,
                                current_run.style,
                            )

                        # 不合并字符，但将之前的字符加入到字符串中
                        # 同志将prev_run 指向 当前run
                        else:
                            run_str_content.append(prev_run.content)
                            prev_run = current_run

        # 处理最后一个run
        if prev_run is not None:
            run_str_content.append(prev_run.content)

        return run_str_content

    def parse_paragrah_run_text(
        self, ele: CT_Text, character_styles: dict[str, Any]
    ) -> HtmlRun | None:
        """解析文本"""

        txt: str = ele.text or ""

        # 没有文本
        if not txt:
            return None

        # 1个空格
        if txt == " ":
            return HtmlRun(" ", True, "")

        # 全是空格:
        if self.is_all_spaces(txt) and self.render_format == RenderFormat.html:
            _txt = txt.replace("    ", "&emsp;")  # 四个空格
            _txt = txt.replace("  ", "&ensp;")  # 2个空格
            _txt = txt.replace(" ", "&nbsp;")  # 1个空格
            return HtmlRun(_txt, True, "")

        # 其他不可见字符, 比如 \n, \t, \r, \v, \f
        if txt.isspace() and self.render_format == RenderFormat.html:
            _txt = self.convert_invisible_to_html(txt)
            return HtmlRun(_txt, True, "")

        style_text = ";".join(
            [f"{key}:{value}" for key, value in character_styles.items()]
        )

        if style_text:
            return HtmlRun(txt, False, style_text)

        elif txt:
            return HtmlRun(txt, False, "")

        else:
            return HtmlRun(txt, True, "")

    def is_all_spaces(self, text: str) -> bool:
        """判断字符串是否全为空格且长度大于1"""
        return text.strip(" ") == "" and len(text) > 1

    def convert_invisible_to_html(self, text: str) -> str:
        """将多个不可见字符转为html字符"""

        html_escaped_text = []
        for char in text:
            if char == "\t":
                html_escaped_text.append("&emsp;")
            elif char == "\n":
                html_escaped_text.append("<br>")
            else:
                html_escaped_text.append(char)  # 其他空白字符（如垂直制表符等）

        return "".join(html_escaped_text)

    def parse_paragrah_run_text_4_number_text(
        self, text: str, character_styles: dict[str, Any]
    ) -> str:
        """解析文本"""

        # ctent = ele.replace(" ", "&nbsp;")

        # 1个空格
        if text == " ":
            ctent = text

        # 全是空格:
        elif self.is_all_spaces(text) and self.render_format == RenderFormat.html:
            ctent = text.replace("    ", "&emsp;")  # 四个空格
            ctent = ctent.replace("  ", "&ensp;")  # 2个空格
            ctent = ctent.replace(" ", "&nbsp;")  # 1个空格

        # 其他不可见字符, 比如 \n, \t, \r, \v, \f
        elif text.isspace() and self.render_format == RenderFormat.html:
            ctent = self.convert_invisible_to_html(text)

        else:
            ctent = text

        style_text = ";".join(
            [f"{key}:{value}" for key, value in character_styles.items()]
        )

        if self.render_format == RenderFormat.html:
            if style_text:
                return f"<span style='{style_text};'>{ctent}</span>"

            else:
                return f"<span>{ctent}</span>"

        else:
            return ctent

    # --- 正文表格块 ----
    def parse_table(self, ele: CT_Tbl) -> str:
        """解析表格"""

        # logger.info(ele.xml)

        # 表格样式
        table_styles: dict[str, Any] = {
            # https://developer.mozilla.org/zh-CN/docs/Web/CSS/border-spacing
            "border-spacing": "0",  # 浏览器默认边框间距设为0
            # https://developer.mozilla.org/zh-CN/docs/Web/CSS/border-collapse
            "border-collapse": "collapse",  # 表格边框属于合并还是分开模式, 浏览器默认分开模式.
        }

        # 表格单元格默认样式
        cell_styles: dict[str, Any] = {}

        # 段落样式
        paragraph_styles: dict[str, Any] = {}

        # 字符样式
        character_styles: dict[str, Any] = {}

        # 表格样式ID
        table_style_id: str | None = None

        if ele.tblPr is not None:
            # 样式表样式
            if ele.tblPr.tblStyle is not None:
                table_style_id = ele.tblPr.tblStyle.val_str

                # 样式表样式中的表格样式
                get_table_styles_from_define(
                    self.docx.styles, table_style_id, table_styles
                )
                # 样式表样式中的表格单元格样式
                get_cell_styles_from_define(
                    self.docx.styles, table_style_id, cell_styles
                )
                # 样式表样式中的表格段落样式
                get_table_paragraph_styles_from_define(
                    self.docx.styles, table_style_id, paragraph_styles
                )
                # 样式表样式中的表格字符样式
                get_table_character_styles_from_define(
                    self.docx.styles, table_style_id, character_styles
                )

            # 元素自身的样式
            get_table_styles(ele.tblPr, table_styles)
            get_table_cell_default_styls(ele.tblPr, cell_styles)

        # 行解析
        tblrows = ele.tr_lst

        # 单元格属性矩阵
        tcpr_matrix = gen_table_tcpr_matrix(ele)

        row_html_arr: list[str] = []

        for r_no, row in enumerate(tblrows):
            # 段落样式
            current_paragraph_styles = paragraph_styles.copy()

            # 字符样式
            current_character_styles = character_styles.copy()

            # 行样式
            current_row_styles: dict[str, Any] = {}

            # 单元格样式
            current_cell_styles = cell_styles.copy()

            # 条件样式获取，比如第一列，第一行，最后一行...的样式
            if (
                table_style_id is not None
                and row.trPr is not None
                and row.trPr.cnfStyle is not None
            ):
                if (
                    row.trPr.cnfStyle.firstRow is not None
                    and row.trPr.cnfStyle.firstRow
                ):
                    get_firstrow_styles_from_define(
                        self.docx.styles,
                        table_style_id,
                        current_paragraph_styles,
                        current_character_styles,
                        current_row_styles,
                        current_cell_styles,
                    )

            row_html = self.parse_table_row(
                row,
                current_row_styles,
                current_cell_styles,
                current_paragraph_styles,
                current_character_styles,
                r_no,
                tcpr_matrix,
            )

            row_html_arr.append(row_html)

        table_html_content = "\n".join(row_html_arr)

        if table_styles and self.render_format == RenderFormat.html:
            style_text = ";".join([f"{key}:{val}" for key, val in table_styles.items()])
            table_html = f'<table style="{style_text};">{table_html_content}</table>'

        elif table_styles and self.render_format == RenderFormat.shtml:
            # table_styles.pop("width", None)  # 不要宽度
            table_styles = {'border-collapse': 'collapse'}  # 表格标签只要border-collapse属性
            style_text = ";".join([f"{key}:{val}" for key, val in table_styles.items()])
            table_html = f'<table style="{style_text};">{table_html_content}</table>'

        elif self.render_format == RenderFormat.txt:
            table_html = table_html_content

        else:
            # 非html格式，仅包含基本的标签内容，用于转换
            table_html = f"<table>{table_html_content}</table>"

        # logger.info(table_html)

        # return table_html

        return table_html

    def parse_table_row(
        self,
        ele: CT_Row,
        row_default_styles: dict[str, Any],
        cell_default_styles: dict[str, Any],
        paragraph_styls: dict[str, Any],
        character_styles: dict[str, Any],
        row_no: int,
        tcpr_matrix: list[list[CT_TcPr | None]],
    ) -> str:
        """解析行(Row)里面的内容"""

        row_styles: dict[str, Any] = row_default_styles.copy()

        if ele.trPr is not None:
            row_styles = get_table_row_styles(ele.trPr, row_styles)

        # 行解析
        cell_html_arr: list[str] = []
        colspans: list[int] = []
        rowspans: list[int] = []  # 该变量声明，还未使用，以做不时之需.

        # 常规的tc标签
        for col_no, cell in enumerate(ele.tc_lst):
            colspans_total = sum(colspans)

            cell_html, colspan, rowspan = self.parse_table_cell(
                cell,
                cell_default_styles,
                paragraph_styls,
                character_styles,
                row_no,
                col_no,
                tcpr_matrix,
                colspans_total,
            )

            if cell_html is not None:
                cell_html_arr.append(cell_html) if cell_html is not None else ""

                colspans.append(colspan)
                rowspans.append(rowspan)

        # sdt标签里面的tc标签处理
        if (
            ele.sdt is not None
            and isinstance(ele.sdt, Union_CT_SdtCellRowRunBlock)
            and ele.sdt.sdtContent_cell is not None
            and ele.sdt.sdtContent_cell.tc_lst is not None
        ):
            for col_no, cell in enumerate(ele.sdt.sdtContent_cell.tc_lst):
                colspans_total = sum(colspans)

                cell_html, colspan, rowspan = self.parse_table_cell(
                    cell,
                    cell_default_styles,
                    paragraph_styls,
                    character_styles,
                    row_no,
                    col_no,
                    tcpr_matrix,
                    colspans_total,
                )

                if cell_html is not None:
                    cell_html_arr.append(cell_html) if cell_html is not None else ""

                    colspans.append(colspan)
                    rowspans.append(rowspan)

        # 封装tr标签内容
        row_html_content = "\n".join(cell_html_arr)

        if row_styles and self.render_format == RenderFormat.html:
            style_text = ";".join([f"{key}:{val}" for key, val in row_styles.items()])
            row_html = f'<tr style="{style_text};">{row_html_content}</tr>'
        elif row_styles and self.render_format == RenderFormat.shtml:
            # row_styles.pop("width", None)  # 不要宽度
            # style_text = ";".join([f"{key}:{val}" for key, val in row_styles.items()])
            # row_html = f'<tr style="{style_text};">{row_html_content}</tr>'
            row_html = f'<tr>{row_html_content}</tr>'

        elif self.render_format == RenderFormat.txt:
            row_html = '|'.join(cell_html_arr)

        else:
            # 非html格式，仅包含基本的标签内容，用于转换
            row_html = f"<tr>{row_html_content}</tr>"

        return row_html

    def parse_table_cell(
        self,
        ele: CT_Tc,
        cell_default_styls: dict[str, Any],
        table_paragraph_styls: dict[str, Any],
        table_character_styles: dict[str, Any],
        row_no: int,
        col_no: int,
        tcpr_matrix: list[list[CT_TcPr | None]],
        colspans_total: int,
    ) -> (
        tuple[None, ST_DecimalNumber | Literal[1], Literal[1]]
        | tuple[str, ST_DecimalNumber | int, int]
    ):
        """解析单元格里面的内容"""

        # 单元格属性
        # ele.tcPr

        cell_styles: dict[str, Any] = copy.deepcopy(cell_default_styls)
        paragraph_styls: dict[str, Any] = copy.deepcopy(table_paragraph_styls)
        character_styles: dict[str, Any] = copy.deepcopy(table_character_styles)

        # ---- 获取单元格内容 start -----

        # td标签中的段落解析
        pargraph_arr: list[HtmlParagraph | str] = []

        # 段落标签
        for pragraph in ele.p_lst:
            html_p = self.parse_paragraph(
                pragraph, paragraph_styls.copy(), character_styles.copy()
            )

            pargraph_arr.extend(html_p) if html_p is not None else ""

        # sdt 标签
        if (
            ele.sdt is not None
            and isinstance(ele.sdt, Union_CT_SdtCellRowRunBlock)
            and ele.sdt.sdtContent_block is not None
            and ele.sdt.sdtContent_block.p_lst is not None
        ):
            for p in ele.sdt.sdtContent_block.p_lst:
                pargraph_arr.extend(
                    self.parse_paragraph(
                        p, paragraph_styls.copy(), character_styles.copy()
                    )
                )

        # 封装td标签的内容
        td_html_content = self.render_paragraph(pargraph_arr)

        # logger.info(f"{td_html_content = }")

        # ---- 获取单元格内容 end -----

        # ---- 获取跨行跨列信息 start -----
        colspan: int = 1
        rowspan: int = 1

        if ele.tcPr is not None:
            get_table_cell_styles(ele.tcPr, cell_styles)
            colspan = get_table_cell_colspan(ele.tcPr)
            # logger.info(f"re{colspan = }")

            # 纵向合并的单元格,计算合并的行数
            if ele.tcPr.vMerge is not None and ele.tcPr.vMerge.val == ST_Merge.restart:
                # 可能存在跨列的情况, col_no不能真实反映当前cell所处的col索引.
                really_colspan = colspans_total if colspans_total > col_no else col_no
                rowspan = get_table_cell_rowspan(tcpr_matrix, row_no, really_colspan)

            # 说明当前单元格与前行单元格合并, 不处理当前单元格. 跳过.
            elif (
                ele.tcPr.vMerge is not None and ele.tcPr.vMerge.val == ST_Merge.Continue
            ):
                return None, colspan, rowspan  # type: ignore

        # logger.info(f"{colspan = }")
        # logger.info(f"{rowspan = }")

        # ---- 获取跨行跨列信息 end -----

        # ---- 封装html标签 start -----

        # td标签的属性解析
        td_attrs: dict[str, Any] = {}

        # 样式
        # 以html格式渲染时，才保存样式
        if cell_styles and self.render_format == RenderFormat.html:
            style_text = ";".join([f"{key}:{val}" for key, val in cell_styles.items()])
            td_attrs["style"] = f"{style_text};"

        elif cell_styles and self.render_format == RenderFormat.shtml:
            # cell_styles.pop("width", None)  # 不要宽度
            cell_styles = {"border": "1px solid #000"}
            style_text = ";".join([f"{key}: {val}" for key, val in cell_styles.items()])
            td_attrs["style"] = f"{style_text};"

        # colspan 跨列
        if colspan > 1:
            td_attrs["colspan"] = colspan

        # rowspan 跨行
        if rowspan > 1:
            td_attrs["rowspan"] = rowspan

        # 构造 <td> 结构
        if self.render_format in (RenderFormat.html, RenderFormat.shtml):
            if td_attrs and self.render_format == RenderFormat.html:
                td_attr_content = " ".join(
                    [f'{key}="{val}"' for key, val in td_attrs.items()]
                )
                td_html = f"<td {td_attr_content}>{td_html_content}</td>"
            else:
                td_html = f"<td>{td_html_content}</td>"

        elif self.render_format == RenderFormat.txt:
            td_html = td_html_content

        else:
            td_html = f"<td>{td_html_content}</td>"

        # ---- 封装html标签 end -----
        # logger.info(f"{td_html = }")

        return td_html, colspan, rowspan

    # ---- 绘制(drawing)对象块 -------

    def parse_drawing(self, ele: CT_Drawing) -> str | None:
        """解析绘制对象块，可能是形状， 图片..."""

        drawing = ele.drawing

        # logger.info(f"{type(drawing) = }")

        # 浮动对象
        if isinstance(drawing, wp_CT_Anchor):
            return self.parse_drawing_anchor(drawing)

        # 内联对象
        elif isinstance(drawing, wp_CT_Inline):
            return self.parse_drawing_inline(drawing)

        else:
            logger.warning(f"未知绘制对象类型: {type(drawing) = }")

        return None

    def parse_drawing_anchor(self, ele: wp_CT_Anchor) -> str | None:
        """解析浮动的对象： 图片， 表格， 形状..."""

        logger.info(f"处理浮动对象: {type(ele) = }")
        # 下面的处理与wp_CT_Inline对象一致.

        # 绘制对象的样式
        styles: dict[str, Any] = {}

        # 绘制对象的外边距
        if ele.dist_l is not None and ele.dist_l > 0:
            styles["margin-left"] = f"{Emu(ele.dist_l).pt}pt"

        elif ele.dist_t is not None and ele.dist_t > 0:
            styles["margin-top"] = f"{Emu(ele.dist_t).pt}pt"

        elif ele.dist_r is not None and ele.dist_r > 0:
            styles["margin-right"] = f"{Emu(ele.dist_r).pt}pt"

        elif ele.dist_b is not None and ele.dist_b > 0:
            styles["margin-bottom"] = f"{Emu(ele.dist_b).pt}pt"

        # 绘制对象的宽高
        styles["width"] = Emu(ele.extent.cx_val).px
        styles["height"] = Emu(ele.extent.cy_val).px
        styles["width_pt"] = Emu(ele.extent.cx_val).pt
        styles["height_pt"] = Emu(ele.extent.cy_val).pt

        # 解析具体的绘制对象
        # logger.info(ele.graphic.graphic_data.uri)
        graphic_data = ele.graphic.graphic_data
        graphic_data_uri = graphic_data.uri

        # 图表: 柱状图, 饼图...
        if graphic_data_uri == namespace_c:
            logger.info("解析图表...")

            return None

        # 图片
        elif graphic_data_uri == namespace_pic:
            logger.info("解析图片...")

            return self.parse_drawing_inline_picture(graphic_data.picuture_data, styles)

        # 表格
        elif graphic_data_uri == namespace_tb:
            logger.info("解析表格...")
            ...

        # 智能图形
        elif graphic_data_uri == namespace_dgm:
            logger.info("解析智能图形...")
            ...

        else:
            logger.warning(f"未知的{graphic_data_uri = }")

        return None

    def parse_drawing_inline(self, ele: wp_CT_Inline) -> str | None:
        """解析内联的对象： 图片， 表格， 形状..."""

        # logger.info(ele.xml)

        # 绘制对象的样式
        styles: dict[str, Any] = {}

        # 绘制对象的外边距
        if ele.dist_l is not None and ele.dist_l > 0:
            styles["margin-left"] = f"{Emu(ele.dist_l).pt}pt"

        elif ele.dist_t is not None and ele.dist_t > 0:
            styles["margin-top"] = f"{Emu(ele.dist_t).pt}pt"

        elif ele.dist_r is not None and ele.dist_r > 0:
            styles["margin-right"] = f"{Emu(ele.dist_r).pt}pt"

        elif ele.dist_b is not None and ele.dist_b > 0:
            styles["margin-bottom"] = f"{Emu(ele.dist_b).pt}pt"

        # 绘制对象的宽高
        styles["width"] = Emu(ele.extent.cx_val).px
        styles["height"] = Emu(ele.extent.cy_val).px
        styles["width_pt"] = Emu(ele.extent.cx_val).pt
        styles["height_pt"] = Emu(ele.extent.cy_val).pt

        # 解析具体的绘制对象
        # logger.info(ele.graphic.graphic_data.uri)
        graphic_data = ele.graphic.graphic_data
        graphic_data_uri = graphic_data.uri

        # 图表: 柱状图, 饼图...
        if graphic_data_uri == namespace_c:
            logger.info("解析图表...")

            return None

        # 图片
        elif graphic_data_uri == namespace_pic:
            logger.info("解析图片...")

            return self.parse_drawing_inline_picture(graphic_data.picuture_data, styles)

        # 表格
        elif graphic_data_uri == namespace_tb:
            logger.info("解析表格...")
            ...

        # 智能图形
        elif graphic_data_uri == namespace_dgm:
            logger.info("解析智能图形...")
            ...

        else:
            logger.warning(f"未知的{graphic_data_uri = }")

        return None

    def parse_drawing_inline_picture(self, ele: pct_CT_Picture, html_styls: dict[str, Any]
    ) -> str | None:
        """解析图片

        前端需要的结构:

        <vue-img id="BKmqavqoJFcs" data-toc-id="BKmqavqoJFcs" width="535" height="528" left="0" top="0" uuid="AWba3bMMF2HP" class="space-component" name="img" info="[{&quot;cover&quot;:&quot;&quot;,&quot;file_tags&quot;:[{&quot;id&quot;:101,&quot;name&quot;:&quot;发大水&quot;}],&quot;file_type&quot;:1,&quot;height&quot;:528,&quot;name&quot;:&quot;微信截图_20240113142451_339e9e.png&quot;,&quot;pk&quot;:326,&quot;public_file_tags&quot;:[],&quot;short_url&quot;:&quot;/proxy3/gateway/yunpan/shorturl?uid=1e6b2293-aab4-4607-b700-5724c924adeb&quot;,&quot;threed_model_id&quot;:null,&quot;thumbnail&quot;:&quot;/proxy3/gateway/yunpan/shorturl?uid=88b1126757284ac190dd893fe4fa3679&quot;,&quot;video_duration&quot;:null,&quot;width&quot;:535,&quot;link&quot;:null}]"></vue-img>

        [
            {
                "file_type": 1,
                "height": 528,
                "name": "微信截图_20240113142451_339e9e.png",
                "short_url": "/proxy3/gateway/yunpan/shorturl?uid=1e6b2293-aab4-4607-b700-5724c924adeb",
                "width": 535,
            }
        ]

        其他注意事项: vue-img 标签需要与p标签同级
        """

        if ele.blip_fill.blip is None:
            return None

        r_id = ele.blip_fill.blip.r_embed

        # 图片宽高
        img_width = html_styls["width"]
        img_height = html_styls["height"]

        return self.gen_img_by_rid(r_id, img_width, img_height)

    # ---- VML 对象块 -------

    def parse_object(self, ele: CT_Object) -> str | None:
        """解析 Object 对象

        <w:object>
            <v:shape id="_x0000_i1067" o:spt="75" type="#_x0000_t75" style="height:12pt;width:24.4pt;" o:ole="t" filled="f" o:preferrelative="t" stroked="f" coordsize="21600,21600">
                <v:path/>
                <v:fill on="f" focussize="0,0"/>
                <v:stroke on="f" color="#000000"/>
                <v:imagedata r:id="rId101" o:title="image49"/>
                <o:lock v:ext="edit" aspectratio="t"/>
                <w10:wrap type="none"/>
                <w10:anchorlock/>
            </v:shape>
            <o:OLEObject Type="Embed" ProgID="Package" ShapeID="_x0000_i1067" DrawAspect="Content" ObjectID="_1468075767" r:id="rId100">
                <o:LockedField>false</o:LockedField>
            </o:OLEObject>
        </w:object>
        """

        # logger.info(f"{type(ele.shape) =}")
        # logger.info(f"{type(ele.shape.imagedata) =}")
        # logger.info(f"{type(ele.ole_object) =}")

        if ele.shape is not None and ele.shape.imagedata is not None:
            return self.parse_object_image_shape(ele.shape, ele.shape.imagedata)

        else:
            logger.info("未解析的基于VML的形状...")

        return None

    def parse_object_image_shape(
        self, ele: v_CT_shape, imagedata: v_CT_ImageData
    ) -> str | None:
        """解析基于vml的由shape封装的图片"""

        if ele.style is None:
            return None

        if imagedata.r_id is None:
            return None

        width, height = get_wh_from_vml_sp_style(ele.style)

        r_id = imagedata.r_id

        width_pt = float(width[0:-2])
        height_pt = float(height[0:-2])

        return self.gen_img_by_rid(r_id, width_pt, height_pt)

    # ---- AlternateContent 对象块 -------

    def parse_alternateContent(self, ele: CT_MC_AlternateContent) -> str | None:
        """解析对象块:

        <mc:AlternateContent>
          <mc:Choice Requires="wps">
          ...
        </mc:AlternateContent>

        """

        # namespace_p
        # 优先从fallback 元素中获取对象，这个是对旧的版本软件做的兼容。
        pict: CT_Picture | None = getattr(ele.fallback, qn("w:pict"), None)  # type: ignore

        if pict is None:
            return None

        if pict.v_shap is None:
            return None

        if pict.v_shap.textbox is None:
            return None

        if pict.v_shap.textbox.txbx_content is None:
            return None

        paragraph_arr: list[HtmlParagraph | str] = []
        block_level_eles = pict.v_shap.textbox.txbx_content.block_level_eles

        for block_ele in block_level_eles:
            if isinstance(block_ele, CT_P):
                # paragraph_style = {"display": "inline-block"}
                html_p = self.parse_paragraph(block_ele, paragraph_tag="span")
                paragraph_arr.extend(html_p) if html_p is not None else ""

        # 渲染为html格式
        html_text = self.render_paragraph(paragraph_arr)

        # 块中嵌套块元素，用html元素表达始终有问题,先这样，后面看需求如何处理.
        return f'<span style="display: inline-block">{html_text}</span>'

    # ---- 生成img标签工具函数 -------

    def gen_img_by_rid(self, rid: str, width: float, height: float) -> str | None:
        """根据传入的img 的关系id，返回图片

        - rid: 关系id
        - width: 宽度, pt单位
        - height: 高度, pt单位
        """

        image = self.docx.get_image(rid)

        if image is None:
            return None

        # 转换图片
        if image.filename.endswith(".wmf") and ImageTool.wmf2gd_exists():
            image_bytes = ImageTool.convert_wmf_image(image)

            if not image_bytes:
                return f"<span>[{image.filename}]:转换wmf图片失败</span>"

        elif image.filename.endswith(".emf") and ImageTool.inkscape_exists():
            image_bytes = ImageTool.convert_emf_image_by_inkscape(image)

            if not image_bytes:
                return f"<span>[{image.filename}]:转换emf图片失败</span>"

        elif image.filename.endswith((".tif", ".tiff")):
            image_bytes = ImageTool.convert_tif_image_by_pil(image)

            if not image_bytes:
                return f"<span>[{image.filename}]:转换tif格式图片失败</span>"

        else:
            image_bytes = image.blob

        return self.gen_img_tag(image.filename, image.sha1, image_bytes, width, height)

    def gen_img_tag(
        self,
        filename: str,
        sha1: str,
        img_bytes: bytes,
        img_width: float,
        img_height: float,
    ) -> str:
        # 短链接
        short_url = OssTool.short_url(self.use_oss, sha1, img_bytes)

        # 图片大于56px(42pt)时, 封装成 vue-img 标签，页面上可以选中调节
        # if self.use_oss and img_width > 56:

        # 前端统一使用 <vue-img 标签
        if self.use_oss:
            ds = [
                {
                    "file_type": FileType.IMAGE.value,
                    "height": img_height,
                    "name": filename,
                    "short_url": short_url,
                    "width": img_width,
                }
            ]

            info = html.escape(json.dumps(ds))  # 对json字符串进行html字符转义

            vue_key = gen_random_characters(12)
            uuid_key = gen_random_characters(12)

            # id 和 data-toc-id必须一致.
            html_content = f'<vue-img id="{vue_key}" data-toc-id="{vue_key}" width="{img_width}" height="{img_height}" left="0" top="0" uuid="{uuid_key}" class="space-component" name="img" info="{info}" ></vue-img>'

        # 否则 封装成 给予 <img 的，使img的字在页面上可正常显示，版式与word中一致.
        elif self.use_oss and img_width < 56:
            html_content = f'<img src="{short_url}" alt="{filename}" width="{img_width}" height="{img_height}" />'

        # 本地调试时， 所有图片都基于base64显示.
        else:
            html_content = f'<img src="{short_url}" alt="{filename}" width="{img_width}" height="{img_height}" />'

        return html_content

    # ---- 生成html标签工具函数
    def render_paragraph(self, paragraph_arr: list[str | HtmlParagraph]) -> str:
        rendered_arr: list[str] = []

        context_spacing_arr: list[HtmlParagraph] = []

        for current_p in paragraph_arr:
            if isinstance(current_p, str):
                rendered_arr.append(current_p)
                continue

            # 处理上下文边距段落, 针对列表
            # http://192.168.2.53:8001/openxml/ecma-part1/chapter17/03paragraphs/#17319-contextualspacing-使用相同样式时忽略上方和下方的间距
            if current_p.styles.pop("contextualSpacing", False):
                context_spacing_arr.append(current_p)

            else:
                if context_spacing_arr:
                    rendered_arr.extend(
                        self.render_same_style_id_pragraphs(context_spacing_arr)
                    )
                    context_spacing_arr.clear()

                if self.render_format == RenderFormat.html:
                    rendered_arr.append(gen_paragraph_html(current_p))
                elif self.render_format == RenderFormat.shtml:
                    rendered_arr.append(gen_paragraph_shtml(current_p))
                else:
                    rendered_arr.append(gen_paragraph_txt(current_p))

        return "\n".join(rendered_arr)

    def render_same_style_id_pragraphs(self, paragraph_arr: list[HtmlParagraph]) -> list[str]:
        """针对同一组样式ID段落进行生成html并返回"""

        p_total = len(paragraph_arr)

        # 只有1个段落，不处理
        if p_total <= 1:
            if self.render_format == RenderFormat.html:
                return [gen_paragraph_html(current_p) for current_p in paragraph_arr]
            elif self.render_format == RenderFormat.shtml:
                return [gen_paragraph_shtml(current_p) for current_p in paragraph_arr]
            else:
                return [gen_paragraph_txt(current_p) for current_p in paragraph_arr]

        # 后续为, 处理上下文间距的段落
        # prev_p: Optional[HtmlParagraph] = None

        # 处理过上下文间距样式的段落
        new_paragraph_arr: list[HtmlParagraph] = []

        for idx in range(0, p_total):
            current_p = paragraph_arr[idx]

            # 第一个段落
            if idx == 0:
                # next_p = paragraph_arr[1]

                # next_p_margin_top = float(next_p.styles.get("margin-top", "0pt")[0:-2])  # type: ignore
                # curr_p_margin_bottom = float(
                #     current_p.styles.get("margin-top", "0pt")[0:-2]  # type: ignore
                # )

                # # 绝对值
                # new_current_p_margin_bottom = abs(
                #     next_p_margin_top - curr_p_margin_bottom
                # )

                new_current_p = copy.deepcopy(current_p)
                # new_current_p.styles["margin-bottom"] = f"{new_current_p_margin_bottom}pt"  # type: ignore
                new_current_p.styles["margin-bottom"] = "0pt"  # type: ignore
                new_paragraph_arr.append(new_current_p)

            # 最后1个段落
            elif idx + 1 == p_total:
                # prev_p = paragraph_arr[idx - 1]

                # prev_p_margin_bottom = float(prev_p.styles.get("margin-bottom", "0pt")[0:-2])  # type: ignore
                # curr_p_margin_top = float(current_p.styles.get("margin-top", "0pt")[0:-2])  # type: ignore

                # 绝对值
                # new_current_p_top = abs(curr_p_margin_top - prev_p_margin_bottom)

                new_current_p = copy.deepcopy(current_p)
                # new_current_p.styles["margin-top"] = f"{new_current_p_top}pt"  # type: ignore
                new_current_p.styles["margin-top"] = "0pt"  # type: ignore
                new_paragraph_arr.append(new_current_p)

            # 中间段落
            else:
                new_current_p = copy.deepcopy(current_p)
                new_current_p.styles["margin-top"] = "0pt"  # type: ignore
                new_current_p.styles["margin-bottom"] = "0pt"  # type: ignore
                new_paragraph_arr.append(new_current_p)

        if self.render_format == RenderFormat.html:
            return [gen_paragraph_html(current_p) for current_p in new_paragraph_arr]

        elif self.render_format == RenderFormat.shtml:
            return [gen_paragraph_shtml(current_p) for current_p in new_paragraph_arr]

        elif self.render_format == RenderFormat.txt:
            return [gen_paragraph_txt(current_p) for current_p in new_paragraph_arr]

        else:
            return [gen_paragraph_txt(current_p) for current_p in new_paragraph_arr]

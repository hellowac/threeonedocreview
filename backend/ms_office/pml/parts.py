"""
PrensentationML 部件概览

参考: http://192.168.2.53:8001/openxml/ecma-part1/chapter-16/#163-presentationml-概览
"""

from ..part import Part


class CommentAuthorsPart(Part):
    """评论作者部件

    根节点: cmAuthorLst
    """

    @property
    def oxml(self):
        """
        经过lxml解析过后的对象化的xml文档
        """
        from ..oxml.pml.core import CT_CommentAuthorList

        oxml: CT_CommentAuthorList = super().oxml

        return oxml


class CommentsPart(Part):
    """评论部件

    根节点: cmLst
    """

    @property
    def oxml(self):
        """
        经过lxml解析过后的对象化的xml文档
        """
        from ..oxml.pml.core import CT_CommentList

        oxml: CT_CommentList = super().oxml

        return oxml


class HandoutMasterPart(Part):
    """手稿母板部件

    根节点: handoutMaster
    """

    @property
    def oxml(self):
        """
        经过lxml解析过后的对象化的xml文档
        """
        from ..oxml.pml.core import CT_HandoutMaster

        oxml: CT_HandoutMaster = super().oxml

        return oxml


class NotesMasterPart(Part):
    """注释母板部件

    根节点: notesMaster
    """

    @property
    def oxml(self):
        """
        经过lxml解析过后的对象化的xml文档
        """
        from ..oxml.pml.core import CT_NotesMaster

        oxml: CT_NotesMaster = super().oxml

        return oxml


class NotesSlidePart(Part):
    """注释幻灯片部件

    根节点: notes
    """

    @property
    def oxml(self):
        """
        经过lxml解析过后的对象化的xml文档
        """
        from ..oxml.pml.core import CT_NotesSlide

        oxml: CT_NotesSlide = super().oxml

        return oxml


class PresentaionPart(Part):
    """演示文稿部件

    根节点: presentation
    """

    @property
    def oxml(self):
        """
        经过lxml解析过后的对象化的xml文档
        """
        from ..oxml.pml.core import CT_Presentation

        oxml: CT_Presentation = super().oxml

        return oxml


class PresentationPropertiesPart(Part):
    """演示文稿属性部件

    根节点: presentationPr
    """

    @property
    def oxml(self):
        """
        经过lxml解析过后的对象化的xml文档
        """
        from ..oxml.pml.core import CT_PresentationProperties

        oxml: CT_PresentationProperties = super().oxml

        return oxml


class SlidePart(Part):
    """幻灯片部件

    根节点: sld
    """

    @property
    def oxml(self):
        """
        经过lxml解析过后的对象化的xml文档
        """
        from ..oxml.pml.core import CT_Slide

        oxml: CT_Slide = super().oxml

        return oxml


class SlideLayoutPart(Part):
    """幻灯片布局部件

    根节点: sldLayout
    """

    @property
    def oxml(self):
        """
        经过lxml解析过后的对象化的xml文档
        """
        from ..oxml.pml.core import CT_SlideLayout

        oxml: CT_SlideLayout = super().oxml

        return oxml


class SlideMasterPart(Part):
    """幻灯片母板部件

    根节点: sldMaster
    """

    @property
    def oxml(self):
        """
        经过lxml解析过后的对象化的xml文档
        """
        from ..oxml.pml.core import CT_SlideMaster

        oxml: CT_SlideMaster = super().oxml

        return oxml


class SlideSynchronizationDataPart(Part):
    """幻灯片同步数据部件

    根节点: sldSyncPr
    """

    @property
    def oxml(self):
        """
        经过lxml解析过后的对象化的xml文档
        """
        from ..oxml.pml.core import CT_SlideSyncProperties

        oxml: CT_SlideSyncProperties = super().oxml

        return oxml


class UserDefinedTagsPart(Part):
    """用户定义标签部件

    根节点: tagLst
    """

    @property
    def oxml(self):
        """
        经过lxml解析过后的对象化的xml文档
        """
        from ..oxml.pml.core import CT_TagList

        oxml: CT_TagList = super().oxml

        return oxml


class ViewProperitesPart(Part):
    """视窗属性部件

    根节点: viewPr
    """

    @property
    def oxml(self):
        """
        经过lxml解析过后的对象化的xml文档
        """
        from ..oxml.pml.core import CT_ViewProperties

        oxml: CT_ViewProperties = super().oxml

        return oxml


class HTMLPublishLocation(Part):
    """html 发布地址"""

    ...


class SlideSynchronizationServerLocation(Part):
    """幻灯片同步服务器地址"""

    ...

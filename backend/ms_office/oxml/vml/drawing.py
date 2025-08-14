"""
参考文档: http://192.168.2.53:8001/openxml/ecma-part1/annexL/vml/ VML 简介.

以及ECMA-376 第一版 的 关于 vml 的文档.

- https://c-rex.net/samples/ooxml/e1/Part3/OOXML_P3_Primer_Introduction_topic_ID0EZA3O.html
- https://c-rex.net/samples/ooxml/e1/Part4/OOXML_P4_DOCX_VML_topic_ID0EZAUTB.html

本模块针对 vml-main.xsd 文档中定义的数据模型，

因为 vml 相对与 DrawingML 落后，所以该 vml 已不推荐.

在线 vml-officeDrawing.xsd schema 参考: http://www.datypic.com/sc/ooxml/s-vml-officeDrawing.xsd.html

<xsd:attribute name="bwmode" type="ST_BWMode" />
<xsd:attribute name="bwpure" type="ST_BWMode" />
<xsd:attribute name="bwnormal" type="ST_BWMode" />
<xsd:attribute name="targetscreensize" type="ST_ScreenSize" />
<xsd:attribute name="insetmode" type="ST_InsetMode" default="custom" />
<xsd:attribute name="spt" type="xsd:float" />
<xsd:attribute name="wrapcoords" type="xsd:string" />
<xsd:attribute name="oned" type="ST_TrueFalse" />
<xsd:attribute name="regroupid" type="xsd:integer" />
<xsd:attribute name="doubleclicknotify" type="ST_TrueFalse" />
<xsd:attribute name="connectortype" type="ST_ConnectorType" default="straight" />
<xsd:attribute name="button" type="ST_TrueFalse" />
<xsd:attribute name="userhidden" type="ST_TrueFalse" />
<xsd:attribute name="forcedash" type="ST_TrueFalse" />
<xsd:attribute name="oleicon" type="ST_TrueFalse" />
<xsd:attribute name="ole" type="ST_TrueFalseBlank" />
<xsd:attribute name="preferrelative" type="ST_TrueFalse" />
<xsd:attribute name="cliptowrap" type="ST_TrueFalse" />
<xsd:attribute name="clip" type="ST_TrueFalse" />
<xsd:attribute name="bullet" type="ST_TrueFalse" />
<xsd:attribute name="hr" type="ST_TrueFalse" />
<xsd:attribute name="hrstd" type="ST_TrueFalse" />
<xsd:attribute name="hrnoshade" type="ST_TrueFalse" />
<xsd:attribute name="hrpct" type="xsd:float" />
<xsd:attribute name="hralign" type="ST_HrAlign" default="left" />
<xsd:attribute name="allowincell" type="ST_TrueFalse" />
<xsd:attribute name="allowoverlap" type="ST_TrueFalse" />
<xsd:attribute name="userdrawn" type="ST_TrueFalse" />
<xsd:attribute name="bordertopcolor" type="xsd:string" />
<xsd:attribute name="borderleftcolor" type="xsd:string" />
<xsd:attribute name="borderbottomcolor" type="xsd:string" />
<xsd:attribute name="borderrightcolor" type="xsd:string" />
<xsd:attribute name="connecttype" type="ST_ConnectType" />
<xsd:attribute name="connectlocs" type="xsd:string" />
<xsd:attribute name="connectangles" type="xsd:string" />
<xsd:attribute name="master" type="xsd:string" />
<xsd:attribute name="extrusionok" type="ST_TrueFalse" />
<xsd:attribute name="href" type="xsd:string" />
<xsd:attribute name="althref" type="xsd:string" />
<xsd:attribute name="title" type="xsd:string" />
<xsd:attribute name="singleclick" type="ST_TrueFalse" />
<xsd:attribute name="oleid" type="xsd:float" />
<xsd:attribute name="detectmouseclick" type="ST_TrueFalse" />
<xsd:attribute name="movie" type="xsd:float" />
<xsd:attribute name="spid" type="xsd:string" />
<xsd:attribute name="opacity2" type="xsd:string" />
<xsd:attribute name="relid" type="ST_RelationshipId" />
<xsd:attribute name="dgmlayout" type="xsd:integer" />
<xsd:attribute name="dgmnodekind" type="xsd:integer" />
<xsd:attribute name="dgmlayoutmru" type="xsd:integer" />
<xsd:attribute name="gfxdata" type="xsd:base64Binary" />
<xsd:attribute name="tableproperties" type="xsd:string" />
<xsd:attribute name="tablelimits" type="xsd:string" />
"""

from __future__ import annotations

import logging

from ..base import (
    OxmlBaseElement,
    ST_BaseEnumType,
    lookup,
)
from .const import (
    NS_MAP as ns_map,
)
from .const import (
    NameSpace_o as namespace_o,  # 当前命名空间
)

logger = logging.getLogger(__name__)


def qn(tag: str):
    """将 dc:creator 这种的标签,转换为 {http://purl.org/dc/elements/1.1/}creator 这样的形式"""

    global ns_map

    if ":" not in tag:
        return tag

    ns_prefix, ns = tag.split(":")

    return f"{{{ns_map[ns_prefix]}}}{ns}"


class CT_Empty(OxmlBaseElement):
    """17.17.4 布尔属性 (CT_OnOff)

    此通用复杂类型指定了在整个 WordprocessingML 中使用的布尔属性。
    """

    @property
    def is_empty(self):
        return True


class v_AG_Ext(OxmlBaseElement):
    @property
    def ext(self):
        """VML Extension Handling Behavior

        <xsd:attributeGroup ref="v:AG_Ext" />
        """

        from .main import ST_Ext

        val = self.attrib.get(qn("v:ext"))

        if val is not None:
            return ST_Ext(val)


class CT_ShapeDefaults(v_AG_Ext):
    """New Shape Defaults

    <xsd:complexType name="CT_ShapeDefaults">
        <xsd:all minOccurs="0">
            <xsd:element ref="v:fill" minOccurs="0" />
            <xsd:element ref="v:stroke" minOccurs="0" />
            <xsd:element ref="v:textbox" minOccurs="0" />
            <xsd:element ref="v:shadow" minOccurs="0" />
            <xsd:element ref="skew" minOccurs="0" />
            <xsd:element ref="extrusion" minOccurs="0" />
            <xsd:element ref="callout" minOccurs="0">
                <xsd:annotation>
                    <xsd:documentation>Callout</xsd:documentation>
                </xsd:annotation>
            </xsd:element>
            <xsd:element ref="lock" minOccurs="0">
                <xsd:annotation>
                    <xsd:documentation>Shape Protections</xsd:documentation>
                </xsd:annotation>
            </xsd:element>
            <xsd:element name="colormru" minOccurs="0" type="CT_ColorMru">
                <xsd:annotation>
                    <xsd:documentation>Most Recently Used Colors</xsd:documentation>
                </xsd:annotation>
            </xsd:element>
            <xsd:element name="colormenu" minOccurs="0" type="CT_ColorMenu">
                <xsd:annotation>
                    <xsd:documentation>UI Default Colors</xsd:documentation>
                </xsd:annotation>
            </xsd:element>
        </xsd:all>
        <xsd:attributeGroup ref="v:AG_Ext" />
        <xsd:attribute name="spidmax" type="xsd:integer" use="optional">
            <xsd:annotation>
                <xsd:documentation>Shape ID Optional Storage</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="style" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Shape Styling Properties</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="fill" type="ST_TrueFalse" use="optional">
            <xsd:annotation>
                <xsd:documentation>Shape Fill Toggle</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="fillcolor" type="ST_ColorType" use="optional">
            <xsd:annotation>
                <xsd:documentation>Default Fill Color</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="stroke" type="ST_TrueFalse" use="optional">
            <xsd:annotation>
                <xsd:documentation>Shape Stroke Toggle</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="strokecolor" type="ST_ColorType">
            <xsd:annotation>
                <xsd:documentation>Shape Stroke Color</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="allowincell" form="qualified" type="ST_TrueFalse">
            <xsd:annotation>
                <xsd:documentation>Allow in Table Cell</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
    </xsd:complexType>
    """

    @property
    def v_fill(self):
        ele: CT_Fill | None = getattr(self, qn("v:fill"), None)

        return ele

    @property
    def v_stroke(self):
        from .main import CT_Stroke

        ele: CT_Stroke | None = getattr(self, qn("v:stroke"), None)

        return ele

    @property
    def v_textbox(self):
        from .main import CT_Textbox

        ele: CT_Textbox | None = getattr(self, qn("v:textbox"), None)

        return ele

    @property
    def v_shadow(self):
        from .main import CT_Shadow

        ele: CT_Shadow | None = getattr(self, qn("v:shadow"), None)

        return ele

    @property
    def skew(self):
        return getattr(self, qn("o:skew"), None)

    @property
    def extrusion(self):
        return getattr(self, qn("o:extrusion"), None)

    @property
    def callout(self):
        """Callout"""

        return getattr(self, qn("o:callout"), None)

    @property
    def lock(self):
        """Shape Protections"""

        return getattr(self, qn("o:lock"), None)

    @property
    def colormenu(self) -> CT_ColorMenu | None:
        """Most Recently Used Colors"""

        return getattr(self, qn("o:colormenu"), None)

    @property
    def colormru(self) -> CT_ColorMru | None:
        """Most Recently Used Colors"""

        return getattr(self, qn("o:colormru"), None)

    @property
    def ext(self):
        """VML Extension Handling Behavior

        <xsd:attributeGroup ref="v:AG_Ext" />
        """

        from .main import ST_Ext

        val = self.attrib.get(qn("v:ext"))

        if val is not None:
            return ST_Ext(val)

    @property
    def spidmax(self) -> int | None:
        """Shape ID Optional Storage"""

        val = self.attrib.get(qn("o:spidmax"))
        if val is not None:
            return int(val)

    @property
    def style(self) -> str | None:
        """Shape Styling Propertiesn>"""

        val = self.attrib.get(qn("o:style"))
        if val is not None:
            return str(val)

    @property
    def fill(self) -> ST_TrueFalse | None:
        """Shape Fill Toggle"""

        val = self.attrib.get(qn("o:fill"))
        if val is not None:
            return ST_TrueFalse(val)

    @property
    def fillcolor(self) -> ST_ColorType | None:
        """Default Fill Color"""

        val = self.attrib.get(qn("o:fillcolor"))
        if val is not None:
            return ST_ColorType(val)

    @property
    def stroke(self) -> ST_TrueFalse | None:
        """Shape Stroke Toggle"""

        val = self.attrib.get(qn("o:stroke"))
        if val is not None:
            return ST_TrueFalse(val)

    @property
    def strokecolor(self) -> ST_ColorType | None:
        """Shape Stroke Coloron>"""

        val = self.attrib.get(qn("o:strokecolor"))
        if val is not None:
            return ST_ColorType(val)

    @property
    def allowincell(self) -> ST_TrueFalse | None:
        """Allow in Table Cell"""

        val = self.attrib.get(qn("o:allowincell"))
        if val is not None:
            return ST_TrueFalse(val)


class CT_Ink(OxmlBaseElement):
    """

    <xsd:complexType name="CT_Ink">
        <xsd:sequence></xsd:sequence>
        <xsd:attribute name="i" type="xsd:base64Binary">
            <xsd:annotation>
                <xsd:documentation>Ink Data</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="annotation" type="ST_TrueFalse">
            <xsd:annotation>
                <xsd:documentation>Annotation Flag</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
    </xsd:complexType>
    """

    @property
    def i(self) -> str | None:
        """Ink Data

        <xsd:attribute name="i" type="xsd:base64Binary">
            <xsd:annotation>
                <xsd:documentation>Ink Data</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:i"))

        if val is not None:
            return str(val)

    @property
    def annotation(self) -> ST_TrueFalse | None:
        """Annotation Flag

        <xsd:attribute name="i" type="xsd:base64Binary">
            <xsd:annotation>
                <xsd:documentation>Ink Data</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:annotation"))

        if val is not None:
            return ST_TrueFalse(val)


class CT_SignatureLine(v_AG_Ext):
    """

    <xsd:complexType name="CT_SignatureLine">
        <xsd:attributeGroup ref="v:AG_Ext" />
        <xsd:attribute name="issignatureline" type="ST_TrueFalse">
            <xsd:annotation>
                <xsd:documentation>Signature Line Flag</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="id" type="ST_Guid">
            <xsd:annotation>
                <xsd:documentation>Unique ID</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="provid" type="ST_Guid">
            <xsd:annotation>
                <xsd:documentation>Signature Provider ID</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="signinginstructionsset" type="ST_TrueFalse">
            <xsd:annotation>
                <xsd:documentation>Use Signing Instructions Flag</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="allowcomments" type="ST_TrueFalse">
            <xsd:annotation>
                <xsd:documentation>User-specified Comments Flag</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="showsigndate" type="ST_TrueFalse">
            <xsd:annotation>
                <xsd:documentation>Show Signed Date Flag</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="suggestedsigner" type="xsd:string" form="qualified">
            <xsd:annotation>
                <xsd:documentation>Suggested Signer Line 1</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="suggestedsigner2" type="xsd:string" form="qualified">
            <xsd:annotation>
                <xsd:documentation>Suggested Signer Line 2</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="suggestedsigneremail" type="xsd:string" form="qualified">
            <xsd:annotation>
                <xsd:documentation>Suggested Signer E-mail Address</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="signinginstructions" type="xsd:string">
            <xsd:annotation>
                <xsd:documentation>Instructions for Signing</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="addlxml" type="xsd:string">
            <xsd:annotation>
                <xsd:documentation>Additional Signature Information</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="sigprovurl" type="xsd:string">
            <xsd:annotation>
                <xsd:documentation>Signature Provider Download URL</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
    </xsd:complexType>
    """

    @property
    def issignatureline(self) -> ST_TrueFalse | None:
        """Signature Line Flag"""

        val = self.attrib.get(qn("o:issignatureline"))
        if val is not None:
            return ST_TrueFalse(val)

    @property
    def id(self) -> ST_Guid | None:
        """Unique ID"""

        val = self.attrib.get(qn("o:id"))
        if val is not None:
            return ST_Guid(val)

    @property
    def provid(self) -> ST_Guid | None:
        """Signature Provider ID"""

        val = self.attrib.get(qn("o:provid"))
        if val is not None:
            return ST_Guid(val)

    @property
    def signinginstructionsset(self) -> ST_TrueFalse | None:
        """Use Signing Instructions Flag"""

        val = self.attrib.get(qn("o:signinginstructionsset"))
        if val is not None:
            return ST_TrueFalse(val)

    @property
    def allowcomments(self) -> ST_TrueFalse | None:
        """User-specified Comments Flag"""

        val = self.attrib.get(qn("o:allowcomments"))
        if val is not None:
            return ST_TrueFalse(val)

    @property
    def showsigndate(self) -> ST_TrueFalse | None:
        """Show Signed Date Flag"""

        val = self.attrib.get(qn("o:showsigndate"))
        if val is not None:
            return ST_TrueFalse(val)

    @property
    def suggestedsigner(self) -> str | None:
        """Suggested Signer Line 1"""

        val = self.attrib.get(qn("o:suggestedsigner"))
        if val is not None:
            return str(val)

    @property
    def suggestedsigner2(self) -> str | None:
        """Suggested Signer Line 2"""

        val = self.attrib.get(qn("o:suggestedsigner2"))
        if val is not None:
            return str(val)

    @property
    def suggestedsigneremail(self) -> str | None:
        """Suggested Signer E-mail Address"""

        val = self.attrib.get(qn("o:suggestedsigneremail"))
        if val is not None:
            return str(val)

    @property
    def signinginstructions(self) -> str | None:
        """Instructions for Signing"""

        val = self.attrib.get(qn("o:signinginstructions"))
        if val is not None:
            return str(val)

    @property
    def addlxml(self) -> str | None:
        """Additional Signature Information"""

        val = self.attrib.get(qn("o:addlxml"))
        if val is not None:
            return str(val)

    @property
    def sigprovurl(self) -> str | None:
        """Signature Provider Download URL"""

        val = self.attrib.get(qn("o:sigprovurl"))
        if val is not None:
            return str(val)


class CT_ShapeLayout(v_AG_Ext):
    """
    <xsd:complexType name="CT_ShapeLayout">
        <xsd:all>
            <xsd:element name="idmap" type="CT_IdMap" minOccurs="0">
                <xsd:annotation>
                    <xsd:documentation>Shape ID Map</xsd:documentation>
                </xsd:annotation>
            </xsd:element>
            <xsd:element name="regrouptable" type="CT_RegroupTable" minOccurs="0">
                <xsd:annotation>
                    <xsd:documentation>Shape Grouping History</xsd:documentation>
                </xsd:annotation>
            </xsd:element>
            <xsd:element name="rules" type="CT_Rules" minOccurs="0">
                <xsd:annotation>
                    <xsd:documentation>Rule Set</xsd:documentation>
                </xsd:annotation>
            </xsd:element>
        </xsd:all>
        <xsd:attributeGroup ref="v:AG_Ext" />
    </xsd:complexType>
    """

    def idmap(self) -> CT_IdMap | None:
        """Shape ID Map"""

        return getattr(self, qn("o:idmap"), None)

    def regrouptable(self) -> CT_RegroupTable | None:
        """Shape Grouping History"""

        return getattr(self, qn("o:regrouptable"), None)

    def rules(self) -> CT_Rules | None:
        """Rule Set"""

        return getattr(self, qn("o:rules"), None)


class CT_IdMap(v_AG_Ext):
    """
    <xsd:complexType name="CT_IdMap">
        <xsd:attributeGroup ref="v:AG_Ext" />
        <xsd:attribute name="data" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Shape IDs</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
    </xsd:complexType>
    """

    @property
    def data(self) -> str | None:
        """Shape IDs"""

        val = self.attrib.get(qn("o:data"))
        if val is not None:
            return str(val)


class CT_RegroupTable(v_AG_Ext):
    """
    <xsd:complexType name="CT_RegroupTable">
        <xsd:sequence>
            <xsd:element name="entry" type="CT_Entry" minOccurs="0" maxOccurs="unbounded">
                <xsd:annotation>
                    <xsd:documentation>Regroup Entry</xsd:documentation>
                </xsd:annotation>
            </xsd:element>
        </xsd:sequence>
        <xsd:attributeGroup ref="v:AG_Ext" />
    </xsd:complexType>
    """

    def entry(self) -> list[CT_Entry]:
        """Regroup Entry"""

        return self.findall(qn("o:entry"))  # type: ignore


class CT_Entry(OxmlBaseElement):
    """
    <xsd:complexType name="CT_Entry">
        <xsd:attribute name="new" type="xsd:int" use="optional">
            <xsd:annotation>
                <xsd:documentation>New Group ID</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="old" type="xsd:int" use="optional">
            <xsd:annotation>
                <xsd:documentation>Old Group ID</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
    </xsd:complexType>
    """

    @property
    def new(self) -> int | None:
        """New Group ID"""

        val = self.attrib.get(qn("o:new"))
        if val is not None:
            return int(val)

    @property
    def old(self) -> int | None:
        """Old Group ID"""

        val = self.attrib.get(qn("o:old"))
        if val is not None:
            return int(val)


class CT_Rules(v_AG_Ext):
    """
    <xsd:complexType name="CT_Rules">
        <xsd:sequence>
            <xsd:element name="r" type="CT_R" minOccurs="0" maxOccurs="unbounded">
                <xsd:annotation>
                    <xsd:documentation>Rule</xsd:documentation>
                </xsd:annotation>
            </xsd:element>
        </xsd:sequence>
        <xsd:attributeGroup ref="v:AG_Ext" />
    </xsd:complexType>
    """

    def r(self) -> list[CT_R]:
        """Rule"""

        return self.findall(qn("o:r"))  # type: ignore


class CT_R(OxmlBaseElement):
    """
    <xsd:complexType name="CT_R">
        <xsd:sequence>
            <xsd:element name="proxy" type="CT_Proxy" minOccurs="0" maxOccurs="unbounded">
                <xsd:annotation>
                    <xsd:documentation>Shape Reference</xsd:documentation>
                </xsd:annotation>
            </xsd:element>
        </xsd:sequence>
        <xsd:attribute name="id" type="xsd:string" use="required">
            <xsd:annotation>
                <xsd:documentation>Rule ID</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="type" type="ST_RType" use="optional">
            <xsd:annotation>
                <xsd:documentation>Rule Type</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="how" type="ST_How" use="optional">
            <xsd:annotation>
                <xsd:documentation>Alignment Rule Type</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="idref" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Rule Shape Reference</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
    </xsd:complexType>
    """

    def proxy(self) -> list[CT_Proxy]:
        """Shape Reference"""

        return self.findall(qn("o:proxy"))  # type: ignore

    @property
    def id(self) -> str | None:
        """Rule ID


        <xsd:attribute name="id" type="xsd:string" use="required">
            <xsd:annotation>
                <xsd:documentation>Rule ID</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:id"))
        if val is not None:
            return str(val)

    @property
    def idref(self) -> int | None:
        """Rule Shape Reference

        <xsd:attribute name="idref" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Rule Shape Reference</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:idref"))
        if val is not None:
            return int(val)

    @property
    def type(self) -> ST_RType | None:
        """Rule Type


        <xsd:attribute name="type" type="ST_RType" use="optional">
            <xsd:annotation>
                <xsd:documentation>Rule Type</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:type"))
        if val is not None:
            return ST_RType(val)

    @property
    def how(self) -> ST_How | None:
        """Alignment Rule Type

        <xsd:attribute name="how" type="ST_How" use="optional">
            <xsd:annotation>
                <xsd:documentation>Alignment Rule Type</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:how"))
        if val is not None:
            return ST_How(val)


class CT_Proxy(OxmlBaseElement):
    """
    <xsd:complexType name="CT_Proxy">
        <xsd:attribute name="start" type="ST_TrueFalseBlank" use="optional" default="false">
            <xsd:annotation>
                <xsd:documentation>Start Point Connection Flag</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="end" type="ST_TrueFalseBlank" use="optional" default="false">
            <xsd:annotation>
                <xsd:documentation>End Point Connection Flag</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="idref" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Proxy Shape Reference</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="connectloc" type="xsd:int" use="optional">
            <xsd:annotation>
                <xsd:documentation>Connection Location</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
    </xsd:complexType>
    """

    @property
    def start(self) -> ST_TrueFalseBlank:
        """Start Point Connection Flag

        <xsd:attribute name="start" type="ST_TrueFalseBlank" use="optional" default="false">
            <xsd:annotation>
                <xsd:documentation>Start Point Connection Flag</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("start"))

        if val is not None:
            return ST_TrueFalseBlank(val)

        return ST_TrueFalseBlank("false")

    @property
    def end(self) -> ST_TrueFalseBlank:
        """End Point Connection Flag

        <xsd:attribute name="end" type="ST_TrueFalseBlank" use="optional" default="false">
            <xsd:annotation>
                <xsd:documentation>End Point Connection Flag</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("type"))

        if val is not None:
            return ST_TrueFalseBlank(val)

        return ST_TrueFalseBlank("false")

    @property
    def idref(self) -> str | None:
        """Proxy Shape Reference

        <xsd:attribute name="idref" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Proxy Shape Reference</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("idref"))

        if val is not None:
            return str(val)

    @property
    def connectloc(self) -> int | None:
        """Connection Location

        <xsd:attribute name="connectloc" type="xsd:int" use="optional">
            <xsd:annotation>
                <xsd:documentation>Connection Location</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("connectloc"))

        if val is not None:
            return int(val)


class CT_Diagram(v_AG_Ext):
    """

    <xsd:complexType name="CT_Diagram">
        <xsd:sequence>
            <xsd:element name="relationtable" type="CT_RelationTable" minOccurs="0">
                <xsd:annotation>
                    <xsd:documentation>Diagram Relationship Table</xsd:documentation>
                </xsd:annotation>
            </xsd:element>
        </xsd:sequence>
        <xsd:attributeGroup ref="v:AG_Ext" />
        <xsd:attribute name="dgmstyle" type="xsd:integer" use="optional">
            <xsd:annotation>
                <xsd:documentation>Diagram Style Options</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="autoformat" type="ST_TrueFalse" use="optional">
            <xsd:annotation>
                <xsd:documentation>Diagram Automatic Format</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="reverse" type="ST_TrueFalse" use="optional">
            <xsd:annotation>
                <xsd:documentation>Diagram Reverse Direction</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="autolayout" type="ST_TrueFalse" use="optional">
            <xsd:annotation>
                <xsd:documentation>Diagram Automatic Layout</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="dgmscalex" type="xsd:integer" use="optional">
            <xsd:annotation>
                <xsd:documentation>Diagram Layout X Scale</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="dgmscaley" type="xsd:integer" use="optional">
            <xsd:annotation>
                <xsd:documentation>Diagram Layout Y Scale</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="dgmfontsize" type="xsd:integer" use="optional">
            <xsd:annotation>
                <xsd:documentation>Diagram Font Size</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="constrainbounds" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Diagram Layout Extents</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="dgmbasetextscale" type="xsd:integer" use="optional">
            <xsd:annotation>
                <xsd:documentation>Diagram Base Font Size</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
    </xsd:complexType>
    """

    def relationtable(self) -> CT_RelationTable | None:
        """Diagram Relationship Table

        <xsd:element name="relationtable" type="CT_RelationTable" minOccurs="0">
            <xsd:annotation>
                <xsd:documentation>Diagram Relationship Table</xsd:documentation>
            </xsd:annotation>
        </xsd:element>
        """

        return getattr(self, qn("o:relationtable"))

    def dgmstyle(self) -> int | None:
        """Diagram Style Options

        <xsd:attribute name="dgmstyle" type="xsd:integer" use="optional">
            <xsd:annotation>
                <xsd:documentation>Diagram Style Options</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:dgmstyle"))

        if val is not None:
            return int(val)

    def autoformat(self) -> ST_TrueFalse | None:
        """Diagram Automatic Format

        <xsd:attribute name="autoformat" type="ST_TrueFalse" use="optional">
            <xsd:annotation>
                <xsd:documentation>Diagram Automatic Format</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:autoformat"))

        if val is not None:
            return ST_TrueFalse(val)

    def reverse(self) -> ST_TrueFalse | None:
        """Diagram Reverse Direction

        <xsd:attribute name="reverse" type="ST_TrueFalse" use="optional">
            <xsd:annotation>
                <xsd:documentation>Diagram Reverse Direction</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:reverse"))

        if val is not None:
            return ST_TrueFalse(val)

    def autolayout(self) -> ST_TrueFalse | None:
        """Diagram Automatic Layout

        <xsd:attribute name="autolayout" type="ST_TrueFalse" use="optional">
            <xsd:annotation>
                <xsd:documentation>Diagram Automatic Layout</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:autolayout"))

        if val is not None:
            return ST_TrueFalse(val)

    def dgmscalex(self) -> int | None:
        """Diagram Layout X Scale

        <xsd:attribute name="dgmscalex" type="xsd:integer" use="optional">
            <xsd:annotation>
                <xsd:documentation>Diagram Layout X Scale</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:dgmscalex"))

        if val is not None:
            return int(val)

    def dgmscaley(self) -> int | None:
        """Diagram Layout Y Scale

        <xsd:attribute name="dgmscaley" type="xsd:integer" use="optional">
            <xsd:annotation>
                <xsd:documentation>Diagram Layout Y Scale</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:dgmscaley"))

        if val is not None:
            return int(val)

    def dgmfontsize(self) -> int | None:
        """Diagram Font Size

        <xsd:attribute name="dgmfontsize" type="xsd:integer" use="optional">
            <xsd:annotation>
                <xsd:documentation>Diagram Font Size</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:dgmfontsize"))

        if val is not None:
            return int(val)

    def constrainbounds(self) -> str | None:
        """Diagram Layout Extents

        <xsd:attribute name="constrainbounds" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Diagram Layout Extents</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:constrainbounds"))

        if val is not None:
            return str(val)

    def dgmbasetextscale(self) -> int | None:
        """Diagram Base Font Size

        <xsd:attribute name="dgmbasetextscale" type="xsd:integer" use="optional">
            <xsd:annotation>
                <xsd:documentation>Diagram Base Font Size</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:dgmbasetextscale"))

        if val is not None:
            return int(val)


class CT_RelationTable(v_AG_Ext):
    """
    <xsd:complexType name="CT_RelationTable">
        <xsd:sequence>
            <xsd:element name="rel" type="CT_Relation" minOccurs="0" maxOccurs="unbounded">
                <xsd:annotation>
                    <xsd:documentation>Diagram Relationship</xsd:documentation>
                </xsd:annotation>
            </xsd:element>
        </xsd:sequence>
        <xsd:attributeGroup ref="v:AG_Ext" />
    </xsd:complexType>
    """

    def rel(self) -> list[CT_Relation]:
        """Diagram Relationship

        <xsd:element name="rel" type="CT_Relation" minOccurs="0" maxOccurs="unbounded">
            <xsd:annotation>
                <xsd:documentation>Diagram Relationship</xsd:documentation>
            </xsd:annotation>
        </xsd:element>
        """

        return self.findall(qn("o:rel"))  # type: ignore


class CT_Relation(v_AG_Ext):
    """
    <xsd:complexType name="CT_Relation">
        <xsd:attributeGroup ref="v:AG_Ext" />
        <xsd:attribute name="idsrc" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Diagram Relationship Source Shape</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="iddest" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Diagram Relationship Destination Shape</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="idcntr" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Diagram Relationship Center Shape</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
    </xsd:complexType>
    """

    @property
    def idsrc(self) -> str | None:
        """Diagram Relationship Source Shape

        <xsd:attribute name="idsrc" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Diagram Relationship Source Shape</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:idsrc"))

        if val is not None:
            return str(val)

    @property
    def iddest(self) -> str | None:
        """Diagram Relationship Destination Shape

        <xsd:attribute name="iddest" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Diagram Relationship Destination Shape</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:iddest"))

        if val is not None:
            return str(val)

    @property
    def idcntr(self) -> str | None:
        """Diagram Relationship Center Shape

        <xsd:attribute name="idcntr" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Diagram Relationship Center Shape</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:idcntr"))

        if val is not None:
            return str(val)


class CT_ColorMru(v_AG_Ext):
    """
    <xsd:complexType name="CT_ColorMru">
        <xsd:attributeGroup ref="v:AG_Ext" />
        <xsd:attribute name="colors" type="xsd:string">
            <xsd:annotation>
                <xsd:documentation>Recent colors</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
    </xsd:complexType>
    """

    def colors(self) -> str:
        """Recent colors

        <xsd:attribute name="colors" type="xsd:string">
            <xsd:annotation>
                <xsd:documentation>Recent colors</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib[qn("o:colors")]

        return str(val)


class CT_ColorMenu(v_AG_Ext):
    """
    <xsd:complexType name="CT_ColorMenu">
        <xsd:attributeGroup ref="v:AG_Ext" />
        <xsd:attribute name="strokecolor" type="ST_ColorType">
            <xsd:annotation>
                <xsd:documentation>Default stroke color</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="fillcolor" type="ST_ColorType">
            <xsd:annotation>
                <xsd:documentation>Default fill color</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="shadowcolor" type="ST_ColorType">
            <xsd:annotation>
                <xsd:documentation>Default shadow color</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="extrusioncolor" type="ST_ColorType">
            <xsd:annotation>
                <xsd:documentation>Default extrusion color</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
    </xsd:complexType>
    """

    def strokecolor(self) -> ST_ColorType:
        """Default stroke color

        <xsd:attribute name="strokecolor" type="ST_ColorType">
            <xsd:annotation>
                <xsd:documentation>Default stroke color</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib[qn("o:strokecolor")]

        return ST_ColorType(val)

    def fillcolor(self) -> ST_ColorType:
        """Default fill color

        <xsd:attribute name="fillcolor" type="ST_ColorType">
            <xsd:annotation>
                <xsd:documentation>Default fill color</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib[qn("o:fillcolor")]

        return ST_ColorType(val)

    def shadowcolor(self) -> ST_ColorType:
        """Default shadow color

        <xsd:attribute name="shadowcolor" type="ST_ColorType">
            <xsd:annotation>
                <xsd:documentation>Default shadow color</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib[qn("o:shadowcolor")]

        return ST_ColorType(val)

    def extrusioncolor(self) -> ST_ColorType:
        """Default extrusion color

        <xsd:attribute name="extrusioncolor" type="ST_ColorType">
            <xsd:annotation>
                <xsd:documentation>Default extrusion color</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib[qn("o:extrusioncolor")]

        return ST_ColorType(val)


class CT_Skew(v_AG_Ext):
    """

    <xsd:complexType name="CT_Skew">
        <xsd:attributeGroup ref="v:AG_Ext" />
        <xsd:attribute name="id" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Skew ID</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="on" type="ST_TrueFalse" use="optional">
            <xsd:annotation>
                <xsd:documentation>Skew Toggle</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="offset" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Skew Offset</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="origin" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Skew Origin</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="matrix" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Skew Perspective Matrix</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
    </xsd:complexType>
    """

    @property
    def id(self) -> str | None:
        """Skew ID

        <xsd:attribute name="id" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Skew ID</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:id"))

        if val is not None:
            return str(val)

    @property
    def on(self) -> ST_TrueFalse | None:
        """Skew Toggle

        <xsd:attribute name="on" type="ST_TrueFalse" use="optional">
            <xsd:annotation>
                <xsd:documentation>Skew Toggle</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:on"))

        if val is not None:
            return ST_TrueFalse(val)

    @property
    def offset(self) -> str | None:
        """Skew Offset

        <xsd:attribute name="offset" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Skew Offset</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:offset"))

        if val is not None:
            return str(val)

    @property
    def origin(self) -> str | None:
        """Skew Origin

        <xsd:attribute name="origin" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Skew Origin</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:origin"))

        if val is not None:
            return str(val)

    @property
    def matrix(self) -> str | None:
        """Skew Perspective Matrix

        <xsd:attribute name="matrix" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Skew Perspective Matrix</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:matrix"))

        if val is not None:
            return str(val)


class CT_Extrusion(v_AG_Ext):
    """
    <xsd:complexType name="CT_Extrusion">
        <xsd:attributeGroup ref="v:AG_Ext" />
        <xsd:attribute name="on" type="ST_TrueFalse" use="optional">
            <xsd:annotation>
                <xsd:documentation>Extrusion Toggle</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="type" type="ST_ExtrusionType" default="parallel" use="optional">
            <xsd:annotation>
                <xsd:documentation>Extrusion Type</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="render" type="ST_ExtrusionRender" default="solid" use="optional">
            <xsd:annotation>
                <xsd:documentation>Extrusion Render Mode</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="viewpointorigin" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Extrusion Viewpoint Origin</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="viewpoint" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Extrusion Viewpoint</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="plane" type="ST_ExtrusionPlane" default="XY" use="optional">
            <xsd:annotation>
                <xsd:documentation>Extrusion Direction</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="skewangle" type="xsd:float" use="optional">
            <xsd:annotation>
                <xsd:documentation>Extrusion Skew Angle</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="skewamt" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Extrusion Skew</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="foredepth" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Forward Extrusion</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="backdepth" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Backward Extrusion Depth</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="orientation" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Rotation Axis</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="orientationangle" type="xsd:float" use="optional">
            <xsd:annotation>
                <xsd:documentation>Rotation Around Axis</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="lockrotationcenter" type="ST_TrueFalse" use="optional">
            <xsd:annotation>
                <xsd:documentation>Rotation Toggle</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="autorotationcenter" type="ST_TrueFalse" use="optional">
            <xsd:annotation>
                <xsd:documentation>Center of Rotation Toggle</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="rotationcenter" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Rotation Center</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="rotationangle" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>X-Y Rotation Angle</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="colormode" type="ST_ColorMode" use="optional">
            <xsd:annotation>
                <xsd:documentation>Extrusion Color Mode</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="color" type="ST_ColorType" use="optional">
            <xsd:annotation>
                <xsd:documentation>Extrusion Color</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="shininess" type="xsd:float" use="optional">
            <xsd:annotation>
                <xsd:documentation>Shininess</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="specularity" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Specularity</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="diffusity" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Diffuse Reflection</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="metal" type="ST_TrueFalse" use="optional">
            <xsd:annotation>
                <xsd:documentation>Metallic Surface Toggle</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="edge" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Simulated Bevel</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="facet" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Faceting Quality</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="lightface" type="ST_TrueFalse" use="optional">
            <xsd:annotation>
                <xsd:documentation>Shape Face Lighting Toggle</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="brightness" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Brightness</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="lightposition" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Primary Light Position</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="lightlevel" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Primary Light Intensity</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="lightharsh" type="ST_TrueFalse" use="optional">
            <xsd:annotation>
                <xsd:documentation>Primary Light Harshness Toggle</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="lightposition2" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Secondary Light Position</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="lightlevel2" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Secondary Light Intensity</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="lightharsh2" type="ST_TrueFalse" use="optional">
            <xsd:annotation>
                <xsd:documentation>Secondary Light Harshness Toggle</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
    </xsd:complexType>
    """

    @property
    def on(self) -> ST_TrueFalse | None:
        """Extrusion Toggle

        <xsd:attribute name="on" type="ST_TrueFalse" use="optional">
            <xsd:annotation>
                <xsd:documentation>Extrusion Toggle</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:on"))

        if val is not None:
            return ST_TrueFalse(val)

    @property
    def type(self) -> ST_ExtrusionType | None:
        """Extrusion Type

        <xsd:attribute name="type" type="ST_ExtrusionType" default="parallel" use="optional">
            <xsd:annotation>
                <xsd:documentation>Extrusion Type</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:type"))

        if val is not None:
            return ST_ExtrusionType(val)

        return ST_ExtrusionType("parallel")

    @property
    def render(self) -> ST_ExtrusionRender | None:
        """Extrusion Render Mode

        <xsd:attribute name="render" type="ST_ExtrusionRender" default="solid" use="optional">
            <xsd:annotation>
                <xsd:documentation>Extrusion Render Mode</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:render"))

        if val is not None:
            return ST_ExtrusionRender(val)

    @property
    def viewpointorigin(self) -> str | None:
        """Extrusion Viewpoint Origin

        <xsd:attribute name="viewpointorigin" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Extrusion Viewpoint Origin</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:viewpointorigin"))

        if val is not None:
            return str(val)

    @property
    def viewpoint(self) -> str | None:
        """Extrusion Viewpoint

        <xsd:attribute name="viewpoint" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Extrusion Viewpoint</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:viewpoint"))

        if val is not None:
            return str(val)

    @property
    def plane(self) -> ST_ExtrusionPlane | None:
        """Extrusion Direction

        <xsd:attribute name="plane" type="ST_ExtrusionPlane" default="XY" use="optional">
            <xsd:annotation>
                <xsd:documentation>Extrusion Direction</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:plane"))

        if val is not None:
            return ST_ExtrusionPlane(val)

    @property
    def skewangle(self) -> float | None:
        """Extrusion Skew Angle

        <xsd:attribute name="skewangle" type="xsd:float" use="optional">
            <xsd:annotation>
                <xsd:documentation>Extrusion Skew Angle</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:skewangle"))

        if val is not None:
            return float(val)

    @property
    def skewamt(self) -> str | None:
        """Extrusion Skew

        <xsd:attribute name="skewamt" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Extrusion Skew</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:skewamt"))

        if val is not None:
            return str(val)

    @property
    def foredepth(self) -> str | None:
        """Forward Extrusion

        <xsd:attribute name="foredepth" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Forward Extrusion</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:foredepth"))

        if val is not None:
            return str(val)

    @property
    def backdepth(self) -> str | None:
        """Backward Extrusion Depth

        <xsd:attribute name="backdepth" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Backward Extrusion Depth</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:backdepth"))

        if val is not None:
            return str(val)

    @property
    def orientation(self) -> str | None:
        """Rotation Axis

        <xsd:attribute name="orientation" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Rotation Axis</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:orientation"))

        if val is not None:
            return str(val)

    @property
    def orientationangle(self) -> float | None:
        """Rotation Around Axis

        <xsd:attribute name="orientationangle" type="xsd:float" use="optional">
            <xsd:annotation>
                <xsd:documentation>Rotation Around Axis</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:orientationangle"))

        if val is not None:
            return float(val)

    @property
    def lockrotationcenter(self) -> ST_TrueFalse | None:
        """Rotation Toggle

        <xsd:attribute name="lockrotationcenter" type="ST_TrueFalse" use="optional">
            <xsd:annotation>
                <xsd:documentation>Rotation Toggle</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:lockrotationcenter"))

        if val is not None:
            return ST_TrueFalse(val)

    @property
    def autorotationcenter(self) -> ST_TrueFalse | None:
        """Center of Rotation Toggle

        <xsd:attribute name="autorotationcenter" type="ST_TrueFalse" use="optional">
            <xsd:annotation>
                <xsd:documentation>Center of Rotation Toggle</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:autorotationcenter"))

        if val is not None:
            return ST_TrueFalse(val)

    @property
    def rotationcenter(self) -> str | None:
        """Rotation Center

        <xsd:attribute name="rotationcenter" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Rotation Center</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:rotationcenter"))

        if val is not None:
            return str(val)

    @property
    def rotationangle(self) -> str | None:
        """X-Y Rotation Angle

        <xsd:attribute name="rotationangle" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>X-Y Rotation Angle</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:rotationangle"))

        if val is not None:
            return str(val)

    @property
    def colormode(self) -> ST_ColorMode | None:
        """Extrusion Color Mode

        <xsd:attribute name="colormode" type="ST_ColorMode" use="optional">
            <xsd:annotation>
                <xsd:documentation>Extrusion Color Mode</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:colormode"))

        if val is not None:
            return ST_ColorMode(val)

    @property
    def color(self) -> ST_ColorType | None:
        """Extrusion Color

        <xsd:attribute name="color" type="ST_ColorType" use="optional">
            <xsd:annotation>
                <xsd:documentation>Extrusion Color</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:color"))

        if val is not None:
            return ST_ColorType(val)

    @property
    def shininess(self) -> float | None:
        """Shininess

        <xsd:attribute name="shininess" type="xsd:float" use="optional">
            <xsd:annotation>
                <xsd:documentation>Shininess</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:shininess"))

        if val is not None:
            return float(val)

    @property
    def specularity(self) -> str | None:
        """Specularity

        <xsd:attribute name="specularity" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Specularity</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:specularity"))

        if val is not None:
            return str(val)

    @property
    def diffusity(self) -> str | None:
        """Diffuse Reflection

        <xsd:attribute name="diffusity" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Diffuse Reflection</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:diffusity"))

        if val is not None:
            return str(val)

    @property
    def metal(self) -> ST_TrueFalse | None:
        """Metallic Surface Toggle

        <xsd:attribute name="metal" type="ST_TrueFalse" use="optional">
            <xsd:annotation>
                <xsd:documentation>Metallic Surface Toggle</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:metal"))

        if val is not None:
            return ST_TrueFalse(val)

    @property
    def edge(self) -> str | None:
        """Simulated Bevel

        <xsd:attribute name="edge" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Simulated Bevel</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:edge"))

        if val is not None:
            return str(val)

    @property
    def facet(self) -> str | None:
        """Faceting Quality

        <xsd:attribute name="facet" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Faceting Quality</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:facet"))

        if val is not None:
            return str(val)

    @property
    def lightface(self) -> ST_TrueFalse | None:
        """Shape Face Lighting Toggle

        <xsd:attribute name="lightface" type="ST_TrueFalse" use="optional">
            <xsd:annotation>
                <xsd:documentation>Shape Face Lighting Toggle</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:lightface"))

        if val is not None:
            return ST_TrueFalse(val)

    @property
    def brightness(self) -> str | None:
        """Brightness

        <xsd:attribute name="brightness" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Brightness</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:brightness"))

        if val is not None:
            return str(val)

    @property
    def lightposition(self) -> str | None:
        """Primary Light Position

        <xsd:attribute name="lightposition" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Primary Light Position</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:lightposition"))

        if val is not None:
            return str(val)

    @property
    def lightlevel(self) -> str | None:
        """Primary Light Intensity

        <xsd:attribute name="lightlevel" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Primary Light Intensity</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:lightlevel"))

        if val is not None:
            return str(val)

    @property
    def lightharsh(self) -> ST_TrueFalse | None:
        """Primary Light Harshness Toggle

        <xsd:attribute name="lightharsh" type="ST_TrueFalse" use="optional">
            <xsd:annotation>
                <xsd:documentation>Primary Light Harshness Toggle</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:lightharsh"))

        if val is not None:
            return ST_TrueFalse(val)

    @property
    def lightposition2(self) -> str | None:
        """Secondary Light Position

        <xsd:attribute name="lightposition2" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Secondary Light Position</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:lightposition2"))

        if val is not None:
            return str(val)

    @property
    def lightlevel2(self) -> str | None:
        """Secondary Light Intensity

        <xsd:attribute name="lightlevel2" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Secondary Light Intensity</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:lightlevel2"))

        if val is not None:
            return str(val)

    @property
    def lightharsh2(self) -> ST_TrueFalse | None:
        """Secondary Light Harshness Toggle

        <xsd:attribute name="lightharsh2" type="ST_TrueFalse" use="optional">
            <xsd:annotation>
                <xsd:documentation>Secondary Light Harshness Toggle</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:lightharsh2"))

        if val is not None:
            return ST_TrueFalse(val)


class CT_Callout(v_AG_Ext):
    """
    <xsd:complexType name="CT_Callout">
        <xsd:attributeGroup ref="v:AG_Ext" />
        <xsd:attribute name="on" type="ST_TrueFalse" use="optional">
            <xsd:annotation>
                <xsd:documentation>Callout toggle</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="type" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Callout type</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="gap" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Callout gap</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="angle" type="ST_Angle" use="optional">
            <xsd:annotation>
                <xsd:documentation>Callout angle</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="dropauto" type="ST_TrueFalse" use="optional">
            <xsd:annotation>
                <xsd:documentation>Callout automatic drop toggle</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="drop" type="ST_CalloutDrop" use="optional">
            <xsd:annotation>
                <xsd:documentation>Callout drop position</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="distance" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Callout drop distance</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="lengthspecified" type="ST_TrueFalse" default="f" use="optional">
            <xsd:annotation>
                <xsd:documentation>Callout length toggle</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="length" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Callout length</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="accentbar" type="ST_TrueFalse" use="optional">
            <xsd:annotation>
                <xsd:documentation>Callout accent bar toggle</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="textborder" type="ST_TrueFalse" use="optional">
            <xsd:annotation>
                <xsd:documentation>Callout text border toggle</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="minusx" type="ST_TrueFalse" use="optional">
            <xsd:annotation>
                <xsd:documentation>Callout flip x</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="minusy" type="ST_TrueFalse" use="optional">
            <xsd:annotation>
                <xsd:documentation>Callout flip y</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
    </xsd:complexType>
    """

    def on(self) -> ST_TrueFalse | None:
        """Callout toggle

        <xsd:attribute name="on" type="ST_TrueFalse" use="optional">
            <xsd:annotation>
                <xsd:documentation>Callout toggle</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:on"))
        if val is not None:
            return ST_TrueFalse(val)

    def type(self) -> str | None:
        """Callout type

        <xsd:attribute name="type" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Callout type</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:type"))
        if val is not None:
            return str(val)

    def gap(self) -> str | None:
        """Callout gap

        <xsd:attribute name="gap" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Callout gap</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:gap"))
        if val is not None:
            return str(val)

    def angle(self) -> ST_Angle | None:
        """Callout angle

        <xsd:attribute name="angle" type="ST_Angle" use="optional">
            <xsd:annotation>
                <xsd:documentation>Callout angle</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:angle"))
        if val is not None:
            return ST_Angle(val)

    def dropauto(self) -> ST_TrueFalse | None:
        """Callout automatic drop toggle

        <xsd:attribute name="dropauto" type="ST_TrueFalse" use="optional">
            <xsd:annotation>
                <xsd:documentation>Callout automatic drop toggle</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:dropauto"))
        if val is not None:
            return ST_TrueFalse(val)

    def drop(self) -> ST_CalloutDrop | None:
        """Callout drop position

        <xsd:attribute name="drop" type="ST_CalloutDrop" use="optional">
            <xsd:annotation>
                <xsd:documentation>Callout drop position</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:drop"))
        if val is not None:
            return ST_CalloutDrop(val)

    def distance(self) -> str | None:
        """Callout drop distance

        <xsd:attribute name="distance" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Callout drop distance</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:distance"))
        if val is not None:
            return str(val)

    def lengthspecified(self) -> ST_TrueFalse | None:
        """Callout length toggle

        <xsd:attribute name="lengthspecified" type="ST_TrueFalse" default="f" use="optional">
            <xsd:annotation>
                <xsd:documentation>Callout length toggle</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:lengthspecified"))
        if val is not None:
            return ST_TrueFalse(val)

        return ST_TrueFalse("f")

    def length(self) -> str | None:
        """Callout length

        <xsd:attribute name="length" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Callout length</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:length"))
        if val is not None:
            return str(val)

    def accentbar(self) -> ST_TrueFalse | None:
        """Callout accent bar toggle

        <xsd:attribute name="accentbar" type="ST_TrueFalse" use="optional">
            <xsd:annotation>
                <xsd:documentation>Callout accent bar toggle</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:accentbar"))
        if val is not None:
            return ST_TrueFalse(val)

    def textborder(self) -> ST_TrueFalse | None:
        """Callout text border toggle

        <xsd:attribute name="textborder" type="ST_TrueFalse" use="optional">
            <xsd:annotation>
                <xsd:documentation>Callout text border toggle</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:textborder"))
        if val is not None:
            return ST_TrueFalse(val)

    def minusx(self) -> ST_TrueFalse | None:
        """Callout flip x

        <xsd:attribute name="minusx" type="ST_TrueFalse" use="optional">
            <xsd:annotation>
                <xsd:documentation>Callout flip x</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:minusx"))
        if val is not None:
            return ST_TrueFalse(val)

    def minusy(self) -> ST_TrueFalse | None:
        """Callout flip y

        <xsd:attribute name="minusy" type="ST_TrueFalse" use="optional">
            <xsd:annotation>
                <xsd:documentation>Callout flip y</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:minusy"))
        if val is not None:
            return ST_TrueFalse(val)


class CT_Lock(v_AG_Ext):
    """
    <xsd:complexType name="CT_Lock">
        <xsd:attributeGroup ref="v:AG_Ext" />
        <xsd:attribute name="position" type="ST_TrueFalse" use="optional">
            <xsd:annotation>
                <xsd:documentation>Position Lock</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="selection" type="ST_TrueFalse" use="optional">
            <xsd:annotation>
                <xsd:documentation>Selection Lock</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="grouping" type="ST_TrueFalse" use="optional">
            <xsd:annotation>
                <xsd:documentation>Grouping Lock</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="ungrouping" type="ST_TrueFalse" use="optional">
            <xsd:annotation>
                <xsd:documentation>Ungrouping Lock</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="rotation" type="ST_TrueFalse" use="optional">
            <xsd:annotation>
                <xsd:documentation>Rotation Lock</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="cropping" type="ST_TrueFalse" use="optional">
            <xsd:annotation>
                <xsd:documentation>Cropping Lock</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="verticies" type="ST_TrueFalse" use="optional">
            <xsd:annotation>
                <xsd:documentation>Vertices Lock</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="adjusthandles" type="ST_TrueFalse" use="optional">
            <xsd:annotation>
                <xsd:documentation>Handles Lock</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="text" type="ST_TrueFalse" use="optional">
            <xsd:annotation>
                <xsd:documentation>Text Lock</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="aspectratio" type="ST_TrueFalse" use="optional">
            <xsd:annotation>
                <xsd:documentation>Aspect Ratio Lock</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="shapetype" type="ST_TrueFalse" use="optional">
            <xsd:annotation>
                <xsd:documentation>AutoShape Type Lock</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
    </xsd:complexType>
    """

    def position(self) -> ST_TrueFalse | None:
        """Position Lock

        <xsd:attribute name="position" type="ST_TrueFalse" use="optional">
            <xsd:annotation>
                <xsd:documentation>Position Lock</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:position"))

        if val is not None:
            return ST_TrueFalse(val)

    def selection(self) -> ST_TrueFalse | None:
        """Selection Lock

        <xsd:attribute name="selection" type="ST_TrueFalse" use="optional">
            <xsd:annotation>
                <xsd:documentation>Selection Lock</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:selection"))

        if val is not None:
            return ST_TrueFalse(val)

    def grouping(self) -> ST_TrueFalse | None:
        """Grouping Lock

        <xsd:attribute name="grouping" type="ST_TrueFalse" use="optional">
            <xsd:annotation>
                <xsd:documentation>Grouping Lock</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:grouping"))

        if val is not None:
            return ST_TrueFalse(val)

    def ungrouping(self) -> ST_TrueFalse | None:
        """Ungrouping Lock

        <xsd:attribute name="ungrouping" type="ST_TrueFalse" use="optional">
            <xsd:annotation>
                <xsd:documentation>Ungrouping Lock</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:ungrouping"))

        if val is not None:
            return ST_TrueFalse(val)

    def rotation(self) -> ST_TrueFalse | None:
        """Rotation Lock

        <xsd:attribute name="rotation" type="ST_TrueFalse" use="optional">
            <xsd:annotation>
                <xsd:documentation>Rotation Lock</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:rotation"))

        if val is not None:
            return ST_TrueFalse(val)

    def cropping(self) -> ST_TrueFalse | None:
        """Cropping Lock

        <xsd:attribute name="cropping" type="ST_TrueFalse" use="optional">
            <xsd:annotation>
                <xsd:documentation>Cropping Lock</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:cropping"))

        if val is not None:
            return ST_TrueFalse(val)

    def verticies(self) -> ST_TrueFalse | None:
        """Vertices Lock

        <xsd:attribute name="verticies" type="ST_TrueFalse" use="optional">
            <xsd:annotation>
                <xsd:documentation>Vertices Lock</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:verticies"))

        if val is not None:
            return ST_TrueFalse(val)

    def adjusthandles(self) -> ST_TrueFalse | None:
        """Handles Lock

        <xsd:attribute name="adjusthandles" type="ST_TrueFalse" use="optional">
            <xsd:annotation>
                <xsd:documentation>Handles Lock</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:adjusthandles"))

        if val is not None:
            return ST_TrueFalse(val)

    def text(self) -> ST_TrueFalse | None:
        """Text Lock

        <xsd:attribute name="text" type="ST_TrueFalse" use="optional">
            <xsd:annotation>
                <xsd:documentation>Text Lock</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:text"))

        if val is not None:
            return ST_TrueFalse(val)

    def aspectratio(self) -> ST_TrueFalse | None:
        """Aspect Ratio Lock

        <xsd:attribute name="aspectratio" type="ST_TrueFalse" use="optional">
            <xsd:annotation>
                <xsd:documentation>Aspect Ratio Lock</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:aspectratio"))

        if val is not None:
            return ST_TrueFalse(val)

    def shapetype(self) -> ST_TrueFalse | None:
        """AutoShape Type Lock

        <xsd:attribute name="shapetype" type="ST_TrueFalse" use="optional">
            <xsd:annotation>
                <xsd:documentation>AutoShape Type Lock</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:shapetype"))

        if val is not None:
            return ST_TrueFalse(val)


class CT_OLEObject(OxmlBaseElement):
    """
    <xsd:complexType name="CT_OLEObject">
        <xsd:sequence>
            <xsd:element name="LinkType" type="ST_OLELinkType" minOccurs="0">
                <xsd:annotation>
                    <xsd:documentation>Embedded Object Alternate Image Request</xsd:documentation>
                </xsd:annotation>
            </xsd:element>
            <xsd:element name="LockedField" type="ST_TrueFalseBlank" minOccurs="0">
                <xsd:annotation>
                    <xsd:documentation>Embedded Object Cannot Be Refreshed</xsd:documentation>
                </xsd:annotation>
            </xsd:element>
            <xsd:element name="FieldCodes" type="xsd:string" minOccurs="0">
                <xsd:annotation>
                    <xsd:documentation>WordprocessingML Field Switches</xsd:documentation>
                </xsd:annotation>
            </xsd:element>
        </xsd:sequence>
        <xsd:attribute name="Type" type="ST_OLEType" use="optional">
            <xsd:annotation>
                <xsd:documentation>OLE Object Type</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="ProgID" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>OLE Object Application</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="ShapeID" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>OLE Object Shape</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="DrawAspect" type="ST_OLEDrawAspect" use="optional">
            <xsd:annotation>
                <xsd:documentation>OLE Object Representation</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="ObjectID" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>OLE Object Unique ID</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute ref="r:id" use="optional">
            <xsd:annotation>
                <xsd:documentation>Relationship</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="UpdateMode" type="ST_OLEUpdateMode" use="optional">
            <xsd:annotation>
                <xsd:documentation>OLE Update Mode</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
    </xsd:complexType>
    """

    @property
    def LinkType(self) -> ST_OLELinkType | None:
        """
        <xsd:element name="LinkType" type="ST_OLELinkType" minOccurs="0">
            <xsd:annotation>
                <xsd:documentation>Embedded Object Alternate Image Request</xsd:documentation>
            </xsd:annotation>
        </xsd:element>
        """

        ele: OxmlBaseElement | None = getattr(self, qn("o:LinkType"))

        if ele is not None:
            return ST_OLELinkType(ele.text)

    @property
    def LockedField(self) -> ST_TrueFalseBlank | None:
        """
        <xsd:element name="LockedField" type="ST_TrueFalseBlank" minOccurs="0">
            <xsd:annotation>
                <xsd:documentation>Embedded Object Cannot Be Refreshed</xsd:documentation>
            </xsd:annotation>
        </xsd:element>
        """

        ele: OxmlBaseElement | None = getattr(self, qn("o:LockedField"))

        if ele is not None:
            return ST_TrueFalseBlank(ele.text)

    @property
    def FieldCodes(self) -> str | None:
        """
        <xsd:element name="FieldCodes" type="xsd:string" minOccurs="0">
            <xsd:annotation>
                <xsd:documentation>WordprocessingML Field Switches</xsd:documentation>
            </xsd:annotation>
        </xsd:element>
        """

        ele: OxmlBaseElement | None = getattr(self, qn("o:FieldCodes"))

        if ele is not None:
            return ele.text

    @property
    def Type(self) -> ST_OLEType | None:
        """
        <xsd:attribute name="Type" type="ST_OLEType" use="optional">
            <xsd:annotation>
                <xsd:documentation>OLE Object Type</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:Type"))
        if val is not None:
            return ST_OLEType(val)

    @property
    def ProgID(self) -> str | None:
        """
        <xsd:attribute name="ProgID" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>OLE Object Application</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:ProgID"))
        if val is not None:
            return str(val)

    @property
    def ShapeID(self) -> str | None:
        """
        <xsd:attribute name="ShapeID" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>OLE Object Shape</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:ShapeID"))
        if val is not None:
            return str(val)

    @property
    def DrawAspect(self) -> ST_OLEDrawAspect | None:
        """
        <xsd:attribute name="DrawAspect" type="ST_OLEDrawAspect" use="optional">
            <xsd:annotation>
                <xsd:documentation>OLE Object Representation</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:DrawAspect"))
        if val is not None:
            return ST_OLEDrawAspect(val)

    @property
    def ObjectID(self) -> str | None:
        """
        <xsd:attribute name="ObjectID" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>OLE Object Unique ID</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:ObjectID"))
        if val is not None:
            return str(val)

    @property
    def r_id(self) -> str | None:
        """
        <xsd:attribute ref="r:id" use="optional">
            <xsd:annotation>
                <xsd:documentation>Relationship</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:r"))
        if val is not None:
            return str(val)

    @property
    def UpdateMode(self) -> ST_OLEUpdateMode | None:
        """
        <xsd:attribute name="UpdateMode" type="ST_OLEUpdateMode" use="optional">
            <xsd:annotation>
                <xsd:documentation>OLE Update Mode</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:UpdateMode"))
        if val is not None:
            return ST_OLEUpdateMode(val)


class CT_Complex(v_AG_Ext):
    """
    <xsd:complexType name="CT_Complex">
        <xsd:attributeGroup ref="v:AG_Ext" />
    </xsd:complexType>
    """

    ...


class CT_StrokeChild(v_AG_Ext):
    """

    <xsd:complexType name="CT_StrokeChild">
        <xsd:attributeGroup ref="v:AG_Ext" />
        <xsd:attribute name="on" type="ST_TrueFalse" use="optional">
            <xsd:annotation>
                <xsd:documentation>Stroke Toggle</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="weight" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Stroke Weight</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="color" type="ST_ColorType" use="optional">
            <xsd:annotation>
                <xsd:documentation>Stroke Color</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="color2" type="ST_ColorType" use="optional">
            <xsd:annotation>
                <xsd:documentation>Stroke Alternate Pattern Color</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="opacity" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Stroke Opacity</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="linestyle" type="v:ST_StrokeLineStyle" use="optional">
            <xsd:annotation>
                <xsd:documentation>Stroke Line Style</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="miterlimit" type="xsd:decimal" use="optional">
            <xsd:annotation>
                <xsd:documentation>Miter Joint Limit</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="joinstyle" type="v:ST_StrokeJoinStyle" use="optional">
            <xsd:annotation>
                <xsd:documentation>Line End Join Style)</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="endcap" type="v:ST_StrokeEndCap" use="optional">
            <xsd:annotation>
                <xsd:documentation>Line End Cap</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="dashstyle" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Stroke Dash Pattern</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="insetpen" type="ST_TrueFalse" use="optional">
            <xsd:annotation>
                <xsd:documentation>Inset Border From Path</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="filltype" type="v:ST_FillType" use="optional">
            <xsd:annotation>
                <xsd:documentation>Stroke Image Style</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="src" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Stroke Image Location</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="imageaspect" type="v:ST_ImageAspect" use="optional">
            <xsd:annotation>
                <xsd:documentation>Stroke Image Aspect Ratio</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="imagesize" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Stroke Image Size</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="imagealignshape" type="ST_TrueFalse" use="optional">
            <xsd:annotation>
                <xsd:documentation>Stoke Image Alignment</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="startarrow" type="v:ST_StrokeArrowType" use="optional">
            <xsd:annotation>
                <xsd:documentation>Line Start Arrowhead</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="startarrowwidth" type="v:ST_StrokeArrowWidth" use="optional">
            <xsd:annotation>
                <xsd:documentation>Line Start Arrowhead Width</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="startarrowlength" type="v:ST_StrokeArrowLength" use="optional">
            <xsd:annotation>
                <xsd:documentation>Line Start Arrowhead Length</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="endarrow" type="v:ST_StrokeArrowType" use="optional">
            <xsd:annotation>
                <xsd:documentation>Line End Arrowhead</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="endarrowwidth" type="v:ST_StrokeArrowWidth" use="optional">
            <xsd:annotation>
                <xsd:documentation>Line End Arrowhead Width</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute name="endarrowlength" type="v:ST_StrokeArrowLength" use="optional">
            <xsd:annotation>
                <xsd:documentation>Line End Arrowhead Length</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute ref="href">
            <xsd:annotation>
                <xsd:documentation>Original Image Reference</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute ref="althref">
            <xsd:annotation>
                <xsd:documentation>Alternate Image Reference</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute ref="title">
            <xsd:annotation>
                <xsd:documentation>Stroke Title</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        <xsd:attribute ref="forcedash">
            <xsd:annotation>
                <xsd:documentation>Force Dashed Outline</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
    </xsd:complexType>
    """

    @property
    def on(self) -> ST_TrueFalse | None:
        """Stroke Toggle

        <xsd:attribute name="on" type="ST_TrueFalse" use="optional">
            <xsd:annotation>
                <xsd:documentation>Stroke Toggle</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """
        val = self.attrib.get(qn("o:on"))

        if val is not None:
            return ST_TrueFalse(val)

    @property
    def weight(self) -> str | None:
        """Stroke Weight

        <xsd:attribute name="weight" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Stroke Weight</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """
        val = self.attrib.get(qn("o:weight"))

        if val is not None:
            return str(val)

    @property
    def color(self) -> ST_ColorType | None:
        """Stroke Color

        <xsd:attribute name="color" type="ST_ColorType" use="optional">
            <xsd:annotation>
                <xsd:documentation>Stroke Color</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """
        val = self.attrib.get(qn("o:color"))

        if val is not None:
            return ST_ColorType(val)

    @property
    def color2(self) -> ST_ColorType | None:
        """Stroke Alternate Pattern Color

        <xsd:attribute name="color2" type="ST_ColorType" use="optional">
            <xsd:annotation>
                <xsd:documentation>Stroke Alternate Pattern Color</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """
        val = self.attrib.get(qn("o:color2"))

        if val is not None:
            return ST_ColorType(val)

    @property
    def opacity(self) -> str | None:
        """Stroke Opacity

        <xsd:attribute name="opacity" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Stroke Opacity</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """
        val = self.attrib.get(qn("o:opacity"))

        if val is not None:
            return str(val)

    @property
    def linestyle(self):
        """Stroke Line Style

        <xsd:attribute name="linestyle" type="v:ST_StrokeLineStyle" use="optional">
            <xsd:annotation>
                <xsd:documentation>Stroke Line Style</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """
        from .main import ST_StrokeLineStyle

        val = self.attrib.get(qn("o:linestyle"))

        if val is not None:
            return ST_StrokeLineStyle(val)

    @property
    def miterlimit(self) -> float | None:
        """Miter Joint Limit

        <xsd:attribute name="miterlimit" type="xsd:decimal" use="optional">
            <xsd:annotation>
                <xsd:documentation>Miter Joint Limit</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """
        val = self.attrib.get(qn("o:miterlimit"))

        if val is not None:
            return float(val)

    @property
    def joinstyle(self):
        """Line End Join Style)

        <xsd:attribute name="joinstyle" type="v:ST_StrokeJoinStyle" use="optional">
            <xsd:annotation>
                <xsd:documentation>Line End Join Style)</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """
        from .main import ST_StrokeJoinStyle

        val = self.attrib.get(qn("o:joinstyle"))

        if val is not None:
            return ST_StrokeJoinStyle(val)

    @property
    def endcap(self):
        """Line End Cap

        <xsd:attribute name="endcap" type="v:ST_StrokeEndCap" use="optional">
            <xsd:annotation>
                <xsd:documentation>Line End Cap</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """
        from .main import ST_StrokeEndCap

        val = self.attrib.get(qn("o:endcap"))

        if val is not None:
            return ST_StrokeEndCap(val)

    @property
    def dashstyle(self) -> str | None:
        """Stroke Dash Pattern

        <xsd:attribute name="dashstyle" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Stroke Dash Pattern</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """
        val = self.attrib.get(qn("o:dashstyle"))

        if val is not None:
            return str(val)

    @property
    def insetpen(self) -> ST_TrueFalse | None:
        """Inset Border From Path

        <xsd:attribute name="insetpen" type="ST_TrueFalse" use="optional">
            <xsd:annotation>
                <xsd:documentation>Inset Border From Path</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """
        val = self.attrib.get(qn("o:insetpen"))

        if val is not None:
            return ST_TrueFalse(val)

    @property
    def filltype(self):
        """Stroke Image Style

        <xsd:attribute name="filltype" type="v:ST_FillType" use="optional">
            <xsd:annotation>
                <xsd:documentation>Stroke Image Style</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        from .main import ST_FillType

        val = self.attrib.get(qn("o:filltype"))

        if val is not None:
            return ST_FillType(val)

    @property
    def src(self) -> str | None:
        """Stroke Image Location

        <xsd:attribute name="src" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Stroke Image Location</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """
        val = self.attrib.get(qn("o:src"))

        if val is not None:
            return str(val)

    @property
    def imageaspect(self):
        """Stroke Image Aspect Ratio

        <xsd:attribute name="imageaspect" type="v:ST_ImageAspect" use="optional">
            <xsd:annotation>
                <xsd:documentation>Stroke Image Aspect Ratio</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """
        from .main import ST_ImageAspect

        val = self.attrib.get(qn("o:imageaspect"))

        if val is not None:
            return ST_ImageAspect(val)

    @property
    def imagesize(self) -> str | None:
        """Stroke Image Size

        <xsd:attribute name="imagesize" type="xsd:string" use="optional">
            <xsd:annotation>
                <xsd:documentation>Stroke Image Size</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """
        val = self.attrib.get(qn("o:imagesize"))

        if val is not None:
            return str(val)

    @property
    def imagealignshape(self) -> ST_TrueFalse | None:
        """Stoke Image Alignment

        <xsd:attribute name="imagealignshape" type="ST_TrueFalse" use="optional">
            <xsd:annotation>
                <xsd:documentation>Stoke Image Alignment</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """
        val = self.attrib.get(qn("o:imagealignshape"))

        if val is not None:
            return ST_TrueFalse(val)

    @property
    def startarrow(self):
        """Line Start Arrowhead

        <xsd:attribute name="startarrow" type="v:ST_StrokeArrowType" use="optional">
            <xsd:annotation>
                <xsd:documentation>Line Start Arrowhead</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """
        from .main import ST_StrokeArrowType

        val = self.attrib.get(qn("o:startarrow"))

        if val is not None:
            return ST_StrokeArrowType(val)

    @property
    def startarrowwidth(self):
        """Line Start Arrowhead Width

        <xsd:attribute name="startarrowwidth" type="v:ST_StrokeArrowWidth" use="optional">
            <xsd:annotation>
                <xsd:documentation>Line Start Arrowhead Width</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """
        from .main import ST_StrokeArrowWidth

        val = self.attrib.get(qn("o:startarrowwidth"))

        if val is not None:
            return ST_StrokeArrowWidth(val)

    @property
    def startarrowlength(self):
        """Line Start Arrowhead Length

        <xsd:attribute name="startarrowlength" type="v:ST_StrokeArrowLength" use="optional">
            <xsd:annotation>
                <xsd:documentation>Line Start Arrowhead Length</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """
        from .main import ST_StrokeArrowLength

        val = self.attrib.get(qn("o:startarrowlength"))

        if val is not None:
            return ST_StrokeArrowLength(val)

    @property
    def endarrow(self):
        """Line End Arrowhead

        <xsd:attribute name="endarrow" type="v:ST_StrokeArrowType" use="optional">
            <xsd:annotation>
                <xsd:documentation>Line End Arrowhead</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """
        from .main import ST_StrokeArrowType

        val = self.attrib.get(qn("o:endarrow"))

        if val is not None:
            return ST_StrokeArrowType(val)

    @property
    def endarrowwidth(self):
        """Line End Arrowhead Width

        <xsd:attribute name="endarrowwidth" type="v:ST_StrokeArrowWidth" use="optional">
            <xsd:annotation>
                <xsd:documentation>Line End Arrowhead Width</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """
        from .main import ST_StrokeArrowWidth

        val = self.attrib.get(qn("o:endarrowwidth"))

        if val is not None:
            return ST_StrokeArrowWidth(val)

    @property
    def endarrowlength(self):
        """Line End Arrowhead Length

        <xsd:attribute name="endarrowlength" type="v:ST_StrokeArrowLength" use="optional">
            <xsd:annotation>
                <xsd:documentation>Line End Arrowhead Length</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """
        from .main import ST_StrokeArrowLength

        val = self.attrib.get(qn("o:endarrowlength"))

        if val is not None:
            return ST_StrokeArrowLength(val)

    @property
    def href(self):
        """Original Image Reference

        <xsd:attribute ref="href">
            <xsd:annotation>
                <xsd:documentation>Original Image Reference</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """
        val = self.attrib.get(qn("o:href"))

        if val is not None:
            return str(val)

    @property
    def althref(self):
        """Alternate Image Reference

        <xsd:attribute ref="althref">
            <xsd:annotation>
                <xsd:documentation>Alternate Image Reference</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>

        """
        val = self.attrib.get(qn("o:althref"))

        if val is not None:
            return str(val)

    @property
    def title(self):
        """Stroke Title
        <xsd:attribute ref="title">
            <xsd:annotation>
                <xsd:documentation>Stroke Title</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>

        """
        val = self.attrib.get(qn("o:title"))

        if val is not None:
            return str(val)

    @property
    def forcedash(self):
        """Force Dashed Outline

        <xsd:attribute ref="forcedash">
            <xsd:annotation>
                <xsd:documentation>Force Dashed Outline</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """
        val = self.attrib.get(qn("o:forcedash"))

        if val is not None:
            return str(val)


class CT_ClipPath(OxmlBaseElement):
    """
    <xsd:complexType name="CT_ClipPath">
        <xsd:attribute name="v" type="xsd:string" use="required" form="qualified">
            <xsd:annotation>
                <xsd:documentation>Path Definition</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
    </xsd:complexType>
    """

    def v(self) -> str | None:
        """Path Definition

        <xsd:attribute name="v" type="xsd:string" use="required" form="qualified">
            <xsd:annotation>
                <xsd:documentation>Path Definition</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:v"))

        if val is not None:
            return str(val)


class CT_Fill(v_AG_Ext):
    """
    <xsd:complexType name="CT_Fill">
        <xsd:attributeGroup ref="v:AG_Ext" />
        <xsd:attribute name="type" type="ST_FillType">
            <xsd:annotation>
                <xsd:documentation>Fill Type</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
    </xsd:complexType>
    """

    def type(self) -> ST_FillType | None:
        """Fill Type

        <xsd:attribute name="type" type="ST_FillType">
            <xsd:annotation>
                <xsd:documentation>Fill Type</xsd:documentation>
            </xsd:annotation>
        </xsd:attribute>
        """

        val = self.attrib.get(qn("o:type"))

        if val is not None:
            return ST_FillType(val)


class ST_RType(ST_BaseEnumType):
    """Rule Type

    <xsd:simpleType name="ST_RType">
        <xsd:annotation>
            <xsd:documentation>Rule Type</xsd:documentation>
        </xsd:annotation>
        <xsd:restriction base="xsd:string">
            <xsd:enumeration value="arc">
                <xsd:annotation>
                    <xsd:documentation>Arc Rule</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="callout">
                <xsd:annotation>
                    <xsd:documentation>Callout Rule</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="connector">
                <xsd:annotation>
                    <xsd:documentation>Connector Rule</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="align">
                <xsd:annotation>
                    <xsd:documentation>Alignment Rule</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
        </xsd:restriction>
    </xsd:simpleType>
    """

    arc = "arc"
    """
    Arc Rule
    """

    callout = "callout"
    """
    Callout Rule
    """

    connector = "connector"
    """
    Connector Rule
    """

    align = "align"
    """
    Alignment Rule
    """


class ST_How(ST_BaseEnumType):
    """Alignment Type

    <xsd:simpleType name="ST_How">
        <xsd:annotation>
            <xsd:documentation>Alignment Type</xsd:documentation>
        </xsd:annotation>
        <xsd:restriction base="xsd:string">
            <xsd:enumeration value="top">
                <xsd:annotation>
                    <xsd:documentation>Top Alignment</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="middle">
                <xsd:annotation>
                    <xsd:documentation>Middle Alignment</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="bottom">
                <xsd:annotation>
                    <xsd:documentation>Bottom Alignment</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="left">
                <xsd:annotation>
                    <xsd:documentation>Left Alignment</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="center">
                <xsd:annotation>
                    <xsd:documentation>Center Alignment</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="right">
                <xsd:annotation>
                    <xsd:documentation>Right Alignment</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
        </xsd:restriction>
    </xsd:simpleType>
    """

    top = "top"
    """
    Top Alignment
    """

    middle = "middle"
    """
    Middle Alignment
    """

    bottom = "bottom"
    """
    Bottom Alignment
    """

    left = "left"
    """
    Left Alignment
    """

    center = "center"
    """
    Center Alignment
    """

    right = "right"
    """
    Right Alignment
    """


class ST_BWMode(ST_BaseEnumType):
    """Black And White Modes

    <xsd:simpleType name="ST_BWMode">
        <xsd:annotation>
            <xsd:documentation>Black And White Modes</xsd:documentation>
        </xsd:annotation>
        <xsd:restriction base="xsd:string">
            <xsd:enumeration value="color">
                <xsd:annotation>
                    <xsd:documentation>Color</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="auto">
                <xsd:annotation>
                    <xsd:documentation>Automatic</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="grayScale">
                <xsd:annotation>
                    <xsd:documentation>Grayscale</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="lightGrayscale">
                <xsd:annotation>
                    <xsd:documentation>Light grayscale</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="inverseGray">
                <xsd:annotation>
                    <xsd:documentation>Inverse Grayscale</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="grayOutline">
                <xsd:annotation>
                    <xsd:documentation>Gray Outlines</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="highContrast">
                <xsd:annotation>
                    <xsd:documentation>Black And White</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="black">
                <xsd:annotation>
                    <xsd:documentation>Black</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="white">
                <xsd:annotation>
                    <xsd:documentation>White</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="hide">
                <xsd:annotation>
                    <xsd:documentation>Hide Object When Displayed in Black and White</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="undrawn">
                <xsd:annotation>
                    <xsd:documentation>Do Not Show</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="blackTextAndLines">
                <xsd:annotation>
                    <xsd:documentation>Black Text And Lines</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
        </xsd:restriction>
    </xsd:simpleType>
    """

    color = "color"
    """
    Color
    """

    auto = "auto"
    """
    Automatic
    """

    grayScale = "grayScale"
    """
    Grayscale
    """

    lightGrayscale = "lightGrayscale"
    """
    Light grayscale
    """

    inverseGray = "inverseGray"
    """
    Inverse Grayscale
    """

    grayOutline = "grayOutline"
    """
    Gray Outlines
    """

    highContrast = "highContrast"
    """
    Black And White
    """

    black = "black"
    """
    Black
    """

    white = "white"
    """
    White
    """

    hide = "hide"
    """
    Hide Object When Displayed in Black and White
    """

    undrawn = "undrawn"
    """
    Do Not Show
    """

    blackTextAndLines = "blackTextAndLines"
    """
    Black Text And Lines
    """


class ST_ScreenSize(ST_BaseEnumType):
    """Screen Sizes Type
    <xsd:simpleType name="ST_ScreenSize">
        <xsd:annotation>
            <xsd:documentation>Screen Sizes Type</xsd:documentation>
        </xsd:annotation>
        <xsd:restriction base="xsd:string">
            <xsd:enumeration value="544,376">
                <xsd:annotation>
                    <xsd:documentation>544x376 pixels</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="640,480">
                <xsd:annotation>
                    <xsd:documentation>640x480 pixels</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="720,512">
                <xsd:annotation>
                    <xsd:documentation>720x512 pixels</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="800,600">
                <xsd:annotation>
                    <xsd:documentation>800x600 pixels</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="1024,768">
                <xsd:annotation>
                    <xsd:documentation>1024x768 pixels</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="1152,862">
                <xsd:annotation>
                    <xsd:documentation>1152x862 pixels</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
        </xsd:restriction>
    </xsd:simpleType>
    """

    size1 = "544,376"
    """
    544x376 pixels
    """

    size2 = "640,480"
    """
    640x480 pixels
    """

    size3 = "720,512"
    """
    720x512 pixels
    """

    size4 = "800,600"
    """
    800x600 pixels
    """

    size5 = "1024,768"
    """
    1024x768 pixels
    """

    size6 = "1152,862"
    """
    1152x862 pixels
    """


class ST_InsetMode(ST_BaseEnumType):
    """
    <xsd:simpleType name="ST_InsetMode">
        <xsd:annotation>
            <xsd:documentation>Inset Margin Type</xsd:documentation>
        </xsd:annotation>
        <xsd:restriction base="xsd:string">
            <xsd:enumeration value="auto">
                <xsd:annotation>
                    <xsd:documentation>Automatic Margins</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="custom">
                <xsd:annotation>
                    <xsd:documentation>Custom Margins</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
        </xsd:restriction>
    </xsd:simpleType>
    """

    auto = "auto"
    """
    Automatic Margins
    """

    custom = "custom"
    """
    Custom Margins
    """


class ST_ColorMode(ST_BaseEnumType):
    """
    <xsd:simpleType name="ST_ColorMode">
        <xsd:annotation>
            <xsd:documentation>Extrusion Color Types</xsd:documentation>
        </xsd:annotation>
        <xsd:restriction base="xsd:string">
            <xsd:enumeration value="auto">
                <xsd:annotation>
                    <xsd:documentation>Use Shape Fill Color</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="custom">
                <xsd:annotation>
                    <xsd:documentation>Use Custom Color</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
        </xsd:restriction>
    </xsd:simpleType>
    """

    auto = "auto"
    """Use Shape Fill Color"""

    custom = "custom"
    """Use Custom Color"""


class ST_ColorType(str):
    """Color Type

    <xsd:simpleType name="ST_ColorType">
        <xsd:annotation>
            <xsd:documentation>Color Type</xsd:documentation>
        </xsd:annotation>
        <xsd:restriction base="xsd:string" />
    </xsd:simpleType>
    """

    ...


class ST_ExtrusionType(ST_BaseEnumType):
    """Extrusion Type

    <xsd:simpleType name="ST_ExtrusionType">
        <xsd:annotation>
            <xsd:documentation>Extrusion Type</xsd:documentation>
        </xsd:annotation>
        <xsd:restriction base="xsd:string">
            <xsd:enumeration value="perspective">
                <xsd:annotation>
                    <xsd:documentation>Perspective Projection</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="parallel">
                <xsd:annotation>
                    <xsd:documentation>Parallel Projection</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
        </xsd:restriction>
    </xsd:simpleType>
    """

    perspective = "perspective"
    """Perspective Projection
    """

    parallel = "parallel"
    """Parallel Projection
    """


class ST_ExtrusionRender(ST_BaseEnumType):
    """Extrusion Rendering Types

    <xsd:simpleType name="ST_ExtrusionRender">
        <xsd:annotation>
            <xsd:documentation>Extrusion Rendering Types</xsd:documentation>
        </xsd:annotation>
        <xsd:restriction base="xsd:string">
            <xsd:enumeration value="solid">
                <xsd:annotation>
                    <xsd:documentation>Solid</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="wireFrame">
                <xsd:annotation>
                    <xsd:documentation>Wireframe</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="boundingCube">
                <xsd:annotation>
                    <xsd:documentation>Bounding Cube</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
        </xsd:restriction>
    </xsd:simpleType>
    """

    solid = "solid"
    """
    Solid
    """

    wireFrame = "wireFrame"
    """
    Wireframe
    """

    boundingCube = "boundingCube"
    """
    Bounding Cube
    """


class ST_ExtrusionPlane(ST_BaseEnumType):
    """
    <xsd:simpleType name="ST_ExtrusionPlane">
        <xsd:annotation>
            <xsd:documentation>Extrusion Planes</xsd:documentation>
        </xsd:annotation>
        <xsd:restriction base="xsd:string">
            <xsd:enumeration value="XY">
                <xsd:annotation>
                    <xsd:documentation>XY Plane</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="ZX">
                <xsd:annotation>
                    <xsd:documentation>ZX Plane</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="YZ">
                <xsd:annotation>
                    <xsd:documentation>YZ Plane</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
        </xsd:restriction>
    </xsd:simpleType>
    """

    XY = "XY"
    """
    XY Plane
    """

    ZX = "ZX"
    """
    ZX Plane
    """

    YZ = "YZ"
    """
    YZ Plane
    """


class ST_Angle(ST_BaseEnumType):
    """Callout Angles
    <xsd:simpleType name="ST_Angle">
        <xsd:annotation>
            <xsd:documentation>Callout Angles</xsd:documentation>
        </xsd:annotation>
        <xsd:restriction base="xsd:string">
            <xsd:enumeration value="any">
                <xsd:annotation>
                    <xsd:documentation>Any Angle</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="30">
                <xsd:annotation>
                    <xsd:documentation>30 degrees</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="45">
                <xsd:annotation>
                    <xsd:documentation>45 degrees</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="60">
                <xsd:annotation>
                    <xsd:documentation>60 degrees</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="90">
                <xsd:annotation>
                    <xsd:documentation>90 degrees</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="auto">
                <xsd:annotation>
                    <xsd:documentation>Automatic Angle</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
        </xsd:restriction>
    </xsd:simpleType>
    """

    any = "any"
    """
    Any Angle
    """

    angle30 = "30"
    """
    30 degrees
    """

    angle45 = "45"
    """
    45 degrees
    """

    angle60 = "60"
    """
    60 degrees
    """

    angle90 = "90"
    """
    90 degrees
    """

    auto = "auto"
    """
    Automatic Angle
    """


class ST_CalloutDrop(str):
    """Callout Drop Location

    <xsd:simpleType name="ST_CalloutDrop">
        <xsd:annotation>
            <xsd:documentation>Callout Drop Location</xsd:documentation>
        </xsd:annotation>
        <xsd:restriction base="xsd:string" />
    </xsd:simpleType>
    """


class ST_CalloutPlacement(ST_BaseEnumType):
    """Callout Placement

    <xsd:simpleType name="ST_CalloutPlacement">
        <xsd:annotation>
            <xsd:documentation>Callout Placement</xsd:documentation>
        </xsd:annotation>
        <xsd:restriction base="xsd:string">
            <xsd:enumeration value="top">
                <xsd:annotation>
                    <xsd:documentation>Top placement</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="center">
                <xsd:annotation>
                    <xsd:documentation>Center placement</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="bottom">
                <xsd:annotation>
                    <xsd:documentation>Bottom placement</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="user">
                <xsd:annotation>
                    <xsd:documentation>User-defined placement</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
        </xsd:restriction>
    </xsd:simpleType>
    """

    top = "top"
    """
    Top placement
    """

    center = "center"
    """
    Center placement
    """

    bottom = "bottom"
    """
    Bottom placement
    """

    user = "user"
    """
    User-defined placement
    """


class ST_ConnectorType(ST_BaseEnumType):
    """Connector Type

    <xsd:simpleType name="ST_ConnectorType">
        <xsd:annotation>
            <xsd:documentation>Connector Type</xsd:documentation>
        </xsd:annotation>
        <xsd:restriction base="xsd:string">
            <xsd:enumeration value="none">
                <xsd:annotation>
                    <xsd:documentation>No Connector</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="straight">
                <xsd:annotation>
                    <xsd:documentation>Straight Connector</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="elbow">
                <xsd:annotation>
                    <xsd:documentation>Elbow Connector</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="curved">
                <xsd:annotation>
                    <xsd:documentation>Curved Connector</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
        </xsd:restriction>
    </xsd:simpleType>
    """

    none = "none"
    """
    No Connector
    """

    straight = "straight"
    """
    Straight Connector
    """

    elbow = "elbow"
    """
    Elbow Connector
    """

    curved = "curved"
    """
    Curved Connector
    """


class ST_HrAlign(ST_BaseEnumType):
    """Alignment Type

    <xsd:simpleType name="ST_HrAlign">
        <xsd:annotation>
            <xsd:documentation>Alignment Type</xsd:documentation>
        </xsd:annotation>
        <xsd:restriction base="xsd:string">
            <xsd:enumeration value="left">
                <xsd:annotation>
                    <xsd:documentation>Left Alignment</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="right">
                <xsd:annotation>
                    <xsd:documentation>Right Alignment</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="center">
                <xsd:annotation>
                    <xsd:documentation>Center Alignment</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
        </xsd:restriction>
    </xsd:simpleType>
    """

    left = "left"
    """
    Left Alignment
    """

    right = "right"
    """
    Right Alignment
    """

    center = "center"
    """
    Center Alignment
    """


class ST_ConnectType(ST_BaseEnumType):
    """Connection Locations Type

    <xsd:simpleType name="ST_ConnectType">
        <xsd:annotation>
            <xsd:documentation>Connection Locations Type</xsd:documentation>
        </xsd:annotation>
        <xsd:restriction base="xsd:string">
            <xsd:enumeration value="none">
                <xsd:annotation>
                    <xsd:documentation>No</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="rect">
                <xsd:annotation>
                    <xsd:documentation>Four Connections</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="segments">
                <xsd:annotation>
                    <xsd:documentation>Edit Point Connections</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="custom">
                <xsd:annotation>
                    <xsd:documentation>Custom Connections</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
        </xsd:restriction>
    </xsd:simpleType>
    """

    none = "none"
    """
    No
    """

    rect = "rect"
    """
    Four Connections
    """

    segments = "segments"
    """
    Edit Point Connections
    """

    custom = "custom"
    """
    Custom Connections
    """


class ST_OLELinkType(ST_BaseEnumType):
    """Embedded Object Alternate Image Request Types

    <xsd:simpleType name="ST_OLELinkType">
        <xsd:annotation>
            <xsd:documentation>Embedded Object Alternate Image Request Types</xsd:documentation>
        </xsd:annotation>
        <xsd:restriction base="xsd:string">
            <xsd:enumeration value="Picture">
                <xsd:annotation>
                    <xsd:documentation>Other Image</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="Bitmap">
                <xsd:annotation>
                    <xsd:documentation>Bitmap Image</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="EnhancedMetaFile">
                <xsd:annotation>
                    <xsd:documentation>Enhanced Metafile Image</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
        </xsd:restriction>
    </xsd:simpleType>
    """

    Picture = "Picture"
    """Other Image"""

    Bitmap = "Bitmap"
    """Bitmap Image"""

    EnhancedMetaFile = "EnhancedMetaFile"
    """Enhanced Metafile Image"""


class ST_OLEType(ST_BaseEnumType):
    """OLE Connection Type

    <xsd:simpleType name="ST_OLEType">
        <xsd:annotation>
            <xsd:documentation>OLE Connection Type</xsd:documentation>
        </xsd:annotation>
        <xsd:restriction base="xsd:string">
            <xsd:enumeration value="Embed">
                <xsd:annotation>
                    <xsd:documentation>Embedded Object</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="Link">
                <xsd:annotation>
                    <xsd:documentation>Linked Object</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
        </xsd:restriction>
    </xsd:simpleType>
    """

    Embed = "Embed"
    """Embedded Object"""

    Link = "Link"
    """Linked Object"""


class ST_OLEDrawAspect(ST_BaseEnumType):
    """OLE Object Representations

    <xsd:simpleType name="ST_OLEDrawAspect">
        <xsd:annotation>
            <xsd:documentation>OLE Object Representations</xsd:documentation>
        </xsd:annotation>
        <xsd:restriction base="xsd:string">
            <xsd:enumeration value="Content">
                <xsd:annotation>
                    <xsd:documentation>Snapshot</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="Icon">
                <xsd:annotation>
                    <xsd:documentation>Icon</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
        </xsd:restriction>
    </xsd:simpleType>
    """

    Content = "Content"
    """Snapshot"""

    Icon = "Icon"
    """Icon"""


class ST_OLEUpdateMode(ST_BaseEnumType):
    """OLE Update Method Type

    <xsd:simpleType name="ST_OLEUpdateMode">
        <xsd:annotation>
            <xsd:documentation>OLE Update Method Type</xsd:documentation>
        </xsd:annotation>
        <xsd:restriction base="xsd:string">
            <xsd:enumeration value="Always">
                <xsd:annotation>
                    <xsd:documentation>Server Application Update</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="OnCall">
                <xsd:annotation>
                    <xsd:documentation>User Update</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
        </xsd:restriction>
    </xsd:simpleType>
    """

    Always = "Always"
    """Server Application Update"""

    OnCall = "OnCall"
    """User Update"""


class ST_Guid(str):
    r"""128-Bit GUID

    <xsd:simpleType name="ST_Guid">
        <xsd:annotation>
            <xsd:documentation>128-Bit GUID</xsd:documentation>
        </xsd:annotation>
        <xsd:restriction base="xsd:token">
            <xsd:pattern value="\{[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}\}" />
        </xsd:restriction>
    </xsd:simpleType>
    """

    ...


class ST_RelationshipId(str):
    """Explicit Relationship ID

    <xsd:simpleType name="ST_RelationshipId">
        <xsd:annotation>
            <xsd:documentation>Explicit Relationship ID</xsd:documentation>
        </xsd:annotation>
        <xsd:restriction base="xsd:string" />
    </xsd:simpleType>
    """


class ST_TrueFalse(ST_BaseEnumType):
    """Boolean Value

    <xsd:simpleType name="ST_TrueFalse">
        <xsd:annotation>
            <xsd:documentation>Boolean Value</xsd:documentation>
        </xsd:annotation>
        <xsd:restriction base="xsd:string">
            <xsd:enumeration value="t">
                <xsd:annotation>
                    <xsd:documentation>True</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="f">
                <xsd:annotation>
                    <xsd:documentation>False</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="true">
                <xsd:annotation>
                    <xsd:documentation>True</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="false">
                <xsd:annotation>
                    <xsd:documentation>False</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
        </xsd:restriction>
    </xsd:simpleType>
    """

    t = "t"
    """True"""

    f = "f"
    """False"""

    true = "true"
    """True"""

    false = "false"
    """False"""


class ST_TrueFalseBlank(ST_BaseEnumType):
    """Boolean Value with Blank [False] State

    <xsd:simpleType name="ST_TrueFalseBlank">
        <xsd:annotation>
            <xsd:documentation>Boolean Value with Blank [False] State</xsd:documentation>
        </xsd:annotation>
        <xsd:restriction base="xsd:string">
            <xsd:enumeration value="">
                <xsd:annotation>
                    <xsd:documentation>Blank – Logical False</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="t">
                <xsd:annotation>
                    <xsd:documentation>Logical True</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="f">
                <xsd:annotation>
                    <xsd:documentation>Logical False</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="true">
                <xsd:annotation>
                    <xsd:documentation>Logical True</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="false">
                <xsd:annotation>
                    <xsd:documentation>Logical False</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
        </xsd:restriction>
    </xsd:simpleType>
    """

    blank = ""
    """Blank – Logical False"""

    t = "t"
    """Logical True"""

    f = "f"
    """Logical False"""

    true = "true"
    """Logical True"""

    false = "false"
    """Logical False"""


class ST_FillType(ST_BaseEnumType):
    """Shape Fill Type

    <xsd:simpleType name="ST_FillType">
        <xsd:annotation>
            <xsd:documentation>Shape Fill Type</xsd:documentation>
        </xsd:annotation>
        <xsd:restriction base="xsd:string">
            <xsd:enumeration value="gradientCenter">
                <xsd:annotation>
                    <xsd:documentation>Centered Radial Gradient</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="solid">
                <xsd:annotation>
                    <xsd:documentation>Solid Fill</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="pattern">
                <xsd:annotation>
                    <xsd:documentation>Image Pattern</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="tile">
                <xsd:annotation>
                    <xsd:documentation>Tiled Image</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="frame">
                <xsd:annotation>
                    <xsd:documentation>Stretch Image to Fit</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="gradientUnscaled">
                <xsd:annotation>
                    <xsd:documentation>Unscaled Gradient</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="gradientRadial">
                <xsd:annotation>
                    <xsd:documentation>Radial Gradient</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="gradient">
                <xsd:annotation>
                    <xsd:documentation>Linear Gradient</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
            <xsd:enumeration value="background">
                <xsd:annotation>
                    <xsd:documentation>Use Background Fill</xsd:documentation>
                </xsd:annotation>
            </xsd:enumeration>
        </xsd:restriction>
    </xsd:simpleType>
    """

    gradientCenter = "gradientCenter"
    """Centered Radial Gradient"""

    solid = "solid"
    """Solid Fill"""

    pattern = "pattern"
    """Image Pattern"""

    tile = "tile"
    """Tiled Image"""

    frame = "frame"
    """Stretch Image to Fit"""

    gradientUnscaled = "gradientUnscaled"
    """Unscaled Gradient"""

    gradientRadial = "gradientRadial"
    """Radial Gradient"""

    gradient = "gradient"
    """Linear Gradient"""

    background = "background"
    """Use Background Fill"""


vml_drawing_namespace = lookup.get_namespace(namespace_o)
vml_drawing_namespace[None] = CT_Empty
vml_drawing_namespace["shapedefaults"] = CT_ShapeDefaults  # New Shape Defaults
vml_drawing_namespace["shapelayout"] = CT_ShapeLayout  # Shape Layout Properties
vml_drawing_namespace["signatureline"] = CT_SignatureLine  # Digital Signature Line
vml_drawing_namespace["ink"] = CT_Ink  # Ink
vml_drawing_namespace["diagram"] = CT_Diagram  # VML Diagram
vml_drawing_namespace["colormru"] = CT_ColorMru
vml_drawing_namespace["colormenu"] = CT_ColorMenu

vml_drawing_namespace["idmap"] = CT_IdMap
vml_drawing_namespace["regrouptable"] = CT_RegroupTable
vml_drawing_namespace["rules"] = CT_Rules

vml_drawing_namespace["entry"] = CT_Entry

vml_drawing_namespace["r"] = CT_R
vml_drawing_namespace["proxy"] = CT_Proxy

vml_drawing_namespace["relationtable"] = CT_RelationTable
vml_drawing_namespace["rel"] = CT_Relation

vml_drawing_namespace["skew"] = CT_Skew  # Skew Transform
vml_drawing_namespace["extrusion"] = CT_Extrusion  # 3D Extrusion
vml_drawing_namespace["callout"] = CT_Callout
vml_drawing_namespace["lock"] = CT_Lock
vml_drawing_namespace["OLEObject"] = CT_OLEObject  # Embedded OLE Object
# 特殊类型
vml_drawing_namespace["LinkType"] = (
    OxmlBaseElement  # ST_OLELinkType , Embedded Object Alternate Image Request
)
vml_drawing_namespace["LockedField"] = (
    OxmlBaseElement  # ST_TrueFalseBlank , Embedded Object Cannot Be Refreshed
)
vml_drawing_namespace["FieldCodes"] = (
    OxmlBaseElement  # xsd:string , WordprocessingML Field Switches
)

vml_drawing_namespace["complex"] = CT_Complex  # Complex
vml_drawing_namespace["left"] = CT_StrokeChild  # Text Box Left Stroke
vml_drawing_namespace["top"] = CT_StrokeChild  # Text Box Top Stroke
vml_drawing_namespace["right"] = CT_StrokeChild  # Text Box Right Stroke
vml_drawing_namespace["bottom"] = CT_StrokeChild  # Text Box Bottom Stroke
vml_drawing_namespace["column"] = CT_StrokeChild  # Text Box Interior Stroke
vml_drawing_namespace["clippath"] = CT_ClipPath  # Shape Clipping Path
vml_drawing_namespace["fill"] = CT_Fill  # Shape Fill Extended Properties

# 注册 命名空间中的 类映射
import logging

logger = logging.getLogger(__name__)

# opc  # opc包封装必要xml定义
# dml  # 文档基础xml定义，绘制，颜色，等等
from .dml import (
    dml_diagram_namespace,  # noqa: F401
    dml_main_namespace,  # noqa: F401
)
from .opc import (  # noqa: F401
    content_type_namespace,
    core_properties_namespace,
    relationship_namespace,
)

# pml  # *.pptx 文件
from .pml import pml_core_namespace  # noqa: F401

# shared  # opc包共享的xml定义
from .shared import (  # noqa: F401
    shared_additional_character_namespace,
    shared_bibliography_namespace,
    shared_common_st_namespace,
    shared_cust_data_pr_namespace,
    shared_custom_schema_pr_namespace,
    shared_doc_custom_pr_namespace,
    shared_doc_pr_extended_namespace,
    shared_doc_pr_variant_namespace,
    shared_math_namespace,
)

# ecma-376 第一版的vml模块的xml定义
from .vml import vml_drawing_namespace, vml_main_namespace  # noqa: F401

# wml  # *.word 文件, 暂不支持
from .wml import wml_main_namespace  # noqa: F401

# sml  # *.xlsx 文件, 暂不支持

logger.info("oxml 初始化xml对象模型成功!!!")

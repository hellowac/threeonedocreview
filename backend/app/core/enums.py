from enum import StrEnum


# ------- ocr 相关 ------------
class OcrApiType(StrEnum):
    """ocr 接口类型"""

    PPOCR = 'ppocr'  # 本地部署的cpu版本的ocr
    BAIDU = 'baidu'  # ai平台的百度智能体的接口


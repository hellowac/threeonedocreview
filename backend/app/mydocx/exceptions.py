""" 解析异常模块 """


class ParseException(Exception):
    """解析异常"""

    ...


class ChartDrawingException(Exception):
    """图表绘制异常， 捕获后采用截图方式"""

    ...


class ReviewException(Exception):
    """审阅状态异常

    当docx文件处于审阅状态时，解析异常
    """

    ...

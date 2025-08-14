
import os
import shutil
import subprocess
from io import BytesIO
from pathlib import Path

from loguru import logger
from PIL import Image as PIL_Image

from ms_office.shared.image import Image


class ImageTool:
    """图片工具"""

    @classmethod
    def convert_tif_image_by_pil(cls, image: Image):
        """将tif格式的图片转换为PNG格式"""
        converted_img = BytesIO()

        tiff_image = PIL_Image.open(BytesIO(image.blob))

        # 如果图像是 CMYK 模式，则转换为 RGB 模式
        if tiff_image.mode == "CMYK":
            tiff_image = tiff_image.convert("RGB")

        tiff_image.save(converted_img, "PNG")

        converted_img.seek(0)
        return converted_img.getvalue()

    @classmethod
    def convert_emf_image_by_soffice(cls, image: Image):
        """将单个emf文件转为png

        命令:

        soffice --headless --convert-to png <pdf_file>

        如果报错，需在服务器安装这些包

        sudo apt-get install default-jre libreoffice-java-common

        apt install libreoffice-common inkscape default-jre libreoffice-java-common

        注意:

        这里对emf的兼容性最好， 但是解析出来是1页.
        """

        blob = image.blob
        filename = image.filename

        emf_file = str(Path(filename).resolve())  # 以wmf结尾

        # xxx.pdf => xxx.png
        png_file = f"{emf_file[0:-4]}.png"

        if os.path.exists(png_file):
            return png_file

        with open(emf_file, "wb") as fw:
            fw.write(blob)  # type: ignore

        # cmd = cls.inkscape_command_line(png_file, emf_file)
        cmd = f"soffice --headless --convert-to png {emf_file}"
        logger.info(f"转换 emf文件: {cmd}")

        if cmd is None:
            return None

        logger.info(cmd)

        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        process.wait()

        # returncode 不为 0 表示非正常退出
        if process.returncode and process.stdout:
            logger.warning(
                f"emf:【{emf_file}】{cmd} 转换emf文件失败: {process.stdout.read() !r}"
            )
            return None

        # 删除使用过的pdf文件
        if os.path.exists(emf_file):
            os.remove(emf_file)

        return png_file

    @classmethod
    def convert_emf_image_by_inkscape(cls, image: Image):
        """转换emf文件

        inkscape emf -> png
        """

        blob = image.blob
        filename = image.filename

        filename_prefix = str(Path(filename).resolve())

        emf_file = filename_prefix  # 以wmf结尾
        png_file = filename_prefix.replace(".emf", ".png")

        with open(emf_file, "wb") as fw:
            fw.write(blob)  # type: ignore

        cmd = cls.inkscape_command_line(png_file, emf_file)

        if cmd is None:
            return None

        logger.info(cmd)

        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        process.wait()

        logger.info(f"{process.returncode = } {process.stdout = }")

        # returncode 不为 0 表示非正常退出
        if process.returncode and process.stdout:
            logger.warning(
                f"【{image.filename}】{cmd} 转换wmf文件失败: {process.stdout.read() !r}"
            )
            return None

        with open(png_file, "rb") as fr:
            image_bytes = fr.read()

        try:
            # 删除缓存文件
            os.remove(emf_file)
            os.remove(png_file)
        except FileNotFoundError:
            pass

        return image_bytes

    @classmethod
    def convert_wmf_image(cls, image: Image):
        """转换wmf文件"""

        blob = image.blob
        filename = image.filename

        filename_prefix = str(Path(filename).resolve())

        wmf_file = filename_prefix
        png_file = filename_prefix.replace(".wmf", ".png")

        with open(wmf_file, "wb") as fw:
            fw.write(blob)  # type: ignore

        cmd = f"wmf2gd --maxpect -o {png_file} {wmf_file}"

        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        process.wait()

        # returncode 不为 0 表示非正常退出
        if process.returncode and process.stdout:
            logger.error(
                f"【{Image.filename}】{cmd} 转换wmf文件失败: {process.stdout.read() !r}"
            )
            return None

        with open(png_file, "rb") as fr:
            image_bytes = fr.read()

        try:
            # 删除缓存文件
            os.remove(wmf_file)
            os.remove(png_file)
        except FileNotFoundError:
            pass

        return image_bytes

    @classmethod
    def wmf2gd_exists(cls):
        """检查wmf2gd命令是否存在

        该命令需要 apt 安装 libwmf-bin 包
        """
        return shutil.which("wmf2gd") is not None

    @classmethod
    def inkscape_exists(cls):
        """
        inkscape 官网: https://inkscape.org/zh-hans/simplified-chinese-about/

        检查inkscape命令是否存在

        该命令需要 apt 安装 inkscape 包： `sudo apt install inkscape`

        对于 inkscape 版本为 0.91 r13725 的 软件

        转换命令为:

        inkspace --export-png=xxx.png source.emf

        对于 inkscape 版本为 1.1.2 (0a00cf5339, 2022-02-04) 的软件

        转换命令为:

        inkscape --export-filename=image42-1.svg  image42.emf
        """
        return shutil.which("inkscape") is not None

    @classmethod
    def inkscape_version(cls) -> tuple | None:
        """获取inkscape 版本

        版本发布(release)历史:

            - 参考: https://inkscape.org/zh-hans/release/
            - 命令行在线文档: http://tavmjong.free.fr/INKSCAPE/MANUAL/html/CommandLine.html

        inkscape --version

            Inkscape 1.1.2 (0a00cf5339, 2022-02-04)

            返回: (1,1,2)

            Inkscape 0.91 r13725

            返回: (0, 91)

        如果抛出异常

            返回: None
        """

        try:
            out = subprocess.check_output(["inkscape", "--version"]).decode()

            version = tuple(map(int, out.split(" ")[1].split(".")))

            logger.info(f"inkscape 版本: {version =}")

            return version

        except Exception:
            logger.exception("获取inkscape版本失败!")
            return None

    @classmethod
    def inkscape_command_line(cls, target: str, source: str):
        """根据inkscape版本构造不同的命令行

        - 0.91 -> inkscape --export-png=<target> <source>
        - 1.1.2 -> inkscape --export-filename=<target> <source>
        """

        version = cls.inkscape_version()

        # 测试服 inkscape 版本
        if version == (0, 91):
            return f"inkscape --export-png={target} {source}"

        # 本地开发服务器(wac) inkscape 版本
        # 预览服务器版本
        # pro3服务器版本
        # pro4服务器版本
        elif version == (1, 1, 2):
            return f"inkscape --export-filename={target} {source}"

        return None

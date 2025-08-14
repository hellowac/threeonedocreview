"""图片上传阿里云模块"""

from __future__ import annotations

import base64


class OssTool:
    """阿里云盘工具类"""

    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types
    content_type_map = {
        # 图片
        "tiff": "image/tiff",
        "png": "image/png",
        "svg": "image/svg+xml",
        "webp": "image/webp",
        "jpg": "image/jpg",
        "jpeg": "image/jpeg",
        "gif": "image/gif",
        # 音频
        "mp3": "audio/mp3",
        "mpeg": "audio/mpeg",
        # 视频
        "mp4": "video/mp4",
        "ogg": "video/ogg",
    }

    # 已上传阿里云图片的sha1合集
    uploaded_imags: dict[str, str] = {}

    @classmethod
    def upload_image(cls, sha1: str, image: bytes, file_suffix: str = "png"):
        """上传图片到阿里云"""

        my_oss = MyOss()

        aliyun_path = f"apps/eduai/media/ppt/{sha1}.{file_suffix}"
        my_oss.upload(aliyun_path, image)

        rpc_proxy = rpc_pool.get_connection()
        url: str = (
            rpc_proxy.yunpan_service.file_url_post({"param": {"oss_path": aliyun_path}})
            .get("data", {})
            .get("url")
        )
        rpc_pool.put_connection(rpc_proxy)

        return url

    @classmethod
    def upload_media(cls, sha1: str, vedio: bytes, ext: str):
        """上传视频到阿里云"""

        my_oss = MyOss()

        aliyun_path = f"apps/eduai/media/ppt/{sha1}.{ext}"
        my_oss.upload(aliyun_path, vedio)

        rpc_proxy = rpc_pool.get_connection()
        url: str = (
            rpc_proxy.yunpan_service.file_url_post({"param": {"oss_path": aliyun_path}})
            .get("data", {})
            .get("url")
        )
        rpc_pool.put_connection(rpc_proxy)

        return url

    @classmethod
    def short_url(cls, use_oss: bool, sha1: str, data: bytes, file_suffix: str = "png"):
        """获取图片或其他文件格式的短链接"""

        # 上传过到阿里云，直接使用缓存，降低网络请求，提升解析进度。
        if use_oss and sha1 in cls.uploaded_imags:
            short_url = cls.uploaded_imags[sha1]

        elif use_oss:
            short_url = OssTool.upload_image(sha1, data, file_suffix=file_suffix)
            cls.uploaded_imags[sha1] = short_url

        # 先用base64显示出来:
        else:
            content_type = cls.content_type_map[file_suffix]
            b64_str = base64.b64encode(data).decode()
            short_url = f"data:{content_type};base64,{b64_str}"

        return short_url

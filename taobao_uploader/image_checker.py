"""图片读取与检查模块。"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image

from . import config


@dataclass
class ImageCheckResult:
    """图片检查结果。"""

    path: Path
    ok: bool
    message: str


def find_images(product_folder: Path, prefix: str) -> list[Path]:
    """按文件名前缀查找图片，例如 主图1.jpg、详情页1.jpg。"""
    return sorted(
        path
        for path in product_folder.iterdir()
        if path.is_file()
        and path.stem.startswith(prefix)
        and path.suffix.lower() in config.SUPPORTED_IMAGE_FORMATS
    )


def check_image(path: Path) -> ImageCheckResult:
    """检查单张图片格式、大小和尺寸。"""
    if path.suffix.lower() not in config.SUPPORTED_IMAGE_FORMATS:
        return ImageCheckResult(path, False, "图片格式不支持")

    size_mb = path.stat().st_size / 1024 / 1024
    if size_mb > config.MAX_IMAGE_SIZE_MB:
        return ImageCheckResult(path, False, f"图片大小超过 {config.MAX_IMAGE_SIZE_MB}MB")

    try:
        with Image.open(path) as image:
            width, height = image.size
    except Exception as exc:  # Pillow 读取失败代表图片损坏，需要向用户报告。
        return ImageCheckResult(path, False, f"图片无法读取：{exc}")

    if width < config.MIN_IMAGE_WIDTH or height < config.MIN_IMAGE_HEIGHT:
        return ImageCheckResult(path, False, "图片尺寸不符合要求")
    return ImageCheckResult(path, True, "检查通过")


def check_product_images(product_folder: Path) -> tuple[list[Path], list[Path], list[ImageCheckResult]]:
    """检查商品主图和详情页图片。"""
    main_images = find_images(product_folder, config.MAIN_IMAGE_PREFIX)
    detail_images = find_images(product_folder, config.DETAIL_IMAGE_PREFIX)
    if not main_images:
        raise ValueError(f"{product_folder.name} 缺少主图")
    if not detail_images:
        raise ValueError(f"{product_folder.name} 缺少详情页图片")

    results = [check_image(path) for path in [*main_images, *detail_images]]
    failed = [result for result in results if not result.ok]
    if failed:
        messages = "；".join(f"{item.path.name}：{item.message}" for item in failed)
        raise ValueError(messages)
    return main_images, detail_images, results

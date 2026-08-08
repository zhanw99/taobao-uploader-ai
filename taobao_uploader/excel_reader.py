"""商品 Excel 资料读取模块。"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from . import config


@dataclass
class ProductInfo:
    """单个商品的结构化资料。"""

    folder: Path
    title: str
    category: str
    price: float
    stock: int
    color: str = ""
    size: str = ""
    sku: str = ""
    description: str = ""


def _safe_value(row: pd.Series, key: str, default: str = "") -> str:
    value = row.get(key, default)
    if pd.isna(value):
        return default
    return str(value).strip()


def read_product_excel(product_folder: Path) -> ProductInfo:
    """读取商品文件夹中的 商品资料.xlsx。"""
    excel_path = product_folder / config.EXCEL_FILE_NAME
    if not excel_path.exists():
        raise FileNotFoundError(f"缺少 Excel 文件：{excel_path}")

    df = pd.read_excel(excel_path)
    missing = [col for col in config.REQUIRED_EXCEL_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Excel 缺少必填字段：{', '.join(missing)}")
    if df.empty:
        raise ValueError(f"Excel 没有商品数据：{excel_path}")

    row = df.iloc[0]
    return ProductInfo(
        folder=product_folder,
        title=_safe_value(row, "商品标题"),
        category=_safe_value(row, "商品类目"),
        price=float(row["商品价格"]),
        stock=int(row["库存数量"]),
        color=_safe_value(row, "商品颜色"),
        size=_safe_value(row, "商品尺寸"),
        sku=_safe_value(row, "SKU信息"),
        description=_safe_value(row, "商品描述"),
    )


def scan_products(root_folder: Path) -> list[ProductInfo]:
    """扫描根目录下所有包含 商品资料.xlsx 的商品文件夹。"""
    products: list[ProductInfo] = []
    for folder in sorted(path for path in root_folder.iterdir() if path.is_dir()):
        if (folder / config.EXCEL_FILE_NAME).exists():
            products.append(read_product_excel(folder))
    if not products:
        raise ValueError("未找到任何商品文件夹，请确认每个商品目录内存在 商品资料.xlsx。")
    return products

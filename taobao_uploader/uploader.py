"""商品上传主流程。"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from threading import Event
from typing import Callable

import pandas as pd
from playwright.sync_api import Page

from . import config
from .browser import BrowserManager
from .excel_reader import ProductInfo, scan_products
from .image_checker import check_product_images


@dataclass
class UploadResult:
    """上传结果记录。"""

    title: str
    upload_time: str
    status: str
    error: str = ""


class TaobaoUploader:
    """淘宝商品批量上架执行器。"""

    def __init__(self, log_callback: Callable[[str], None], status_callback: Callable[[int, int, str, str], None]) -> None:
        self.log_callback = log_callback
        self.status_callback = status_callback
        self.pause_event = Event()
        self.pause_event.set()
        self.stop_requested = False
        self.results: list[UploadResult] = []

    def pause(self) -> None:
        """暂停任务。"""
        self.pause_event.clear()
        self.log_callback("任务已暂停。")

    def resume(self) -> None:
        """继续任务。"""
        self.pause_event.set()
        self.log_callback("任务已继续。")

    def stop(self) -> None:
        """请求停止任务。"""
        self.stop_requested = True
        self.pause_event.set()
        self.log_callback("收到停止请求，将在当前步骤后停止。")

    def run(self, root_folder: Path) -> None:
        """批量执行商品上传。"""
        products = scan_products(root_folder)
        total = len(products)
        self.log_callback(f"共发现 {total} 个商品，开始处理。")

        with BrowserManager(self.log_callback) as browser:
            browser.goto_with_retry(config.QIANNIU_HOME_URL)
            browser.wait_for_manual_login_if_needed()
            for index, product in enumerate(products, start=1):
                if self.stop_requested:
                    break
                self.pause_event.wait()
                try:
                    self.status_callback(index, total, product.title, "检查图片")
                    main_images, detail_images, _ = check_product_images(product.folder)
                    self._upload_one(browser, product, main_images, detail_images, index, total)
                    self._record(product.title, "成功")
                except Exception as exc:
                    self.log_callback(f"商品 {product.title} 上传失败：{exc}")
                    self._record(product.title, "失败", str(exc))
        self._save_results()

    def _upload_one(self, browser: BrowserManager, product: ProductInfo, main_images: list[Path], detail_images: list[Path], index: int, total: int) -> None:
        """上传单个商品并保存草稿。"""
        page = browser.page
        if page is None:
            raise RuntimeError("浏览器页面未初始化")

        self.status_callback(index, total, product.title, "打开发布商品页面")
        browser.goto_with_retry(config.PUBLISH_PRODUCT_URL)
        browser.pause_if_captcha()

        self.status_callback(index, total, product.title, "填写商品资料")
        self._fill_text(page, "title_input", product.title)
        self._fill_text(page, "category_input", product.category, required=False)
        self._fill_text(page, "price_input", str(product.price))
        self._fill_text(page, "stock_input", str(product.stock))
        self._fill_text(page, "description_input", product.description, required=False)

        self.status_callback(index, total, product.title, "上传主图")
        self._upload_files(page, "main_image_upload", main_images)
        self.status_callback(index, total, product.title, "上传详情页图片")
        self._upload_files(page, "detail_image_upload", detail_images, required=False)

        self.status_callback(index, total, product.title, "填写规格/SKU")
        self.log_callback(f"规格信息：颜色={product.color}，尺寸={product.size}，SKU={product.sku}")

        self.status_callback(index, total, product.title, "保存草稿")
        self._click(page, "save_draft_button")
        self.log_callback(f"商品 {product.title} 已保存草稿。")

    def _fill_text(self, page: Page, selector_key: str, value: str, required: bool = True) -> None:
        """按配置选择器填写文本。"""
        if not value and not required:
            return
        selector = config.SELECTORS[selector_key]
        locator = page.locator(selector).first
        if not locator.count() and required:
            raise RuntimeError(f"未找到输入框：{selector_key}")
        if locator.count():
            locator.fill(value)

    def _upload_files(self, page: Page, selector_key: str, files: list[Path], required: bool = True) -> None:
        """上传一个或多个文件。"""
        selector = config.SELECTORS[selector_key]
        locator = page.locator(selector).first
        if not locator.count() and required:
            raise RuntimeError(f"未找到上传控件：{selector_key}")
        if locator.count():
            locator.set_input_files([str(path) for path in files])

    def _click(self, page: Page, selector_key: str) -> None:
        """点击按钮。"""
        selector = config.SELECTORS[selector_key]
        page.locator(selector).first.click()

    def _record(self, title: str, status: str, error: str = "") -> None:
        self.results.append(UploadResult(title, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), status, error))
        self.log_callback(f"商品：{title}，状态：{status}，错误：{error or '无'}")

    def _save_results(self) -> None:
        """保存上传结果 Excel。"""
        config.LOG_DIR.mkdir(parents=True, exist_ok=True)
        df = pd.DataFrame([result.__dict__ for result in self.results])
        df.to_excel(config.RESULT_FILE, index=False)
        self.log_callback(f"结果已保存：{config.RESULT_FILE}")

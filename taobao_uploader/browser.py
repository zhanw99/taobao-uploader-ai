"""Playwright 浏览器自动化封装。"""
from __future__ import annotations

import time
from contextlib import AbstractContextManager
from typing import Callable

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError, sync_playwright

from . import config


class BrowserManager(AbstractContextManager["BrowserManager"]):
    """管理 Playwright 浏览器生命周期。"""

    def __init__(self, log_callback: Callable[[str], None] | None = None) -> None:
        self.log_callback = log_callback or (lambda message: None)
        self._playwright = None
        self.context = None
        self.page: Page | None = None

    def __enter__(self) -> "BrowserManager":
        self._playwright = sync_playwright().start()
        self.context = self._playwright.chromium.launch_persistent_context(
            user_data_dir=str(config.USER_DATA_DIR),
            headless=config.HEADLESS,
            slow_mo=config.SLOW_MO_MS,
        )
        self.context.set_default_timeout(config.DEFAULT_TIMEOUT_MS)
        self.page = self.context.pages[0] if self.context.pages else self.context.new_page()
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        if self.context:
            self.context.close()
        if self._playwright:
            self._playwright.stop()

    def goto_with_retry(self, url: str) -> None:
        """带重试打开页面，处理临时网络异常。"""
        assert self.page is not None
        last_error: Exception | None = None
        for index in range(1, config.RETRY_TIMES + 1):
            try:
                self.log_callback(f"打开页面：{url}（第 {index} 次）")
                self.page.goto(url, wait_until="domcontentloaded")
                return
            except Exception as exc:
                last_error = exc
                self.log_callback(f"页面打开失败，准备重试：{exc}")
                time.sleep(config.RETRY_INTERVAL_SECONDS)
        raise RuntimeError(f"页面打开失败：{url}，错误：{last_error}")

    def wait_for_manual_login_if_needed(self) -> None:
        """检测登录状态，未登录则等待用户人工登录。"""
        assert self.page is not None
        try:
            if self.page.locator(config.SELECTORS["login_marker"]).first.is_visible(timeout=3000):
                self.log_callback("检测到未登录，请在浏览器中完成淘宝账号登录。")
                self.page.wait_for_timeout(1000)
                self.page.wait_for_selector(config.SELECTORS["login_marker"], state="detached", timeout=10 * 60 * 1000)
                self.log_callback("登录完成，继续执行。")
        except PlaywrightTimeoutError:
            raise RuntimeError("等待登录超时，请重新运行程序。")
        except Exception:
            # 如果页面没有登录提示，则视为已登录或淘宝页面结构变化。
            self.log_callback("未检测到登录提示，继续执行。")

    def pause_if_captcha(self) -> None:
        """检测验证码，出现时暂停等待人工处理。"""
        assert self.page is not None
        try:
            if self.page.locator(config.SELECTORS["captcha_marker"]).first.is_visible(timeout=2000):
                self.log_callback("检测到验证码，请人工处理后程序会继续。")
                self.page.wait_for_selector(config.SELECTORS["captcha_marker"], state="detached", timeout=10 * 60 * 1000)
        except PlaywrightTimeoutError as exc:
            raise RuntimeError("验证码处理等待超时。") from exc
        except Exception:
            return

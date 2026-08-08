"""日志工具。"""
from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

from . import config


def setup_logger(name: str = "taobao_uploader") -> logging.Logger:
    """创建同时输出到文件与控制台的日志记录器。"""
    config.LOG_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    log_file = config.LOG_DIR / f"{datetime.now():%Y-%m-%d}.log"

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    return logger


def read_latest_log(max_chars: int = 8000) -> str:
    """读取最近日志内容，用于 GUI 展示。"""
    if not config.LOG_DIR.exists():
        return "暂无日志。"
    log_files = sorted(Path(config.LOG_DIR).glob("*.log"), reverse=True)
    if not log_files:
        return "暂无日志。"
    content = log_files[0].read_text(encoding="utf-8", errors="ignore")
    return content[-max_chars:] if len(content) > max_chars else content

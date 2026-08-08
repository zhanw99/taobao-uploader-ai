"""tkinter 桌面界面。"""
from __future__ import annotations

import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext

from . import config
from .logger import read_latest_log, setup_logger
from .uploader import TaobaoUploader


class App(tk.Tk):
    """淘宝商品批量上架助手主窗口。"""

    def __init__(self) -> None:
        super().__init__()
        self.title(config.APP_NAME)
        self.geometry("560x360")
        self.resizable(False, False)
        self.logger = setup_logger()
        self.selected_folder: Path | None = None
        self.uploader: TaobaoUploader | None = None
        self.worker: threading.Thread | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        tk.Label(self, text=config.APP_NAME, font=("Microsoft YaHei", 16, "bold")).pack(pady=14)

        folder_frame = tk.Frame(self)
        folder_frame.pack(fill="x", padx=24, pady=8)
        self.folder_var = tk.StringVar(value="尚未选择商品文件夹")
        tk.Label(folder_frame, textvariable=self.folder_var, anchor="w").pack(side="left", fill="x", expand=True)
        tk.Button(folder_frame, text="选择商品文件夹", command=self.choose_folder).pack(side="right")

        button_frame = tk.Frame(self)
        button_frame.pack(pady=16)
        tk.Button(button_frame, text="开始执行", width=14, command=self.start_task).grid(row=0, column=0, padx=8)
        self.pause_button = tk.Button(button_frame, text="暂停任务", width=14, command=self.toggle_pause)
        self.pause_button.grid(row=0, column=1, padx=8)
        tk.Button(button_frame, text="查看日志", width=14, command=self.show_logs).grid(row=0, column=2, padx=8)

        status_frame = tk.LabelFrame(self, text="执行状态", padx=12, pady=12)
        status_frame.pack(fill="x", padx=24, pady=12)
        self.current_product_var = tk.StringVar(value="当前商品：0/0")
        self.current_title_var = tk.StringVar(value="商品名称：-")
        self.current_status_var = tk.StringVar(value="当前状态：等待开始")
        tk.Label(status_frame, textvariable=self.current_product_var, anchor="w").pack(fill="x", pady=4)
        tk.Label(status_frame, textvariable=self.current_title_var, anchor="w").pack(fill="x", pady=4)
        tk.Label(status_frame, textvariable=self.current_status_var, anchor="w").pack(fill="x", pady=4)

        tk.Label(
            self,
            text="提示：首次运行会打开浏览器，请手动登录淘宝；验证码和风控需人工处理。",
            fg="#666666",
        ).pack(pady=10)

    def choose_folder(self) -> None:
        """选择商品根目录。"""
        folder = filedialog.askdirectory(title="请选择包含 商品001、商品002 的根目录")
        if folder:
            self.selected_folder = Path(folder)
            self.folder_var.set(str(self.selected_folder))

    def start_task(self) -> None:
        """启动后台上传线程，避免界面卡死。"""
        if not self.selected_folder:
            messagebox.showwarning("提示", "请先选择商品文件夹。")
            return
        if self.worker and self.worker.is_alive():
            messagebox.showinfo("提示", "任务正在执行中。")
            return

        self.uploader = TaobaoUploader(self.log_message, self.update_status)
        self.worker = threading.Thread(target=self._run_task, daemon=True)
        self.worker.start()

    def _run_task(self) -> None:
        try:
            assert self.uploader is not None and self.selected_folder is not None
            self.uploader.run(self.selected_folder)
            messagebox.showinfo("完成", "任务执行完成，请查看日志和结果文件。")
        except Exception as exc:
            self.log_message(f"任务异常：{exc}")
            messagebox.showerror("错误", str(exc))

    def toggle_pause(self) -> None:
        """暂停或继续任务。"""
        if not self.uploader:
            return
        if self.pause_button["text"] == "暂停任务":
            self.uploader.pause()
            self.pause_button.configure(text="继续任务")
            self.current_status_var.set("当前状态：已暂停")
        else:
            self.uploader.resume()
            self.pause_button.configure(text="暂停任务")

    def show_logs(self) -> None:
        """弹窗显示最新日志。"""
        window = tk.Toplevel(self)
        window.title("运行日志")
        window.geometry("760x520")
        text = scrolledtext.ScrolledText(window, wrap="word")
        text.pack(fill="both", expand=True)
        text.insert("1.0", read_latest_log())
        text.configure(state="disabled")

    def log_message(self, message: str) -> None:
        self.logger.info(message)

    def update_status(self, index: int, total: int, title: str, status: str) -> None:
        """线程安全更新界面状态。"""
        self.after(0, lambda: self.current_product_var.set(f"当前商品：{index}/{total}"))
        self.after(0, lambda: self.current_title_var.set(f"商品名称：{title}"))
        self.after(0, lambda: self.current_status_var.set(f"当前状态：{status}"))

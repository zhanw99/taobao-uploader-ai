# 淘宝商品批量上架助手 V1.0

一个面向淘宝卖家的 Windows 桌面端批量上架辅助工具。程序读取商品文件夹中的 Excel 和图片，通过 Playwright 打开淘宝千牛卖家后台，辅助填写商品资料、上传图片并保存草稿。

> 说明：淘宝后台页面会不定期改版，真实使用前需要根据页面实际元素调整 `taobao_uploader/config.py` 中的选择器。

## 项目架构

```text
taobao_uploader
├── __init__.py
├── main.py            # 程序入口
├── gui.py             # tkinter 桌面界面
├── browser.py         # Playwright 浏览器管理
├── excel_reader.py    # 商品 Excel 读取
├── image_checker.py   # 图片读取与检查
├── uploader.py        # 批量上传主流程
├── logger.py          # 日志系统
└── config.py          # 全局配置与淘宝页面选择器
```

## 商品目录格式

```text
商品资料根目录
├── 商品001
│   ├── 商品资料.xlsx
│   ├── 主图1.jpg
│   ├── 主图2.jpg
│   ├── 主图3.jpg
│   ├── 详情页1.jpg
│   └── 详情页2.jpg
└── 商品002
    └── ...
```

Excel 至少包含以下字段：

- 商品标题
- 商品类目
- 商品价格
- 库存数量

可选字段：

- 商品颜色
- 商品尺寸
- SKU信息
- 商品描述

## 安装说明

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

## 运行说明

```bash
python -m taobao_uploader.main
```

运行后：

1. 点击“选择商品文件夹”。
2. 选择包含 `商品001`、`商品002` 等子目录的根目录。
3. 点击“开始执行”。
4. 浏览器打开后，如未登录淘宝，请人工完成登录。
5. 如遇验证码或淘宝风控，请人工处理。
6. 程序会保存商品草稿，并在 `logs` 目录写入日志与结果文件。

## 打包 Windows EXE

```bash
pyinstaller --noconfirm --windowed --name 淘宝商品批量上架助手 --add-data "taobao_uploader;taobao_uploader" taobao_uploader/main.py
```

打包结果位于 `dist/淘宝商品批量上架助手/`。

## 日志与结果

- 日志目录：`logs/`
- 每日日志：`logs/YYYY-MM-DD.log`
- 上传结果：`logs/upload_results.xlsx`

## V1.0 已实现能力

- tkinter 主界面
- 选择商品文件夹
- 开始、暂停/继续、查看日志
- Excel 商品资料读取
- 主图和详情页图片扫描
- 图片格式、大小、尺寸检查
- Playwright 持久化浏览器会话
- 登录检测与人工登录等待
- 验证码检测与人工处理等待
- 网络/页面打开重试
- 商品草稿保存流程框架
- 上传结果记录

## 后续扩展方向

- AI 自动生成淘宝标题
- AI 优化商品详情描述
- 自动生成关键词
- 批量修改价格
- 同步 1688
- 同步其他电商平台

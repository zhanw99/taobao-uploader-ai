"""淘宝商品批量上架助手配置项。"""
from pathlib import Path

APP_NAME = "淘宝商品批量上架助手 V1.0"
BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"
RESULT_FILE = LOG_DIR / "upload_results.xlsx"

# 淘宝千牛卖家后台地址。实际地址可能随淘宝后台调整，可在此统一修改。
QIANNIU_HOME_URL = "https://myseller.taobao.com/home.htm"
PUBLISH_PRODUCT_URL = "https://sell.taobao.com/auction/goods/goods_on_sale.htm"

# 浏览器设置
HEADLESS = False
SLOW_MO_MS = 250
DEFAULT_TIMEOUT_MS = 30_000
RETRY_TIMES = 3
RETRY_INTERVAL_SECONDS = 3
USER_DATA_DIR = BASE_DIR / ".browser_profile"

# 商品目录与文件规则
EXCEL_FILE_NAME = "商品资料.xlsx"
MAIN_IMAGE_PREFIX = "主图"
DETAIL_IMAGE_PREFIX = "详情页"
SUPPORTED_IMAGE_FORMATS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_IMAGE_SIZE_MB = 10
MIN_IMAGE_WIDTH = 300
MIN_IMAGE_HEIGHT = 300

# Excel 字段名
REQUIRED_EXCEL_COLUMNS = [
    "商品标题",
    "商品类目",
    "商品价格",
    "库存数量",
]
OPTIONAL_EXCEL_COLUMNS = [
    "商品颜色",
    "商品尺寸",
    "SKU信息",
    "商品描述",
]

# 页面选择器集中管理。淘宝后台经常改版，现场使用时优先调整这里。
SELECTORS = {
    "login_marker": "text=请登录",
    "captcha_marker": "text=验证码",
    "title_input": "input[name='title'], textarea[name='title']",
    "category_input": "input[placeholder*='类目'], input[name='category']",
    "price_input": "input[name='price'], input[placeholder*='价格']",
    "stock_input": "input[name='stock'], input[placeholder*='库存']",
    "description_input": "textarea[name='description'], div[contenteditable='true']",
    "main_image_upload": "input[type='file']",
    "detail_image_upload": "input[type='file']",
    "save_draft_button": "text=保存草稿, text=保存",
}

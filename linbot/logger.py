import logging
from logging import Logger

#全局日志配置

class Colors:
    GREEN = '\033[92m'      # 绿色
    YELLOW = '\033[93m'     # 黄色
    RED = '\033[91m'        # 红色
    BLUE = '\033[94m'       # 蓝色
    MAGENTA = '\033[95m'    # 洋红色
    CYAN = '\033[96m'       # 青色
    BOLD = '\033[1m'        # 粗体
    UNDERLINE = '\033[4m'   # 下划线
    END = '\033[0m'         # 结束颜色

class Logging:
    logging.addLevelName(25, 'SUCCESS')  # 25介于INFO(20)和WARNING(30)之间

    # 2. 创建记录success级别日志的方法
    def success(self, message, *args, **kwargs):
        if self.isEnabledFor(25):
            message = f"{Colors.GREEN}[SUCCESS]{Colors.END} {message}"
            self._log(25, message, args, **kwargs)
    
    def warning(self, message, *args, **kwargs):
        if self.isEnabledFor(30):
            message = f"{Colors.YELLOW}[WARNING]{Colors.END} {message}"
            self._log(30, message, args, **kwargs)

    def error(self, message, *args, **kwargs):
        if self.isEnabledFor(40):
            message = f"{Colors.RED}[ERROR]{Colors.END} {message}"
            self._log(40, message, args, **kwargs)

    def debug(self, message, *args, **kwargs):
        if self.isEnabledFor(10):
            message = f"{Colors.BLUE}[DEBUG]{Colors.END} {message}"
            self._log(10, message, args, **kwargs)

    def info(self, message, *args, **kwargs):
        if self.isEnabledFor(20):
            message = f"{Colors.UNDERLINE}[INFO]{Colors.END} {message}"
            self._log(20, message, args, **kwargs)

    logger = logging.getLogger("linbot")
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(fmt='%(asctime)s - %(message)s',datefmt='%H:%M:%S')
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    Logger.success = success
    Logger.warning = warning
    Logger.error = error
    Logger.debug = debug
    Logger.info = info
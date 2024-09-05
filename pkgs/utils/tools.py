from __future__ import annotations

import os
import sys

from loguru import logger


class HiddenPrints:

    def __init__(self, hide: bool = True):
        self.hide = hide

    def __enter__(self):
        if self.hide:
            self._original_stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.hide:
            sys.stdout.close()
            sys.stdout = self._original_stdout


import sys

from loguru import logger


# 重定向 print 到 logger
class PrintToLogger:

    def write(self, message):
        if message != '\n':  # 检查消息是否只包含换行符
            logger.info(message)  # 直接将消息写入 logger

    def flush(self):
        pass

    @staticmethod
    def init_logger(terminal: bool = True):
        # s=sys.stdout
        if terminal:
            logger.remove()
        logger.add("./log/test_{time:YYYY-MM-DD-HH-mm-ss-SSS}.log",
                   format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
                   rotation="1 day")
        # 替换 sys.stdout
        sys.stdout = PrintToLogger()
        sys.stderr = PrintToLogger()

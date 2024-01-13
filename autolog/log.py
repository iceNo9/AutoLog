import logging
import os
import time

# 创建一个线程安全的日志记录器
logger = logging.getLogger('my_logger')
logger.setLevel(logging.DEBUG)

# 创建一个控制台处理器，并设置其日志级别
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# 创建一个文件处理器，
log_file_name = time.strftime("%Y-%m-%d", time.localtime()) + ".log"
log_path = os.path.join("logs", log_file_name)
# 判断文件是否存在
if not os.path.exists(log_path):
    # 如果文件不存在，创建文件
    with open(log_path, "w") as file:
        pass  # 这里可以添加你的文件操作代码

file_handler = logging.FileHandler(log_path)
file_handler.setLevel(logging.INFO)

# 创建一个格式化字符串
formatter = logging.Formatter('%(asctime)s - [%(filename)s:%(lineno)d] - %(levelname)s - %(message)s')

# 将格式化字符串添加到处理器中
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# 将处理器添加到记录器中
logger.addHandler(console_handler)
logger.addHandler(file_handler)


# 定义一个函数，用于在线程中输出日志信息
def log_info(rv_str):
    logger.info(rv_str)

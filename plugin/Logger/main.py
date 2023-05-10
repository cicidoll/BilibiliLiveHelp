from loguru import logger
from pathlib import Path
import datetime, sys

date = datetime.datetime.now()

# 路径设置
log_path = "logs"
logger.remove()
format_template = "<green>{time: YYYY/MM/DD HH:mm:ss}</green> <red>|</red> <green>{level}</green> <red>|</red> {message}"

""" 完整日志配置定义 """
# 日志文件名
all_log_file_name = "all_logs-%s.log" % (date.strftime('%Y-%m-%d-%H_%M_%S'))
all_log_file_path: Path = Path(__file__).parents[0].parents[0].resolve() / log_path / all_log_file_name
# 添加日志配置
logger.add(
    all_log_file_path,
    level = "INFO",
    format = format_template
)

""" 错误日志配置定义 """
# 日志文件名
err_log_file_name = "err_logs-%s.log" % (date.strftime('%Y-%m-%d-%H_%M_%S'))
err_log_file_path: Path = Path(__file__).parents[0].parents[0].resolve() / log_path / err_log_file_name
# 添加日志配置
logger.add(
    err_log_file_path,
    level = "ERROR",
    format = format_template
)

""" 调用成功显示 """
logger.add(
    sys.stderr,
    level = "SUCCESS",
    format = format_template
)
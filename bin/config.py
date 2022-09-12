#  -*-  coding: utf-8  -*-
"""
@author 商文涛
@desc 用于处理软件配置参数的模块
@date 2022年5月17日
"""

from loguru import logger
# 数据库存储位置
path_database = '../assets/records.db'
# 录制视频存储位置
path_video = '../assets/records'
# 日志文件路径
path_logfile = "../assets/runtime.log"
# 添加日志文件
logger.add(path_logfile, rotation="500 MB", encoding='utf-8', level="INFO")
# 配置文件路径
path_configfile = "../assets/config.ini"
# 存储输入的ip地址
store_ip = True
# 服务器默认端口
server_port = 17781
# 窗口标题
window_title = "2020217781商文涛"
# 服务器接收缓冲区大小
server_recv_buffersize = 10240
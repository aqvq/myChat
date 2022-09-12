#  -*-  coding: utf-8  -*-
"""
@author 商文涛
@desc 用于处理消息传输的模块
@date 2022年5月15日
"""

import socket
import sys
from PyQt5.QtCore import QThread, QMutex, pyqtSignal
from lib.tcp import Server, Client
from loguru import logger


class MessageServer(Server, QThread):
    """
    消息服务器，用于接收信息
    """
    # 定义信号
    callback_msg = pyqtSignal(object)  # 连接消息处理
    callback_video = pyqtSignal(object)  # 显示接收的视频

    def __init__(self):
        Server.__init__(self)
        QThread.__init__(self)

    def emit(self, conn, addr, msg: dict):
        """
        发送回调信号，供软件进行连接操作或画面显示
        """
        data_type = msg['type']
        data = msg['data']

        if data_type == 'message':
            self.callback_msg.emit({
                'conn': conn,
                'addr': addr,
                'data': data
            })
        if data_type == 'video':
            self.callback_video.emit({
                'conn': conn,
                'addr': addr,
                'data': data
            })

    def run(self):
        """
        运行服务器，持续监听连接信息
        """
        try:
            self.listen()
        except socket.error:
            logger.error("[服务器]: 打开套接字出错")
            sys.exit(1)


class MessageClient(Client, QThread):
    """
    消息客户端，用于发送消息
    """
    def __init__(self, target_ip):
        Client.__init__(self)
        QThread.__init__(self)
        self.mutex = QMutex()
        self.target_ip = target_ip

    def quit(self):
        """
        关闭连接
        """
        self.close_connect()

    def send_message(self, data: str):
        """
        发送消息，启用互斥锁，防止抢占资源
        """
        self.mutex.lock()
        self.sendall({
            'type': 'message',
            'data': data
        })
        self.mutex.unlock()

    def send_video(self, data: bytes):
        """
        发送视频数据，启用互斥锁，防止抢占资源
        """
        self.mutex.lock()
        self.sendall({
            'type': 'video',
            'data': data
        })
        self.mutex.unlock()

    def run(self):
        """
        运行客户端，连接到指定ip的服务器
        """
        try:
            self.get_connect(self.target_ip)
        except:
            pass

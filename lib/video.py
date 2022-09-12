#  -*-  coding: utf-8  -*-
"""
@author 商文涛
@desc 用于发送视频数据的模块
@date 2022年5月22日
"""

import sys
import cv2
from PyQt5.QtCore import QThread, pyqtSignal
from lib.message import MessageClient
from loguru import logger


class VideoSender1(QThread):
    """
    发送视频到服务器，同时发送信号到本地进行回显
    """

    # 在本地显示视频画面的回调信号
    callback_local_video = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.msg_client = None
        self.cap = None
        self.closed = True

    def set_sender(self, msg_client: MessageClient):
        """
        设置消息客户端，通过消息客户端进行数据的发送
        """
        self.msg_client = msg_client

    def quit(self):
        """
        关闭时的清理工作
        """
        self.close_server()
        self.wait()

    def open_server(self):
        """
        打开摄像头，执行一些初始化操作
        """
        try:
            cap = self.cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        except:
            logger.error("打开摄像头出错")
            sys.exit(1)
        self.closed = False

    def close_server(self):
        """
        关闭摄像头
        """
        self.closed = True
        if self.cap:
            self.cap.release()
            self.cap = None

    def sendall(self, data: bytes):
        """
        通过消息客户端发送数据到服务器，如果没有设置消息客户端则直接返回
        """
        if self.msg_client is None:
            return
        self.msg_client.send_video(data)

    def run(self):
        """
        持续读取摄像头内容，进行本地回调及发送至远程服务器
        """
        while not self.closed:
            ret, frame = self.cap.read()
            if not ret:
                logger.error("读取摄像头出错")
                break

            # 本地回调
            self.callback_local_video.emit(frame)
            # 发送到服务器
            self.sendall(frame)
            # QThread函数，休眠50ms
            self.msleep(50)

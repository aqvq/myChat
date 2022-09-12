#  -*-  coding: utf-8  -*-
"""
@author 商文涛
@desc 用于服务端处理摄像头数据的控件
@date 2022年6月17日
"""

import datetime
import time
import cv2
from PyQt5 import QtCore
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QLabel
from loguru import logger
from bin import config


class CameraLabel(QLabel):
    """
    重写QLabel，使之具有显示视频，录制视频以及写入数据库的功能
    """

    def __init__(self, parent=None):
        # logger.debug("[CameraLabel]: __init__")
        QLabel.__init__(self, parent)

        # 界面相关的参数
        self.setMinimumSize(QtCore.QSize(640, 480))

        # 相关数据对象
        self.out = None
        self.addr = None
        self.video_name = ""
        self.end_time = datetime.datetime.now()
        self.start_time = datetime.datetime.now()
        self.database = None
        self.index = -1

    def set_database(self, database):
        """
        设置待写入的数据库
        """
        if database is None:
            logger.error("数据库对象不能设置为空")
        self.database = database

    def set_addr(self, addr):
        """
        设置与标签关联的地址
        """
        self.addr = addr

    def set_index(self, index):
        """
        记录控件所在位置
        """
        self.index = index

    def end_record(self):
        """
        停止录制，并保存现有数据
        """
        # logger.debug("[CameraLabel]: end record")

        self.clear()
        self.repaint()

        # 数据库保存数据
        if self.out is not None:
            if self.database is None:
                logger.error("数据库对象不能设置为空")
            ip = self.video_name.split('-')[-3]
            port = self.video_name.split('-')[-2]
            self.end_time = datetime.datetime.now()
            logger.debug("[Database] start time: {}".format(self.start_time))
            logger.debug("[Database] end time: {}".format(self.end_time))
            logger.debug("[Database] duration: {}".format(self.end_time - self.start_time))
            self.database.insert((ip, port), self.video_name, self.start_time, self.end_time)
            logger.info("[Database] 已添加一条视频记录(存放路径: {} 开始时间: {} 持续时间: {})".format(self.video_name, self.start_time,
                                                                                  self.end_time - self.start_time))
            # opencv停止录制
            self.out.release()
            self.out = None

    def start_record(self):
        """
        开始录制，初始化一些数据
        """
        # logger.debug("[CameraLabel]: start record")

        if self.out is not None:
            self.close()
        # opencv开始录制
        self.video_name = "{dir}/record-{ip}-{port}-{time}.avi".format(dir=config.path_video, ip=self.addr[0],
                                                                       port=self.addr[1], time=int(time.time()))
        self.start_time = datetime.datetime.now()
        logger.debug("video name: {}".format(self.video_name))
        self.out = cv2.VideoWriter(self.video_name, cv2.VideoWriter_fourcc(*'MJPG'), 25, (640, 480))


    def show_video(self, frame):
        """
        显示接收到的视频数据
        """
        # logger.debug("[CameraLabel]: show video")
        if frame is None:
            self.clear()
            self.repaint()
            return

        # opencv录制视频
        if self.out is not None:
            self.out.write(frame)

        # 将图片显示到界面上
        height, width = frame.shape[:2]
        bytesPerLine = 3 * width
        q_img = QImage(frame.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped()
        pixmap = QPixmap.fromImage(q_img).scaled(self.size(), transformMode=1)  # 平滑缩放
        self.setPixmap(pixmap)
        self.repaint()

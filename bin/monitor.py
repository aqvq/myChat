#  -*-  coding: utf-8  -*-
"""
@author 商文涛
@desc 用于处理数据接收端的模块
@date 2022年6月17日
"""

import sys

from PyQt5.QtCore import QTimer, QMutex
from PyQt5.QtGui import QIcon, QPixmap, QFont

from bin import config
from loguru import logger
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QGridLayout, QHBoxLayout, QWidget, QLabel
from lib.message import MessageServer
from lib.database import Database
from lib.camera_label import CameraLabel

class Monitor(QWidget):
    """
    接收端类，用于接收摄像头数据、控制消息数据并进行相关操作
    """
    def __init__(self, parent=None):

        # 初始化界面
        super(Monitor, self).__init__(parent)
        self.setWindowTitle("Monitor - " + config.window_title)
        self.setStyleSheet('background-color: #44cef6;')
        self.setWindowIcon(QIcon('../ui/monitor.png'))
        self.layout = QGridLayout(self)
        self.setLayout(self.layout)
        welcome = QLabel()
        welcome.setText("摄像监控系统 - By 商文涛 2020217781")
        self.layout.addWidget(welcome)
        self.resize(self.sizeHint())

        # 接收端的相关数据对象
        self.cameras = dict()
        self.mutex = QMutex()
        self.database = Database(config.path_database)
        self.msg_server = MessageServer()
        self.msg_server.callback_msg.connect(self.show_msg)
        self.msg_server.callback_video.connect(self.show_video)
        self.msg_server.start()

    def close_all_threads(self, addr=None):
        """
        停止接收数据，关闭所有线程，并保存现有数据
        """
        # logger.debug("[Monitor]: close all threads")
        self.mutex.lock()
        if addr is None:
            for _, camera in self.cameras.items():
                camera.end_record()
        else:
            self.cameras[addr].end_record()
        self.mutex.unlock()

    def show_msg(self, data):
        """
        当接收到连接信息或关闭信息时进行的一些操作
        """
        # logger.debug("[Monitor]: show msg")
        conn = data['conn']
        addr = data['addr']
        data = data['data']

        if data == 'connect':
            question_msg = ("{}\n提醒您：\n是否接受来至{}:{}的连接".format(config.window_title, addr[0], addr[1]))
            reply = QMessageBox.question(
                self, '提示', question_msg, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                # 接受连接
                self.msg_server.accept_connect(addr)

                newCamera = CameraLabel(self)
                self.layout.addWidget(newCamera)
                self.resize(self.sizeHint())
                self.cameras[addr] = newCamera
                self.cameras[addr].set_database(self.database)
                self.cameras[addr].set_addr(addr)
                self.cameras[addr].start_record()

            else:
                # 拒绝连接
                self.msg_server.close_connect(addr)
        elif data == 'close':
            if self.cameras.get(addr, None) is not None:
                logger.debug(self.cameras[addr].index)
                self.close_all_threads(addr)
                self.cameras[addr].deleteLater()
                # 在这里设置了timer来缩小扩大的窗口
                self.timer = QTimer(self)
                self.timer.timeout.connect(lambda: self.resize(self.sizeHint()))
                self.timer.start(1)
                self.cameras.pop(addr)
          
    def show_video(self, data):
        """
        线程回调，显示接收到的视频数据
        """
        conn = data['conn']
        addr = data['addr']
        frame = data['data']
        if self.cameras.get(addr, None) is not None:
            self.cameras[addr].show_video(frame)

    def closeEvent(self, event):
        """
        重载QT的closeEvent，在关闭时询问用户是否关闭，并在程序结束之前进行一些必要的操作
        """
        # logger.debug("[Monitor]: close window")

        # 重构closeEvent函数，关闭所有线程
        reply = QMessageBox.question(
            self, '提示', '{}\n提醒您：\n是否要退出程序？'.format(config.window_title), QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
            self.close_all_threads()
        else:
            event.ignore()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    master = Monitor()
    master.show()
    sys.exit(app.exec_())

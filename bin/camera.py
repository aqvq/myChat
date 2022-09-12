#  -*-  coding: utf-8  -*-
"""
@author 商文涛
@desc 用于处理数据发送端的模块
@date 2022年6月17日
"""

import sys
from bin import config
from loguru import logger
from lib.video import VideoSender
from ui.camera import Ui_MainWindow
import configparser
from PyQt5.QtGui import QPixmap, QImage, QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from lib.message import MessageClient


class Camera(QMainWindow, Ui_MainWindow):
    """
    发送端类，将采集到的摄像头信息发送到服务器
    """
    def __init__(self, parent=None):
        # logger.debug("[Camera]: __init__")

        # 初始化界面
        Ui_MainWindow.__init__(self)
        QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.setWindowTitle("Camera - " + config.window_title) # 设置窗口标题
        self.setStyleSheet('background-color: #44cef6')
        self.setWindowIcon(QIcon('../ui/camera.png'))
        self.connect_button.setEnabled(True) # 界面初始化时设置连接按钮可用，断开按钮不可用
        self.close_button.setDisabled(True)
        self.ip_text.setFocus() # IP编辑框自动获取焦点
        self.connect_button.clicked.connect(self.con_connect_btn)  # 开启连接
        self.ip_text.returnPressed.connect(self.con_connect_btn)   # 关联回车键动作
        self.close_button.clicked.connect(self.close_all_threads)  # 关闭连接

        # 读取配置文件
        logger.debug("读取配置文件")
        if config.store_ip:
            configreader = configparser.ConfigParser()
            try:
                configreader.read(config.path_configfile)
                self.ip_text.setText(configreader['DEFAULT']['ip'])
            except:
                pass

        # 设置发送端
        self.video_sender = None
        self.msg_client = None

    def close_all_threads(self):
        """
        当停止发送数据时，关闭所有线程，并更新UI界面
        """
        logger.debug("关闭所有进程")
        # 关闭发送端进程
        self.close_video_sender()
        self.close_msg_client()

        # 清除摄像头画面
        self.camera_label.clear()
        self.camera_label.repaint()

        # 断开连接时设置连接按钮可用，断开按钮不可用
        self.connect_button.setEnabled(True)
        self.close_button.setDisabled(True)

    def con_connect_btn(self):
        """
        当按下连接按钮时进行的操作，启动消息客户端和视频发送端
        """
        # 启动发送端进程
        self.run_msg_client()
        self.run_video_sender()

        # 连接操作后设置连接按钮不可用，断开按钮可用
        self.connect_button.setDisabled(True)
        self.close_button.setEnabled(True)

    def run_msg_client(self):
        """
        运行消息客户端
        """
        logger.debug("运行消息客户端")

        if self.msg_client:
            return
        self.target_ip = self.ip_text.text()
        self.msg_client = MessageClient(self.target_ip)
        self.msg_client.start()

    def close_msg_client(self):
        """
        关闭消息客户端
        """
        logger.debug("关闭消息客户端")
        if self.msg_client:
            # logger.debug("向服务器发送close消息")
            self.msg_client.send_message('close')
            # logger.debug("关闭客户端")
            self.msg_client.quit()
            # logger.debug("删除客户端")
            self.msg_client = None


    def run_video_sender(self):
        """
        运行视频发送端
        """
        logger.debug("运行视频发送端")
        if self.video_sender:
            return
        self.video_sender = VideoSender()
        self.video_sender.open_server()
        # 创建视频发送线程
        self.video_sender.set_sender(self.msg_client)
        # 连接信号，绑定回调事件
        self.video_sender.callback_local_video.connect(self.show_video_src)
        self.video_sender.start()

    def close_video_sender(self):
        """
        关闭视频发送端
        """
        logger.debug("关闭视频发送端")
        if self.video_sender:
            # 关闭视频发送进程
            self.video_sender.quit()
            self.video_sender = None

            # 清除摄像头画面
            self.camera_label.clear()
            self.camera_label.repaint()

    def show_video_src(self, frame):
        """
        将本地采集的摄像头数据回显到本地界面中
        """
        # logger.debug("[Camera]: show video src")
        if frame is None:
            return
        height, width = frame.shape[:2]
        bytesPerLine = 3 * width
        # opencv的rgb信息是反的，需要进行转换，并将数据转换为QPixmap，显示到label控件上
        q_img = QImage(frame.data, width, height, bytesPerLine,
                       QImage.Format_RGB888).rgbSwapped()
        pixmap = QPixmap.fromImage(q_img).scaled(
            self.camera_label.size(), transformMode=1)  # 平滑缩放
        self.camera_label.setPixmap(pixmap)
        self.camera_label.repaint()

    def closeEvent(self, event):
        """
        重载QT的closeEvent，在关闭时询问用户是否关闭，并在结束程序前执行必要的数据保存与清理工作
        """
        logger.debug("用户尝试关闭窗口")

        # 重构closeEvent函数，关闭所有线程
        reply = QMessageBox.question(
            self, '提示', '{}\n提醒您：\n是否要退出程序？'.format(config.window_title), QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
            self.close_all_threads()

            # 保存配置信息
            logger.debug("保存配置信息")
            stored_ip = self.ip_text.text()
            if stored_ip and config.store_ip:
                configwriter = configparser.ConfigParser()
                configwriter['DEFAULT'] = {'ip': stored_ip}
                with open(config.path_configfile, 'w') as configfile:
                    configwriter.write(configfile)
        else:
            event.ignore()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    detector = Camera()
    detector.show()
    sys.exit(app.exec_())

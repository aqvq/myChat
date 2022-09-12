import os
import threading
from loguru import logger
import bin.config as config
from bin.translate_ui import translate_ui
import sys
from PyQt5.QtWidgets import  QApplication

def run_monitor():
    # os.system(r"cd C:\Users\shang\myChat\bin\ &&  C:\Users\shang\anaconda3\envs\myChat\python.exe C:\Users\shang\myChat\bin\monitor.py")
    app = QApplication(sys.argv)
    master = Monitor()
    master.show()
    app.exec_()

def run_camera():
    # os.system(r"cd C:\Users\shang\myChat\bin\ && C:\Users\shang\anaconda3\envs\myChat\python.exe C:\Users\shang\myChat\bin\camera.py")
    app = QApplication(sys.argv)
    detector = Camera()
    detector.show()
    app.exec_()

if __name__ == "__main__":

    translate_ui(r'./ui/camera.ui')
    from bin.monitor import Monitor
    from bin.camera import Camera
    monitor = threading.Thread(target=run_monitor)
    camera = threading.Thread(target=run_camera)
    monitor.start()
    camera.start()
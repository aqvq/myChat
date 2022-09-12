#  -*-  coding: utf-8  -*-
"""
@author 商文涛
@desc 用于处理摄像头设备的模块
@date 2022年5月13日
"""

class CameraDevice:
    """
    摄像头类，返回本地摄像头或ip网络摄像头
    """
    def __init__(self, ip=None, port=None, username="admin", password="admin"):
        if ip == None and port == None:
            self._url = 0
        else:
            self._ip = ip
            self._port = port
            self._username = username
            self._password = password
            self._url = f"http://{username}:{password}@{ip}:{port}/"

    def device(self):
        """
        返回本地摄像头编号或ip网络摄像头网址
        """
        return self._url


if __name__ == "__main__":
    ip = "127.0.0.1"
    port = "4567"
    username = "shang"
    password = "2020217781"
    ip_camera = CameraDevice(ip, port, username, password)
    print("IP camera url: ", ip_camera.device())

    pc_camera = CameraDevice()
    print("PC camera index: ", pc_camera.device())
#  -*-  coding: utf-8  -*-
"""
@author 商文涛
@desc 用于处理数据传输的模块
@date 2022年6月14日
"""

from abc import abstractmethod
import socket
import struct
import pickle
import threading
from lib.data_handler import DataHandler
from bin import config
from loguru import logger


class Server:
    """
    服务器：用于发送数据
    """
    def __init__(self):
        self.address = ('', config.server_port) # config.server_port为config模块预置的参数
        self.sock = None
        self.conn_map = {}

    @abstractmethod
    def emit(self, conn, addr: tuple, msg: dict):
        """
        信号发送函数，需要子类重写
        """
        pass

    def accept_connect(self, addr):
        """
        接受连接之后，创建线程进行数据接收的操作
        """
        logger.info('[服务器]: 接受来自{}:{}的连接'.format(addr[0], addr[1]))
        conn = self.conn_map[addr]
        link = threading.Thread(
            target=self.connect_thread, args=(conn, addr))
        link.setDaemon(True)
        link.start()

    def close_connect(self, addr):
        """
        关闭连接并删除保存的连接信息
        """
        conn = self.conn_map.get(addr, None)
        if conn:
            self.conn_map.pop(addr)
            conn.close()

    def connect_thread(self, conn, addr):
        """
        用于接收客户端消息，解决数据流连续发送过程中的粘包问题
        """
        conn_map = self.conn_map

        data_buffer = b''
        header_size = struct.calcsize('L')  # 结果为4

        while conn_map.get(addr):
            try:
                # 使用滑动窗口不断接收数据
                while len(data_buffer) < header_size:
                    data_buffer += conn.recv(config.server_recv_buffersize)
                packed_size = data_buffer[:header_size]
                data_buffer = data_buffer[header_size:]
                msg_size = struct.unpack('L', packed_size)[0]
                while len(data_buffer) < msg_size:
                    data_buffer += conn.recv(config.server_recv_buffersize)
                zipdata = data_buffer[:msg_size]
                data = DataHandler.decode(zipdata)
                data = pickle.loads(data)
                # 使用回调函数执行后续操作
                self.emit(conn, addr, data)
                # 滑动窗口向前移动
                data_buffer = data_buffer[msg_size:]
            except:
                break

        conn_map.pop(addr)
        logger.info('[服务器]: {}:{}已断开连接'.format(addr[0],addr[1]))
        conn.close()

    def listen(self):
        """
        绑定端口，时刻监听新的连接
        """
        # tcp sock
        sock = self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(self.address)
        sock.listen(3)
        logger.info('[服务器]: 端口{}绑定成功!'.format(config.server_port))

        while True:
            # 接受新的连接
            conn, addr = sock.accept()
            self.conn_map[addr] = conn
            self.emit(conn, addr, {
                'type': 'message',
                'data': 'connect'
            })


class Client:
    """
    客户端：只发送数据
    """

    def __init__(self) -> None:
        self.sock = None
        self.is_connected = False
        self.closed = False

    def get_connect(self, target_ip: str):
        """
        连接到指定ip的服务器
        """
        logger.info('[客户端]: 即将连接到' + target_ip)
        try:
            # 与服务端建立socket连接
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((target_ip, config.server_port))
            self.is_connected = True
            self.closed = False
            logger.info('[客户端]: 已与服务器建立连接，等待服务器确认中...')
        except:
            logger.error('[客户端]: 连接失败，请重试')
            self.close_connect()

    def close_connect(self):
        """
        关闭连接，释放套接字
        """
        if self.sock:
            self.sock.close()
            self.sock = None
        self.is_connected = False
        self.closed = True

    def sendall(self, obj):
        """
        打包编码并发送数据
        """
        senddata = pickle.dumps(obj)
        senddata = DataHandler.encode(senddata)
        try:
            self.sock.sendall(struct.pack('L', len(senddata)) + senddata)
        except:
            logger.debug('[客户端]: 数据发送失败')
            self.close_connect()

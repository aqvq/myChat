#  -*-  coding: utf-8  -*-
"""
@author 商文涛
@desc 用于处理数据传输编码与解码的模块
@date 2022年5月15日
"""

import base64

class DataHandler:
    """
    在网络传输过程中，进行一些加密、编码操作，本类只有静态方法，不需要创建具体实例
    """
    def __init__(self) -> None:
        pass

    @staticmethod
    def encode(send_data: bytes) -> bytes:
        """
        编码数据
        """
        return base64.b64encode(send_data)

    @staticmethod
    def decode(receive_data: bytes) -> bytes:
        """
        解码数据
        """
        return base64.b64decode(receive_data)



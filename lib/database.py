#  -*-  coding: utf-8  -*-
"""
@author 商文涛
@desc 用于处理数据库的模块
@date 2022年5月15日
"""

import datetime
import os
import sqlite3
from loguru import logger
import time


class Database:
    """
    用于数据库操作
    """
    def __init__(self, database):
        """
        定义一些数据库操作常用命令的常量，在第一次运行时创建数据库，最后连接数据库
        """
        self.CREATE_RECORDS = "create table records( id INTEGER PRIMARY KEY AUTOINCREMENT, ip TEXT NOT NULL, port INTEGER NOT NULL, start DATETIME NOT NULL, end DATETIME NOT NULL, duration TIME NOT NULL, path TEXT NOT NULL)"
        self.INSERT_RECORD = "insert into records(ip, port, start, end, duration,path) values('{}', '{}', '{}', '{}', '{}', '{}')"
        self.DELETE_RECORDS = "drop table records"
        self.SHOW_RECORDS = "select * from records"
        self.ORDER_BY_ID_ASC = " order by id asc"
        self.ORDER_BY_START_ASC = " order by start asc"
        self.ORDER_BY_END_ASC = " order by end asc"
        self.ORDER_BY_DURATION_ASC = " order by duration asc"
        self.ORDER_BY_ID_DESC = " order by id desc"
        self.ORDER_BY_START_DESC = " order by start desc"
        self.ORDER_BY_END_DESC = " order by end desc"
        self.ORDER_BY_DURATION_DESC = " order by duration desc"
        self.ORDER_BY_IP_ASC = "order by ip asc"
        self.ORDER_BY_IP_DESC = "order by ip desc"
        self.ORDER_BY_PORT_ASC = "order by port asc"
        self.ORDER_BY_PORT_DESC = "order by port desc"

        first_start = False
        if not os.path.exists(database):
            logger.debug("数据库({})不存在".format(database))
            first_start = True

        # ===================INIT===================
        # self.conn = sqlite3.connect(database, check_same_thread=False)
        self.conn = sqlite3.connect(database)
        logger.info("数据库({})连接成功".format(database))
        # ==========================================

        if first_start:
            self.execute(self.CREATE_RECORDS)
            logger.debug("数据表创建成功")

    def execute(self, sql):
        """
        执行sql语句
        """
        cursor = self.conn.cursor()
        cursor.execute(sql)
        logger.info("执行SQL语句: {}".format(sql))
        logger.info("{}行被影响".format(self.conn.total_changes))
        ret = cursor.fetchall()
        self.conn.commit()
        cursor.close()
        return ret

    def create(self):
        """
        创建records表
        """
        self.execute(self.CREATE_RECORDS)

    def destroy(self):
        """
        删除records表
        """
        self.execute(self.DELETE_RECORDS)

    def insert(self, addr, path, start, end):
        """
        向records表中插入一条记录
        """
        sql = self.INSERT_RECORD.format(addr[0], addr[1], start, end, end - start, path)
        self.execute(sql)

    def show(self, order=''):
        """
        根据order的规则显示records表中的所有数据内容
        """
        content = self.execute(self.SHOW_RECORDS + order)
        logger.info("记录: {}".format(content))

    def __del__(self):
        """
        当对象销毁时关闭数据库
        """
        self.conn.close()


if __name__ == "__main__":
    logger.add('runtime.log')
    db = Database('2020217781.db')
    start_time = datetime.datetime.now()
    time.sleep(3)
    end_time = datetime.datetime.now()
    db.show()
    db.insert(("127.0.0.1", 17781), r"C:\Users\shang\myChat\Receiver", start_time, end_time)
    db.show()

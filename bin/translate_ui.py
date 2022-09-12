#  -*-  coding: utf-8  -*-
"""
@author 商文涛
@desc 用于处理ui文件的模块
@date 2022年5月13日
"""

import os
from loguru import logger
# import config

def translate_ui(ui_file):
    """
    将ui文件自动转换成python文件
    """
    base_name = os.path.basename(ui_file)
    pure_name = os.path.splitext(base_name)[0]
    dir = os.path.dirname(ui_file)
    source = ui_file
    dist = os.path.join(dir, pure_name+'.py')
    logger.debug("Translate ui | base name: {}".format(base_name))
    logger.debug("Translate ui | pure name: {}".format(pure_name))
    logger.debug("Translate ui | dir: {}".format(dir))
    logger.debug("Translate ui | source: {}".format(source))
    logger.debug("Translate ui | dist: {}".format(dist))
    logger.info("Translate ui | {}".format('python -m PyQt5.uic.pyuic ' + source + ' -o ' + dist))
    os.system('python -m PyQt5.uic.pyuic ' + source + ' -o ' + dist)


if __name__ == "__main__":
    # logger.add(config.path_logfile, rotation="500 MB", encoding='utf-8', level='INFO')
    translate_ui(r'../ui/camera.ui')

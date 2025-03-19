import os
import time
from threading import Lock
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QPixmap
import logging
from typing import Tuple


class Worker(QThread):
    """
    基类
    """
    image_processed = pyqtSignal(QPixmap)  # 用于发送处理后的图像
    stopSignal = pyqtSignal()  # 用于停止线程
    loggerSignal = pyqtSignal(list)

    def __init__(self, WorkerName=None, FilePath=None):
        super(Worker, self).__init__()
        self.is_DualSwitch = 'openpose'
        self.DualSwitch = None
        self.is_open = None
        self.is_open_models = 'openpose'
        self.humans = None
        self.image = None
        self.lock = Lock()  # 创建一个锁对象
        self.is_paused = False  # 用于标记线程是否被暂停
        self.fps_time = time.time()
        self.WorkerName = WorkerName
        self.is_paused = True
        self.WorkerName = WorkerName
        self.FilePath = FilePath
        self.logger = logging.getLogger(__name__)
        self.root_dir = os.path.split(os.path.abspath(__file__))[0]
        self.args = self.parse_arguments()

    def parse_arguments(self, WorkerName=None, FilePath=None) -> Tuple[str, str]:
        """
        参数解析
        :param WorkerName: 功能模块functionModule
        :param FilePath: 文件地址file_address
        """
        pass

    def InitialEnvironment(self) -> None:
        """
        环境初始化
        """
        pass

    def run(self) -> None:
        """
        主运算逻辑
        """
        # self.start()
        pass

    def start_run(self) -> None:
        """
        启动线程
        """
        self.start()
        pass

    def stop(self) -> None:
        """
        终止线程
        """
        pass

    def pause(self):
        """
        暂停线程的执行
        """
        self.is_paused = False

    def resume(self):
        """
        恢复线程的执行
        """
        self.is_paused = True

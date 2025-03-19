import argparse  # 导入用于构建命令行参数的模块
import ctypes
import logging  # 导入用于日志记录的模块
import os
import re
import sys
from io import BytesIO

import numpy as np
import requests
from PyQt5.QtCore import pyqtSlot, Qt, pyqtSignal, QMutex
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QGridLayout, QWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QImage, QPixmap
from tf_pose import common
import cv2  # 导入OpenCV库，用于图像处理
from tf_pose.estimator import TfPoseEstimator  # 从tf_pose库导入TfPoseEstimator类，用于姿态估计
from tf_pose.networks import get_graph_path, model_wh  # 从tf_pose库导入网络相关的函数
import warnings

warnings.filterwarnings("ignore")

logger = logging.getLogger('TfPoseEstimator')  # 获取一个记录器，用于记录日志
logger.setLevel(logging.DEBUG)  # 设置记录器的日志级别为DEBUG
ch = logging.StreamHandler()  # 创建一个流处理器，用于输出日志到控制台
ch.setLevel(logging.DEBUG)  # 设置流处理器的日志级别为DEBUG
formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')  # 创建一个日志格式器
ch.setFormatter(formatter)  # 将格式器设置到流处理器
logger.addHandler(ch)  # 将流处理器添加到记录器


class Worker_image():
    humans_sold = pyqtSignal(list)

    def __init__(self, image_path):
        self.image_mast = None
        self.image_path = image_path
        self.w, self.h = model_wh('0x0')  # 假设不调整输入图像大小
        self.args = self.parse_arguments(self.image_path)
        if self.w == 0 or self.h == 0:
            self.e = TfPoseEstimator(get_graph_path(self.args.model),
                                     target_size=(432, 368))  # 创建TfPoseEstimator对象，使用默认尺寸
        else:
            self.e = TfPoseEstimator(get_graph_path(self.args.model),
                                     target_size=(self.w, self.h))  # 创建TfPoseEstimator对象，使用指定的尺寸
        self.image = common.read_imgfile(self.args.image, None, None)

    def parse_arguments(self, image_path):
        """
        参数解析
        :param image_path: 图片路径
        :return:
        """
        parser = argparse.ArgumentParser(description='tf-pose-estimation run')  # 创建一个命令行参数解析器
        parser.add_argument('--image', type=str, default=image_path)
        parser.add_argument('--model', type=str, default='mobilenet_thin',
                            help='cmu / mobilenet_thin')  # 添加一个命令行参数，用于指定模型类型
        parser.add_argument('--resize', type=str, default='0x0',  # 添加一个命令行参数，用于指定图像的调整大小
                            help='if provided, resize images before they are processed. default=0x0,'
                                 ' Recommends : 432x368 or 656x368 or 1312x736 ')
        parser.add_argument('--resize-out-ratio', type=float, default=4.0,  # 添加一个命令行参数，用于指定输出尺寸的比例
                            help='if provided, resize heatmaps before they are post-processed. default=1.0')
        parser.add_argument('--output_json', type=str, default='C:/Windows/Temp/',
                            help='writing output json dir')  # 添加一个命令行参数，用于指定输出JSON的目录
        return parser.parse_args()

    def display_image(self, image):
        """
        图像转换
        :param image: 图片
        """
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # 将 OpenCV 的 BGR 图像转换为 RGB 格式
        height, width, channels = image_rgb.shape
        bytes_per_line = channels * width
        convert_to_qt_format = QImage(image_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888) # 将 NumPy 数组转换为 QImage
        pixmap = QPixmap.fromImage(convert_to_qt_format)  # 创建 QPixmap 并将其设置为 QLabel 的显示内容
        return pixmap

    def server_imgfile(self, path):
        response = requests.get(path)
        if response.status_code == 200:  # 确保请求成功
            image_data = BytesIO(response.content)  # 从HTTP响应中获取图像数据
            image = cv2.imdecode(np.frombuffer(image_data.read(), np.uint8), cv2.IMREAD_UNCHANGED)
            return image

    def masterMap(self):
        """
        原图
        """
        if self.image_path is None:
            logger.error('Image can not be read, path=%s' % self.args.image)  # 如果图像无法读取，记录错误信息
            sys.exit(-1)  # 退出程序
        if re.match(r'http[s]?://.*\.(jpg|jpeg|png|bmp|gif|tiff)$', self.image_path, re.IGNORECASE):
            self.image_mast = self.server_imgfile(self.image_path)
        else:
            self.image_mast = cv2.imread(self.image_path)
        self.image_mast = cv2.resize(self.image_mast, (432, 368), interpolation=cv2.INTER_AREA)
        pixmap = self.display_image(self.image_mast)
        return pixmap

    def heatMap(self):
        """
        热力图
        """
        tmp = np.amax(self.e.heatMat[:, :, :-1], axis=2)
        tmp_8bit = (tmp - np.min(tmp)) / (np.max(tmp) - np.min(tmp)) * 255  # 将热图数据转换为 8 位整数格式
        tmp_8bit = tmp_8bit.astype(np.uint8)
        pixmap = self.display_image(tmp_8bit)
        return pixmap

    def poseMap(self):
        """
        绘制姿态结果
        :return:
        """
        self.image = common.read_imgfile(self.args.image, None, None)
        humans = self.e.inference(self.image, resize_to_default=True, upsample_size=4.0)
        # self.humans_sold.emit(humans)
        image = TfPoseEstimator.draw_humans(self.image, humans, imgcopy=False, frame=0)
        # output_json_dir=self.args.output_json)  # 在图像上绘制姿态结果
        images = cv2.resize(image, (self.e.heatMat.shape[1], self.e.heatMat.shape[0]), interpolation=cv2.INTER_AREA)
        pixmap = self.display_image(images)
        return pixmap, humans

    def paf_x(self):
        # 显示向量图 - x方向
        humans = self.e.inference(self.image, resize_to_default=True, upsample_size=4.0)
        image = TfPoseEstimator.draw_humans(self.image, humans, imgcopy=False, frame=0)
        # output_json_dir=self.args.output_json)  # 在图像上绘制姿态结果
        self.tmp = self.e.pafMat.transpose((2, 0, 1))  # 转置PAF矩阵
        tmp2_odd = np.amax(np.absolute(self.tmp[::2, :, :]), axis=0)  # 计算奇数PAF的最大值
        tmp_8bit_x = (tmp2_odd - np.min(tmp2_odd)) / (np.max(tmp2_odd) - np.min(tmp2_odd)) * 255  # 将热图数据转换为 8 位整数格式
        tmp_8bit_x = tmp_8bit_x.astype(np.uint8)
        pixmap = self.display_image(tmp_8bit_x)
        return pixmap

    def paf_y(self):
        # 显示向量图 - y方向
        humans = self.e.inference(self.image, resize_to_default=True, upsample_size=4.0)
        image = TfPoseEstimator.draw_humans(self.image, humans, imgcopy=False, frame=0)
        # output_json_dir=self.args.output_json)
        images = cv2.resize(image, (self.e.heatMat.shape[1], self.e.heatMat.shape[0]), interpolation=cv2.INTER_AREA)
        self.tmp = self.e.pafMat.transpose((2, 0, 1))  # 转置PAF矩阵
        tmp2_even = np.amax(np.absolute(self.tmp[1::2, :, :]), axis=0)  # 计算偶数PAF的最大值
        tmp_8bit_y = (tmp2_even - np.min(tmp2_even)) / (np.max(tmp2_even) - np.min(tmp2_even)) * 255  # 将热图数据转换为 8 位整数格式
        tmp_8bit_y = tmp_8bit_y.astype(np.uint8)
        pixmap = self.display_image(tmp_8bit_y)
        return pixmap

    def maps_emit(self):
        self.poseMap_image, self.poseMap_info = self.poseMap()
        return self.masterMap(), self.paf_x(), self.paf_y(), self.heatMap(), self.poseMap_image, self.poseMap_info


from run_app.worker.worker import Worker


class FileProcessingThread(Worker):
    image_loaded1 = pyqtSignal(QPixmap)  # 定义信号
    image_loaded2 = pyqtSignal(QPixmap)
    image_loaded3 = pyqtSignal(QPixmap)
    image_loaded4 = pyqtSignal(QPixmap)
    image_loaded5 = pyqtSignal(QPixmap)
    poseMap_info_list = pyqtSignal(list)

    def __init__(self, image_path=None, folder_path=None):
        super(FileProcessingThread, self).__init__()
        self.is_paused = True
        self.lock = QMutex()  # 创建一个锁对象，使用 PyQt5 提供的锁
        self.image_path = image_path
        self.folder_path = folder_path
        self.image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff'}
        self.image_list = []
        self.current_image_index = 0

    def run1(self):
        """
        循环文件夹的方法
        """
        # 获取文件夹中所有文件的列表，并筛选出图片文件
        try:
            self.image_list = [f for f in os.listdir(self.folder_path) if
                               os.path.isfile(os.path.join(self.folder_path, f)) and os.path.splitext(f)[
                                   1].lower() in self.image_extensions]
        except:
            self.image_list = self.folder_path
            print(type(self.image_list))

        if self.is_paused:
            self.lock.lock()  # 获取锁
            try:
                for self.current_image_index in range(len(self.image_list)):
                    if not self.is_paused:
                        break
                    image_path = os.path.join(self.image_list, self.image_list[self.current_image_index])
                    pixmap1, pixmap2, pixmap3, pixmap4, pixmap5, humans = Worker_image(image_path).maps_emit()
                    self.image_loaded1.emit(pixmap1)
                    self.image_loaded2.emit(pixmap2)
                    self.image_loaded3.emit(pixmap3)
                    self.image_loaded4.emit(pixmap4)
                    self.image_loaded5.emit(pixmap5)
                    self.poseMap_info_list.emit(humans)
            finally:
                self.lock.unlock()

    def run(self):
        if self.is_paused:
            try:
                pixmap1, pixmap2, pixmap3, pixmap4, pixmap5, humans = Worker_image(self.image_path).maps_emit()
                self.image_loaded1.emit(pixmap1)
                self.image_loaded2.emit(pixmap2)
                self.image_loaded3.emit(pixmap3)
                self.image_loaded4.emit(pixmap4)
                self.image_loaded5.emit(pixmap5)
                self.poseMap_info_list.emit(humans)
            except Exception:
                logging.info('The image is not valid. Please check your image exists.')
                # pass  # todo
        else:
            pass  # todo

    def start_run(self):
        """
        启动线程
        """
        self.start()
        pass

    def stop(self):
        """
        终止线程
        """
        # self.is_paused = False
        # self.wakeUp()
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

    def kill(self):
        """
        杀死线程
        :return:
        """
        self.pause()  # 暂停线程
        self.deleteLater()  # 杀死线程


# 创建一个主窗口类
class MainWindow(QMainWindow):
    def __init__(self, image_path):
        super().__init__()
        self.initUI()
        self.file_worker = FileProcessingThread(image_path=image_path)
        self.file_worker.image_loaded1.connect(self.show_image1)
        self.file_worker.image_loaded2.connect(self.show_image2)
        self.file_worker.image_loaded3.connect(self.show_image3)
        self.file_worker.image_loaded4.connect(self.show_image4)
        self.file_worker.image_loaded5.connect(self.show_image5)
        self.file_worker.start()

    def get_desktop_size(self):
        # 定义获取桌面分辨率的函数
        def get_screen_resolution():
            user32 = ctypes.windll.user32
            screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
            return screensize

        # 获取桌面大小
        self.width, self.height = get_screen_resolution()
        return self.width, self.height

    def centre_windowd(self, x, y):
        window_x, window_y = self.get_desktop_size()
        x, y = (window_x - x) // 2, (window_y - y) // 2
        return x, y

    @pyqtSlot()
    def initUI(self):
        self.setWindowTitle('图片姿态检测')
        window_w, window_h = self.get_desktop_size()  # 获取桌面的分辨率elf
        window_w, window_h = window_w * 0.4, window_h * 0.8
        window_x, window_y = self.centre_windowd(window_w, window_h)
        self.setGeometry(window_x, window_y, window_w, window_h)
        central_widget = QWidget()  # 创建容器
        self.setCentralWidget(central_widget)
        layout = QGridLayout()  # 创建一个网格布局
        vertical_layout1 = QVBoxLayout()  # 垂直布局
        vertical_layout2 = QVBoxLayout()
        vertical_layout3 = QVBoxLayout()
        vertical_layout4 = QVBoxLayout()
        vertical_layout5 = QVBoxLayout()
        vertical_layout6 = QVBoxLayout()
        horizontal_layout1 = QHBoxLayout()  # 水平布局
        horizontal_layout2 = QHBoxLayout()

        # 创建四个 QLabel 控件用于显示图像
        self.label1 = QLabel(self)
        self.label3 = QLabel(self)
        self.label4 = QLabel(self)
        self.label5 = QLabel(self)
        self.label6 = QLabel(self)

        self.label1_t = QLabel(self)
        self.label3_t = QLabel(self)
        self.label4_t = QLabel(self)
        self.label5_t = QLabel(self)
        self.label6_t = QLabel(self)

        self.label1_t.setText('原图')
        self.label3_t.setText('Vector-X')
        self.label4_t.setText('Vector-Y')
        self.label5_t.setText('热力图')
        self.label6_t.setText('预测图')

        for label in [
            self.label1_t, self.label3_t, self.label4_t, self.label5_t, self.label6_t,
            self.label1, self.label3, self.label4, self.label5, self.label6
        ]:
            label.setAlignment(Qt.AlignCenter)  # 设置 QLabel 的对齐方式
            self.label1.setMinimumSize(216, 184)

        # 将 QLabel 添加到布局中
        vertical_layout1.addWidget(self.label1_t)
        vertical_layout3.addWidget(self.label3_t)
        vertical_layout4.addWidget(self.label4_t)
        vertical_layout5.addWidget(self.label5_t)
        vertical_layout6.addWidget(self.label6_t)

        vertical_layout1.addWidget(self.label1)
        vertical_layout3.addWidget(self.label3)
        vertical_layout4.addWidget(self.label4)
        vertical_layout5.addWidget(self.label5)
        vertical_layout6.addWidget(self.label6)

        layout.addLayout(vertical_layout3, 1, 0)
        layout.addLayout(vertical_layout4, 1, 1)
        layout.addLayout(vertical_layout5, 2, 0)
        layout.addLayout(vertical_layout6, 2, 1)

        vertical_layout2.addLayout(vertical_layout1)
        vertical_layout2.addLayout(layout)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_widget.setLayout(vertical_layout2)

    def show_image1(self, pixmap1):
        self.label1.setPixmap(pixmap1)

    def show_image2(self, pixmap2):
        self.label3.setPixmap(pixmap2)

    def show_image3(self, pixmap3):
        self.label4.setPixmap(pixmap3)

    def show_image4(self, pixmap4):
        self.label5.setPixmap(pixmap4)

    def show_image5(self, pixmap5):
        self.label6.setPixmap(pixmap5)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # window = MainWindow('../images')
    # window = MainWindow('../resources/images/p1.jpg')
    # window = MainWindow('http://47.100.111.106/download_image/1ea60c9e61b91f84cc9a6e9473bcb3fdf21af797.jpg')
    window = MainWindow('https://scpic.chinaz.net/files/pic/pic9/201911/zzpic21097.jpg')

    window.show()
    sys.exit(app.exec())

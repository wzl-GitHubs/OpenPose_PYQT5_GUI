import ctypes
import gc
import os
import argparse
import sys
import time
import cv2
import mediapipe as mp
from PyQt5.QtCore import pyqtSignal, QTimer, Qt
from PyQt5.QtGui import QPixmap, QImage, QGuiApplication
import logging
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QWidget, QGridLayout
from tf_pose.estimator import TfPoseEstimator, logger
from tf_pose.networks import model_wh, get_graph_path
from threading import Lock
from run_app.worker.worker import Worker


class Worker_carme(Worker):
    """
    摄像头
    """
    image_processed = pyqtSignal(QPixmap)  # 用于发送处理后的图像
    stopSignal = pyqtSignal()  # 用于停止线程
    loggerSignal = pyqtSignal(list)

    # def __init__(self, WorkerName: object = None, FilePath: object = None,
    #              Camera_Index='http://192.178.124.1:8089') -> object:
    def __init__(self, WorkerName: object = None, FilePath: object = None,
                 Camera_Index=0) -> object:
        super(Worker_carme, self).__init__()

        self.WorkerName = WorkerName
        # self.FilePath = FilePath
        self.Camera_Index = Camera_Index
        self.is_open_moldes = True
        self.humans = None
        self.lock = Lock()  # 创建一个锁对象
        self.is_paused = False  # 用于标记线程是否被暂停
        self.fps_time = time.time()
        self.logger = logging.getLogger(__name__)
        self.root_dir = os.path.split(os.path.abspath(__file__))[0]
        self.args = self.parse_arguments()
        self.video_cap = cv2.VideoCapture(self.Camera_Index)
        self.total_frames = int(self.video_cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = self.video_cap.get(cv2.CAP_PROP_FPS)
        self.ret, self.image = self.video_cap.read()
        try:
            self.height, self.width, self.channels = self.image.shape  # 拿到输入数据的长宽，后续调整窗口大小
        except AttributeError as e:
            raise AttributeError(f"传入参数错误:无法识别该摄像头 {e}")
        self.w, self.h = model_wh(self.args.resize)
        if self.w > 0 and self.h > 0:
            self.e = TfPoseEstimator(get_graph_path(self.args.model), target_size=(self.w, self.h))
        else:
            self.e = TfPoseEstimator(get_graph_path(self.args.model), target_size=(432, 368))

        self.is_DualSwitch = 'openpose'
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_pose = mp.solutions.pose
        self.pose_model = self.init_pose_model()

        self.camera_timer = QTimer(self)
        self.camera_timer.timeout.connect(self.on_signal_list)
        self.camera_timer.start(1000)
        self.iconwindow = QPixmap(os.path.join(self.root_dir, '../../resources/icon/002.png'))

    def parse_arguments(self):
        """
        参数解析
        :return:
        """
        parser = argparse.ArgumentParser(description='tf-pose-estimation realtime webcam')
        # b. 添加camera参数，用于指定摄像头编号，默认为0
        parser.add_argument('--camera', type=int, default=0)
        # c. 添加resize参数，用于指定图像缩放尺寸，默认为'0x0'
        parser.add_argument('--resize', type=str, default='0x0',
                            help='if provided, resize images before they are processed. default=0x0, '
                                 'Recommends : 432x368 or 656x368 or 1312x736')
        # d. 添加resize-out-ratio参数，用于指定热图缩放比例，默认为4.0
        parser.add_argument('--resize-out-ratio', type=float, default=4.0,
                            help='if provided, resize heatmaps before they are post-processed. default=1.0')
        # e. 添加model参数，用于指定模型类型，默认为'mobilenet_thin'
        parser.add_argument('--model', type=str, default='mobilenet_thin', help='cmu / mobilenet_thin')
        # f. 添加output_json参数，用于指定输出json文件的目录，默认为'E:/tmp/'
        parser.add_argument('--output_json', type=str, default='C:/Windows/Temp/', help='writing output json dir')
        # g. 添加show-process参数，用于调试目的，如果启用，推理速度会降低，默认为False
        parser.add_argument('--show-process', type=bool, default=False,
                            help='for debug purpose, if enabled, speed for inference is dropped.')
        # h.解析命令行参数
        return parser.parse_args()

    def InitialEnvironment(self) -> None:
        """
        环境初始化
        """
        try:
            if self.video_cap is None:
                self.video_cap = cv2.VideoCapture(self.Camera_Index)
                if not self.video_cap.isOpened():
                    raise Exception("Failed to open camera")
                logger.info("Camera initialized successfully")
        except cv2.error as e:
            logger.error(f"Error initializing camera: {e}")
            print(f"Error initializing camera: {e}")  # 打印到控制台
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            print(f"An unexpected error occurred: {e}")  # 打印到控制台

    def init_pose_model(self):
        """初始化MediaPipe姿态估计模型"""
        model_complexity = 1
        enable_segmentation = False
        min_detection_confidence = 0.5
        min_tracking_confidence = 0.5

        return self.mp_pose.Pose(
            model_complexity=model_complexity,
            enable_segmentation=enable_segmentation,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )

    def run(self) -> None:
        """
        主运算逻辑
        """
        frame = 0
        while self.is_paused:
            with self.lock:
                ret, self.image = self.video_cap.read()
                if ret:
                    if self.is_open_moldes:
                        if self.is_DualSwitch == 'openpose':
                            self.humans = self.e.inference(self.image, resize_to_default=(self.w > 0 and self.h > 0),
                                                           upsample_size=self.args.resize_out_ratio)
                            # todo e.inference()
                            # logger.debug(self.humans)
                            self.image = TfPoseEstimator.draw_humans(self.image, self.humans, imgcopy=False,
                                                                     frame=frame)
                            # output_json_dir=self.args.output_json)
                        elif self.is_DualSwitch == 'posenet':
                            results = self.pose_model.process(self.image)
                            if results.pose_landmarks:
                                self.mp_drawing.draw_landmarks(
                                    self.image,
                                    results.pose_landmarks,
                                    self.mp_pose.POSE_CONNECTIONS,
                                    connection_drawing_spec=self.mp_drawing.DrawingSpec(
                                        color=(0, 255, 0), thickness=2))
                                time.sleep(0.005)  # 睡眠33毫秒
                                self.humans = ['现在运行的是Google的posenet']
                    else:
                        self.image = self.image
                        self.humans = ['现在运行的是opencv读取的原视频']
                    frame += 1
                    plan = (frame / self.total_frames) * 100
                    # todo
                    # logger.debug('show+')
                    cv2.putText(self.image,
                                "FPS: %f" % (1.0 / (time.time() - self.fps_time)),
                                (10, 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                (0, 255, 0), 2)
                    self.fps_time = time.time()
                    # cv2.imshow('tf-pose-estimation result', image)
                    height, width, channels = self.image.shape
                    bytes_per_line = channels * width
                    # ---------------------------------------------------------------
                    rgb_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
                    qimage = QImage(rgb_image.data, width, height, bytes_per_line, QImage.Format_RGB888)
                    pixmap = QPixmap.fromImage(qimage)
                    self.image_processed.emit(pixmap)
                    gc.collect()
                else:
                    self.lock.release()  # 注意：这里释放锁可能会导致线程退出循环
                    time.sleep(0.1)  # 等待一小段时间再次检查锁状态
                    continue
        # except ZeroDivisionError:
        #     self.InitialEnvironment()
        #
        # finally:
        #     pass  # todo
        # self.release_camera()

        # self.run()

    def on_signal_list(self):
        """
        使用定时器发射信号
        """
        if self.humans and self.humans != []:
            self.loggerSignal.emit(self.humans)

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
        self.is_paused = False  # 暂停线程的执行
        self.wait()  # 等待线程退出
        self.video_cap.release()  # 清理资源
        self.finished.emit()  # 发出完成信号
        self.deleteLater()

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

    def openpose_model(self):
        """
        打开模型
        """
        self.is_DualSwitch = 'openpose'

    def posenet_model(self):
        """
        切换模型为posenet
        """
        self.is_DualSwitch = 'posenet'


class Cam_MainWindow(QMainWindow):
    """
    测试窗口
    """

    def __init__(self):
        super().__init__()
        self.worker = Worker_carme()
        self.setWindowTitle('openpose实时检测')
        self.btn_camera = QPushButton('打开摄像头')  # 控制摄像头的状态
        self.lbl_img = QLabel('显示摄像头图像')  # 创建标签控件来显示摄像头的图像， 标签的大小由QGridLayout的布局来决定
        self.lbl_img.setStyleSheet('border: 1px solid black;')  # 给标签设置黑色边框
        self.lbl_img.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 让标签要显示的内容居中
        self.set_label_windows()
        self.btn_camera.clicked.connect(self.btn_camera_click)
        top_widget = QWidget()
        grid = QGridLayout()
        grid.addWidget(self.lbl_img, 0, 0, Qt.AlignmentFlag.AlignTop)  # 放置顶部
        grid.addWidget(self.btn_camera, 1, 0, Qt.AlignmentFlag.AlignBottom)  # 放置底部
        top_widget.setLayout(grid)
        self.setCentralWidget(top_widget)
        self.center_win()  # 居中显示主窗口
        self.camera_timer = QTimer(self)
        self.camera_timer.timeout.connect(self.worker.start_run)
        self.camera_timer.setInterval(245)
        self.worker.image_processed.connect(self.update_image)

    def set_label_windows(self):
        """
        设置label标签的大小
        """
        self.window_w, self.window_h = self.get_desktop_size()  # 获取桌面的分辨率
        if self.window_w * 0.6 <= self.worker.width or self.window_h * 0.6 <= self.worker.width:
            self.w, self.h = self.worker.width * 0.5, self.worker.height * 0.5
        else:
            self.w, self.h = self.worker.width, self.worker.height
        self.lbl_img.setMinimumSize(self.w, self.h)  # 宽和高保持和摄像头获取的默认大小一致

    def get_desktop_size(self):
        # 定义获取桌面分辨率的函数
        def get_screen_resolution():
            user32 = ctypes.windll.user32
            screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
            return screensize

        # 获取桌面大小
        self.width, self.height = get_screen_resolution()
        return self.width, self.height

    def center_win(self):
        qr = self.frameGeometry()
        cp = QGuiApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def btn_camera_click(self):
        if self.worker.is_paused:
            # 启动或恢复图像处理
            self.worker.pause()  # 释放锁
            self.btn_camera.setText('恢复摄像头')

        else:
            # 暂停图像处理
            self.worker.resume()  # 获取锁
            self.worker.start()  # 启动线程
            self.btn_camera.setText('暂停摄像头')

    def update_image(self, pixmap):
        if pixmap is not None:
            self.lbl_img.setPixmap(pixmap.scaled(self.lbl_img.size(), Qt.KeepAspectRatio))
            # print("---------------------------------Image received and displayed.----------------------------------")
        else:
            print("No image data to display.")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Cam_MainWindow()
    window.show()
    sys.exit(app.exec())

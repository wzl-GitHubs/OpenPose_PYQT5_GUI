import ctypes
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QGuiApplication, QIcon
from PyQt5.QtWidgets import QMainWindow, QPushButton, QLabel, QWidget, QApplication, QVBoxLayout, QHBoxLayout, \
    QSplitter, QLineEdit, QMessageBox
from run_app.listviow.listviow_cam import Cam_ListView
from run_app.listviow.logging_QWidget import LogWindow
from run_app.listviow.matpltlib_widget import MatplotlibWidget


def get_desktop_size():
    """定义获取桌面分辨率的函数:return:桌面长宽
    :return:
    """
    user32 = ctypes.windll.user32
    screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    width, height = screensize  # 获取桌面大小
    return width, height


class Cam_MainWindow(QMainWindow):
    def __init__(self, ThemeSwitch: bool = False, str_0: str = ''):
        super().__init__()
        self.ThemeSwitch = ThemeSwitch
        # self.worker = Worker_carme()
        self.list_cam_widget = Cam_ListView()
        self.log_widget = LogWindow()  # 创建 LogWindow 实例
        self.Matplotlib_Widget = MatplotlibWidget(data=str_0, title='openpose')  # 创建 MatplotlibWidget 实例
        self.setWindowTitle('openpose实时检测')
        self.btn_camera = QPushButton('打开摄像头')  # 控制摄像头的状态
        self.btn_moldels = QPushButton('关闭模型')
        self.DualSwitch = QPushButton('posenet')
        self.label_txt = QLabel("摄像头")
        self.cam_line_edit = QLineEdit('')
        self.btn_search = QPushButton('搜索')
        self.lbl_img = QLabel('显示摄像头图像')  # 创建标签控件来显示摄像头的图像， 标签的大小由QGridLayout的布局来决定
        self.lbl_img.setStyleSheet('border: 1px solid black;')  # 给标签设置黑色边框
        self.lbl_img.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 让标签要显示的内容居中
        self.set_label_windows()
        self.center_widget = QWidget()
        self.file_widget2 = LogWindow()  # 创建 LogWindow 实例
        self.right_widget = QWidget()

        self.vertical_layout1 = QVBoxLayout()  # 垂直布局
        self.vertical_layout2 = QVBoxLayout()  # 垂直布局
        self.horizontal_layout1 = QHBoxLayout()
        self.horizontal_layout2 = QHBoxLayout()

        self.horizontal_layout1.addWidget(self.label_txt)
        self.horizontal_layout1.addWidget(self.cam_line_edit, 1)
        self.horizontal_layout1.addWidget(self.btn_search)
        self.vertical_layout1.addLayout(self.horizontal_layout1)

        self.horizontal_layout2.addWidget(self.btn_moldels)
        self.horizontal_layout2.addWidget(self.DualSwitch)
        self.vertical_layout1.addLayout(self.horizontal_layout2)
        self.vertical_layout1.addWidget(self.lbl_img)
        self.vertical_layout1.addWidget(self.btn_camera)

        self.vertical_layout2.addWidget(self.log_widget, 2)
        self.vertical_layout2.addWidget(self.Matplotlib_Widget, 1)

        self.center_widget.setLayout(self.vertical_layout1)
        self.right_widget.setLayout(self.vertical_layout2)
        # self.setCentralWidget(self.centre_widget)

        self.splitter = QSplitter()
        self.splitter.addWidget(self.list_cam_widget)
        self.splitter.addWidget(self.center_widget)
        self.splitter.addWidget(self.right_widget)
        self.setCentralWidget(self.splitter)
        self.splitter.setStretchFactor(0, 1)  # 第一个 widget 的初始占比
        self.splitter.setStretchFactor(1, 1)  # 第二个 widget 的初始占比
        self.splitter.setStretchFactor(2, 1)  # 第三个 widget 的初始占比

        self.center_win()  # 居中显示主窗口
        # self.camera_timer = QTimer(self)
        # self.camera_timer.timeout.connect(self.worker.start_run)
        # self.camera_timer.setInterval(245)
        self.list_cam_widget.Cam_Signal.connect(self.input_txt)
        self.btn_search.clicked.connect(self.on_btn_search)
        # self.list_cam_widget.image_processed.connect(self.update_image)
        self.btn_camera.clicked.connect(self.btn_camera_click)
        self.btn_moldels.clicked.connect(self.on_but_models_click)
        self.DualSwitch.clicked.connect(self.on_switch_model)

        self.icon_window = QIcon('../../resources/icon/posewindow.png')
        self.setWindowIcon(self.icon_window)
        if self.ThemeSwitch:
            self.changeSubject()

    def changeSubject(self):
        self.setStyleSheet("""
                   QMainWindow {
                       background-color: #444; /* 深灰色背景 */
                       border-radius: 10px; /* 添加圆角边框 */
                   }
                   QWidget {
                       background-color: #222; /* 深灰色背景 */

                   }
                   QSplitter {
                       background-position: center;
                       background-repeat: no-repeat;
                       background-attachment: scroll; /* 使用 scroll 允许背景滚动 */
                       background-size: cover; /* 使图片覆盖整个分割器区域 */

                   }
                   /* 设置所有控件的文本颜色为白色 */
                   QToolTip, QAbstractButton, QAbstractItemView, QAbstractScrollArea, QAbstractSpinBox,
                   QCalendarWidget, QCheckBox, QComboBox, QDateEdit, QDateTimeEdit, QDial,
                   QDialog, QDockWidget, QFileDialog, QFocusFrame, QFrame, QGroupBox,
                   QLabel, QLayoutWidget, QLineEdit, QListView, QMenuBar, QMdiArea,
                   QMdiSubWindow, QMenu, QMessageBox, QProgressBar, QRadioButton,
                   QScrollBar, QSlider, QSpinBox, QStatusBar, QStyleFactory, QTabBar,
                   QTabWidget, QTextEdit, QToolBar, QToolBox, QToolTip, QTreeView, QTreeView,
                   QListWidget, QScrollBar, QProgressBar, QStackedWidget, QToolBar,
                   QToolButton {
                       color: #ffffff; /* 设置文本颜色为白色 */
                   }
                   /* 设置选中或激活状态下的文本颜色 */
                   QAbstractItemView::item:selected, QAbstractItemView::item:hover {
                       color: #ffffff; /* 选中或悬停时的文本颜色 */
                   }
                   /* 设置一些控件的背景色，以确保它们与白色文本的对比度 */
                   QLineEdit, QTextEdit {
                       background-color: #333; /* 浅灰色背景 */
                   }
                   /* 设置按钮的背景色 */
                   QPushButton {
                       background-color: #555; /* 深灰色按钮背景 */
                   }
                   /* 设置工具栏的背景色 */
                   QToolBar {
                       background-color: #444; /* 深灰色工具栏背景 */
                   }
                   /* 设置菜单的背景色 */
                   QMenu {
                       background-color: #444; /* 深灰色菜单背景 */
                       color: #ffffff; /* 菜单文本颜色 */
                   }
                   /* 设置菜单项的背景色和文本颜色 */
                   QMenu::item:selected {
                       background-color: #555; /* 选中的菜单项背景色 */
                   }
               """)

    # def set_label_windows(self):
    #     """
    #     设置label标签的大小
    #     """
    #     self.window_w, self.window_h = self.get_desktop_size()  # 获取桌面的分辨率
    #     if self.window_w * 0.6 <= self.worker.width or self.window_h * 0.6 <= self.worker.width:
    #         self.w, self.h = self.worker.width * 0.5, self.worker.height * 0.5
    #     else:
    #         self.w, self.h = self.worker.width, self.worker.height
    #     self.lbl_img.setMinimumSize(self.w, self.h)  # 宽和高保持和摄像头获取的默认大小一致

    def set_label_windows(self):
        window_w, window_h = get_desktop_size()
        self.lbl_img.setMinimumSize(window_w * 0.3, window_h * 0.3)

    def center_win(self):
        qr = self.frameGeometry()
        cp = QGuiApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def on_but_models_click(self):
        try:
            if self.list_cam_widget.Worker_carme.is_open_moldes:
                self.list_cam_widget.Worker_carme.is_open_moldes = False
                self.btn_moldels.setText('打开模型')
            else:
                self.list_cam_widget.Worker_carme.is_open_moldes = True
                self.btn_moldels.setText('关闭模型')
        except AttributeError as e:
            QMessageBox.warning(self, "错误", f"请选择摄像头{e}")

    def btn_camera_click(self):
        """
            摄像头开关槽函数
        """
        try:
            if self.list_cam_widget.Worker_carme.is_paused:  # 暂停图像处理
                self.list_cam_widget.Worker_carme.pause()  # 获取锁
                self.btn_camera.setText('恢复摄像头')
                self.list_cam_widget.Worker_carme.loggerSignal.disconnect(self.log_widget.on_update_keypoint)  # 信号解绑
                self.list_cam_widget.Worker_carme.loggerSignal.disconnect(
                    self.Matplotlib_Widget.on_update_radar)  # 信号解绑

            else:  # 启动或恢复图像处理
                self.list_cam_widget.Worker_carme.resume()  # 释放锁
                self.list_cam_widget.Worker_carme.start()  # 启动线程
                self.btn_camera.setText('暂停摄像头')
                self.update_worker()
        except AttributeError:
            QMessageBox.information(self, "错误", "请选择摄像头")
            print("请选择资源")
        except TypeError:
            print("初次打开请忽略")
        except RuntimeError:
            print('窗口放大后的点击事件')

    def on_switch_model(self):
        """
        切换模型的开关
        """
        try:
            if self.list_cam_widget.Worker_carme.is_DualSwitch == 'openpose':
                self.list_cam_widget.Worker_carme.posenet_model()
                self.DualSwitch.setText('openpose')
            else:
                self.list_cam_widget.Worker_carme.openpose_model()
                self.DualSwitch.setText('mediapipe')
        except AttributeError as e:
            QMessageBox.warning(self, "错误", f"请选择摄像头{e}")

    def update_image(self, pixmap):
        if pixmap is not None:
            self.lbl_img.setPixmap(pixmap.scaled(self.lbl_img.size(), Qt.KeepAspectRatio))
        else:
            print("No image data to display.")

    def update_worker(self):
        """更新图像和日志"""
        self.list_cam_widget.Worker_carme.image_processed.connect(self.update_image)
        self.list_cam_widget.Worker_carme.loggerSignal.connect(self.log_widget.on_update_keypoint)
        self.list_cam_widget.Worker_carme.loggerSignal.connect(self.Matplotlib_Widget.on_update_radar)
        self.log_widget.calculate_metrics(self.log_widget.keypoint_info)

    def on_btn_search(self):
        """
        搜索按钮的点击事件
        """
        current_path_str = self.cam_line_edit.text()
        self.list_cam_widget.start_worker(current_path_str)
        # QMessageBox.information(self, "打开摄像头", "摄像头成功加载")

    def input_txt(self, path_str):
        """
        输入框显示文件路径
        :param path_str:文件url
        """
        self.cam_line_edit.clear()  # 清空输入框的内容
        self.cam_line_edit.setText(path_str)  # 将新的文件路径显示在输入框


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Cam_MainWindow()
    window.show()
    sys.exit(app.exec())

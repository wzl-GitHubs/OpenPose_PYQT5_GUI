import ctypes
import logging
import os
import sys
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap, QMouseEvent
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QMainWindow, QHBoxLayout, \
    QVBoxLayout, QLineEdit, QSplitter, QMessageBox, QFrame
from run_app.listviow.listviow_QWidget import FileBrowser
from run_app.listviow.logging_QWidget import LogWindow
from run_app.listviow.matpltlib_widget import MatplotlibWidget


def get_desktop_size():
    """定义获取桌面分辨率的函数:return:桌面长宽"""
    user32 = ctypes.windll.user32
    screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    width, height = screensize  # 获取桌面大小
    return width, height


class Video_MainWindow(QMainWindow):
    clicked = pyqtSignal()
    """
    视频姿态估计窗口类
    """

    def __init__(self, type_list=None, service_url=None, ThemeSwitch: bool = False, str_0: str = ''):
        super().__init__()
        self.ThemeSwitch = ThemeSwitch
        self.root_dir = os.path.split(os.path.abspath(__file__))[0]
        self.logger = logging.getLogger(__name__)
        self.label_doubleclick = True
        self.file_widget = FileBrowser(type_list=type_list, service_url=service_url)  # 创建 FileBrowser 实例
        self.file_widget2 = LogWindow()  # 创建 LogWindow 实例
        self.Matplotlib_Widget = MatplotlibWidget(data=str_0, title='openpose')  # 创建 MatplotlibWidget 实例
        self.ui_init()

        # 资源加载
        self.icon_window = QIcon(os.path.join(self.root_dir, 'resources/posewindow.png'))
        self.file_icon = QIcon(os.path.join(self.root_dir, 'resources/file.png'))
        self.model_icon = QIcon(os.path.join(self.root_dir, 'resources/model.png'))
        self.select_icon = QIcon(os.path.join(self.root_dir, 'resources/select.png'))
        self.btn_bf = QIcon(os.path.join(self.root_dir, 'resources/bofang.png'))  # 播放图标
        self.but_js = QIcon(os.path.join(self.root_dir, 'resources/jieshu.png'))  # 结束图标
        self.lbl_icon = QPixmap(os.path.join(self.root_dir, 'resources/jx.png'))
        self.schedule_icon = QIcon(os.path.join(self.root_dir, 'resources/ziyuanjiazai.png'))
        self.stop_label_icon = QPixmap('../../resources/icon/btn_stop.png')

        self.lbl_img.setPixmap(self.stop_label_icon)

        # 连接信号槽
        self.btn_video.clicked.connect(self.btn_video_click)
        self.file_widget.filepath_Signal.connect(self.input_txt)
        self.btn_search.clicked.connect(self.on_btn_search)
        self.lbl_img.mousePressEvent = self.on_label_clicked
        self.btn_moldels.clicked.connect(self.on_but_models_click)
        self.DualSwitch.clicked.connect(self.on_switch_model)

    def ui_init(self):
        # 创建组件
        self.setWindowTitle('TF 姿态估计')
        self.btn_video = QPushButton('检测视频源')
        self.btn_left = QPushButton('<<')
        self.btn_right = QPushButton('>>')
        self.btn_moldels = QPushButton('关闭模型')
        self.DualSwitch = QPushButton('openpose')
        self.lbl_img = QLabel('显示视频图像')
        self.label_txt = QLabel("数据源")
        self.btn_search = QPushButton('搜索')
        self.video_line_edit = QLineEdit('')
        self.vertical_separator1 = QFrame()  # 水平分割
        self.vertical_separator2 = QFrame()  # 水平分割
        self.Split_v1 = QSplitter(Qt.Vertical)  # 垂直分割
        self.Split_v2 = QSplitter(Qt.Vertical)  # 垂直分割
        self.center_widget = QWidget()
        self.main_widget = QWidget()
        self.right_widget = QWidget()

        # 设置标签
        self.set_label_windows()  # 设置标签大小
        self.lbl_img.setStyleSheet('border: 1px solid black;')  # 给标签设置黑色边框
        self.lbl_img.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 让标签要显示的内容居中

        # 创建布局
        self.vertical_layout1 = QVBoxLayout()  # 垂直布局
        self.vertical_layout2 = QVBoxLayout()  # 垂直布局
        self.horizontal_layout1 = QHBoxLayout()  # 水平布局
        self.horizontal_layout2 = QHBoxLayout()

        # 布局设计
        self.horizontal_layout1.addWidget(self.label_txt)
        self.horizontal_layout1.addWidget(self.video_line_edit, 1)
        self.horizontal_layout1.addWidget(self.btn_search)
        self.vertical_layout1.addLayout(self.horizontal_layout1)

        self.horizontal_layout2.addWidget(self.vertical_separator1)
        # self.horizontal_layout2.addWidget(self.btn_left)
        self.horizontal_layout2.addWidget(self.btn_video)
        # self.horizontal_layout2.addWidget(self.btn_right)
        self.horizontal_layout2.addWidget(self.vertical_separator2, 1)
        self.horizontal_layout2.addWidget(self.btn_moldels)
        self.horizontal_layout2.addWidget(self.DualSwitch)

        self.vertical_layout1.addLayout(self.horizontal_layout2)
        self.vertical_layout1.addWidget(self.lbl_img, 2)

        self.center_widget.setLayout(self.vertical_layout1)

        self.vertical_layout2.addWidget(self.file_widget2, 1)
        self.vertical_layout2.addWidget(self.Matplotlib_Widget, 1)
        self.right_widget.setLayout(self.vertical_layout2)

        # 设置滑动调节窗口组件
        self.splitter = QSplitter()
        self.splitter.addWidget(self.file_widget)
        self.splitter.addWidget(self.center_widget)
        self.splitter.addWidget(self.right_widget)

        self.setCentralWidget(self.splitter)
        self.splitter.setStretchFactor(0, 1)  # 第一个 widget 的初始占比
        self.splitter.setStretchFactor(1, 1)  # 第二个 widget 的初始占比
        self.splitter.setStretchFactor(2, 1)  # 第三个 widget 的初始占比

        # 窗口属性设置
        self.setAcceptDrops(True)
        # self.setWindowOpacity(0.96)  # 80% 的透明度
        self.icon_window = QIcon('../../resources/icon/posewindow.png')
        self.setWindowIcon(self.icon_window)
        # 设置尺寸策略
        # size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # self.splitter.setSizePolicy(size_policy)
        if self.ThemeSwitch:
            self.changeSubject()

    def changeSubject(self):
        self.setStyleSheet("""
                   QMainWindow {
                       /*background-color: #444; 深灰色背景 */
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

    def on_label_clicked(self, event: QMouseEvent):
        """窗口点击事件:param event:"""
        if event.button() == Qt.LeftButton:  # 检查是否是鼠标左键点击lbl_img
            self.btn_video_click()  # 调用btn的槽函数

    def on_label_doubleclick(self, event: QMouseEvent):
        """
        点击窗口Qlable组件的槽函数
        :param event:
        """
        if event.button() == Qt.LeftButton and self.label_doubleclick:
            self.setCentralWidget(self.lbl_img)
            self.label_doubleclick = False
        elif event.button() == Qt.LeftButton and not self.label_doubleclick:
            self.ui_init()
            self.label_doubleclick = True

    def on_btn_search(self):
        """
        搜索按钮的点击事件
        """
        current_path_str = self.video_line_edit.text()
        self.file_widget.start_werker_video(current_path_str)

    def set_label_windows(self):
        """设置标签大小"""
        window_w, window_h = get_desktop_size()
        self.lbl_img.setMinimumSize(window_w * 0.4, window_h * 0.4)

    def btn_video_click(self):
        """
        打开视频处理的按钮事件
        """
        try:
            if self.file_widget.Worker_video.is_paused:  # 启动或恢复图像处理
                self.file_widget.Worker_video.pause()  # 加锁
                self.btn_video.setText('打开')
                self.file_widget.Worker_video.loggerSignal.disconnect(self.file_widget2.on_update_keypoint)  # 信号解绑
                self.file_widget.Worker_video.loggerSignal.disconnect(self.Matplotlib_Widget.on_update_radar)  # 信号解绑
            else:  # 暂停图像处理
                self.file_widget.Worker_video.resume()  # 释放锁
                self.file_widget.Worker_video.start()  # 启动线程
                self.btn_video.setText('暂停')
                self.update_worker()
        except AttributeError:
            QMessageBox.information(self, "错误", "请选择视频文件打开")
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
            if self.file_widget.Worker_video.is_DualSwitch == 'openpose':
                self.file_widget.Worker_video.posenet_model()
                self.DualSwitch.setText('openpose')
            else:
                self.file_widget.Worker_video.openpose_model()
                self.DualSwitch.setText('mediapipe')
        except:
            # QMessageBox.information(self, "错误", "请选择视频文件打开")
            print('初次加载忽略')

    def on_but_models_click(self):
        """
        加载模型
        """
        try:
            if self.file_widget.Worker_video.is_open_models:
                self.file_widget.Worker_video.off_models()
                self.btn_moldels.setText('打开模型')
            else:
                self.file_widget.Worker_video.on_models()
                self.btn_moldels.setText('关闭模型')
        except:
            print('初次加载忽略')

    def update_worker(self):
        """更新图像和日志"""
        self.file_widget.Worker_video.image_processed.connect(self.update_image)
        self.file_widget.Worker_video.loggerSignal.connect(self.file_widget2.on_update_keypoint)
        self.file_widget.Worker_video.loggerSignal.connect(self.Matplotlib_Widget.on_update_radar)
        self.file_widget2.calculate_metrics(self.file_widget2.keypoint_info)

    def update_image(self, pixmap):
        """
        更新图像
        :param pixmap:
        """
        if pixmap is not None:
            self.lbl_img.setPixmap(pixmap.scaled(self.lbl_img.size(), Qt.KeepAspectRatio))
        else:
            print("No image data to display.")

    def dragEnterEvent(self, event):
        # 当文件被拖入窗口时调用
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        # 当文件被拖放到窗口上时调用
        event.acceptProposedAction()
        urls = event.mimeData().urls()
        filepath = urls[0].toLocalFile()
        self.input_txt(filepath)
        self.on_btn_search()

    def input_txt(self, path_str):
        """
        输入框显示文件路径
        :param path_str:文件url
        """
        self.video_line_edit.clear()  # 清空输入框的内容
        self.video_line_edit.setText(path_str)  # 将新的文件路径显示在输入框


if __name__ == '__main__':
    app = QApplication(sys.argv)
    service_url = 'http://47.100.111.106/download_video/'
    video_extensions = ['*.mp4', '*.avi', '*.mkv', '*.mov', '*.wmv', '*.flv', '*.f4v', '*.webm', '*.m4v',
                        '*.ts', '*.mpeg', '*.mpe', '*.mpg', '*.rm', '*.rmvb', '*.vob', '*.m2ts', '*.dts']
    window = Video_MainWindow(type_list=video_extensions, service_url=service_url)
    window.show()
    sys.exit(app.exec())

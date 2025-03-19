import ctypes
import logging
import sys

from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QLabel, QVBoxLayout, QGridLayout, QWidget, QMainWindow, \
    QSplitter, QLineEdit, QPushButton

from run_app.listviow.listviow_QWidget import FileBrowser
from run_app.listviow.logging_QWidget import LogWindow
from run_app.listviow.matpltlib_widget import MatplotlibWidget


class MainWindow(QMainWindow):
    type_list = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.gif', '*.tiff']
    service_url = 'http://47.100.111.106/download_image/'
    file_path = "../../resources/videos"
    WorkerName = 'image'

    def __init__(self, type_list, service_url, file_path="../resources/images/", WorkerName='image',
                 ThemeSwitch: bool = False, str_0: str = ''):
        super().__init__()

        self.ThemeSwitch = ThemeSwitch

        self.file_widget = FileBrowser(type_list=type_list, service_url=service_url, file_path=file_path,
                                       WorkerName=WorkerName)  # 创建 FileBrowser 实例
        self.file_widget2 = LogWindow()  # 创建 LogWindow 实例
        self.Matplotlib_Widget = MatplotlibWidget(data=str_0, title='openpose')  # 创建 MatplotlibWidget 实例
        self.initUI()

        self.time_image = QTimer()
        self.time_image.timeout.connect(self.on_sold_image)
        self.time_image.start(100)
        self.file_widget.filepath_Signal.connect(self.input_txt)
        self.btn_search.clicked.connect(self.on_btn_search)

    @pyqtSlot()
    def initUI(self):
        self.setWindowTitle('图片姿态检测')
        window_w, window_h = self.get_desktop_size()  # 获取桌面的分辨率elf
        window_w, window_h = window_w * 0.4, window_h * 0.8
        window_x, window_y = self.centre_windowd(window_w, window_h)
        self.setGeometry(window_x, window_y, window_w, window_h)

        layout = QGridLayout()  # 创建一个网格布局
        vertical_layout1 = QVBoxLayout()  # 垂直布局
        vertical_layout2 = QVBoxLayout()
        vertical_layout3 = QVBoxLayout()
        vertical_layout4 = QVBoxLayout()
        vertical_layout5 = QVBoxLayout()
        vertical_layout6 = QVBoxLayout()
        vertical_layout7 = QVBoxLayout()
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

        # 创建组件
        self.btn_image = QPushButton('检测图片源')
        self.btn_left = QPushButton('<<')
        self.btn_right = QPushButton('>>')
        self.label_txt = QLabel("数据源")
        self.video_line_edit = QLineEdit('')
        self.btn_search = QPushButton('搜索')
        self.label1_t.setText('原图')
        self.label3_t.setText('Vector-X')
        self.label4_t.setText('Vector-Y')
        self.label5_t.setText('热力图')
        self.label6_t.setText('预测图')

        for label in [
            self.label1_t, self.label3_t, self.label4_t, self.label5_t, self.label6_t,
        ]:
            label.setAlignment(Qt.AlignCenter)  # 设置 QLabel 的对齐方式

        for label in [
            self.label1, self.label3, self.label4, self.label5, self.label6
        ]:
            label.setAlignment(Qt.AlignCenter)  # 设置 QLabel 的对齐方式
            label.setStyleSheet("QLabel { border: 2px solid black; }")
            self.label1.setMinimumSize(216, 184)
        # 将 QLabel 添加到布局中
        vertical_layout1.addWidget(self.label1_t)
        vertical_layout3.addWidget(self.label3_t)
        vertical_layout4.addWidget(self.label4_t)
        vertical_layout5.addWidget(self.label5_t)
        vertical_layout6.addWidget(self.label6_t)

        vertical_layout1.addWidget(self.label1, 1)
        vertical_layout3.addWidget(self.label3, 1)
        vertical_layout4.addWidget(self.label4, 1)
        vertical_layout5.addWidget(self.label5, 1)
        vertical_layout6.addWidget(self.label6, 1)

        layout.addLayout(vertical_layout3, 1, 0)
        layout.addLayout(vertical_layout4, 1, 1)
        layout.addLayout(vertical_layout5, 2, 0)
        layout.addLayout(vertical_layout6, 2, 1)

        # 放置按钮和组件
        horizontal_layout1.addWidget(self.label_txt)
        horizontal_layout1.addWidget(self.video_line_edit, 1)
        horizontal_layout1.addWidget(self.btn_search)
        # horizontal_layout2.addWidget(self.btn_left)
        # horizontal_layout2.addWidget(self.btn_image)
        # horizontal_layout2.addWidget(self.btn_right)

        # 将主窗口组件放入垂直布局
        vertical_layout2.addLayout(horizontal_layout1)
        vertical_layout2.addLayout(horizontal_layout2)
        vertical_layout2.addLayout(vertical_layout1)
        vertical_layout2.addLayout(layout)

        # 创建widget 将vertical_layout2放入central_widget
        self.central_widget = QWidget()
        self.right_widget = QWidget()
        self.central_widget.setLayout(vertical_layout2)
        file_widget = self.file_widget
        file_widget2 = self.file_widget2
        matplotlib_widget3 = self.Matplotlib_Widget

        vertical_layout7.addWidget(file_widget2, 2)
        vertical_layout7.addWidget(matplotlib_widget3, 1)
        self.right_widget.setLayout(vertical_layout7)

        # 设置滑动调节窗口组件，将所有创建widget放入QSplitter
        self.splitter = QSplitter()
        self.splitter.addWidget(file_widget)
        self.splitter.addWidget(self.central_widget)
        self.splitter.addWidget(self.right_widget)
        self.setCentralWidget(self.splitter)

        self.splitter.setStretchFactor(0, 1)  # 第一个 widget 的初始占比
        self.splitter.setStretchFactor(1, 3)  # 第二个 widget 的初始占比
        self.splitter.setStretchFactor(2, 1)  # 第三个 widget 的初始占比

        self.setAcceptDrops(True)  # 支持文件拖动
        self.icon_window = QIcon('../../resources/icon/posewindow.png')
        self.setWindowIcon(self.icon_window)

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

    def dragEnterEvent(self, event):
        # 当文件被拖入窗口时调用
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        event.acceptProposedAction()
        urls = event.mimeData().urls()

        # 检查urls列表是否为空
        if urls:  # 这将检查urls是否非空
            url = urls[0]  # 获取第一个QUrl对象
            if url.scheme() == 'http' or url.scheme() == 'https':  # 检查是否为网络URL
                filepath = url.toString()  # 将QUrl对象转换为字符串
                self.input_txt(filepath)  # 假设这是处理文本输入的方法
                self.on_btn_search()  # 假设这是处理搜索的方法
            else:
                filepath = url.toLocalFile()  # 将QUrl转换为本地文件路径
                if filepath:  # 检查转换是否成功
                    self.input_txt(filepath)
                    self.on_btn_search()
        else:
            print("拖放的数据中没有URL。")

        # 异常处理（如果有的话）
        # 注意：异常处理应该放在可能抛出异常的代码行的周围
        try:
            # 假设这里是可能会抛出异常的代码
            pass
        except Exception as e:
            print(f"发生错误：{e}")

    def on_sold_image(self):
        """
        连接信号,使用定時器啓動
        """
        try:
            self.file_widget.Worker_image.image_loaded1.connect(self.show_image1)
            self.file_widget.Worker_image.image_loaded2.connect(self.show_image2)
            self.file_widget.Worker_image.image_loaded3.connect(self.show_image3)
            self.file_widget.Worker_image.image_loaded4.connect(self.show_image4)
            self.file_widget.Worker_image.image_loaded5.connect(self.show_image5)
            self.file_widget.Worker_image.poseMap_info_list.connect(self.file_widget2.on_update_keypoint)
            self.file_widget.Worker_image.poseMap_info_list.connect(self.Matplotlib_Widget.on_update_radar)
        except AttributeError:
            logging.info('初次加载请忽略')

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

    def on_btn_search(self):
        """
        搜索按钮的点击事件
        """
        current_path_str = self.video_line_edit.text()
        self.file_widget.start_werker_image(current_path_str)

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

    def input_txt(self, path_str):
        """
        输入框显示文件路径
        :param path_str:文件url
        """
        self.video_line_edit.clear()  # 清空输入框的内容
        self.video_line_edit.setText(path_str)  # 将新的文件路径显示在输入框


if __name__ == '__main__':
    type_list = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.gif', '*.tiff']
    service_url = 'http://47.100.111.106/download_image/'
    app = QApplication(sys.argv)
    window = MainWindow(type_list, service_url)
    window.show()
    sys.exit(app.exec())

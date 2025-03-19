import sys
from PyQt5.QtWidgets import QApplication, QWidget, QTextEdit, QVBoxLayout, QMenu, QAction, QMainWindow
from PyQt5.QtGui import QFont


class MarkdownViewer(QMainWindow):
    """
    读取markdown文件的类
    """
    def __init__(self, markdown_file_path, parent=None):

        super().__init__(parent)
        self.markdown_file_path = markdown_file_path
        self.init_ui()
        self.resize(860, 640)
        self.show()

    def init_ui(self):
        # 读取 Markdown 文件内容
        markdown_text = self.read_markdown_file(self.markdown_file_path)

        # 创建 QTextEdit 实例并设置 Markdown
        self.text_edit = QTextEdit(self)
        self.text_edit.setMarkdown(markdown_text)
        self.text_edit.setReadOnly(True)

        # 设置字体大小
        font = QFont()
        font.setPointSize(12)  # 设置字体大小为 12 点
        self.text_edit.setFont(font)

        # 设置样式，包括背景色、文字颜色
        # self.text_edit.setStyleSheet(
        #     "QTextEdit { background-color: black; color: white; }"
        #     "QTextEdit::selection { background-color: darkgray; color: white; }"
        # )
        self.setWindowOpacity(0.9)  # 设置窗口透明度为 80%
        # 创建自定义上下文菜单
        self.create_context_menu()

        # 设置布局
        layout = QVBoxLayout()
        layout.addWidget(self.text_edit)
        self.setCentralWidget(self.text_edit)  # 使用 QMainWindow 的 setCentralWidget

    def create_context_menu(self):
        def context_menu(event):
            self.menu = QMenu(self)
            self.copy_action = QAction('Copy', self.menu)
            self.copy_action.triggered.connect(self.text_edit.copy)
            self.menu.addAction(self.copy_action)
            self.menu.exec_(self.text_edit.mapToGlobal(event.globalPos()))

        # 连接自定义上下文菜单到 QTextEdit 的信号
        self.text_edit.customContextMenuRequested.connect(context_menu)

    @staticmethod
    def read_markdown_file(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()


# 主程序
if __name__ == '__main__':
    app = QApplication(sys.argv)
    markdown_file_path = '../tf-gpu23.md'
    markdown_viewer = MarkdownViewer(markdown_file_path)  # 创建 MarkdownViewer 实例
    sys.exit(app.exec_())

import ctypes
import logging
import sys
from pathlib import Path

# 确保 src/ 在 sys.path 中（直接运行时需要）
_src_dir = Path(__file__).resolve().parent
if str(_src_dir) not in sys.path:
    sys.path.insert(0, str(_src_dir))

# DPI 感知必须在 QApplication 创建之前设置
ctypes.windll.shcore.SetProcessDpiAwareness(2)

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from gui.log_handler import QtLogHandler, QtStreamRedirector, get_log_signal
from gui.main_window import MainWindow


def main() -> None:
    # 配置根日志器
    logging.getLogger().setLevel(logging.INFO)

    app = QApplication(sys.argv)
    app.setApplicationName("NTE Nanally Assistant")

    # 安装日志桥接 — 捕获 logging 输出
    qt_handler = QtLogHandler(level=logging.INFO)
    logging.getLogger().addHandler(qt_handler)

    # 安装 stdout 桥接 — 捕获脚本中的 print() 输出
    stdout_redirector = QtStreamRedirector()
    stdout_redirector.new_text.connect(
        get_log_signal().message, Qt.ConnectionType.QueuedConnection
    )
    sys.stdout = stdout_redirector

    # 日志初始化信息
    logging.getLogger(__name__).info("GUI 启动完成")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

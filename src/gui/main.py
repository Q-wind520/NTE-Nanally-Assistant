import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtQuick import QQuickView

if __name__ == "__main__":
    app = QApplication(sys.argv)                                                # 1.创建一个QApplication类的实例
    view = QQuickView()                                                         # 2.创建QML视图对象
    view.setSource("src/gui/ui.qml")                                                    # 3.加载QML文件 
    view.show()                                                                 # 4.显示QML视图对象
    sys.exit(app.exec())                                                        # 5.进入程序的主循环并通过exit()函数确保主循环安全结束

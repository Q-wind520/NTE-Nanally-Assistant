from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('PyQt5 Test')
        self.setGeometry(100, 100, 300, 200)

        self.button = QPushButton('Click Me', self)
        self.button.setGeometry(100, 80, 100, 30)
        self.button.clicked.connect(self.button_click)

    def button_click(self):
        print('Button clicked!')
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


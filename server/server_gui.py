from PySide2 import QtCore, QtGui, QtWidgets
import server
import sys

HOST = "0.0.0.0"
PORT = 6666
BACKLOG = 10

SW_SHOWNORMAL = 1
SW_SHOWMINIMIZED = 2

class ServerUI(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.serverProgram = server.ServerProgram()

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        event.accept()
        if self.serverProgram.connected:
            self.serverProgram.CloseServer()

    def openServer(self):
        port = int(self.port_box.text())
        self.serverProgram.OpenServer(host=HOST, port=port, backlog=BACKLOG)
        self.serverProgram.Run()

    def closeServer(self):
        self.serverProgram.CloseServer()

    def setupUI(self):
        self.setObjectName("MainWindow")
        self.setFixedSize(250, 100)

        self.WELCOME_label = QtWidgets.QLabel()
        self.WELCOME_label.setGeometry(QtCore.QRect(0, 20, 200, 30))
        font = QtGui.QFont()
        font.setFamily("Helvetica")
        font.setPointSize(24)
        font.setBold(True)
        font.setWeight(70)
        self.WELCOME_label.setFont(font)
        self.WELCOME_label.setStyleSheet("color:rgb(50, 185, 80)")
        self.WELCOME_label.setAlignment(QtCore.Qt.AlignCenter)
        self.WELCOME_label.setObjectName("WELCOME_label")

        self.port_box = QtWidgets.QLineEdit()
        font = QtGui.QFont()
        font.setFamily("Helvetica")
        font.setPointSize(12)
        self.port_box.setFont(font)
        self.port_box.setAlignment(QtCore.Qt.AlignCenter)
        self.port_box.setStyleSheet("background-color: rgb(246, 252, 255);")
        self.port_box.setObjectName("port_box")

        self.open_close_sv_button = QtWidgets.QPushButton(clicked = lambda:self.openServer())
        font = QtGui.QFont()
        font.setFamily("Helvetica")
        font.setPointSize(12)
        self.open_close_sv_button.setFont(font)
        icon = QtGui.QIcon.fromTheme("☺")
        self.open_close_sv_button.setIcon(icon)
        self.open_close_sv_button.setAutoDefault(False)
        self.open_close_sv_button.setStyleSheet("background-color: rgb(246, 252, 255);")
        self.open_close_sv_button.setObjectName("open_close_sv_button")

        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "Server"))
        self.WELCOME_label.setText(_translate("MainWindow", "SERVER"))
        self.open_close_sv_button.setText(_translate("MainWindow", "Mở Server"))
        self.port_box.setText(_translate("MainWindow", "6666"))

        portLayout = QtWidgets.QHBoxLayout() 
        portLayout.addWidget(self.port_box)
        portLayout.addSpacing(10)
        portLayout.addWidget(self.open_close_sv_button)

        tmp = QtWidgets.QWidget(self)
        tmp.setFixedSize(300, 210)
        # tmp.setStyleSheet("background-color: rgb(30, 30, 90)")

        mainLayout = QtWidgets.QVBoxLayout(tmp)
        mainLayout.addWidget(self.WELCOME_label)
        mainLayout.addItem(portLayout)

        self.setLayout(mainLayout)

        QtCore.QMetaObject.connectSlotsByName(self)

if __name__ == "__main__":
    import sys
    from os import environ

    def suppress_qt_warnings():
        environ["QT_DEVICE_PIXEL_RATIO"] = "0"
        environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
        environ["QT_SCREEN_SCALE_FACTORS"] = "1"
        environ["QT_SCALE_FACTOR"] = "1"

    suppress_qt_warnings()

    app = QtWidgets.QApplication(sys.argv)
    ui = ServerUI()
    ui.setupUI()
    ui.show()
    sys.exit(app.exec_())
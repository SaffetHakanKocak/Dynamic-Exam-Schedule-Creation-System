import sys
from PyQt5 import QtWidgets
from app.ui.main_window import MainWindow

def main():
    app = QtWidgets.QApplication(sys.argv)
    with open("app/ui/style.qss", "r") as f:
        app.setStyleSheet(f.read())
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

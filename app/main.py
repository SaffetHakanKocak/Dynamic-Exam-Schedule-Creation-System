# app/main.py
import sys
from PyQt5 import QtWidgets
from app.ui.login_window import LoginWindow
from app.ui.main_window import MainWindow

_main_window = None  # GC'den koru

def on_success(user_dict):
    global _main_window
    _main_window = MainWindow(user_dict)
    _main_window.show()

def main():
    app = QtWidgets.QApplication(sys.argv)
    login = LoginWindow(on_success=on_success)
    login.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()


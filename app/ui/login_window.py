# app/ui/login_window.py
from PyQt5 import QtWidgets, QtCore
from app.services.auth_service import AuthService

class LoginWindow(QtWidgets.QDialog):
    def __init__(self, on_success, parent=None):
        super().__init__(parent)
        self.on_success = on_success
        self.setWindowTitle("Exam Scheduler – Giriş")
        self.setModal(True)
        self.setFixedSize(380, 220)

        # --- Widgets ---
        email_lbl = QtWidgets.QLabel("E-posta")
        self.email_input = QtWidgets.QLineEdit()
        self.email_input.setPlaceholderText("admin@example.com")
        self.email_input.setClearButtonEnabled(True)

        pass_lbl = QtWidgets.QLabel("Şifre")
        self.password_input = QtWidgets.QLineEdit()
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password_input.setPlaceholderText("Şifre")

        self.remember_chk = QtWidgets.QCheckBox("Beni hatırla")  # opsiyonel

        self.login_btn = QtWidgets.QPushButton("Giriş Yap")
        self.login_btn.setDefault(True)
        self.cancel_btn = QtWidgets.QPushButton("İptal")

        # --- Layout ---
        form = QtWidgets.QFormLayout()
        form.addRow(email_lbl, self.email_input)
        form.addRow(pass_lbl, self.password_input)

        btns = QtWidgets.QHBoxLayout()
        btns.addStretch(1)
        btns.addWidget(self.cancel_btn)
        btns.addWidget(self.login_btn)

        root = QtWidgets.QVBoxLayout()
        root.addLayout(form)
        root.addWidget(self.remember_chk)
        root.addStretch(1)
        root.addLayout(btns)
        self.setLayout(root)

        # --- Signals ---
        self.login_btn.clicked.connect(self.do_login)
        self.cancel_btn.clicked.connect(self.reject)
        self.email_input.returnPressed.connect(self.password_input.setFocus)
        self.password_input.returnPressed.connect(self.do_login)

        # Varsayılan odak
        self.email_input.setFocus()

    def do_login(self):
        em = self.email_input.text().strip()
        pw = self.password_input.text()

        if not em or not pw:
            QtWidgets.QMessageBox.warning(self, "Eksik Bilgi", "E-posta ve şifre zorunlu.")
            return

        try:
            user = AuthService.login(em, pw)
            if not user:
                QtWidgets.QMessageBox.warning(self, "Hatalı Giriş", "E-posta veya şifre yanlış.")
                return
            # Ana pencereyi aç, sonra login'i kapat
            self.on_success(user)
            self.accept()
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Bağlantı Hatası",
                f"Giriş sırasında hata oluştu:\n{e}\n\nLütfen .env/DB ayarlarını kontrol edin."
            )

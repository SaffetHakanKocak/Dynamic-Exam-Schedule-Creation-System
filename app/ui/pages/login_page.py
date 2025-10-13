from PyQt5 import QtWidgets, QtGui, QtCore
from app.services.auth_service import AuthService


class LoginPage(QtWidgets.QWidget):
    def __init__(self, on_success):
        super().__init__()
        self.on_success = on_success
        self.setup_ui()

    def setup_ui(self):
        # Ana layout
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Arka plan (soft gradient)
        self.setStyleSheet("""
            QWidget {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #dcefff, stop:1 #f5f8fc
                );
            }
        """)

        # Ekran boyutuna göre kutu
        screen = QtWidgets.QApplication.primaryScreen().availableGeometry()
        w, h = screen.width(), screen.height()
        box_w, box_h = int(w * 0.35), int(h * 0.45)

        # Ana container
        container = QtWidgets.QFrame()
        container.setFixedSize(box_w, box_h)
        container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 20px;
                border: 1px solid #d0d7de;
            }
        """)

        # Gölge efekti
        shadow = QtWidgets.QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setXOffset(0)
        shadow.setYOffset(8)
        shadow.setColor(QtGui.QColor(0, 0, 0, 60))
        container.setGraphicsEffect(shadow)

        vbox = QtWidgets.QVBoxLayout(container)
        vbox.setContentsMargins(40, 40, 40, 40)
        vbox.setSpacing(20)
        vbox.setAlignment(QtCore.Qt.AlignCenter)

        # Başlık
        title = QtWidgets.QLabel("🧾 Sınav Programı Oluşturma Sistemi")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setFont(QtGui.QFont("Segoe UI", int(h * 0.03), QtGui.QFont.Bold))
        title.setStyleSheet("color: #2c3e50;")
        vbox.addWidget(title)

        subtitle = QtWidgets.QLabel("Lütfen e-posta ve şifrenizle giriş yapın")
        subtitle.setAlignment(QtCore.Qt.AlignCenter)
        subtitle.setStyleSheet("color: #7f8c8d; font-size: 11pt;")
        vbox.addWidget(subtitle)

        # E-posta alanı
        self.email = QtWidgets.QLineEdit()
        self.email.setPlaceholderText("E-posta adresi")
        self.email.setFixedHeight(45)
        self.email.setFont(QtGui.QFont("Segoe UI", 11))
        self.email.setStyleSheet("""
            QLineEdit {
                border: 1px solid #bdc3c7;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 11pt;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
            }
        """)

        # Şifre alanı + göster/gizle butonu
        pw_container = QtWidgets.QHBoxLayout()
        pw_container.setContentsMargins(0, 0, 0, 0)
        pw_container.setSpacing(0)

        self.password = QtWidgets.QLineEdit()
        self.password.setPlaceholderText("Şifre")
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password.setFixedHeight(45)
        self.password.setFont(QtGui.QFont("Segoe UI", 11))
        self.password.setStyleSheet("""
            QLineEdit {
                border: 1px solid #bdc3c7;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 11pt;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
            }
        """)

        # 👁 Göster/Gizle butonu
        self.toggle_btn = QtWidgets.QToolButton()
        self.toggle_btn.setText("👁")
        self.toggle_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.toggle_btn.setStyleSheet("""
            QToolButton {
                border: none;
                background: transparent;
                font-size: 14pt;
                padding-right: 8px;
            }
        """)
        self.toggle_btn.clicked.connect(self.toggle_password_visibility)

        pw_container.addWidget(self.password)
        pw_container.addWidget(self.toggle_btn)

        pw_widget = QtWidgets.QWidget()
        pw_widget.setLayout(pw_container)

        # Giriş butonu
        login_btn = QtWidgets.QPushButton("Giriş Yap")
        login_btn.setFixedHeight(50)
        login_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        login_btn.setFont(QtGui.QFont("Segoe UI", 11, QtGui.QFont.Bold))
        login_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 10px;
            }
            QPushButton:hover { background-color: #2980b9; }
        """)
        login_btn.clicked.connect(self.do_login)

        # Form alanı
        form = QtWidgets.QVBoxLayout()
        form.setSpacing(15)
        form.addWidget(self.email)
        form.addWidget(pw_widget)
        form.addWidget(login_btn)
        vbox.addLayout(form)

        # Alt bilgi
        footer = QtWidgets.QLabel("© 2025 Kocaeli Üniversitesi — Yazılım Lab I Projesi")
        footer.setAlignment(QtCore.Qt.AlignCenter)
        footer.setStyleSheet("color: #95a5a6; font-size: 9pt;")
        vbox.addWidget(footer)

        # Ortalamak için hizalama
        wrapper = QtWidgets.QHBoxLayout()
        wrapper.addStretch()
        wrapper.addWidget(container)
        wrapper.addStretch()

        main_layout.addStretch()
        main_layout.addLayout(wrapper)
        main_layout.addStretch()

        # 🔹 ENTER tuşuna basınca login
        self.email.returnPressed.connect(self.do_login)
        self.password.returnPressed.connect(self.do_login)

    # ---------------------------------------------------------------------
    def toggle_password_visibility(self):
        """Şifreyi göster/gizle"""
        if self.password.echoMode() == QtWidgets.QLineEdit.Password:
            self.password.setEchoMode(QtWidgets.QLineEdit.Normal)
            self.toggle_btn.setText("🙈")
        else:
            self.password.setEchoMode(QtWidgets.QLineEdit.Password)
            self.toggle_btn.setText("👁")

    # ---------------------------------------------------------------------
    def do_login(self):
        em = self.email.text().strip()
        pw = self.password.text()

        if not em or not pw:
            QtWidgets.QMessageBox.warning(self, "Eksik Bilgi", "E-posta ve şifre zorunludur.")
            return

        try:
            # 🔹 Login işlemi
            user = AuthService.login(em, pw)
            if not user:
                QtWidgets.QMessageBox.warning(self, "Hatalı Giriş", "E-posta veya şifre yanlış.")
                return

            # 🔹 Departman adını çek (gerekirse)
            if not user.get("department_name") and user.get("department_id"):
                from app.db import fetchone
                row = fetchone("SELECT name FROM departments WHERE id=%s", (user["department_id"],))
                if row:
                    user["department_name"] = row["name"]

            self.on_success(user)

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Hata", f"Giriş başarısız:\n{e}")

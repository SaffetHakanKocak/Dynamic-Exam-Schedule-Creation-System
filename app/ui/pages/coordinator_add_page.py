from PyQt5 import QtWidgets, QtGui, QtCore
from app.repositories.departments import list_all as list_departments
from app.repositories.users_admin import create_coord, email_exists
import bcrypt


class CoordinatorAddPage(QtWidgets.QWidget):
    def __init__(self, go_back, main_window=None):
        super().__init__()
        self.go_back = go_back
        self.main_window = main_window  # ✅ main window referansı
        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)

        # === Üst Bar ===
        header = QtWidgets.QHBoxLayout()
        back_btn = QtWidgets.QPushButton("⬅️ Geri Dön")
        back_btn.setFixedWidth(130)
        back_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 8px;
                font-weight: bold;
                padding: 8px 12px;
            }
            QPushButton:hover { background-color: #2980b9; }
        """)
        back_btn.clicked.connect(self.go_back)
        header.addWidget(back_btn)

        title = QtWidgets.QLabel("🧑‍💼 Yeni Koordinatör Kaydı")
        title.setFont(QtGui.QFont("Segoe UI", 16, QtGui.QFont.Bold))
        title.setAlignment(QtCore.Qt.AlignCenter)
        header.addStretch(1)
        header.addWidget(title)
        header.addStretch(1)
        layout.addLayout(header)

        # === Form Çerçevesi ===
        form_frame = QtWidgets.QFrame()
        form_frame.setStyleSheet("""
            QFrame {
                background-color: #f9fbfd;
                border: 1px solid #d0d7de;
                border-radius: 10px;
                padding: 25px;
            }
        """)
        vform = QtWidgets.QVBoxLayout(form_frame)
        vform.setSpacing(15)

        form = QtWidgets.QFormLayout()
        form.setSpacing(12)

        self.dept_combo = QtWidgets.QComboBox()
        for r in list_departments():
            self.dept_combo.addItem(r["name"], r["id"])

        self.email_input = QtWidgets.QLineEdit()
        self.email_input.setPlaceholderText("ör. coord@bm.kou.edu.tr")

        self.pass1_input = QtWidgets.QLineEdit()
        self.pass1_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.pass1_input.setPlaceholderText("Şifre")

        self.pass2_input = QtWidgets.QLineEdit()
        self.pass2_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.pass2_input.setPlaceholderText("Şifre (tekrar)")

        form.addRow("📘 Bölüm:", self.dept_combo)
        form.addRow("📧 E-posta:", self.email_input)
        form.addRow("🔑 Şifre:", self.pass1_input)
        form.addRow("🔑 Şifre (tekrar):", self.pass2_input)
        vform.addLayout(form)

        # === Mesaj Alanı ===
        self.message_label = QtWidgets.QLabel("")
        self.message_label.setAlignment(QtCore.Qt.AlignCenter)
        self.message_label.setStyleSheet("font-weight:bold;")
        vform.addWidget(self.message_label)

        # === Kaydet / Temizle Butonları ===
        btn_box = QtWidgets.QHBoxLayout()
        btn_save = QtWidgets.QPushButton("💾 Kaydet")
        btn_cancel = QtWidgets.QPushButton("🧹 Temizle")
        btn_box.addStretch(1)
        btn_box.addWidget(btn_cancel)
        btn_box.addWidget(btn_save)
        vform.addLayout(btn_box)

        btn_save.clicked.connect(self.save_coordinator)
        btn_cancel.clicked.connect(self.clear_form)

        layout.addWidget(form_frame)
        layout.addStretch(1)

    # --------------------------------------------------------
    # Koordinatör Kaydetme
    # --------------------------------------------------------
    def save_coordinator(self):
        dept_id = self.dept_combo.currentData()
        email = self.email_input.text().strip().lower()
        p1, p2 = self.pass1_input.text(), self.pass2_input.text()

        if not email or not p1 or not p2:
            return self.show_message("⚠️ Tüm alanlar zorunludur.", "orange")
        if p1 != p2:
            return self.show_message("❌ Şifreler eşleşmiyor.", "red")
        if email_exists(email):
            return self.show_message("⚠️ Bu e-posta zaten kayıtlı.", "orange")

        try:
            pw_hash = bcrypt.hashpw(p1.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            create_coord(email=email, password_hash=pw_hash, department_id=dept_id)

            # Başarılı kayıt mesajı
            self.show_message("✅ Koordinatör başarıyla eklendi.", "green")

            # Formu temizle
            self.clear_form()

            # ✅ Kullanıcı listesi sayfasını otomatik yenile
            if self.main_window and self.main_window.user_list_page:
                self.main_window.user_list_page.load_users()

                # 🔹 Eğer kullanıcı listesi sayfası o anda açık ise anında yenile
                if self.main_window.stack.currentWidget() == self.main_window.user_list_page:
                    self.main_window.user_list_page.load_users()

            # ✅ Mesajı 2 saniye sonra otomatik kaldır
            QtCore.QTimer.singleShot(2000, lambda: self.message_label.clear())

        except Exception as e:
            self.show_message(f"❌ Hata: {str(e)}", "red")

    # --------------------------------------------------------
    # Yardımcılar
    # --------------------------------------------------------
    def clear_form(self):
        self.email_input.clear()
        self.pass1_input.clear()
        self.pass2_input.clear()
        self.message_label.clear()

    def show_message(self, text, color):
        self.message_label.setText(text)
        self.message_label.setStyleSheet(f"color:{color}; font-weight:bold;")

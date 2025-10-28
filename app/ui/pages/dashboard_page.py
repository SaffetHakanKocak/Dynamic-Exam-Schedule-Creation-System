from PyQt5 import QtWidgets, QtGui, QtCore
from app.db import fetchone, fetchall
from app.repositories.departments import list_all as list_departments
from app.repositories.users_admin import create_coord, email_exists
import bcrypt


class DashboardPage(QtWidgets.QWidget):
    def __init__(self, on_navigate, on_logout=None):
        super().__init__()
        self.user = None
        self.on_navigate = on_navigate
        self.on_logout = on_logout
        self.setup_ui()

    # --------------------------------------------------------
    # KULLANICI AYARLAMA (ROL BAZLI PANEL VE MESAJ)
    # --------------------------------------------------------
    def set_user(self, user):
        self.user = user

        role = user["role"].strip().upper()
        email = user.get("email", "")

        # 🎯 Rol bazlı panel başlığı ve hoş geldin mesajı
        if role == "ADMIN":
            panel_title = "👑 ADMİN PANELİ"
            greeting = (
                f"<b>Hoş geldin</b>, <span style='color:#2E86DE'>{email}</span> 👋<br>"
            )
        elif role == "COORD":
            panel_title = "🎓 KOORDİNATÖR PANELİ"
            greeting = (
                f"<b>Merhaba</b>, <span style='color:#27AE60'>{email}</span> 🎓<br>"
            )
        else:
            panel_title = "📋 Kullanıcı Paneli"
            greeting = f"<b>Hoş geldin</b>, <span style='color:#2E86DE'>{email}</span>"

        self.title_label.setText(panel_title)
        self.info_label.setText(greeting)
        self._update_role_visibility()
        self._update_accessibility()

    # --------------------------------------------------------
    # ROL GÖRÜNÜRLÜĞÜ GÜNCELLEME
    # --------------------------------------------------------
    def _update_role_visibility(self):
        """Admin kullanıcıya özel butonları görünür yapar"""
        is_admin = self.user and self.user["role"].strip().upper() == "ADMIN"
        self.btn_addcoord.setVisible(is_admin)
        self.btn_show_users.setVisible(is_admin)

    # --------------------------------------------------------
    # ANA ARAYÜZ
    # --------------------------------------------------------
    def setup_ui(self):
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(50, 40, 50, 20)
        self.layout.setSpacing(20)

        # === Panel Başlığı ===
        self.title_label = QtWidgets.QLabel("📋 Ana Kontrol Paneli")
        self.title_label.setFont(QtGui.QFont("Segoe UI", 20, QtGui.QFont.Bold))
        self.title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.title_label)

        # === Kullanıcı Bilgisi ===
        self.info_label = QtWidgets.QLabel("")
        self.info_label.setAlignment(QtCore.Qt.AlignCenter)
        self.info_label.setFont(QtGui.QFont("Segoe UI", 11))
        self.info_label.setStyleSheet("color: #333;")
        self.layout.addWidget(self.info_label)

        # === ADMIN Koordinatör Ekle Butonu ===
        self.btn_addcoord = self.make_button(
            "🧑‍💼 Koordinatör Ekle", lambda: self.on_navigate("coord_add")
        )
        self.btn_addcoord.setMinimumHeight(50)

        # === ADMIN Kayıtlı Kullanıcıları Görüntüle Butonu ===
        self.btn_show_users = self.make_button(
            "👥 Kayıtlı Kullanıcıları Görüntüle", lambda: self.on_navigate("user_list")
        )
        self.btn_show_users.setMinimumHeight(45)
        self.btn_show_users.hide()  # sadece admin görür

        # === Inline Form ===
        self.addcoord_frame = QtWidgets.QFrame()
        self.addcoord_frame.hide()
        self.addcoord_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dcdde1;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        vform = QtWidgets.QVBoxLayout(self.addcoord_frame)
        vform.setSpacing(12)

        lbl = QtWidgets.QLabel("🧾 Yeni Koordinatör Kaydı")
        lbl.setFont(QtGui.QFont("Segoe UI", 13, QtGui.QFont.Bold))
        vform.addWidget(lbl)

        form = QtWidgets.QFormLayout()
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

        self.message_label = QtWidgets.QLabel("")
        self.message_label.setAlignment(QtCore.Qt.AlignCenter)
        vform.addWidget(self.message_label)

        # Kaydet / Vazgeç Butonları
        btn_box = QtWidgets.QHBoxLayout()
        btn_save = QtWidgets.QPushButton("Kaydet")
        btn_cancel = QtWidgets.QPushButton("Vazgeç")
        btn_box.addStretch(1)
        btn_box.addWidget(btn_cancel)
        btn_box.addWidget(btn_save)
        vform.addLayout(btn_box)

        btn_save.clicked.connect(self.save_coordinator)
        btn_cancel.clicked.connect(self.toggle_addcoord_form)

        # === Arayüze Ekle ===
        self.layout.addWidget(self.btn_addcoord)
        self.layout.addWidget(self.btn_show_users)
        self.layout.addWidget(self.addcoord_frame)

        # === Kullanıcı Listesi Tablosu ===
        self.user_table = QtWidgets.QTableWidget()
        self.user_table.setColumnCount(4)
        self.user_table.setHorizontalHeaderLabels(["ID", "E-posta", "Rol", "Bölüm"])
        self.user_table.horizontalHeader().setStretchLastSection(True)
        self.user_table.setVisible(False)
        self.layout.addWidget(self.user_table)

        # === Diğer Butonlar ===
        self.btn_derslik = self.make_button("🏫 Derslik Girişi", lambda: self.on_navigate("derslik"))
        self.btn_ders = self.make_button("📚 Ders Listesi Yükle", lambda: self.try_open("ders"))
        self.btn_ogr = self.make_button("👨‍🎓 Öğrenci Listesi Yükle", lambda: self.try_open("ogrenci"))
        self.btn_ogr_list = self.make_button("📋 Öğrenci Listesi", lambda: self.on_navigate("ogrenci_listesi"))
        self.btn_ders_list = self.make_button("📘 Ders Listesi", lambda: self.on_navigate("ders_listesi"))
        self.btn_exam = self.make_button("📅 Sınav Programı Oluştur", lambda: self.try_open("exam"))
        self.btn_seating = self.make_button("🪑 Oturma Planı", lambda: self.try_open("seating"))

        self.other_buttons = [
            self.btn_derslik, self.btn_ders, self.btn_ogr,
            self.btn_ogr_list, self.btn_ders_list, self.btn_exam, self.btn_seating
        ]
        for b in self.other_buttons:
            self.layout.addWidget(b)

        # === Uyarı etiketi ===
        self.warning_label = QtWidgets.QLabel("")
        self.warning_label.setAlignment(QtCore.Qt.AlignCenter)
        self.warning_label.setFont(QtGui.QFont("Segoe UI", 10, QtGui.QFont.Bold))
        self.layout.addWidget(self.warning_label)

        self.layout.addStretch(1)

        # === ÇIKIŞ BUTONU ===
        self.logout_btn = QtWidgets.QPushButton("⬅️  Çıkış")
        self.logout_btn.setFixedWidth(120)
        self.logout_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.logout_btn.setFont(QtGui.QFont("Segoe UI", 10))
        self.logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 8px;
                padding: 8px 12px;
            }
            QPushButton:hover { background-color: #c0392b; }
        """)
        self.logout_btn.clicked.connect(self.logout_clicked)

        logout_bar = QtWidgets.QHBoxLayout()
        logout_bar.setAlignment(QtCore.Qt.AlignLeft)
        logout_bar.addWidget(self.logout_btn)
        self.layout.addLayout(logout_bar)

    # --------------------------------------------------------
    # Yardımcılar
    # --------------------------------------------------------
    def make_button(self, text, slot):
        b = QtWidgets.QPushButton(text)
        b.setMinimumHeight(55)
        b.setFont(QtGui.QFont("Segoe UI", 12))
        b.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        b.clicked.connect(slot)
        b.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 10px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #2980b9; }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #6c757d;
            }
        """)
        return b

    # --------------------------------------------------------
    # ERİŞİM KONTROLÜ
    # --------------------------------------------------------
    def has_enough_classrooms(self):
        if not self.user or self.user["role"].strip().upper() == "ADMIN":
            return True
        row = fetchone("SELECT COUNT(*) AS cnt FROM classrooms WHERE department_id = %s",
                       (self.user["department_id"],))
        return row and row["cnt"] >= 5

    def has_courses_loaded(self):
        row = fetchone("SELECT COUNT(*) AS cnt FROM courses WHERE department_id = %s",
                       (self.user["department_id"],))
        return row and row["cnt"] > 0

    def has_students_loaded(self):
        row = fetchone("SELECT COUNT(*) AS cnt FROM student_course_summary WHERE department_id = %s",
                       (self.user["department_id"],))
        return row and row["cnt"] > 0

    def _update_accessibility(self):
        enough_cls = self.has_enough_classrooms()
        courses_loaded = self.has_courses_loaded()
        students_loaded = self.has_students_loaded()
        is_admin = self.user and self.user["role"].strip().upper() == "ADMIN"

        if is_admin:
            for b in [self.btn_ders, self.btn_ogr, self.btn_ogr_list,
                      self.btn_ders_list, self.btn_exam, self.btn_seating]:
                b.setEnabled(True)
            self.warning_label.clear()
            return

        # 1️⃣ Derslik 5'ten azsa hiçbir şey aktif değil
        if not enough_cls:
            for b in [self.btn_ders, self.btn_ogr, self.btn_ogr_list,
                      self.btn_ders_list, self.btn_exam, self.btn_seating]:
                b.setEnabled(False)
            self.warning_label.setText("⚠️ En az 5 derslik girişi tamamlanmadan işlem yapılamaz.")
            self.warning_label.setStyleSheet("color: orange;")
            return

        # 2️⃣ Derslik tamam ama Excel’ler yüklenmediyse sadece upload aktif
        if enough_cls and not (courses_loaded and students_loaded):
            self.btn_ders.setEnabled(True)
            self.btn_ogr.setEnabled(True)
            for b in [self.btn_ogr_list, self.btn_ders_list, self.btn_exam, self.btn_seating]:
                b.setEnabled(False)
            self.warning_label.setText("📚 Lütfen ders ve öğrenci listelerini yükleyin.")
            self.warning_label.setStyleSheet("color: orange;")
            return

        # 3️⃣ Her şey tamam — tüm butonlar aktif
        for b in [self.btn_ders, self.btn_ogr, self.btn_ogr_list,
                  self.btn_ders_list, self.btn_exam, self.btn_seating]:
            b.setEnabled(True)
        self.warning_label.clear()

    def try_open(self, page_name):
        if not self.has_enough_classrooms() and self.user["role"].strip().upper() != "ADMIN":
            self.show_message("⚠️ En az 5 derslik girişi tamamlanmadan geçilemez.", "orange")
            return
        self.on_navigate(page_name)

    # --------------------------------------------------------
    # KOORDİNATÖR KAYDI
    # --------------------------------------------------------
    def toggle_addcoord_form(self):
        if self.addcoord_frame.isVisible():
            self.addcoord_frame.hide()
        else:
            self.addcoord_frame.show()

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
            self.show_message("✅ Koordinatör başarıyla eklendi.", "green")
            self.load_users()
        except Exception as e:
            self.show_message(f"❌ Hata: {str(e)}", "red")

    def show_message(self, text, color):
        self.message_label.setText(text)
        self.message_label.setStyleSheet(f"color:{color}; font-weight:bold;")

    # --------------------------------------------------------
    # ÇIKIŞ
    # --------------------------------------------------------
    def logout_clicked(self):
        if self.on_logout:
            self.on_logout()

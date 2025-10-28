from PyQt5 import QtWidgets, QtGui, QtCore
from app.services.student_course_summary_service import StudentCourseSummaryService


class StudentListPage(QtWidgets.QWidget):
    def __init__(self, user, go_back):
        super().__init__()
        self.user = user  # ✅ Kullanıcı bilgisi eklendi (admin/koord ayrımı için)
        self.go_back = go_back
        self.service = StudentCourseSummaryService()
        self.init_ui()

    # --------------------------------------------------------
    # UI OLUŞTURMA
    # --------------------------------------------------------
    def init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # ÜST BAR
        header = QtWidgets.QHBoxLayout()
        header.setSpacing(20)
        back_btn = QtWidgets.QPushButton("⬅️ Geri Dön")
        back_btn.setFixedWidth(150)
        back_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover { background-color: #2980b9; }
        """)
        back_btn.clicked.connect(self.go_back)

        title = QtWidgets.QLabel("🎓 Öğrenci Ders Listesi Görüntüleme")
        title.setFont(QtGui.QFont("Segoe UI", 20, QtGui.QFont.Bold))
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50;")

        header.addWidget(back_btn)
        header.addStretch()
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)

        # Arama kutusu
        search_layout = QtWidgets.QHBoxLayout()
        search_layout.setSpacing(10)
        self.search_box = QtWidgets.QLineEdit()
        self.search_box.setPlaceholderText("Öğrenci numarasını giriniz...")
        self.search_box.setFixedHeight(40)
        self.search_box.setFont(QtGui.QFont("Segoe UI", 11))
        self.search_btn = QtWidgets.QPushButton("🔍 Ara")
        self.search_btn.setFixedWidth(120)
        self.search_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.search_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
                border-radius: 8px;
            }
            QPushButton:hover { background-color: #1e8449; }
        """)
        self.search_btn.clicked.connect(self.search_student)
        search_layout.addWidget(self.search_box)
        search_layout.addWidget(self.search_btn)
        layout.addLayout(search_layout)

        # Sonuç alanı
        self.result_label = QtWidgets.QLabel("")
        self.result_label.setFont(QtGui.QFont("Segoe UI", 13, QtGui.QFont.Bold))
        self.result_label.setAlignment(QtCore.Qt.AlignLeft)
        layout.addWidget(self.result_label)

        # Tablo
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Dersin Kodu", "Aldığı Ders"])
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                alternate-background-color: #f4f7fb;
                border: 1px solid #d0d7de;
                gridline-color: #d0d7de;
            }
            QHeaderView::section {
                background-color: #e8eef6;
                font-weight: bold;
                padding: 6px;
                border: none;
            }
        """)
        layout.addWidget(self.table, stretch=1)

    # --------------------------------------------------------
    # ÖĞRENCİ ARAMA (Admin / Koordinatör Ayrımı)
    # --------------------------------------------------------
    def search_student(self):
        number = self.search_box.text().strip()
        if not number:
            QtWidgets.QMessageBox.warning(self, "Uyarı", "Lütfen öğrenci numarası girin.")
            return

        try:
            # ✅ Admin tüm bölümleri görebilir, koordinatör sadece kendi bölümünü
            role = self.user.get("role", "").strip().upper()
            if role == "ADMIN":
                results = self.service.get_by_student_number(number)
            else:
                dept_id = self.user.get("department_id")
                results = self.service.get_by_student_number(number, dept_id)

            # Sonuç yoksa
            if not results:
                self.result_label.setText(f"❌ {number} numaralı öğrenci bulunamadı veya erişim yetkiniz yok.")
                self.result_label.setStyleSheet("color: red; font-weight:bold;")
                self.table.setRowCount(0)
                return

            # Sonuç varsa tabloyu doldur
            name = results[0]["Ad Soyad"]
            self.result_label.setText(f"👤 Öğrenci: <b>{name}</b>  |  🎓 Aldığı Dersler:")
            self.result_label.setStyleSheet("color: #2c3e50; font-weight:bold;")

            self.table.setRowCount(len(results))
            for i, r in enumerate(results):
                self.table.setItem(i, 0, QtWidgets.QTableWidgetItem(r["Dersin Kodu"]))
                self.table.setItem(i, 1, QtWidgets.QTableWidgetItem(r["Aldığı Ders"]))

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Hata", f"Arama başarısız:\n{e}")
            print("🟥 Öğrenci sorgu hatası:", e)

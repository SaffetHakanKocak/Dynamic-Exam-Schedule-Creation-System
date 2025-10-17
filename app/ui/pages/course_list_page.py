from PyQt5 import QtWidgets, QtGui, QtCore
from app.services.student_course_summary_service import StudentCourseSummaryService


class CourseListPage(QtWidgets.QWidget):
    def __init__(self, go_back):
        super().__init__()
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

        # Üst bar
        header = QtWidgets.QHBoxLayout()
        back_btn = QtWidgets.QPushButton("⬅️ Geri Dön")
        back_btn.setFixedWidth(150)
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

        title = QtWidgets.QLabel("📘 Ders Listesi ve Öğrenci Görüntüleme")
        title.setFont(QtGui.QFont("Segoe UI", 20, QtGui.QFont.Bold))
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50;")

        header.addWidget(back_btn)
        header.addStretch()
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)

        # Bölmeli yapı
        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        splitter.setHandleWidth(5)

        # Sol panel (Dersler)
        self.course_list = QtWidgets.QListWidget()
        self.course_list.setStyleSheet("""
            QListWidget {
                background-color: #ffffff;
                border: 1px solid #d0d7de;
                font-size: 11pt;
            }
            QListWidget::item:selected {
                background-color: #a7c7f9;
                color: black;
                font-weight: bold;
            }
        """)
        self.course_list.itemClicked.connect(self.show_students)

        # Sağ panel (Öğrenciler)
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Öğrenci No", "Ad Soyad"])
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
                border: none;
                padding: 6px;
            }
        """)

        splitter.addWidget(self.course_list)
        splitter.addWidget(self.table)
        splitter.setSizes([350, 900])  # Sol panel küçük, sağ panel geniş
        layout.addWidget(splitter, stretch=1)

        # Alt durum çubuğu
        self.status_label = QtWidgets.QLabel("📚 Dersler yükleniyor...")
        self.status_label.setAlignment(QtCore.Qt.AlignCenter)
        self.status_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        layout.addWidget(self.status_label)

        # Sayfa açıldığında dersleri yükle
        self.load_courses()

    # --------------------------------------------------------
    # 🆕 SAYFA GÖSTERİLDİĞİNDE OTOMATİK YENİLEME
    # --------------------------------------------------------
    def showEvent(self, event):
        """Sayfa her görüntülendiğinde ders listesini otomatik yeniler."""
        super().showEvent(event)
        self.load_courses()

    # --------------------------------------------------------
    # DERSLERİ YÜKLEME
    # --------------------------------------------------------
    def load_courses(self):
        """Tüm dersleri sol listeye yükler."""
        try:
            courses = self.service.list_all_courses()
            self.course_list.clear()

            if not courses:
                self.status_label.setText("⚠️ Hiç ders bulunamadı. Öğrenci listesini tekrar yükleyin.")
                self.status_label.setStyleSheet("color: orange; font-weight: bold;")
                return

            for c in courses:
                ders_kodu = c.get("Dersin Kodu", "")
                ders_adi = c.get("Aldığı Ders", "")
                item = QtWidgets.QListWidgetItem(f"{ders_kodu} — {ders_adi}")
                item.setData(QtCore.Qt.UserRole, ders_kodu)
                self.course_list.addItem(item)

            self.status_label.setText(f"✅ {len(courses)} ders yüklendi.")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")

        except Exception as e:
            self.status_label.setText(f"❌ Dersler yüklenemedi: {e}")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
            print("🟥 Hata detay:", e)

    # --------------------------------------------------------
    # SEÇİLEN DERSİN ÖĞRENCİLERİNİ GÖSTER
    # --------------------------------------------------------
    def show_students(self, item):
        """Listeden bir ders seçildiğinde o dersi alan öğrencileri getirir."""
        code = item.data(QtCore.Qt.UserRole)
        try:
            students = self.service.get_by_course_code(code)
            self.table.setRowCount(len(students))

            if not students:
                self.status_label.setText(f"⚠️ {code} kodlu dersi alan öğrenci bulunamadı.")
                self.status_label.setStyleSheet("color: orange; font-weight: bold;")
                return

            for i, s in enumerate(students):
                self.table.setItem(i, 0, QtWidgets.QTableWidgetItem(s["Öğrenci No"]))
                self.table.setItem(i, 1, QtWidgets.QTableWidgetItem(s["Ad Soyad"]))

            self.status_label.setText(f"📖 {code} kodlu dersi alan {len(students)} öğrenci listelendi.")
            self.status_label.setStyleSheet("color: #2c3e50; font-weight: bold;")

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Hata", f"Öğrenciler getirilemedi:\n{e}")
            print("🟥 Öğrenci sorgu hatası:", e)

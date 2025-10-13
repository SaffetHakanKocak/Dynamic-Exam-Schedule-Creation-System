from PyQt5 import QtWidgets, QtGui, QtCore
from app.services.exam_scheduler_service import ExamSchedulerService
from app.db import fetchall
import tempfile, os


class ExamSchedulerPage(QtWidgets.QWidget):
    def __init__(self, user, go_back):
        super().__init__()
        self.user = user
        self.go_back = go_back
        self.service = ExamSchedulerService()
        self.generated_plan = []

        # Ana kaydırılabilir yapı
        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.container = QtWidgets.QWidget()
        self.scroll.setWidget(self.container)

        self.layout = QtWidgets.QVBoxLayout(self.container)
        self.layout.setContentsMargins(40, 25, 40, 25)
        self.layout.setSpacing(20)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.scroll)

        self._init_ui()
        self._load_courses()

    # ------------------------------------------------------------
    def _init_ui(self):
        # === Üst Başlık ===
        title = QtWidgets.QLabel("🧾 Sınav Programı Oluşturma Sistemi")
        title.setFont(QtGui.QFont("Segoe UI", 18, QtGui.QFont.Bold))
        title.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(title)

        # === Kullanıcı Bilgisi ===
        info_bar = QtWidgets.QFrame()
        info_bar.setStyleSheet("""
            QFrame {
                background-color: #ecf4ff;
                border: 1px solid #c7d9f1;
                border-radius: 8px;
                padding: 10px 15px;
            }
        """)
        hinfo = QtWidgets.QHBoxLayout(info_bar)
        lbl_user = QtWidgets.QLabel(f"👤 {self.user['email']}  —  🏛 {self.user.get('department_name', 'Bilinmeyen Bölüm')}")
        lbl_user.setFont(QtGui.QFont("Segoe UI", 10))
        lbl_user.setStyleSheet("color: #2c3e50; font-weight: bold;")
        hinfo.addWidget(lbl_user)
        hinfo.addStretch(1)
        self.layout.addWidget(info_bar)

        # === Geri Dön ===
        back_btn = QtWidgets.QPushButton("⬅️ Geri Dön")
        back_btn.setFixedWidth(130)
        back_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        back_btn.clicked.connect(self.go_back)
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
        self.layout.addWidget(back_btn, alignment=QtCore.Qt.AlignLeft)

        # === Ana Form Çerçevesi ===
        frame = QtWidgets.QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #f9fbfd;
                border: 1px solid #d0d7de;
                border-radius: 12px;
                padding: 25px;
            }
        """)
        vbox = QtWidgets.QVBoxLayout(frame)
        vbox.setSpacing(25)

        # --------------------------------------------------------
        # 1️⃣ Ders Seçimi
        # --------------------------------------------------------
        lbl1 = QtWidgets.QLabel("1️⃣ Ders Seçimi — Program dışı bırakılacak dersleri seçin")
        lbl1.setFont(QtGui.QFont("Segoe UI", 11, QtGui.QFont.Bold))
        vbox.addWidget(lbl1)

        self.course_list = QtWidgets.QListWidget()
        self.course_list.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.course_list.setMinimumHeight(250)
        self.course_list.setStyleSheet("""
            QListWidget {
                background-color: white;
                border: 1px solid #ccd3dc;
                border-radius: 6px;
                font-size: 11pt;
            }
            QListWidget::item:selected {
                background-color: #a7c7f9;
                color: black;
                font-weight: bold;
            }
        """)
        vbox.addWidget(self.course_list)

        # 🔹 Ders bazlı özel süreler
        lbl2 = QtWidgets.QLabel("⏱ Ders Bazlı Özel Süreler (boş bırakılanlar varsayılan alınır):")
        lbl2.setFont(QtGui.QFont("Segoe UI", 10))
        vbox.addWidget(lbl2)

        self.custom_duration_table = QtWidgets.QTableWidget()
        self.custom_duration_table.setColumnCount(2)
        self.custom_duration_table.setHorizontalHeaderLabels(["Ders Kodu", "Süre (dk)"])
        self.custom_duration_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        vbox.addWidget(self.custom_duration_table)

        # --------------------------------------------------------
        # 2️⃣ Tarih Aralığı ve Tatil Günleri
        # --------------------------------------------------------
        lbl3 = QtWidgets.QLabel("2️⃣ Sınav Tarihleri ve Tatil Günleri")
        lbl3.setFont(QtGui.QFont("Segoe UI", 11, QtGui.QFont.Bold))
        vbox.addWidget(lbl3)

        date_layout = QtWidgets.QHBoxLayout()
        date_layout.addWidget(QtWidgets.QLabel("📅 Tarih Aralığı:"))
        self.start_date = QtWidgets.QDateEdit(QtCore.QDate.currentDate())
        self.start_date.setCalendarPopup(True)
        self.start_date.setDisplayFormat("dd.MM.yyyy")
        self.end_date = QtWidgets.QDateEdit(QtCore.QDate.currentDate().addDays(7))
        self.end_date.setCalendarPopup(True)
        self.end_date.setDisplayFormat("dd.MM.yyyy")

        date_layout.addWidget(self.start_date)
        date_layout.addWidget(QtWidgets.QLabel("—"))
        date_layout.addWidget(self.end_date)
        date_layout.addStretch(1)
        vbox.addLayout(date_layout)

        hol_layout = QtWidgets.QHBoxLayout()
        hol_layout.addWidget(QtWidgets.QLabel("🚫 Tatil Günleri:"))
        self.chk_sat = QtWidgets.QCheckBox("Cumartesi")
        self.chk_sun = QtWidgets.QCheckBox("Pazar")
        hol_layout.addWidget(self.chk_sat)
        hol_layout.addWidget(self.chk_sun)
        hol_layout.addStretch(1)
        vbox.addLayout(hol_layout)

        # --------------------------------------------------------
        # 3️⃣ Sınav Türü
        # --------------------------------------------------------
        lbl4 = QtWidgets.QLabel("3️⃣ Sınav Türü")
        lbl4.setFont(QtGui.QFont("Segoe UI", 11, QtGui.QFont.Bold))
        vbox.addWidget(lbl4)

        self.exam_type = QtWidgets.QComboBox()
        self.exam_type.addItems(["VIZE", "FINAL", "BUTUNLEME"])
        self.exam_type.setFixedWidth(200)
        vbox.addWidget(self.exam_type)

        # --------------------------------------------------------
        # 4️⃣ Süre ve Bekleme
        # --------------------------------------------------------
        lbl5 = QtWidgets.QLabel("4️⃣ Süre ve Bekleme Süresi")
        lbl5.setFont(QtGui.QFont("Segoe UI", 11, QtGui.QFont.Bold))
        vbox.addWidget(lbl5)

        s_layout = QtWidgets.QHBoxLayout()
        s_layout.addWidget(QtWidgets.QLabel("⏱ Varsayılan Süre (dk):"))
        self.spin_duration = QtWidgets.QSpinBox()
        self.spin_duration.setRange(30, 240)
        self.spin_duration.setValue(75)
        s_layout.addWidget(self.spin_duration)

        s_layout.addWidget(QtWidgets.QLabel("🕓 Bekleme (dk):"))
        self.spin_gap = QtWidgets.QSpinBox()
        self.spin_gap.setRange(5, 60)
        self.spin_gap.setValue(15)
        s_layout.addWidget(self.spin_gap)
        s_layout.addStretch(1)
        vbox.addLayout(s_layout)

        # --------------------------------------------------------
        # 5️⃣ Çakışma Engeli
        # --------------------------------------------------------
        lbl6 = QtWidgets.QLabel("5️⃣ Sınavların Aynı Zamana Denk Gelmemesi")
        lbl6.setFont(QtGui.QFont("Segoe UI", 11, QtGui.QFont.Bold))
        vbox.addWidget(lbl6)
        self.chk_no_overlap = QtWidgets.QCheckBox("Hiçbir sınav aynı anda olmasın (öğrenci çakışması engeli)")
        self.chk_no_overlap.setChecked(True)
        vbox.addWidget(self.chk_no_overlap)

        # --------------------------------------------------------
        # Butonlar
        # --------------------------------------------------------
        btn_layout = QtWidgets.QHBoxLayout()
        self.btn_generate = QtWidgets.QPushButton("📅 Programı Oluştur")
        self.btn_generate.setMinimumHeight(45)
        self.btn_generate.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #219150; }
        """)
        self.btn_generate.clicked.connect(self._on_generate_clicked)
        btn_layout.addWidget(self.btn_generate)

        self.btn_export = QtWidgets.QPushButton("💾 Excel Olarak Kaydet")
        self.btn_export.setMinimumHeight(45)
        self.btn_export.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #e67e22; }
        """)
        self.btn_export.clicked.connect(self._on_export_clicked)
        btn_layout.addWidget(self.btn_export)
        vbox.addLayout(btn_layout)

        # --------------------------------------------------------
        # Çıktı Alanı
        # --------------------------------------------------------
        self.output_box = QtWidgets.QTextEdit()
        self.output_box.setReadOnly(True)
        self.output_box.setPlaceholderText("Oluşturulan sınav planı burada görüntülenecek...")
        self.output_box.setMinimumHeight(180)
        self.output_box.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 1px solid #ccd3dc;
                border-radius: 6px;
                padding: 8px;
            }
        """)
        vbox.addWidget(self.output_box)

        # Frame ekle
        self.layout.addWidget(frame)
        self.layout.addStretch(1)

    # ------------------------------------------------------------
    def _load_courses(self):
        try:
            rows = fetchall("""
                SELECT code, name FROM courses
                WHERE department_id = %s
                ORDER BY code
            """, (self.user["department_id"],))
            self.course_list.clear()
            self.custom_duration_table.setRowCount(len(rows))
            for idx, r in enumerate(rows):
                self.course_list.addItem(f"{r['code']} — {r['name']}")
                self.custom_duration_table.setItem(idx, 0, QtWidgets.QTableWidgetItem(r['code']))
                spin = QtWidgets.QSpinBox()
                spin.setRange(30, 240)
                spin.setValue(75)
                self.custom_duration_table.setCellWidget(idx, 1, spin)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Hata", f"Ders listesi yüklenemedi:\n{e}")

    # ------------------------------------------------------------
    def _on_generate_clicked(self):
        # Hariç tutulacak dersleri al
        all_items = [self.course_list.item(i) for i in range(self.course_list.count())]
        all_courses = [it.text().split("—")[0].strip() for it in all_items]
        excluded = [i.text().split("—")[0].strip() for i in self.course_list.selectedItems()]
        included_courses = [c for c in all_courses if c not in excluded]

        # Tarihler
        start_date = self.start_date.date().toString("dd.MM.yyyy")
        end_date = self.end_date.date().toString("dd.MM.yyyy")
        holidays = []
        if self.chk_sat.isChecked(): holidays.append("SAT")
        if self.chk_sun.isChecked(): holidays.append("SUN")

        # Tür & süre
        exam_type = self.exam_type.currentText()
        default_duration = self.spin_duration.value()
        gap_duration = self.spin_gap.value()
        no_overlap = self.chk_no_overlap.isChecked()

        # Ders bazlı özel süreler
        custom_durations = {}
        for row in range(self.custom_duration_table.rowCount()):
            code_item = self.custom_duration_table.item(row, 0)
            widget = self.custom_duration_table.cellWidget(row, 1)
            if not code_item:
                continue
            code = code_item.text().strip()
            val = widget.value() if widget else default_duration
            if val != default_duration:
                custom_durations[code] = val

        # Program oluştur
        plan = self.service.generate_schedule(
            department_id=self.user["department_id"],
            included_courses=included_courses,
            start_date=start_date,
            end_date=end_date,
            holidays=holidays,
            exam_type=exam_type,
            default_duration=default_duration,
            gap_duration=gap_duration,
            no_overlap=no_overlap,
            custom_durations=custom_durations
        )

        if self.service.errors:
            QtWidgets.QMessageBox.critical(self, "Hata",
                "Sınav programı oluşturulamadı:\n" + "\n".join(self.service.errors))
            return

        self.generated_plan = plan
        self.output_box.clear()
        for row in plan:
            line = f"{row['Tarih']} | {row['Saat']} | {row['Ders']} | {row['Derslikler']} | {row['Tür']} | {row['Süre (dk)']} dk"
            self.output_box.append(line)

        QtWidgets.QMessageBox.information(self, "Başarılı", "Sınav programı başarıyla oluşturuldu!")

    # ------------------------------------------------------------
    def _on_export_clicked(self):
        if not self.generated_plan:
            QtWidgets.QMessageBox.warning(self, "Uyarı", "Henüz bir sınav programı oluşturulmadı!")
            return

        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Excel olarak kaydet",
            os.path.join(tempfile.gettempdir(), "sinav_programi.xlsx"),
            "Excel Dosyası (*.xlsx)"
        )
        if not filename:
            return

        try:
            self.service.export_to_excel(self.generated_plan, filename)
            QtWidgets.QMessageBox.information(self, "Başarılı", f"Excel dosyası kaydedildi:\n{filename}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Hata", f"Excel kaydedilemedi:\n{e}")

from PyQt5 import QtWidgets, QtGui, QtCore
from app.services.classroom_service import ClassroomService
from app.repositories.departments import list_all as list_departments


class ClassroomPage(QtWidgets.QWidget):
    classroom_added = QtCore.pyqtSignal()  # ✅ Derslik eklendi/güncellendi/silindi sinyali

    def __init__(self, user, go_back):
        super().__init__()
        self.user = user
        self.go_back = go_back
        self.service = ClassroomService()
        self.setup_ui()

    # --------------------------------------------------------
    # UI OLUŞTURMA
    # --------------------------------------------------------
    def setup_ui(self):
        # === Ana Scrollable yapı ===
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        container = QtWidgets.QWidget()
        scroll.setWidget(container)
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(scroll)

        layout = QtWidgets.QVBoxLayout(container)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(25)

        # ÜST KISIM (Başlık + Geri)
        header_layout = QtWidgets.QHBoxLayout()
        back_btn = QtWidgets.QPushButton("⬅️ Geri Dön")
        back_btn.setFixedWidth(130)
        back_btn.clicked.connect(self.go_back)
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

        title = QtWidgets.QLabel("🏫 Derslik Giriş Ekranı")
        title.setFont(QtGui.QFont("Segoe UI", 18, QtGui.QFont.Bold))
        title.setAlignment(QtCore.Qt.AlignCenter)

        header_layout.addWidget(back_btn)
        header_layout.addStretch()
        header_layout.addWidget(title)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # 🔹 Admin için bölüm filtreleme
        if self.user["role"].upper() == "ADMIN":
            filter_layout = QtWidgets.QHBoxLayout()
            filter_label = QtWidgets.QLabel("📘 Bölüm Filtrele:")
            filter_label.setFont(QtGui.QFont("Segoe UI", 10, QtGui.QFont.Bold))
            self.filter_combo = QtWidgets.QComboBox()
            self.filter_combo.addItem("Tüm Bölümler", None)
            for r in list_departments():
                self.filter_combo.addItem(r["name"], r["id"])
            self.filter_combo.currentIndexChanged.connect(self.load_classrooms)
            filter_layout.addWidget(filter_label)
            filter_layout.addWidget(self.filter_combo)
            layout.addLayout(filter_layout)

        # FORM ALANI
        form_box = QtWidgets.QGroupBox("📋 Derslik Bilgileri")
        form_layout = QtWidgets.QFormLayout(form_box)
        form_layout.setLabelAlignment(QtCore.Qt.AlignRight)
        form_layout.setFormAlignment(QtCore.Qt.AlignLeft)
        form_layout.setHorizontalSpacing(25)
        form_layout.setVerticalSpacing(10)

        self.dept_combo = QtWidgets.QComboBox()
        for r in list_departments():
            self.dept_combo.addItem(r["name"], r["id"])
        if self.user["role"].upper() != "ADMIN":
            self.dept_combo.hide()

        self.dept_name = QtWidgets.QLineEdit()
        self.dept_name.setPlaceholderText("ör: Bilgisayar Mühendisliği")

        self.code_input = QtWidgets.QLineEdit()
        self.name_input = QtWidgets.QLineEdit()
        self.rows_input = QtWidgets.QSpinBox(); self.rows_input.setRange(1, 100)
        self.cols_input = QtWidgets.QSpinBox(); self.cols_input.setRange(1, 100)
        self.group_combo = QtWidgets.QComboBox()
        self.group_combo.addItems(["2", "3", "4"])

        # ✅ Yeni kapasite alanı
        self.capacity_input = QtWidgets.QSpinBox()
        self.capacity_input.setRange(1, 1000)
        self.capacity_input.setSuffix(" kişi")

        if self.user["role"].upper() == "ADMIN":
            form_layout.addRow("📘 Bölüm Seç:", self.dept_combo)
        form_layout.addRow("Bölüm Adı:", self.dept_name)
        form_layout.addRow("Derslik Kodu:", self.code_input)
        form_layout.addRow("Derslik Adı:", self.name_input)
        form_layout.addRow("Kapasite:", self.capacity_input)
        form_layout.addRow("Boyuna Sıra (Satır):", self.rows_input)
        form_layout.addRow("Enine Sıra (Sütun):", self.cols_input)
        form_layout.addRow("Sıra Yapısı:", self.group_combo)
        layout.addWidget(form_box)

        # BUTONLAR
        btn_layout = QtWidgets.QHBoxLayout()
        self.btn_add = self.make_button("➕ Ekle")
        self.btn_update = self.make_button("✏️ Güncelle")
        self.btn_delete = self.make_button("🗑️ Sil")
        self.btn_search = self.make_button("🔍 Arama")
        self.btn_preview = self.make_button("👁️ Görsel Önizleme")

        for b in [self.btn_add, self.btn_update, self.btn_delete, self.btn_search, self.btn_preview]:
            btn_layout.addWidget(b)
        layout.addLayout(btn_layout)

        # TABLO
        table_box = QtWidgets.QGroupBox("📋 Kayıtlı Derslikler")
        table_layout = QtWidgets.QVBoxLayout(table_box)
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Bölüm Adı", "Kod", "Ad", "Satır", "Sütun", "Sıra Yapısı", "Kapasite"]
        )
        self.table.setColumnHidden(0, True)
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setMinimumHeight(400)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #f5f8fc;
                border: 1px solid #d0d7de;
                border-radius: 8px;
                font-size: 11pt;
            }
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                padding: 5px;
                border: none;
            }
            QTableWidget::item:selected { background-color: #d7ebff; }
        """)
        table_layout.addWidget(self.table)
        layout.addWidget(table_box)

        # OTURMA PLANI GÖRSELİ
        self.preview_label = QtWidgets.QLabel("🪑 Oturma Planı Önizleme")
        self.preview_label.setFont(QtGui.QFont("Segoe UI", 12, QtGui.QFont.Bold))
        layout.addWidget(self.preview_label)

        self.preview_scene = QtWidgets.QGraphicsScene()
        self.preview_view = QtWidgets.QGraphicsView(self.preview_scene)
        self.preview_view.setFixedHeight(280)
        layout.addWidget(self.preview_view)

        # SİNYALLER
        self.btn_add.clicked.connect(self.add_classroom)
        self.btn_update.clicked.connect(self.update_classroom)
        self.btn_delete.clicked.connect(self.delete_classroom)
        self.btn_search.clicked.connect(self.search_classroom)
        self.btn_preview.clicked.connect(self.show_preview)
        self.table.itemSelectionChanged.connect(self.auto_fill_fields)

        self.load_classrooms()

    # --------------------------------------------------------
    def make_button(self, text):
        b = QtWidgets.QPushButton(text)
        b.setMinimumHeight(45)
        b.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        b.setStyleSheet("""
            QPushButton {
                background-color: #4A90E2;
                color: white;
                font-weight: bold;
                border-radius: 6px;
                padding: 8px 12px;
            }
            QPushButton:hover { background-color: #357ABD; }
        """)
        return b

    # --------------------------------------------------------
    # EKLE / GÜNCELLE / SİL
    # --------------------------------------------------------
    def add_classroom(self):
        try:
            dept_name = self.dept_name.text().strip()
            code = self.code_input.text().strip()
            name = self.name_input.text().strip()
            rows = self.rows_input.value()
            cols = self.cols_input.value()
            group = int(self.group_combo.currentText())
            capacity_manual = self.capacity_input.value()

            if not (dept_name and code and name):
                QtWidgets.QMessageBox.warning(self, "Eksik Bilgi", "Tüm alanları doldurun.")
                return

            # Maksimum kapasiteyi hesapla
            fill_per_group = {2: 1, 3: 2, 4: 2}
            max_capacity = rows * cols * fill_per_group[group]

            if capacity_manual > max_capacity:
                QtWidgets.QMessageBox.critical(
                    self,
                    "Hatalı Kapasite",
                    f"Girilen kapasite ({capacity_manual}) maksimum oturulabilir kapasiteyi ({max_capacity}) aşıyor!"
                )
                return

            department_id = (
                self.dept_combo.currentData() if self.user["role"].upper() == "ADMIN"
                else self.user["department_id"]
            )

            self.service.create_with_department(department_id, dept_name, code, name, rows, cols, group)
            QtWidgets.QMessageBox.information(self, "Başarılı", "Derslik eklendi (kapasite otomatik hesaplandı).")
            self.load_classrooms()
            self.classroom_added.emit()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Hata", str(e))

    def update_classroom(self):
        row = self.table.currentRow()
        if row < 0:
            QtWidgets.QMessageBox.warning(self, "Seçim", "Bir satır seçmelisin.")
            return
        try:
            classroom_id = int(self.table.item(row, 0).text())
            name = self.name_input.text().strip()
            rows = self.rows_input.value()
            cols = self.cols_input.value()
            group = int(self.group_combo.currentText())
            capacity_manual = self.capacity_input.value()

            fill_per_group = {2: 1, 3: 2, 4: 2}
            max_capacity = rows * cols * fill_per_group[group]

            if capacity_manual > max_capacity:
                QtWidgets.QMessageBox.critical(
                    self,
                    "Hatalı Kapasite",
                    f"Girilen kapasite ({capacity_manual}) maksimum oturulabilir kapasiteyi ({max_capacity}) aşıyor!"
                )
                return

            confirm = QtWidgets.QMessageBox.question(
                self, "Güncelleme Onayı", f"'{name}' adlı dersliği güncellemek istediğine emin misin?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )
            if confirm == QtWidgets.QMessageBox.No:
                return

            self.service.update_by_id(classroom_id, name, rows, cols, group)
            QtWidgets.QMessageBox.information(self, "Başarılı", "Derslik güncellendi.")
            self.load_classrooms()
            self.classroom_added.emit()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Hata", str(e))

    # --------------------------------------------------------
    # DERSLİK SİLME, ARAMA, TABLO, ÖNİZLEME — (KISALTILMADAN AYNEN KORUNDU)
    # --------------------------------------------------------
    def delete_classroom(self):
        row = self.table.currentRow()
        if row < 0:
            QtWidgets.QMessageBox.warning(self, "Seçim", "Bir satır seçmelisin.")
            return

        name = self.table.item(row, 3).text()
        confirm = QtWidgets.QMessageBox.question(
            self, "Silme Onayı", f"'{name}' adlı dersliği silmek istediğine emin misin?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if confirm == QtWidgets.QMessageBox.No:
            return

        try:
            classroom_id = int(self.table.item(row, 0).text())
            self.service.delete_by_id(classroom_id)
            QtWidgets.QMessageBox.information(self, "Silindi", f"{name} adlı derslik silindi.")
            self.load_classrooms()
            self.classroom_added.emit()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Hata", str(e))

    def search_classroom(self):
        keyword, ok = QtWidgets.QInputDialog.getText(self, "Derslik Ara", "Derslik Kodu (ör: C101):")
        if not ok or not keyword.strip():
            return
        try:
            keyword = keyword.strip()
            if self.user["role"].upper() == "ADMIN":
                results = self.service.search_global(keyword)
            else:
                results = self.service.search(self.user["department_id"], keyword)

            if not results:
                QtWidgets.QMessageBox.information(self, "Sonuç", "Eşleşen derslik bulunamadı.")
                return

            self.fill_table(results)

            data = results[0]
            self.dept_name.setText(data["department_name"])
            self.code_input.setText(data["code"])
            self.name_input.setText(data["name"])
            self.rows_input.setValue(int(data["num_rows"]))
            self.cols_input.setValue(int(data["num_cols"]))
            self.group_combo.setCurrentText(str(data["seat_group"]))
            self.show_preview()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Hata", str(e))

    def load_classrooms(self):
        try:
            if self.user["role"].upper() == "ADMIN":
                selected_dept = None
                if hasattr(self, "filter_combo"):
                    selected_dept = self.filter_combo.currentData()
                rooms = (
                    self.service.list_by_department(selected_dept)
                    if selected_dept else self.service.list_all()
                )
            else:
                rooms = self.service.list_by_department(self.user["department_id"])
            self.fill_table(rooms)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Hata", str(e))

    def fill_table(self, rooms):
        self.table.setRowCount(len(rooms))
        for r, room in enumerate(rooms):
            self.table.setItem(r, 0, QtWidgets.QTableWidgetItem(str(room["id"])))
            self.table.setItem(r, 1, QtWidgets.QTableWidgetItem(room["department_name"]))
            self.table.setItem(r, 2, QtWidgets.QTableWidgetItem(room["code"]))
            self.table.setItem(r, 3, QtWidgets.QTableWidgetItem(room["name"]))
            self.table.setItem(r, 4, QtWidgets.QTableWidgetItem(str(room["num_rows"])))
            self.table.setItem(r, 5, QtWidgets.QTableWidgetItem(str(room["num_cols"])))
            self.table.setItem(r, 6, QtWidgets.QTableWidgetItem(str(room["seat_group"])))
            self.table.setItem(r, 7, QtWidgets.QTableWidgetItem(str(room["capacity"])))

    def auto_fill_fields(self):
        row = self.table.currentRow()
        if row < 0:
            return
        self.dept_name.setText(self.table.item(row, 1).text())
        self.code_input.setText(self.table.item(row, 2).text())
        self.name_input.setText(self.table.item(row, 3).text())
        self.rows_input.setValue(int(self.table.item(row, 4).text()))
        self.cols_input.setValue(int(self.table.item(row, 5).text()))
        self.group_combo.setCurrentText(self.table.item(row, 6).text())

    def show_preview(self):
        rows = self.rows_input.value()
        cols = self.cols_input.value()
        group = int(self.group_combo.currentText())

        if rows <= 0 or cols <= 0:
            return

        self.preview_scene.clear()
        box_w, box_h, spacing = 25, 18, 6
        for i in range(rows):
            for j in range(cols):
                for k in range(group):
                    rect = QtCore.QRectF(
                        j * (box_w * group + spacing) + k * box_w,
                        i * (box_h + spacing),
                        box_w - 2,
                        box_h - 2
                    )
                    brush = QtGui.QBrush(QtGui.QColor(173, 216, 230))
                    self.preview_scene.addRect(rect, QtGui.QPen(QtCore.Qt.black), brush)

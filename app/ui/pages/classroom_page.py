from PyQt5 import QtWidgets, QtGui, QtCore
from app.services.classroom_service import ClassroomService


class ClassroomPage(QtWidgets.QWidget):
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
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 20)
        layout.setSpacing(20)

        # ÜST KISIM (Başlık + Çıkış)
        header_layout = QtWidgets.QHBoxLayout()
        back_btn = QtWidgets.QPushButton("⬅️ Geri Dön")
        back_btn.setFixedWidth(120)
        back_btn.clicked.connect(self.go_back)
        back_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

        title = QtWidgets.QLabel("🏫 Derslik Giriş Ekranı")
        title.setFont(QtGui.QFont("Segoe UI", 18, QtGui.QFont.Bold))
        title.setAlignment(QtCore.Qt.AlignCenter)

        header_layout.addWidget(back_btn)
        header_layout.addStretch()
        header_layout.addWidget(title)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # FORM ALANI
        form_layout = QtWidgets.QFormLayout()
        form_layout.setLabelAlignment(QtCore.Qt.AlignRight)
        form_layout.setFormAlignment(QtCore.Qt.AlignLeft)
        form_layout.setHorizontalSpacing(20)
        form_layout.setVerticalSpacing(10)

        self.dept_name = QtWidgets.QLineEdit()
        self.dept_name.setPlaceholderText("ör: Bilgisayar Mühendisliği")

        self.code_input = QtWidgets.QLineEdit()
        self.name_input = QtWidgets.QLineEdit()
        self.rows_input = QtWidgets.QSpinBox(); self.rows_input.setRange(1, 100)
        self.cols_input = QtWidgets.QSpinBox(); self.cols_input.setRange(1, 100)
        self.group_combo = QtWidgets.QComboBox()
        self.group_combo.addItems(["2", "3", "4"])
        self.capacity_input = QtWidgets.QLineEdit()

        form_layout.addRow("Bölüm Adı:", self.dept_name)
        form_layout.addRow("Derslik Kodu:", self.code_input)
        form_layout.addRow("Derslik Adı:", self.name_input)
        form_layout.addRow("Boyuna Sıra (Satır):", self.rows_input)
        form_layout.addRow("Enine Sıra (Sütun):", self.cols_input)
        form_layout.addRow("Sıra Yapısı:", self.group_combo)
        form_layout.addRow("Kapasite:", self.capacity_input)
        layout.addLayout(form_layout)

        # BUTONLAR
        btn_layout = QtWidgets.QHBoxLayout()
        self.btn_add = QtWidgets.QPushButton("➕ Ekle")
        self.btn_update = QtWidgets.QPushButton("✏️ Güncelle")
        self.btn_delete = QtWidgets.QPushButton("🗑️ Sil")
        self.btn_search = QtWidgets.QPushButton("🔍 Ara")
        self.btn_preview = QtWidgets.QPushButton("👁️ Görsel Önizleme")

        for b in [self.btn_add, self.btn_update, self.btn_delete, self.btn_search, self.btn_preview]:
            b.setMinimumHeight(40)
            b.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            b.setStyleSheet("""
                QPushButton {
                    background-color: #4A90E2;
                    color: white;
                    font-weight: bold;
                    border-radius: 6px;
                }
                QPushButton:hover { background-color: #357ABD; }
            """)
            btn_layout.addWidget(b)
        layout.addLayout(btn_layout)

        # TABLO
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            ["Bölüm Adı", "Kod", "Ad", "Satır", "Sütun", "Sıra Yapısı", "Kapasite"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        layout.addWidget(self.table)

        # OTURMA PLANI GÖRSELİ
        self.preview_label = QtWidgets.QLabel("🪑 Oturma Planı Önizleme")
        self.preview_label.setFont(QtGui.QFont("Segoe UI", 12, QtGui.QFont.Bold))
        layout.addWidget(self.preview_label)

        self.preview_scene = QtWidgets.QGraphicsScene()
        self.preview_view = QtWidgets.QGraphicsView(self.preview_scene)
        self.preview_view.setFixedHeight(250)
        layout.addWidget(self.preview_view)

        # SİNYALLER
        self.btn_add.clicked.connect(self.add_classroom)
        self.btn_update.clicked.connect(self.update_classroom)
        self.btn_delete.clicked.connect(self.delete_classroom)
        self.btn_search.clicked.connect(self.search_classroom)
        self.btn_preview.clicked.connect(self.show_preview)

        self.load_classrooms()

    # --------------------------------------------------------
    # DERSLİK EKLEME
    # --------------------------------------------------------
    def add_classroom(self):
        try:
            dept_name = self.dept_name.text().strip()
            code = self.code_input.text().strip()
            name = self.name_input.text().strip()
            rows = self.rows_input.value()
            cols = self.cols_input.value()
            group = int(self.group_combo.currentText())
            capacity = self.capacity_input.text().strip()

            if not (dept_name and code and name and capacity):
                QtWidgets.QMessageBox.warning(self, "Eksik Bilgi", "Tüm alanları doldurun.")
                return

            self.service.create_with_department(
                self.user["department_id"], dept_name, code, name, rows, cols, group, int(capacity)
            )
            QtWidgets.QMessageBox.information(self, "Başarılı", "Derslik eklendi.")
            self.load_classrooms()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Hata", str(e))

    # --------------------------------------------------------
    # GÜNCELLEME
    # --------------------------------------------------------
    def update_classroom(self):
        row = self.table.currentRow()
        if row < 0:
            QtWidgets.QMessageBox.warning(self, "Seçim", "Bir satır seçmelisin.")
            return
        code = self.table.item(row, 1).text()
        try:
            dept_name = self.dept_name.text().strip()
            name = self.name_input.text().strip()
            rows = self.rows_input.value()
            cols = self.cols_input.value()
            group = int(self.group_combo.currentText())
            capacity = int(self.capacity_input.text().strip())

            self.service.update_with_department(
                self.user["department_id"], dept_name, code, name, rows, cols, group, capacity
            )
            QtWidgets.QMessageBox.information(self, "Başarılı", "Derslik güncellendi.")
            self.load_classrooms()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Hata", str(e))

    # --------------------------------------------------------
    # SİLME
    # --------------------------------------------------------
    def delete_classroom(self):
        row = self.table.currentRow()
        if row < 0:
            QtWidgets.QMessageBox.warning(self, "Seçim", "Bir satır seçmelisin.")
            return
        code = self.table.item(row, 1).text()
        ok = QtWidgets.QMessageBox.question(
            self, "Onay", f"{code} kodlu derslik silinsin mi?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if ok == QtWidgets.QMessageBox.No:
            return
        try:
            self.service.delete_by_code(self.user["department_id"], code)
            self.load_classrooms()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Hata", str(e))

    # --------------------------------------------------------
    # ARAMA
    # --------------------------------------------------------
    def search_classroom(self):
        keyword, ok = QtWidgets.QInputDialog.getText(self, "Ara", "Derslik kodu veya adı:")
        if not ok or not keyword.strip():
            return
        try:
            results = self.service.search(self.user["department_id"], keyword.strip())
            self.fill_table(results)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Hata", str(e))

    # --------------------------------------------------------
    # TABLO DOLDURMA
    # --------------------------------------------------------
    def fill_table(self, rooms):
        self.table.setRowCount(len(rooms))
        for r, room in enumerate(rooms):
            self.table.setItem(r, 0, QtWidgets.QTableWidgetItem(room["department_name"]))
            self.table.setItem(r, 1, QtWidgets.QTableWidgetItem(room["code"]))
            self.table.setItem(r, 2, QtWidgets.QTableWidgetItem(room["name"]))
            self.table.setItem(r, 3, QtWidgets.QTableWidgetItem(str(room["num_rows"])))
            self.table.setItem(r, 4, QtWidgets.QTableWidgetItem(str(room["num_cols"])))
            self.table.setItem(r, 5, QtWidgets.QTableWidgetItem(str(room["seat_group"])))
            self.table.setItem(r, 6, QtWidgets.QTableWidgetItem(str(room["capacity"])))

    # --------------------------------------------------------
    # LİSTELEME
    # --------------------------------------------------------
    def load_classrooms(self):
        try:
            rooms = self.service.list_by_department(self.user["department_id"])
            self.fill_table(rooms)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Hata", str(e))

    # --------------------------------------------------------
    # GÖRSEL ÖNİZLEME
    # --------------------------------------------------------
    def show_preview(self):
        row = self.table.currentRow()
        if row < 0:
            QtWidgets.QMessageBox.warning(self, "Uyarı", "Bir derslik seçmelisin.")
            return

        rows = int(self.table.item(row, 3).text())
        cols = int(self.table.item(row, 4).text())
        group = int(self.table.item(row, 5).text())

        self.preview_scene.clear()
        box_w, box_h = 25, 18
        spacing = 6
        for i in range(rows):
            for j in range(cols):
                for k in range(group):
                    rect = QtCore.QRectF(
                        j * (box_w * group + spacing) + k * box_w,
                        i * (box_h + spacing),
                        box_w - 2,
                        box_h - 2
                    )
                    seat = self.preview_scene.addRect(rect, QtGui.QPen(QtCore.Qt.black),
                                                      QtGui.QBrush(QtGui.QColor(173, 216, 230)))
                    seat.setToolTip(f"Satır {i+1}, Sütun {j+1}, Koltuk {k+1}")

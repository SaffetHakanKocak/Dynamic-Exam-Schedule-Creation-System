from PyQt5 import QtWidgets, QtGui, QtCore
import pandas as pd
from app.services.student_service import StudentService
from app.repositories.departments import list_all as list_departments


class StudentUploadPage(QtWidgets.QWidget):
    students_uploaded = QtCore.pyqtSignal()  # ✅ Dashboard güncelleme sinyali

    def __init__(self, user, go_back):
        super().__init__()
        self.user = user
        self.go_back = go_back
        self.service = StudentService()
        self.df = None
        self.selected_department_id = None  # ✅ Admin için seçilen bölüm
        self.init_ui()

    # --------------------------------------------------------
    def init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(40, 25, 40, 25)
        layout.setSpacing(15)

        # === Başlık ===
        title = QtWidgets.QLabel("🎓 Öğrenci Listesi Yükleme Ekranı")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setFont(QtGui.QFont("Segoe UI", 14, QtGui.QFont.Bold))
        layout.addWidget(title)

        # === Kullanıcı Bilgisi ===
        info = QtWidgets.QLabel(
            f"Bölüm ID: {self.user.get('department_id', 'None')} — Kullanıcı: {self.user.get('email', '')}"
        )
        info.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(info)

        # === Admin için Bölüm Seçimi ===
        if self.user["role"].upper() == "ADMIN":
            dept_layout = QtWidgets.QHBoxLayout()
            lbl = QtWidgets.QLabel("📘 Bölüm Seç:")
            lbl.setFont(QtGui.QFont("Segoe UI", 10, QtGui.QFont.Bold))
            self.dept_combo = QtWidgets.QComboBox()
            self.dept_combo.addItem("— Bölüm Seçiniz —", None)
            for d in list_departments():
                self.dept_combo.addItem(d["name"], d["id"])
            self.dept_combo.currentIndexChanged.connect(self._on_dept_changed)
            dept_layout.addWidget(lbl)
            dept_layout.addWidget(self.dept_combo)
            layout.addLayout(dept_layout)

        # === Butonlar ===
        btns = QtWidgets.QHBoxLayout()
        self.btn_select = QtWidgets.QPushButton("📄 Excel Dosyası Seç (.xlsx)")
        self.btn_upload = QtWidgets.QPushButton("💾 Veritabanına Kaydet")
        self.btn_back = QtWidgets.QPushButton("↩️ Geri Dön")

        for b in [self.btn_select, self.btn_upload, self.btn_back]:
            b.setFixedHeight(40)
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

        btns.addWidget(self.btn_select)
        btns.addWidget(self.btn_upload)
        btns.addWidget(self.btn_back)
        layout.addLayout(btns)

        # === Durum etiketi ===
        self.status_label = QtWidgets.QLabel("")
        self.status_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.status_label)

        # === Tablo ===
        self.table = QtWidgets.QTableWidget()
        layout.addWidget(self.table)

        # === Bağlantılar ===
        self.btn_select.clicked.connect(self.load_excel)
        self.btn_upload.clicked.connect(self.save_to_db)
        self.btn_back.clicked.connect(self.go_back)

    # --------------------------------------------------------
    def _on_dept_changed(self):
        self.selected_department_id = self.dept_combo.currentData()

    # --------------------------------------------------------
    # Excel yükleme + sayfa/satır bazlı hata kontrolü
    # --------------------------------------------------------
    def load_excel(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Excel Dosyası Seç", "", "Excel Files (*.xlsx *.xls)"
        )
        if not path:
            return

        try:
            excel = pd.ExcelFile(path)
            all_data = []

            for sheet in excel.sheet_names:
                try:
                    df = pd.read_excel(excel, sheet_name=sheet)
                    df.columns = [str(c).strip() for c in df.columns]

                    expected = ["Öğrenci No", "Ad Soyad", "Sınıf", "Ders"]
                    missing = [col for col in expected if col not in df.columns]
                    if missing:
                        raise ValueError(f"{sheet} sayfasında eksik sütun(lar): {', '.join(missing)}")

                    # Satır satır kontrol
                    for idx, row in df.iterrows():
                        try:
                            if any(pd.isna(row[c]) for c in expected):
                                raise ValueError(f"{sheet} sayfasındaki {idx + 1}. satırda boş hücre var.")
                        except Exception as inner_err:
                            raise ValueError(f"{sheet} sayfasındaki {idx + 1}. satır hatalı: {inner_err}")

                    all_data.append(df)

                except Exception as sheet_err:
                    raise ValueError(f"{sheet} sayfası okunamadı veya hatalı: {sheet_err}")

            # Tüm sayfaları birleştir
            if all_data:
                self.df = pd.concat(all_data, ignore_index=True)
                self.display_table(self.df)
                self.status_label.setText("✅ Dosya başarıyla yüklendi.")
                self.status_label.setStyleSheet("color: green; font-weight: bold;")
            else:
                self.status_label.setText("❌ Excel boş veya uygun veri içermiyor.")
                self.status_label.setStyleSheet("color: red; font-weight: bold;")

        except Exception as e:
            self.status_label.setText(f"❌ Okuma hatası: {e}")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")

    # --------------------------------------------------------
    def display_table(self, df):
        self.table.setRowCount(len(df))
        self.table.setColumnCount(len(df.columns))
        self.table.setHorizontalHeaderLabels(df.columns)
        for i in range(len(df)):
            for j in range(len(df.columns)):
                self.table.setItem(i, j, QtWidgets.QTableWidgetItem(str(df.iat[i, j])))
        self.table.resizeColumnsToContents()

    # --------------------------------------------------------
    def save_to_db(self):
        if self.df is None or self.df.empty:
            self.status_label.setText("❌ Önce bir Excel dosyası yükleyin.")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
            return

        try:
            dept_id = self.user.get("department_id")
            if self.user["role"].upper() == "ADMIN":
                dept_id = self.selected_department_id
                if not dept_id:
                    self.status_label.setText("⚠️ Lütfen bir bölüm seçiniz.")
                    self.status_label.setStyleSheet("color: orange; font-weight: bold;")
                    return

            students, enrollments = self.service.bulk_insert_from_excel(int(dept_id), self.df)
            self.status_label.setText(f"✅ {students} öğrenci, {enrollments} ders kaydı işlendi.")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            self.students_uploaded.emit()
        except Exception as e:
            self.status_label.setText(f"❌ Kayıt başarısız: {e}")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")

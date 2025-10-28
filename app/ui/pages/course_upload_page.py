from PyQt5 import QtWidgets, QtGui, QtCore
import pandas as pd
from app.services.course_service import CourseService
from app.repositories.departments import list_all as list_departments


class CourseUploadPage(QtWidgets.QWidget):
    courses_uploaded = QtCore.pyqtSignal()  # ✅ Dashboard güncelleme sinyali

    def __init__(self, user, go_back):
        super().__init__()
        self.user = user
        self.go_back = go_back
        self.service = CourseService()
        self.df = None
        self.selected_department_id = None  # ✅ Admin için seçilen bölüm
        self.init_ui()

    # --------------------------------------------------------
    def init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(40, 25, 40, 25)
        layout.setSpacing(15)

        # === Başlık ===
        title = QtWidgets.QLabel("📚 Ders Listesi Yükleme Ekranı")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setFont(QtGui.QFont("Segoe UI", 14, QtGui.QFont.Bold))
        layout.addWidget(title)

        # === Kullanıcı Bilgisi ===
        info = QtWidgets.QLabel(
            f"Bölüm ID: <b>{self.user.get('department_id', '')}</b> — "
            f"Kullanıcı: {self.user.get('email', '')}"
        )
        info.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(info)

        # === Admin ise bölüm seçme combobox'ı ===
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
        hbtn = QtWidgets.QHBoxLayout()
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

        hbtn.addWidget(self.btn_select)
        hbtn.addWidget(self.btn_upload)
        hbtn.addWidget(self.btn_back)
        layout.addLayout(hbtn)

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
    # Excel yükleme + satır/sayfa hata kontrolü
    # --------------------------------------------------------
    def load_excel(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Excel Dosyası Seç", "", "Excel Files (*.xlsx *.xls)"
        )
        if not path:
            return

        try:
            excel = pd.ExcelFile(path)
            final_rows = []
            current_class = None
            current_type = "Zorunlu"

            for sheet in excel.sheet_names:
                df = pd.read_excel(excel, sheet_name=sheet, header=None)

                for idx, row in df.iterrows():
                    try:
                        col_values = [str(x).strip() if not pd.isna(x) else "" for x in row.tolist()]
                        if not any(col_values):
                            continue

                        first_col = col_values[0].upper()

                        # 🔹 Sınıf tespiti
                        if any(f"{n}. SINIF" in first_col for n in ["1", "2", "3", "4"]):
                            current_class = col_values[0].strip()
                            current_type = "Zorunlu"
                            continue

                        # 🔹 Seçmeli tespiti
                        if "SEÇMEL" in first_col or "SEÇİML" in first_col:
                            current_type = "Seçmeli"
                            continue

                        # 🔹 "DERS KODU" başlık satırlarını atla
                        if "DERS KODU" in first_col:
                            continue

                        # 🔹 Gerçek ders satırlarını tespit et
                        if len(col_values) >= 3 and col_values[0] and col_values[1]:
                            final_rows.append({
                                "DERS KODU": col_values[0],
                                "DERSİN ADI": col_values[1],
                                "DERSİ VEREN ÖĞR. ELEMANI": col_values[2],
                                "SINIF": current_class if current_class else "Belirtilmemiş",
                                "DERS TÜRÜ": current_type
                            })

                    except Exception as row_err:
                        raise ValueError(f"{sheet} sayfasındaki {idx + 1}. satırda hata: {row_err}")

            df_final = pd.DataFrame(final_rows)
            if df_final.empty:
                self.status_label.setText("❌ Dosyada geçerli ders bilgisi yok.")
                self.status_label.setStyleSheet("color: red; font-weight: bold;")
                return

            self.df = df_final
            self.display_table(df_final)
            self.status_label.setText("✅ Dosya başarıyla yüklendi (sınıf ve tür dahil).")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")

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

            self.df.columns = [str(c).strip().upper() for c in self.df.columns]
            count = self.service.bulk_insert_from_excel(int(dept_id), self.df)
            self.status_label.setText(f"✅ {count} ders başarıyla veritabanına kaydedildi.")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            self.courses_uploaded.emit()

        except Exception as e:
            self.status_label.setText(f"❌ Kayıt başarısız: {e}")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")

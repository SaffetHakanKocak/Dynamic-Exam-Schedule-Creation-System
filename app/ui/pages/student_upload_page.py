from PyQt5 import QtWidgets, QtGui, QtCore
import pandas as pd
from app.services.student_service import StudentService


class StudentUploadPage(QtWidgets.QWidget):
    def __init__(self, user, go_back):
        super().__init__()
        self.user = user
        self.go_back = go_back
        self.service = StudentService()
        self.df = None
        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        title = QtWidgets.QLabel("🎓 Öğrenci Listesi Yükleme Ekranı")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setFont(QtGui.QFont("Segoe UI", 12, QtGui.QFont.Bold))
        layout.addWidget(title)

        info = QtWidgets.QLabel(
            f"Bölüm ID: {self.user.get('department_id', '')} — Kullanıcı: {self.user.get('email', '')}"
        )
        info.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(info)

        btns = QtWidgets.QHBoxLayout()
        self.btn_select = QtWidgets.QPushButton("📄 Excel Dosyası Seç (.xlsx)")
        self.btn_upload = QtWidgets.QPushButton("💾 Veritabanına Kaydet")
        self.btn_back = QtWidgets.QPushButton("↩️ Geri Dön")

        for b in [self.btn_select, self.btn_upload, self.btn_back]:
            b.setFixedHeight(40)
            b.setStyleSheet("background-color: #4A90E2; color: white; font-weight: bold; border-radius: 6px;")

        btns.addWidget(self.btn_select)
        btns.addWidget(self.btn_upload)
        btns.addWidget(self.btn_back)
        layout.addLayout(btns)

        self.status_label = QtWidgets.QLabel("")
        self.status_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.status_label)

        self.table = QtWidgets.QTableWidget()
        layout.addWidget(self.table)

        self.btn_select.clicked.connect(self.load_excel)
        self.btn_upload.clicked.connect(self.save_to_db)
        self.btn_back.clicked.connect(self.go_back)

    # --------------------------------------------------------
    def load_excel(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Excel Dosyası Seç", "", "Excel Files (*.xlsx *.xls)")
        if not path:
            return

        try:
            df = pd.read_excel(path)
            df.columns = [str(c).strip() for c in df.columns]

            expected = ["Öğrenci No", "Ad Soyad", "Sınıf", "Ders"]
            missing = [col for col in expected if col not in df.columns]
            if missing:
                raise ValueError(f"Excel'de eksik sütun(lar): {', '.join(missing)}")

            self.df = df
            self.display_table(df)
            self.status_label.setText("✅ Dosya başarıyla yüklendi.")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
        except Exception as e:
            self.status_label.setText(f"❌ Dosya okunamadı: {e}")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")

    def display_table(self, df):
        self.table.setRowCount(len(df))
        self.table.setColumnCount(len(df.columns))
        self.table.setHorizontalHeaderLabels(df.columns)
        for i in range(len(df)):
            for j in range(len(df.columns)):
                self.table.setItem(i, j, QtWidgets.QTableWidgetItem(str(df.iat[i, j])))
        self.table.resizeColumnsToContents()

    def save_to_db(self):
        if self.df is None or self.df.empty:
            self.status_label.setText("❌ Önce bir Excel dosyası yükleyin.")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
            return

        try:
            students, enrollments = self.service.bulk_insert_from_excel(
                int(self.user["department_id"]), self.df
            )
            self.status_label.setText(
                f"✅ {students} öğrenci, {enrollments} ders kaydı işlendi. Tablo güncellendi."
            )
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
        except Exception as e:
            self.status_label.setText(f"❌ Kayıt başarısız: {e}")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")

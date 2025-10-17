from PyQt5 import QtWidgets, QtGui, QtCore
from app.services.exam_seating_service import ExamSeatingService
import os, tempfile


class ExamSeatingPage(QtWidgets.QWidget):
    def __init__(self, user, go_back):
        super().__init__()
        self.user = user
        self.go_back = go_back
        self.svc = ExamSeatingService()
        self.seating = []
        self.current_exam_id = None
        self._init_ui()
        self._load_exams()

    def _init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(40, 25, 40, 25)
        layout.setSpacing(16)

        title = QtWidgets.QLabel("🪑 Ders Bazlı Oturma Planı")
        title.setFont(QtGui.QFont("Segoe UI", 18, QtGui.QFont.Bold))
        title.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title)

        back_btn = QtWidgets.QPushButton("⬅️ Geri")
        back_btn.clicked.connect(self.go_back)
        back_btn.setFixedWidth(120)
        layout.addWidget(back_btn, alignment=QtCore.Qt.AlignLeft)

        box = QtWidgets.QGroupBox("Sınavlar")
        hb = QtWidgets.QHBoxLayout(box)

        self.exam_list = QtWidgets.QListWidget()
        self.exam_list.setMinimumWidth(380)
        self.exam_list.itemSelectionChanged.connect(self._on_exam_selected)
        hb.addWidget(self.exam_list, 2)

        right = QtWidgets.QVBoxLayout()
        self.btn_generate = QtWidgets.QPushButton("📐 Oturma Planını Oluştur")
        self.btn_generate.clicked.connect(self._on_generate)
        self.btn_pdf = QtWidgets.QPushButton("📄 PDF İndir")
        self.btn_pdf.clicked.connect(self._on_pdf)
        right.addWidget(self.btn_generate)
        right.addWidget(self.btn_pdf)
        right.addStretch(1)
        hb.addLayout(right, 1)
        layout.addWidget(box)

        self.table = QtWidgets.QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Öğrenci No", "Ad Soyad", "Derslik", "Sıra", "Sütun"])
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        layout.addWidget(self.table, 3)

        self.info = QtWidgets.QLabel("")
        self.info.setStyleSheet("color:#2c3e50; font-weight:bold;")
        layout.addWidget(self.info)

        layout.addStretch(1)

    def _load_exams(self):
        self.exam_list.clear()
        rows = self.svc.list_latest_exams(self.user["department_id"])
        if not rows:
            QtWidgets.QMessageBox.information(
                self, "Bilgi", "Henüz sınav programı oluşturulmamış veya sınav bulunamadı."
            )
            return
        for r in rows:
            dt = r["starts_at"].strftime("%d.%m.%Y %H:%M")
            item = QtWidgets.QListWidgetItem(f"{r['course_code']} — {r['course_name']}  |  {dt}")
            item.setData(QtCore.Qt.UserRole, r["id"])
            self.exam_list.addItem(item)

    def _on_exam_selected(self):
        it = self.exam_list.currentItem()
        if not it:
            return
        self.current_exam_id = it.data(QtCore.Qt.UserRole)
        self.table.setRowCount(0)
        self.seating = []
        self.info.setText("")

    def _on_generate(self):
        if not self.current_exam_id:
            QtWidgets.QMessageBox.warning(self, "Uyarı", "Önce bir sınav seçin.")
            return
        try:
            self.seating = self.svc.generate_seating(self.current_exam_id)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Hata", str(e))
            return

        self.table.setRowCount(len(self.seating))
        for i, p in enumerate(self.seating):
            self.table.setItem(i, 0, QtWidgets.QTableWidgetItem(p["student_number"]))
            self.table.setItem(i, 1, QtWidgets.QTableWidgetItem(p["student_name"]))
            self.table.setItem(i, 2, QtWidgets.QTableWidgetItem(p["room_code"]))
            self.table.setItem(i, 3, QtWidgets.QTableWidgetItem(str(p["row_no"])))
            self.table.setItem(i, 4, QtWidgets.QTableWidgetItem(str(p["col_no"])))

        self.info.setText(f"Toplam {len(self.seating)} öğrenci yerleştirildi.")

    def _on_pdf(self):
        if not self.seating:
            QtWidgets.QMessageBox.warning(self, "Uyarı", "Önce oturma planını oluşturun.")
            return
        fn, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "PDF olarak kaydet",
            os.path.join(tempfile.gettempdir(), "oturma_plani.pdf"),
            "PDF (*.pdf)"
        )
        if not fn:
            return
        try:
            self.svc.export_pdf(self.current_exam_id, self.seating, fn)
            QtWidgets.QMessageBox.information(self, "Tamam", f"PDF kaydedildi:\n{fn}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Hata", f"PDF oluşturulamadı:\n{e}")

        # -------------------- SAYFA YENİLENDİĞİNDE --------------------
    def showEvent(self, event):
        """Sayfa her görüntülendiğinde sınav listesini günceller."""
        super().showEvent(event)
        self._load_exams()

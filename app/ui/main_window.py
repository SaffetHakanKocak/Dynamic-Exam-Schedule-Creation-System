# app/ui/main_window.py
from PyQt5 import QtWidgets, QtCore
from app.ui.dialogs.add_coord_dialog import AddCoordinatorDialog  # (yalnızca ADMIN menüsünde kullanılır)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, user: dict):
        super().__init__()
        self.user = user  # {"id","email","role","department_id"}
        self.setWindowTitle(f"Exam Scheduler — {self.user.get('role', '')}")
        self.resize(1200, 760)

        # ---- Merkez Bilgi ----
        center = QtWidgets.QLabel(
            f"Hoş geldin {self.user.get('email','')}\n"
            f"Rol: {self.user.get('role','')}\n"
            f"Bölüm ID: {self.user.get('department_id')}"
        )
        center.setAlignment(QtCore.Qt.AlignCenter)
        self.setCentralWidget(center)

        # ---- Menü ve Kısayollar ----
        self._build_menu()
        self.statusBar().showMessage("Hazır")

    # ---------- Role & Scope ----------
    @property
    def is_admin(self) -> bool:
        """ADMIN her şeyi görür; COORD yalnız kendi bölümünü."""
        return self.user.get("role") == "ADMIN"

    @property
    def scope_department_id(self) -> int | None:
        """ADMIN -> None (tüm bölümler), COORD -> kendi department_id'si."""
        return None if self.is_admin else self.user.get("department_id")

    # ---------- Menüler ----------
    def _build_menu(self):
        mb = self.menuBar()

        # Dosya
        m_file = mb.addMenu("Dosya")
        act_exit = QtWidgets.QAction("Çıkış", self)
        act_exit.setShortcut("Ctrl+Q")
        act_exit.triggered.connect(self.close)
        m_file.addAction(act_exit)

        # Tanımlar (ADMIN + COORD)
        m_defs = mb.addMenu("Tanımlar")
        act_rooms    = QtWidgets.QAction("Derslikler", self)
        act_courses  = QtWidgets.QAction("Dersler", self)
        act_students = QtWidgets.QAction("Öğrenciler", self)
        m_defs.addAction(act_rooms)
        m_defs.addAction(act_courses)
        m_defs.addAction(act_students)
        act_rooms.triggered.connect(self.open_classrooms)
        act_courses.triggered.connect(self.open_courses)
        act_students.triggered.connect(self.open_students)

        # Planlama (ADMIN + COORD)
        m_plan = mb.addMenu("Planlama")
        act_terms = QtWidgets.QAction("Sınav Dönemi & Timeslot", self)
        act_sched = QtWidgets.QAction("Sınav Programı", self)
        act_seats = QtWidgets.QAction("Oturma Planı", self)
        m_plan.addAction(act_terms)
        m_plan.addAction(act_sched)
        m_plan.addAction(act_seats)
        act_terms.triggered.connect(self.open_terms)
        act_sched.triggered.connect(self.open_schedule)
        act_seats.triggered.connect(self.open_seating)

        # Yönetim (SADECE ADMIN)
        if self.is_admin:
            m_admin = mb.addMenu("Yönetim")
            act_add_coord = QtWidgets.QAction("Bölüm Koordinatörü Ekle", self)
            act_add_coord.triggered.connect(self.open_add_coord)
            m_admin.addAction(act_add_coord)

    # ---------- Ekran Açıcılar (şimdilik stub; sayfalar geldikçe buraya bağlayacağız) ----------
    def open_classrooms(self):
        QtWidgets.QMessageBox.information(
            self, "Derslikler",
            f"Derslik CRUD burada açılacak.\nscope_department_id={self.scope_department_id}"
        )

    def open_courses(self):
        QtWidgets.QMessageBox.information(
            self, "Dersler",
            f"Ders CRUD burada açılacak.\nscope_department_id={self.scope_department_id}"
        )

    def open_students(self):
        QtWidgets.QMessageBox.information(
            self, "Öğrenciler",
            f"Öğrenci CRUD burada açılacak.\nscope_department_id={self.scope_department_id}"
        )

    def open_terms(self):
        QtWidgets.QMessageBox.information(
            self, "Sınav Dönemi & Timeslot",
            "Dönem oluşturma ve timeslot üretimi burada olacak."
        )

    def open_schedule(self):
        QtWidgets.QMessageBox.information(
            self, "Sınav Programı",
            "Greedy yerleştirme + çakışma kontrolleri burada olacak."
        )

    def open_seating(self):
        QtWidgets.QMessageBox.information(
            self, "Oturma Planı",
            "Salon/koltuk dağıtımı ve çıktı alma burada olacak."
        )

    # ---------- Yönetim İşlemleri ----------
    def open_add_coord(self):
        """Sadece ADMIN: Bölüm Koordinatörü ekleme dialogu."""
        dlg = AddCoordinatorDialog(parent=self)
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            QtWidgets.QMessageBox.information(self, "Başarılı", "Koordinatör kaydedildi.")

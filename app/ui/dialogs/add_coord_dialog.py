from PyQt5 import QtWidgets
import bcrypt
from app.repositories.departments import list_all as list_departments
from app.repositories.users_admin import create_coord, email_exists

class AddCoordinatorDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bölüm Koordinatörü Ekle")
        self.setModal(True)
        self.resize(420, 230)

        self.email = QtWidgets.QLineEdit()
        self.email.setPlaceholderText("coord.bm@example.com")
        self.pass1 = QtWidgets.QLineEdit(); self.pass1.setEchoMode(QtWidgets.QLineEdit.Password)
        self.pass2 = QtWidgets.QLineEdit(); self.pass2.setEchoMode(QtWidgets.QLineEdit.Password)

        self.dept = QtWidgets.QComboBox()
        self._fill_departments()

        form = QtWidgets.QFormLayout()
        form.addRow("Bölüm", self.dept)
        form.addRow("E-posta", self.email)
        form.addRow("Şifre", self.pass1)
        form.addRow("Şifre (tekrar)", self.pass2)

        btn_ok = QtWidgets.QPushButton("Kaydet")
        btn_cancel = QtWidgets.QPushButton("Vazgeç")
        btn_ok.clicked.connect(self._save)
        btn_cancel.clicked.connect(self.reject)

        v = QtWidgets.QVBoxLayout(self)
        v.addLayout(form)
        v.addStretch(1)
        h = QtWidgets.QHBoxLayout(); h.addStretch(1); h.addWidget(btn_cancel); h.addWidget(btn_ok)
        v.addLayout(h)

    def _fill_departments(self):
        self.dept.clear()
        rows = list_departments()
        for r in rows:
            self.dept.addItem(r["name"], r["id"])

    def _save(self):
        dept_id = self.dept.currentData()
        email = self.email.text().strip().lower()
        p1 = self.pass1.text(); p2 = self.pass2.text()

        if not email or not p1 or not p2:
            QtWidgets.QMessageBox.warning(self, "Eksik", "Tüm alanlar zorunludur."); return
        if p1 != p2:
            QtWidgets.QMessageBox.warning(self, "Uyarı", "Şifreler eşleşmiyor."); return
        if email_exists(email):
            QtWidgets.QMessageBox.warning(self, "Uyarı", "Bu e-posta zaten kayıtlı."); return

        try:
            pw_hash = bcrypt.hashpw(p1.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            create_coord(email=email, password_hash=pw_hash, department_id=dept_id)
            self.accept()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Hata", str(e))

from PyQt5 import QtWidgets, QtGui, QtCore
from app.db import fetchall, execute


class UserListPage(QtWidgets.QWidget):
    def __init__(self, go_back):
        super().__init__()
        self.go_back = go_back
        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)

        # === Üst Bar ===
        header = QtWidgets.QHBoxLayout()
        back_btn = QtWidgets.QPushButton("⬅️ Geri Dön")
        back_btn.setFixedWidth(130)
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
        back_btn.clicked.connect(self.go_back)
        header.addWidget(back_btn)

        title = QtWidgets.QLabel("👥 Sistemde Kayıtlı Kullanıcılar")
        title.setFont(QtGui.QFont("Segoe UI", 16, QtGui.QFont.Bold))
        title.setAlignment(QtCore.Qt.AlignCenter)
        header.addStretch(1)
        header.addWidget(title)
        header.addStretch(1)
        layout.addLayout(header)

        # === Mesaj etiketi ===
        self.message_label = QtWidgets.QLabel("")
        self.message_label.setAlignment(QtCore.Qt.AlignCenter)
        self.message_label.setStyleSheet("font-weight:bold;")
        layout.addWidget(self.message_label)

        # === Tablo ===
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "E-posta", "Rol", "Bölüm", "İşlem"])
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
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
                padding: 6px;
                font-weight: bold;
                border: none;
            }
        """)
        layout.addWidget(self.table)

        # === Veri yükle ===
        self.load_users()

    # --------------------------------------------------------
    # Kullanıcıları Veritabanından Çek
    # --------------------------------------------------------
    def load_users(self):
        users = fetchall("""
            SELECT u.id, u.email, u.role, d.name AS department_name
            FROM users u
            LEFT JOIN departments d ON u.department_id = d.id
            ORDER BY u.id
        """)
        self.table.setRowCount(len(users))

        for i, user in enumerate(users):
            self.table.setItem(i, 0, QtWidgets.QTableWidgetItem(str(user["id"])))
            self.table.setItem(i, 1, QtWidgets.QTableWidgetItem(user["email"]))
            self.table.setItem(i, 2, QtWidgets.QTableWidgetItem(user["role"]))
            self.table.setItem(i, 3, QtWidgets.QTableWidgetItem(user.get("department_name", "-")))

            # --- İşlem sütunu ---
            if user["role"].strip().upper() == "ADMIN":
                # Admin silinemez
                lbl = QtWidgets.QLabel("🔒 Yönetici")
                lbl.setAlignment(QtCore.Qt.AlignCenter)
                lbl.setStyleSheet("color: gray; font-weight:bold;")
                self.table.setCellWidget(i, 4, lbl)
            else:
                # Normal kullanıcılar için sil butonu
                btn_delete = QtWidgets.QPushButton("🗑️ Sil")
                btn_delete.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
                btn_delete.setStyleSheet("""
                    QPushButton {
                        background-color: #e74c3c;
                        color: white;
                        border-radius: 6px;
                        font-weight: bold;
                        padding: 4px 10px;
                    }
                    QPushButton:hover { background-color: #c0392b; }
                """)
                btn_delete.clicked.connect(lambda _, uid=user["id"]: self.delete_user(uid))
                self.table.setCellWidget(i, 4, btn_delete)

    # --------------------------------------------------------
    # Kullanıcı Silme İşlemi
    # --------------------------------------------------------
    def delete_user(self, user_id):
        try:
            # Admin kontrolü (her ihtimale karşı)
            admin_check = fetchall("SELECT role FROM users WHERE id = %s", (user_id,))
            if admin_check and admin_check[0]["role"].strip().upper() == "ADMIN":
                self.show_message("⚠️ Yönetici hesabı silinemez.", "orange")
                return

            execute("DELETE FROM users WHERE id = %s", (user_id,))
            self.load_users()
            self.show_message("✅ Kullanıcı başarıyla silindi.", "green")

        except Exception as e:
            self.show_message(f"❌ Silme hatası: {e}", "red")

    # --------------------------------------------------------
    # Yardımcı Fonksiyonlar
    # --------------------------------------------------------
    def show_message(self, text, color):
        self.message_label.setText(text)
        self.message_label.setStyleSheet(f"color:{color}; font-weight:bold;")
        QtCore.QTimer.singleShot(2000, lambda: self.message_label.clear())

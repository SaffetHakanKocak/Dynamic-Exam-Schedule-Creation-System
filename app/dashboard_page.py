from PyQt5 import QtWidgets, QtGui, QtCore

class DashboardPage(QtWidgets.QWidget):
    def __init__(self, on_navigate):
        super().__init__()
        self.user = None
        self.on_navigate = on_navigate
        self.setup_ui()

    def set_user(self, user):
        self.user = user
        self.info_label.setText(f"Hoş geldin, {user['email']} ({user['role']})")

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignTop)

        title = QtWidgets.QLabel("📋 Ana Kontrol Paneli")
        title.setFont(QtGui.QFont("Segoe UI", 20, QtGui.QFont.Bold))
        title.setAlignment(QtCore.Qt.AlignCenter)

        self.info_label = QtWidgets.QLabel()
        self.info_label.setAlignment(QtCore.Qt.AlignCenter)

        btn_derslik = QtWidgets.QPushButton("🏫 Derslik Girişi")
        btn_derslik.clicked.connect(lambda: self.on_navigate("derslik"))

        btn_ders = QtWidgets.QPushButton("📚 Ders Listesi Yükle")
        btn_ders.clicked.connect(lambda: self.on_navigate("ders"))

        btn_ogr = QtWidgets.QPushButton("👨‍🎓 Öğrenci Listesi Yükle")
        btn_ogr.clicked.connect(lambda: self.on_navigate("ogrenci"))

        for b in [btn_derslik, btn_ders, btn_ogr]:
            b.setMinimumHeight(60)
            b.setFont(QtGui.QFont("Segoe UI", 12))
            b.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

        v = QtWidgets.QVBoxLayout()
        v.setSpacing(20)
        v.addWidget(btn_derslik)
        v.addWidget(btn_ders)
        v.addWidget(btn_ogr)

        frame = QtWidgets.QFrame()
        frame.setLayout(v)
        frame.setStyleSheet("QFrame { background-color: white; border-radius: 12px; padding: 25px; }")

        layout.addWidget(title)
        layout.addWidget(self.info_label)
        layout.addWidget(frame)
        layout.addStretch(1)

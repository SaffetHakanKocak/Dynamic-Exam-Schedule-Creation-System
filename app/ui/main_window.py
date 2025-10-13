from PyQt5 import QtWidgets, QtCore
from app.ui.pages.login_page import LoginPage
from app.ui.pages.dashboard_page import DashboardPage
from app.ui.pages.classroom_page import ClassroomPage
from app.ui.pages.course_upload_page import CourseUploadPage
from app.ui.pages.student_upload_page import StudentUploadPage
from app.ui.pages.student_list_page import StudentListPage
from app.ui.pages.course_list_page import CourseListPage
from app.ui.pages.exam_scheduler_page import ExamSchedulerPage  # ✅ eklendi


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Exam Scheduler — Modern")
        self.resize(1280, 800)
        self.setMinimumSize(1100, 700)

        self.user = None
        self.stack = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.stack)

        # === SAYFALAR ===
        self.login_page = LoginPage(self.on_login_success)
        self.dashboard_page = None
        self.classroom_page = None
        self.course_upload_page = None
        self.student_upload_page = None
        self.student_list_page = None
        self.course_list_page = None
        self.exam_scheduler_page = None  # ✅ yeni sayfa

        self.stack.addWidget(self.login_page)
        self.stack.setCurrentWidget(self.login_page)

    # ========================================================
    # GİRİŞ BAŞARILI OLUNCA
    # ========================================================
    def on_login_success(self, user):
        """Giriş başarılı olduğunda kullanıcıya ait tüm sayfaları hazırla"""
        self.user = user

        # === DASHBOARD ===
        self.dashboard_page = DashboardPage(
            on_navigate=self.on_navigate,
            on_logout=self.logout
        )
        self.dashboard_page.set_user(user)
        self.stack.addWidget(self.dashboard_page)

        # === ALT SAYFALAR ===
        self.classroom_page = ClassroomPage(user, self.go_back_to_dashboard)
        self.course_upload_page = CourseUploadPage(user, self.go_back_to_dashboard)
        self.student_upload_page = StudentUploadPage(user, self.go_back_to_dashboard)
        self.student_list_page = StudentListPage(self.go_back_to_dashboard)
        self.course_list_page = CourseListPage(self.go_back_to_dashboard)
        self.exam_scheduler_page = ExamSchedulerPage(user, self.go_back_to_dashboard)  # ✅ parametre güncel

        # Hepsini stack’e ekle
        for page in [
            self.classroom_page,
            self.course_upload_page,
            self.student_upload_page,
            self.student_list_page,
            self.course_list_page,
            self.exam_scheduler_page
        ]:
            self.stack.addWidget(page)

        # Ana sayfaya yönlendir
        self.stack.setCurrentWidget(self.dashboard_page)

    # ========================================================
    # SAYFA GEÇİŞLERİ
    # ========================================================
    def on_navigate(self, page_name: str):
        """Dashboard'dan diğer sayfalara geçiş kontrolü"""
        mapping = {
            "derslik": self.classroom_page,
            "ders": self.course_upload_page,
            "ogrenci": self.student_upload_page,
            "ogrenci_listesi": self.student_list_page,
            "ders_listesi": self.course_list_page,
            "exam": self.exam_scheduler_page  # ✅ yeni yönlendirme
        }

        if page_name in mapping:
            self.stack.setCurrentWidget(mapping[page_name])
        else:
            QtWidgets.QMessageBox.information(
                self,
                "Henüz Eklenmedi",
                f"'{page_name}' sayfası yakında eklenecek."
            )

    # ========================================================
    # GERİ DÖNÜŞ
    # ========================================================
    def go_back_to_dashboard(self):
        """Her alt sayfadan dashboard'a dönüş"""
        if self.dashboard_page:
            self.stack.setCurrentWidget(self.dashboard_page)

    # ========================================================
    # ÇIKIŞ
    # ========================================================
    def logout(self):
        """Kullanıcı çıkış işlemi"""
        confirm = QtWidgets.QMessageBox.question(
            self,
            "Çıkış Onayı",
            "Oturumdan çıkmak istediğinizden emin misiniz?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )

        if confirm == QtWidgets.QMessageBox.Yes:
            self.user = None
            self.stack.setCurrentWidget(self.login_page)

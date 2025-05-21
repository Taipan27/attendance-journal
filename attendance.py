import sys
import json
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem, QInputDialog,
    QLabel, QLineEdit, QMessageBox, QComboBox, QSpinBox, QHeaderView
)
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtCore import Qt, QObject

USERS_FILE = "users.json"


# ──────────────────── вспомогательные функции ────────────────────
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}


def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)


# ─────────────────────────── контроллер ───────────────────────────
class AppController(QObject):
    """Управляет переходами между окнами"""

    def __init__(self):
        super().__init__()
        self.users = load_users()
        self.current_user = None
        self.login_window = None
        self.schedule_window = None
        self.attendance_window = None

    def start(self):
        self.login_window = LoginRegisterWindow(self)
        self.login_window.show()

    # ――― после успешного входа
    def login_successful(self, username):
        self.current_user = username
        self.show_schedule_window()

    # ――― показать окно расписания
    def show_schedule_window(self):
        if self.login_window:
            self.login_window.hide()
        if self.attendance_window:
            self.attendance_window.hide()

        self.schedule_window = ScheduleSetupWindow(
            self.current_user, self.users, self
        )
        self.schedule_window.show()

    # ――― показать журнал
    def show_attendance_window(self):
        if self.schedule_window:
            self.schedule_window.hide()

        self.attendance_window = AttendanceApp(
            self.current_user, self.users, self
        )
        self.attendance_window.show()

    def save_data(self):
        save_users(self.users)


# ───────────────── окно регистрации / логина ─────────────────
class LoginRegisterWindow(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("Вход / Регистрация старосты")
        self.resize(320, 200)

        lay = QVBoxLayout(self)
        lay.addWidget(QLabel("Логин:"))
        self.login_edit = QLineEdit()
        lay.addWidget(self.login_edit)
        lay.addWidget(QLabel("Пароль:"))
        self.pass_edit = QLineEdit()
        self.pass_edit.setEchoMode(QLineEdit.Password)
        lay.addWidget(self.pass_edit)

        btns = QHBoxLayout()
        btn_login = QPushButton("Войти", clicked=self.try_login)
        btn_reg = QPushButton("Зарегистрироваться", clicked=self.try_register)
        btns.addWidget(btn_login)
        btns.addWidget(btn_reg)
        lay.addLayout(btns)

        self.setStyleSheet("""
            QWidget { background:#23272e; color:#fafbfc; }
            QLineEdit { padding:5px; background:#2c313c; border:1px solid #444; }
            QPushButton { background:#326fff; color:white; border-radius:8px; padding:6px 12px; }
            QPushButton:hover { background:#214bc4; }
        """)

    # ――― проверки
    def try_login(self):
        u, p = self.login_edit.text().strip(), self.pass_edit.text().strip()
        if u in self.controller.users and self.controller.users[u]["password"] == p:
            self.controller.login_successful(u)
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль!")

    def try_register(self):
        u, p = self.login_edit.text().strip(), self.pass_edit.text().strip()
        if not u or not p:
            QMessageBox.warning(self, "Ошибка", "Введите логин и пароль!")
            return
        if u in self.controller.users:
            QMessageBox.warning(self, "Ошибка", "Пользователь уже существует!")
            return
        self.controller.users[u] = {"password": p, "students": [], "schedule": []}
        self.controller.save_data()
        QMessageBox.information(self, "Успех", "Регистрация завершена. Войдите.")


# ──────────────────────── окно расписания ────────────────────────
class ScheduleSetupWindow(QWidget):
    def __init__(self, username, users, controller):
        super().__init__()
        self.u = username
        self.users = users
        self.c = controller
        self.setWindowTitle("Настройка расписания")
        self.resize(550, 460)

        self.editing_row = None  # индекс правимой строки

        main = QVBoxLayout(self)

        lbl = QLabel("Расписание занятий")
        lbl.setFont(QFont('Arial', 15, QFont.Bold))
        lbl.setAlignment(Qt.AlignCenter)
        main.addWidget(lbl)

        # ――― таблица текущих пар
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["Предмет", "День", "Тип", "Начало", "Мин"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        main.addWidget(self.table)

        # ――― поля ввода
        form = QVBoxLayout()
        form.addWidget(QLabel("Предмет:"))
        self.subj_edit = QLineEdit()
        form.addWidget(self.subj_edit)

        form.addWidget(QLabel("День недели:"))
        self.day_cb = QComboBox()
        self.day_cb.addItems(["Понедельник", "Вторник", "Среда",
                              "Четверг", "Пятница", "Суббота", "Воскресенье"])
        form.addWidget(self.day_cb)

        form.addWidget(QLabel("Тип занятия:"))
        self.type_cb = QComboBox()
        self.type_cb.addItems(["Лекция", "Практика", "Лабораторная работа"])
        form.addWidget(self.type_cb)

        form.addWidget(QLabel("Время начала (HH:MM):"))
        self.time_edit = QLineEdit()
        form.addWidget(self.time_edit)

        form.addWidget(QLabel("Длительность (минут):"))
        self.dur_spin = QSpinBox()
        self.dur_spin.setRange(1, 300)
        self.dur_spin.setValue(90)
        form.addWidget(self.dur_spin)

        main.addLayout(form)

        # ――― кнопки
        btns = QHBoxLayout()
        btn_add = QPushButton("Добавить / Сохранить", clicked=self.add_or_save)
        btn_edit = QPushButton("Редактировать", clicked=self.start_edit)
        btn_del = QPushButton("Удалить", clicked=self.delete_row)
        btn_next = QPushButton("Перейти к журналу", clicked=self.finish)
        btns.addWidget(btn_add);
        btns.addWidget(btn_edit)
        btns.addWidget(btn_del);
        btns.addWidget(btn_next)
        main.addLayout(btns)

        # стиль
        self.setStyleSheet("""
            QWidget { background:#23272e; color:#fafbfc; }
            QLineEdit, QComboBox, QSpinBox { background:#2c313c; border:1px solid #444; padding:4px; }
            QPushButton { background:#326fff; color:white; border-radius:8px; padding:6px 12px; }
            QPushButton:hover { background:#214bc4; }
            QTableWidget { background:#2c313c; gridline-color:#444; }
            QHeaderView::section { background:#1e2329; color:white; font-weight:bold; border:1px solid #444; }
        """)

        self.load_table()

    # ――― заполнить таблицу
    def load_table(self):
        self.table.setRowCount(0)
        for e in self.users[self.u]["schedule"]:
            r = self.table.rowCount()
            self.table.insertRow(r)
            self.table.setItem(r, 0, QTableWidgetItem(e["subject"]))
            self.table.setItem(r, 1, QTableWidgetItem(e["day"]))
            self.table.setItem(r, 2, QTableWidgetItem(e["type"]))
            self.table.setItem(r, 3, QTableWidgetItem(e["start"]))
            self.table.setItem(r, 4, QTableWidgetItem(str(e["duration"])))

    # ――― проверка времени
    @staticmethod
    def valid_time(t):
        if len(t) != 5 or ':' not in t:
            return False
        h, m = t.split(':')
        return h.isdigit() and m.isdigit() and 0 <= int(h) < 24 and 0 <= int(m) < 60

    # ――― добавить или сохранить изменения
    def add_or_save(self):
        subj = self.subj_edit.text().strip()
        t = self.time_edit.text().strip()
        if not subj:
            QMessageBox.warning(self, "Ошибка", "Введите предмет!")
            return
        if not self.valid_time(t):
            QMessageBox.warning(self, "Ошибка", "Время в формате HH:MM")
            return

        entry = {
            "subject": subj,
            "day": self.day_cb.currentText(),
            "type": self.type_cb.currentText(),
            "start": t,
            "duration": self.dur_spin.value()
        }

        sched = self.users[self.u]["schedule"]
        if self.editing_row is not None:
            sched[self.editing_row] = entry
            self.editing_row = None
        else:
            sched.append(entry)

        self.c.save_data()
        self.load_table()
        self.clear_inputs()

    # ――― начать редактирование
    def start_edit(self):
        r = self.table.currentRow()
        if r == -1:
            QMessageBox.warning(self, "Выбор", "Выберите строку для редактирования")
            return
        self.editing_row = r
        self.subj_edit.setText(self.table.item(r, 0).text())
        self.day_cb.setCurrentText(self.table.item(r, 1).text())
        self.type_cb.setCurrentText(self.table.item(r, 2).text())
        self.time_edit.setText(self.table.item(r, 3).text())
        self.dur_spin.setValue(int(self.table.item(r, 4).text()))

    # ――― удалить пару
    def delete_row(self):
        r = self.table.currentRow()
        if r == -1:
            QMessageBox.warning(self, "Выбор", "Выберите строку для удаления")
            return
        if QMessageBox.question(self, "Удалить", "Удалить выбранную пару?",
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.No:
            return
        del self.users[self.u]["schedule"][r]
        self.c.save_data()
        self.load_table()

    # ――― очистить поля
    def clear_inputs(self):
        self.subj_edit.clear()
        self.time_edit.clear()
        self.dur_spin.setValue(90)

    # ――― перейти к журналу
    def finish(self):
        self.c.save_data()
        self.c.show_attendance_window()


# ───────────────────── окно журнала ─────────────────────
class AttendanceApp(QWidget):
    def __init__(self, username, users, controller):
        super().__init__()
        self.u = username
        self.users = users
        self.c = controller
        self.setWindowTitle(f"Журнал: {username}")
        self.resize(1000, 650)  # Увеличен размер для новых кнопок

        lay = QVBoxLayout(self)

        # Верхняя панель с заголовком и статистикой
        top_layout = QHBoxLayout()
        lbl = QLabel(f"Журнал посещаемости — {username}")
        lbl.setFont(QFont('Arial', 17, QFont.Bold))
        lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        top_layout.addWidget(lbl, 1)  # 1 - коэффициент растяжения

        # Метка для статистики
        self.stats_label = QLabel()
        self.stats_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        top_layout.addWidget(self.stats_label)
        lay.addLayout(top_layout)

        sched = self.users[self.u]["schedule"]
        self.table = QTableWidget(0, 2 + len(sched))
        headers = ["ФИО", "Телефон"] + [
            f"{s['day']} | {s['subject']} | {s['start']} ({s['duration']} мин) | {s['type']}"
            for s in sched
        ]
        self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.cellClicked.connect(self.cell_clicked)  # Обработчик клика
        lay.addWidget(self.table)

        # Создаем две строки кнопок для лучшего размещения
        b1 = QHBoxLayout()
        b1.addWidget(QPushButton("Добавить ученика", clicked=self.add_student))
        b1.addWidget(QPushButton("Редактировать ученика", clicked=self.edit_student))
        b1.addWidget(QPushButton("Удалить ученика", clicked=self.delete_student))
        lay.addLayout(b1)

        b2 = QHBoxLayout()
        b2.addWidget(QPushButton("Отметить посещение", clicked=self.toggle_attendance))
        b2.addWidget(QPushButton("Сохранить", clicked=self.save_students))
        b2.addWidget(QPushButton("Вернуться к расписанию", clicked=self.back))
        lay.addLayout(b2)

        self.load_students()
        self.update_statistics()  # Обновляем статистику при загрузке
        self.apply_styles()

    # ――― обработчик клика на ячейку
    def cell_clicked(self, row, column):
        """Обработчик клика на ячейку таблицы"""
        if column >= 2:  # Клик по ячейке с посещаемостью
            item = self.table.item(row, column)
            # Переключаем статус присутствия
            new_text = "Присутствует" if item.text() == "Отсутствует" else "Отсутствует"
            item.setText(new_text)
            self.set_status_color(item)
            # Обновляем статистику после изменения
            self.update_statistics()

    # ――― обновление статистики
    def update_statistics(self):
        """Обновляет статистику посещаемости и отображает её"""
        if self.table.rowCount() == 0:
            self.stats_label.setText("Нет данных")
            return

        total_students = self.table.rowCount()
        total_classes = self.table.columnCount() - 2  # Минус столбцы ФИО и телефон

        if total_classes == 0:
            self.stats_label.setText(f"Студентов: {total_students}, занятий нет")
            return

        # Общее количество присутствий
        total_present = 0

        # Проход по всем ячейкам с отметками посещаемости
        for r in range(self.table.rowCount()):
            for c in range(2, self.table.columnCount()):
                item = self.table.item(r, c)
                if item and item.text() == "Присутствует":
                    total_present += 1

        # Вычисляем общий процент посещаемости
        total_cells = total_students * total_classes
        attendance_percent = (total_present / total_cells) * 100 if total_cells > 0 else 0

        # Формируем текст статистики
        stats_text = f"Студентов: {total_students}, Занятий: {total_classes}\n"
        stats_text += f"Общая посещаемость: {attendance_percent:.1f}%"

        self.stats_label.setText(stats_text)

        # Настраиваем цвет метки в зависимости от процента посещаемости
        if attendance_percent < 50:
            self.stats_label.setStyleSheet("color: #ff6b6b; font-size: 13px;")  # Красный
        elif attendance_percent < 75:
            self.stats_label.setStyleSheet("color: #ffd166; font-size: 13px;")  # Желтый
        else:
            self.stats_label.setStyleSheet("color: #06d6a0; font-size: 13px;")  # Зеленый

    # ――― загрузка студентов
    def load_students(self):
        self.table.setRowCount(0)
        sched_len = len(self.users[self.u]["schedule"])
        for row in self.users[self.u]["students"]:
            if len(row) < 2 + sched_len:
                row += ["Отсутствует"] * (2 + sched_len - len(row))
            r = self.table.rowCount()
            self.table.insertRow(r)
            for c, val in enumerate(row):
                item = QTableWidgetItem(val)
                if c >= 2:
                    self.set_status_color(item)
                self.table.setItem(r, c, item)

    # ――― добавить студента
    def add_student(self):
        name, ok1 = QInputDialog.getText(self, "ФИО", "Введите ФИО:")
        if not ok1 or not name:
            return
        phone, ok2 = QInputDialog.getText(self, "Телефон", "Введите телефон:")
        if not ok2:
            return
        r = self.table.rowCount()
        self.table.insertRow(r)
        self.table.setItem(r, 0, QTableWidgetItem(name))
        self.table.setItem(r, 1, QTableWidgetItem(phone))
        for c in range(2, self.table.columnCount()):
            it = QTableWidgetItem("Отсутствует")
            self.set_status_color(it)
            self.table.setItem(r, c, it)
        # Обновляем статистику после добавления студента
        self.update_statistics()

    # ――― редактировать студента
    def edit_student(self):
        r = self.table.currentRow()
        if r == -1:
            QMessageBox.warning(self, "Выбор", "Выберите строку для редактирования")
            return

        current_name = self.table.item(r, 0).text()
        current_phone = self.table.item(r, 1).text()

        new_name, ok1 = QInputDialog.getText(self, "Редактировать ФИО", "ФИО:", text=current_name)
        if not ok1 or not new_name:
            return

        new_phone, ok2 = QInputDialog.getText(self, "Редактировать Телефон", "Телефон:", text=current_phone)
        if not ok2:
            return

        self.table.item(r, 0).setText(new_name)
        self.table.item(r, 1).setText(new_phone)
        QMessageBox.information(self, "Обновлено", "Данные студента обновлены")

    # ――― удалить
    def delete_student(self):
        r = self.table.currentRow()
        if r == -1:
            QMessageBox.warning(self, "Выбор", "Выберите строку для удаления")
            return
        if QMessageBox.question(
                self, "Удалить", f"Удалить {self.table.item(r, 0).text()}?",
                QMessageBox.Yes | QMessageBox.No) == QMessageBox.No:
            return
        self.table.removeRow(r)
        # Обновляем статистику после удаления студента
        self.update_statistics()

    # ――― отметить/снять
    def toggle_attendance(self):
        r, c = self.table.currentRow(), self.table.currentColumn()
        if r == -1:
            QMessageBox.warning(self, "Выбор", "Выберите ячейку/студента")
            return
        if c >= 2:
            items = [self.table.item(r, c)]
        else:  # клик по ФИО/тел — весь ряд
            items = [self.table.item(r, cc) for cc in range(2, self.table.columnCount())]
        for it in items:
            new = "Присутствует" if it.text() == "Отсутствует" else "Отсутствует"
            it.setText(new)
            self.set_status_color(it)
        # Обновляем статистику после изменения посещаемости
        self.update_statistics()

    @staticmethod
    def set_status_color(item):
        if item.text() == "Присутствует":
            item.setBackground(QColor(60, 180, 60))
            item.setForeground(QColor("white"))
        else:
            item.setBackground(QColor(180, 60, 60))
            item.setForeground(QColor("white"))

    # ――― сохранить
    def save_students(self):
        data = []
        for r in range(self.table.rowCount()):
            row = []
            for c in range(self.table.columnCount()):
                it = self.table.item(r, c)
                row.append(it.text() if it else "")
            data.append(row)
        self.users[self.u]["students"] = data
        self.c.save_data()
        # Обновляем статистику после сохранения
        self.update_statistics()
        QMessageBox.information(self, "Сохранено", "Данные сохранены")

    def back(self):
        self.save_students()
        self.c.show_schedule_window()

    # ――― стили
    def apply_styles(self):
        self.table.setShowGrid(True)
        self.table.verticalHeader().setVisible(True)
        self.table.verticalHeader().setDefaultSectionSize(24)
        self.table.setColumnWidth(0, 220)
        self.table.setColumnWidth(1, 150)
        self.setStyleSheet("""
            QWidget { background:#23272e; color:#fafbfc; }
            QTableWidget { background:#2c313c; font-size:14px; gridline-color:#444; }
            QHeaderView::section { background:#1e2329; color:white; font-weight:bold; border:1px solid #444; }
            QPushButton { background:#326fff; color:white; border-radius:8px; padding:6px 12px; margin:2px; }
            QPushButton:hover { background:#214bc4; }
        """)


# ──────────────────── ловушка необработанных исключений ───────────────────
def except_hook(cls, exc, tb):
    sys.__excepthook__(cls, exc, tb)
    QMessageBox.critical(None, "Ошибка", f"{exc}")


# ───────────────────────── запуск приложения ─────────────────────────
if __name__ == "__main__":
    sys.excepthook = except_hook
    app = QApplication(sys.argv)
    AppController().start()
    sys.exit(app.exec_())
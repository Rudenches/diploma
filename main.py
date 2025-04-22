import sys
import traceback
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QTextEdit, QScrollArea, QVBoxLayout, QHBoxLayout, QMessageBox
from PyQt5.QtCore import Qt
from parse.sel_parse import start_sel

class PyQtMain(QWidget):
    def __init__(self):
        super().__init__()
        self.url_entry = None
        self.dunc = None
        self.links_text = None
        self.percent_label = None  # Новый QLabel для процента
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 600, 400)
        self.setWindowTitle("Проверка работы функции")
        layout = QVBoxLayout()
        url_layout = QHBoxLayout()
        url_label = QLabel('Введите поиск:')
        url_layout.addWidget(url_label)
        self.url_entry = QTextEdit()
        self.url_entry.setFixedHeight(30)  # Ограничим высоту ввода
        url_layout.addWidget(self.url_entry)

        execute_button = QPushButton('Запустить')
        execute_button.clicked.connect(self.execute_test)
        url_layout.addWidget(execute_button)
        layout.addLayout(url_layout)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        self.links_text = QLabel()
        self.links_text.setOpenExternalLinks(True)
        self.links_text.setWordWrap(True)
        scroll_area.setWidget(self.links_text)
        layout.addWidget(scroll_area)
        self.percent_label = QLabel()
        layout.addWidget(self.percent_label)
        self.percent_label.setAlignment(Qt.AlignBottom | Qt.AlignLeft)
        self.setLayout(layout)
        self.show()

    def start_parse_main(self, url):
        try:
            print("Начало парсинга...")
            self.dunc = start_sel(url)
            if not self.dunc:
                result = "Ничего не найдено"
                self.percent_label.setText("")
            else:
                result = "<br><br>".join([f'<a href="{item["link"]}">{item["author"]}</a>' for item in self.dunc])
                self.calculate_and_display_percent()
            self.links_text.setText(result)
            print("Парсинг завершен успешно")
        except Exception as e:
            print("Ошибка при парсинге:", str(e))
            print("Трассировка ошибки:")
            traceback.print_exc()
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка при выполнении поиска:\n{str(e)}")
            self.links_text.setText("Произошла ошибка при выполнении поиска")
            self.percent_label.setText("")

    def calculate_and_display_percent(self):
        try:
            total_percent = []
            for item in self.dunc:
                try:
                    total_percent.append(float(item["author"].split()[-1].replace('%', '')))
                except Exception as e:
                    print(f"Ошибка при обработке процента: {str(e)}")
                    continue
            if total_percent:
                average_percent = sum(total_percent) / len(total_percent)
                self.percent_label.setText(f"Общий процент: {average_percent:.2f}%")
            else:
                self.percent_label.setText("Невозможно рассчитать процент")
        except Exception as e:
            print("Ошибка при расчете процента:", str(e))
            self.percent_label.setText("Ошибка при расчете процента")

    def execute_test(self):
        try:
            url = self.url_entry.toPlainText()
            if url:
                print(f"Запуск поиска для запроса: {url}")
                self.start_parse_main(url)
            else:
                print("Ошибка: Пустой поисковый запрос")
                QMessageBox.warning(self, "Предупреждение", "Пожалуйста, введите текст для поиска")
        except Exception as e:
            print("Ошибка при выполнении поиска:", str(e))
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка:\n{str(e)}")

if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        gui_app = PyQtMain()
        sys.exit(app.exec_())
    except Exception as e:
        print("Критическая ошибка приложения:", str(e))
        traceback.print_exc()
        QMessageBox.critical(None, "Критическая ошибка", f"Приложение завершило работу с ошибкой:\n{str(e)}")




import sys
import traceback
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QLineEdit, 
                            QScrollArea, QVBoxLayout, QHBoxLayout, QMessageBox, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor
from parse.sel_parse import start_sel

class PyQtMain(QWidget):
    def __init__(self):
        super().__init__()
        self.url_entry = None
        self.dunc = None
        self.links_text = None
        self.percent_label = None
        self.initUI()
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                font-family: 'Segoe UI', Arial;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
            QLineEdit {
                border: 2px solid #BDBDBD;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
                font-size: 14px;
                min-height: 20px;
            }
            QLineEdit:focus {
                border: 2px solid #2196F3;
            }
            QLabel {
                color: #424242;
            }
            QScrollArea {
                border: 2px solid #BDBDBD;
                border-radius: 4px;
                background-color: white;
            }
        """)

    def initUI(self):
        self.setGeometry(200, 200, 800, 600)
        self.setWindowTitle("Проверка источников статей")
        
        # Основной layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Заголовок
        title_label = QLabel("Анализатор источников")
        title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #1976D2;
            margin-bottom: 10px;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # Контейнер для поиска
        search_container = QFrame()
        search_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        search_layout = QVBoxLayout(search_container)

        # Метка поиска
        search_label = QLabel('Введите поисковый запрос:')
        search_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        search_layout.addWidget(search_label)

        # Контейнер для поля ввода и кнопки
        input_container = QHBoxLayout()
        
        # Поле ввода
        self.url_entry = QLineEdit()
        self.url_entry.setPlaceholderText("Введите текст для поиска...")
        self.url_entry.setMinimumHeight(40)
        input_container.addWidget(self.url_entry)

        # Кнопка
        execute_button = QPushButton('Начать поиск')
        execute_button.setFixedWidth(150)
        execute_button.clicked.connect(self.execute_test)
        input_container.addWidget(execute_button)
        
        search_layout.addLayout(input_container)
        main_layout.addWidget(search_container)

        # Контейнер для результатов
        results_container = QFrame()
        results_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        results_layout = QVBoxLayout(results_container)

        # Заголовок результатов
        results_label = QLabel("Результаты поиска:")
        results_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        results_layout.addWidget(results_label)

        # Область прокрутки
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        self.links_text = QLabel()
        self.links_text.setOpenExternalLinks(True)
        self.links_text.setWordWrap(True)
        self.links_text.setStyleSheet("""
            QLabel {
                padding: 10px;
                line-height: 1.5;
            }
            QLabel a {
                color: #2196F3;
                text-decoration: none;
            }
            QLabel a:hover {
                color: #1976D2;
                text-decoration: underline;
            }
        """)
        scroll_area.setWidget(self.links_text)
        results_layout.addWidget(scroll_area)
        
        # Метка процента
        self.percent_label = QLabel()
        self.percent_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #1976D2;
            padding: 10px;
        """)
        self.percent_label.setAlignment(Qt.AlignCenter)
        results_layout.addWidget(self.percent_label)
        
        main_layout.addWidget(results_container)
        self.setLayout(main_layout)
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
            url = self.url_entry.text()
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




import json
import sys
import pandas as pd
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog
from PyQt5.QtGui import QPixmap
import io
from VkGroupPlotter.design import Ui_Dialog  # Import the UI class from design.py
import datetime

class App(QWidget, Ui_Dialog):  # Subclass Ui_Dialog to integrate the UI
    def __init__(self):
        super().__init__()
        self.setupUi(self)  # Setup the UI from design.py
        self.title = 'VkGroupPlotter.exe'
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(100, 100, 985, 794)  # Adjust to match the UI size

        # Connect buttons from design.py to their respective methods
        self.button.clicked.connect(self.openFileNameDialog)
        self.sex_button.clicked.connect(self.plot_sex_distribution)
        self.age_button.clicked.connect(self.plot_age_distribution)
        self.personal_button.clicked.connect(self.plot_personal_distribution)
        self.education_button.clicked.connect(self.plot_education_distribution)

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        fileName, _ = QFileDialog.getOpenFileName(self, "Выбрать CSV файл", "", "CSV Files (*.csv);;All Files (*)", options=options)
        if fileName:
            self.csv_file = fileName
            self.button.setStyleSheet("background-color: rgb(0, 255, 0);")
            self.graphic_label.clear()  # Clear label text if any

    def plot_sex_distribution(self):
        self.button.setStyleSheet("")

        if hasattr(self, 'csv_file'):
            df = pd.read_csv(self.csv_file)
            sex_counts = df['sex'].value_counts()

            # Преобразуем индексы в читаемые строки
            sex_counts.index = sex_counts.index.map(lambda
                                                        x: "Мужчины" if x == 2 or x == 'Мужской' else "Женщины" if x == 1 or x == 'Женский' else "Пол не указан")

            # Создаем столбчатую диаграмму
            fig, ax = plt.subplots()
            sex_counts.plot(kind='bar', ax=ax, color=['blue', 'pink', 'gray'])

            ax.set_xlabel('Пол')
            ax.set_ylabel('Количество')
            ax.set_title('Распределение по полу')

            # Поворачиваем текст на оси X
            ax.set_xticklabels(ax.get_xticklabels(), rotation=0)

            # Save the plot to a PNG file in memory
            buffer = io.BytesIO()
            fig.savefig(buffer, format='png')
            buffer.seek(0)

            # Convert PNG buffer to QPixmap
            pixmap = QPixmap()
            pixmap.loadFromData(buffer.getvalue())

            # Display QPixmap in the graphic_label QLabel from design.py
            self.graphic_label.setPixmap(pixmap)

        else:
            self.graphic_label.setText('Пожалуйста, выберите CSV файл.')
    def plot_age_distribution(self):
        self.button.setStyleSheet("")
        if hasattr(self, 'csv_file'):
            df = pd.read_csv(self.csv_file)
            current_year = datetime.datetime.now().year

            def calculate_age(bdate):
                try:
                    birth_date = datetime.datetime.strptime(bdate, "%d.%m.%Y")
                    return current_year - birth_date.year
                except (ValueError, TypeError):
                    return None

            df['age'] = df['bdate'].apply(calculate_age)
            df = df.dropna(subset=['age'])

            bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
            age_distribution = pd.cut(df['age'], bins).value_counts().sort_index()

            fig, ax = plt.subplots(figsize=(8, 6))  # Set the figure size to 8x6 inches
            age_distribution.plot(kind='bar', ax=ax, color='skyblue')
            ax.set_xlabel('')
            ax.set_ylabel('Количество')
            ax.set_xticklabels([f'{int(bin.left)}-{int(bin.right)}' for bin in age_distribution.index])

            # Save the plot to a PNG file in memory
            buffer = io.BytesIO()
            fig.savefig(buffer, format='png')
            buffer.seek(0)

            # Convert PNG buffer to QPixmap
            pixmap = QPixmap()
            pixmap.loadFromData(buffer.getvalue())

            # Display QPixmap in the graphic_label QLabel from design.py
            self.graphic_label.setPixmap(pixmap)

        else:
            self.graphic_label.setText('Пожалуйста, выберите CSV файл.')

    def plot_personal_distribution(self):
        self.button.setStyleSheet("")
        if hasattr(self, 'csv_file'):
            df = pd.read_csv(self.csv_file)
            def parse_personal(x):
                try:
                    return json.loads(x.replace("'", '"'))
                except json.JSONDecodeError:
                    return None

            personal_data = df['personal'].dropna().apply(parse_personal).dropna()
            life_main_values = personal_data.apply(lambda x: x.get('life_main', None))

            life_main_labels = {
                0: 'Не указано',
                1: 'Семья и дети',
                2: 'Карьера и деньги',
                3: 'Развлечения и отдых',
                4: 'Наука и исследования',
                5: 'Совершенствование мира',
                6: 'Саморазвитие',
                7: 'Красота и искусство',
                8: 'Слава и влияние'
            }

            life_main_counts = life_main_values.value_counts().sort_index()
            life_main_counts.index = life_main_counts.index.map(life_main_labels)

            fig, ax = plt.subplots(figsize=(8, 6))  # Set the figure size to 8x6 inches
            life_main_counts.plot(kind='bar', ax=ax, color='skyblue')
            ax.set_ylabel('Количество')
            ax.set_xticklabels(life_main_counts.index, rotation=15, ha='right', fontsize=9)

            # Save the plot to a PNG file in memory
            buffer = io.BytesIO()
            fig.savefig(buffer, format='png')
            buffer.seek(0)

            # Convert PNG buffer to QPixmap
            pixmap = QPixmap()
            pixmap.loadFromData(buffer.getvalue())

            # Display QPixmap in the graphic_label QLabel from design.py
            self.graphic_label.setPixmap(pixmap)

        else:
            self.graphic_label.setText('Пожалуйста, выберите CSV файл.')

    def plot_education_distribution(self):
        self.button.setStyleSheet("")

        if hasattr(self, 'csv_file'):
            df = pd.read_csv(self.csv_file)
            education_counts = df['education_status'].value_counts()

            # Создаем столбчатую диаграмму
            fig, ax = plt.subplots(figsize=(7, 5))
            education_counts.plot(kind='bar', ax=ax, color='skyblue')

            ax.set_xlabel('')
            ax.set_ylabel('Количество')

            # Поворачиваем текст на оси X
            ax.set_xticklabels(ax.get_xticklabels(), rotation=90, fontsize=8)
            plt.tight_layout()
            # Save the plot to a PNG file in memory
            buffer = io.BytesIO()
            fig.savefig(buffer, format='png')
            buffer.seek(0)

            # Convert PNG buffer to QPixmap
            pixmap = QPixmap()
            pixmap.loadFromData(buffer.getvalue())

            # Display QPixmap in the graphic_label QLabel from design.py
            self.graphic_label.setPixmap(pixmap)
        else:
            self.graphic_label.setText('Пожалуйста, выберите CSV файл.')



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())

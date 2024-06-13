import io
import sys

from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget
import requests
import matplotlib.pyplot as plt
from collections import Counter
from design import Ui_Dialog


def get_vk_group_info(group_id, access_token):
    url = 'https://api.vk.com/method/groups.getById'
    params = {
        'group_id': group_id,
        'fields': 'activity',
        'access_token': access_token,
        'v': '5.131'
    }
    response = requests.get(url, params=params)
    data = response.json()
    if 'error' in data:
        return None
    group_info = data['response'][0]
    return group_info

class App(QWidget, Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.title = 'VkGroupsPlotter'
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(100, 100, 1370, 794)
        self.pushButton.clicked.connect(self.analyze_groups)

    def analyze_groups(self):
        group_ids = self.textEdit.toPlainText().strip().split('\n')
        access_token = 'af994a41af994a41af994a41a0ac81d19caaf99af994a41c9f125026e10d960d0daabc8'  # Замените на ваш access token
        activities = []

        for group_id in group_ids:
            if "http" in group_id:
                group_info = get_vk_group_info(group_id.strip().split("/")[-1], access_token)
            else:
                group_info = get_vk_group_info(group_id.strip(), access_token)
            if group_info:
                activity = group_info.get('activity', 'No activity information')
                activities.append(activity)
            else:
                # QMessageBox.warning(self, 'Ошибка', f'Не удалось получить данные для группы {group_id}')
                pass

        if activities:
            self.show_bar_chart(activities)

    def show_bar_chart(self, activities):
        activity_counts = Counter(activities)
        activities = list(activity_counts.keys())
        counts = list(activity_counts.values())

        fig, ax = plt.subplots(figsize=(8, 6))
        ax.bar(activities, counts)
        ax.set_xlabel('Тематика')
        ax.set_ylabel('Количество')
        ax.set_title('Распределение тематик сообществ')
        ax.set_xticklabels(ax.get_xticklabels(), rotation=90, fontsize=8)
        plt.tight_layout()

        buffer = io.BytesIO()
        fig.savefig(buffer, format='png')
        buffer.seek(0)

        pixmap = QPixmap()
        pixmap.loadFromData(buffer.getvalue())
        self.label.setPixmap(pixmap)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())

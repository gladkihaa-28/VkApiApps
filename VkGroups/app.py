import sys
import vk_api
import pandas as pd
import requests
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QProgressBar, QLabel, QFileDialog
from PyQt5.QtCore import Qt, QThread, pyqtSignal


def get_group_id(group_name, access_token):
    url = 'https://api.vk.com/method/utils.resolveScreenName'
    params = {
        'screen_name': group_name,
        'access_token': access_token,
        'v': '5.131'
    }
    with requests.get(url, params=params) as response:
        data = response.json()
        if 'response' in data and data['response']['type'] == 'group':
            return data['response']['object_id']
        else:
            raise ValueError(f"Error fetching group ID: {data}")


class VKThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(list)

    def __init__(self, group_name, filename, access_token):
        super().__init__()
        self.group_name = group_name
        self.filename = filename
        self.access_token = access_token

    def run(self):
        try:
            group_id = get_group_id(self.group_name, self.access_token)
            members = self.get_group_members(group_id)
            save_to_csv(members, self.filename)
            self.finished.emit(members)
        except Exception as e:
            print(f"Error: {e}")
            self.finished.emit([])

    def get_group_members(self, group_id):
        vk_session = vk_api.VkApi(token=self.access_token)
        vk = vk_session.get_api()

        members = []
        offset = 0
        count = 1000

        while True:
            response = vk.groups.getMembers(group_id=group_id, offset=offset, count=count, fields='id,first_name,last_name,bdate,country,home_town,sex,domain,education,personal')
            members.extend(response['items'])
            offset += count
            self.progress.emit(int(offset / response['count'] * 100))
            print(f"{response['count']}/{offset}")
            if offset >= response['count']:
                break

        return members


def save_to_csv(data, filename):
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False, encoding='utf-8')


class VKApp(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()
        self.access_token = 'af994a41af994a41af994a41a0ac81d19caaf99af994a41c9f125026e10d960d0daabc8'

    def initUI(self):
        self.setWindowTitle('VK Group Members Downloader')
        self.setGeometry(100, 100, 400, 200)

        self.layout = QVBoxLayout()

        self.group_name_label = QLabel('Название сообщества:')
        self.layout.addWidget(self.group_name_label)

        self.group_name_input = QLineEdit(self)
        self.layout.addWidget(self.group_name_input)

        self.filename_label = QLabel('Имя файла:')
        self.layout.addWidget(self.filename_label)

        self.filename_input = QLineEdit(self)
        self.layout.addWidget(self.filename_input)

        self.start_button = QPushButton('Начать процесс', self)
        self.start_button.clicked.connect(self.start_process)
        self.layout.addWidget(self.start_button)

        self.progress = QProgressBar(self)
        self.layout.addWidget(self.progress)

        self.setLayout(self.layout)

    def start_process(self):
        group_name = self.group_name_input.text()
        filename = self.filename_input.text()
        if group_name and filename:
            self.thread = VKThread(group_name, filename, self.access_token)
            self.thread.progress.connect(self.update_progress)
            self.thread.finished.connect(self.process_finished)
            self.thread.start()

    def update_progress(self, value):
        self.progress.setValue(value)

    def process_finished(self, members):
        if members:
            self.progress.setValue(100)
            print(f"Total members: {len(members)}")
        else:
            self.progress.setValue(0)
            print("An error occurred during the process.")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = VKApp()
    ex.show()
    sys.exit(app.exec_())

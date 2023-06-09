import os
import requests
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QTextBrowser, QVBoxLayout, QWidget, QFileDialog
from PyQt5.QtCore import Qt, QMetaObject, QThread, pyqtSignal
from threading import Thread

class FileTransferApp(QMainWindow):
    updateChatSignal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle('File Transfer App')
        self.setGeometry(100, 100, 600, 400)

        self.chat_browser = QTextBrowser()
        self.nickname_label = QLabel('Nickname:')
        self.nickname_input = QLineEdit()
        self.nickname_button = QPushButton('Set Nickname')
        self.nickname_button.clicked.connect(self.set_nickname)
        self.upload_button = QPushButton('Upload File')
        self.upload_button.clicked.connect(self.upload_file)
        self.download_button = QPushButton('Download File')
        self.download_button.clicked.connect(self.download_file)

        layout = QVBoxLayout()
        layout.addWidget(self.chat_browser)
        layout.addWidget(self.nickname_label)
        layout.addWidget(self.nickname_input)
        layout.addWidget(self.nickname_button)
        layout.addWidget(self.upload_button)
        layout.addWidget(self.download_button)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.nickname = None
        self.available_files = []

        self.updateChatSignal.connect(self.update_chat)
        self.updateChatSignal.emit()

    def update_chat(self):
        url = 'http://localhost:5000/get-files'
        response = requests.get(url)
        if response.ok:
            files = response.json().get('files', [])
            self.chat_browser.clear()
            self.available_files = files
            for file in files:
                filename = file['filename']
                uploader = file['uploader']
                self.chat_browser.append(f'File: {filename} | Uploader: {uploader}')
        else:
            self.chat_browser.append('Error fetching file list')

    def upload_file(self):
        if self.nickname:
            file_path, _ = QFileDialog.getOpenFileName(self, 'Upload File', '', 'All Files (*.*)')
            if file_path:
                url = 'http://localhost:5000/send-file'
                files = {'file': open(file_path, 'rb')}
                data = {'nickname': self.nickname}

                def upload():
                    response = requests.post(url, files=files, data=data)
                    if response.ok:
                        self.chat_browser.append('File uploaded successfully')
                        self.updateChatSignal.emit()
                    else:
                        self.chat_browser.append('Error uploading file')

                thread = Thread(target=upload)
                thread.start()
        else:
            self.chat_browser.append('Please set a nickname first')

    def download_file(self):
        if self.nickname:
            if self.available_files:
                selected_file = QFileDialog.getSaveFileName(self, 'Download File', '', 'All Files (*.*)')[0]
                if selected_file:
                    selected_file = os.path.basename(selected_file)
                    if selected_file in [file['filename'] for file in self.available_files]:
                        url = f'http://localhost:5000/download-file/{selected_file}'

                        def download():
                            response = requests.get(url)
                            if response.ok:
                                file_path, _ = QFileDialog.getSaveFileName(self, 'Save File', selected_file)
                                with open(file_path, 'wb') as file:
                                    file.write(response.content)
                                self.chat_browser.append('File downloaded successfully')
                            else:
                                self.chat_browser.append('Error downloading file')

                        thread = Thread(target=download)
                        thread.start()
                    else:
                        self.chat_browser.append('Selected file is not available')
            else:
                self.chat_browser.append('No files available for download')
        else:
            self.chat_browser.append('Please set a nickname first')

    def set_nickname(self):
        nickname = self.nickname_input.text()
        if nickname:
            self.nickname = nickname
            self.nickname_label.setText(f'Nickname: {self.nickname}')
            self.nickname_input.clear()
            self.chat_browser.append(f'Nickname set: {self.nickname}')
        else:
            self.chat_browser.append('Please enter a nickname')

if __name__ == '__main__':
    app = QApplication([])
    window = FileTransferApp()
    window.show()
    app.exec_()

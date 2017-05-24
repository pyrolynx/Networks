from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit,                       QLabel, QHBoxLayout, QPushButton
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from requests import Session
from json import loads
import os
from hashlib import md5
import re

class VkApi(Session):
    class VkApiError(Exception):
        pass
    
    URL = 'https://api.vk.com/method/'
    
    def __init__(self):
        super().__init__()
    
    def getId(self, short_name):
        if not short_name:
            return 
        response = loads(self.get(self.URL + \
            'users.get?user_ids={0}'.format(short_name)).text)
        if 'error' in response.keys():
            raise VkApi.VkApiError()
        return response['response'][0]['uid']
    
    def getFriends(self, user_id):
        response = loads(self.get(self.URL + \
            'friends.get?user_id={0}&fields=photo_200_orig'.format(user_id)).text)
        if 'error' in response.keys():
            raise VkApi.VkApiError()
        return response['response']


class VKFriendBrowser(QWidget):
    API = VkApi()

    def __init__(self):
        super().__init__()
        self.init_UI()
        self.userId = None
        self.friendsData = None
        self.friendIndex = 0

    def init_UI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        lineLayout = QHBoxLayout()
        layout.addLayout(lineLayout)
        self.linkLabel = QLabel('vk.com/id')
        lineLayout.addWidget(self.linkLabel)
        self.userIdEdit = QLineEdit()
        self.userIdEdit.textChanged.connect(self.onLoad)
        lineLayout.addWidget(self.userIdEdit)
        self.avatarLabel = QLabel()
        layout.addWidget(self.avatarLabel)
        self.nameLabel = QLabel()
        layout.addWidget(self.nameLabel, Qt.AlignCenter)
        buttonLayout = QHBoxLayout()
        layout.addLayout(buttonLayout)
        leftButton = QPushButton('Previous')
        leftButton.clicked.connect(self.previousFriend)
        buttonLayout.addWidget(leftButton)
        layout.addLayout(buttonLayout)
        rightButton = QPushButton('Next')
        rightButton.clicked.connect(self.nextFriend)
        buttonLayout.addWidget(rightButton)
        self.resize(210, 280)
        self.move(200, 200)
    
    def updateInfo(self):
        if self.friendsData is None:
            return
        firstname = self.friendsData[self.friendIndex]['first_name']
        lastname = self.friendsData[self.friendIndex][
            'last_name']
        picture = self.API.get(self.friendsData[self.friendIndex][
            'photo_200_orig']).content
        pixmap = QPixmap() 
        QPixmap.loadFromData(pixmap, picture)
        self.avatarLabel.setPixmap(pixmap)
        self.nameLabel.setText("{0} {1}".format(firstname, lastname))

    def onLoad(self):
        try:
            id = self.userIdEdit.text()
            if re.match(r'\d+', id) is None:
                print('catch short name!')
                id = self.API.getId(id)
            self.userId = id
            print(id)
            self.friendsData = self.API.getFriends(id)
            self.friendIndex = 0
        except VkApi.VkApiError:
            print('error')
            pass
        self.updateInfo()

    def nextFriend(self):
        if self.friendsData is None:
            return
        self.friendIndex+=1
        if self.friendIndex > len(self.friendsData):
            self.friendIndex = 0
        self.updateInfo()

    def previousFriend(self):
        if self.friendsData is None:
            return
        self.friendIndex-=1
        if self.friendIndex < 0:
            self.friendIndex = len(self.friendsData) - 1
        self.updateInfo()
        

def main():
    # api = VkApi()
    # id = api.getId('brizzzz')
    # api.getFriends(id)
    app = QApplication([])
    browser = VKFriendBrowser()
    browser.show()
    app.exec()

if __name__ == '__main__':
    main()
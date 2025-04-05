import os
from pygame import mixer


class Player:
    def __init__(self):
        self.mixer = mixer
        self.mixer.init()
        self.root = "./song"  # 播放文件夹
        self.song_name = ""  # 当前歌曲名

    def start(self):
        self.mixer.music.unpause()

    def stop(self):
        self.mixer.music.pause()

# coding := utf-8

from PyQt5.QtWidgets import (QApplication, QPushButton,
        QVBoxLayout, QWidget, QFileDialog)
from multiprocessing import Process, Queue
import sys, glob, time, os
from pprint import pprint
from winsound import PlaySound, SND_FILENAME

class MyWidget(QWidget):
    
    def __init__(self):
        super().__init__()
        self.initUI()


    def initUI(self):
        self.play_process = None
        self.infos = []
        self.status_q = Queue()
        self.result_q = Queue()

        self.resize(320, 180)

        self.setWindowTitle('音频播放小程序')
        mainLayout = QVBoxLayout()

        importButton = QPushButton("import")
        mainLayout.addWidget(importButton)

        playButton = QPushButton("play")
        mainLayout.addWidget(playButton)

        outButton = QPushButton("save")
        mainLayout.addWidget(outButton)

        self.pauseButton = QPushButton("pause")
        mainLayout.addWidget(self.pauseButton)

        playButton.clicked.connect(self.play)
        importButton.clicked.connect(self.import_files)
        outButton.clicked.connect(self.save)
        self.pauseButton.clicked.connect(self.pause)

        self.setLayout(mainLayout)

    def import_files(self):
        self.wavs = []
        self.fname_text = {}

        dr = QFileDialog.getExistingDirectory(self)
        for f in glob.iglob(dr+'\\*.wav'):
            self.wavs.append(f)

        for f in glob.iglob(dr+'\\*.txt'):
            fname = f.split('\\')[-1].split('.')[0]
            with open(f, encoding='utf8') as fp:
                self.fname_text[fname] = fp.readline().strip()
        # pprint(self.fname_text)

        self.infos = []

    def play(self):
        if self.play_process and self.play_process.is_alive():
            return

        p = Process(target=play_in_background, args=(self.wavs, self.status_q, self.result_q))
        p.start()
        self.play_process = p

    def save(self):
        if self.play_process and self.play_process.is_alive() and self.pauseButton.text() == 'pause':
            return

        while not self.result_q.empty():
            fname, start, end = self.result_q.get()
            text = self.fname_text.get(fname)
            self.infos.append([fname, text, start, end])

        if self.infos:
            out_file = QFileDialog.getSaveFileName(self)[0]
            self.write_to_file(out_file)

    def write_to_file(self, f):
        txt_item = 'index %s :\n音频名称 : %s\n音频内容 : %s\n起点 : %s\n终点 : %s\n'
        txt = ''
        for i, (fname, text, start, end) in enumerate(self.infos):
            txt += txt_item % (i, fname, text, start, end)

        with open(f, 'w', encoding='utf8') as fp:
            fp.write(txt)

    def pause(self):
        if self.status_q.empty():
            self.status_q.put(0)
            self.pauseButton.setText('continue')
        else:
            self.status_q.get()
            self.pauseButton.setText('pause')

def play_in_background(wavls, status_q, result_q):
    start_stamp = time.time()
    for wav in wavls:
        while not status_q.empty():
            time.sleep(0.1)
        start = time.time()
        PlaySound(wav, SND_FILENAME)
        end = time.time()

        result_q.put([wav.split('\\')[-1].split('.')[0], start-start_stamp, end-start_stamp])

if __name__ == '__main__':
    myapp = QApplication(sys.argv)
    mywidget = MyWidget()
    mywidget.show()
    sys.exit(myapp.exec_())

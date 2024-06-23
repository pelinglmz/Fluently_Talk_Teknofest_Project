from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from ui_dafgen import Ui_DAFGen

from pyaudio import PyAudio, paFloat32
from math import floor
import time
import numpy as np
import noisereduce as nr

import sys


class Worker(QThread):
    _trigger = pyqtSignal(float)

    def __init__(self, bufferSize, streamIn, streamOut):
        QThread.__init__(self)
        self._bufferSize = bufferSize
        self._streamIn = streamIn
        self._streamOut = streamOut

    def __del__(self):
        self.wait()

    def _genDAF(self):
        while self._streamIn.is_active():
            start = time.perf_counter()
            audioData = self._streamIn.read(self._bufferSize)

            # Gürültü azaltma işlemi
            audio_array = np.frombuffer(audioData, dtype=np.float32)
            reduced_noise_audio = nr.reduce_noise(y=audio_array, sr=44100)
            audioData = reduced_noise_audio.tobytes()

            self._streamOut.write(audioData)
            actualDelay = time.perf_counter() - start
            self._trigger.emit(actualDelay)

    def run(self):
        self._genDAF()


class MainApp(QMainWindow, Ui_DAFGen):
    _CHANNELS = 2
    _RATE = 44100

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.stopButton.setEnabled(False)
        self._updateDelay()

        self.delaySlider.valueChanged.connect(self._updateDelay)
        self.startButton.clicked.connect(self._startCapture)
        self.stopButton.clicked.connect(self._stopCapture)
        self.quitButton.clicked.connect(QApplication.quit)

    def _updateDelay(self):
        self.delayEdit.setPlainText(str(self.delaySlider.value()) + ' ms')

    def _startCapture(self):
        bufferSize = floor(self.delaySlider.value() / 1000 * self._RATE)
        device = PyAudio()

        try:
            streamIn = device.open(
                format=paFloat32,
                channels=self._CHANNELS,
                rate=self._RATE,
                input=True,
                frames_per_buffer=bufferSize
            )

            streamOut = device.open(
                format=paFloat32,
                channels=self._CHANNELS,
                rate=self._RATE,
                output=True,
                frames_per_buffer=bufferSize
            )

        except OSError as e:
            QMessageBox.critical(self, 'Error', 'No input/output device found! Connect and rerun.')
            return

        self._workerThread = Worker(bufferSize, streamIn, streamOut)
        self._workerThread._trigger.connect(self._updateActualDelay)

        self.startButton.setEnabled(False)
        self.delaySlider.setEnabled(False)
        self.stopButton.setEnabled(True)

        self._workerThread.start()

    def _stopCapture(self):
        self._workerThread.terminate()

        self.actualDelayEdit.clear()
        self.startButton.setEnabled(True)
        self.delaySlider.setEnabled(True)
        self.stopButton.setEnabled(False)

    def _updateActualDelay(self, t):
        newValue = floor(t * 1000)
        self.actualDelayEdit.setPlainText(str(newValue) + ' ms')


def main():
    app = QApplication(sys.argv)
    win = MainApp()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

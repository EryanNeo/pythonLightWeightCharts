import pandas as pd
from pymongo import MongoClient
from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QComboBox, QLabel, QDoubleSpinBox
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import QTimer
from lightweight_charts.widgets import QtChart
from datetime import timedelta
from sectors import nifty50, niftyNext50, niftyFno, nifty500
import time

class App:
    def __init__(self):
        self.mongo = MongoClient('localhost:27017')
        self.initial = 10
        self.is_paused = False
        self.speed = 500
        self.timer = QTimer()
        self.app = QApplication([])
        self.app.setApplicationName('Neo Charting App')
        self.window = QMainWindow()
        self.layout = QVBoxLayout()
        self.h_layout = QHBoxLayout()
        self.widget = QWidget()
        self.widget.setLayout(self.layout)
        self.window.resize(1920, 1080)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.chart = QtChart(self.widget)
        self.chart.time_scale(right_offset=10)
        # self.df, self.bb = self.load_data()
        self.window.setCentralWidget(self.widget)
        self.timer.timeout.connect(self.update_chart)
        self.timer.start(self.speed)
        # Adding buttons
        self.pause_button = QPushButton("Play" if self.is_paused else "Pause")
        self.pause_button.clicked.connect(self.toggle_pause)
        self.restart_button = QPushButton("Restart")
        self.restart_button.clicked.connect(self.restart)
        self.next5_button = QPushButton('>')
        self.next5_button.clicked.connect(self.next5)
        self.next10_button = QPushButton('>>')
        self.next10_button.clicked.connect(self.next10)
        self.prev5_button = QPushButton('<')
        self.prev5_button.clicked.connect(self.prev5)
        self.prev10_button = QPushButton('<<')
        self.prev10_button.clicked.connect(self.prev10)
        self.speed_increase_button = QPushButton('+')
        self.speed_increase_button.clicked.connect(self.increase)
        self.speed_decrease_button = QPushButton('-')
        self.speed_decrease_button.clicked.connect(self.decrease)
        self.h_layout.addWidget(self.prev10_button)
        self.h_layout.addWidget(self.prev5_button)
        self.h_layout.addWidget(self.pause_button)
        self.h_layout.addWidget(self.restart_button)
        self.h_layout.addWidget(self.next5_button)
        self.h_layout.addWidget(self.next10_button)
        self.h_layout.addWidget(self.speed_decrease_button)
        self.h_layout.addWidget(self.speed_increase_button)
        self.layout.addLayout(self.h_layout)
        # Adding Combobox
        self.combo = QComboBox(self.widget)     # self.combo = QComboBox(self.widget)
        self.combo.addItems(['Nifty50', 'NiftyNext50', 'NiftyFNO', 'Nifty500'])
        self.label = QLabel("Index")    # self.label = QLabel("Index", self.widget)
        self.combo.setCurrentIndex(0)
        self.combo2 = QComboBox()
        if self.combo.currentIndex() == 0:
            self.combo2.addItems(nifty50)
        self.combo2.setCurrentIndex(0)
        self.label2 = QLabel("Script")    
        self.combo3 = QComboBox()
        if self.combo.currentIndex() == 0:
            self.combo3.addItems(['5M', '15M', 'D'])
        self.combo3.setCurrentIndex(0)
        self.label3 = QLabel("Timeframe")
        self.input_speed = QDoubleSpinBox()
        self.input_speed.setRange(0.1, 30)
        self.input_speed.setValue(0.5)
        self.input_speed.setSingleStep(0.1)
        self.label_4 = QLabel(str(int(self.speed)) + ' ms')
        self.input_speed.valueChanged.connect(self.speed_changed)
        # self.label_4 = QLabel(str(int(self.speed)) + ' ms')
        # self.label5 = QLabel(self.input_speed.value())
        # Adding functionality to Dropdown menu
        self.combo.currentIndexChanged.connect(self.index_changed)
        self.combo2.currentIndexChanged.connect(self.script_changed)
        self.combo3.currentIndexChanged.connect(self.timeframe_changed)
        self.h_layout2 = QHBoxLayout()
        self.h_layout2.addWidget(self.label)
        self.h_layout2.addWidget(self.combo)
        self.h_layout2.addWidget(self.label2)
        self.h_layout2.addWidget(self.combo2)
        self.h_layout2.addWidget(self.label3)
        self.h_layout2.addWidget(self.combo3)
        self.h_layout2.addWidget(self.label_4)
        self.h_layout2.addWidget(self.input_speed)
        # self.h_layout2.addWidget(self.label5)
        self.layout.addLayout(self.h_layout2)
        #  Adding chart to layout
        self.df = None
        self.chart_load()
        self.layout.addWidget(self.chart.get_webview())

    def run(self):
        self.window.show()
        self.app.exec()

    def chart_load(self):
        self.df = self.load_data()
        self.chart.set(self.df.iloc[:self.initial])
    
    def chart_load_2(self):
        self.chart.set(self.df.iloc[:self.initial])

    def load_data(self):
        # df = pd.read_csv('data.csv')
        self.script = self.combo2.currentText()
        self.timeFrame = self.combo3.currentText()
        if self.timeFrame == '5M':
            self.timeFrame_1 = '5Minute'
        elif self.timeFrame == '15M':
            self.timeFrame_1 = '15Minute'
        elif self.timeFrame == 'D':
            self.timeFrame_1 = 'Daily'
        df = pd.DataFrame(list(self.mongo[self.script][self.timeFrame_1].find()))
        if not df.empty:
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df['time'] = df['time'] + timedelta(hours = 5.5)
            # bb = ta.bbands(close = df['close'], length = 20, std = 2).bfill()
        self.initial = int(len(df) * 0.5)
        if len(df) - self.initial > 1000:
            self.initial = len(df) - 1000
        elif len(df) - self.initial < 100:
            self.initial = self.initial - 200 
        return df
    
    def update_chart(self):
        if not self.is_paused:
            if self.initial >= len(self.df):
                self.toggle_pause()
                return
            self.chart.update(self.df.iloc[self.initial])
            self.initial += 1
        else:
            self.toggle_pause()
            QApplication.quit()
    
    def toggle_pause(self):
        if self.is_paused:
            self.is_paused = False
            self.timer.start(self.speed)
        else:
            self.is_paused = True
            self.timer.stop()
        self.pause_button.setText('Play' if self.is_paused else 'Pause')
        

    def restart(self):
        self.toggle_pause()
        self.chart_load()
        
    def next5(self):
        self.initial += 5
        if self.initial >= len(self.df):
            self.initial = len(self.df)
        self.chart_load_2()

    def next10(self):
        self.initial += 10
        if self.initial >= len(self.df):
            self.initial = len(self.df)
        self.chart_load_2()
            
    def prev5(self):
        self.initial -= 5
        if self.initial < 0:
            self.initial = 1
        self.chart_load_2()

    def prev10(self):
        self.initial -= 10
        if self.initial < 0:
            self.initial = 1
        self.chart_load_2()
    
    def decrease(self):
        self.timer.stop()
        self.speed += 500
        if self.speed > 5000:
            self.speed = 5000
        # print(self.speed)
        self.timer.start(self.speed)
        self.label_4.setText(str(int(self.speed)) + ' ms')
    
    def increase(self):
        self.timer.stop()
        self.speed -= 500
        if self.speed <500:
            self.speed = 500
        # print(self.speed)
        self.timer.start(self.speed)
        self.label_4.setText(str(int(self.speed)) + ' ms')
        
    def index_changed(self):
        self.combo2.clear()
        if self.combo.currentIndex() == 0:
            self.combo2.addItems(nifty50)
        elif self.combo.currentIndex() == 1:
            self.combo2.addItems(niftyNext50)
        elif self.combo.currentIndex() == 2:
            self.combo2.addItems(niftyFno)
        elif self.combo.currentIndex() == 3:
            self.combo2.addItems(nifty500)
            self.combo3.clear()
            self.combo3.addItem('D')
            self.combo3.setCurrentIndex(0)
            
        self.combo2.setCurrentIndex(0)
            
    def script_changed(self):
        # time.sleep(5)
        # print(self.combo2.currentText())
        # print(self.combo2.currentData())
        self.chart_load()
    
    def timeframe_changed(self):
        # time.sleep(5)
        # print(self.combo3.currentText())
        self.chart_load()
    
    def speed_changed(self):
        self.timer.stop()
        self.speed = self.input_speed.value() * 1000
        # if self.speed <500:
        #     self.speed = 500
        # print(self.speed)
        self.timer.start(self.speed)
        self.label_4.setText(str(int(self.speed)) + ' ms')
        
                
if __name__ == '__main__':
    App().run()
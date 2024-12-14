import pandas as pd
from pymongo import MongoClient
from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QComboBox, QLabel, QDoubleSpinBox, QSpinBox
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import QTimer, Qt
from lightweight_charts.widgets import QtChart
from datetime import timedelta
from sectors import nifty50, niftyNext50, niftyFno, nifty500
import time
import json

class NoKeyEventComboBox(QComboBox):
    def keyPressEvent(self, event):
        # Ignore all key events for the combo box (disabling default key events)
        event.ignore()

class App:
    def __init__(self):
        self.length = None
        # self.start = None
        # self.end = None
        self.indexes = ['Nifty50', 'NiftyNext50', 'NiftyFNO', 'Nifty500']
        self.timeFrames = ['5M', '15M', 'D']
        self.alt_timeFrames = ['D']
        self.file = 'chart.json'
        self.data = self.read_json()
        self.index = self.data['index']
        self.script = self.data['script']
        self.timeFrame = self.data['timeFrame']
        self.speed = self.data['speed']
        self.initial = self.data['initial']
        self.mongo = MongoClient('localhost:27017')
        self.initial = 10
        self.is_paused = self.data['is_paused']
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
        self.combo = NoKeyEventComboBox()  
        self.combo2 = NoKeyEventComboBox()
        self.combo3 = NoKeyEventComboBox()
        # self.combo = QComboBox()     # self.combo = QComboBox(self.widget)
        self.combo.addItems(self.indexes)
        self.label = QLabel("Index")    # self.label = QLabel("Index", self.widget)
        self.combo.setCurrentIndex(self.indexes.index(self.data['index']))
        # self.combo2 = QComboBox()
        if self.combo.currentIndex() == 0:
            self.combo2.addItems(nifty50)
            self.combo2.setCurrentIndex(nifty50.index(self.data['script']))
        elif self.combo.currentIndex() == 1:
            self.combo2.addItems(niftyNext50)
            self.combo2.setCurrentIndex(niftyNext50.index(self.data['script']))
        elif self.combo.currentIndex() == 2:
            self.combo2.addItems(niftyFno)
            self.combo2.setCurrentIndex(niftyFno.index(self.data['script']))
        elif self.combo.currentIndex() == 3:
            self.combo2.addItems(nifty500)
            self.combo2.setCurrentIndex(nifty500.index(self.data['script']))
        self.label2 = QLabel("Script")    
        # self.combo3 = QComboBox()
        if self.combo.currentIndex() != 3:
            self.combo3.addItems(self.timeFrames)
            self.combo3.setCurrentIndex(self.timeFrames.index(self.data['timeFrame']))
        else:
            self.combo3.addItems(self.alt_timeFrames)
            self.combo3.setCurrentIndex(self.alt_timeFrames.index(self.data['timeFrame']))
        self.label3 = QLabel("Timeframe")
        self.input_speed = QDoubleSpinBox()
        self.input_speed.setRange(0.1, 30)
        self.input_speed.setValue(self.data['speed'])
        self.input_speed.setSingleStep(0.1)
        self.label_4 = QLabel(str(int(self.speed)) + ' ms')
        self.input_speed.valueChanged.connect(self.speed_changed)
        # self.label_4 = QLabel(str(int(self.speed)) + ' ms')
        # self.label5 = QLabel(self.input_speed.value())
        # Adding functionality to Dropdown menu
        self.combo.currentIndexChanged.connect(self.index_changed)
        self.combo2.currentIndexChanged.connect(self.script_changed)
        self.combo3.currentIndexChanged.connect(self.timeframe_changed)
        
        # Other Widgets
        self.length_label = QLabel('Length')
        self.length_button = QSpinBox()
        self.length_button.setSingleStep(100)
        self.h_layout3 = QHBoxLayout()
        self.h_layout3.addWidget(self.length_label)
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
        # KeyEvent
        self.window.keyPressEvent = self.keyPressEvent
    
    def read_json(self):
        return json.load(open(self.file, 'r'))
    
    def write_json(self):
        with open(self.file, 'w') as file:
            file.write(json.dumps(self.data, indent = 4))

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
        self.length = len(df)
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
        self.index = self.combo.currentText()
        self.data['index'] = self.index
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
        self.write_json()   
        # self.combo2.setCurrentIndex(0)
            
    def script_changed(self):
        if self.combo2.currentText():
            self.script = self.combo2.currentText()
            self.data['script'] = self.script
            self.write_json()
            self.chart_load()
    
    def timeframe_changed(self):
        if self.combo3.currentText():
            self.timeFrame = self.combo3.currentText()
            self.data['timeFrame'] = self.timeFrame
            self.write_json()
            self.chart_load()
    
    def speed_changed(self):
        self.timer.stop()
        self.speed = self.input_speed.value() * 1000
        self.data['speed'] = self.speed
        self.write_json()
        # if self.speed <500:
        #     self.speed = 500
        # print(self.speed)
        self.timer.start(self.speed)
        self.label_4.setText(str(int(self.speed)) + ' ms')

    def keyPressEvent(self, event):
            if event.key() == Qt.Key_Q:
                self.data['initial'] = self.initial
                self.write_json()
                QApplication.quit()
            elif event.key() == Qt.Key_Space:  # Check if spacebar is pressed
                self.toggle_pause()  # Toggle pause on spacebar press
            elif event.key() == Qt.Key_Plus:  # '+' key for stepping up
                self.step_up()
            elif event.key() == Qt.Key_Minus:  # '-' key for stepping down
                self.step_down()
            elif event.key() == Qt.Key_R:  # '-' key for stepping down
                self.restart()
            elif event.key() == Qt.Key_T:  # '-' key for stepping down
                if self.combo3.count() > 1:
                    if self.combo3.currentIndex() < self.combo3.count() -1:
                        self.combo3.setCurrentIndex(self.combo3.currentIndex() + 1)
                    else:
                        self.combo3.setCurrentIndex(0)
            elif event.key() == Qt.Key_I:  # '-' key for stepping down
                if self.combo.currentIndex() < self.combo.count() -1:
                    self.combo.setCurrentIndex(self.combo.currentIndex() + 1)
                else:
                    self.combo.setCurrentIndex(0)
            elif event.key() == 16777234:
                self.prev10()
            elif event.key() == 16777236:
                self.next10()
            elif event.key() == 16777237:
                if self.combo2.currentIndex() < self.combo2.count() - 1:
                    self.combo2.setCurrentIndex(self.combo2.currentIndex() + 1)
                else :
                    self.combo2.setCurrentIndex(0)
            elif event.key() == 16777235:
                if self.combo2.currentIndex() > 0:
                    self.combo2.setCurrentIndex(self.combo2.currentIndex() - 1)
                else :
                    self.combo2.setCurrentIndex(self.combo2.count() - 1)
            else:
                print(event.key())
            
    def step_up(self):
        current_value = self.input_speed.value()
        if current_value < 30:
            self.input_speed.setValue(current_value + 0.1)  # Step up by 0.1
    
    def step_down(self):
        current_value = self.input_speed.value()
        if current_value > 0.1:
            self.input_speed.setValue(current_value - 0.1)  # Step up by 0.1
                
if __name__ == '__main__':
    App().run()
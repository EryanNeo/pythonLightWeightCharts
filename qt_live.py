import pandas as pd
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QLabel, QSizePolicy, QDoubleSpinBox, QMessageBox, QSpinBox
from PySide6.QtCore import QTimer, Qt
from lightweight_charts.widgets import QtChart
from pymongo import MongoClient
from datetime import timedelta
from sectors import nifty50, niftyNext50, niftyFno, nifty500
from writer import read_json, write_json, timeframe_convert, NoKeyEventComboBox

class LiveChart(QWidget):
    def __init__(self):
        super().__init__()
        self.mongo = MongoClient('mongodb://localhost:27017')
        self.index = None
        self.script = None
        self.timeFrame = None
        self.speed = None
        self.is_paused = False
        self.last = None
        self.length = 0
        self.config = read_json()
        self.index, self.script, self.timeFrame, self.speed, self.last, self.is_paused = self.config['dynamic'].values()
        # print(self.index, self.script, self.timeFrame, self.speed, self.last, self.is_paused)
        self.initial = self.last
        self.indices = ['Nifty50', 'NiftyNext50', 'NiftyFno', 'Nifty500']
        self.timeframes = ['5M', '15M', 'D']
        self.setup()
        self.add_buttons()
        self.add_combobox()
        self.chart_load_initial()
        self.layout.addWidget(self.chart.get_webview())
        self.set_timer()
    
    def load_data(self):
        self.df = pd.DataFrame(list(self.mongo[self.script][timeframe_convert[self.timeFrame]].find()))
        # self.df = pd.read_csv('data.csv')
        if not self.df.empty:
            self.df['time'] = pd.to_datetime(self.df['time'], unit = 's')
            self.df['time'] = self.df['time'] + timedelta(hours = 5.5)
            self.length = len(self.df)
            self.label_length.setText('Total: ' + str(self.length))
            self.input_last.setRange(0, self.length)
    
    def chart_load_initial(self):            
        self.load_data()
        self.chart.set(self.df.iloc[:self.initial])
        self.label_last.setText('Current: ' + str(self.initial))
        self.last = self.initial
        self.label_last.setText('Current: ' + str(self.last))
    
    def chart_load(self):
        self.chart.set(self.df.iloc[:self.last])
    
    def update_chart(self):
        if not self.is_paused:
            if self.last >= self.length:
                self.toggle_pause()
                self.show_message('Data Loaded')
                return
            self.chart.update(self.df.iloc[self.last])
            self.last += 1
            self.label_last.setText('Current: ' + str(self.last))
               
    def toggle_pause(self):
        if self.is_paused:
            self.is_paused = False
            self.timer.start(self.speed) 
        else:
            self.is_paused = True
            self.timer.stop()
        self.pause_btn.setText('Play' if self.is_paused else 'Pause')
        
    def restart(self):
        if not self.is_paused:
            self.toggle_pause()
        self.chart_load_initial()
        
    def setup(self):
        self.layout = QVBoxLayout()
        self.h_layout_1 = QHBoxLayout()
        self.h_layout_2 = QHBoxLayout()
        self.h_layout_1.setContentsMargins(50, 0, 50, 0)
        self.h_layout_2.setContentsMargins(50, 0, 50, 0)
        self.setLayout(self.layout)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.chart = QtChart(self)
        self.chart.time_scale(right_offset = 10)
    
    def set_timer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_chart)
        self.timer.start(self.speed)
        
    def add_buttons(self):
        self.pause_btn = QPushButton('Play' if self.is_paused else 'Pause')
        self.restart_btn = QPushButton('Restart')
        self.next5_btn = QPushButton('>')
        self.next10_btn = QPushButton('>>')
        self.end_btn = QPushButton('>>>')
        self.prev5_btn = QPushButton('<')
        self.prev10_btn = QPushButton('<<')
        self.speed_increase_btn = QPushButton('+')
        self.speed_decrease_btn = QPushButton('-')        
        self.pause_btn.clicked.connect(self.toggle_pause)
        self.restart_btn.clicked.connect(self.restart)
        self.next5_btn.clicked.connect(self.next5)
        self.next10_btn.clicked.connect(self.next10)
        self.prev5_btn.clicked.connect(self.prev5)
        self.prev10_btn.clicked.connect(self.prev10)
        self.speed_increase_btn.clicked.connect(self.increase)
        self.speed_decrease_btn.clicked.connect(self.decrease)
        self.end_btn.clicked.connect(self.end)
        self.h_layout_1.addWidget(self.prev10_btn)
        self.h_layout_1.addWidget(self.prev5_btn)
        self.h_layout_1.addWidget(self.pause_btn)
        self.h_layout_1.addWidget(self.restart_btn)
        self.h_layout_1.addWidget(self.next5_btn)
        self.h_layout_1.addWidget(self.next10_btn)
        self.h_layout_1.addWidget(self.end_btn)
        self.h_layout_1.addWidget(self.speed_decrease_btn)
        self.h_layout_1.addWidget(self.speed_increase_btn)
        self.layout.addLayout(self.h_layout_1)
        
    def add_combobox(self):
        self.label_index = QLabel('Index')
        self.label_script = QLabel('Script')
        self.label_timeFrame = QLabel('Timeframe')
        self.label_length = QLabel('Total: ' + str(self.length))
        self.label_last = QLabel('Current: ' + str(self.last))
        self.label_speed = QLabel(str(int(self.speed)) + ' ms')
        self.label_index.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.label_script.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.label_timeFrame.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.label_length.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.label_last.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.label_speed.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.combo_index = NoKeyEventComboBox()
        self.combo_script = NoKeyEventComboBox()
        self.combo_timeFrame = NoKeyEventComboBox()
        self.update_last_input_btn = QPushButton('Update')
        self.update_last_input_btn.clicked.connect(self.update_last_input)
        self.input_last = QSpinBox()
        self.input_last.valueChanged.connect(self.last_value_changed)
        self.input_last.setRange(0, self.length)
        self.input_last.setSingleStep(50)
        self.combo_speed = QDoubleSpinBox()
        self.combo_speed.setRange(0.1, 30)
        self.combo_speed.setValue(self.speed/1000)
        self.combo_speed.setSingleStep(0.1)
        self.combo_index.addItems(self.indices)
        self.combo_index.setCurrentIndex(self.indices.index(self.index))
        if self.combo_index.currentIndex() == 0:
            self.combo_script.addItems(nifty50)
            self.combo_timeFrame.addItems(self.timeframes)
            try:
                self.combo_script.setCurrentIndex(nifty50.index(self.script))
                self.combo_timeFrame.setCurrentIndex(self.timeframes.index(self.timeFrame))
            except:
                self.combo_script.setCurrentIndex(0)
                self.combo_timeFrame.setCurrentIndex(0)
        elif self.combo_index.currentIndex() == 1:
            self.combo_script.addItems(niftyNext50)
            self.combo_timeFrame.addItems(self.timeframes)
            try:
                self.combo_script.setCurrentIndex(niftyNext50.index(self.script))
                self.combo_timeFrame.setCurrentIndex(self.timeframes.index(self.timeFrame))
            except:
                self.combo_script.setCurrentIndex(0)
                self.combo_timeFrame.setCurrentIndex(0)
        elif self.combo_index.currentIndex() == 2:
            self.combo_script.addItems(niftyFno)
            self.combo_timeFrame.addItems(self.timeframes)
            try:
                self.combo_script.setCurrentIndex(niftyFno.index(self.script))
                self.combo_timeFrame.setCurrentIndex(self.timeframes.index(self.timeFrame))
            except:
                self.combo_script.setCurrentIndex(0)
                self.combo_timeFrame.setCurrentIndex(0)
        elif self.combo_index.currentIndex() == 3:
            self.combo_script.addItems(nifty500)
            self.combo_timeFrame.addItem(self.timeframes[-1])
            self.combo_timeFrame.setCurrentIndex(0)
            try:
                self.combo_script.setCurrentIndex(nifty500.index(self.script))
            except:
                self.combo_script.setCurrentIndex(0)
        self.combo_index.currentIndexChanged.connect(self.index_changed)
        self.combo_script.currentIndexChanged.connect(self.script_changed)
        self.combo_timeFrame.currentIndexChanged.connect(self.timeFrame_changed)
        self.combo_speed.valueChanged.connect(self.speed_changed)
        self.h_layout_2.addWidget(self.label_index)
        self.h_layout_2.addWidget(self.combo_index)
        self.h_layout_2.addWidget(self.label_script)
        self.h_layout_2.addWidget(self.combo_script)
        self.h_layout_2.addWidget(self.label_timeFrame)
        self.h_layout_2.addWidget(self.combo_timeFrame)
        self.h_layout_2.addWidget(self.label_length)
        self.h_layout_2.addWidget(self.label_last)
        self.h_layout_2.addWidget(self.input_last)
        self.h_layout_2.addWidget(self.update_last_input_btn)
        self.h_layout_2.addWidget(self.label_speed)
        self.h_layout_2.addWidget(self.combo_speed)
        self.layout.addLayout(self.h_layout_2)
        
    def show_message(self, message, information = 'All Data Loaded!'):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)  # Icon type (Information, Warning, Critical, Question)
        msg.setWindowTitle("Info")  # Title of the window
        msg.setText(message)  # Main text
        msg.setInformativeText(information)  # Additional text
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)  # Buttons
        msg.exec()
     
    def update_label_last_data(self):
        self.label_last.setText('Current: ' + str(self.last))
       
    def next5(self):
        self.last += 5
        if self.last >= self.length:
            self.last = self.length
        self.chart_load()
        self.update_label_last_data()
        
    def next10(self):
        self.last += 10
        if self.last >= self.length:
            self.last = self.length
        self.chart_load()
        self.update_label_last_data()
        
    def prev5(self):
        self.last -= 5
        if self.last <= 0:
            self.last = 1
        self.chart_load()
        self.update_label_last_data()
    
    def prev10(self):
        self.last -= 10
        if self.last <= 0:
            self.last = 1
        self.chart_load()
        self.update_label_last_data()
        
    def increase(self):
        self.speed += 500
        if self.speed > 30000:
            self.speed = 30000
        self.combo_speed.setValue(self.speed / 1000)
    
    def decrease(self):
        self.speed -= 500
        if self.speed < 100:
            self.speed = 100
        self.combo_speed.setValue(self.speed / 1000)
    
    def speed_changed(self):
        self.timer.stop()
        self.speed = self.combo_speed.value() * 1000
        self.timer.start(self.speed)
        self.label_speed.setText(str(int(self.speed)) + ' ms')
    
    def index_changed(self):
        self.combo_script.clear()
        self.index = self.combo_index.currentText()
        if self.combo_index.currentIndex() == 0:
            self.combo_script.addItems(nifty50)
        elif self.combo_index.currentIndex() == 1:
            self.combo_script.addItems(niftyNext50)
        elif self.combo_index.currentIndex() == 2:
            self.combo_script.addItems(niftyFno)
        elif self.combo_index.currentIndex() == 3:
            self.combo_script.addItems(nifty500)
            self.combo_timeFrame.clear()
            self.combo_timeFrame.addItem('D')
            self.combo_timeFrame.setCurrentIndex(0)   
    
    def script_changed(self):
        if self.combo_script.currentText():
            self.script = self.combo_script.currentText()
            self.chart_load_initial()
    
    def timeFrame_changed(self):
        if self.combo_timeFrame.currentText():
            self.timeFrame = self.combo_timeFrame.currentText()
            self.chart_load_initial()
    
    def end(self):
        self.last = self.length
        self.chart_load()
        self.update_label_last_data()
    
    def last_value_changed(self):
        self.last = self.input_last.value()
        self.chart_load()
    
    def update_last_input(self):
        self.input_last.setValue(self.last)
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            self.toggle_pause()
        elif event.key() == Qt.Key_Plus:
            self.increase()
        elif event.key() == Qt.Key_Minus: 
            self.decrease()
        elif event.key() == Qt.Key_R:
            self.restart()
        elif event.key() == Qt.Key_T:
            if self.combo_timeFrame.count() > 1:
                if self.combo_timeFrame.currentIndex() < self.combo_timeFrame.count() -1:
                    self.combo_timeFrame.setCurrentIndex(self.combo_timeFrame.currentIndex() + 1)
                else:
                    self.combo_timeFrame.setCurrentIndex(0)
        elif event.key() == Qt.Key_I:
            if self.combo_index.currentIndex() < self.combo_index.count() -1:
                self.combo_index.setCurrentIndex(self.combo_index.currentIndex() + 1)
            else:
                self.combo_index.setCurrentIndex(0)
        elif event.key() == 16777234:
            self.prev10()
        elif event.key() == 16777236:
            self.next10()
        elif event.key() == 16777237:
            if self.combo_script.currentIndex() < self.combo_script.count() - 1:
                self.combo_script.setCurrentIndex(self.combo_script.currentIndex() + 1)
            else :
                self.combo_script.setCurrentIndex(0)
        elif event.key() == 16777235:
            if self.combo_script.currentIndex() > 0:
                self.combo_script.setCurrentIndex(self.combo_script.currentIndex() - 1)
            else :
                self.combo_script.setCurrentIndex(self.combo_script.count() - 1)
        elif event.key() == Qt.Key_S:
            self.config['dynamic']['index'] = self.index
            self.config['dynamic']['script'] = self.script
            self.config['dynamic']['timeFrame'] = self.timeFrame
            self.config['dynamic']['speed'] = self.speed
            self.config['dynamic']['last'] = self.last
            self.config['dynamic']['is_paused'] = self.is_paused
            write_json(self.config)
            self.show_message('Config Saved', 'Current Data is Saved!')
        else:
            print(event.key())
        
        
        
        
        
        
        
        
        
        
        
        
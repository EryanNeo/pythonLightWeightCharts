from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QComboBox, QSizePolicy, QMessageBox
from PySide6.QtCore import Qt
from lightweight_charts.widgets import QtChart
import pandas as pd
from pymongo import MongoClient
from datetime import timedelta
from sectors import nifty50, niftyNext50, niftyFno, nifty500
from writer import read_json, write_json, timeframe_convert, NoKeyEventComboBox

class StaticChart(QWidget):
    def __init__(self):
        super().__init__()
        self.mongo = MongoClient('mongodb://localhost:27017')
        self.index = None
        self.script = None
        self.timeFrame = None
        self.last = None
        self.length = None
        self.config = read_json()
        self.index, self.script, self.timeFrame = self.config['static'].values()
        # print(self.script, self.timeFrame)
        self.indices = ['Nifty50', 'NiftyNext50', 'NiftyFno', 'Nifty500']
        self.timeframes = ['5M', '15M', 'D']
        self.setup()
        
    def setup(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.h_layout_1 = QHBoxLayout()
        self.h_layout_2 = QHBoxLayout()
        self.h_layout_1.setContentsMargins(50, 0, 50, 0)
        self.h_layout_2.setContentsMargins(50, 0, 50, 0)
        # self.h_layout_2.setStretchFactor(stretch = False)
        # self.setLayout(self.layout)
        self.chart = QtChart(self)
        self.chart.time_scale(right_offset = 10)
        self.add_buttons()
        self.add_combobox()
        self.chart_load_initial()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addLayout(self.h_layout_1)
        self.layout.addLayout(self.h_layout_2)
        self.layout.addWidget(self.chart.get_webview())
        
    def add_buttons(self):
        self.next5_btn = QPushButton('>')
        self.next10_btn = QPushButton('>>')
        self.end_btn = QPushButton('>>>')
        self.prev5_btn = QPushButton('<')
        self.prev10_btn = QPushButton('<<')
        self.next_script_btn = QPushButton('Next Script')
        self.prev_script_btn = QPushButton('Prev Script')        
        self.next5_btn.clicked.connect(self.next5)
        self.next10_btn.clicked.connect(self.next10)
        self.prev5_btn.clicked.connect(self.prev5)
        self.prev10_btn.clicked.connect(self.prev10)
        self.next_script_btn.clicked.connect(self.next_script)
        self.prev_script_btn.clicked.connect(self.prev_script)
        self.end_btn.clicked.connect(self.end)
        self.h_layout_1.addWidget(self.prev10_btn)
        self.h_layout_1.addWidget(self.prev5_btn)
        self.h_layout_1.addWidget(self.next5_btn)
        self.h_layout_1.addWidget(self.next10_btn)
        self.h_layout_1.addWidget(self.end_btn)
        self.h_layout_1.addWidget(self.prev_script_btn)
        self.h_layout_1.addWidget(self.next_script_btn)
        
    def add_combobox(self):
        self.label_index = QLabel('Index')
        self.label_script = QLabel('Script')
        self.label_timeFrame = QLabel('Timeframe')
        self.label_length = QLabel('Total: ' + str(self.length))
        self.label_last = QLabel('Current: ' + str(self.last))
        self.label_index.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.label_script.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.label_timeFrame.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.label_length.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.label_last.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.combo_index = NoKeyEventComboBox()
        self.combo_script = NoKeyEventComboBox()
        self.combo_timeFrame = NoKeyEventComboBox()
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
        
        self.reload_btn = QPushButton('Reload')
        self.reload_btn.clicked.connect(self.chart_load_initial)
        self.h_layout_2.addWidget(self.label_index)
        self.h_layout_2.addWidget(self.combo_index)
        self.h_layout_2.addWidget(self.label_script)
        self.h_layout_2.addWidget(self.combo_script)
        self.h_layout_2.addWidget(self.label_timeFrame)
        self.h_layout_2.addWidget(self.combo_timeFrame)
        self.h_layout_2.addWidget(self.reload_btn)
        self.h_layout_2.addWidget(self.label_length)
        self.h_layout_2.addWidget(self.label_last)                  
        
    def load_data(self):
        # print(self.script, self.timeFrame)
        # print(self.mongo[self.script][timeframe_convert[self.timeFrame]])
        self.df = pd.DataFrame(list(self.mongo[self.script][timeframe_convert[self.timeFrame]].find()))
        # self.df = pd.read_csv('data.csv')
        if not self.df.empty:
            self.df['time'] = pd.to_datetime(self.df['time'], unit = 's')
            self.df['time'] = self.df['time'] + timedelta(hours = 5.5)
            self.length = len(self.df)
            self.label_length.setText('Total: ' + str(self.length))
            
    def chart_load_initial(self):            
        self.load_data()
        self.last = self.length
        self.chart.set(self.df)
        self.label_last.setText('Current: ' + str(self.last))
    
    def chart_load(self):
        self.chart.set(self.df.iloc[:self.last])
        self.label_last.setText('Current: ' + str(self.last))
        
    def next5(self):
        self.last += 5
        if self.last >= self.length:
            self.last = self.length
        self.chart_load()
        
    def next10(self):
        self.last += 10
        if self.last >= self.length:
            self.last = self.length
        self.chart_load()
        
    def prev5(self):
        self.last -= 5
        if self.last <= 0:
            self.last = 1
        self.chart_load()
    
    def prev10(self):
        self.last -= 10
        if self.last <= 0:
            self.last = 1
        self.chart_load()
        
    def index_changed(self):
        # print('index changed')
        self.combo_script.clear()
        self.index = self.combo_index.currentText()
        self.config['static']['index'] = self.index
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
    
    def update_config_script(self):
        self.script = self.combo_script.currentText()
        self.config['static']['script'] = self.script
    
    def script_changed(self):
        # print('script changed')
        if self.combo_script.currentText():
            self.update_config_script()
            self.chart_load_initial()
    
    def timeFrame_changed(self):
        # print('timeframe changed')
        if self.combo_timeFrame.currentText():
            self.timeFrame = self.combo_timeFrame.currentText()
            self.config['static']['timeFrame'] = self.timeFrame
            self.chart_load_initial()
    
    def end(self):
        self.last = self.length
        self.chart_load()
    
    def next_script(self):
        if self.combo_script.currentIndex() >= self.combo_script.count() - 1:
            self.combo_script.setCurrentIndex(0)
            self.update_config_script()
        else:
            self.combo_script.setCurrentIndex(self.combo_script.currentIndex() + 1)
            self.update_config_script()
        self.chart_load_initial()
    
    def prev_script(self):
        if self.combo_script.currentIndex() <= 0:
            self.combo_script.setCurrentIndex(self.combo_script.count() - 1)
            self.update_config_script()
        else:
            self.combo_script.setCurrentIndex(self.combo_script.currentIndex() - 1)
            self.update_config_script()
        self.chart_load_initial()
    
    def show_message(self, message, information):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)  # Icon type (Information, Warning, Critical, Question)
        msg.setWindowTitle("Info")  # Title of the window
        msg.setText(message)  # Main text
        msg.setInformativeText(information)  # Additional text
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)  # Buttons
        msg.exec()
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_T:
            if self.combo_timeFrame.count() > 1:
                if self.combo_timeFrame.currentIndex() < self.combo_timeFrame.count() -1:
                    self.combo_timeFrame.setCurrentIndex(self.combo_timeFrame.currentIndex() + 1)
                else:
                    self.combo_timeFrame.setCurrentIndex(0)
        elif event.key() == Qt.Key_S:
            write_json(self.config)
            self.show_message('Config Saved', 'Current Data is Saved!')
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
            self.next_script()
        elif event.key() == 16777235:
            self.prev_script()
        else:
            print(event.key())
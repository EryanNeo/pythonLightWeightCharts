from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QComboBox, QSizePolicy, QMessageBox
from PySide6.QtCore import Qt
from lightweight_charts.widgets import QtChart
import pandas as pd
from pymongo import MongoClient
from datetime import timedelta
from sectors import nifty50, niftyNext50, niftyFno, nifty500
from writer import read_json, write_json, timeframe_convert, NoKeyEventComboBox

class AnalysisChart(QWidget):
    def __init__(self):
        super().__init__()
        self.mongo = MongoClient('mongodb://localhost:27017')
        self.index = None
        self.script = None
        self.config = read_json()
        self.index, self.script = self.config['analysis'].values()
        # print(self.script, self.timeFrame)
        self.indices = ['Nifty50', 'NiftyNext50', 'NiftyFno']
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
        self.chart_5Minute = QtChart(self, inner_height = 0.5)
        self.chart_15Minute = self.chart_5Minute.create_subchart(position = 'left', width = 0.5, height = 0.5)
        self.chart_Daily = self.chart_5Minute.create_subchart(position = 'right', width = 0.5, height = 0.5, sync_crosshairs_only = True)
        self.chart_5Minute.price_scale(auto_scale = True, mode = 'logarithmic', minimum_width = 0)
        self.add_buttons()
        self.add_combobox()
        self.chart_load_initial()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addLayout(self.h_layout_1)
        self.layout.addLayout(self.h_layout_2)
        self.layout.addWidget(self.chart_5Minute.get_webview())
        
    def add_buttons(self):
        self.next_script_btn = QPushButton('Next Script')
        self.prev_script_btn = QPushButton('Prev Script')        
        self.next_script_btn.clicked.connect(self.next_script)
        self.prev_script_btn.clicked.connect(self.prev_script)
        self.h_layout_1.addWidget(self.prev_script_btn)
        self.h_layout_1.addWidget(self.next_script_btn)
        
    def add_combobox(self):
        self.label_index = QLabel('Index')
        self.label_script = QLabel('Script')
        self.label_index.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.label_script.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.combo_index = NoKeyEventComboBox()
        self.combo_script = NoKeyEventComboBox()
        self.combo_index.addItems(self.indices)
        self.combo_index.setCurrentIndex(self.indices.index(self.index))
        if self.combo_index.currentIndex() == 0:
            self.combo_script.addItems(nifty50)
            try:
                self.combo_script.setCurrentIndex(nifty50.index(self.script))
            except:
                self.combo_script.setCurrentIndex(0)
        elif self.combo_index.currentIndex() == 1:
            self.combo_script.addItems(niftyNext50)
            try:
                self.combo_script.setCurrentIndex(niftyNext50.index(self.script))
            except:
                self.combo_script.setCurrentIndex(0)
        elif self.combo_index.currentIndex() == 2:
            self.combo_script.addItems(niftyFno)
            try:
                self.combo_script.setCurrentIndex(niftyFno.index(self.script))
            except:
                self.combo_script.setCurrentIndex(0)
        self.combo_index.currentIndexChanged.connect(self.index_changed)
        self.combo_script.currentIndexChanged.connect(self.script_changed)
        
        self.reload_btn = QPushButton('Reload')
        self.reload_btn.clicked.connect(self.chart_load_initial)
        self.h_layout_2.addWidget(self.label_index)
        self.h_layout_2.addWidget(self.combo_index)
        self.h_layout_2.addWidget(self.label_script)
        self.h_layout_2.addWidget(self.combo_script)
        self.h_layout_2.addWidget(self.reload_btn)               
        
    def load_data(self):
        # print(self.script, self.timeFrame)
        # print(self.mongo[self.script][timeframe_convert[self.timeFrame]])
        self.df_Daily = pd.DataFrame(list(self.mongo[self.script]['Daily'].find()))
        self.df_15Minute = pd.DataFrame(list(self.mongo[self.script]['15Minute'].find()))
        self.df_5Minute = pd.DataFrame(list(self.mongo[self.script]['5Minute'].find()))
        if not self.df_Daily.empty:
            self.df_Daily['time'] = pd.to_datetime(self.df_Daily['time'], unit = 's')
            self.df_Daily['time'] = self.df_Daily['time'] + timedelta(hours = 5.5)
        if not self.df_15Minute.empty:
            self.df_15Minute['time'] = pd.to_datetime(self.df_15Minute['time'], unit = 's')
            self.df_15Minute['time'] = self.df_15Minute['time'] + timedelta(hours = 5.5)
        if not self.df_5Minute.empty:
            self.df_5Minute['time'] = pd.to_datetime(self.df_5Minute['time'], unit = 's')
            self.df_5Minute['time'] = self.df_5Minute['time'] + timedelta(hours = 5.5)
                     
    def chart_load_initial(self):            
        self.load_data()
        self.chart_5Minute.set(self.df_5Minute)
        self.chart_15Minute.set(self.df_15Minute)
        self.chart_Daily.set(self.df_Daily)
        self.chart_15Minute.run_script(f'''
            let vr_15Minute = {self.chart_15Minute.id}.chart.timeScale().getVisibleLogicalRange();
            // {self.chart_15Minute.id}.chart.timeScale().setVisibleLogicalRange({{ from: vr_15Minute.to - 1500, to: vr_15Minute.to + 10 }});
            {self.chart_15Minute.id}.chart.timeScale().setVisibleLogicalRange({{ from: vr_15Minute.from * 0.8, to: vr_15Minute.to + 50 }});  
            ''')
        self.chart_5Minute.run_script(f'''
            let vr_5Minute = {self.chart_5Minute.id}.chart.timeScale().getVisibleLogicalRange();
            // {self.chart_5Minute.id}.chart.timeScale().setVisibleLogicalRange({{ from: vr_5Minute.to - 1500, to: vr_5Minute.to + 10 }});
            {self.chart_5Minute.id}.chart.timeScale().setVisibleLogicalRange({{ from: vr_5Minute.from * 0.995, to: vr_5Minute.to + 10 }});  
            ''')
        self.chart_Daily.run_script(f'''
            let vr_Daily = {self.chart_Daily.id}.chart.timeScale().getVisibleLogicalRange();
            // {self.chart_Daily.id}.chart.timeScale().setVisibleLogicalRange({{ from: vr_Daily.to - 1500, to: vr_Daily.to + 10 }});
            {self.chart_Daily.id}.chart.timeScale().setVisibleLogicalRange({{ from: vr_Daily.from * 0.6, to: vr_Daily.to + 50 }});  
            ''')
        
    def index_changed(self):
        # print('index changed')
        self.combo_script.clear()
        self.index = self.combo_index.currentText()
        self.config['analysis']['index'] = self.index
        if self.combo_index.currentIndex() == 0:
            self.combo_script.addItems(nifty50)
        elif self.combo_index.currentIndex() == 1:
            self.combo_script.addItems(niftyNext50)
        elif self.combo_index.currentIndex() == 2:
            self.combo_script.addItems(niftyFno)  
    
    def update_config_script(self):
        self.script = self.combo_script.currentText()
        self.config['analysis']['script'] = self.script
    
    def script_changed(self):
        # print('script changed')
        if self.combo_script.currentText():
            self.update_config_script()
            self.chart_load_initial()
    
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
            # print('No Timeframes')
            pass
        elif event.key() == Qt.Key_S:
            write_json(self.config)
            self.show_message('Config Saved', 'Current Data is Saved!')
        elif event.key() == Qt.Key_I:
            if self.combo_index.currentIndex() < self.combo_index.count() -1:
                self.combo_index.setCurrentIndex(self.combo_index.currentIndex() + 1)
            else:
                self.combo_index.setCurrentIndex(0)
        elif event.key() == 16777237:
            self.next_script()
        elif event.key() == 16777235:
            self.prev_script()
        else:
            print(event.key())
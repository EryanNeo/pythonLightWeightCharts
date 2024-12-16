from PySide6.QtWidgets import QMainWindow, QApplication, QTabWidget, QMessageBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from qt_static import StaticChart
from qt_live import LiveChart
from writer import read_json, write_json


class App:
    def __init__(self):
        self.app = QApplication([])
        self.app.setApplicationName('Neo Charting App')
        self.window = QMainWindow()
        self.menubar = self.window.menuBar()
        menu = self.menubar.addMenu('Menu')
        quit_action = QAction("Quit", self.window)
        save_action = QAction("Save", self.window)
        menu.addAction(save_action)
        menu.addAction(quit_action)
        save_action.triggered.connect(self.save)
        quit_action.triggered.connect(QApplication.quit)
        self.window.resize(1920, 1080)
        self.config = read_json()
        self.tab_widget = QTabWidget()
        self.static_chart_tab = StaticChart()
        self.live_chart_tab = LiveChart()
        self.tab_widget.addTab(self.static_chart_tab, 'Static Chart')
        self.tab_widget.addTab(self.live_chart_tab, 'Live Chart')
        if self.config['live']:
            self.tab_widget.setCurrentWidget(self.live_chart_tab)
        self.tab_widget.currentChanged.connect(self.tab_changed)
        self.window.setCentralWidget(self.tab_widget)
        self.window.keyPressEvent = self.keyPressEvent        

    def tab_changed(self):
        if self.tab_widget.currentIndex() == 0:
            self.config['live'] = False
        else:
            self.config['live'] = True
        if not self.live_chart_tab.is_paused:
            self.live_chart_tab.toggle_pause()
    
    def show_message(self, message, information = 'All Data Loaded!'):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)  # Icon type (Information, Warning, Critical, Question)
        msg.setWindowTitle("Info")  # Title of the window
        msg.setText(message)  # Main text
        msg.setInformativeText(information)  # Additional text
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)  # Buttons
        msg.exec()
    
    def save(self):
        write_json(self.config)
        self.show_message('Saved')
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Q:
            write_json(self.config)
            QApplication.quit()
        elif self.tab_widget.currentIndex() == 0:
            self.static_chart_tab.keyPressEvent(event)
        elif self.tab_widget.currentIndex() == 1:
            self.live_chart_tab.keyPressEvent(event)
        else:
            print('Some Wrong Key Pressed')
    
    def run(self):
        self.window.show()
        self.app.exec()
    
if __name__ == '__main__':
    App().run()

     




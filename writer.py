import json
from PySide6.QtWidgets import QComboBox

class NoKeyEventComboBox(QComboBox):
    def keyPressEvent(self, event):
        event.ignore()
        
file = 'config.json'
timeframe_convert = {
    '5M': '5Minute',
    '15M': '15Minute',
    'D': 'Daily'
}

def read_json():
    return json.load(open(file, 'r'))

def write_json(data):
    with open(file, 'w') as f:
        f.write(json.dumps(data, indent = 4))
        
if __name__ == '__main__':
    live, dynamic, static = read_json().values()
    print(live)
    print(dynamic)
    print(static)
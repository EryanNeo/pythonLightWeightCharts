import json

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
    print(read_json()['dynamic'])
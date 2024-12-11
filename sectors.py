import json

def read_json(file):
    return json.load(open(file, 'r'))['name']

nifty50 = read_json('sectors/nifty50.json')
niftyNext50 = read_json('sectors/niftyNext50.json')
niftyFno = read_json('sectors/niftyFno.json')
nifty500 = read_json('sectors/nifty500.json')

if __name__ == '__main__':
    print(nifty50)
    print(niftyNext50)
    print(niftyFno)
    print(nifty500)
    
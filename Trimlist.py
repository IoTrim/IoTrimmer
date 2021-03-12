from collections import defaultdict

class Trimlist(object):

    def __init__(self):
        self.defaultTrimlist = "/opt/iotrimlist/trimlist"
        self.trimlist = defaultdict(list)

    def loadList(self):
        with open(self.defaultTrimlist) as f:
            for line in f.readlines():
                parts = line.split(',')
                self.trimlist[parts[0]].append(parts[1].strip())

    def __getitem__(self, deviceId):
        try:
            return self.trimlist[deviceId]
        except:
            return []

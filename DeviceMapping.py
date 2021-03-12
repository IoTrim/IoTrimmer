
class DeviceMapping(object):

    def __init__(self):
        self.mappingFile = '/opt/moniotr/etc/devices.txt'
        self.loadMapping()
        self.mapping = {}

    def loadMapping(self):
        self.mapping = {}
        with open(self.mappingFile) as f:
            for line in f.readlines():
                parts = line.split()
                #print(parts)
                self.mapping[parts[0]] = parts[1].strip()

    def __getitem__(self, mac):
        try:
            return self.mapping[mac]
        except:
            return ""

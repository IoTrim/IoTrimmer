import os, pathlib
from ProcessList import ProcessList
from mac_vendor_lookup import MacLookup
from DeviceInfo import DeviceInfo
from DeviceMapping import DeviceMapping
from Trimlist import Trimlist

class Devices(object):

    def __init__(self, baseDir = "/opt/moniotr/traffic/by-mac"):
        self.baseDir = baseDir
        self.infoBaseDir = os.path.join(pathlib.Path(__file__).parent.absolute(), "deviceInfo")
        self.devices = {}

        self.processList = ProcessList()
        self.processList.processesRunning()
        
        self.deviceMapping = DeviceMapping()
        self.deviceMapping.loadMapping()

    def loadDevices(self):
        try:
            for mac in os.listdir(self.baseDir):
                name = open(self.baseDir + '/' + mac + "/name.txt").read().strip()
                self.devices[mac] = Device(self.infoBaseDir, name, mac, self.processList.isMacMonitored(mac), 
                        self.deviceMapping)

        except FileNotFoundError as e:
            print(e)


    def getDict(self):
        data = {}
        for mac, dev in self.devices.items():
            data[dev.mac] = dev.getDict()

        return data

    def __repr__(self):
        info = ""
        for dev in self.devices.iter():
            info+= f"{dev}"

        return info
            

class Device(object):

    def __init__(self, baseDir, name, mac, monitored, mapping):
        self.baseDir = baseDir
        self.mac = mac
        self.name = name
        self.normalisedMac = self._normaliseMac(self.mac)
        self.modelFile = "modelFile.txt"
        self.publicInfoFile = "publicInfo.txt"
        self.privateInfoFile = "privateInfo.txt"
        self.monitored = monitored
        self.vendor = ''

        self.macLookup = MacLookup()

        self._checkDir(os.path.join(self.baseDir, self.mac))

        self.loadInfo()
        
        self.deviceInfo = DeviceInfo()
        self.deviceInfo.loadInfo()

        self.deviceId = mapping[self.mac]

        self.tl = Trimlist()
        self.tl.loadList()
        self.trimlist = self.tl[self.deviceId]

    def getDict(self):
        return {'mac': self.mac, 
                'class': 'green' if self.monitored else 'red',
                'name': self.name,
                'vendor': self.vendor,
                'model': self.model,
                'publicInfo': self.publicInfo,
                'privateInfo': self.privateInfo,
                'deviceInfo': self.deviceInfo.toHTML(self.name),
                'trimlist': self.trimlist
               }

    def _checkDir(self, dirName):
        if not os.path.exists(dirName):
            os.makedirs(dirName)

    def loadInfo(self):
        self.model = self._loadInfoFromFile(self.modelFile)
        self.publicInfo = self._loadInfoFromFile(self.publicInfoFile)
        self.privateInfo = self._loadInfoFromFile(self.privateInfoFile)

        self._loadVendor()

    def _loadInfoFromFile(self, fileName):
        path = os.path.join(self.baseDir, self.mac, fileName)
        
        if os.path.exists(path):
            with open(path) as f:
                info = f.read()
        else:
            info = ""

        return info

    def _loadVendor(self):
        try:
            self.vendor = self.macLookup.lookup(self.normalisedMac)
        except KeyError:
            self.vendor = 'Unknown'
  
    def _normaliseMac(self, mac):
        return ":".join([n.zfill(2) for n in mac.split(":")])

    def updateInfo(self, data):
        if data['what'] == 'model':
            self._saveInfoToFile(self.modelFile, data['text'])
        if data['what'] == 'publicInfo':
            self._saveInfoToFile(self.publicInfoFile, data['text'])

    def _saveInfoToFile(self, fileName, info):
        path = os.path.join(self.baseDir, self.mac, fileName)

        with open(path, 'w') as f:
            f.write(info)

    def __repr__(self):
        return f"{self.mac}: {self.publicInfo} {self.privateInfo} {self.monitored}"


if __name__ == "__main__":
    devices = Devices()
    devices.loadDevices()

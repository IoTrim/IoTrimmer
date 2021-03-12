import os, pathlib

class GeneralInfo(object):

    def __init__(self, infoDir = "deviceInfo", fileName = "generalInfo.txt"):
        self.infoDir = infoDir
        self.infoBaseDir = os.path.join(pathlib.Path(__file__).parent.absolute(), self.infoDir)
        self.infoPath = os.path.join(self.infoBaseDir, fileName)
        self.generalInfo = ""

    def loadInfo(self):
        if os.path.exists(self.infoPath):
            with open(self.infoPath) as f:
                self.generalInfo = f.read()
        else:
            self.generalInfo = ""

    def saveInfo(self, info):
        with open(self.infoPath, 'w') as f:
            f.write(info)

 
    

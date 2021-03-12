import psutil, os
from pathlib import Path

class ProcessList(object):

    def __init__(self):
        self.tcpdumps = []

    def processesRunning(self):

        listOfProcessNames = []
        for proc in psutil.process_iter():
            # Get process detail as dictionary
            pInfoDict = proc.as_dict(attrs=['pid', 'name', 'cpu_percent', 'cmdline'])
            # Append dict of process detail in list
            
            if "tcpdump" in pInfoDict['name']:
                #pInfoDict['fList'] = proc.open_files()
                self.tcpdumps.append(TCPDumpProc(pInfoDict))

        #print(self.tcpdumps)

    def isFileUsed(self, fileName):
        return any([proc.isFileUsed(fileName) for proc in self.tcpdumps])

    def isMacMonitored(self, mac):
        return any([proc.mac == mac for proc in self.tcpdumps])

class TCPDumpProc(object):

    def __init__(self, _dict):
        #self.openFiles = [fl[0] for fl in _dict['fList']]
        self.tcpdumpPath = _dict['cmdline'][-4]
        self.tcpdumpDir = os.path.dirname(self.tcpdumpPath)
        self.mac = _dict['cmdline'][-1]
        self.pid = _dict['pid']

        self.loadFiles()

    def loadFiles(self):
        self.tcpdumpFiles = sorted(Path(self.tcpdumpDir).iterdir(), key=os.path.getmtime)
        #print(self.tcpdumpFiles)

    def isFileUsed(self, fileName):
        #return fileName in self.openFiles
        return Path(fileName) == self.tcpdumpFiles[-1] # the last file is still being used for writing current tcpdump

    def __repr__(self):
        return f"{self.mac} {self.pid} {self.tcpdumpPath} {self.tcpdumpDir} {self.tcpdumpFiles}"

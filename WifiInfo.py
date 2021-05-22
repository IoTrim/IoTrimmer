
class WifiInfo(object):

    def __init__(self):
        self.defaultConfigFile = "/etc/hostapd/hostapd.conf"
        self.config = {}

    def loadConfig(self, configFile = None):
        if configFile is None:
            configFile = self.defaultConfigFile

        with open(configFile) as f:
            lines = f.readlines()

        for line in lines:
            parts = line.split('=')
            self.config[parts[0]] = parts[1].strip()

    def saveConfig(self, configFile = None):
        if configFile is None:
            configFile = self.defaultConfigFile
        
        if not self.config:
            return

        with open(configFile, 'w') as f:
            for k, v in self.config.items():
                f.write(f"{k}={v}\n")

    def getSSID(self):
        return self.config['ssid']

    def setSSID(self, ssid):
        self.config['ssid'] = ssid

    def getPassword(self):
        return self.config['wpa_passphrase']

    def setPassword(self, password):
        self.config['wpa_passphrase'] = password

if __name__ == "__main__":
    wi = WifiInfo()
    wi.loadConfig('/tmp/hostapd.conf')
    wi.setPassword('new_passworda')
    wi.saveConfig("/tmp/hostapd.conf")
            


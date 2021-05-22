
class DeviceInfo(object):

    def __init__(self):
        self.defaultModelFile = "/opt/iotrimlist/devices.csv"
        self.devices = {}

    def loadInfo(self):
        with open(self.defaultModelFile) as f:
            for line in f.readlines():
                parts = line.split(';')
                if parts[0] != "device":
                    self.devices[parts[0]] = parts[0].strip()
            self.devices["unknown"] = "unknown"

    def toHTML(self, name):
        html = f"<select>"

        for device, deviceName in self.devices.items():
            sel = ' selected' if device == name else ''
            html+= f"<option value='{device}'{sel}>{deviceName}</option>"
               
        html+= f"</select>"

        return html

if __name__ == "__main__":
    di = DeviceInfo()
    di.loadInfo()
    html = di.toHTML('firetv')
    print(html)

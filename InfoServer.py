#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, HTTPServer

from multiprocessing import  Process
from multiprocessing.connection import Client
#from logzero import logger
import sys, json, cgi, os, pathlib, time
import subprocess

from ProcessList import ProcessList
from Devices import Devices
from WifiInfo import WifiInfo
from DeviceInfo import DeviceInfo

from mako.template import Template

class DadaServer(object):

    def __init__(self, baseDir=None, configFile=None):
        if baseDir is None:
            baseDir = pathlib.Path(__file__).parent.absolute()

        self.baseDir = baseDir

        if configFile is None:
            configFile = os.path.join(self.baseDir, "dada_server.config")
        
        with open(configFile) as f:
            self.config = json.load(f)

    def runServer(self):
        serverAddress = (self.config['serverAddr'], self.config['serverPort'])

        self.httpd = HTTPServer(serverAddress, DadaHandler)
        
        try:
            print("starting server")
            self.httpd.serve_forever()
        except KeyboardInterrupt:
            pass

        self.httpd.server_close()

    def run(self):
        self.p = Process(target=self.runServer)
        self.p.start()

    def stop(self):
        self.p.terminate()



class DadaHandler(BaseHTTPRequestHandler):
    
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def _formToDict(self, form):
        _dict = {}
        for field in form.keys():
            _dict[field] = form[field].value
        return _dict

    def getWifiInfo(self):
        self.wifi = WifiInfo()
        self.wifi.loadConfig()


    def do_GET(self):
        self._set_response()

        data = {}

        self.getWifiInfo()
        data['wifiPassword'] = self.wifi.getPassword()
        data['ssid'] = self.wifi.getSSID()

        pl = ProcessList()
        pl.processesRunning()
        
        devs = Devices()
        devs.loadDevices()

        data['devices'] = devs.getDict()
        #print(data)
        templ = Template(filename=os.path.join(pathlib.Path(__file__).parent.absolute(), 'templates/index.html'))
        #self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))
        renderStr = templ.render(**data)
        self.wfile.write("{}".format(renderStr).encode('utf-8'))

    def do_POST(self):
        self._set_response()

        form = cgi.FieldStorage(
        fp = self.rfile,
        headers = self.headers,
        environ = {'REQUEST_METHOD': 'POST',
                   'CONTENT_TYPE': self.headers['Content-Type'],
                  })
        data = self._formToDict(form)
        #print(data)

        if self.path == "/reboot":
            self._rebootDadaBox(data)
        elif self.path == "/restart":
            self._restartDadaServer(data)
        elif self.path == "/updateGeneralInfo":
            self._updateGeneralInfo(data)
        elif self.path == "/updateDeviceInfo":
            self._updateDeviceInfo(data)
        elif self.path == "/updateWifiPassword":
            self._updateWifiPassword(data)
        elif self.path == "/updateSSID":
            self._updateWifiSSID(data)
        elif self.path == "/stop":
            self._stopMoniotr()
        elif self.path == "/start":
            self._startMoniotr()
        elif self.path == "/renameDevice":
            self._renameDevice(data)

    def _updateDeviceInfo(self, data):
        data['mac'], data['what'] = data['id'].split('_')
        
        devs = Devices()
        devs.loadDevices()
        
        dev = devs.devices[data['mac']]
        dev.updateInfo(data)

        #for field in form.keys():
        #    print(field, form[field].value)

        #contentLength = int(self.headers['Content-Length']) # <--- Gets the size of data
        #postData = self.rfile.read(contentLength) # <--- Gets the data itself
        #logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
        #        str(self.path), str(self.headers), post_data.decode('utf-8'))

        
        #self.conn.send(postData.decode('utf-8'))


    def _rebootDadaBox(self, data):
        subprocess.run("reboot")

    def _restartDadaServer(self, data):
        subprocess.run(["/opt/moniotr/bin/moniotr-ctrl", "restart"])
        #time.sleep(15)
        subprocess.run(["systemctl", "restart", "info-server.service"])

    def _stopMoniotr(self):
        subprocess.run(["/opt/moniotr/bin/moniotr-ctrl", "stop"])

    def _startMoniotr(self):
        subprocess.run(["/opt/moniotr/bin/moniotr-ctrl", "start"])

    def _renameDevice(self, data):
        subprocess.run(["/opt/moniotr/bin/identify-device", f"{data['mac']}", f"{data['name']}"])

    def _getGeneralInfo(self):
        gi = GeneralInfo()
        gi.loadInfo()
        return gi.generalInfo

    def _updateGeneralInfo(self, data):
        gi = GeneralInfo()
        gi.saveInfo(data['text'])
        

    def _updateWifiPassword(self, data):
        self.getWifiInfo()
        if len(data['text']) < 8:
            return
        self.wifi.setPassword(data['text'])
        self.wifi.saveConfig()
        subprocess.run(["service", "hostapd", "restart"])

    def _updateWifiSSID(self, data):
        self.getWifiInfo()
        self.wifi.setSSID(data['text'])
        self.wifi.saveConfig()
        subprocess.run(["service", "hostapd", "restart"])


#def run(server_class=HTTPServer, handler_class=S, port=80):
#    logging.basicConfig(level=logging.INFO)
#    server_address = ('', port)
#    httpd = server_class(server_address, handler_class)
#    logging.info('Starting httpd...\n')
#    try:
#        httpd.serve_forever()
#    except KeyboardInterrupt:
#        pass
#    httpd.server_close()
#    logging.info('Stopping httpd...\n')
#
if __name__ == '__main__':
    try:
        configFile = sys.argv[1]
    except IndexError:
        configFile = None

    ds = DadaServer(configFile=configFile)
    ds.runServer()
#    from sys import argv
#
#    if len(argv) == 2:
#        run(port=int(argv[1]))
#    else:
#        run()
#

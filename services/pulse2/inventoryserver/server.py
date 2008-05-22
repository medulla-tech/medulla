import BaseHTTPServer
from zlib import *
from mmc.support.mmctools import Singleton
from time import strftime
import logging
import time
import re

from mmc.plugins.inventory.database import Inventory
from pulse2.inventoryserver.mapping import OcsMapping

class InventoryServer(BaseHTTPServer.BaseHTTPRequestHandler):
    def __init__(self, *args):
        self.logger = logging.getLogger()
        BaseHTTPServer.BaseHTTPRequestHandler.__init__(self, *args)
        
    def log_message(self, format, *args):
        self.logger.info(format % args)

    def do_POST(self):
        try:
            deviceid = ''
            query = ''
            
            self.logger.debug("%s start" % (time.time()))
            content = self.rfile.read(int(self.headers['Content-Length']))
            if self.headers['Content-Type'] == 'application/x-compress':
                content = decompress(content)
    
            self.logger.debug("%s decompressed" % (time.time()))
            try:
                query = re.search(r'<QUERY>([\w-]+)</QUERY>', content).group(1)
            except AttributeError, e:
                query = 'FAILS'
            try:
                deviceid = re.search(r'<DEVICEID>([\w-]+)</DEVICEID>', content).group(1)
            except AttributeError, e:
                pass
            self.logger.debug("%s regex" % (time.time()))
    
            if query == 'PROLOG':
                resp = '<?xml version="1.0" encoding="utf-8" ?><REPLY><RESPONSE>SEND</RESPONSE></REPLY>'
            elif query == 'UPDATE':
                resp = '<?xml version="1.0" encoding="utf-8" ?><REPLY><RESPONSE>no_update</RESPONSE></REPLY>'
            elif query == 'INVENTORY':
                inv_data, encoding, date = '', '', strftime("%Y-%m-%d %H:%M:%S")
                self.logger.debug("%s inventory" % (time.time()))
                try:
                    inv_data = re.compile(r'<CONTENT>(.+)</CONTENT>', re.DOTALL).search(content).group(1)
                except AttributeError, e:
                    pass
    
                try:
                    encoding = re.search(r' encoding="([^"]+)"', content).group(1)
                except AttributeError, e:
                    pass
    
                try:
                    date = re.compile(r'<LOGDATE>(.+)</LOGDATE>', re.DOTALL).search(inv_data).group(1)
                except AttributeError, e:
                    pass
    
                self.logger.debug("%s regex" % (time.time()))
                inventory = '<?xml version="1.0" encoding="%s" ?><Inventory>%s</Inventory>' % (encoding, inv_data)
                inventory = re.sub(r'</?HISTORY>', '', inventory)
                inventory = re.sub(r'</?DOWNLOAD>', '', inventory)
    
                resp = '<?xml version="1.0" encoding="utf-8" ?><REPLY><RESPONSE>no_account_update</RESPONSE></REPLY>'
    
                # Store data on the server
                inventory = OcsMapping().parse(inventory)
                self.logger.debug("%s parsed" % (time.time()))
                hostname = '-'.join(deviceid.split('-')[0:-6])
                try:
                    hostname = inventory['HARDWARE'][1]['NAME']
                except:
                    pass
                try:
                    date = inventory['ACCESSLOG'][1]['LOGDATE']
                except:
                    pass
                    
                ret = Inventory().createNewInventory(hostname, inventory, date)
                # TODO if ret == False : reply something else
                if not ret:
                    self.logger.error("no inventory created!")
                    self.send_response(500)
                    self.end_headers()
                    return
    
            self.logger.debug("%s send" % (time.time()))
            self.send_response(200)
            self.end_headers()
            self.wfile.write(compress(resp))
        except Exception, e:
            self.send_response(500)
            self.end_headers()

class InventoryGetService(Singleton):
    def initialise(self, config):
        Inventory().activate()
        self.config = config
        self.bind = config.bind
        self.port = int(config.port)
        self.xmlmapping = config.ocsmapping
        OcsMapping().initialize(self.xmlmapping)

    def run(self, server_class=BaseHTTPServer.HTTPServer, handler_class=InventoryServer):
        server_address = (self.bind, int(self.port))
        httpd = server_class(server_address, handler_class)
        httpd.serve_forever()
        

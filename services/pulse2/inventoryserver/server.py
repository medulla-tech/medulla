import BaseHTTPServer
from zlib import *
from mmc.support.mmctools import Singleton
from time import strftime
import logging
import time
import re

from pulse2.inventoryserver.mapping import OcsMapping
from pulse2.inventoryserver.database import InventoryWrapper
from pulse2.inventoryserver.config import Pulse2OcsserverConfigParser

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
                content = decompressobj().decompress(content)
    
            self.logger.debug("%s decompressed" % (time.time()))
            try:
                query = re.search(r'<QUERY>([\w-]+)</QUERY>', content).group(1)
            except AttributeError, e:
                query = 'FAILS'
            try:
                deviceid = re.search(r'<DEVICEID>([\w-]+)</DEVICEID>', content).group(1)
            except AttributeError, e:
                pass
            self.logger.debug("%s regex %s" % (time.time(), query))
    
            a = 0
            if query == 'PROLOG':
                config = InventoryGetService().config
                if len(config.options.keys()) == 0:
                    resp = '<?xml version="1.0" encoding="utf-8" ?><REPLY><RESPONSE>SEND</RESPONSE></REPLY>'
                else:
                    resp = '<?xml version="1.0" encoding="utf-8" ?><REPLY>'
                    for section in config.options:
                        try:
                            params = config.options[section]
                            resp += '<OPTION><NAME>%s</NAME>' % (params['name'])
                            resp_param = ""
                            for p in params['param']:
                                resp_param += '<PARAM '
                                for attr in p['param']:
                                    resp_param += '%s="%s" ' % (attr[0], attr[1])
                                resp_param += '>%s</PARAM>' % (p['value'])
                            resp += resp_param + '</OPTION>'
                        except:
                            self.logger.error('please check your %s config parameter' % (section))
                    resp = resp + '<RESPONSE>SEND</RESPONSE></REPLY>'
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
                    path = Pulse2OcsserverConfigParser().hostname
                    # WARNING : no fallback if the tag does not exists....
                    if len(path) == 4:
                        for tag in inventory[path[0]]:
                            if tag[path[2]] == path[3]:
                                hostname = tag[path[1]]
                    else:
                        hostname = inventory[path[0]][1][path[1]]
                except:
                    pass
                try:
                    date = inventory['ACCESSLOG'][1]['LOGDATE']
                except:
                    pass
                    
                ret = InventoryWrapper().createNewInventory(hostname, inventory, date)
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
        except IOError, e:
            self.logger.error(e)
            self.logger.error(e.orig)
            self.send_response(500)
            self.end_headers()
        except Exception, e:
            self.logger.error(e)
            self.send_response(500)
            self.end_headers()

class InventoryGetService(Singleton):
    def initialise(self, config):
        InventoryWrapper().activate()
        self.config = config
        self.bind = config.bind
        self.port = int(config.port)
        self.xmlmapping = config.ocsmapping
        OcsMapping().initialize(self.xmlmapping)

    def run(self, server_class=BaseHTTPServer.HTTPServer, handler_class=InventoryServer):
        server_address = (self.bind, int(self.port))
        httpd = server_class(server_address, handler_class)
        httpd.serve_forever()
        

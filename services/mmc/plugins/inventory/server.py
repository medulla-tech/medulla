import BaseHTTPServer
from zlib import *
import re
from mmc.support.mmctools import Singleton
from mmc.plugins.inventory.database import Inventory
from xml.dom.minidom import parse, parseString
from time import strftime
import time

class InventoryServer(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        pass

    def do_POST(self):
        deviceid = ''
        query = ''
        #print "%s start" % (time.time())
        content = self.rfile.read(int(self.headers['Content-Length']))
        if self.headers['Content-Type'] == 'application/x-compress':
            content = decompress(content)

        #print "%s decompressed" % (time.time())
        try:
            query = re.search(r'<QUERY>([\w-]+)</QUERY>', content).group(1)
        except AttributeError, e:
            query = 'FAILS'
        try:
            deviceid = re.search(r'<DEVICEID>([\w-]+)</DEVICEID>', content).group(1)
        except AttributeError, e:
            pass
        #print "%s regex" % (time.time())

        if query == 'PROLOG':
            resp = '<?xml version="1.0" encoding="utf-8" ?><REPLY><RESPONSE>SEND</RESPONSE></REPLY>'
        elif query == 'UPDATE':
            resp = '<?xml version="1.0" encoding="utf-8" ?><REPLY><RESPONSE>no_update</RESPONSE></REPLY>'
        elif query == 'INVENTORY':
            inv_data, encoding, date = '', '', strftime("%Y-%m-%d %H:%M:%S")
            #print "%s inventory" % (time.time())
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

            #print "%s regex" % (time.time())
            inventory = '<?xml version="1.0" encoding="%s" ?><Inventory>%s</Inventory>' % (encoding, inv_data)
            inventory = re.sub(r'</?HISTORY>', '', inventory)
            inventory = re.sub(r'</?DOWNLOAD>', '', inventory)

            resp = '<?xml version="1.0" encoding="utf-8" ?><REPLY><RESPONSE>no_account_update</RESPONSE></REPLY>'

            # Store data on the server
            inventory = OcsMapping().parse(inventory)
            #print "%s parsed" % (time.time())
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
                
                print ".createNewInventory fails"

        #print "%s send" % (time.time())
        self.send_response(200)
        self.end_headers()
        self.wfile.write(compress(resp))
        exit 

class InventoryGetService(Singleton):
#    isactive = False
    
    def initialise(self):
#        if self.isactive:
#            return False
        #self.config = ...
#        self.isactive = True
        self.bind = ''
        self.port = 8000
        self.xmlmapping = '/usr/lib/python2.3/site-packages/mmc/plugins/inventory/OcsNGMap.xml' # TODO : put in conf
        OcsMapping().initialize(self.xmlmapping)
        return True

    def run(self, server_class=BaseHTTPServer.HTTPServer, handler_class=InventoryServer):
#        import logging
#        import os
#
#        pid = 0
#        try:
#            pid = os.fork()
#            logging.getLogger().error("pid = %s" % (str(pid)))
#            if pid > 0:
#                # parent stays alive
#                return pid
#        except OSError, error:
#            logging.getLogger().error('launching ocs input method fail (%s)' % (str(error)))
#            return 0
#    
        # child
        server_address = (self.bind, self.port)
        httpd = server_class(server_address, handler_class)
        httpd.serve_forever()
        
class OcsMapping(Singleton):
    def initialize(self, xmlmapping):
        self.doc = parse(xmlmapping)
        self.tables = {}

        for table in self.doc.documentElement.getElementsByTagName("MappedObject"):
            xmlname = table.getAttribute('name')
            xmlclass = table.getAttribute('class')
            self.tables[xmlname] = [xmlclass, {}]
            for field in table.getElementsByTagName('MappedField'):
                xmlfrom = field.getAttribute('from')
                xmlto = field.getAttribute('to')
                self.tables[xmlname][1][xmlfrom] = xmlto

    def parse(self, xmltext):
        inventory = {}
        xml = parseString(xmltext)
        for tablename in self.tables:
            try:
                dbtablename = self.tables[tablename][0]
                inventory[dbtablename] = []
                for tag in xml.getElementsByTagName(tablename):
                    entry = {}
                    for fieldname in self.tables[tablename][1]:
                        try:
                            field = tag.getElementsByTagName(fieldname)[0]
                            dbfieldname = self.tables[tablename][1][fieldname]
                            entry[dbfieldname] = field.childNodes[0].nodeValue
                        except IndexError:
                            pass
                    inventory[dbtablename].append(entry)
                    
#                tag = xml.getElementsByTagName(tablename)[0]
#                dbtablename = self.tables[tablename][0]
#                inventory[dbtablename] = {}
#                # TODO : forgot a level.... (can have more than one of each table...)
#                for fieldname in self.tables[tablename][1]:
#                    try:
#                        field = tag.getElementsByTagName(fieldname)[0]
#                        dbfieldname = self.tables[tablename][1][fieldname]
#                        inventory[dbtablename][dbfieldname] = field.childNodes[0].nodeValue
#                    except IndexError:
#                        pass
            except IndexError:
                pass

        return inventory

#Inventory().activate()
#a = InventoryGetService()
#ret = a.run()
#if ret:
#    print "reussi"
#else:
#    print "fails"


#!/usr/bin/python
# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2009 Mandriva, http://www.mandriva.com
#
# $Id$
#
# This file is part of Mandriva Management Console (MMC).
#
# MMC is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# MMC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MMC.  If not, see <http://www.gnu.org/licenses/>.

"""
Little common utility functions used by some tests.
"""

from os import makedirs, chdir, popen
from xml.dom.minidom import Document
from sqlalchemy import create_engine

from xmlrpclib import SafeTransport, Server, ProtocolError
from urllib2 import Request as CookieRequest
from cookielib import LWPCookieJar
from os.path import exists
from base64 import encodestring

import sys

def generation_Pserver(directory):
    """
    generate the package 'test' for the Package Server tests
    """
    
    makedirs ("%s/test" %(directory))#create the directory of the test's package
    
    doc=Document()

    comment = doc.createComment("DOCTYPE package SYSTEM \"package_v1.dtd\"")
    doc.appendChild(comment)
    
    package = doc.createElement("package")
    package.setAttribute("id","test")
    doc.appendChild(package)
    
    name = doc.createElement("name")
    package.appendChild(name)
    
    natext = doc.createTextNode("TestPackage")
    name.appendChild(natext)
    
    version = doc.createElement("version")
    package.appendChild(version)
    
    numeric = doc.createElement("numeric")
    version.appendChild(numeric)
    
    nutext = doc.createTextNode("")
    numeric.appendChild(nutext)
    
    label = doc.createElement("label")
    version.appendChild(label)
    
    latext = doc.createTextNode("2.0.0.9")
    label.appendChild(latext)
    
    description = doc.createElement("description")
    package.appendChild(description)
    
    dtext = doc.createTextNode("Ceci est le package de test")
    description.appendChild(dtext)
    
    commands = doc.createElement("commands")
    commands.setAttribute("reboot","1")
    package.appendChild(commands)
    
    Precommands = doc.createElement("Precommands")
    commands.appendChild(Precommands)
    
    Ptext = doc.createTextNode("")
    Precommands.appendChild(Ptext)
    
    installInit = doc.createElement("installInit")
    commands.appendChild(installInit)
    
    itext = doc.createTextNode("")
    installInit.appendChild(itext)
    
    
    command = doc.createElement("command")
    command.setAttribute("name","commande")
    commands.appendChild(command)
    
    ctext = doc.createTextNode("./install.bat")
    command.appendChild(ctext)
    
    postCommandSuccess = doc.createElement("postCommandSuccess")
    commands.appendChild(postCommandSuccess)
    
    Stext = doc.createTextNode("")
    postCommandSuccess.appendChild(Stext)
    
    postCommandFailure = doc.createElement("postCommandFailure")
    commands.appendChild(postCommandFailure)
    
    Ftext = doc.createTextNode("")
    postCommandFailure.appendChild(Ftext)
    
    
    fichier=open("%s/test/conf.xml" %(directory),"w")
    doc.writexml(fichier,indent="   ",addindent="    ",newl="\n", encoding="utf-8")
    
    chdir("%s/test" %(directory))
    instalfile=open("install.bat","w")
    instalfile.write("I can\'t be installed")
    instalfile.close()
    
def ipconfig():
    """
    Returns the current system IP address (from eth0).
    """
    conf=popen("/sbin/ifconfig eth0")
    server=conf.read()
    server=server.split()
    ipserver=server[6][5:]
    if ipserver == "":
        print "The computer doesn't have an IP address on the eth0 interface"
        sys.exit(1)
    return ipserver
    
def generation_Launcher(directory):
    """
    Generate the temporary files for Launcher's tests.
    """
    chdir(directory)
    testfile=open("test.bin","w")
    testfile.write("file test")
    testfile.close()

def generation_Machine(driver,host,port):
    """
    Add a computer into the inventory database.
    """

    connectionM=create_engine('%s://mmc:mmc@%s:%s/inventory' %(driver,host,port))
    m=connectionM.connect()

    m.execute("""INSERT INTO `Inventory` VALUES (1,'0000-00-00','00:00:00',1)""")

    m.execute("""INSERT INTO `Machine` VALUES (1,'localhost',NULL,NULL,NULL,NULL)""")

    m.execute("""INSERT INTO `Network` VALUES (1,NULL,NULL,NULL,NULL,'',NULL,'127.0.0.1','',NULL,NULL)""")

    m.execute("""INSERT INTO `hasCustom` VALUES (1,1,1)""")

    m.execute("""INSERT INTO `hasEntity` VALUES (1,1,1)""")

    m.execute("""INSERT INTO `hasNetwork` VALUES (1,1,1)""")

    m.close()

    return connectionM

def generation_Commands(driver,host,port):

    connectionC=create_engine('%s://mmc:mmc@%s:%s/msc' %(driver,host,port))
    c=connectionC.connect()

    c.execute("""INSERT INTO `commands` VALUES (1,'active','2029-10-29 22:53:58','sleep 360\n','','enable','enable','','0000-00-00 00:00:00','2029-01-01 00:00:00','root','root','YES','Test Mandriva : Pause 6 minute\n','disable','disable',360,3,NULL,NULL,NULL,NULL,NULL,NULL,0,NULL,'disable','',NULL,NULL,NULL,'none') """)
    
    c.execute("""INSERT INTO `commands` VALUES (2,'active','2029-10-29 22:53:58','sleep 360\n','','enable','enable','','0000-00-00 00:00:00','2029-01-01 00:00:00','root','root','YES','Test Mandriva : Pause 6 minute\n','disable','disable',360,3,NULL,NULL,NULL,NULL,NULL,NULL,0,NULL,'disable','',NULL,NULL,NULL,'none') """)

    c.execute(""" INSERT INTO `commands_on_host` VALUES (1,1,'localhost','2009-10-29 22:54:00',NULL,'execution_in_progress','pending','IGNORED','IGNORED','WORK_IN_PROGRESS','TODO','TODO','TODO','TODO','2009-10-29 22:53:59',3,0,'launcher_01',1,'scheduler_01',NULL,NULL,NULL,0) """)
    
    c.execute(""" INSERT INTO `commands_on_host` VALUES (2,2,'localhost','2009-10-29 22:54:00','2029-10-29 22:54:00','scheduled','pending','IGNORED','IGNORED','TODO','TODO','TODO','TODO','TODO','2009-10-29 23:53:59',3,0,'launcher_01',1,'scheduler_01',NULL,NULL,NULL,0) """)
    
    c.execute(""" INSERT INTO `commands_on_host` VALUES (3,1,'localhost','2009-10-29 22:54:00','2029-10-29 22:54:00','scheduled','pending','IGNORED','IGNORED','TODO','TODO','TODO','TODO','TODO','2009-10-29 23:53:59',3,0,'launcher_01',1,'scheduler_01',NULL,NULL,NULL,0) """)
    
    c.execute(""" INSERT INTO `target` VALUES (1,'localhost','file://0','','UUID1','','','','') """)

    c.close()

    return connectionC


def SupEspLi (li):
    """Delete spaces in list"""
    # Verify if the element at the index i is a string or recall SupEsp
    for i in range (0,len(li)):
        if type (li[i]) == type (""):
            li[i]=li[i].strip()
        else:
            SupEsp(li[i])

def SupEspDi (di):
    """Delete spaces in dict"""
    # Verify if the values associated at the key k is a string or recall SupEsp
    for k in di.keys():
        if type (di[k]) == type (""):
            di[k]=di[k].strip()
        else:
            SupEsp(di[k])

def SupEsp (obj):
    """
    Call the function SupEspLi if the object is a list, SupEspDi if it's a dict or if it's a string return the string without the space.
    """
    if type(obj) == type([]):
        SupEspLi(obj)
    elif type(obj) == type({}):
        SupEspDi(obj)
    elif type(obj) == type(""):
        lobj=[obj]
        lobj[0]=lobj[0].strip()
        obj=lobj[0]
        return obj

"""
MMC Synchronous Client.

MMC use a modify XMLRPC implementation which use cookies and authentification.
This module provides a function called MMCProxy that returned a xmlrpc.Server
object, which use a modified Transport (called here MMCSafeTransport).

Cookies are stored as a LWPCookieJar in "/tmp/cookies".
"""

def MMCProxy (server_uri, verbose = False):
    """
    This method returns a xmlrpc.Server object with an appropriate Transport
    object to interact with the MMC.
    """

    # Convert http://login:password@host:port to (login, password)
    auth = tuple(server_uri.rsplit('@')[0][8:].split(':',1))
    return Server(server_uri, transport=MMCSafeTransport(auth), verbose=verbose)

class MMCSafeTransport(SafeTransport):
    """
    Standard synchronous Transport for the MMC agent.
    MMC agent provides a slightly modified XMLRPC interface.
    Each xmlrpc request has to contains a modified header containing a
    valid session ID and authentication information.
    """

    user_agent = 'AdminProxy'

    def __init__(self, auth= (), use_datetime = 0):
        """
        This method returns an XMLRPC client which supports
        basic authentication through cookies.
        """
        self.cookiefile = '/tmp/cookies'

        self.credentials = auth
        # See xmlrpc.Transport Class
        self._use_datetime = use_datetime

    def send_basic_auth(self, connection):
        """Include HTTPS Basic Authentication data in a header"""

        auth = encodestring("%s:%s"%self.credentials).strip()
        auth = 'Basic %s' %(auth,)
        connection.putheader('Authorization',auth)

    def send_cookie_auth(self, connection):
        """Include Cookie Authentication data in a header"""

        cj = LWPCookieJar()
        cj.load(self.cookiefile, ignore_discard=True, ignore_expires=True)

        for cookie in cj:
            connection.putheader('Cookie', '%s=%s' % (cookie.name, cookie.value))

    ## override the send_host hook to also send authentication info
    def send_host(self, connection, host):
        """
        This method override the send_host method of SafeTransport to send
        authentication and cookie info.
        """
        SafeTransport.send_host(self, connection, host)
        if exists(self.cookiefile):
            self.send_cookie_auth(connection)
        elif self.credentials != ():
            self.send_basic_auth(connection)

    def request(self, host, handler, request_body, verbose=0):

        class CookieResponse:
            """
            Adaptater for the LWPCookieJar.extract_cookies
            """
            def __init__(self, headers):
                self.headers = headers
            def info(self):
                return self.headers

        crequest = CookieRequest('https://'+host+'/')

        # issue XML-RPC request
        h = self.make_connection(host)
        if verbose:
            h.set_debuglevel(1)

        self.send_request(h, handler, request_body)
        self.send_host(h, host)
        self.send_user_agent(h)

        self.send_content(h, request_body)

        errcode, errmsg, headers = h.getreply()
        cresponse = CookieResponse(headers)

        # Creating cookie jar when needed
        if '<methodName>base.ldapAuth</methodName>' in request_body:
            cj = LWPCookieJar()
            cj.extract_cookies(cresponse, crequest)
            if len(cj) >0 and self.cookiefile != None:
                cj.save(self.cookiefile, ignore_discard=True, ignore_expires=True)

        if errcode != 200:
            raise ProtocolError(
                host + handler,
                errcode, errmsg,
                headers
                )

        self.verbose = verbose

        try:
            sock = h._conn.sock
        except AttributeError:
            sock = None

        result = self._parse_response(h.getfile(), sock)
        if isinstance(result, tuple) and isinstance(result[0], dict) and 'faultCode' in result[0]:
            errcode = result[0]['faultCode']
            raise RuntimeError(errcode)
        return result


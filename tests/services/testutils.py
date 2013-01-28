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
import sys
from os import makedirs, chdir, popen, path

from xml.dom.minidom import Document
from sqlalchemy import create_engine

from mmc.site import mmcconfdir
from pulse2.database.config import DatabaseConfig

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
    dbpasswd = DatabaseConfig.dbpasswd
    connectionM=create_engine('%s://mmc:%s@%s:%s/inventory' %(driver,dbpasswd,host,port))
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

    # Read config from ini file
    inifile = path.join(mmcconfdir, "plugins", "pulse2.ini")
    config = DatabaseConfig()
    config.setup(inifile)

    dbpasswd = config.dbpasswd
    connectionC=create_engine('%s://mmc:%s@%s:%s/msc' %(driver,dbpasswd,host,port))
    c=connectionC.connect()

    c.execute("""INSERT INTO `commands` VALUES (1,'active','2029-10-29 22:53:58','sleep 360\n','','enable','enable','','0000-00-00 00:00:00','2029-01-01 00:00:00','root','root','YES','Test Mandriva : Pause 6 minute\n','disable','disable',360,3,NULL,NULL,NULL,NULL,NULL,NULL,0,NULL,'disable','',NULL,NULL,NULL,'none') """)
    
    c.execute("""INSERT INTO `commands` VALUES (2,'active','2029-10-29 22:53:58','sleep 360\n','','enable','enable','','0000-00-00 00:00:00','2029-01-01 00:00:00','root','root','YES','Test Mandriva : Pause 6 minute\n','disable','disable',360,3,NULL,NULL,NULL,NULL,NULL,NULL,0,NULL,'disable','',NULL,NULL,NULL,'none') """)

    c.execute(""" INSERT INTO `commands_on_host` VALUES (1,1,'localhost','2009-10-29 22:54:00',NULL,'execution_in_progress','pending','IGNORED','IGNORED','WORK_IN_PROGRESS','TODO','TODO','TODO','TODO','2009-10-29 22:53:59',3,0,0,0,'launcher_01',1,'scheduler_01',NULL,NULL,NULL,0) """)
    
    c.execute(""" INSERT INTO `commands_on_host` VALUES (2,2,'localhost','2009-10-29 22:54:00','2029-10-29 22:54:00','scheduled','pending','IGNORED','IGNORED','TODO','TODO','TODO','TODO','TODO','2009-10-29 23:53:59',3,0,0,0,'launcher_01',1,'scheduler_01',NULL,NULL,NULL,0) """)
    
    c.execute(""" INSERT INTO `commands_on_host` VALUES (3,1,'localhost','2009-10-29 22:54:00','2029-10-29 22:54:00','scheduled','pending','IGNORED','IGNORED','TODO','TODO','TODO','TODO','TODO','2009-10-29 23:53:59',3,0,0,0,'launcher_01',1,'scheduler_01',NULL,NULL,NULL,0) """)
    
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

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
Test module for the Pulse 2 package server: Mirror's module, Mirror_API's module, Package_API's module and Scheduler's module
"""

import xmlrpclib
import unittest
import urllib2
import sys
import string
from os import system, getcwd, chdir, popen
from testutils import generation_Pserver, SupEsp, ipconfig
from time import sleep
from tempfile import mkdtemp

uuid='UUID1' #client uuid
protocol='https' #protocol's server
makefile=False
# FIXME: we'd better get it from the package files size
PKGSIZE = 66

if "makefile" in sys.argv:
    makefile=True

if "debug" in sys.argv:
    mode="debug"
    Verbosity=2
else:
    mode="info"

del(sys.argv[1:])

directory=getcwd()


ipserver=ipconfig()

serverM=xmlrpclib.ServerProxy('%s://%s:9990/mirror1' %(protocol,ipserver))
serverMA = xmlrpclib.ServerProxy('%s://%s:9990/rpc' %(protocol,ipserver))
serverP = xmlrpclib.ServerProxy('%s://%s:9990/package_api_get1' %(protocol,ipserver))
serverS = xmlrpclib.ServerProxy('%s://%s:9990/scheduler_api' %(protocol,ipserver))

class class01testMirror (unittest.TestCase):
    """
    Test's class of Mirror's module
    """
    def test101isAvailable (self):
        result=serverM.isAvailable("test")
        self.assertEqual (result,True)

    def test102getFilePath (self):
        result=serverM.getFilePath("5d3ff03e396aa072f5cae2b2ddcd88b9")
        self.assertEqual (result,"%s://%s:9990/mirror1_files/test/MD5SUMS" %(protocol,ipserver))

    def test103getFileURI (self):
        result=serverM.getFileURI("5d3ff03e396aa072f5cae2b2ddcd88b9")
        self.assertEqual (result,"%s://%s:9990/mirror1_files/test/MD5SUMS" %(protocol,ipserver))

    def test104getFilesURI (self):
        result=serverM.getFilesURI(["5d3ff03e396aa072f5cae2b2ddcd88b9","7885517b39317add6a1d362968b01774"])
        self.assertEqual (result,['%s://%s:9990/mirror1_files/test/MD5SUMS' %(protocol,ipserver), '%s://%s:9990/mirror1_files/test/install.bat' %(protocol,ipserver)])

class class02testMirror_API (unittest.TestCase):
    """
    Test's class of Mirror_API's module
    """

    def test201getApiPackage (self):
        result=serverMA.getApiPackage({'uuid':uuid})
        self.assertEqual (result,[{'mountpoint': '/package_api_get1', 'server': ipserver, 'protocol': protocol, 'uuid': 'UUID/package_api_get1', 'port': '9990'}])

    def test202getApiPackages (self):
        result=serverMA.getApiPackages([{'uuid':uuid},{'uuid':uuid}])
        self.assertEqual (result,[[{'mountpoint': '/package_api_get1', 'server': ipserver, 'protocol': protocol, 'uuid': 'UUID/package_api_get1', 'port': '9990'}], [{'mountpoint': '/package_api_get1', 'server': ipserver, 'protocol': protocol, 'uuid': 'UUID/package_api_get1', 'port': '9990'}]])

    def test203getMirror (self):
        result=serverMA.getMirror({'uuid':uuid})
        self.assertEqual (result, {'mountpoint': '/mirror1', 'server': ipserver, 'protocol': protocol, 'uuid': 'UUID/mirror1', 'port': '9990'})

    def test204getMirrors (self):
        result=serverMA.getMirrors([{'uuid':uuid},{'uuid':uuid}])
        self.assertEqual (result,[{'mountpoint': '/mirror1', 'server': ipserver, 'protocol': protocol, 'uuid': 'UUID/mirror1', 'port': '9990'}, {'mountpoint': '/mirror1', 'server': ipserver, 'protocol': protocol, 'uuid': 'UUID/mirror1', 'port': '9990'}])

    def test205getFallbackMirror (self):
        result=serverMA.getFallbackMirror({'uuid':uuid})
        self.assertEqual (result,{'mountpoint': '/mirror1', 'server': ipserver, 'protocol': protocol, 'uuid': 'UUID/mirror1', 'port': '9990'})

    def test206getFallbackMirrors (self):
        result = serverMA.getFallbackMirrors([{'uuid':uuid},{'uuid':uuid}])
        self.assertEqual (result,[{'mountpoint': '/mirror1', 'server': ipserver, 'protocol': protocol, 'uuid': 'UUID/mirror1', 'port': '9990'}, {'mountpoint': '/mirror1', 'server': ipserver, 'protocol': protocol, 'uuid': 'UUID/mirror1', 'port': '9990'}])

    def test207getServerDetails (self):
        result=serverMA.getServerDetails()
        self.assertEqual (result, {'package_api': [{'mountpoint': '/package_api_get1', 'server': ipserver, 'protocol': protocol, 'uuid': 'UUID/package_api_get1', 'port': '9990'}], 'mirror': [{'mountpoint': '/mirror1', 'server': ipserver, 'protocol': protocol, 'uuid': 'UUID/mirror1', 'port': '9990'}]})

class class03testPackages_get (unittest.TestCase):
    """
    Test's class of Package_API's module
    """

    def test301getAllPendingPackages (self):
        result=serverP.getAllPendingPackages({'mountpoint': '/mirror1', 'server': ipserver, 'protocol': protocol, 'uuid': 'UUID/mirror1', 'port': '9990'})
        self.assertEqual (result,[])

    def test302getAllPackages (self):
        result=serverP.getAllPackages({'mountpoint': '/mirror1', 'server': ipserver, 'protocol': protocol, 'uuid': 'UUID/mirror1', 'port': '9990'})
        SupEsp(result)
        self.assertEqual (result,[{'postCommandSuccess': {'command': '', 'name': ''}, 'files': [{'path': '/test', 'name': 'install.bat', 'id': '7885517b39317add6a1d362968b01774'}, {'path': '/test', 'name': 'MD5SUMS', 'id': '5d3ff03e396aa072f5cae2b2ddcd88b9'}], 'installInit': {'command': '', 'name': ''}, 'description': 'Ceci est le package de test', 'preCommand': {'command': '', 'name': ''}, 'basepath': direct, 'reboot': '1', 'label': 'TestPackage', 'version': '2.0.0.9', 'command': {'command': './install.bat', 'name': 'commande'}, 'postCommandFailure': {'command': '', 'name': ''}, 'id': 'test', 'size': PKGSIZE}])

    def test303getLocalPackagePath (self):
        result=serverP.getLocalPackagePath ("test")
        self.assertEqual (result,directory_temp)

    def test304getLocalPackagesPath (self):
       result=serverP.getLocalPackagesPath(["test","test"])
       self.assertEqual (result,[directory_temp,directory_temp])

    def test305getPackageDetail (self):
        result=serverP.getPackageDetail("test")
        SupEsp(result)
        self.assertEqual (result,{'postCommandSuccess': {'command': '', 'name': ''}, 'files': [{'path': '/test', 'name': 'install.bat', 'id': '7885517b39317add6a1d362968b01774'}, {'path': '/test', 'name': 'MD5SUMS', 'id': '5d3ff03e396aa072f5cae2b2ddcd88b9'}], 'installInit': {'command': '', 'name': ''}, 'description': 'Ceci est le package de test', 'preCommand': {'command': '', 'name': ''}, 'basepath': direct, 'reboot': '1', 'label': 'TestPackage', 'version': '2.0.0.9', 'command': {'command': './install.bat', 'name': 'commande'}, 'postCommandFailure': {'command': '', 'name': ''}, 'id': 'test', 'size': PKGSIZE})

    def test306getPackagesDetail (self):
        result = serverP.getPackagesDetail(["test","test"])
        SupEsp(result)
        self.assertEqual (result,[{'postCommandSuccess': {'command': '', 'name': ''}, 'files': [{'path': '/test', 'name': 'install.bat', 'id': '7885517b39317add6a1d362968b01774'}, {'path': '/test', 'name': 'MD5SUMS', 'id': '5d3ff03e396aa072f5cae2b2ddcd88b9'}], 'installInit': {'command': '', 'name': ''}, 'description': 'Ceci est le package de test', 'preCommand': {'command': '', 'name': ''}, 'basepath': direct, 'reboot': '1', 'label': 'TestPackage', 'version': '2.0.0.9', 'command': {'command': './install.bat', 'name': 'commande'}, 'postCommandFailure': {'command': '', 'name': ''}, 'id': 'test', 'size': PKGSIZE},{'postCommandSuccess': {'command': '', 'name': ''}, 'files': [{'path': '/test', 'name': 'install.bat', 'id': '7885517b39317add6a1d362968b01774'}, {'path': '/test', 'name': 'MD5SUMS', 'id': '5d3ff03e396aa072f5cae2b2ddcd88b9'}], 'installInit': {'command': '', 'name': ''}, 'description': 'Ceci est le package de test', 'preCommand': {'command': '', 'name': ''}, 'basepath': direct, 'reboot': '1', 'label': 'TestPackage', 'version': '2.0.0.9', 'command': {'command': './install.bat', 'name': 'commande'}, 'postCommandFailure': {'command': '', 'name': ''}, 'id': 'test', 'size': PKGSIZE}])

    def test307getPackageCommand (self):
        result=serverP.getPackageCommand("test")
        SupEsp(result)
        self.assertEqual (result,{'command': './install.bat', 'name': 'commande'})

    def test308getPackageFiles (self):
        result=serverP.getPackageFiles("test")
        SupEsp(result)
        self.assertEqual (result,[{'path': '/test', 'name': 'install.bat', 'id': '7885517b39317add6a1d362968b01774'}, {'path': '/test', 'name': 'MD5SUMS', 'id': '5d3ff03e396aa072f5cae2b2ddcd88b9'}])

    def test309getPackageInstallInit (self):
        result=serverP.getPackageInstallInit("test")
        SupEsp(result)
        self.assertEqual (result,{'command': '', 'name': ''})

    def test310getPackageHasToReboot (self):
        result=serverP.getPackageHasToReboot("test")
        self.assertEqual (result,"1")

    def test311getPackageLabel (self):
        result=serverP.getPackageLabel("test")
        cresult = SupEsp(result)
        self.assertEqual (cresult,"TestPackage")

    def test312getPackagePostCommandFailure (self):
        result=serverP.getPackagePostCommandFailure("test")
        SupEsp(result)
        self.assertEqual (result,{'command': '', 'name': ''})

    def test313getPackagePreCommand (self):
        result=serverP.getPackagePreCommand("test")
        SupEsp(result)
        self.assertEqual (result,{'command': '', 'name': ''})

    def test314getPackagePostCommandSucces (self):
        result=serverP.getPackagePostCommandSuccess("test")
        SupEsp(result)
        self.assertEqual (result,{'command': '', 'name': ''})

    def test315getPackageSize (self):
        result=serverP.getPackageSize("test")
        self.assertEqual(result, PKGSIZE)

    def test316isAvailable (self):
        result=serverP.isAvailable("test",{'mountpoint': '/mirror1', 'server': ipserver, 'protocol': protocol, 'uuid': 'UUID/package_api_get1', 'port': '9990'})
        self.assertEqual (result,True)

    def test317getServerDetails (self):
        result=serverP.getServerDetails()
        SupEsp(result)
        self.assertEqual (result,[{'postCommandSuccess': {'command': '', 'name': ''}, 'files': [{'path': '/test', 'name': 'install.bat', 'id': '7885517b39317add6a1d362968b01774'}, {'path': '/test', 'name': 'MD5SUMS', 'id': '5d3ff03e396aa072f5cae2b2ddcd88b9'}], 'installInit': {'command': '', 'name': ''}, 'description': 'Ceci est le package de test', 'preCommand': {'command': '', 'name': ''}, 'basepath': direct, 'reboot': '1', 'label': 'TestPackage', 'version': '2.0.0.9', 'command': {'command': './install.bat', 'name': 'commande'}, 'postCommandFailure': {'command': '', 'name': ''}, 'id': 'test', 'size': PKGSIZE}])

    def test318getPackageVersion (self):
        result=serverP.getPackageVersion("test")
        cresult=SupEsp(result)
        self.assertEqual (cresult,'2.0.0.9')

#    def test319getPackagesIds (self):
#        result=serverP.getPackagesIds("TestPackage")
#        self.assertEqual (result,{})

#    def test320getPackageId (self):
#        result=serverP.getPackageId("TestPackage","2.0.0.9")
#        self.assertEqual (result,'test')

#    def test321getFileChecksum (self):
#        result=serverP.getFileChecksum("7885517b39317add6a1d362968b01774")
#        self.assertEqual (result,27)

#    def test322getFilesChecksum (self):
#        result=serverP.getFileChecksum(["7885517b39317add6a1d362968b01774","5d3ff03e396aa072f5cae2b2ddcd88b9"])
#        self.assertEqual (result,[27,27])

class class04testScheduler (unittest.TestCase):
    """
    Test's class of Scheduler's module
    """
    def test401getScheduler(self):
        result=serverS.getScheduler({'uuid':uuid})
        if result in ["scheduler_01","scheduler_02"]:
            sresult=result
        else:
            sresult="echec"
        self.assertEqual(result,sresult)

    def test402getSchedulers(self):
        result=serverS.getSchedulers([{'uuid':uuid},{'uuid':uuid}])
        if (result[0] in ["scheduler_01","scheduler_02"]) & (result[1] in ["scheduler_01","scheduler_02"]):
            sresult=result
        else:
            sresult="echec"
        self.assertEqual(result,sresult)

class class05valid_urlTest(unittest.TestCase):
    """
    Test's class which test if the dowloading urls work
    """
    def test501valid_url(self):
        for package in serverM.getFilesURI(["7885517b39317add6a1d362968b01774","5d3ff03e396aa072f5cae2b2ddcd88b9"]):
            package1=string.split(package)
            cpackage=string.joinfields(package1,"%20")
            urllib2.urlopen(cpackage)

class class06removedirTest(unittest.TestCase):
    """
    Test's class which exist only for remove the tempory's package
    """
    def test601removedirs(self):
        system ("rm -rf %s/*" %(directory_temp))

if makefile:
    test=popen('ps ax|grep \"bin/pulse2-package-server\"')
    t=test.read()
    ts=t.split()
    process=int(ts[0])
    test.close()
    system ("kill %i" %(process))
    directory_temp=mkdtemp(suffix='Pserver',prefix='pulse2',dir="/tmp")
    generation_Pserver(directory)
    direct=directory_temp+'/test'
    chdir("%s/config/" %(directory))
    system( "sed \'s/src = /src = \/tmp\/%s/\' package_server.conf > package-server.conf" %(directory_temp[5:]))
    system( "sed -i \'s/host = /host = %s/\' package-server.conf" %(ipserver))
    system ("PYTHONPATH=%s/services/ %s/services/bin/pulse2-package-server -f %s/config/package-server.conf" %(directory,directory,directory))
else:
    directory_temp='/var/lib/pulse2/packages'
    generation_Pserver(directory_temp)
    direct='/var/lib/pulse2/packages/test'
    system ("/etc/init.d/pulse2-package-server restart")

sleep(10)

if mode=="debug":
    success=[]
    nb=0
    for klass in [class01testMirror,class02testMirror_API,class03testPackages_get,class04testScheduler,class05valid_urlTest,class06removedirTest]:
        suite = unittest.TestLoader().loadTestsFromTestCase(klass)
        test=unittest.TextTestRunner(verbosity=Verbosity).run(suite)
        success.append(test.wasSuccessful())
        nb=nb+test.testsRun


    if False in success:
        print "One or more test are failed or have an unexpected error"
    else:
        print "All function work"

    print "Pserver\'s test has run %s test" %(nb)
else:

    unittest.main()

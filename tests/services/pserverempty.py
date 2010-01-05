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

import sys
import xmlrpclib
import unittest
from os import system

from testutils import ipconfig
from time import sleep

"""
Test module of package server: Mirror's module, Mirror_API's module, Package_API's module and Scheduler's module

Theses tests allows to stress Package Server behaviours when no package are
available.
"""

ipserver = ipconfig()
uuid='UUID1' #client uuid
protocol='http' #protocol's server

if "debug" in sys.argv:
    mode="debug"
    Verbosity=2
else:
    mode="info"

del(sys.argv[1:])

#remove if exist the package test
system ("rm -rf /var/lib/pulse2/packages/test")

serverM=xmlrpclib.ServerProxy('%s://%s:9990/mirror1' %(protocol,ipserver))
serverMA = xmlrpclib.ServerProxy('%s://%s:9990/rpc' %(protocol,ipserver))
serverP = xmlrpclib.ServerProxy('%s://%s:9990/package_api_get1' %(protocol,ipserver))
serverS = xmlrpclib.ServerProxy('%s://%s:9990/scheduler_api' %(protocol,ipserver))

class class01testMirror (unittest.TestCase):
    """
    Test's class of Mirror's module
    """
    
    def test101isAvailable (self):
        result = serverM.isAvailable ("test")
        self.assertEqual (result,False)

    def test102getFilePath (self):
        result = serverM.getFilePath ("43f38f712223725ac3e220b96889484b")
        self.assertEqual (result,"")

    def test103getFileURI (self):
        result = serverM.getFileURI ("43f38f712223725ac3e220b96889484b")
        self.assertEqual (result,"")

    def test104getFilesURI (self):
        result = serverM.getFilesURI (["43f38f712223725ac3e220b96889484b","baf68c123b04d61856f71fe07b7bd84b"])
        self.assertEqual (result,["",""])

class class02testMirror_API (unittest.TestCase):
    """
    Test's class of Mirror_API's module
    """

    def test201getApiPackage (self):
        result = serverMA.getApiPackage ({'uuid':uuid})
        self.assertEqual (result,[{'mountpoint': '/package_api_get1', 'server': ipserver, 'protocol': protocol, 'uuid': 'UUID/package_api_get1', 'port': '9990'}])

    def test202getApiPackages (self):
        result = serverMA.getApiPackages ([{'uuid':uuid},{'uuid':uuid}])
        self.assertEqual (result,[[{'mountpoint': '/package_api_get1', 'server': ipserver, 'protocol': protocol, 'uuid': 'UUID/package_api_get1', 'port': '9990'}], [{'mountpoint': '/package_api_get1', 'server': ipserver, 'protocol': protocol, 'uuid': 'UUID/package_api_get1', 'port': '9990'}]])

    def test203getMirror (self):
        result = serverMA.getMirror ({'uuid':uuid})
        self.assertEqual (result, {'mountpoint': '/mirror1', 'server': ipserver, 'protocol': protocol, 'uuid': 'UUID/mirror1', 'port': '9990'})

    def test204getMirrors (self):
        result = serverMA.getMirrors ([{'uuid':uuid},{'uuid':uuid}])
        self.assertEqual (result,[{'mountpoint': '/mirror1', 'server': ipserver, 'protocol': protocol, 'uuid': 'UUID/mirror1', 'port': '9990'}, {'mountpoint': '/mirror1', 'server': ipserver, 'protocol': protocol, 'uuid': 'UUID/mirror1', 'port': '9990'}])

    def test205getFallbackMirror (self):
        result = serverMA.getFallbackMirror ({'uuid':uuid})
        self.assertEqual (result,{'mountpoint': '/mirror1', 'server': ipserver, 'protocol': protocol, 'uuid': 'UUID/mirror1', 'port': '9990'})

    def test206getFallbackMirrors (self):
        result = serverMA.getFallbackMirrors ([{'uuid':uuid},{'uuid':uuid}])
        self.assertEqual (result,[{'mountpoint': '/mirror1', 'server': ipserver, 'protocol': protocol, 'uuid': 'UUID/mirror1', 'port': '9990'}, {'mountpoint': '/mirror1', 'server': ipserver, 'protocol': protocol, 'uuid': 'UUID/mirror1', 'port': '9990'}])

    def test207getServerDetails (self):
        result = serverMA.getServerDetails ()
        self.assertEqual (result, {'package_api': [{'mountpoint': '/package_api_get1', 'server': ipserver, 'protocol': protocol, 'uuid': 'UUID/package_api_get1', 'port': '9990'}], 'mirror': [{'mountpoint': '/mirror1', 'server': ipserver, 'protocol': protocol, 'uuid': 'UUID/mirror1', 'port': '9990'}]})

class class03testPackages_get (unittest.TestCase):
    """
    Test's class of Package_API's module
    """

    def test301getAllPendingPackages (self):
        result = serverP.getAllPendingPackages ({'mountpoint': '/mirror1', 'server': ipserver, 'protocol': protocol, 'uuid': 'UUID/mirror1', 'port': '9990'})
        self.assertEqual (result,[])

    def test302getAllPackages (self):
        result = serverP.getAllPackages ({'mountpoint': '/mirror1', 'server': ipserver, 'protocol': protocol, 'uuid': 'UUID/mirror1', 'port': '9990'})
        self.assertEqual (result,[])

    def test303getLocalPackagePath (self):
        result = serverP.getLocalPackagePath ("test")
        self.assertEqual (result,{})

    def test304getLocalPackagesPath (self):
       result = serverP.getLocalPackagesPath (["test","test"])
       self.assertEqual (result,[])

    def test305getPackageDetail (self):
        result = serverP.getPackageDetail ("test")
        self.assertEqual (result,{})

    def test306getPackagesDetail (self):
        result = serverP.getPackagesDetail (["test","test"])
        self.assertEqual (result,[])

#    def test307getPackageCommand (self):
#        result = serverP.getPackageCommand ("test")
#        self.assertEqual (result,{})

#    def test308getPackageFiles (self):
#        result = serverP.getPackageFiles ("test")
#        self.assertEqual (result,[])

#    def test309getPackageInstallInit (self):
#        result = serverP.getPackageInstallInit ("test")
#        self.assertEqual (result,{})

#    def test310getPackageHasToReboot (self):
#        result = serverP.getPackageHasToReboot ("test")
#        self.assertEqual (result,"0")

#    def test311getPackageLabel (self):
#        result = serverP.getPackageLabel ("test")
#        self.assertEqual (result,None)

#    def test312getPackagePostCommandFailure (self):
#        result = serverP.getPackagePostCommandFailure ("test")
#        self.assertEqual (result,{})

#    def test313getPackagePreCommand (self):
#        result = serverP.getPackagePreCommand ("test")
#        self.assertEqual (result,{})

#    def test314getPackagePostCommandSucces (self):
#        result = serverP.getPackagePostCommandSuccess ("test")
#        self.assertEqual (result,{})

#    def test315getPackageSize (self):
#        result = serverP.getPackageSize ("test")
#        self.assertEqual (result,0)

#     def test316isAvailable (self): #The test 'testisAvailable' return true but the package don't exist 
#         result = serverP.isAvailable ("test",{'mountpoint': '/mirror1', 'server': ipserver, 'protocol': protocol, 'uuid': 'UUID/package_api_get1', 'port': '9990'})
#        self.assertEqual (result,False)

    def test317getServerDetails (self):
        result = serverP.getServerDetails ()
        self.assertEqual (result,[])

#     def test318getPackageVersion (self):
#         result = serverP.getPackageVersion ("test")
#         self.assertEqual (result,None)

#    def test319getPackagesIds (self):
#        result = serverP.getPackagesIds ("TestPackage")
#        self.assertEqual (result,{})

#    def test320getPackageId (self):
#        result = serverP.getPackageId ("TestPackage","2.0.0.9")
#        self.assertEqual (result,'')

    def test321getFileChecksum (self):
        result = serverP.getFileChecksum ("baf68c123b04d61856f71fe07b7bd84b")
        self.assertEqual (result,0)

    def test322getFilesChecksum (self):
        result = serverP.getFileChecksum (["baf68c123b04d61856f71fe07b7bd84b","43f38f712223725ac3e220b96889484b"])
        self.assertEqual (result,0)

class class04testScheduler (unittest.TestCase):
    """
    Test's class of Scheduler's module
    """
    def test401getScheduler(self):
        result = serverS.getScheduler({'uuid':uuid})
        if result in ["scheduler_01","scheduler_02"]:
            sresult=result
        else:
            sresult="echec"
        self.assertEqual(result,sresult)

    def test402getSchedulers(self):
        result = serverS.getSchedulers([{'uuid':uuid},{'uuid':uuid}])
        if (result[0] in ["scheduler_01","scheduler_02"]) & (result[1] in ["scheduler_01","scheduler_02"]):
            sresult=result
        else:
            sresult="echec"
        self.assertEqual(result,sresult)

system ("/etc/init.d/pulse2-package-server restart")
sleep(10)

if mode=="debug":
    success=[]
    nb=0
    for klass in [class01testMirror,class02testMirror_API,class03testPackages_get,class04testScheduler]:
        suite = unittest.TestLoader().loadTestsFromTestCase(klass)
        test=unittest.TextTestRunner(verbosity=Verbosity).run(suite)
        success.append(test.wasSuccessful())
        nb=nb+test.testsRun


    if False in success:
        print "One or more test are failed or have an unexpected error"
    else:
        print "All function work"
    
    print "PserverEmpty\'s test has run %s test" %(nb)
else:

    unittest.main()

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
Test module for the Pulse 2 MMC Agent dyngroup plugin init
All the values are tested as empty
"""

import unittest
import sys

from unittest import TestCase
from testutils import MMCProxy

# Set options to use to run the tests
makefile = False

if "debug" in sys.argv:
    mode = "debug"
    Verbosity = 2
else:
    mode = "info"

if "makefile" in sys.argv:
    makefile = True

login = 'mmc'
password = 's3cr3t'

client = MMCProxy('https://%s:%s@localhost:7080'%(login, password), False)
client.base.ldapAuth('root', 'secret')

"""
Test class
"""

class class01dyngroupInitTest(TestCase):
    """
    Tests classes of the dyngroup module
    """
    def setUp(self):
        self.client = client.dyngroup
        self.deleteUser = None
        self.deleteGroup = None
        self.deleteProfile = None
        self.deleteShare = None

    def tearDown(self):
        if self.deleteUser != None:
            client.base.delUserFromAllGroups(self.deleteUser)
            client.dyngroup.delmembers_to_group(1337, [self.deleteUser])
        if self.deleteGroup != None:
            client.dyngroup.delete_group(int(self.deleteGroup))
        if self.deleteProfile != None:
            # TODO: Uncomment the following line when it will be implemented in the dyngroup plugin
            # client.dyngroup.delete_profile(int(self.deleteProfile))
            pass
        if self.deleteShare != None:
            client.dyngroup.del_share(self.deleteShare[0], self.deleteShare[1])

    def test201countAllProfiles(self):
        result = self.client.countallprofiles({})
        self.assertEqual(result, 0)

    def test202countAllGroups(self):
        result = self.client.countallgroups({})
        self.assertEqual(result, 0)

    def test203getAllProfiles(self):
        result = self.client.getallprofiles({})
        self.assertEqual(result, [])

    def test204getMachinesProfiles(self):
        result = self.client.getmachinesprofiles([1337, 42, 1983])
        self.assertEqual(result, [False, False, False])

    def test205getMachineProfile(self):
        result = self.client.getmachineprofile(1337)
        self.assertEqual(result, False)

    def test206getAllGroups(self):
        result = self.client.getallgroups({})
        self.assertEqual(result, [])

    def test207groupNameExists(self):
        result = self.client.group_name_exists("Toto")
        self.assertEqual(result, False)

    def test208getGroup(self):
        result = self.client.get_group(1337)
        self.assertEqual(result, False)

    def test209deleteGroup(self):
        result = self.client.delete_group(1337)
        self.assertEqual(result, True)

    def disabledtest210createGroup(self):
        result = self.client.create_group("Group", 0)
        self.assertEqual(type(result), str)
        self.deleteGroup = int(result)

    def test212tosGroup(self):
        # TODO : When the method will be implemented in the dyngroup plugin, test its return value :
        #result = self.client.tos_group()
        #self.assertEqual(result, True)
        pass

    def test213setnameGroup(self):
        result = self.client.setname_group(1337, "Group")
        self.assertEqual(result, False)
        self.deleteGroup = result

    def test214setVisibilityGroup(self):
        # FIXME: Need a test on the group before access to attributes
        #result = self.client.setvisibility_group(1337, 1)
        #self.assertEqual(result, True)
        pass

    def test215requestGroup(self):
        # FIXME: Need a test on the group before access to attributes
        #result = self.client.request_group(1337)
        #self.assertEqual(result, "")
        pass

    def test216setRequestGroup(self):
        # FIXME: Need a test on the group before access to attributes
        #result = self.client.setrequest_group(1337, "inventory.Date==2010-04-29")
        #self.assertEqual(result, 1337)
        pass

    def test217boolGroup(self):
        #result = self.client.setrequest_group(1337, "inventory.Date==2010-04-29")
        #result = self.client.bool_group(1337)
        #self.assertEqual(result, False)
        pass

    def test218setBoolGroup(self):
        # FIXME: Need a test on the group before access to attributes
        #result = self.client.setbool_group(1337, True)
        #self.assertEqual(result, False)
        pass

    def test219requestResultGroup(self):
        # FIXME: Need a test on the group before access to attributes
        #result = self.client.requestresult_group(1337, 0, 10, "")
        #self.assertEqual(result, False)
        pass

    def test220countRequestResultGroup(self):
        # FIXME: Need a test on the group before access to attributes
        #result = self.client.countrequestresult_group(1337, "")
        #self.assertEqual(result, False)
        pass

    def test221resultGroup(self):
        result = self.client.result_group(1337, 0, 10, "")
        self.assertEqual(result, [])

    def test222countResultGroup(self):
        result = self.client.countresult_group(1337, "")
        self.assertEqual(result, '0')

    def test223canShowGroup(self):
        result = self.client.canshow_group(1337)
        self.assertEqual(result, False)

    def test224showGroup(self):
        # FIXME: Need a test on the group before access to attributes
        #result = self.client.show_group(1337)
        #self.assertEqual(result, '1')
        pass

    def test225hideGroup(self):
        # FIXME: Need a test on the group before access to attributes
        #result = self.client.hide_group(1337)
        #self.assertEqual(result, '1')
        pass

    def test226isDynGroup(self):
        result = self.client.isdyn_group(1337)
        self.assertEqual(result, False)

    def test227toDynGroup(self):
        result = self.client.todyn_group(1337)
        self.assertEqual(result, False)

    def test228isRequestGroup(self):
        result = self.client.isrequest_group(1337)
        self.assertEqual(result, False)

    def test229isProfile(self):
        result = self.client.isprofile(1337)
        self.assertEqual(result, False)

    def test230reloadGroup(self):
        # FIXME: Need a test on the group before access to attributes
        #result = self.client.reload_group(1337)
        #self.assertEqual(result, False)
        pass

    def test231addMembersToGroup(self):
        # FIXME: Need a test on the group before access to attributes
        #result = self.client.addmembers_to_group(1337, "UUID1")
        #self.assertEqual(result, False)
        #self.deleteUser = "UUID1"
        pass

    def test232delMembersToGroup(self):
        # FIXME: Need a test on the group before access to attributes
        #result = self.client.delmembers_to_group(1337, "UUID1")
        #self.assertEqual(result, False)
        #self.deleteUser = "UUID1"
        pass

    def test233importMembersToGroup(self):
        # FIXME: Need a test on the group before accessing to attributes
        #result = self.client.importmembers_to_group(1337, "Inventory/Date", "2010-04-29")
        #self.assertEqual(result, False)
        #self.deleteUser = "UUID1"
        pass

    def test234shareWith(self):
        # FIXME: Need a test on the group before accessing to attributes
        #result = self.client.share_with(1337)
        #self.assertEqual(result, [])
        #self.deleteUser = "UUID1"
        pass

    def test235addShare(self):
        # FIXME: Need a test on the group before access to attributes
        #result = self.client.add_share(1337, [("login", "t"),])
        #self.assertEqual(result, False)
        #self.deleteUser = "UUID1"
        #self.deleteShare = [result, [("login", "t"),]]
        pass

    def test236delShare(self):
        # FIXME: Need a test on the group before access to attributes
        #result = self.client.del_share(1337, [("login", "t"),])
        #self.assertEqual(result, True)
        pass

    def test237canEdit(self):
        # FIXME: Need a test on the group before access to attributes
        #result = self.client.can_edit(1337)
        #self.assertEqual(result, False)
        pass

    def test238getQueryPossibilities(self):
        # FIXME : Can't get the response due to a serialization error
        #result = self.client.getQueryPossibilities()
        #self.assertEqual(result, {})
        pass

    def test239getPossiblesModules(self):
        result = self.client.getPossiblesModules()
        self.assertEqual(result, ['inventory', 'dyngroup'])

    def test240getPossiblesCriterionsInMainModule(self):
        result = self.client.getPossiblesCriterionsInMainModule()
        self.assertEqual(result, ['Entity/Label', 'Software/ProductName', 'Hardware/OperatingSystem', 'Registry/Value/display name', 'Drive/TotalSpace', 'Hardware/ProcessorType', 'Software/Products'])

    def test241getPossiblesCriterionInModule(self):
        result = self.client.getPossiblesCriterionsInModule('inventory')
        self.assertEqual(result, ['Entity/Label', 'Software/ProductName', 'Hardware/OperatingSystem', 'Registry/Value/display name', 'Drive/TotalSpace', 'Hardware/ProcessorType', 'Software/Products'])

    def test242getTypeForCriterionInModule(self):
        result = self.client.getTypeForCriterionInModule("inventory", "Software/ProductName")
        self.assertEqual(result, "list")

    def test243getPossiblesValuesForCriterionInModule(self):
        result = self.client.getPossiblesValuesForCriterionInModule("inventory", "Software/ProductName")
        self.assertEqual(result, ['list', []])

    def test244getPossiblesValuesForCriterionInModuleFuzzy(self):
        result = self.client.getPossiblesValuesForCriterionInModuleFuzzy("inventory", "Software/ProductName")
        self.assertEqual(result, [])

    def test245getPossiblesValuesForCriterionInModuleFuzzyWhere(self):
        # FIXME: What is the last parameter ??
        #result = self.client.getPossiblesValuesForCriterionInModuleFuzzyWhere("inventory", "Software/ProductName", "blabla")
        #self.assertEqual(result, [])
        pass

    def test246checkBoolean(self):
        result = self.client.checkBoolean('')
        self.assertEqual(result, [True, -1])

    def test247updateMachineCache(self):
        result = self.client.update_machine_cache()
        self.assertEqual(result, 0)

    def test248setProfileImagingServer(self):
        result = self.client.set_profile_imaging_server(1337, 1338)
        self.assertEqual(result, False)

    def test249getProfileImagingServer(self):
        result = self.client.get_profile_imaging_server(1337)
        self.assertEqual(result, False)

    def test250setProfileEntity(self):
        result = self.client.set_profile_entity(1337, 42)
        self.assertEqual(result, False)

    def test251getProfileEntity(self):
        result = self.client.get_profile_entity(1337)
        self.assertEqual(result, False)

    def test252isProfileAssociatedToImagingServer(self):
        result = self.client.isProfileAssociatedToImagingServer(1337)
        self.assertEqual(result, False)

    def test255forgeRequest(self):
        result = self.client.forgeRequest("Drive/TotalSpace", ["1337", "42"])
        self.assertEqual( result, ['1==inventory::Drive/TotalSpace==1337||2==inventory::Drive/TotalSpace==42', 'OR(1,2)', {'criterion':'Drive/TotalSpace', 'data':['1337', '42']}])

    def disabled_test211createProfile(self):
        # This method is placed here not to influence the behavior of the tests (there is not yet method to delete a profile)
        result = self.client.create_profile("Profile", 0)
        self.assertEqual(type(result), str)
        # TODO : Delete this new profile in tearDown() (the deleting method is not yet implemented in the dyngroup plugin)
        self.deleteProfile = result

"""
Launch of the tests
"""

if mode == "debug":
    nb = 0
    success = []
    suite=unittest.TestLoader().loadTestsFromTestCase(class01dyngroupInitTest)
    test=unittest.TextTestRunner(verbosity=Verbosity).run(suite)
    success.append(test.wasSuccessful())
    nb=nb+test.testsRun

    if False in success:
        print "One or more tests failed or have an unexpected error"
    else:
        print "All function work"
else:
    unittest.main()

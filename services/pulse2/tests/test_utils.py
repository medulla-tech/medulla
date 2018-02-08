# -*- coding: utf-8; -*-
#
# (c) 2007-2010 Mandriva, http://www.mandriva.com/
#
# $Id$
#
# This file is part of Pulse 2, http://pulse2.mandriva.org
#
# Pulse 2 is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Pulse 2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pulse 2.  If not, see <http://www.gnu.org/licenses/>.


"""
Tests for pulse2.utils
"""

# -*- coding: utf-8; -*-
#
# (c) 2016 Siveo, http://www.siveo.net/
#
# $Id$
#
# This file is part of Pulse 2.
#
# Pulse 2 is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Pulse 2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pulse 2.  If not, see <http://www.gnu.org/licenses/>.

# This file make unit tests for the content of pulse2/utils.py

import pulse2.utils
from datetime import datetime, date
import pytest
import ConfigParser

#Imports for unitest
import unittest
from pulse2.utils import isMACAddress, isUUID, splitComputerPath

###
#
# pytest
#
###
def test_singleton():
    """Tests the Singleton object in pulse2/utils.py
    Test 1"""

    class UniqueSingleton(pulse2.utils.Singleton):
        """Object for simulate Singleton"""

    def __init__(self, value):
        self.attribute = value

    a = UniqueSingleton(4)
    b = UniqueSingleton(5)
    assert a == b


def test_singleton_n():
    """Tests the SingletonN object in pulse2/utils.py
Test 2"""

    class UniqueSingletonN(object):
        """Object for simulate SingletonN"""
        __metaclass__ = pulse2.utils.SingletonN

        def __init__(self, value):
            self.attribute = value

    a = UniqueSingletonN(4)
    b = UniqueSingletonN(5)
    assert a == b


class TestPulse2ConfigParser(object):
    """Tests the Pulse2ConfigParser object"""

    a = pulse2.utils.Pulse2ConfigParser()

    def test_getpassword_without_parameters(self):
        """Test the method getpassword witheout conf file and without any parameter
        Test 3"""
        with pytest.raises(TypeError):
            # the result is an error
            self.a.getpassword()

    def test_getpassword_with_wrong_parameters(self):
        """Test the method getpassword with conf file loaded and wrong parameters
        Test 4"""
        self.a.read("config.ini")
        with pytest.raises(ConfigParser.NoSectionError):
            # the result is an error
            self.a.getpassword("AAA","bbb")

    def test_getpassword_with_partial_parameters(self):
        """Test the method getpassword with conf file loaded and partial wrong parameters
        Test 5"""
        self.a.read("config.ini")
        with pytest.raises(ConfigParser.NoOptionError):
            # the result is an error
            self.a.getpassword("SECTION_A","bbb")

    def test_getpassword_with_parameters(self):
        """Test the method getpassword with conf file loaded and good parameters
        Test 6"""
        # the file config.ini is in the same directory as this test file
        self.a.read("config.ini")
        assert self.a.getpassword("SECTION_A","my_key1") == "my_value1"

    def test_decode_from_getpassword(self):
        """Test if the method getpassword decode a base64 value
        Test 7"""
        self.a.read("config.ini")
        assert self.a.getpassword("SECTION_A","my_key2") == "Siv30"


class TestXmlrpcCleanup(object):
    """This object tests the function xmlrpcCleanup(data)"""

    class MyClass(object):
        def __init__(self):
            self.my_attribut = 4

    # Simple datas type
    def test_with_date(self):
        """Test xmlrpcCleanup with date
        Test 8"""
        the_date = date(2018,02,05)
        assert pulse2.utils.xmlrpcCleanup(the_date) == tuple(the_date.timetuple())

    def test_with_datetime(self):
        """Test xmlrpcCleanup with datetime
        Test 9"""
        the_date = datetime(2018,02,3)
        assert pulse2.utils.xmlrpcCleanup(the_date) == tuple(the_date.timetuple())

    def test_with_string(self):
        """Test xmlrpcCleanup with string
        Test 10"""
        assert pulse2.utils.xmlrpcCleanup("default") == "default"

    def test_with_int(self):
        """Test xmlrpcCleanup with int
        Test 11"""
        assert pulse2.utils.xmlrpcCleanup(3) == 3

    def test_with_none_value(self):
        """Test xmlrpcCleanup with None value
        Test 12"""
        assert pulse2.utils.xmlrpcCleanup(None) == False

    def test_with_object(self):
        """Test xmlrpcCleanup with custom object
        Test 13"""
        my_object = self.MyClass()
        assert pulse2.utils.xmlrpcCleanup(my_object) == my_object

    def test_with_long(self):
        """Test xmlrpcCleanup with long
        Test 14"""
        assert pulse2.utils.xmlrpcCleanup(long(3)) == "3"

    # Composed datas type
    def test_with_tuple(self):
        """Test xmlrpcCleanup with tuple
        Test 15"""
        the_date = datetime(2018,02,3)
        assert pulse2.utils.xmlrpcCleanup((1,long(2),"3",the_date, None)) == [1,"2","3",tuple(the_date.timetuple()), False]

    def test_with_list(self):
        """Test xmlrpcCleanup with list
        Test 16"""
        the_date = datetime(2018,02,3)
        assert pulse2.utils.xmlrpcCleanup([1,long(2),"3",[the_date, None]]) == [1,"2","3",[tuple(the_date.timetuple()), False]]

    def test_with_dict(self):
        """Test xmlrpcCleanup with dict
        Test 17"""
        the_dict = {'a': 4, 1: 'value', 'key': None}
        assert pulse2.utils.xmlrpcCleanup(the_dict) == {'a': 4, '1': 'value', 'key': False}

    def test_without_parameters(self):
        """Test xmlrpcCleanup without parameters
        Test 18"""
        with pytest.raises(TypeError):
            pulse2.utils.xmlrpcCleanup()


class TestUnique(object):
    """This object tests the function unique"""

    def test_with_list(self):
        """Test with mixed list
        Test 19"""
        # Test the function unique()
        assert pulse2.utils.unique(["c",["a","b"],(0,0), [2,3],["a","b"],"c",1,1,[2,3], (0,0)]) == [1, [2, 3], ['a', 'b'], 'c', (0,0)]

    def test_with_string(self):
        """Test with string
        Test 20"""
        assert pulse2.utils.unique("test") == ['s','e','t']

    def test_with_int(self):
        """Test with int
        Test 21"""
        with pytest.raises(TypeError):
            pulse2.utils.unique(2)

    def test_with_dict(self):
        """Test with dict
        Test 22"""
        assert pulse2.utils.unique({"c":["a","b"],'b':(0,0),'c':4}) == ['c', 'b']

    def test_without_parameters(self):
        """Test without parameters
        Test 23"""
        # Test the function unique()
        with pytest.raises(TypeError):
            pulse2.utils.unique()


class TestSameNetwork(object):
    """This object tests the function same_network"""

    def test_with_wrong_string(self):
        """The ip and mask are random string
        Test 24"""
        ip1 = "wrong ip1"
        ip2 = "wrong ip2"
        mask = "wrong mask"
        assert pulse2.utils.same_network(ip1,ip2,mask) == False

    def test_with_right_string_same_network(self):
        """The ips and mask are good
        Test 25"""
        ip1 = "192.168.1.101"
        ip2 = "192.168.1.140"
        mask = "255.255.255.0"
        assert pulse2.utils.same_network(ip1,ip2,mask) == True

    def test_with_right_string_different_network(self):
        """The ips and mask are in differents network
        Test 26"""
        ip1 = "192.168.1.101"
        ip2 = "82.190.34.140"
        mask = "255.255.255.0"
        assert pulse2.utils.same_network(ip1,ip2,mask) == False

    def test_with_int(self):
        """The ips and mask are int
        Test 27"""
        ip1 = 14
        ip2 = 314
        mask = 4
        with pytest.raises(AttributeError):
            # Generate an error
            pulse2.utils.same_network(ip1,ip2,mask)

    def test_without_parameters(self):
        """The parameters are not given
        Test 28"""
        with pytest.raises(TypeError):
            # Generate an error
            pulse2.utils.same_network()

    def test_with_none(self):
        """The parameters are None
        Test 29"""
        ip1 = None
        ip2 = None
        mask = None
        with pytest.raises(AttributeError):
            # Generate an error
            pulse2.utils.same_network(ip1,ip2,mask)


class TestOnlyAddNew(object):
    """This class tests the onlyAddNew function"""

    def test_without_parameters(self):
        """The parameters are not given
        Test 30"""
        with pytest.raises(TypeError):
            pulse2.utils.onlyAddNew()

    def test_with_none(self):
        """The parameters are set to None (unexpected parameters)
        Test 31"""
        obj = None
        value = None
        with pytest.raises(AttributeError):
            pulse2.utils.onlyAddNew(obj,value)

    def test_unique_value_not_in_obj(self):
        """The function is tested with unique value not declared in obj
        Test 32"""
        obj = []
        value = 4
        assert pulse2.utils.onlyAddNew(obj, value) == [4]

    def test_unique_value_in_obj(self):
        """The function is tested with unique value declared in obj
        Test 33"""
        obj = [4]
        value = 4
        assert pulse2.utils.onlyAddNew(obj, value) == [4]

    def test_list_not_in_obj(self):
        """The function is tested with unique value declared in obj
        Test 34"""
        obj = [4]
        value = [1,2,3,4,5,5,6,7]
        assert pulse2.utils.onlyAddNew(obj, value) == [4,1,2,3,5,6,7]


class TestGetConfigFile(object):
    """This class tests the getConfigFile function"""

    def test_without_parameters_and_default_path(self):
        """Test the function without parameters
        Test 35"""
        with pytest.raises(TypeError):
            pulse2.utils.getConfigFile()

    def test_with_none_and_default_path(self):
        """Test the function with none value instead of module name (unexpected value)
        Test 36"""
        with pytest.raises(AttributeError):
            pulse2.utils.getConfigFile(None)

    def test_with_int_and_default_path(self):
        """Test the function with int value instead of module name
        Test 37"""
        with pytest.raises(AttributeError):
            pulse2.utils.getConfigFile(None)

    def test_with_string_and_default_path(self):
        """Test the function with string for the module name
        Test 38"""
        assert pulse2.utils.getConfigFile("my_module") == "/etc/mmc/plugins/my_module.ini"

    def test_with_string_and_string_path(self):
        """Test the function with another path
        Test 39"""
        assert pulse2.utils.getConfigFile("my_module", "my/new/path/") == "my/new/path/my_module.ini"

    def test_with_string_and_int_path(self):
        """Test the function with another path
        Test 40"""
        with pytest.raises(AttributeError):
            pulse2.utils.getConfigFile("my_module", 4)

    def test_with_string_and_none_path(self):
        """Test the function with another path
        Test 41"""
        with pytest.raises(AttributeError):
            pulse2.utils.getConfigFile("my_module", None)

    def test_with_string_and_empty_string_in_path(self):
        """Test the function with another path
        Test 42"""
        assert pulse2.utils.getConfigFile("my_module", "") == "my_module.ini"


class TestIsdigit(object):
    """This class tests the isdigit function"""

    def test_without_parameters(self):
        """Test the function isdigit without parameters
        Test 43"""
        with pytest.raises(TypeError):
            pulse2.utils.isdigit()

    def test_with_none(self):
        """Test the function isdigit with none parameter
        Test 44"""
        assert pulse2.utils.isdigit(None) == False

    def test_with_string(self):
        """Test the function isdigit with string parameter
        Test 45"""
        assert pulse2.utils.isdigit("the value") == False

    def test_with_int(self):
        """Test the function isdigit with int parameter
        Test 46"""
        assert pulse2.utils.isdigit(-3543) == True

    def test_with_long(self):
        """Test the function isdigit with int parameter
        Test 47"""
        assert pulse2.utils.isdigit(long(-3543)) == True

    def test_with_float(self):
        """Test the function isdigit with float parameter
        Test 48"""
        assert pulse2.utils.isdigit(3.14) == False

    def test_with_int_in_string(self):
        """Test the function isdigit with int in string. The function should eval it
        Test 49"""
        assert pulse2.utils.isdigit("4") == True


class TestGrep(object):
    """This class tests the grep function"""

    def test_without_parameters(self):
        """Test the function without parameters
        Test 50"""
        with pytest.raises(TypeError):
            pulse2.utils.grep()

    def test_with_string_as_none(self):
        """Test the function with the criterion set to None
        Test 51"""
        with pytest.raises(TypeError):
            pulse2.utils.grep(None, [])

    def test_with_string_as_int(self):
        """Test the function. The string parameter is set with int
        Test 52"""
        with pytest.raises(TypeError):
            pulse2.utils.grep(5,[])

    def test_with_string(self):
        """Test the function with string for string parameter
        Test 53"""
        assert pulse2.utils.grep("the_string",[]) == []

    def test_with_list_as_string(self):
        """Test the function. The list parameter is set with string
        Test 54"""
        assert pulse2.utils.grep("string","reference string") == ""

    def test_the_result_of_research(self):
        """Test if the returned result is correct
        Test 55"""
        assert pulse2.utils.grep("is", ["this", 'string','is','relatively','long','to','test','the','result']) == ['this','is']

    def test_with_list_as_int(self):
        """Test the function with int instead of the list
        Test 56"""
        with pytest.raises(TypeError):
            pulse2.utils.grep("", 5)


class TestGrepv(object):
    """This class tests the grepv function"""

    def test_without_parameters(self):
        """Tests the function without parameters
        Test57"""
        with pytest.raises(TypeError):
            pulse2.utils.grepv()

    def test_with_unexpected_parameters(self):
        """Tests the function without parameters
        Test58"""
        with pytest.raises(TypeError):
            pulse2.utils.grepv(1, 3)
            pulse2.utils.grepv(1, [1, 2, 3])
            pulse2.utils.grepv("Test", [1, 2, 3])

    def test_with_expected_parameters(self):
        """Tests the function without parameters
        Test59"""
        assert pulse2.utils.grepv("1", ["1", "2", "3"]) == ["2", "3"]

        # Test 60
        assert pulse2.utils.grepv("a", "arbre") == ["r", 'b', 'r', 'e']



###
#
# Unitest
#
###

class InputTests(unittest.TestCase):

    def test_MACValid(self):
        self.assertTrue(isMACAddress('00:11:aa:BB:22:33'))
        self.assertTrue(isMACAddress(u'00:11:aa:BB:22:33'))

    def test_MACNotValid(self):
        self.assertFalse(isMACAddress('00:11:aa:BB:22:zz'))
        self.assertFalse(isMACAddress('00:11:aa:BB:22:33:00'))

    def test_UUIDValid(self):
        self.assertTrue(isUUID('UUID1'))
        self.assertTrue(isUUID(u'UUID1'))
        self.assertTrue(isUUID('1a10b1f4-bb6e-4798-b39e-bb8d090dd8b6'))

    def test_UUIDNotValid(self):
        self.assertFalse(isUUID('UUID0'))
        self.assertFalse(isUUID('UUID-10'))
        self.assertFalse(isUUID(''))
        self.assertFalse(isUUID('1a10b1f4-bb6e-4798-b39e-bb8d090dd8b'))
        self.assertFalse(isUUID(42))

    def test_computerPathValid(self):
        self.assertEqual(splitComputerPath('hostname'), ('', '', 'hostname', ''))
        self.assertEqual(splitComputerPath(u'123456'), ('', '', '123456', ''))
        self.assertEqual(splitComputerPath('hostname.domain-example.net'), ('', '', 'hostname', 'domain-example.net'))
        self.assertEqual(splitComputerPath('profile:hostname'), ('profile', '', 'hostname', ''))
        self.assertEqual(splitComputerPath('profile:/hostname'), ('profile', '', 'hostname', ''))
        self.assertEqual(splitComputerPath('/root/sub1/sub2/hostname'), ('', '/root/sub1/sub2', 'hostname', ''))
        self.assertEqual(splitComputerPath('profile:/root/sub1/sub2/hostname'), ('profile', '/root/sub1/sub2', 'hostname', ''))
        self.assertRaises(TypeError, splitComputerPath, 'profile:root/sub1/sub2/hostname')
        self.assertRaises(TypeError, splitComputerPath, 'profile:')

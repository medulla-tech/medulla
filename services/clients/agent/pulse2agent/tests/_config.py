# -*- coding: utf-8; -*-
#
# (c) 2014 Mandriva, http://www.mandriva.com/
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
# along with Pulse 2; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

""" Tests the basic frame for one-level structured configs """

import os
import tempfile
try:
    from twisted.trial.unittest import TestCase
except ImportError:
    from unittest import TestCase, main # pyflakes.ignore

from pulse2agent._config import ExtendedConfigParser, ConfigReader
from pulse2agent._config import InvalidSection, DefaultsNotFound



class Test00_ExtendedConfigParser(TestCase):

    def test00_unicode(self):
        """ Several unicode options test """

        unicode_fr = "Dès Noël où un zéphyr haï me vêt de glaçons würmiens je dîne d’exquis rôtis de bœuf au kir à l’aÿ d’âge mûr & cætera"
        unicode_de = "Zwölf große Boxkämpfer jagen Viktor quer über den Sylter Deich"
        unicode_cz = "Příliš žluťoučký kůň úpěl ďábelské kódy"
        unicode_ru = "Даждъ намъ дънесь"

        body = "[main]\nunicode_fr = %s\nunicode_de = %s\nunicode_cz = %s\nunicode_ru = %s"
        content = body % (unicode_fr, unicode_de, unicode_cz ,unicode_ru)


        t_file = tempfile.NamedTemporaryFile(mode="w", delete=False)
        t_file.write(content)
        t_file.close()

        config = ExtendedConfigParser()
        config.read(t_file.name)

        self.assertEqual(unicode_fr, config.get("main", "unicode_fr"))
        self.assertEqual(unicode_de, config.get("main", "unicode_de"))
        self.assertEqual(unicode_cz, config.get("main", "unicode_cz"))
        self.assertEqual(unicode_ru, config.get("main", "unicode_ru"))

        os.unlink(t_file.name)

    def test01_lists(self):
        """ Reading of lists with several elements """

        list1 = ["first_element", 8, False, 0.21444]
        list2 = ["12.52.12.1", 4144]

        def repr_list(values):
            """
            Returns a string representation of list.

            String values are stripped and all commas are removed.

            @param values: list to convert
            @type values: list or tuple

            @return: list formatted as string
            @rtype: str
            """
            return ", ".join([str(v).replace("'","").replace('"','').strip() for v in values])

        body = "[main]\nlist1 = %s\nlist2 = %s"
        content = body % (repr_list(list1), repr_list(list2))

        t_file = tempfile.NamedTemporaryFile(mode="w", delete=False)
        t_file.write(content)
        t_file.close()

        config = ExtendedConfigParser()
        config.read(t_file.name)

        self.assertEqual(list1, config.getlist("main", "list1"))
        self.assertEqual(list2, config.getlist("main", "list2"))

        os.unlink(t_file.name)

class Test01_ConfigReader(TestCase):

    def setUp(self):
        class MyTestConfig(object):
            __metaclass__ = ConfigReader

            class main(object):
                option_str = "a string value"
                option_int = 215
                option_float = 32.217
                option_bool = False
                option_list = ["toto", True, 635, 1247.4741111]

            class database(object):
                name = "mydb"
                host = "52.124.21.95"
                port = 3306
                user = "root"
                password = "password"
                timeout = 30

        self.config = MyTestConfig()



    def test00_options_list(self):
        """ Test of presence of all options """
        options = {}
        options["main"] = ["option_str",
                           "option_int",
                           "option_float",
                           "option_bool",
                           "option_list"]
        options["database"] = ["name",
                               "host",
                               "port",
                               "user",
                               "password",
                               "timeout",
                               ]

        for section_name in options:
            section = getattr(self.config, section_name)
            for name, value in self.config.options(section):
                self.assertIn(name, options[section_name])


    def test01_override(self):
        """Test of overriding by config file """
        main_option_int = 60
        database_name = "anotherdb"
        body = "[main]\noption_int = %s\n[database]\nname = %s"
        content = body % (main_option_int, database_name)

        t_file = tempfile.NamedTemporaryFile(mode="w", delete=False)
        t_file.write(content)
        t_file.close()

        self.config.read(t_file.name)

        self.assertEqual(main_option_int, self.config.main.option_int)
        self.assertEqual(database_name, self.config.database.name)

        os.unlink(t_file.name)


    def test02_add_not_existing_section(self):
        """ File contains undeclared section """
        body = "[another_section]\noption1 = any string"

        t_file = tempfile.NamedTemporaryFile(mode="w", delete=False)
        t_file.write(body)
        t_file.close()

        self.assertRaises(DefaultsNotFound, self.config.read, t_file.name)

        os.unlink(t_file.name)


    def test03_bad_section_declare(self):
        """
        Declaration of defaults contains a bad-type section.
        In other words, the declaration of defaults can't contain
        another attribute than nested class which is considered
        as a section.
        """
        # just a simple content to have a config file as attribute
        body = "[main]\noption_int = 1"

        # retype nested class to str
        self.config.main = ""

        t_file = tempfile.NamedTemporaryFile(mode="w", delete=False)
        t_file.write(body)
        t_file.close()

        # declaration contains an invalid section
        self.assertRaises(InvalidSection, self.config.read, t_file.name)

        os.unlink(t_file.name)


if __name__ == '__main__':

    if TestCase.__module__ != "twisted.trial.unittest" :
        main()





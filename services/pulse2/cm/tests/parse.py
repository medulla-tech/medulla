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

from twisted.trial.unittest import TestCase

from pulse2.cm.parse import Parser


class Test00_Parser(TestCase):

    def test00_assign_invalid_parser_type(self):
        "try to assign invalid serializer type"

        parser = Parser()
        self.assertRaises(TypeError, parser._set_backend, "toto")

    def test01_encode_decode_json(self):
        """ test with json serializer """
        parser = Parser("json")
        pack = parser.encode("hello")
        self.assertEqual(parser.decode(pack), "hello")


    def test02_encode_decode_pickle(self):
        """ test with pickle serializer """

        parser = Parser("pickle")
        pack = parser.encode("hello")
        self.assertEqual(parser.decode(pack), "hello")

    def test03_encode_decode_marshal(self):
        """ test with pickle serializer """

        parser = Parser("marshal")
        pack = parser.encode("hello")
        self.assertEqual(parser.decode(pack), "hello")


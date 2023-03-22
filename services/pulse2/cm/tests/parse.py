# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2014 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

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

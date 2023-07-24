# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2014 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

"""try:
    from twisted.trial.unittest import TestCase1
except ImportError:
    from unittest import TestCase, main"""
from unittest import TestCase, main


from pulse2agent.types import Component, ComponentUntitled, DispatcherFrame


class Test01_DispatecherFrame(TestCase):
    def test00_add_component(self):
        class FooComponent(Component):
            __component_name__ = "foo"

        class MyDispatcher(DispatcherFrame):
            components = [
                FooComponent,
            ]

        config = object()

        md = MyDispatcher(config)

        self.assertIn("foo", md.__dict__)
        self.assertIsInstance(md.foo, Component)
        self.assertIsInstance(md.foo.parent, DispatcherFrame)

    def test01_add_non_component(self):
        class FooComponent(object):
            __component_name__ = "foo"

        class MyDispatcher(DispatcherFrame):
            components = [
                FooComponent,
            ]

        config = object()

        self.assertRaises(TypeError, MyDispatcher, config)

    def test02_add_untitled_component(self):
        class FooComponent(Component):
            pass

        class MyDispatcher(DispatcherFrame):
            components = [
                FooComponent,
            ]

        config = object()

        self.assertRaises(ComponentUntitled, MyDispatcher, config)


if __name__ == "__main__":
    if TestCase.__module__ != "twisted.trial.unittest":
        main()

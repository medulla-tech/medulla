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
            components = [FooComponent,]

        config = object()

        md = MyDispatcher(config)

        self.assertIn("foo", md.__dict__)
        self.assertIsInstance(md.foo, Component)
        self.assertIsInstance(md.foo.parent, DispatcherFrame)


    def test01_add_non_component(self):

        class FooComponent(object):
            __component_name__ = "foo"

        class MyDispatcher(DispatcherFrame):
            components = [FooComponent,]

        config = object()

        self.assertRaises(TypeError, MyDispatcher,config)

    def test02_add_untitled_component(self):

        class FooComponent(Component):
            pass

        class MyDispatcher(DispatcherFrame):
            components = [FooComponent,]

        config = object()

        self.assertRaises(ComponentUntitled, MyDispatcher, config)



if __name__ == '__main__':

    if TestCase.__module__ != "twisted.trial.unittest" :
        main()

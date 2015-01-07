# -*- test-case-name: pulse2.msc.client.tests.types -*-
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


import logging

def enum(*args, **kwargs):
    """
    Returns a named enumerator based on simple list of integers.

    @param *args: list of names of constants to create
    @type *args: list
    """
    return type('Enum',
                (),
                dict((y, x) for x, y in enumerate(args), **kwargs)
                )


REQUESTS = enum("CHECK",
                "GET_SOFTWARE",
                "SEND_INVENTORY",
                )



class ConnectionCodes(object):
    """ A simple common container of state consts """

    DIRECT  = 0x00
    VPN     = 0x10

    DONE    = 0x01
    REFUSED = 0x02
    TIMEOUT = 0x04
    FAILED  = 0x08

CC = ConnectionCodes()

class ComponentError(Exception):
    def __init__(self, name):
        self.name = name


class ComponentInitError(ComponentError):

    def __repr__(self):
        return "Initialisation of component %s failed" % repr(self.name)

class ComponentAlreadyInitialized(ComponentError):

    def __repr__(self):
        return "Component %s already initialized" % repr(self.name)

class ComponentUntitled(ComponentError):

    def __repr__(self):
        return "Untitled component %s" % repr(self.name)


class Component(object):
    """  """

    __component_name__ = None
    _parent = None

    config = None
    logger = None
    queues = None

    def __init__(self, **kwargs):

        if self.__component_name__ is None:
            raise ComponentUntitled(self)

        for name, value in kwargs.iteritems():
            if hasattr(self, name):
                setattr(self, name, value)
            else:
                raise AttributeError("Attribute %s isn't declared as attribute of component" % name)


    def __repr__(self):
        return "Component object '%s' on %s" % (repr(self.__component_name__), id(self))

    @property
    def parent(self):
        """Returns an instance of dispatcher"""
        return self._parent


    @parent.setter # pyflakes.ignore
    def parent(self, value):
        if not isinstance(value, DispatcherFrame):
            raise TypeError("Parent value must be DispatcherFrame type")
        self._parent = value




class DispatcherFrame(object):
    """
    A root object allowing to pass shared objects to all included components.

    This construction avoids the cyclic declarations during its init etap,
    where all components are the same constructor and passed parameters
    must be accessibles for each them.

    Shared objects must be 'declared' (i.e. attribute = None)
    on both sides (Dispatcher and Component).

    The attribute components declares all components to include.
    """

    config = None
    logger = None
    queues = None

    components = []
    _component_kwargs = {}

    def __init__(self, config):
        self.logger = logging.getLogger()
        self.config = config

        self._set_component_kwargs()
        self._add_components()

    def _get_cmpt_attribute_names(self):
        """ Returns the attributes only 'declared' on 1st level """
        for name, attribute in self.__class__.__bases__[0].__dict__.iteritems():
            if not name.startswith("_") and not callable(attribute):
                if name != "components":
                    yield name


    def _set_component_kwargs(self):
        for name in self._get_cmpt_attribute_names():
            self._component_kwargs[name] = getattr(self, name)



    def _add_components(self):
        for component in self.components:

            if not issubclass(component, Component):
                raise TypeError("Class %s is must inherit from Component type")

            cmpt_instance = component(**self._component_kwargs)
            cmpt_instance.parent = self

            if not cmpt_instance.__component_name__ in self.__dict__:
                setattr(self,
                        cmpt_instance.__component_name__,
                        cmpt_instance
                        )


__all__ = ["CC",]

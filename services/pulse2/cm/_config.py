# -*- test-case-name: pulse2.msc.client.tests._config -*-
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

""" Declaration of config defaults """

import os
import inspect
from ConfigParser import RawConfigParser


class ConfigError(Exception):
    """ A base frame for related exceptions """

    def __init__(self, name):
        """
        @param name: name of entity
        @type name: str
        """
        self.name = name


class InvalidSection(ConfigError):
    """Raised when called section is not declared correctly"""

    def __repr__(self):
        return "Section <%s> must be declared as nested class" % self.name


class DefaultsNotFound(ConfigError):
    """ Raised when section declared in config file not found in defaults"""

    def __repr__(self):
        return "Section <%s> not found in defaults" % self.name


class ExtendedConfigParser(RawConfigParser):
    """Extended for processing list options having heterogenuous content"""


    def getlist(self, section, option):
        """
        Transforms string containing a list to true list datatype.

        This method has a same behavior as others like, getint, getbool, etc.
        The content of declared list may contain several base datatypes like
        str, bool, int, float. When detection fails, element will be converted
        to str.

        @param section: name of section
        @type section: str

        @param option: name of option
        @type option: str

        @return: list of detected values
        @rtype: list
        """
        raw = self.get(section, option)
        ret = []

        # try to check and convert type of all elements
        for s in raw.split(","):
            element = s.strip()
            if element.lower() == "true":
                ret.append(True)
                continue
            elif element.lower() == "false":
                ret.append(False)
                continue

            float_value = None
            try:
                float_value = float(element)
            except ValueError:
                 # float conversion failed - element typed as str
                ret.append(element)
                continue
            try:
                int_value = int(element)
            except ValueError:
                if float_value is None:
                    ret.append(element)
                    continue

            # because int value can be converted to float too,
            # comapring of both values resolves a final datatype
            # i.e.:
            # int("754") == float("754")
            # int("124.251") != float("124.251")
            if int_value == float_value:
                ret.append(int_value)
            else:
                ret.append(float_value)

        return ret



class ConfigReader(type):
    """
    Provides a redable declaration of defaults for ConfigParser instances.

    The style of declarations are realized as a root class
    containing nested classes which will be detected as option containers.
    Name of nested class is considered as name of section and its attributtes
    defines the options as defaults.
    Method read() loads a config file with ConfigParser syntax and overrides
    the values of options.

    All options will be finally accessible hierarchically, like this:

    >>> config.section.option

    Some rules for a final declaration:
    - Root frame of must declare this frame as metaclass
    - Each section must be declared as nested class of root
    - Nested class inherits from object
    - Assigning of attributte defines its datatype

    Example :
    ---------
    >>> class Config(object):
    >>>    __metaclass__ = ConfigReader
    >>>
    >>>    class database(type):
    >>>        host = "localhost"
    >>>        port = 3306
    >>>
    >>> config = Config()
    >>> config.database.port
    3306
    >>>
    """

    def __new__(cls, name, bases, attrs):
        """
        A metaclass stuff to implement.

        @param name: name of new instance
        @type name: str

        @param bases: types to inherit
        @type bases: tuple

        @param attrs: dictionnary of attributtes
        @type attrs: dict
        """
        att_dict = dict((k, v) for (k, v) in cls.__dict__.items()
                if not k.startswith("__"))

        attrs.update(att_dict)

        return type.__new__(cls, name, bases, attrs)


    def read(self, filename):
        """
        Reads the content of config file and overrides the defaults.

        @param filename: path to config file
        @type filename: str
        """

        config_file = ExtendedConfigParser()
        config_file.read(filename)
        filename_local = "%s.local" % filename
        if os.path.exists(filename_local):
            config_file.read(filename_local)


        for section_name in config_file.sections():
            if hasattr(self, section_name):
                section = getattr(self, section_name)
                if inspect.isclass(section):

                    setattr(section, "__name__", section_name)
                    self._update_options(config_file, section)

                else:
                    raise InvalidSection(section_name)
            else:
                raise DefaultsNotFound(section_name)


    @classmethod
    def options(self, section):
        """
        Returns a list of options.

        @param section: section class-like container
        @type section: class

        @return: all options found in section
        @rtype: generator
        """
        for name, value in section.__dict__.items():
            if not name.startswith("_"):

                yield name, value


    @classmethod
    def cast_relations(self, parser):
        """
        Allowed convert methods.

        @param parser: config instance
        @type parser: ConfigParser

        @return: datatype bases and related converting method
        @rtype: generator
        """
        for base, method in [(bool, parser.getboolean),
                             (int, parser.getint),
                             (float, parser.getfloat),
                             (str, parser.get),
                             (unicode, parser.get),
                             (list, parser.getlist),
                             ]:
            yield base, method



    def _update_options(self, config_file, section):
        """
        Overrides default values of options by options from config file.

        @param config_file: instance of parser
        @type config_file: ConfigParser

        @param section: section class-like container
        @type section: class
        """
        for name, value in self.options(section):
            if config_file.has_option(section.__name__, name):
                for base, method in self.cast_relations(config_file):

                    try:
                        if isinstance(value, base):
                            new_value = method(section.__name__, name)
                            setattr(section, name, new_value)
                            break
                        elif value is None:
                            new_value = config_file.get(section.__name__, name)
                            setattr(section, name, new_value)
                    except TypeError, e:
                        print e
                else:
                    # defalt value stays unchanged
                    pass
        setattr(self, section.__name__, section)


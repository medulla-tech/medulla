#!/usr/bin/env python2.7
# -*- coding: utf-8; -*-
#
# (c) 2018 siveo, http://www.siveo.net
#
# This file is part of Pulse 2, http://www.siveo.net
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

from mmc.support.config import PluginConfig, PluginConfigFactory
from mmc.plugins.base.config import BasePluginConfig

class TreeOU(object):
    """ TreeOU represents the arborescence of the founded OUs"""
    def __init__(self, name=""):
        self.name = name
        self.child = []
        self.parent = None
        self.level = 0
        self.path = []

    def search(self, string):
        """Search the element specified

        Params:
            string string represents the element we need to locate. The string is formated like this:
            string = "first/second/third/fourth"

        Returns:
            TreeOU object if the string match with any leaf of the tree
            False if the string don't match
        """

        string = string.split('/')
        temp = self

        for element in string:
            # If the element exists
            if temp.search_direct_child(element):
                # The next element is analysed
                temp = temp.search_direct_child(element)

                # If nothing is founded, temp = False and bool type for temp variable is not possible, it's due to the
                # line above. So for the first 'unmatch' element in the string, the method returns False
                if temp is False:
                    return temp
        # Finally if something match with the string, the matched object is returned.
        return temp

    def search_direct_child(self, child_name=""):
        """Search if the object has the specified child in it's direct child

        Params:
            string child_name is the name of the child we are looking for.

        Returns:
            TreeOU this is the children found.
        """
        response = False
        if len(self.child) == 0:
            return False
        else:
            for children in self.child:
                # By default response = False. If a child match with the search, response is set to the child
                if children.name == child_name:
                    response = children

            # Finally the response return the result.
            # The result can be a TreeOU object if a child is found or False if nothing is found
            return response

    def add_child(self, children):
        """
        This method add the specified children to the actual object.

        Params:
            TreeOU children
        Returns:
            Bool True if success and False if failure
        """

        # Verify if the children is a TreeOu object
        if type(children) == TreeOU:
            # Verify if the new children is not already known
            if not self.search_direct_child(children.name):
                # Verify if the children has not already a parent
                if children.parent is None:
                    # A parent is given to the children
                    children.parent = self
                    children.level = self.level + 1
                    self.child.append(children)

                    last = self.child[-1]
                    last.path = last.get_path()

                    return True
                else:
                    return False
            else:
                return False
        else:
            return False

    def create_recursively(self, string):
        """
        Create recursively the TreeOU objects as child from the specified string.

        Params:
            string this string contains the OUs name separated by /, like "my_first/my_sub/my_subsub"
        """
        string = string.split('/')
        temp = self

        for element in string:
            # If the element exists
            if temp.search_direct_child(element):
                # The next element is analysed
                temp = temp.search_direct_child(element)

            else:
                new = TreeOU(element)
                temp.add_child(new)
                temp = new

    def recursive_json(self):
        """
        Generate a dict which starts at the specified object and gives all the childrens.

        Returns:
            a dict of the tree structure.
        """

        # This is the initial structure whe want.
        self.json = {
            'name':self.name,
            'child':[],
            'path':'/'.join(self.path)
        }
        # Check if the actual node has children
        for element in self.child:
            # If it's the case each child's dict is append
            self.json['child'].append(element.recursive_json())
        return self.json

    def get_path(self):
        """
        get_path generate the "path" between the root tree and the actual node.

        Returns:
            String of the path from root tree and the pointed node.
        """
        canonical = []
        temp = self
        while temp.parent is not None:
            canonical.append(temp.name)
            temp = temp.parent

        canonical.reverse()
        return canonical

    def str_to_ou(self, ou_string):
        """
        Generate a OU string with the path of the node. For example, for the node /root/first_child/grand_son,
        it's str_to_ou() is OU=grand_son,OU=first_child,OU=root,DC=myDomain,DC=local.
        The DC datas are read from the configuration file.

        Params:
            String ou_string contains the path of the node pointed.

        Returns:
            String which contains the result (i.e.: OU=grand_son,OU=first_child,OU=root,DC=myDomain,DC=local)
            or
            returns False if the string can't be generated
        """
        config = PluginConfigFactory.new(BasePluginConfig, "base")
        if config.has_section('authentication_externalldap'):
            # Get the parameters from the config file
            suffix = config.get('authentication_externalldap', 'suffix')

            ou_list = ou_string.split('/')
            ou_list.reverse()

            ous = []
            for ou in ou_list:
                ou = 'OU='+ou
                ous.append(ou)

            ous.append(suffix)
            return ','.join(ous)

        else:
            return False

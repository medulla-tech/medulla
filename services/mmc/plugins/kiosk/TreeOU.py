#!/usr/bin/env python2.7
# -*- coding: utf-8; -*-
#
# (c) 2016 siveo, http://www.siveo.net
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

class TreeOU(object):
    """ TreeOU represente the arborescence of the founded OUs"""
    def __init__(self, name=""):
        self.name = name
        self.child = []
        self.parent = None

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
                print(element)
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
            TreeOU this is the children found."""
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

        param:
            TreeOU children
        return:
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
                    self.child.append(children)
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

        param:
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

#!/usr/bin/env python
# -*- coding: utf-8; -*-
#
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later


class TreeOU(object):
    """TreeOU represents the arborescence of the founded OUs"""

    def __init__(self, name=""):
        self.name = name
        self.child = []
        self.parent = None
        self.level = 0
        self.path = []
        # True only when the node corresponds to an OU explicitly authorized
        # for the current user. Intermediate ancestors created to materialize
        # the hierarchy stay False and are rendered as non-selectable.
        self.selectable = False

    def search(self, string):
        """Search the element specified

        Params:
            string string represents the element we need to locate. The string is formated like this:
            string = "first>>second>>third>>fourth"

        Returns:
            TreeOU object if the string match with any leaf of the tree
            False if the string don't match
        """

        string = string.split(">>")
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
        if isinstance(children, TreeOU):
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

    def create_recursively(self, string, leaf_only=False, separator=None):
        """
        Create recursively the TreeOU objects as child from the specified string.

        Params:
            string this string contains the OUs name separated by >>, like "my_first>>my_sub>>my_subsub"
            leaf_only when True, only the leaf of the path is flagged as
                selectable so intermediate ancestors created on the fly stay
                non-selectable (used for the Entity source). When False
                (default, kept for backward compat with Group/OU/LDAP sources)
                every node touched by this call is selectable.
            separator when given, the names are separated by it instead of >>
                and " > " is part of a name.
        """
        temp = self

        if separator is None:
            string = string.replace(" > ", ">>")
            separator = ">>"
        elements = string.split(separator)
        last_index = len(elements) - 1
        for idx, element in enumerate(elements):
            element = element.strip()
            if element:
                if temp.search_direct_child(element):
                    temp = temp.search_direct_child(element)
                else:
                    new = TreeOU(element)
                    temp.add_child(new)
                    temp = new
                if not leaf_only or idx == last_index:
                    temp.selectable = True

    def recursive_json(self, separator=">>"):
        """
        Generate a dict which starts at the specified object and gives all the childrens.

        Params:
            separator string joining the names of a node path.

        Returns:
            a dict of the tree structure.
        """

        # This is the initial structure whe want.
        self.json = {
            "name": self.name,
            "child": [],
            "path": separator.join(self.path),
            "selectable": self.selectable,
        }
        # Check if the actual node has children
        for element in self.child:
            # If it's the case each child's dict is append
            self.json["child"].append(element.recursive_json(separator))
        return self.json

    def get_path(self):
        """
        get_path generate the "path" between the root tree and the actual node.

        Returns:
            list of the path from root tree and the pointed node.
        """
        canonical = []
        temp = self
        while temp.parent is not None:
            canonical.append(temp.name)
            temp = temp.parent

        canonical.reverse()
        return canonical

    def recursive_paths(self, list):
        """This method returns the list of the paths for all the childrens.
        Params:
            list : reference to the final list.
        Returns:
            The list of all the childrens
        """
        for children in self.child:
            if children is not None:
                list.append(">>".join(children.get_path()))
                children.recursive_paths(list)
        return list

    def recursive_parent(self, list):
        """This method returns the list of the parents recursively.
        Params:
            list: reference to the final list.
        Returns:
            The list of all the parents in canonical format (parent1>>parent2).
        """
        if self.parent is not None:
            list.append(">>".join(self.parent.get_path()))
            self.parent.recursive_parent(list)
        return list

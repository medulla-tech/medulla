#!/usr/bin/python
# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2009 Mandriva, http://www.mandriva.com
#
# $Id$
#
# This file is part of Mandriva Management Console (MMC).
#
# MMC is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# MMC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MMC.  If not, see <http://www.gnu.org/licenses/>.

"""
Little tool to check the coverage of unit tests according to the functions
exported by a XML-RPC server.
"""

import sys
import re
from testutils import SupEspLi
source=sys.argv[1]
test=sys.argv[2]

if 'mmcagent' in test:
    function_source="def "
    function_test="result *= *self.client"
else:
    function_source="def xmlrpc"
    function_test="result *= *server"

file_source = source
file_test = test


file1=open(file_source,"r")
list_functions_source=[]
list_functions_tested=[]
list_functions_not_tested=[]
list_functions=[]

def remove_occur(li):
    """
    remove all occurence in the list give in argument
    """
    for function in li:
        if li.count(function)!=1:
            li.remove(function)
            remove_occur(li)

# Read the file and create a list with all functions starting by
# function_source
for line in file1:
    if function_source in line:
        lin=""
        function_name=""
        linecut=""
        for letter in line:
            if letter == "_" or ('mmcagent' in test and 'def' in lin):
                linecut=line[(len(lin)+1):]
                break
            else :
                lin=lin+letter

        for letter in linecut:
            if letter=='(':
                break
            else:
                function_name=function_name+letter
        list_functions_source.append(function_name)
file1.close()

# Read the file and create a list with all functions starting by function_test
file2=open(file_test,'r')
for line in file2:
    if re.search(function_test, line):
        if line[0]=='#':
            lin=""
            function_name=""
            linecut=""
            for letter in line:
                if letter == ".":
                    linecut=line[(len(lin)+1):]
                    break
                else :
                    lin=lin+letter

            for letter in linecut:
                if letter=='(':
                    break
                else:
                    function_name=function_name+letter
            list_functions_not_tested.append(function_name)
        else:
            lin=""
            function_name=""
            linecut=""
            for letter in line:
                if letter == ".":
                    linecut=line[(len(lin)+1):]
                    break
                else :
                    lin=lin+letter


            for letter in linecut:
                if letter=='(':
                    break
                else:
                    function_name=function_name+letter
            list_functions_tested.append(function_name)
file2.close()
SupEspLi(list_functions_source)
SupEspLi(list_functions_not_tested)
SupEspLi(list_functions_tested)
remove_occur(list_functions_tested)
remove_occur(list_functions_source)
remove_occur(list_functions_not_tested)
    
for function_source in list_functions_source:
    if function_source not in (list_functions_tested):
        list_functions.append(function_source)

all = len(list_functions_source)
tested = len(list_functions_tested)
percent = (float(tested) / float(all) ) * 100
print "%f %% functions are tested (%d / %d)" % (percent, tested, all)

# Write in alphabetics' order the function(s) witch are not in the test's
# module
if list_functions:
    list_functions.sort()
    for function in list_functions:
        print "%s is not tested" % function

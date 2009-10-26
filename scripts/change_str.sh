#!/bin/sh
#
# Copyright (C) 2006, Adam Cécile et Jerome Wax pour Linbox FAS
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

echo "Enter the pattern to replace :"
read pattern1


echo "Enter the replacing pattern :"
read pattern2

for file in `find . -type f`
  do
    echo ${file} | egrep -q ".svn" || \
    sed -i "s/${pattern1}/${pattern2}/g" ${file}
  done
  
exit 0

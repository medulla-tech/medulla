#!/bin/sh
#
# Copyright (C) 2006, Adam Cécile et Jérôme Wax pour Linbox FAS
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

for name in `find "${1}" -type f -name "*.po"`
  do
    newname=`echo ${name} | sed 's!^\(.*\)/\(.*\).po$!\1/\2.mo!'`
    echo -n "Building ${name} as ${newname}..."
    msgfmt ${name} -o ${newname} || true
    echo "done"
  done

exit 0
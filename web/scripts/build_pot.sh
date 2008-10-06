#!/bin/sh
#
# Copyright (C) 2006, Jérôme Wax and Adam Cécile  for Linbox FAS
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

POT="modules/base/locale/base.pot"

rm ${POT}
touch ${POT}
find . -iname "*.php" -exec xgettext -C -j -o ${POT} --language=PHP --keyword=_ {} \;

for name in `find ${1} -type f -name *.po`; do
    echo -n "updating ${name}..."
    msgmerge --update --add-location --sort-output ${name} ${POT}
    echo "done"
done

exit 0

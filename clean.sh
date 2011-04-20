#!/bin/sh
# (c) 2011 Mandriva, http://www.mandriva.com
#
# Authors:
#   Jean Parpaillon <jparpaillon@mandriva.com>
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

set -e

AUTOGEN_FILES="aclocal.m4 autom4te.cache configure config.guess config.log config.sub config.status depcomp compile libtool ltmain.sh missing mkinstalldirs config.h config.h.in py-compile"

echo "Clean autogen generated files"
for file in $AUTOGEN_FILES; do
    ( cd $(dirname $0) && rm -rf $file )
done

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

$(dirname $0)/clean.sh

#
# check tools version number -- we require >= 1.10
#
find_tools() {
    tool=$1

    if [ -s "$(which $tool-1.10)" ]; then
        TOOL=$tool-1.10
    elif [ -s "$(which $tool)" ]; then
        major=`$tool --version | grep $tool | awk {'print \$4'} | awk -F '.' {'print \$1'}`
        minor=`$tool --version | grep $tool | awk {'print \$4'} | awk -F '.' {'print \$2'}`
        if test "$major" -gt 1; then
            TOOL=$tool
        elif test "$major" -eq 1 -a "$minor" -ge 10; then
            TOOL=$tool
        else
            echo "Required: $tool version >= 1.10" >&2
            exit 1
        fi
    else
        echo "Required: $tool version >= 1.10" >&2
        exit 1
    fi

    echo "$TOOL"
}

# Find required tools:
ACLOCAL=$(find_tools aclocal)
AUTOMAKE=$(find_tools automake)
if [ -z "$(which libtool)" ]; then
    echo "Required: libtool"
    exit 1
fi

# Run the actual process:
if test -f $(dirname $0)/configure.ac; then
    (
        cd $(dirname $0)
        echo "Regenerating autoconf files"
        $ACLOCAL -I m4
        libtoolize -c
        #autoheader
        $AUTOMAKE --add-missing --copy
        autoconf
        )
fi

$(dirname $0)/configure $@

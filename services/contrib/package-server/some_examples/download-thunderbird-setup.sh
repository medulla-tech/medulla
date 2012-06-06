#!/bin/bash
#
# (c) 2008-2009 Mandriva, http://www.mandriva.com
#
# $Id$
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

BASE=http://download.mozilla.org

if [ "$#" -ne "3" ]; then
    echo "usage: $0 <platform> <version> <lang>"
    exit 1
fi

PLATEFORM=$1
VERSION=$2
LANG=$3

URI="$BASE?product=thunderbird-$VERSION&os=$PLATEFORM&lang=$LANG"

wget $URI

#!/bin/sh
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

for i in 1 2 4 7; do # units
        for j in 1 10 100 1000; do # magnitude orders (kB)
                l=$(($i * $j))
                f=`printf "dummy-package-%.4d-kB" $l`
                mkdir $f
                pushd $f
                dd if=/dev/urandom of=data.bin bs=1k count=$l
                cat ../summon-dummy-packages.xml | sed "s/##ID##/$f/" | sed "s/##CMD##/uuencode -m data.bin data.bin/" > conf.xml
                popd
        done
done

#!/bin/sh -e
# (c) 2011 Mandriva, http://www.mandriva.com
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
#
# Author(s):
#   Jean Parpaillon <jparpaillon@mandriva.com>
#
topdir=$(dirname $0)

usage ()
{
    echo "$0: path_to_key.pub"
}

abspath ()
{
    path=$1
    dir=$(cd $(dirname ${path}) && pwd)
    name=$(basename ${path})
    echo ${dir}/${name}
}

if [ $# != 1 ]; then
    usage
    exit 0
fi

key=$(abspath $1)

make -C ${topdir} -f win32.mk KEY_PATH=${key}

if [ "${topdir}" != "$(pwd)" ]; then
    packpath=$(make -s -C ${topdir} -f win32.mk path)
    cp ${topdir}/${packpath} .
fi

exit 0

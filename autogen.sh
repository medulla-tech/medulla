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

# Replace old stuff with the new intelligent autoreconf
# http://www.gnu.org/s/libtool/manual/automake/Error-required-file-ltmain_002esh-not-found.html
autoreconf --install

exit 0

#!/bin/bash
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2011 Mandriva, http://www.mandriva.com
#
# $Id: build_pot.sh 6329 2010-03-30 07:51:21Z cdelfosse $
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

for module in dyngroup glpi imaging inventory msc pkgs pulse2 backuppc update; do
    POT="modules/$module/locale/$module.pot"
    rm -f $POT
    touch $POT
    # Change gettext keyword according to the module
    if [ $module == base ]; then
    	keyword="_"
	    fpath=.
    else
    	keyword=_T
    	fpath=modules/$module
    fi
    find $fpath -iname "*.php" -exec xgettext -C -j -o ${POT} --language=PHP --keyword=$keyword {} \;
    # Build only the POT file
    for name in `find modules/$module/locale -type f -name *.po`; do
        echo -n "updating ${name}..."
        msgmerge --update --add-location --sort-output ${name} ${POT}
        echo "done"
    done
done

exit 0

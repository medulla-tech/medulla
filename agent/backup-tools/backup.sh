#!/bin/bash
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2009 Mandriva, http://www.mandriva.com
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

# Helper tool to backup the content of a directory as an ISO to burn

# arg1 : share name
# arg2 : share path
# arg3 : backup path
# arg4 : user
# arg5 : media size
# arg6 : helpers path

share=$1
sharepath=$2
backuppath=$3
login=$4
mediasize=$5
helpers=$6

stamp=$(date "+%Y%m%d")
backupdest=${backuppath}/${login}-${share}-${stamp}
log=${backupdest}/archive.log
tmpdir=/tmp/cdlist-${login}-${share}

mkdir -p ${backupdest}

${helpers}/cdlist ${sharepath} ${backupdest} ${mediasize} > ${log}

if [ "$?" != "0" ]; then
    echo "cdlist failed !" > ${log}
    exit 1
fi

nbcd=$(tail -n 1 ${log})

mkdir -p ${tmpdir}

for i in $(seq 1 ${nbcd}); do
    sed -i "s,=,\\\=,g" ${backupdest}/list${i}
    cat ${backupdest}/list${i} | sed -e "s,^[0-9]*[ ]*${sharepath}/\(.*\)$,\1=${sharepath}/\1," > ${tmpdir}/list${i}
    echo "FILELIST=${backupdest}/list${i}" >> ${tmpdir}/list${i}
done

for i in $(seq 1 ${nbcd}); do
    echo ${login}-${share}-${stamp}/${stamp}-${share}-vol${i}.iso
    echo "Creation volume ${i}/${nbcd}"

    mkisofs -v -graft-points -iso-level 4 -joliet-long \
	-path-list ${tmpdir}/list${i} \
	-J -r -A "Backup de ${sharepath} (date: ${stamp})" \
	-o ${backupdest}/${stamp}-${share}-vol${i}.iso \
	  2>&1
#	-volset-size ${nbcd} -volset-seqno ${i}  2>&1
#	-volset-size ${nbcd} -volset-seqno ${i} >> ${log} 2>&1

    if [ "$?" != "0" ]; then
	exit 2
    fi
done

chmod 700 ${backupdest}
chown 600 ${backupdest}/*
chown -R $login ${backupdest}
rm -rf ${tmpdir}

exit 0

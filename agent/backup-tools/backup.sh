#!/bin/bash
# $Id: backup.sh 48 2004-05-10 13:18:53Z jwax $
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
    sed -i "s,=,\\\=," ${backupdest}/list${i}
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

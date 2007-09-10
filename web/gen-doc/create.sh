#!/bin/bash


rm -rf /tmp/mmc-base/
TMPDIR=`mktemp -d`
echo ${TMPDIR}
svn export http://svn2/repo/mmc-base/trunk ${TMPDIR}/mmc/ --force

svn export http://svn2/repo/mmc-samba/trunk/samba ${TMPDIR}/mmc/modules/ --force

cp doxygen-mmc.conf ${TMPDIR}/

cd ${TMPDIR}
doxygen doxygen-mmc.conf

rm -rf ${TMPDIR}


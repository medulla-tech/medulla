#!/bin/bash


rm -rf /tmp/lmc-base/
TMPDIR=`mktemp -d`
echo ${TMPDIR}
svn export http://svn2/repo/lmc-base/trunk ${TMPDIR}/lmc/ --force

svn export http://svn2/repo/lmc-ox/trunk/ox ${TMPDIR}/lmc/modules/ --force
svn export http://svn2/repo/lmc-samba/trunk/samba ${TMPDIR}/lmc/modules/ --force

cp doxygen-lmc.conf ${TMPDIR}/

cd ${TMPDIR}
doxygen doxygen-lmc.conf

rm -rf ${TMPDIR}


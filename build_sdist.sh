#!/bin/bash

VERSION='5.4.5'

rm -f medulla-*.tar.gz medulla-*.tar.gz.md5
git clean -fdx && ./autogen.sh && ./configure --sysconfdir=/etc --localstatedir=/var --disable-python-check --disable-conf && make distcheck
tar xzvf medulla-$VERSION.tar.gz
cp setup.py medulla-$VERSION
cp -frv debian medulla-$VERSION
cp -frv services/contrib/glpi-92.sql  medulla-$VERSION/services/contrib/ 
cp -frv services/contrib/glpi-94.sql  medulla-$VERSION/services/contrib/
cp -frv services/contrib/glpi-95.sql  medulla-$VERSION/services/contrib/
cp -frv services/contrib/glpi-100.sql medulla-$VERSION/services/contrib/
mkdir medulla-$VERSION/services/systemd
cp -fv services/systemd/mmc-agent.service medulla-$VERSION/services/systemd
tar czvf medulla-$VERSION.tar.gz medulla-$VERSION
mv medulla-$VERSION.tar.gz medulla_$VERSION.orig.tar.gz
rm -fr medulla-$VERSION/
if [ $? -eq 0 ]; then
    for tarball in medulla*.tar.gz; do
        md5sum $tarball > $tarball.md5
    done
fi

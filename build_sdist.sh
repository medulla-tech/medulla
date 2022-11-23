#!/bin/bash

VERSION='4.6.9'

rm -f pulse2-*.tar.gz pulse2-*.tar.gz.md5
git clean -fdx && ./autogen.sh && ./configure --sysconfdir=/etc --localstatedir=/var --disable-python-check --disable-conf && make distcheck
tar xzvf pulse2-$VERSION.tar.gz
cp setup.py pulse2-$VERSION
cp -frv debian pulse2-$VERSION
cp -frv services/contrib/glpi-92.sql pulse2-$VERSION/services/contrib/ 
cp -frv services/contrib/glpi-94.sql pulse2-$VERSION/services/contrib/
cp -frv services/contrib/glpi-95.sql pulse2-$VERSION/services/contrib/
mkdir pulse2-$VERSION/services/systemd
cp -fv services/systemd/mmc-agent.service pulse2-$VERSION/services/systemd
tar czvf pulse2-$VERSION.tar.gz pulse2-$VERSION
mv pulse2-$VERSION.tar.gz pulse2_$VERSION.orig.tar.gz
rm -fr pulse2-$VERSION/
if [ $? -eq 0 ]; then
    for tarball in pulse2*.tar.gz; do
        md5sum $tarball > $tarball.md5
    done
fi

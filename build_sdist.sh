#!/bin/bash

VERSION='3.9.90'

rm -f mmc-core-*.tar.gz mmc-core-*.tar.gz.md5
git clean -fdx && ./autogen.sh && ./configure --sysconfdir=/etc --localstatedir=/var --disable-python-check --disable-conf && make distcheck
tar xzvf mmc-core-$VERSION.tar.gz
cp setup.py mmc-core-$VERSION
cp -frv debian pulse2-$VERSION
tar czvf mmc-core-$VERSION.tar.gz mmc-core-$VERSION
if [ $? -eq 0 ]; then
    for tarball in mmc-core-*.tar.gz; do
        md5sum $tarball > $tarball.md5
    done
fi

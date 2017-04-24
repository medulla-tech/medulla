#!/bin/bash

rm -f mmc-core-*.tar.gz mmc-core-*.tar.gz.md5
git clean -fdx && ./autogen.sh && ./configure --sysconfdir=/etc --localstatedir=/var --disable-python-check --disable-conf && make distcheck
tar xzvf mmc-core-3.9.90.tar.gz
cp setup.py mmc-core-3.9.90
tar czvf mmc-core-3.9.90.tar.gz pulse2-3.9.90
if [ $? -eq 0 ]; then
    for tarball in mmc-core-*.tar.gz; do
        md5sum $tarball > $tarball.md5
    done
fi

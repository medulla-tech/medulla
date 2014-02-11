#!/bin/bash

rm -f mmc-core-*.tar.gz mmc-core-*.tar.gz.md5
git clean -fdx && ./autogen.sh && ./configure --sysconfdir=/etc --localstatedir=/var --disable-python-check --disable-conf && make distcheck
if [ $? -eq 0 ]; then
    for tarball in mmc-core-*.tar.gz; do
        md5sum $tarball > $tarball.md5
    done
fi

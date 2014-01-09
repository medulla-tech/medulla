#!/bin/bash

rm -f pulse2-*.tar.gz pulse2-*.tar.gz.md5
git clean -fdx && ./autogen.sh && ./configure --sysconfdir=/etc --localstatedir=/var --disable-python-check --disable-conf && make distcheck
if [ $? -eq 0 ]; then
    for tarball in pulse2-*.tar.gz; do
        md5sum $tarball > $tarball.md5
    done
fi

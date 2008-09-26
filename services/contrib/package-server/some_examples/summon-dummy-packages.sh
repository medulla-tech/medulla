#!/bin/sh

for i in 1 2 4 7; do # units
        for j in 1 10 100 1000; do # magnitude orders (kB)
                l=$(($i * $j))
                f=`printf "dummy-package-%.4d-kB" $l`
                mkdir $f
                pushd $f
                dd if=/dev/urandom of=data.bin bs=1k count=$l
                cat ../summon-dummy-packages.xml | sed "s/##ID##/$f/" | sed "s/##CMD##/uuencode -m data.bin data.bin/" > conf.xml
                popd
        done
done

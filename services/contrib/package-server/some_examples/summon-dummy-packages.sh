#!/bin/sh

for i in 1 2 4 7; do # units
        for j in 1 10 100 1000; do # magnitude orders (kB)
                l=$(($i * $j))
                mkdir $l.kB
                pushd $l.kB
                dd if=/dev/urandom of=data.bin bs=1k count=$l
                uuencode -m data.bin data.bin > data.b64
                cat ../summon-dummy-packages.xml | sed "s/##ID##/$l.kB/" | sed "s/##CMD##/cat data.b64/" > conf.xml
                popd
        done
done

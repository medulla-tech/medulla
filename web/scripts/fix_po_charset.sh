#!/bin/bash

for i in `find -name "*.po"`; do sed -e 's,charset=CHARSET,charset=UTF-8,g' -i $i ; done
for i in `find -name "*.pot"`; do sed -e 's,charset=CHARSET,charset=UTF-8,g' -i $i ; done

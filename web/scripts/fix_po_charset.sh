#!/bin/bash

for i in `find -name "*.po"`; do sed -e 's,charset=CHARSET,charset=UTF-8,g' -i $i ; done

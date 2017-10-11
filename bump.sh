#!/bin/bash

version=$1
rc=$2

if [ ! -z $1 ]; then

    sed -i "s/^AC_INIT.*$/AC_INIT\(project, [$version], [http:\/\/www.siveo.net]\)/" configure.ac
    sed -i "s/^VERSION = .*$/VERSION = \"$version\"/" agent/mmc/agent.py
    sed -i "s/^release = .*$/release = '$version'/" ../doc/source/conf.py
    sed -i "s/version=*$/version='$version'/" setup.py

    for plugin in `ls agent/mmc/plugins`
    do
        sed -i "s/^VERSION = .*$/VERSION = \"$version\"/" agent/mmc/plugins/${plugin}/__init__.py
        sed -i "s/^\$mod->setVersion.*/\$mod->setVersion(\"$version\");/" web/modules/${plugin}/infoPackage.inc.php
    done

    git diff
#    if [ ! -z $2 ]; then
#        git commit -a -m "core: bump version to $1 (RC)"
#    else
#        git commit -a -m "core: bump version to $1"
#    fi

else

    echo Missing version.

fi


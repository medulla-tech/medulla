#!/bin/bash

version=$1
rc=$2

if [ ! -z $1 ]; then

    sed -i "s/^AC_INIT.*$/AC_INIT\(project, [$1], [http:\/\/projects.mandriva.org\/projects\/mmc]\)/" configure.ac
    sed -i "s/^VERSION = .*$/VERSION = \"$1\"/" agent/mmc/agent.py
    sed -i "s/^release = .*$/release = '$1'/" ../doc/source/conf.py

    for plugin in admin base ppolicy services dashboard
    do
        sed -i "s/^VERSION = .*$/VERSION = \"$1\"/" agent/mmc/plugins/${plugin}/__init__.py
        sed -i "s/^\$mod->setVersion.*/\$mod->setVersion(\"$1\");/" web/modules/${plugin}/infoPackage.inc.php
    done

    git diff
    if [ ! -z $2 ]; then
        git commit -a -m "core: bump version to $1 (RC)"
    else
        git commit -a -m "core: bump version to $1"
    fi

else

    echo Missing version.

fi


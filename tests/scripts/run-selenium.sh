#!/bin/bash -e

#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2009 Mandriva, http://www.mandriva.com
#
# $Id$
#
# This file is part of Mandriva Management Console (MMC).
#
# MMC is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# MMC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MMC.  If not, see <http://www.gnu.org/licenses/>.

# run-selenium.sh <test-suite-file> <result-file>
#
# Run Selenium with the in test-suite-file, and put all the results in
# resultèfile

TESTS=$1
RESULTDIR=$2

XSERVER=X
DISPLAY=:1

if ! which java;
then
    if [ -f /usr/lib/jre-1_5_0_06/bin/java ];
    then
        # Special case for one of our test machine
        JAVA=/usr/lib/jre-1_5_0_06/bin/java
    else
        echo "JAVA must be installed."
        exit 1
    fi
else
    JAVA=java
fi


if ! which X;
then
    echo "X must be installed."
    exit 1
fi

if ! which firefox;
then
    echo "firefox must be installed."
    exit 1
fi

# FIXME: should find a better way
if [ -f /usr/lib/mozilla-firefox-2.0.0.19/mozilla-firefox-bin ];
    then
    # Firefox exec path for CS4
    FIREFOX=/usr/lib/mozilla-firefox-2.0.0.19/mozilla-firefox-bin
elif [ -f /usr/lib/firefox-3.0.18/firefox ];
    then
    # Firefox exec path for MES5
    FIREFOX=/usr/lib/firefox-3.0.18/firefox
else
    echo "Can't find firefox executable"
    exit 1
fi

# Start X on :1
killall $XSERVER || true
$XSERVER $DISPLAY &
export DISPLAY

# Cleanup firefox cookie
rm -f /root/.mozilla/firefox/*.default/cookies.sqlite

set +e
# See: http://seleniumhq.org/docs/05_selenium_rc.html#server-options
$JAVA -jar $MMCCORE/tests/libs/selenium-server.jar -userExtensions $MMCCORE/tests/libs/user-extensions.js -htmlSuite "*firefox $FIREFOX" "http://localhost/" "./$TESTS" "$RESULTDIR/result.html"
RET=$?
set -e

killall $XSERVER

cp -vr /var/log/mmc/* $RESULTDIR

exit $RET

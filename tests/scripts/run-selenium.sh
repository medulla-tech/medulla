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
RESULT=$2

XSERVER=X
DISPLAY=:1

if [ ! which java ];
then
    echo "JAVA must be installed."
    exit 1
fi

if [ ! which X ];
then
    echo "X must be installed."
    exit 1
fi

if [ ! which firefox ];
then
    echo "firefox must be installed."
    exit 1
fi
FIREFOX=`which firefox`

# Start X on :1
killall $XSERVER
$XSERVER $DISPLAY &
export DISPLAY

# Cleanup firefox cookie
rm -f /root/.mozilla/firefox/*.default/cookies.sqlite

# See: http://seleniumhq.org/docs/05_selenium_rc.html#server-options
java -jar selenium-server.jar -userExtensions user-extensions.js -htmlSuite "*firefox $FIREFOX" "http://localhost/" "$TESTS" "$RESULT"

killall $XSERVER

exit 0

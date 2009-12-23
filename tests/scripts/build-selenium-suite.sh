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

# build-selenium-suite.sh <result-file> <directory-with-tests>
#
# Build a selenium test file, using tests stored in the given directory

FILENAME="$1"
DIR="$2"

cat << EOF > ${FILENAME}
<html>
<head>
<meta content="text/html; charset=ISO-8859-1" http-equiv="content-type">
<title>Selenium Test Suite</title>

</head\>

<body>

  <table cellpadding="1" cellspacing="1"border="1">
    <tbody>
      <tr><td><b>Selenium Test Suite</b></td></tr>
    </tbody>
EOF

for file in `ls $DIR`
do
    file=$DIR/$file
    test -d ${file} && for file2 in `ls ${file}`
    do
        echo "<tr><td><a href=\"./${file}/${file2}\">${file}/`echo ${file2} | sed 's/^\(.*\)\..*$/\1/'`</a></td></tr>" >> ${FILENAME}
    done
done

cat << EOF >> ${FILENAME}
  </table>
  
    
</body>
</html>

EOF

exit 0

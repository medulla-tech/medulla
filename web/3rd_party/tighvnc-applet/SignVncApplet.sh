#!/bin/bash
#
# (c) 2008 Mandriva, http://www.mandriva.com/
#
# $Id$
#
# This file is part of Pulse 2, http://pulse2.mandriva.org
#
# Pulse 2 is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Pulse 2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pulse 2; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

# It is nomore necessary to sign the TightVNC plugin
# because it is already signed and his signature is better for
# security checks

export JAVA_HOME=/usr/lib/j2sdk1.5-sun
export PATH=$JAVA_HOME/bin:$PATH

DN="cn=Mandriva Pulse 2,OU=Pulse 2 Team,O=Mandriva S.A.,L=Paris,S=France,C=FR"
NAME=VncViewer

cp -a ../../msc/graph/java/$NAME.jar .
jar tvf $NAME.jar

rm $NAME.keystore
keytool -genkey -keyalg dsa -keysize 1024 -validity 3650 -dname "$DN" -keystore $NAME.keystore -alias "Pulse 2 - $NAME"

jarsigner -keystore $NAME.keystore -verbose $NAME.jar "Pulse 2 - $NAME"
jarsigner -verify -verbose -certs $NAME.jar


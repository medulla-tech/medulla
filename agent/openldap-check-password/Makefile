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

CONFFILE = /etc/openldap/mmc-check-password.conf

all: mmc-check-password

mmc-check-password.o:
	$(CC) -g -O2 -Wall -fpic -c -I/usr/include/openldap/include -I/usr/include/openldap/slapd -DCONFIG_FILE=\"$(CONFFILE)\" mmc-check-password.c

mmc-check-password: clean mmc-check-password.o
	$(CC) -shared -o mmc-check-password.so mmc-check-password.o

install: mmc-check-password
	# FIXME: don't know how to make it better ...
	-[ -d /usr/lib/openldap ] && \
	$(INSTALL) mmc-check-password.so -m 755 -o root -g root /usr/lib/openldap/
	-[ -d /usr/lib64/openldap ] && \
	$(INSTALL) mmc-check-password.so -m 755 -o root -g root /usr/lib64/openldap/
	$(INSTALL) mmc-check-password.conf -m 644 -o root -g root $(CONFFILE)

clean:
	$(RM) mmc-check-password.o mmc-check-password.so *~


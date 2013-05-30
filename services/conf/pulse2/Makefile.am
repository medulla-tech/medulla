# (c) 2011 Mandriva, http://www.mandriva.com
#
# $Id$
#
# This file is part of Mandriva Pulse2 project.
#
# This software is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software.  If not, see <http://www.gnu.org/licenses/>.
#
# Author(s):
#   Jean Parpaillon <jparpaillon@mandriva.com>
#
pulseconfdir = $(sysconfdir)/mmc/pulse2

certpaths = \
	package-server/keys inventory-server/keys scheduler/keys \
	launchers/keys
certca = $(patsubst %,%/cacert.pem,$(certpaths))
certpriv = $(patsubst %,%/privkey.pem,$(certpaths))

nobase_pulseconf_DATA = \
	package-server/package-server.ini inventory-server/inventory-server.ini \
	inventory-server/xml-fix/00_Microsoft_consistency.py \
	inventory-server/xml-fix/01_Dell_consistency.py \
	inventory-server/xml-fix/02_ATI_consistency.py \
	inventory-server/xml-fix/03_ASUS_consistency.py \
	inventory-server/xml-fix/04_Adobe_consistency.py \
	inventory-server/xml-fix/05_HP_consistency.py \
	scheduler/scheduler.ini launchers/launchers.ini atftpd/pcre.conf \
	imaging-server/imaging-server.ini \
	$(certca) $(certpriv)

EXTRA_DIST = $(nobase_pulseconf_DATA)  imaging-server/imaging-server.ini.in \
             scheduler/scheduler.ini.in launchers/launchers.ini.in
CLEANFILES = imaging-server/imaging-server.ini scheduler/scheduler.ini \
             launchers/launchers.ini 

imaging-server/imaging-server.ini scheduler/scheduler.ini launchers/launchers.ini: Makefile
	rm -f $@ $@.tmp
	$(MKDIR_P) $(@D)
	srcdir=''; \
	  test -f ./$@.in || srcdir=$(srcdir)/; \
	  $(edit) $${srcdir}$@.in >$@.tmp
	mv $@.tmp $@

edit = sed \
        -e 's|@bindir[@]|$(bindir)|g' \
        -e 's|@sbindir[@]|$(sbindir)|g' \
        -e 's|@libdir[@]|$(libdir)|g'

if ENABLE_CONF_BACKUP
INSTALL += --backup=numbered
endif

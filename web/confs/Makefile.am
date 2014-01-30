# (c) 2011 Mandriva, http://www.mandriva.com
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
#
# Author(s)
#   Jean Parpaillon <jparpaillon@mandriva.com>
#
pkgsysconfdir = ${sysconfdir}/mmc
if ENABLE_CONF
nobase_pkgsysconf_DATA = mmc.ini apache/mmc.conf
endif

EXTRA_DIST = mmc.ini.in apache/mmc.conf.in
CLEANFILES = mmc.ini apache/mmc.conf

edit = sed \
        -e 's|@bindir[@]|$(bindir)|g' \
        -e 's|@sbindir[@]|$(sbindir)|g' \
        -e 's|@datadir[@]|$(datadir)|g' \
        -e 's|@pkgdatadir[@]|$(datadir)/mmc|g' \
        -e 's|@prefix[@]|$(prefix)|g' \
        -e 's|@localstatedir[@]|$(localstatedir)|g' \
        -e 's|@sysconfdir[@]|$(sysconfdir)|g'

mmc.ini apache/mmc.conf: Makefile
	rm -f $@ $@.tmp
	$(MKDIR_P) $(@D)
	srcdir=''; \
	  test -f ./$@.in || srcdir=$(srcdir)/; \
	  $(edit) $${srcdir}$@.in >$@.tmp
	mv $@.tmp $@

mmc.ini: $(srcdir)/mmc.ini.in
apache/mmc.conf: $(srcdir)/apache/mmc.conf.in




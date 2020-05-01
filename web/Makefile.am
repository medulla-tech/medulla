# (c) 2011 Mandriva, http://www.mandriva.com
#
# $Id$
#
# This file is part of Mandriva Pulse2.
#
# Mandriva Pulse2 is free software; you can redistribute it and/or modify
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
# along with MMC.  If not, see <http://www.gnu.org/licenses/>.
#
# Author(s)
#   Jean Parpaillon <jparpaillon@mandriva.com>
#
mmcdatadir = $(datadir)/mmc
SUBDIRS = confs

dataipaths = graph img includes jsframework logout modules/base  modules/dashboard \
	modules/dyngroup modules/msc modules/inventory modules/glpi modules/pkgs \
	modules/pulse2 modules/imaging modules/backuppc modules/update modules/support \
	modules/kiosk conf/apache modules/ppolicy modules/update modules/services modules/report \
	modules/xmppmaster index.php main.php version.php license.php forgotpassword.php token.php
datafiles = $(shell find $(patsubst %,$(srcdir)/%,$(datapaths)) \
		-type f \
		! -name '*.po' \
		! -name '*.mo' \
		! -path '*/.svn/*')

mmcdatadir = $(datadir)/mmc

pofiles = $(shell cd $(srcdir) && find -name '*.po')
mofiles = $(patsubst %.po,%.mo,$(pofiles))

nobase_mmcdata_DATA = $(datafiles) $(mofiles)

nodist_mmcdata_DATA = site.php
EXTRA_DIST = $(datafiles) $(pofiles) site.php.in
CLEANFILES = $(mofiles) site.php

%.mo: %.po
	$(MKDIR_P) $(@D)
	$(MSGFMT) $< -o $@

edit = sed \
        -e 's|@bindir[@]|$(bindir)|g' \
        -e 's|@sbindir[@]|$(sbindir)|g' \
        -e 's|@pkgdatadir[@]|$(datadir)/mmc|g' \
        -e 's|@prefix[@]|$(prefix)|g' \
        -e 's|@localstatedir[@]|$(localstatedir)|g' \
        -e 's|@sysconfdir[@]|$(sysconfdir)|g'

site.php: Makefile
	rm -f $@ $@.tmp
	$(MKDIR_P) $(@D)
	srcdir=''; \
	  test -f ./$@.in || srcdir=$(srcdir)/; \
	  $(edit) $${srcdir}$@.in >$@.tmp
	mv $@.tmp $@

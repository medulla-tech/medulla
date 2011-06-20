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
SUBDIRS = confs

datapaths = graph img includes jsframework logout modules \
	index.php main_content.php main.php version.php license.php site.php

all-local: site.php

datafiles = $(shell find $(patsubst %,$(srcdir)/%,$(datapaths)) \
	-type f \
	! -name '*.po' \
	! -name '*.mo' \
	! -path '*/.svn/*')
pofiles = $(shell cd $(srcdir) && find -name '*.po')
mofiles = $(patsubst %.po,%.mo,$(pofiles))

nobase_pkgdata_DATA = $(datafiles) $(mofiles)

EXTRA_DIST = $(datafiles) $(pofiles) site.php.in
CLEANFILES = $(mofiles) site.php

%.mo: %.po
	$(MKDIR_P) $(@D)
	$(MSGFMT) $< -o $@

edit = sed \
        -e 's|@bindir[@]|$(bindir)|g' \
        -e 's|@sbindir[@]|$(sbindir)|g' \
        -e 's|@pkgdatadir[@]|$(pkgdatadir)|g' \
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
site.php: $(srcdir)/site.php.in

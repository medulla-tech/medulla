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
# Author(s):
#   Jean Parpaillon <jparpaillon@mandriva.com>
#
pythonmodules = apis apis.clients database database.dyngroup \
	database.imaging database.inventory database.msc \
	database.msc.orm database.pulse imaging \
	imaging_server inventoryserver launcher managers \
	package_server package_server.assign_algo \
	package_server.assign_algo.default \
	package_server.assign_algo.terminal_type \
        package_server.common package_server.description \
	package_server.imaging package_server.imaging.api \
	package_server.imaging.common package_server.mirror \
	package_server.mirror_api package_server.package_api_get \
	package_server.package_api_put package_server.scheduler_api \
	package_server.user_package_api scheduler \
	scheduler.assign_algo scheduler.assign_algo.default \
	scheduler.assign_algo.ip_class scheduler.cache \
	scheduler.tracking

all-local: site.py version.py

# Expands Python modules list with found *.py files in each module given in pythonmodules
modpythondir = $(pythondir)/$(notdir $(realpath $(srcdir)))
nobase_modpython_DATA = $(wildcard $(srcdir)/*.py $(patsubst %,$(srcdir)/%/*.py ,$(subst .,/,$(pythonmodules))))
nodist_modpython_DATA = site.py

examplesdir = @examplesdir@
if ENABLE_PACKAGER_MODE
packagermode = True
else
packagermode = False
endif

EXTRA_DIST = site.py.in version.py.in $(nobase_modpython_DATA)
CLEANFILES = site.py
DISTCLEANFILES = version.py

edit = sed \
        -e 's|@packagermode[@]|$(packagermode)|g' \
        -e 's|@bindir[@]|$(bindir)|g' \
        -e 's|@sbindir[@]|$(sbindir)|g' \
        -e 's|@pkgdatadir[@]|$(pkgdatadir)|g' \
        -e 's|@prefix[@]|$(prefix)|g' \
        -e 's|@localstatedir[@]|$(localstatedir)|g' \
        -e 's|@mmcconfdir[@]|$(mmcconfdir)|g' \
        -e 's|@examplesdir[@]|$(examplesdir)|g' \
        -e 's|@sysconfdir[@]|$(sysconfdir)|g'

site.py: Makefile
	rm -f $@ $@.tmp
	$(MKDIR_P) $(@D)
	srcdir=''; \
	  test -f ./$@.in || srcdir=$(srcdir)/; \
	  $(edit) $${srcdir}$@.in >$@.tmp
	mv $@.tmp $@

site.py: site.py.in

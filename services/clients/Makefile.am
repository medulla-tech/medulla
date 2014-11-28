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

SUBDIRS = win32

posixclientdir = $(localstatedir)/lib/pulse2/clients

posixclientscripts = generate-agents create-repos.sh \
                   templates/mac/package/Contents/Resources/postflight \
                   templates/deb/package/DEBIAN/postinst \
                   templates/deb/package/etc/init.d/linuxvnc \
                   templates/rpm/package/SOURCES/postinst


posixclientdata = agents.conf \
                templates/mac/package/Contents/package_version \
                templates/mac/package/Contents/header.png 

nobase_posixclient_SCRIPTS = $(posixclientscripts) 
nobase_posixclient_DATA = $(posixclientdata) 

install-data-local:
	$(MKDIR_P) $(DESTDIR)$(posixclientdir)/templates/deb/package/opt
	$(MKDIR_P) $(DESTDIR)$(posixclientdir)/templates/rpm/package/SPECS
	$(MKDIR_P) $(DESTDIR)$(posixclientdir)/templates/rpm/package/BUILD
	$(MKDIR_P) $(DESTDIR)$(posixclientdir)/templates/rpm/package/BUILDROOT
	$(MKDIR_P) $(DESTDIR)$(posixclientdir)/templates/rpm/package/RPMS
	$(MKDIR_P) $(DESTDIR)$(posixclientdir)/templates/rpm/package/SRPMS

	
EXTRA_DIST = $(posixclientscripts) $(posixclientdata)

prereqs-deb:
	apt-get update
	apt-get install rpm dpkg

.PHONY = prereqs-deb

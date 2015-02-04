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

posixclientscripts = generate-agents create-repos.sh installer.sh.in \
                   templates/mac/package/Contents/Resources/postflight.in \
                   templates/deb/package/DEBIAN/postinst \
                   templates/deb/package/etc/init.d/linuxvnc \
                   templates/rpm/package/SOURCES/postinst \
                   vpn/vpn-client-set.sh \
		   vpn/vpn-server-user-create.sh \
		   vpn/vpn-service-uninstall.sh \
                   vpn/vpn-server-set.sh \
		   vpn/vpn-service-install.sh \
		   vpn/softether/build.sh \
                   agent/pulse2-agent \
		   agent/setup.py \
		   agent/service.py \
		   agent/install.sh \
		   agent/uninstall.sh \
                   agent/linux/pulse2-agent.init \
                   agent/linux/pulse2-agent.init.lsb \
                   agent/linux/pulse2-agent.service


posixclientdata = agents.conf \
                templates/mac/package/Contents/package_version \
                templates/mac/package/Contents/header.png \
                vpn/vpn-variables.in \
	        agent/pulse2agent.defaults.in \
	        agent/pulse2agent.ini \
                agent/linux/pulse2-agent.default \
		agent/mac/com.pulse2.agent.plist \
                agent/pulse2agent/__init__.py \
		agent/pulse2agent/_config.py \
                agent/pulse2agent/config.py \
		agent/pulse2agent/connect.py \
		agent/pulse2agent/control.py \
		agent/pulse2agent/inventory.py \
		agent/pulse2agent/parse.py \
		agent/pulse2agent/pexceptions.py \
		agent/pulse2agent/ptypes.py \
		agent/pulse2agent/shell.py  \
		agent/pulse2agent/vpn.py

installernsi = agent/win32/installer.nsi \
	       vpn/softether/softether-installer.nsi

installerdata = \
	agent/win32/customoptions.ini \
	agent/win32/artwork/header.bmp \
	agent/win32/artwork/uninstall.ico \
	agent/win32/artwork/wizard.bmp \
	agent/win32/artwork/install.ico \
	agent/win32/libs/StrRep.nsh \
	agent/win32/libs/ReplaceInFile.nsh \
	agent/win32/libs/VersionCompare.nsh \
	agent/win32/libs/InstallOptionsMacro.nsh



nobase_posixclient_SCRIPTS = $(posixclientscripts) 
nobase_posixclient_DATA = $(posixclientdata) 

install-data-local:
	$(MKDIR_P) $(DESTDIR)$(posixclientdir)/templates/deb/package/opt
	$(MKDIR_P) $(DESTDIR)$(posixclientdir)/templates/rpm/package/SPECS
	$(MKDIR_P) $(DESTDIR)$(posixclientdir)/templates/rpm/package/BUILD
	$(MKDIR_P) $(DESTDIR)$(posixclientdir)/templates/rpm/package/BUILDROOT
	$(MKDIR_P) $(DESTDIR)$(posixclientdir)/templates/rpm/package/RPMS
	$(MKDIR_P) $(DESTDIR)$(posixclientdir)/templates/rpm/package/SRPMS

	
EXTRA_DIST = $(posixclientscripts) $(posixclientdata) $(installernsi) $(installerdata)

prereqs-deb:
	apt-get update
	apt-get install rpm dpkg

.PHONY = prereqs-deb

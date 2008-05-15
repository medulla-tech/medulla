# Copyright (C) 2006, Adam Cecile for Linbox FAS
# Copyright (C) 2006, Jerome Wax for Linbox FAS
# Copyright (C) 2006, Cedric Delfosse for Linbox FAS
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA



# General Makefile variables
DESTDIR = 
PREFIX = /usr/local
DATADIR = $(PREFIX)/share/mmc
ETCDIR = /etc/mmc
INSTALL = $(shell which install)
CP = $(shell which cp)
CHOWN = $(shell which chown)
CHGRP = $(shell which chgrp)
HTTPDUSER = www-data
SED = $(shell which sed)
RM = $(shell which rm)
APACHE_CONF = confs/apache/mmc.conf

FILESTOINSTALL = graph img includes index.php jsframework logout main_content.php main.php version.php license.php modules

# Default target
all:

debian-package: revision
	sed -i "s/##VERSION##/`cat revision`/" debian/changelog
	sed -i "s/###SVN_VERSION###/`cat revision`/" modules/base/infoPackage.inc.php
	dpkg-buildpackage -b -uc -rfakeroot
	sed -i "s/`cat revision`/###SVN_VERSION###/" modules/base/infoPackage.inc.php
	sed -i "s/`cat revision`/##VERSION##/" debian/changelog

revision:
	# fake SVN revision number if there is none
	# else the revision number is found by BuildBot
	echo -n 100 > "revision"

generate-doc:
	gen-doc/create.sh

clean_mo:
	sh scripts/clean_mo.sh

build_mo:
	sh scripts/build_mo.sh

build_pot:
	sh scripts/build_pot.sh

apache_conf:
	$(SED) 's!###DATADIR###!$(DATADIR)!' $(APACHE_CONF).tmpl > $(APACHE_CONF)

clean: clean_mo
	$(RM) -f $(APACHE_CONF)

install: build_mo apache_conf
	@echo ""
	@echo "Installing mmc-web in $(DESTDIR)$(DATADIR)"
	$(INSTALL) -d -m 755 -o root -g root $(DESTDIR)$(DATADIR)
	$(INSTALL) -d -m 755 -o root -g root $(DESTDIR)$(ETCDIR)
	$(CP) -R $(FILESTOINSTALL) $(DESTDIR)$(DATADIR)
	$(CHOWN) -R root $(DESTDIR)$(DATADIR)
	$(CHGRP) -R root $(DESTDIR)$(DATADIR)
	$(INSTALL) confs/mmc.ini -m 640 -o root -g $(HTTPDUSER) $(DESTDIR)$(ETCDIR)
	$(SED) -i 's!^rootfs[ \t].*$$!rootfs = $(DATADIR)/!' $(DESTDIR)$(ETCDIR)/mmc.ini
	$(SED) -i 's!^rootfsmodules[ \t].*$$!rootfsmodules = $(DATADIR)/modules/!' $(DESTDIR)$(ETCDIR)/mmc.ini
	find $(DESTDIR)$(DATADIR) -type f -name *.po -exec rm -f {} \;

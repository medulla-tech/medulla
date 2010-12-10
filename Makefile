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


# General Makefile variables
DESTDIR =
PREFIX = /usr/local
SBINDIR = $(PREFIX)/sbin
LIBDIR = $(PREFIX)/lib/mmc
ETCDIR = /etc/mmc
INITDIR = /etc/init.d
INSTALL = $(shell which install)
SED = $(shell which sed)

# Python specific variables
PYTHON = $(shell which python)
PYTHON_PREFIX = $(shell $(PYTHON) -c "import sys; print sys.prefix")

# List of files to install
LIBFILESBACKUP = backup-tools/cdlist backup-tools/backup.sh
LIBDIRBACKUP = $(LIBDIR)/backup-tools
SBINFILES = bin/mmc-agent bin/mds-report

# Extension for backuped configuration files
BACKUP = .$(shell date +%Y-%m-%d+%H:%M:%S)

# web part
DATADIR = $(PREFIX)/share/mmc
CP = $(shell which cp)
CHOWN = $(shell which chown)
CHGRP = $(shell which chgrp)
HTTPDUSER = www-data
RM = $(shell which rm)
APACHE_CONF = confs/apache/mmc.conf


FILESTOINSTALL = graph img includes index.php jsframework logout main_content.php main.php version.php license.php modules

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
	sh scripts/build_mo.sh .

build_pot:
	sh scripts/build_pot.sh

apache_conf:
	$(SED) 's!###DATADIR###!$(DATADIR)!' $(APACHE_CONF).tmpl > $(APACHE_CONF)

# Cleaning target
clean: clean_mo
	@echo ""
	@echo "Cleaning sources..."
	@echo "Nothing to do"

# Install everything
install: build_mo apache_conf
	@# Install directories
	@echo ""
	@echo "Move old configuration files to $(DESTDIR)$(ETCDIR)$(BACKUP)"
	-[ -d $(DESTDIR)$(ETCDIR) ] && mv -f $(DESTDIR)$(ETCDIR) $(DESTDIR)$(ETCDIR)$(BACKUP)
	@echo ""
	@echo "Creating directories..."
	$(INSTALL) -d -m 755 -o root -g root $(DESTDIR)$(SBINDIR)
	$(INSTALL) -d -m 755 -o root -g root $(DESTDIR)$(LIBDIR)
	$(INSTALL) -d -m 755 -o root -g root $(DESTDIR)$(LIBDIRBACKUP)
	$(INSTALL) -d -m 755 -o root -g root $(DESTDIR)$(ETCDIR)
	$(INSTALL) -d -m 755 -o root -g root $(DESTDIR)$(PYTHON_PREFIX)

	@echo ""
	@echo "Install python code in $(DESTDIR)$(PYTHON_PREFIX)"
	$(PYTHON) setup.py install --no-compile --prefix $(DESTDIR)$(PYTHON_PREFIX)

	@echo ""
	@echo "Install LIBDIRBACKUP in $(DESTDIR)$(LIBDIRBACKUP)"

	$(INSTALL) $(LIBFILESBACKUP) -m 755 -o root -g root $(DESTDIR)$(LIBDIRBACKUP)

	@echo ""
	@echo "Install SBINFILES in $(DESTDIR)$(SBINDIR)"
	$(INSTALL) $(SBINFILES) -m 755 -o root -g root $(DESTDIR)$(SBINDIR)

	@echo ""
	@echo "Install CONFILES in $(DESTDIR)$(ETCDIR)"
	$(INSTALL) -d -m 755 -o root -g root $(DESTDIR)$(ETCDIR)/agent
	$(INSTALL) -d -m 755 -o root -g root $(DESTDIR)$(ETCDIR)/agent/keys
	$(INSTALL) -d -m 755 -o root -g root $(DESTDIR)$(ETCDIR)/plugins
	$(INSTALL) conf/agent/config.ini -m 600 -o root -g root $(DESTDIR)$(ETCDIR)/agent
	$(INSTALL) conf/agent/keys/* -m 600 -o root -g root $(DESTDIR)$(ETCDIR)/agent/keys
	$(INSTALL) conf/plugins/* -m 600 -o root -g root $(DESTDIR)$(ETCDIR)/plugins
	$(INSTALL) -d -m 755 -o root -g root $(DESTDIR)$(INITDIR)
	$(INSTALL) -m 755 -o root -g root init.d/mmc-agent $(DESTDIR)$(INITDIR)
	$(SED) -i 's!^path[ \t].*$$!path = $(LIBDIR)/backup-tools!' $(DESTDIR)$(ETCDIR)/plugins/base.ini
	$(SED) -i 's!##SBINDIR##!$(SBINDIR)!' $(DESTDIR)$(INITDIR)/mmc-agent

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

include common.mk

$(RELEASES_DIR)/$(TARBALL_GZ):
	mkdir -p $(RELEASES_DIR)/$(TARBALL)/agent $(RELEASES_DIR)/$(TARBALL)/web
	# $(CPA) backup-tools bin Changelog common.mk conf contrib COPYING init.d Makefile mmc setup.py $(RELEASES_DIR)/$(TARBALL)
	$(CPA) agent/bin agent/conf agent/COPYING agent/Changelog agent/contrib agent/backup-tools agent/init.d agent/mmc agent/setup.py web/scripts web/confs $(RELEASES_DIR)/$(TARBALL)
	cd web && $(CPA) $(FILESTOINSTALL) ../$(RELEASES_DIR)/$(TARBALL)
	$(CPA) agent/Changelog agent/COPYING agent/Makefile agent/common.mk $(RELEASES_DIR)/$(TARBALL)/agent
	$(CPA) web/Makefile web/common.mk web/COPYING web/Changelog $(RELEASES_DIR)/$(TARBALL)/web
	$(CPA) Makefile common.mk $(RELEASES_DIR)/$(TARBALL)
	cd $(RELEASES_DIR) && tar -czf $(TARBALL_GZ) $(EXCLUDE_FILES) $(TARBALL); rm -rf $(TARBALL);


docs:
	epydoc mmc

pyflakes:
	pyflakes . bin/mmc-agent

test:
	mkdir tmp
	PYTHONPATH=. python tests/testldap.py
	PYTHONPATH=. python tests/testsamba.py
	PYTHONPATH=. python tests/testproxy.py
	PYTHONPATH=. python tests/testmail.py

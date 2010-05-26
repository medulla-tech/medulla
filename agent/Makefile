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
DESTDIR ?=
PREFIX ?= /usr/local
SBINDIR ?= $(PREFIX)/sbin
BINDIR ?= $(PREFIX)/bin
LIBDIR ?= $(PREFIX)/lib/mmc
ETCDIR ?= /etc/mmc
INITDIR ?= /etc/init.d
INSTALL = $(shell which install)
SED = $(shell which sed)
REINPLACE_CMD ?= $(REINPLACE_CMD)

OWNER ?= root
OGROUP ?= root

# Python specific variables
PYTHON = $(shell which python)
PYTHON_PREFIX = $(shell $(PYTHON) -c "import sys; print sys.prefix")

# List of files to install
LIBFILESBACKUP = backup-tools/cdlist backup-tools/backup.sh
LIBDIRBACKUP = $(LIBDIR)/backup-tools
SBINFILES = bin/mmc-agent bin/mds-report
BINFILES = bin/mmc-helper bin/mmc-password-helper

# Extension for backuped configuration files
BACKUP := .$(shell date +%Y-%m-%d+%H:%M:%S)

all:

# Cleaning target
clean:
	@echo ""
	@echo "Cleaning sources..."
	@echo "Nothing to do"

# Install everything
install:
	@# Install directories
	@echo ""
	@echo "Move old configuration files to $(DESTDIR)$(ETCDIR)$(BACKUP)"
	-[ -d $(DESTDIR)$(ETCDIR) ] && mv -f $(DESTDIR)$(ETCDIR) $(DESTDIR)$(ETCDIR)$(BACKUP)
	@echo ""
	@echo "Creating directories..."
	$(INSTALL) -d -m 755 -o $(OWNER) -g $(OGROUP) $(DESTDIR)$(SBINDIR)
	$(INSTALL) -d -m 755 -o $(OWNER) -g $(OGROUP) $(DESTDIR)$(BINDIR)
	$(INSTALL) -d -m 755 -o $(OWNER) -g $(OGROUP) $(DESTDIR)$(LIBDIR)
	$(INSTALL) -d -m 755 -o $(OWNER) -g $(OGROUP) $(DESTDIR)$(LIBDIRBACKUP)
	$(INSTALL) -d -m 755 -o $(OWNER) -g $(OGROUP) $(DESTDIR)$(ETCDIR)
	$(INSTALL) -d -m 755 -o $(OWNER) -g $(OGROUP) $(DESTDIR)$(PYTHON_PREFIX)

	@echo ""
	@echo "Install python code in $(DESTDIR)$(PYTHON_PREFIX)"
	$(PYTHON) setup.py install --no-compile --prefix $(DESTDIR)$(PYTHON_PREFIX)

	@echo ""
	@echo "Install LIBDIRBACKUP in $(DESTDIR)$(LIBDIRBACKUP)"

	$(INSTALL) -m 755 -o $(OWNER) -g $(OGROUP) $(LIBFILESBACKUP) $(DESTDIR)$(LIBDIRBACKUP)

	@echo ""
	@echo "Install SBINFILES in $(DESTDIR)$(SBINDIR)"
	$(INSTALL) -m 755 -o $(OWNER) -g $(OGROUP) $(SBINFILES) $(DESTDIR)$(SBINDIR)

	@echo ""
	@echo "Install BINFILES in $(DESTDIR)$(BINDIR)"
	$(INSTALL) -m 755 -o $(OWNER) -g $(OGROUP)  $(BINFILES) $(DESTDIR)$(BINDIR)

	@echo ""
	@echo "Install CONFILES in $(DESTDIR)$(ETCDIR)"
	$(INSTALL) -d -m 755 -o $(OWNER) -g $(OGROUP) $(DESTDIR)$(ETCDIR)/agent
	$(INSTALL) -d -m 755 -o $(OWNER) -g $(OGROUP) $(DESTDIR)$(ETCDIR)/agent/keys
	$(INSTALL) -d -m 755 -o $(OWNER) -g $(OGROUP) $(DESTDIR)$(ETCDIR)/plugins
	$(INSTALL) -m 600 -o $(OWNER) -g $(OGROUP) conf/agent/config.ini $(DESTDIR)$(ETCDIR)/agent
	$(INSTALL) -m 600 -o $(OWNER) -g $(OGROUP) conf/agent/keys/* $(DESTDIR)$(ETCDIR)/agent/keys
	$(INSTALL) -m 600 -o $(OWNER) -g $(OGROUP) conf/plugins/* $(DESTDIR)$(ETCDIR)/plugins
	$(INSTALL) -d -m 755 -o $(OWNER) -g $(OGROUP) $(DESTDIR)$(INITDIR)
	$(INSTALL) -m 755 -o $(OWNER) -g $(OGROUP) init.d/mmc-agent $(DESTDIR)$(INITDIR)

ifndef NOCHECKPASSWORD
	$(MAKE) -C openldap-check-password install CC=$(CC) INSTALL=$(INSTALL)
endif

include common.mk

$(RELEASES_DIR)/$(TARBALL_GZ):
	mkdir -p $(RELEASES_DIR)/$(TARBALL)
	$(CPA) backup-tools bin Changelog common.mk conf contrib COPYING init.d Makefile mmc setup.py $(RELEASES_DIR)/$(TARBALL)
	cd $(RELEASES_DIR) && tar -czf $(TARBALL_GZ) $(EXCLUDE_FILES) $(TARBALL); rm -rf $(TARBALL);


docs:
	epydoc mmc

pyflakes:
	pyflakes . bin/*

# This target contains the test suite for MMC core
test:
	PATH=$(PATH):bin/ python tests/mmc-password-helper-test.py

# This target is a convenient way to start MMC core and MDS test suites
test-mds: test
	mkdir -p tmp
	PYTHONPATH=. python tests-mds/testldap.py
	PYTHONPATH=. python tests-mds/testsamba.py
	PYTHONPATH=. python tests-mds/testproxy.py
	PYTHONPATH=. python tests-mds/testmail.py

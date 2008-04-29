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
LIBFILES = bin/add_machine_script
LIBFILESBACKUP = backup-tools/cdlist backup-tools/backup.sh
LIBDIRBACKUP = $(LIBDIR)/backup-tools
SBINFILES = bin/mmc-agent bin/mds-report

# Extension for backuped configuration files
BACKUP = .$(shell date +%Y-%m-%d+%H:%M:%S)

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
	$(INSTALL) -d -m 755 -o root -g root $(DESTDIR)$(SBINDIR)
	$(INSTALL) -d -m 755 -o root -g root $(DESTDIR)$(LIBDIR)
	$(INSTALL) -d -m 755 -o root -g root $(DESTDIR)$(LIBDIRBACKUP)
	$(INSTALL) -d -m 755 -o root -g root $(DESTDIR)$(ETCDIR)
	$(INSTALL) -d -m 755 -o root -g root $(DESTDIR)$(PYTHON_PREFIX)

	@echo ""
	@echo "Install python code in $(DESTDIR)$(PYTHON_PREFIX)"
	$(PYTHON) setup.py install --no-compile --prefix $(DESTDIR)$(PYTHON_PREFIX)

	@echo ""
	@echo "Install LIBFILES in $(DESTDIR)$(LIBDIR)"
	$(INSTALL) $(LIBFILES) -m 755 -o root -g root $(DESTDIR)$(LIBDIR)

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

# Linbox internal target. Will be updated soon.

debian-package: revision
	sed -i "s/##VERSION##/`cat revision`/" debian/changelog
	sed -i "s/###SVN_VERSION###/`cat revision`/" mmc/agent.py
	dpkg-buildpackage -b -uc -rfakeroot
	sed -i "s/`cat revision`/##VERSION##/" debian/changelog
	sed -i "s/`cat revision`/###SVN_VERSION###/" mmc/agent.py

revision:
	# fake SVN revision number if there is none
	# else the revision number is found by BuildBot
	echo -n 100 > "revision"

docs:
	epydoc mmc

test:
	mkdir tmp
	PYTHONPATH=. python tests/testldap.py
	PYTHONPATH=. python tests/testsamba.py
	PYTHONPATH=. python tests/testproxy.py
	PYTHONPATH=. python tests/testmail.py

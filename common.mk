#
# (c) 2008-2009 Mandriva, http://www.mandriva.com/
#
# $Id$
#
# This file is part of Pulse 2, http://pulse2.mandriva.org
#
# Pulse 2 is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Pulse 2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pulse 2; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

export PROJECT_NAME = pulse2
export VERSION = 1.2.2

export RPMBUILD = rpmbuild -ba
export BUILD = $(CURDIR)/build

export TARBALL = $(PROJECT_NAME)-$(VERSION)
export RELEASES_DIR = releases
export TARBALL_BZ = $(TARBALL).tar.bz2
export TARBALL_GZ = $(TARBALL).tar.gz
export EXCLUDE_FILES = --exclude .svn
export CPA = cp -af

export RPM_DIR = $(shell if [ -e ~/.rpmmacros ]; then cat ~/.rpmmacros | grep _topdir | sed "s/^.*\s//"; else echo ""; fi)
export RPM_SPEC = pulse2.spec
export RPM_SPEC_DIR = $(shell if [ "x`which lsb_release >/dev/null 2>/dev/null && echo $$?`" = "x0" ]; then if [ "`lsb_release -sri`" = "RedHatEnterpriseServer 5" ]; then echo "packages/rpm/redhat/el5/" ; elif [ "`lsb_release -sri`" = "RedHatEnterpriseAS 4" ]; then echo "packages/rpm/redhat/el4/" ; elif [ "`lsb_release -sri`" = "RedHatEnterpriseServer 5.1" ]; then echo "packages/rpm/redhat/el5/"; elif [ "`lsb_release -sri`" = "RedHatEnterpriseES 4" ]; then echo "packages/rpm/redhat/el4/"; else echo ""; fi; else if [ "x`cat /etc/release | grep "Corporate Server release 2006.0" | wc -l`" = "x1" ]; then echo "packages/rpm/mandriva/cs4";  elif [ "x`cat /etc/release  | grep "Mandriva Linux Enterprise Server release 5" | wc -l`" = "x1" ]; then echo "packages/rpm/mandriva/mes5"; else echo ""; fi; fi)
export RPM_SPEC_FULLPATH = $(RPM_SPEC_DIR)/$(RPM_SPEC)

rpm: $(RELEASES_DIR)/$(TARBALL_GZ)
ifeq ($(RPM_DIR),)
	echo "RPM_DIR is void, you probably have no .rpmmacros"
else
	@echo "We may exit here if we didn't succeed to detect the distribution"
	exit $(shell if [ -z $(RPM_SPEC_DIR) ]; then echo 1; fi)
	rm -fr $(RPM_DIR)
	mkdir -p $(RPM_DIR)/{SOURCES,SPECS,BUILD,SRPMS,RPMS/i586}
	$(CPA) $(RELEASES_DIR)/$(TARBALL_GZ) $(RPM_DIR)/SOURCES
	cat $(RPM_SPEC_FULLPATH) | sed "s/__VERSION__/$(VERSION)/" > $(RPM_DIR)/SPECS/$(RPM_SPEC)
	$(CPA) $(RPM_SPEC_DIR)/*.diff $(RPM_SPEC_DIR)/*.init $(RPM_DIR)/SOURCES
endif

# build the RPMs in a directory inside the source tree
buildrpms: RPM_DIR = $(BUILD)
buildrpms: rpm
	$(RPMBUILD) --define "_topdir $(RPM_DIR)" $(RPM_DIR)/SPECS/$(RPM_SPEC)


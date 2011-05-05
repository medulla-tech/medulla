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
ACLOCAL_AMFLAGS = -I m4
DISTCHECK_CONFIGURE_FLAGS=--disable-conf-backup

SUBDIRS  = agent web

ldapcontribdir = $(docdir)/contrib/ldap

sysconfdirwarning:
	@if test "${sysconfdir}" != "/etc"; then \
	  echo '###'; \
	  echo '### $${sysconfdir} evaluates to '${sysconfdir}': this is probably not what you want !'; \
	  echo '### You may want to launch ./configure --sysconfdir=/etc.'; \
	  echo '###'; \
	fi

install-data-hook:
	@echo '###'
	@echo '### MMC LDAP schema must be added to your LDAP directory in order for'
	@echo '### mmc-agent to run.'
	@echo '### If using dynamic backend (from OpenLDAP 2.3), schema must be converted'
	@echo '### in LDIF format.'
	@echo '### You can use "mmc-add-schema" to convert and add the schema.'
	@echo '### Schema file is available in: $(ldapcontribdir)'
	@echo '###'

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

EXTRA_DIST = m4

ldapcontribdir = $(datarootdir)/doc/python-mmc-base/contrib/ldap

dist-hook:
	rm -rf `find $(distdir) -name .svn`

confwarning: sysconfdirwarning localstatedirwarning

sysconfdirwarning:
	@if test "${sysconfdir}" != "/etc"; then \
	  echo '###'; \
	  echo '### $${sysconfdir} evaluates to '${sysconfdir}': this is probably not what you want !'; \
	  echo '### You may want to launch ./configure --sysconfdir=/etc.'; \
	  echo '###'; \
	fi

localstatedirwarning:
	@if test "${localstatedir}" != "/var"; then \
	  echo '###'; \
	  echo '### $${localstatedir} evaluates to '${localstatedir}': this is probably not what you want !'; \
	  echo '### You may want to launch ./configure --localstatedir=/var.'; \
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

prereqs:
	if [ -x /usr/bin/apt-get ]; then \
	  $(MAKE) prereqs-deb; \
	elif [ -x /usr/sbin/urpmi ]; then \
	  $(MAKE) prereqs-urpmi; \
	fi

prereqs-urpmi:
	urpmi lsb-release python-sqlalchemy python-twisted php-gd perl-Unix-Syslog openssh-clients \
	  iputils rsync mysql

prereqs-deb:
	apt-get update
	apt-get install python-all lsb-release python-sqlalchemy python-mysqldb \
	  python-ldap python-openssl libapache2-mod-php5 php5-xmlrpc php5-gd \
	  apache2-mpm-prefork ldap-utils slapd

.PHONY = confwarning localstatedirwarning sysconfdirwarning prereqs prereqs-deb prereqs-urpmi

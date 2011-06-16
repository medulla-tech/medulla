# (c) 2011 Mandriva, http://www.mandriva.com
#
# $Id$
#
# This file is part of Mandriva Pulse2 project.
#
# This software is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software.  If not, see <http://www.gnu.org/licenses/>.
#
# Author(s):
#   Jean Parpaillon <jparpaillon@mandriva.com>
#
ACLOCAL_AMFLAGS = -I m4
DISTCHECK_CONFIGURE_FLAGS=--disable-conf-backup

SUBDIRS = web services

backupext = .$(shell date +%Y-%m-%d+%H:%M:%S)

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
	  python-twisted-web perl-modules libsys-syslog-perl openssh-client iputils-ping rsync \
	  mysql-server php5-gd php5-xmlrpc

.PHONY = sysconfdirwarning prereqs prereqs-deb prereqs-urpmi

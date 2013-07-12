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
MAINTAINERCLEANFILES = pci.ids README.pci.ids

EXTRA_DIST = dhcpd.conf pci.ids README.exports README.pci.ids README.tftp-server \
	atftpd.default exports README.dhcpd.conf

pciidsurl = http://pciids.sourceforge.net/v2.2/pci.ids.bz2

configure: pci.ids

pci.ids:
	wget $(pciidsurl)
	bunzip2 pci.ids.bz2
	( echo "Taken from $(pciidsurl)."; \
	  echo "Last update : $(shell date +%Y-%m-%d)" ) > README.pci.ids

.PHONY = configure

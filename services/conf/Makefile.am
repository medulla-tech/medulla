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
SUBDIRS = 
if ENABLE_CONF
SUBDIRS += pulse2 plugins
endif

imagingstatedir = $(localstatedir)/pulse2/imaging
imagingdirs = bootmenus computers custom inventories masters isos archives

examplesdir = @examplesdir@

install-data-local:
	for dir in $(imagingdirs); do \
	  $(mkinstalldirs) $(DESTDIR)$(imagingstatedir)/$$dir; \
	done
	$(MKDIR_P) $(DESTDIR)$(examplesdir)
	for path in `find $(srcdir)/pulse2 $(srcdir)/plugins -name '*.ini'`; do \
	  destpath=`echo $$path | sed 's#'$(srcdir)'/##'`; \
	  $(MKDIR_P) $(DESTDIR)$(examplesdir)/`dirname $$destpath`; \
	  $(INSTALL_DATA) $$path $(DESTDIR)$(examplesdir)/$$destpath; \
	done

# (c) 2011-2012 Mandriva, http://www.mandriva.com
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
# Author(s)
#   Jean Parpaillon <jparpaillon@mandriva.com>
#

mmclogdir = $(localstatedir)/log/mmc/
mmclibdir = $(localstatedir)/lib/mmc/

install-exec-hook:
	install -d -m 0750 $(DESTDIR)$(mmclogdir)
	install -d -m 0750 $(DESTDIR)$(mmclibdir)

SUBDIRS = backup-tools bin init.d contrib man
if ENABLE_CONF
SUBDIRS += conf
endif
if ENABLE_PYTHON
SUBDIRS += mmc
endif

docs: Makefile
	epydoc mmc

pyflakes: Makefile
	pyflakes . bin/*

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
pythonmodules = plugins plugins.dyngroup plugins.dyngroup.querymanager \
	plugins.glpi plugins.glpi.querymanager plugins.glpi.report plugins.imaging \
	plugins.inventory plugins.inventory.provisioning_plugins \
	plugins.inventory.provisioning_plugins.network_to_entity \
	plugins.inventory.querymanager plugins.msc plugins.msc.client \
	plugins.pkgs plugins.backuppc plugins.backuppc.report plugins.pulse2 \
	plugins.update plugins.update.report

# Expands Python modules list with found *.py files in each module given in pythonmodules
modpythondir = $(pythondir)/$(notdir $(realpath $(srcdir)))
nobase_modpython_DATA = $(wildcard $(srcdir)/*.py $(patsubst %,$(srcdir)/%/*.py ,$(subst .,/,$(pythonmodules))))

EXTRA_DIST = $(nobase_modpython_DATA)

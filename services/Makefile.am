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
SUBDIRS = init.d src 3rd_party bin contrib
if ENABLE_CONF
SUBDIRS += conf
endif

pythonmodules = mmc mmc.plugins mmc.plugins.dyngroup mmc.plugins.dyngroup.querymanager \
	mmc.plugins.glpi mmc.plugins.glpi.querymanager mmc.plugins.imaging \
	mmc.plugins.inventory mmc.plugins.inventory.provisioning_plugins \
	mmc.plugins.inventory.provisioning_plugins.network_to_entity \
	mmc.plugins.inventory.querymanager mmc.plugins.msc mmc.plugins.msc.client \
	mmc.plugins.pkgs mmc.plugins.pulse2 \
	pulse2 pulse2.apis pulse2.apis.clients pulse2.database pulse2.database.dyngroup \
	pulse2.database.imaging pulse2.database.inventory pulse2.database.msc \
	pulse2.database.msc.orm pulse2.database.pulse pulse2.imaging \
	pulse2.imaging_server pulse2.inventoryserver pulse2.launcher pulse2.managers \
	pulse2.package_server pulse2.package_server.assign_algo \
	pulse2.package_server.assign_algo.default \
	pulse2.package_server.assign_algo.terminal_type \
        pulse2.package_server.common pulse2.package_server.description \
	pulse2.package_server.imaging pulse2.package_server.imaging.api \
	pulse2.package_server.imaging.common pulse2.package_server.mirror \
	pulse2.package_server.mirror_api pulse2.package_server.package_api_get \
	pulse2.package_server.package_api_put pulse2.package_server.scheduler_api \
	pulse2.package_server.user_package_api pulse2.scheduler \
	pulse2.scheduler.assign_algo pulse2.scheduler.assign_algo.default \
	pulse2.scheduler.assign_algo.ip_class pulse2.scheduler.cache \
	pulse2.scheduler.tracking
# Expands Python modules list with found *.py files in each module given in pythonmodules
nobase_python_PYTHON = $(wildcard $(patsubst %,%/*.py ,$(subst .,/,$(pythonmodules))))

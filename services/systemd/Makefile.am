# (c) 2017 Siveo, http://www.siveo.net
#
# This file is part of Pulse2 project.
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

systemddir = $(localstatedir)/lib/systemd/system
systemdfiles = mmc-agent.service

dist_systemd_DATA = $(systemdfiles)


EXTRA_DIST = $(patsubst %,%.in,$(systemdfiles))

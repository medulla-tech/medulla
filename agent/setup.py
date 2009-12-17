# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2009 Mandriva, http://www.mandriva.com
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

from distutils.core import setup

setup(
    name = 'mmc-agent',
    version = '3.0.0',
    description = 'XML-RPC agent for Mandriva Management Console',
    license = 'GPL',
    url = "http://www.mandriva.com",
    author = "Cedric Delfosse",
    author_email = "cdelfosse@mandriva.com",
    maintainer = "Cedric Delfosse",
    maintainer_email = "cdelfosse@mandriva.com",
    packages = ["mmc", "mmc.support", "mmc.plugins", "mmc.plugins.base",
                "mmc.plugins.ppolicy", "mmc.core", "mmc.core.audit"],
)

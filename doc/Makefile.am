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
SUBDIRS = man user

docsrc = \
	dev/imaging/en/workflow.xml \
	dev/imaging/en/client_content.xml \
	dev/imaging/en/pmrpc.xml \
	dev/imaging/en/image_content.xml \
	dev/inventory/en/database_documentation.xml \
	dev/msc/en/database_documentation.xml \
	dev/dyngroup/en/database_documentation.xml \
	user/msc/en/pulse2_client_check_explained.xml \
	user/msc/en/pulse2_deployment_error_codes_explained.xml \
	user/msc/fr/pulse2_deployment_error_codes_explained.xml \
	conf/en/mmc-python-plugin-glpi-configuration.xml \
	conf/en/mmc-python-plugin-inventory-configuration.xml \
	conf/en/pulse2-inventory-server-configuration.xml \
	conf/en/pulse2-package-server-configuration.xml \
	conf/en/mmc-python-plugin-imaging-configuration.xml \
	conf/en/mmc-python-plugin-msc-configuration.xml \
	conf/en/pulse2-scheduler-configuration.xml \
	conf/en/pulse2-launcher-configuration.xml \
	conf/en/mmc-python-plugin-dyngroup-configuration.xml \
	conf/en/pulse2-imaging-server-configuration.xml \
	conf/en/mmc-python-plugin-pkgs-configuration.xml \
	conf/en/mmc-python-plugin-pulse2-configuration.xml


docpng = \
	dev/inventory/en/database_schema.png \
	dev/msc/en/database_schema.png \
	dev/dyngroup/en/database_schema.png \
	user/msc/en/Deploy_using_MSC-Push_Pull-EN.png \
	user/msc/en/Deploy_using_MSC-Local_Proxy-EN.png \
	user/msc/en/Deploy_using_MSC-Push-EN.png \
	user/msc/en/Deploy_using_MSC-EN.png \
	user/msc/fr/Deploy_using_MSC-Local_Proxy-FR.png \
	user/msc/fr/Deploy_using_MSC-Push-FR.png \
	user/msc/fr/Deploy_using_MSC-Push_Pull-FR.png \
	user/msc/fr/Deploy_using_MSC-FR.png

dochtml = $(patsubst %.xml,%.html,$(docsrc))

nobase_doc_DATA = $(dochtml)

EXTRA_DIST = DocumentConverter.py $(dochtml) $(docpng)

MAINTAINERCLEANFILES = DocumentConverter.py $(dochtml)

include $(top_srcdir)/doc/doc.mk

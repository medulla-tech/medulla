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
SUBDIRS = man

###
### TODO: Old rules, to be automake'd
###
PULSE2_FOLDERS=conf dev install user

html:
	mkdir build
	cp -r $(PULSE2_FOLDERS) build
	-find build -name .svn -exec rm -fr {} \;
	for f in `find build -name \*xml`; do \
		echo $$f; \
		xmlto -o `dirname $$f` -m param.html.xsl xhtml-nochunks $$f; \
		rm -f $$f; \
		tidy -utf8 $${f%.xml}.html > $${f%.xml}.prehtml; \
		./mandrify $${f%.xml}.prehtml $${f%.xml}.html; \
		rm -f $${f%.xml}.prehtml; \
	done

tar: build
	(cd build; tar czf ../pulse2-doc.tar.gz $(PULSE2_FOLDERS))

clean-local:
	rm -fr build

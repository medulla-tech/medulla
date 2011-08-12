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
od2pdf = $(PYTHON) $(top_srcdir)/doc/DocumentConverter.py

%.pdf: %.odt
%.pdf: %.odg
	$(MAKE) start_lo
	$(od2pdf) $< $@

%.png: %.pdf
	convert $< $@

start_lo:
	if ! netstat -napt 2>&1 | grep -q soffice.bin; then \
	  soffice -accept="socket,port=8100;urp;" -headless -nofirststartwizard; \
	  sleep 5; \
	fi

kill_lo:
	pid=$(shell netstat -napt 2>&1 | awk '/soffice.bin/ { print $$7 }' | sed -e 's#/.*$$##'); \
	  if test -n "$$pid"; then \
	    kill $$pid; \
	  fi

%.html: %.xml docbook-xhtml.xsl
	xsltproc --nonet --output $@ $(top_srcdir)/doc/docbook-xhtml.xsl $<

DocumentConverter.py:
	wget -O $@ http://www.artofsolving.com/files/DocumentConverter.py

tar:
	$(MAKE) distdir distdir=build
	cd build && tar czf ../pulse2-doc.tar.gz .

.PHONY: start_lo kill_lo

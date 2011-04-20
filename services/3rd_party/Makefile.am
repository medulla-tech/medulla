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
wol_version = 0.7.1
wol_archive = wol-$(wol_version).tar.gz
wol_src = $(builddir)/wol-src
wol_uri = http://downloads.sourceforge.net/project/wake-on-lan/wol/$(wol_version)/$(wol_archive)

modules = 
if ENABLE_WOL
sbin_SCRIPTS = pulse2-wol
modules += wol
endif

CLEANFILES = pulse2-wol
EXTRA_DIST = $(wol_archive)

configure: $(patsubst %,configure_%,$(modules))

configure_wol: $(wol_src)/Makefile

$(wol_src)/Makefile: $(wol_src)
	cd $(@D) && \
	  ./configure `$(topsrcdir)/config.status --config` --disable-option-checking

$(wol_src): $(wol_archive)
	rm -rf $@
	tmpdir=$(shell mktemp -d --tmpdir=.); \
	  tar xfC $< $$tmpdir; \
	  mv $$tmpdir/* $@; \
	  rm -r $$tmpdir

$(wol_archive):
	if [ -f /usr/src/$@ ]; then \
	  ln -s /usr/src/$@; \
	else; \
	  wget -O $(wol_archive) $(wol_uri); \
	fi

pulse2-wol: $(wol_src)/src/wol
	mv $< $@

$(wol_src)/src/wol:
	$(MAKE) -C $(wol_src)

mostlyclean-local:
	$(MAKE) -C $(wol_src) mostlyclean

clean-local:
	$(MAKE) -C $(wol_src) clean

distclean-local:
	rm -rf $(wol_src)

.PHONY = configure configure_wol

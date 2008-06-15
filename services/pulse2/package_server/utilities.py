#!/usr/bin/python
# -*- coding: utf-8; -*-
#
# (c) 2007-2008 Mandriva, http://www.mandriva.com/
#
# $Id: __init__.py 30 2008-02-08 16:40:54Z nrueff $
#
# This file is part of Pulse 2, http://pulse2.mandriva.org
#
# Pulse 2 is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Pulse 2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pulse 2; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

"""
    Pulse2 Modules
"""

#def encode(obj)
#    if obj.class == Array
#        return obj.map do |v|
#            encode(v)
#        end
#    elsif obj.class == Hash
#        ret = {}
#        obj.each do |k,v|
#            ret[encode(k)] = encode(v)
#        end
#        return ret
#    elsif obj.class == String
#        return obj
#    elsif obj.class == NilClass
#        return ''
#    elsif obj.class == Fixnum
#        return obj
#    else
#        return encode(obj.toH)
#    end
#end
#
#def decodePackages(pkgs)
#    packages = []
#    pkgs.each do |res|
#        pkg = Mandriva::Package.new()
#        pkg.fromH(res)
#        packages << pkg
#    end
#    return packages
#end

import md5
import sys

def sumfile(fobj):
    '''Returns an md5 hash for an object with read() method.'''
    m = md5.new()
    while True:
        d = fobj.read(8096)
        if not d:
            break
        m.update(d)
    return m.hexdigest()

def md5file(fname):
    '''Returns an md5 hash for file fname, or stdin if fname is "-".'''
    if fname == '-':
        ret = sumfile(sys.stdin)
    else:
        try:
            f = file(fname, 'rb')
        except:
            return 'Failed to open file'
        ret = sumfile(f)
        f.close()
    return ret

def md5sum(str):
    return md5.md5(str).hexdigest()

#def humanSize(num)
#    base = 1024
#    unit = 'Bytes'
#
#    ['', 'k', 'M', 'G', 'T', 'P'].each do |i|
#        if num < base then
#            return sprintf('%3.1f %s%s', num, i, unit)
#        end
#        num /= base
#    end
#end


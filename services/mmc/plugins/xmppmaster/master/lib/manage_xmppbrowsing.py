# -*- coding: utf-8; -*-
#
# (c) 2016 siveo, http://www.siveo.net
#
# This file is part of Pulse 2, http://www.siveo.net
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
#
# file manage_xmppbrowsing.py

import os


class xmppbrowsing:
    """
    """

    def __init__(self, defaultdir=None, rootfilesystem=None):
        """
            :param type: Uses this parameter to give a path abs
            :type defaultdir: string
            :type rootfilesystem :string
            :return: Function init has no return
        """
        self.defaultdir = None
        self.rootfilesystem = None
        self.dirinfos = {}

        if defaultdir is not None:
            self.defaultdir = defaultdir
        if rootfilesystem is not None:
            self.rootfilesystem = rootfilesystem
        self.listfileindir()

    def listfileindir1(self, path_abs_current=None):
        if path_abs_current is None or path_abs_current == "":
            if self.defaultdir is None:
                pathabs = os.getcwd()
            else:
                pathabs = self.defaultdir
        else:
            if self.rootfilesystem in path_abs_current:
                pathabs = os.path.abspath(path_abs_current)
            else:
                pathabs = self.rootfilesystem
        self.dirinfos = {
            "path_abs_current": pathabs,
            "list_dirs_current": os.walk(pathabs).next()[1],
            "list_files_current": os.walk(pathabs).next()[2],
            "parentdir": os.path.abspath(os.path.join(pathabs, os.pardir)),
            "rootfilesystem": self.rootfilesystem,
            "defaultdir": self.defaultdir
        }
        return self.dirinfos

    def listfileindir(self, path_abs_current=None):
        if path_abs_current is None or path_abs_current == "":
            if self.defaultdir is None:
                pathabs = os.getcwd()
            else:
                pathabs = self.defaultdir
        else:
            if self.rootfilesystem in path_abs_current:
                pathabs = os.path.abspath(path_abs_current)
            else:
                pathabs = self.rootfilesystem
        list_files_current = os.walk(pathabs).next()[2]
        ff = []
        for t in list_files_current:
            fii = os.path.join(pathabs, t)
            ff.append((t, os.path.getsize(fii)))
        self.dirinfos = {
            "path_abs_current": pathabs,
            "list_dirs_current": os.walk(pathabs).next()[1],
            "list_files_current": ff,
            "parentdir": os.path.abspath(os.path.join(pathabs, os.pardir)),
            "rootfilesystem": self.rootfilesystem,
            "defaultdir": self.defaultdir
        }
        return self.dirinfos


# dirname(path): retourne le répertoire associé au path ;
# basename(path): retourne le nom simple du fichier (extension comprise) ;
# split(path): retourne le couple (répertoire, nom du fichier) ;
# splitdrive(path): retourne le couple (lecteur, chemin du fichier sans le lecteur) ;
# splitext(path): retourne le couple (chemin du fichier sans l'extension, extension) ;
# splitunc(path): retourne le couple (unc, rest) où unc est du type \\h

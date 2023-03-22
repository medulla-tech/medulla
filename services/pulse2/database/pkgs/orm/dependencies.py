# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2013 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

import logging
from sqlalchemy.orm import create_session



""" Class to map pkgs.dependencies to SA
"""

class Dependencies(object):
    """ Mapping between msc.bundle and SA
    """

    def getId(self):
        if self.id is not None:
            return self.id
        else:
            return 0

    def getUuid_package(self):
        if self.uuid_package is not None:
            return self.uuid_package
        else:
            return ""

    def getUuid_dependency(self):
        if self.uuid_dependency is not None:
            return self.uuid_dependency
        else:
            return ""

    def to_array(self):
        """
        This function serialize the object to dict.

        Returns:
            Dict of elements contained into the object.
        """
        return {
            'id' : self.getId(),
            'uuid_package': self.getUuid_package(),
            'uuid_dependency': self.getUuid_dependency()
        }

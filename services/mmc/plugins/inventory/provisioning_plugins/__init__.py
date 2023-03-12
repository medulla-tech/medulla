# SPDX-FileCopyrightText: 2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later


class PluginEntitiesI:

    """
    Interface declaration to implement classes that compute a entities list
    according to user informations.
    """

    def get(self, userinfos):
        """
        Returns a list of entities according to user informations.
        """
        raise Exception("Implement me")

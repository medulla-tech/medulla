# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2010 Mandriva, http://www.mandriva.com
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
# along with MMC; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

"""
Subscription configuration reader classes.
"""

import logging

class SubscriptionConfig:
    """
    Define values needed subscription.
    """

    is_subscribe_done = False
    subs_possible_product_names = ['Pulse 2', 'MDS']
    subs_product_name = ['MDS']
    subs_vendor_name = "Mandriva"
    subs_vendor_mail = "sales@mandriva.com"
    subs_customer_name = ""
    subs_customer_mail = ""
    subs_comment = ""
    subs_users = 0
    subs_computers = 0
    # Support informations
    subs_support_mail = "customer@customercare.mandriva.com"
    subs_support_phone = "0810 LINBOX"
    subs_support_comment = ""

    def getValueMacro(self, section, field, is_int = False):
        try:
            if is_int:
                value = self.getint(section, field)
            else:
                value = self.get(section, field)
            setattr(self, "subs_%s"%field, value)
            logging.getLogger().debug("%s = %s"%(field, str(value)))
        except:
            pass

    def readSubscriptionConf(self, section = 'subscription'):
        """
        Read subscription configuration from the given section
        """
        if not self.has_section(section):
            logging.getLogger().info("This version is a community version.")
            return False
        self.is_subscribe_done = True
        try:
            product_name = self.get(section, 'product_name')
            product_name = product_name.split(' & ')
            self.subs_product_name = []
            for pn in product_name:
                if pn in self.subs_possible_product_names:
                    self.subs_product_name.append(pn)
            if len(self.subs_product_name) == 0:
                self.subs_product_name = ['MDS']
        except:
            pass

        logging.getLogger().info("This version has been subscribed for '%s' products"%(" & ".join(self.subs_product_name)))

        self.getValueMacro(section, "vendor_name")
        self.getValueMacro(section, "vendor_mail")
        self.getValueMacro(section, "customer_name")
        self.getValueMacro(section, "customer_mail")
        self.getValueMacro(section, "comment")
        self.getValueMacro(section, "users", True)
        self.getValueMacro(section, "computers", True)
        self.getValueMacro(section, "support_mail")
        self.getValueMacro(section, "support_phone")
        self.getValueMacro(section, "support_comment")


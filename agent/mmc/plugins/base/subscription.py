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

from mmc.support.mmctools import SingletonN
import logging

logger = logging.getLogger()

class SubscriptionConfig:
    """
    Define values needed subscription.
    """

    is_subscribe_done = False
    subs_possible_product_names = ['Pulse 2', 'CloudPulse',
                                   'MDS', 'Mandriva Directory Server',
                                   'Mandriva Business Server Soho',
                                   'Mandriva Business Server Starter',
                                   'Mandriva Business Server Enterprise',
                                   'Mandriva Business Server Premium']
    subs_product_name = ['MDS']
    subs_vendor_name = "Mandriva"
    subs_vendor_mail = "sales@mandriva.com"
    subs_customer_name = ""
    subs_customer_mail = ""
    subs_comment = ""
    subs_users = 0
    subs_computers = 0
    subs_upgrade_url = ""
    # Support informations
    subs_support_mail = ""
    subs_support_phone = ""
    subs_support_comment = ""

    def getValueMacro(self, section, field, is_int = False):
        try:
            if is_int:
                value = self.getint(section, field)
            else:
                value = self.get(section, field)
            setattr(self, "subs_%s"%field, value)
            logger.debug("%s = %s"%(field, str(value)))
        except:
            pass

    def readSubscriptionConf(self, section = 'subscription'):
        """
        Read subscription configuration from the given section
        """
        if not self.has_section(section):
            logger.info("This version is a community version.")
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

        logger.info("This version has been subscribed for '%s' products"%(" & ".join(self.subs_product_name)))

        self.getValueMacro(section, "vendor_name")
        self.getValueMacro(section, "vendor_mail")
        self.getValueMacro(section, "customer_name")
        self.getValueMacro(section, "customer_mail")
        self.getValueMacro(section, "comment")
        self.getValueMacro(section, "users", True)
        self.getValueMacro(section, "computers", True)
        self.getValueMacro(section, "upgrade_url")
        self.getValueMacro(section, "support_mail")
        self.getValueMacro(section, "support_phone")
        self.getValueMacro(section, "support_comment")


class SubscriptionManager(object):
    __metaclass__ = SingletonN

    def init(self, config):
        self.config = config
        self.config.readSubscriptionConf()
        if self.config.is_subscribe_done:
            try:
                from mmc.plugins.dashboard.manager import DashboardManager
                from mmc.plugins.base.panel import SupportPanel
                DM = DashboardManager()
                DM.register_panel(SupportPanel("support"))
            except ImportError:
                pass

    def getInformations(self, dynamic = False):
        from mmc.plugins.base import ComputerManager, LdapUserGroupControl
        if not self.config.is_subscribe_done:
            return { 'is_subsscribed': False }
        ret = {
            'is_subsscribed':True,
            'product_name':self.config.subs_product_name,
            'vendor_name':self.config.subs_vendor_name,
            'vendor_mail':self.config.subs_vendor_mail,
            'customer_name':self.config.subs_customer_name,
            'customer_mail':self.config.subs_customer_mail,
            'comment':self.config.subs_comment,
            'users':self.config.subs_users,
            'upgrade_url':self.config.subs_upgrade_url,
            'computers':self.config.subs_computers,
            'support_mail':self.config.subs_support_mail,
            'support_phone':self.config.subs_support_phone,
            'support_comment':self.config.subs_support_comment
        }
        if dynamic:
            # Don't count SAMBA admin and nobody users
            userCount = 0
            users = LdapUserGroupControl().search(searchFilter="(&(uid=*)(objectClass=inetOrgPerson))",
                                                  attrs=["uid", "gidNumber"])
            for user in users:
                try:
                    user = user[0][1]
                    if (('uid' in user and not user['uid'] == ['nobody']) and
                            ('gidNumber' in user and not user['gidNumber'] == ['512'])):
                        userCount += 1
                except:
                    pass
            # we add the number of user and computers we have right now
            ret['installed_users'] = userCount
            ret['too_much_users'] = (ret['users'] > 0 and ret['installed_users'] > ret['users'])
            if ComputerManager().isActivated():
                ret['installed_computers'] = ComputerManager().getTotalComputerCount()
            else:
                ret['installed_computers'] = 0
            ret['too_much_computers'] = (ret['computers'] and ret['installed_computers'] > ret['computers'])
        return ret

    def checkUsers(self):
        from mmc.plugins.base import searchUserAdvanced
        if self.config.subs_users == 0:
            return True
        users = searchUserAdvanced()
        if len(users) < self.config.subs_users:
            return True
        return False

    def checkComputers(self):
        from mmc.plugins.base import ComputerManager
        if self.config.subs_computers == 0:
            return True
        if ComputerManager().getTotalComputerCount() < self.config.subs_computers:
            return True
        return False

    def checkAll(self):
        return self.checkUsers() and self.checkComputers()

    def isCommunity(self):
        return not self.config.is_subscribe_done

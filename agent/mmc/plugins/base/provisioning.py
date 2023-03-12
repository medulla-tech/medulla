# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

import logging
import os
from configparser import ConfigParser, NoSectionError, NoOptionError
from twisted.internet import defer
from mmc.support.mmctools import Singleton


class ProvisioningManager(Singleton):
    """
    Class that are able to do provisioning must register to this class.
    """

    components = []

    def __init__(self):
        Singleton.__init__(self)
        self.logger = logging.getLogger()

    def register(self, name, klass):
        """
        @param name: the name of the provisioner
        @param klass: the class name of the provisioner
        """
        self.logger.debug("Registering provisioner %s / %s" % (name, str(klass)))
        self.components.append((name, klass))

    def select(self, names):
        self.logger.debug("Selecting provisioners: " + str(names))
        tmp = []
        if names:
            for name in names.split():
                for n, k in self.components:
                    if n == name:
                        self.logger.info("Selecting provisioner %s / %s" % (n, str(k)))
                        tmp.append((n, k))
        self.components = tmp

    def validate(self):
        ret = True
        tmp = []
        for name, klass in self.components:
            mandatory = True
            try:
                instance = klass()
                valid = instance.validate()
                mandatory = instance.config.mandatory
            except Exception as e:
                self.logger.exception(e)
                valid = False
            if valid:
                self.logger.info("Provisioner %s successfully validated" % name)
                tmp.append((name, klass))
            else:
                self.logger.info("Provisioner %s failed to validate" % name)
                if mandatory:
                    self.logger.error(
                        "Provisioner %s is configured as mandatory, exiting" % name
                    )
                    ret = False
                else:
                    self.logger.info(
                        "Provisioner %s is not configured as mandatory, so going on"
                        % name
                    )
        self.components = tmp
        return ret

    def doProvisioning(self, authtoken):
        """
        Loops on all the provisioners to perform the provisioning.

        @param authtoken: AuthenticationToken containing user informations
        @type authtoken: AuthenticationToken

        @return; Deferred resulting to authtoken
        """

        def _cbError(failure):
            self.logger.exception(failure.getTraceback())
            raise ProvisioningError

        d = None
        if authtoken.isAuthenticated():
            login = authtoken.getLogin()
            for name, klass in self.components:
                self.logger.debug("Provisioning user with %s / %s" % (name, str(klass)))
                instance = klass()
                if login.lower() in instance.config.exclude:
                    self.logger.debug(
                        "User %s is in the exclude list of this provisioner, so skipping it"
                        % login
                    )
                    continue
                if not d:
                    d = defer.maybeDeferred(instance.doProvisioning, authtoken)
                else:
                    d.addCallback(
                        lambda x: defer.maybeDeferred(
                            instance.doProvisioning, authtoken
                        )
                    )
        if d:
            ret = d.addCallback(lambda x: authtoken).addErrback(_cbError)
        else:
            ret = defer.succeed(authtoken)
        return ret


class ProvisionerConfig(ConfigParser):
    """
    Class to handle Provisioner object configuration
    """

    def __init__(self, conffile, section):
        ConfigParser.__init__(self)
        self.conffile = conffile
        self.section = section
        self.setDefault()
        fp = open(self.conffile, "r")
        self.readfp(fp, self.conffile)
        if os.path.isfile(self.conffile + ".local"):
            self.readfp(open(self.conffile + ".local", "r"))
        self.readConf()
        fp.close()

    def readConf(self):
        for option in ["exclude"]:
            try:
                self.__dict__[option] = self.get(self.section, option).lower().split()
            except NoSectionError:
                pass
            except NoOptionError:
                pass
        for option in ["mandatory"]:
            try:
                self.__dict__[option] = self.getboolean(self.section, option)
            except NoSectionError:
                pass
            except NoOptionError:
                pass

    def setDefault(self):
        self.mandatory = True
        self.exclude = []


class ProvisionerI:
    """
    Class for a Provisioner object.

    Instance of this object create or update a user in the MDS main LDAP
    database.
    """

    def __init__(self, conffile, name, klass=ProvisionerConfig):
        """
        @param conffile: provisioner configuration file
        @param name: the provisioner name
        """
        self.logger = logging.getLogger()
        self.config = klass(conffile, "provisioning_" + name)

    def doProvisioning(self, authtoken):
        """
        Take user informations from authtoken, and create or update user
        information in the MDS main LDAP database.
        """
        raise "Must be implemented by the subclass"

    def validate(self):
        """
        Should be implemented by the subclass, as this default method always
        returns False.
        The method should check that the provisioner will work.

        @return: True if the provisioner can be used, else False
        """
        return False


class ProvisioningError:
    """
    Raised by the ProvisioningManager if the provisioning process failed
    """

    pass

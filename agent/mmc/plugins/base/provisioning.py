# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

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
        self.logger.debug(f"Registering provisioner {name} / {str(klass)}")
        self.components.append((name, klass))

    def select(self, names):
        self.logger.debug(f"Selecting provisioners: {str(names)}")
        tmp = []
        if names:
            for name in names.split():
                for n, k in self.components:
                    if n == name:
                        self.logger.info(f"Selecting provisioner {n} / {str(k)}")
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
                self.logger.info(f"Provisioner {name} successfully validated")
                tmp.append((name, klass))
            else:
                self.logger.info(f"Provisioner {name} failed to validate")
                if mandatory:
                    self.logger.error(
                        f"Provisioner {name} is configured as mandatory, exiting"
                    )
                    ret = False
                else:
                    self.logger.info(
                        f"Provisioner {name} is not configured as mandatory, so going on"
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
                self.logger.debug(f"Provisioning user with {name} / {str(klass)}")
                instance = klass()
                if login.lower() in instance.config.exclude:
                    self.logger.debug(
                        f"User {login} is in the exclude list of this provisioner, so skipping it"
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
        with open(self.conffile, "r") as fp:
            self.readfp(fp, self.conffile)
            if os.path.isfile(f"{self.conffile}.local"):
                self.readfp(open(f"{self.conffile}.local", "r"))
            self.readConf()

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
        self.config = klass(conffile, f"provisioning_{name}")

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


class ProvisioningError(BaseException):
    """
    Raised by the ProvisioningManager if the provisioning process failed
    """

    pass

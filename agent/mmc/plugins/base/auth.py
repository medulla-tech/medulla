# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import os
from configparser import ConfigParser, NoSectionError, NoOptionError
from mmc.support.mmctools import Singleton
from mmc.support.config import MMCConfigParser


class AuthenticationManager(Singleton):
    """
    Classes that are able to authenticate users by implementing the
    AuthenticatorI interface must register to this class.
    """

    components = []

    def __init__(self):
        Singleton.__init__(self)
        self.logger = logging.getLogger()

    def register(self, name, klass):
        """
        @param name: the name of the authenticator
        @param klass: the class name of the authenticator
        """
        self.logger.debug(f"Registering authenticator {name} / {str(klass)}")
        self.components.append((name, klass))

    def validate(self):
        ret = True
        tmp = []
        for name, klass in self.components:
            mandatory = True
            try:
                instance = klass()
                mandatory = instance.config.mandatory
                valid = instance.validate()
            except Exception as e:
                self.logger.exception(e)
                valid = False
            if valid:
                self.logger.info(f"Authenticator {name} successfully validated")
                tmp.append((name, klass))
            else:
                self.logger.info(f"Authenticator {name} failed to validate")
                if mandatory:
                    self.logger.error(
                        f"Authenticator {name} is configured as mandatory, exiting"
                    )
                    ret = False
                else:
                    self.logger.info(
                        f"Authenticator {name} is not configured as mandatory, so going on"
                    )
        self.components = tmp
        return ret

    def select(self, names):
        tmp = []
        if names:
            for name in names.split():
                for n, k in self.components:
                    if n == name:
                        self.logger.info(f"Selecting authenticator {n} / {str(k)}")
                        tmp.append((n, k))
        self.components = tmp

    def authenticate(self, user, password, session):
        """
        Loops on the authenticator chains until one successfully authenticates
        the user.

        @return: AuthenticationToken object
        @rtype: AuthenticationToken
        """
        token = AuthenticationToken()
        for name, klass in self.components:
            instance = klass()
            self.logger.debug(f"Try to authenticate user with {name} / {str(klass)}")
            methods = instance.config.method.lower().split()

            if instance.config.authonly:
                if "oidc" in methods:
                    logging.getLogger().error("'OIDC' is present, we bypass Authonly control.")
                elif user.lower() not in instance.config.authonly:
                    self.logger.debug(
                        f"User {user} is not in authonly list for authenticator {name}, skipping."
                    )
                    continue

            if instance.config.exclude:
                if user.lower() in instance.config.exclude:
                    self.logger.debug(
                        f"User {user} is in the exclude list of this authenticator, so we skip it"
                    )

            try:
                token = instance.authenticate(user, password)
            except Exception as e:
                self.logger.exception(e)
                raise AuthenticationError
            self.logger.debug(
                f"Authentication result: {str(token.authenticated)}{str(token.infos)}"
            )
            if token.authenticated:
                # the authentication succeeded
                break
        token.session = session
        return token


class AuthenticatorConfig(MMCConfigParser):
    """
    Class to handle Authenticator object configuration
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
        for option in ["authonly", "exclude"]:
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

        try:
            self.method = self.get("provisioning", "method")
        except NoSectionError:
            pass
        except NoOptionError:
            pass

    def setDefault(self):
        self.authonly = None
        self.mandatory = True
        self.exclude = None


class AuthenticatorI:
    """
    Class for authenticator object.

    Instance of this object is able to authenticate a user with a login and
    password couple.
    """

    def __init__(self, conffile, name, klass=AuthenticatorConfig):
        """
        @param conffile: authenticator configuration file
        @param name: the authenticator name
        """
        self.logger = logging.getLogger()
        self.config = klass(conffile, f"authentication_{name}")

    def authenticate(self, user, password):
        """
        @return: AuthenticationToken object
        @rtype: AuthenticationToken
        """
        raise "Must be implemented by the subclass"

    def validate(self):
        """
        Should be implemented by the subclass, as this default method always
        returns False.
        The method should check that the authenticator will work.

        @return: True if the authenticator can be used, else False
        """
        return False


class AuthenticationToken:
    """
    Store an authentication result

    @ivar authenticated: True if the authenticated succeeded, else False
    @ivar login: the user login
    @ivar infos: User informations (e.g. user LDAP entry)
    @ivar session: User session information (may be used during provisioning)
    """

    def __init__(
        self, authenticated=False, login=None, password=None, infos=None, session=None
    ):
        self.authenticated = authenticated
        self.login = login
        self.infos = infos
        self.password = password
        self.session = None

    def isAuthenticated(self):
        return self.authenticated

    def getInfos(self):
        return self.infos

    def getLogin(self):
        return self.login

    def getPassword(self):
        return self.password

    def getSession(self):
        return self.session


class AuthenticationError(Exception):
    """
    Raised by the AuthenticationManager if the authentication process failed
    """

    pass

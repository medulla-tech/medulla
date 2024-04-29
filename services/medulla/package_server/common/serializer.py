# SPDX-FileCopyrightText: 2007-2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

import pickle
import os
import logging
import medulla.utils


class PkgsRsyncStateSerializer(medulla.utils.Singleton):
    def init(self, common):
        self.logger = logging.getLogger()
        self.logger.debug("Package synchro state serialization, is initializing")
        self.common = common
        self.config = common.config
        self.filename = self.config.package_mirror_status_file
        return self.unserialize()

    def serialize(self):
        self.logger.debug("Package synchro state serialization, serialize")
        # will serialize self.common.dontgivepkgs into file
        try:
            file = open(self.filename, "w")
            pickle.dump(self.common.dontgivepkgs, file)
            file.close()
        except IOError as e:
            if e.errno == 13:
                self.logger.warn(
                    "Package synchro state serialization, serialize failed permission denied while accessing file %s"
                    % (self.filename)
                )
                return False
            elif e.errno == 2:
                self.logger.warn(
                    "Package synchro state serialization, serialize failed, no such file or directory %s"
                    % (self.filename)
                )
                return False
            self.logger.warn(
                "Package synchro state serialization, serialize failed accessing file: %s"
                % (str(e))
            )
            return False
        except Exception as e:
            self.logger.debug(
                "Package synchro state serialization, serialize failed: %s" % (str(e))
            )
            return False
        self.logger.debug("Package synchro state serialization, serialize succeed")
        return True

    def unserialize(self):
        self.logger.debug("Package synchro state serialization, unserialize")
        # will unserialize file into self.common.dontgivepkgs
        try:
            if not os.path.exists(self.filename):
                return False
            file = open(self.filename, "r")
            r = pickle.load(file)
            file.close()
            if isinstance(r, dict):
                self.common.dontgivepkgs = r
                self.logger.debug(
                    "Package synchro state serialization, unserialize succeed"
                )
                return True
            self.logger.debug("Package synchro state serialization, unserialize failed")
            return False
        except IOError as e:
            if e.errno == 13:
                self.logger.warn(
                    "Package synchro state serialization, unserialize failed permission denied while accessing file %s"
                    % (self.filename)
                )
                return False
            elif e.errno == 2:
                self.logger.warn(
                    "Package synchro state serialization, unserialize failed, no such file or directory %s"
                    % (self.filename)
                )
                return False
            self.logger.warn(
                "Package synchro state serialization, unserialize failed accessing file: %s"
                % (str(e))
            )
            return False
        except Exception as e:
            self.logger.debug(
                "Package synchro state serialization, unserialize failed: %s" % (str(e))
            )
            return False

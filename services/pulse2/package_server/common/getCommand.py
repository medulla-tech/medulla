#!/usr/bin/python3
# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import re
import logging
from xml.dom import minidom
from optparse import OptionParser

basename = os.path.basename

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = list(range(8))

# The background is set with 40 plus the number of the color, and the
# foreground with 30

# These are the sequences need to get colored ouput
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"


def formatter_message(message, use_color=True):
    if use_color:
        message = message.replace("$RESET", RESET_SEQ).replace("$BOLD", BOLD_SEQ)
    else:
        message = message.replace("$RESET", "").replace("$BOLD", "")
    return message


COLORS = {
    "WARNING": YELLOW,
    "INFO": WHITE,
    "DEBUG": BLUE,
    "CRITICAL": YELLOW,
    "ERROR": RED,
}


class ColoredFormatter(logging.Formatter):
    def __init__(self, msg, use_color=True):
        logging.Formatter.__init__(self, msg)
        self.use_color = use_color

    def format(self, record):
        levelname = record.levelname
        if self.use_color and levelname in COLORS:
            levelname_color = (
                COLOR_SEQ % (30 + COLORS[levelname]) + levelname + RESET_SEQ
            )
            record.levelname = levelname_color
        return logging.Formatter.format(self, record)


class getCommand(object):
    def __init__(self, file, log=False):
        self.file = file
        self.logger = log and log or logging.getLogger()

    def getStringsData(self):
        """
        Get strings command output as XML string if <?xml is found
        else return all strings datas
        """
        strings_command = 'strings "%s"' % self.file
        strings_data = os.popen(strings_command).read()
        xml_pos = strings_data.find("<?xml")
        if xml_pos != -1:
            strings_data = strings_data[xml_pos:]
            end_pos = strings_data.find("</assembly>") + 11
            return strings_data[:end_pos]
        else:
            self.logger.debug(
                "getStringsData: <?xml tag not found :-(, return all strings_data"
            )
            return strings_data

    def getFileData(self):
        """
        return file command output as dictionary
        """
        file_command = 'file "%s"' % self.file
        file_data = os.popen(file_command).read()
        l = file_data.split(": ")
        n = len(l)
        d = {}

        # this awful piece of code convert file output to a dictionnary
        for i in range(n - 1, 0, -1):
            lcount = len(l[i].split(", "))
            if lcount == 1:
                lcount = 2  # lcount is at least equal to 2 to prevent empty values
            d[l[i - 1].split(", ").pop()] = " ".join(
                l[i].split(", ")[: lcount - 1]
            ).replace("\n", "")

        return d

    def getAdobeCommand(self):
        return '"%s" /sAll' % basename(self.file)

    def getInnoCommand(self):
        return '"%s" /SP /VERYSILENT /NORESTART' % basename(self.file)

    def getNSISCommand(self):
        return '"%s" /S' % basename(self.file)

    def getNSISUpdateCommand(self):
        return '"%s" /S /UPDATE' % basename(self.file)

    def getMozillaCommand(self):
        return '"%s" -ms' % basename(self.file)

    def get7ZipCommand(self):
        return '"%s" /S' % basename(self.file)

    def getMSICommand(self):
        return """msiexec /qn /i "%s" ALLUSERS=1 CREATEDESKTOPLINK=0 ISCHECKFORPRODUCTUPDATES=0 /L install.log

if errorlevel 1 (
  type install.log
  echo "MSI INSTALLER FAILED WITH CODE %%errorlevel%%. SEE LOG ABOVE."
  exit /b %%errorlevel%%
) else (
  del /F install.log
  exit 0
)""" % basename(
            self.file
        )

    def getMSIUpdateCommand(self):
        """
        Command for *.msp files (MSI update packages)
        """
        return 'msiexec /p "%s" /qb REINSTALLMODE="ecmus" REINSTALL="ALL"' % basename(
            self.file
        )

    def getRegCommand(self):
        return 'regedit /s "%s"' % basename(self.file)

    def getDpkgCommand(self):
        return """export DEBIAN_FRONTEND=noninteractive
export UCF_FORCE_CONFFOLD=yes
dpkg -i --force-confdef --force-confold "%s" """ % basename(
            self.file
        )

    def getRpmCommand(self):
        return """if [ ! -e /etc/os-release ]; then
  echo "We are not able to find your linux distibution"
  exit 1
else
  . /etc/os-release
fi

case "$ID" in
  mageia)
    urpmi --auto "%s"
    ;;
  redhat|fedora)
    dnf -y install "%s"
    ;;
  *)
    echo "Your distribution is not supported yet or is not rpm based"
    exit 1
    ;;
esac""" % (
            basename(self.file),
            basename(self.file),
        )

    def getAptCommand(self):
        return 'apt -q -y install "%s" --reinstall' % basename(self.file)

    def getBatCommand(self):
        return 'cmd.exe /c "%s"' % basename(self.file)

    def getShCommand(self):
        return './"%s"' % basename(self.file)

    def getMSUCommand(self):
        """
        Command for *.msu files (Microsoft Update packages)
        """
        return 'wusa.exe "%s" /quiet /norestart' % basename(self.file)

    def getCommand(self):
        self.logger.debug("Parsing %s:" % self.file)

        strings_data = self.getStringsData()
        file_data = self.getFileData()
        self.logger.debug("File data: %s" % file_data)

        if "PE32 executable" in file_data[self.file]:
            # Not an MSI file, maybe InnoSetup or NSIS
            self.logger.debug("%s is a PE32 executable" % self.file)
            installer = None

            # If strings_data startswith <?xml, it is propably
            # standard InnoSetup or NSIS installer
            # else, we check for another custom installer
            # (Adobe, ....)

            if strings_data.startswith("<?xml"):
                xmldoc = minidom.parseString(strings_data)
                identity = xmldoc.getElementsByTagName("assemblyidentity")

                if len(identity) == 0:
                    # if assemblyIdentity don't exists, try assemblyIdentity
                    identity = xmldoc.getElementsByTagName("assemblyIdentity")

                if identity > 0:
                    if identity[0].hasAttribute("name"):
                        installer = identity[0].getAttribute("name")
                        self.logger.debug("Installer: %s" % installer)
            elif "AdobeSelfExtractorApp" in strings_data:
                self.logger.debug("Adobe application detected")
                return self.getAdobeCommand()

            if installer == "JR.Inno.Setup":
                self.logger.debug("InnoSetup detected")
                return self.getInnoCommand()
            elif installer == "Nullsoft.NSIS.exehead":
                self.logger.debug("NSIS detected")
                if re.match(
                    "^pulse2-secure-agent-.*\\.exe$", basename(self.file)
                ) and not re.search("plugin", basename(self.file)):
                    self.logger.debug("Pulse Secure Agent detected, add /UPDATE flag")
                    return self.getNSISUpdateCommand()
                return self.getNSISCommand()
            elif installer == "7zS.sfx.exe":
                self.logger.debug("7zS.sfx detected (Mozilla app inside ?)")
                if not os.system(
                    "grep Mozilla '%s' > /dev/null" % self.file
                ):  # return code is 0 if file match
                    self.logger.debug("Mozilla App detected")
                    return self.getMozillaCommand()
                else:
                    return self.logger.info("I can't get a command for %s" % self.file)
            elif installer == "7-Zip.7-Zip.7zipInstall":
                self.logger.debug("7-Zip detected")
                return self.get7ZipCommand()
            else:
                return self.logger.info("I can't get a command for %s" % self.file)

        elif "Name of Creating Application" in file_data:
            # MSI files are created with Windows Installer, but some apps like
            # Flash Plugin, No
            if (
                "Windows Installer" in file_data["Name of Creating Application"]
                or "Document Little Endian" in file_data[self.file]
            ):
                # MSI files
                if re.match("(x64|Intel);[0-9]+", file_data["Template"]):
                    if self.file.endswith(".msp"):
                        self.logger.debug("%s is a MSI Update file" % self.file)
                        return self.getMSIUpdateCommand()
                    else:
                        self.logger.debug("%s is a MSI file" % self.file)
                        return self.getMSICommand()
                else:
                    return self.logger.info("No Template Key for %s" % self.file)
        elif "Debian binary package" in file_data[self.file] or self.file.endswith(
            ".deb"
        ):
            self.logger.debug("Debian package detected")
            return self.getDpkgCommand()
        elif self.file.endswith(".reg"):
            self.logger.debug("Reg file detected")
            return self.getRegCommand()
        elif self.file.endswith(".bat"):
            self.logger.debug("MS-DOS Batch file detected")
            return self.getBatCommand()
        elif self.file.endswith(".sh"):
            self.logger.debug("sh file detected")
            return self.getShCommand()
        elif self.file.endswith(".rpm"):
            self.logger.debug("rpm file detected")
            return self.getRpmCommand()
        elif self.file.endswith(".msu"):
            self.logger.debug("Windows Update file detected")
            return self.getMSUCommand()
        else:
            return self.logger.info(
                "I don't know what to do with %s (%s)"
                % (self.file, file_data[self.file])
            )


if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option(
        "-d",
        "--debug",
        action="store_true",
        dest="debug",
        default=False,
        help="Print debug messages",
    )
    parser.add_option(
        "--dir",
        dest="dir",
        default=False,
        help="Directory who will be analyzed (default current directory)",
    )

    # Parse and analyse args
    (options, args) = parser.parse_args()
    if options.debug:
        level = logging.DEBUG
    else:
        level = logging.INFO

    if options.dir:
        dir = options.dir
    else:
        dir = "."

    log = logging.getLogger("getCommand")
    log.setLevel(level)
    formatter = ColoredFormatter("%(levelname)-18s %(message)s")
    handler_stream = logging.StreamHandler()
    handler_stream.setFormatter(formatter)
    # handler_stream.setLevel(level)
    log.addHandler(handler_stream)

    for file in os.listdir(dir):
        c = getCommand(file, log)
        command = c.getCommand()
        if command is not None:
            log.info("%s: %s" % (file, command))

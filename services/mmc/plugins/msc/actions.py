# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007 Mandriva, http://www.mandriva.com/
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

import os
import re
import logging

import mmc.plugins.msc.config

from mmc.support.mmctools import shLaunch

def msc_exec(command):
    proc = shLaunch(command)
    return_var = proc.exitCode
    stdout = proc.out
    stderr = proc.err
    output = re.compile('\n').split(stdout)
    return [output, return_var, stdout, stderr]

def msc_ssh(user, ip_addr, command): # TODO better path for annotate_output
    # -tt forces tty allocation so that signals like SIGINT will be properly sent to the remote host
    opts = "-T -R30080:127.0.0.1:80 -o StrictHostKeyChecking=no -o Batchmode=yes -o PasswordAuthentication=no"
    ssh_command = "%s %s ssh %s %s@%s \"%s\"" % (mmc.plugins.msc.MscConfig("msc").annotatepath, mmc.plugins.msc.config.get_keychain(), opts, user, ip_addr, command)
    logging.getLogger().debug("executing |%s|" % ssh_command)
    proc = shLaunch(ssh_command)
    return_var = proc.exitCode
    stdout = proc.out
    stderr = proc.err
# Disabled (FIXME: MAX_LOG_SIZE should be set in msc.ini)
#    if len(stdout) > MAX_LOG_SIZE:
#        stdout = stdout[0:MAX_LOG_SIZE]
#        stdout += "=== LOG MEMORY LIMIT ===\n"

    return [ssh_command, stdout, return_var, stdout, stderr, -1]

def msc_scp(user, ip_addr, source, destination):
    opts = "-o Batchmode=yes -o StrictHostKeyChecking=no -r"
    destination = re.compile(' ').sub('\\ ', destination)
    scp_command = "%s %s scp %s '%s' %s@%s:%s 2>&1" % (\
        mmc.plugins.msc.MscConfig("msc").annotatepath,
        mmc.plugins.msc.config.get_keychain(),
        opts,
        source,
        user,
        ip_addr,
        destination
    )
    logging.getLogger().debug("executing |%s|" % scp_command)
    proc = shLaunch(scp_command)
    return_var = proc.exitCode
    stdout = proc.out
    stderr = proc.err
    output = stdout

    return [scp_command, output, return_var, stdout, stderr, -1]

def mscCopy(session, path_source, files_source, path_destination):
    # * Initialise result variable
    result = {
        "stdout":'',
        "stderr":'',
        "return_var":0
    }
    logger = logging.getLogger()

    if type(files_source) != list:
        files_source = [files_source]

    # This path is used by "scp" command step
    scp_path_destination = path_destination
    logger.debug('Files %s will be copied from "%s" to "%s"' % (files_source, path_source, scp_path_destination))

    # * Make directory step
    logger.debug('Attempted to create "%s"' % scp_path_destination)
    mkdir_command = "test -d '%s' || mkdir -p '%s'" % (scp_path_destination, scp_path_destination)
    (command, output, return_var, stdout, stderr, foo) = msc_ssh(session.user, session.ip, mkdir_command)
    if type(output) == list:
        output = "\n".join(output)
    result["stdout"] += output
    result["return_var"] = return_var
    if return_var != 0: # Error ! I can't make destination directory
        logger.error('Creation of "%s" failed: %s)' % (scp_path_destination, return_var))
        return result
    else:
        logger.debug('"%s" successfuly created' % scp_path_destination)

    # * chmod +x on *.bat and *.exe
    chmod_command = "find %s -iname '*.exe' -or -iname '*.bat' -exec chmod 755 {} \\;" % (path_source) # FIXME: should be up to the user
    msc_exec(chmod_command) # FIXME: should handle errors here ?

    # Iterate over all files
    for filename in files_source:
        myfile = filename.strip('\r') # FIXME: should be processed in command.py ?!
        dirname = os.path.dirname(myfile)
        if dirname == '.':
            dirname = ''
        basename = os.path.basename(myfile)
        logger.debug('Copying file "%s" into "%s"' % (os.path.join(path_source, dirname, basename), scp_path_destination))

        # * Copy files step
        (scp_command, output, return_var, stdout, stderr, foo) = msc_scp(
            session.user,
            session.ip,
            os.path.join(path_source, dirname, basename),
            os.path.join(scp_path_destination, dirname)
        )
        if type(output) == list:
            output = "\n".join(output)

        result["return_var"] = return_var
        result["stdout"] += output

        if return_var != 0: # Error ! I can't copy the file
            logger.debug("Error ! I can't copy the file : %s" % (scp_command))
            logger.debug("Exit value : %s" % (return_var))
        else:
            logger.debug("File successfully copied, command is %s" % (scp_command))
    return result

def mscDelete(session, path_target, files_to_delete):
    # Initialise result variable
    result = {
        "stdout": "",
        "stderr": "",
        "return_var": 0
    }
    logger = logging.getLogger()

    if type(files_to_delete) != list:
        files_to_delete = [files_to_delete]

    path_destination = os.path.join(session.root_path, session.tmp_path.strip('/'), path_target.strip('/'))
    # First step : iterate all files to delete it
    for f in files_to_delete:
        logger.debug('Attempt to delete "%s" from "%s"' % (f, path_destination))
        rm_command = "rm -rf %s" % os.path.join(path_destination, f)
        ret = msc_ssh(session.user, session.ip, rm_command)
        output = ret[1]
        return_var = ret[2]
        if type(output) == list:
            output = "\n".join(output)
        if return_var != 0:
            logger.debug("Warning ! I can't delete file : %s" % rm_command)
            logger.debug("Output value : %s" % output)
            logger.debug("Exit value : %s" % return_var)
            result["return_err"] = return_var
        else:
            logger.debug("File success deleted, command is %s" % rm_command);
        result["stdout"] += output;

    # last step: remove msc's dir
    logger.debug('Attempt to delete MSC main directory ("%s")' % path_destination)
    rm_command = "rmdir %s" % path_destination
    ret = msc_ssh(session.user, session.ip, rm_command)
    output = ret[1]
    return_var = ret[2]
    if type(output) == list:
        output = "\n".join(output)
    result["stdout"] += output
    result["return_err"] = return_var

    return result;

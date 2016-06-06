# -*- coding: utf-8; -*-
#
# (c) 2007-2008 Mandriva, http://www.mandriva.com/
#
# $Id$
#
# This file is part of Pulse 2, http://pulse2.mandriva.org
#
# Pulse 2 is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Pulse 2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pulse 2; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

import re
import popen2
import os       # for adding / removing a ssh key
import signal   # to kill ssh agent
import time
import logging

from pulse2.launcher.config import LauncherConfig

def setupSSHAgent():
    ssh_agent = popen2.Popen4("ssh-agent") # FIXME: should be render configurable
    ssh_agent_auth_sock_re = "^SSH_AUTH_SOCK=([^;]+);";
    ssh_agent_pid_re = "^SSH_AGENT_PID=([^;]+);";

    if not ssh_agent.wait() == 0: # exit code != 0: tell it
        logging.getLogger().warn("launcher %s: Couldn't run the ssh-agent binary, hope you won't need to forward ssh keys !" % (LauncherConfig().name))
        return

    for line in ssh_agent.fromchild.readlines():
        if re.match(ssh_agent_auth_sock_re, line):
            LauncherConfig().ssh_agent_sock = re.search(ssh_agent_auth_sock_re, line).group(1)
        if re.match(ssh_agent_pid_re, line):
            LauncherConfig().ssh_agent_pid = int(re.search(ssh_agent_pid_re, line).group(1))

    if not LauncherConfig().ssh_agent_sock:
        logging.getLogger().info("launcher %s: Successfully run the ssh-agent binary but can't find auth socket" % (LauncherConfig().name))
        return

    os.putenv('SSH_AUTH_SOCK', LauncherConfig().ssh_agent_sock)
    logging.getLogger().info("launcher %s: Successfully run the ssh-agent binary, auth socket is %s" % (LauncherConfig().name, LauncherConfig().ssh_agent_sock))

    for keyname in LauncherConfig().ssh_keys:
        if addPrivKeyToSSHAgent(keyname):
            logging.getLogger().info("launcher %s: Successfuly declared the ssh key '%s' to your ssh agent" % (LauncherConfig().name, keyname))
        else:
            logging.getLogger().warn("launcher %s: Couldn't declare the ssh key '%s' to your ssh agent, hope you won't need to forward it !" % (LauncherConfig().name, keyname))

def killSSHAgent():
    if LauncherConfig().ssh_agent_pid:
        logging.getLogger().info("launcher %s: terminating the ssh-agent binary (pid is %s)" % (LauncherConfig().name, LauncherConfig().ssh_agent_pid))
        try:
            os.kill(LauncherConfig().ssh_agent_pid, signal.SIGTERM)
            time.sleep(1) # give ssh-agent 1 second to exit
            try:
                os.kill(LauncherConfig().ssh_agent_pid, signal.SIGKILL)
                logging.getLogger().warn("launcher %s: Had to kill the ssh-agent binary" % (LauncherConfig().name))
            except OSError: # pid do not exists anymore
                logging.getLogger().info("launcher %s: Successfully terminated the ssh-agent binary" % (LauncherConfig().name))
        except OSError: # agent do not exists anymore
            logging.getLogger().warn("launcher %s: the ssh-agent binary seems already down" % (LauncherConfig().name))

def addPrivKeyToSSHAgent(key_name):
    """
        ask the ssh-agent to keep our key

    """
    if key_name == None or key_name == '':
        key_name = LauncherConfig().ssh_defaultkey

    if key_name not in LauncherConfig().ssh_keys.keys():
        return False

    return (os.system('ssh-add %s 2> /dev/null' % LauncherConfig().ssh_keys[key_name]) == 0)

def removePrivKeyFromSSHAgent(key_name):
    """
        ask the ssh-agent to keep our key

    """
    if key_name == None or key_name == '':
        key_name = LauncherConfig().ssh_defaultkey

    if key_name not in LauncherConfig().ssh_keys.keys():
        return False

    return (os.system('ssh-add -d %s 2> /dev/null' % LauncherConfig().ssh_keys[key_name]) == 0)

# -*- coding: utf-8; -*-
#
# (c) 2009 Mandriva, http://www.mandriva.com/
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
# important consts for overall Pulse 2 consistency

# Encoding, used for a wide bunch of stuff
PULSE2_PREFERRED_ENCODING = 'utf-8'

# separator used by the wrapper
PULSE2_WRAPPER_ARG_SEPARATOR_STR = '·'
PULSE2_WRAPPER_ARG_SEPARATOR_UNICODE = PULSE2_WRAPPER_ARG_SEPARATOR_STR.decode(PULSE2_PREFERRED_ENCODING)
PULSE2_WRAPPER_ARG_SEPARATOR = PULSE2_WRAPPER_ARG_SEPARATOR_UNICODE

# important error code :D
PULSE2_SUCCESS_ERROR    = 0

# pulse 2 errors ranges
PULSE2_UNKNOWN_ERROR_MIN    = 1000
PULSE2_UNKNOWN_ERROR_MAX    = 1999
PULSE2_TARGET_ERROR_MIN     = 2000
PULSE2_TARGET_ERROR_MAX     = 2999
PULSE2_BUNDLE_ERROR_MIN     = 3000
PULSE2_BUNDLE_ERROR_MAX     = 3999
PULSE2_PROXY_ERROR_MIN      = 4000
PULSE2_PROXY_ERROR_MAX      = 4999
PULSE2_PSERVER_ERROR_MIN    = 4000
PULSE2_PSERVER_ERROR_MAX    = 4999


"""
    ####################################################################
    wrapper error codes, see http://pulse2.mandriva.org/ticket/664
    ####################################################################
"""
# standard codes
PULSE2_WRAPPER_ERROR_SUCCESS = PULSE2_SUCCESS_ERROR
PULSE2_WRAPPER_ERROR_FAILURE = 1
PULSE2_WRAPPER_ERROR_PRECHECK = 1
PULSE2_WRAPPER_ERROR_CONNFAILED = 255

# script error client side
PULSE2_WRAPPER_ERROR_SCRIPT_MIN = 1
PULSE2_WRAPPER_ERROR_SCRIPT_MAX = 199

# script error server side; killed by signal
PULSE2_WRAPPER_ERROR_SIGNAL_MIN = 200
PULSE2_WRAPPER_ERROR_SIGNAL_MAX = 231

# reserved codes
PULSE2_WRAPPER_ERROR_RESERVED_MIN = 232
PULSE2_WRAPPER_ERROR_RESERVED_MAX= 239

# script error server side; pre-check failed
PULSE2_WRAPPER_ERROR_PRECHECK_MIN = 240
PULSE2_WRAPPER_ERROR_PRECHECK_MAX = 254

# upon signal reception, this value is added to the signal number
# exit code set to signal_number + PULSE2_WRAPPER_ERROR_SIGNAL_BASE
# in traditionnal unix world, PULSE2_WRAPPER_ERROR_SIGNAL_BASE= 128
# but we wanted a wider script error plage
PULSE2_WRAPPER_ERROR_SIGNAL_BASE = PULSE2_WRAPPER_ERROR_SIGNAL_MIN

# upon pre-check failure, this value is added to the failure reason
# exit code set to exit_code + PULSE2_WRAPPER_ERROR_SIGNAL_BASE
PULSE2_WRAPPER_ERROR_PRECHECK_BASE = PULSE2_WRAPPER_ERROR_PRECHECK_MIN

# exit code pre-check time (including  shifting by PULSE2_WRAPPER_ERROR_PRECHECK_BASE)
PULSE2_WRAPPER_ERROR_PRECHECK_TABLE = {
    'ERROR'     : PULSE2_WRAPPER_ERROR_PRECHECK_BASE + 0,
    'HOSTNAME'  : PULSE2_WRAPPER_ERROR_PRECHECK_BASE + 1,
    'IP'        : PULSE2_WRAPPER_ERROR_PRECHECK_BASE + 2,
    'MAC'       : PULSE2_WRAPPER_ERROR_PRECHECK_BASE + 3
}

"""
    ####################################################################
    Standard codes from workflow
    ####################################################################
"""

PULSE2_UNKNOWN_ERROR        = PULSE2_UNKNOWN_ERROR_MIN

"""
    ####################################################################
    Standard codes for target
    ####################################################################
"""

PULSE2_TARGET_ERROR                 = PULSE2_TARGET_ERROR_MIN
PULSE2_TARGET_NOTENOUGHINFO_ERROR   = PULSE2_TARGET_ERROR_MIN + 1

"""
    ####################################################################
    Standard codes for bundle
    ####################################################################
"""

PULSE2_BUNDLE_ERROR                     = PULSE2_BUNDLE_ERROR_MIN
PULSE2_BUNDLE_MISSING_MANDATORY_ERROR   = PULSE2_BUNDLE_ERROR_MIN + 1

"""
    ####################################################################
    Standard codes for proxy
    ####################################################################
"""

PULSE2_PROXY_ERROR                      = PULSE2_PROXY_ERROR_MIN
PULSE2_PROXY_WAITINGFORDEAD_ERROR       = PULSE2_PROXY_ERROR_MIN + 1

"""
    ####################################################################
    Standard codes for pserver
    ####################################################################
"""

PULSE2_PSERVER_ERROR                        = PULSE2_PSERVER_ERROR_MIN
PULSE2_PSERVER_PACKAGEISUNAVAILABLE_ERROR   = PULSE2_PSERVER_ERROR_MIN + 1
PULSE2_PSERVER_GETFILEURIFROMPACKAGE_ERROR  = PULSE2_PSERVER_ERROR_MIN + 2
PULSE2_PSERVER_GETFILEURIFROMPACKAGE_F_ERROR= PULSE2_PSERVER_ERROR_MIN + 3
PULSE2_PSERVER_MIRRORFAILED_CONNREF_ERROR   = PULSE2_PSERVER_ERROR_MIN + 4
PULSE2_PSERVER_FMIRRORFAILED_CONNREF_ERROR  = PULSE2_PSERVER_ERROR_MIN + 5
PULSE2_PSERVER_MIRRORFAILED_404_ERROR       = PULSE2_PSERVER_ERROR_MIN + 6
PULSE2_PSERVER_FMIRRORFAILED_404_ERROR      = PULSE2_PSERVER_ERROR_MIN + 7

PULSE2_PSERVER_MESSAGES_MIN                 = PULSE2_PSERVER_ERROR_MIN + 500
PULSE2_PSERVER_ISAVAILABLE_FALLBACK         = PULSE2_PSERVER_MESSAGES_MIN + 8
PULSE2_PSERVER_ISAVAILABLE_MIRROR           = PULSE2_PSERVER_MESSAGES_MIN + 9



"""
    some known states
"""

""" Commands in this state are definitively terminated """

PULSE2_FAILURE_STATE = [
    'failed',
    'over_timed'
]

PULSE2_SUCCESS_STATE = [
    'done'
]

PULSE2_TERMINATED_STATES = [
] + PULSE2_FAILURE_STATE + PULSE2_SUCCESS_STATE

""" Commands in this state won't be preempted """
PULSE2_UNPREEMPTABLE_STATES = [
    'stop',
    'stopped',
    'pause',
    'paused'
] + PULSE2_TERMINATED_STATES

""" Commands in these states are executed somewhere """
PULSE2_PROGRESSING_STATES = [
    'upload_in_progress',
    'execution_in_progress',
    'delete_in_progress',
    'inventory_in_progress'
    'reboot_in_progress',
    'halt_in_progress',
]

""" Commands in these states are running somewhere (WOL is, says, 'special') """
PULSE2_RUNNING_STATES = [
    'wol_in_progress'
] + PULSE2_PROGRESSING_STATES

""" Commands in these states have all passed the 'inventory' stage """
PULSE2_POST_INVENTORY_STATES = [
    'reboot_in_progress',
    'reboot_done',
    'reboot_failed',
    'halt_in_progress',
    'halt_done',
    'halt_failed'
] + PULSE2_TERMINATED_STATES

""" Commands in these states have all passed the 'halt' stage """
PULSE2_POST_HALT_STATES = [
] + PULSE2_TERMINATED_STATES


PULSE2_FAILED_NON_FINAL_STATES = [
    'wol_failed',
    'upload_failed',
    'execution_failed',
    'delete_failed',
    'inventory_failed',
    'reboot_failed',
    'halt_failed'
    ]

""" The stages a command will cross by, KEEP IN THAT ORDER ! """
PULSE2_STAGES = [
    'awoken',
    'uploaded',
    'executed',
    'deleted',
    'inventoried',
    'rebooted',
    'halted'
]

""" The stages prefixes KEEP IN THAT ORDER ! KEEP IN SYNC WITH PREVIOUS ! """
PULSE2_STATE_PREFIXES = [
    'wol',
    'upload',
    'execution',
    'delete',
    'inventory',
    'reboot',
    'halt'
]
PULSE2_STAGE_TODO               = 'TODO'
PULSE2_STAGE_WORK_IN_PROGRESS   = 'WORK_IN_PROGRESS'
PULSE2_STAGE_DONE               = 'DONE'
PULSE2_STAGE_IGNORED            = 'IGNORED'
PULSE2_STAGE_FAILED             = 'FAILED'


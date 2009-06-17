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

# wrapper error codes, see http://pulse2.mandriva.org/ticket/664
# standard codes
PULSE2_WRAPPER_ERROR_SUCCESS = 0
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

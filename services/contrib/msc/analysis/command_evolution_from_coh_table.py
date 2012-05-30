#!/usr/bin/python
#
# (c) 2009 Mandriva, http://www.mandriva.com/
#
# $Id: command_evolution_from_coh_table.py 831 2009-12-07 09:24:39Z nrueff $
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

"""

"""

import sys
import time
import re
import datetime
from optparse import OptionParser
from sqlalchemy import *

parser = OptionParser()
parser.add_option("-f", "--format", dest="format", help="Output format (default : human)", metavar="csv|human", default="human")
parser.add_option("--created-after", dest="created_after", help="Min creation date (defaut : yesterday, same hour)", metavar="YYYY-MM-DD HH:MM:SS", default=time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time()-87400)))
parser.add_option("--created-before", dest="created_before", help="Max creation date (defaut : now)", metavar="YYYY-MM-DD HH:MM:SS", default=time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())))
parser.add_option("--started-after", dest="started_after", help="Min execution date (defaut : same value as --created-after)", metavar="YYYY-MM-DD HH:MM:SS", default=None)
parser.add_option("--started-before", dest="started_before", help="Max execution date (defaut : same value as --created-before)", metavar="YYYY-MM-DD HH:MM:SS", default=None)
parser.add_option("-u", "--uri", dest="uri", help="MySQL URI (defaut : mysql://root@127.0.0.1/msc)", metavar="mysql://<user>:<password>@<host>/<base>", default='mysql://root@127.0.0.1/msc')
parser.add_option("--min", dest="min", help="Minimum targets to be displayed (default : 0)", metavar="number", default=0, type=int)
parser.add_option("--domain", dest="domain", help="Domain regex (default : [^\.]+$)", metavar="regex", default='[^\.]+$')
parser.add_option("--docs", dest="docs", help="Show me doc about fields", action="store_true", default=False)

(options, args) = parser.parse_args()

if not options.started_after :
    options.started_after = options.created_after
if not options.started_before :
    options.started_before = options.created_before

if options.docs :
    print "Fields signification"
    print " - Name : The name of the command"
    print " - Creator : The creator of the command"
    print " - Created : The date of creation"
    print " - Domains : The domains found in that command"
    print " - Hosts : Hosts involved in this command, splitted as follow"
    print "   + Scheduled : Hosts which have not yet been touched"
    print "This is neither a success or a failure, they have not been"
    print "processeed."
    print "   + Rescheduled : Hosts which have known at least one"
    print "failure"
    print "This is neither a success or a failure, but are not being"
    print "processed ATM : as failure may be temporary or definitive,"
    print "keep an eye on them : previous failure may be due to"
    print "anything."
    print "   + In Progress : Hosts which are currently working"
    print "It those hosts seems to work since a long time (more than"
    print "24 hours), you should stop them using the interface.."
    print "   + Stopped : Hosts which have been stopped BY THE USER"
    print "Those copmmands can still be a success or a failure, if the"
    print "user start them again"
    print "   + Neutralized : Hosts which have been stopped BY THE SCHEDULER"
    print "Thoses commands were obviously misbehaving - which should"
    print "not arrive - you can consider thoses as a failure"
    print "  + Over Timed : Hosts running out of time"
    print "They were simply running out of time"
    print "  + Success : Hosts which have been successfully deployed"
    print "Nothing more to add : deployment went as expected"
    print "  + Failure : Hosts which have consummed all attempts, but"
    print "don't blame Pulse 2 yet, details are following"
    print "     --> Not Enough Info : The system had not enought information to deploy"
    print "This is generally caused by an out-ot-sync inventory"
    print "datase, or a resolv mechanism (DNS) issue."
    print "     --> Broken Bundle : This commands depends on a failed one"
    print "You should seek out why the dependency do fail."
    print "     --> Package Unavailable : The required package is not on your server anymore"
    print "This is generally because the package was removed from"
    print "the server before the host can get it. This may also"
    print "be due to network issues."
    print "     --> Package Modified : The required package has been modified on your server"
    print "This is generally because the package was modified on"
    print "the server before the host can get it. This may also"
    print "be due to network issues."
    print "     --> Timeout : The script was killed has it took too much time."
    print "Your script is probably broken, and waiting for event"
    print "(keypress for example) which won't occur in silent mode"
    print "     --> Target broken : The target is probably broken."
    print "It may be already crashed."
    print "     --> Mac Mismatch : Issue when controlling the target MAC address."
    print "Also related to an out-of-sync inventory database"
    print "     --> Unreachable : Issue when attempting to contact the host."
    print "The host can be down. Or be firewalled. Or without the agent installed."
    print "     --> Connection issue : Issue while talking to the host."
    print "Issue cause is unknown. Network issue ? Scheduler dying ?"
    print "     --> Delete : Delete failed."
    print "The deletion raised an error, this generaly occurs when"
    print "the install script screw the temporary folder. Script is"
    print "probably broken."
    print "     --> Inventory : Inventory failed."
    print "The inventory command do failed. Please check those hosts;"
    print "the inventory may be misconfigured."
    print "     --> Halt : Halt failed."
    print "The halt command do failed. Please check those hosts;"
    print "it is possible that something prevent the computer to be"
    print "shut down."
    print "     --> Script : Script failed."
    print "The script raised an error you told it to raise (in other"
    print "words : you expected this error; based on this code, you"
    print "should now know what to do with those clients."
    print "     --> Execution : Execution failed."
    print "The script raised an INTERNAL error; you should have a"
    print "look to see why it failed"
    print "     --> Precheck : The precheck failed, no idea why."
    print "The target is probably crached."
    print " - Results : the ammounts, categorized"
    print "  + To Do : deployments till to be done; contains 'Scheduled', 'Rescheduled'"
    print "  + Doing : deployments in progress; contains 'In Progress'"
    print "  + Delayed : deployments postponed by user or scheduler  action, contains 'Stopped', 'Neutralized'"
    print "  + Done : deployments finished on success, contains 'Success'"
    print "  + Failed : deployments finished on error, contains the following field"
    print "  + Target : deployment which have failed since the target was deficient, contains 'Not Enough Info', 'Target broken', 'Halt', 'Mac Mismatch', 'Unreachable', 'Inventory', 'Execution', 'Precheck'"
    print "  + Plan : deployment which have failed since the deployment plan lacked information, contains 'Over Timed', 'Script', 'Broken Bundle', 'Delete', 'Timeout', 'Package Modified'"
    print "  + Infra : deployment which have failed because of some flaws in the infrastructure, contains 'Package Unavailable', 'Connection issue'"
    sys.exit(0)

# create connection
mysql_db = create_engine(options.uri)
metadata = MetaData(mysql_db)

# declare tables
command_table = Table('commands',
                metadata,
                autoload = True)
coh_table = Table('commands_on_host',
                metadata,
                autoload = True)
history_table = Table("commands_history",
                metadata,
                autoload = True)

# gather commands
commandData = command_table.select().where(
            and_(
                command_table.c.creation_date < options.created_before,
                command_table.c.creation_date > options.created_after,
            )
    ).execute().fetchall()

def getStruct():
    struct = dict()
    struct['creator'] = ''
    struct['creation_date'] = datetime.datetime
    struct['name'] = ''
    struct['coh'] = dict()
    struct['states'] = dict()
    struct['Scheduled'] = 0
    struct['Rescheduled'] = 0
    struct['In Progress'] = {
        'upload_in_progress'    : 0,
        'execution_in_progress' : 0,
        'delete_in_progress'    : 0,
        'inventory_in_progress' : 0,
        'wol_done'              : 0
    }
    struct['Stopped'] = 0
    struct['Neutralized'] = 0
    struct['Over Timed'] = 0
    struct['Fatal'] = {
        'not_enought_info'      : 0,
        'bundle_broken'         : 0,
        'package_unavailable'   : 0,
        'package_modified'      : 0,
        'timeout'               : 0,
        'mac_mismatch'          : 0,
        'target_broken'         : 0,
        'unreachable'           : 0,
        'conn_issue'            : 0,
        'precheck'              : 0,
        'delete'                : 0,
        'inventory'             : 0,
        'halt'                  : 0,
        'script'                : 0,
        'execution'             : 0,
        'other'                 : 0
    }
    struct['Results'] = {
        "To Do"     : 0,
        "Doing"     : 0,
        "Delayed" : 0,
        "Done"      : 0,
        "Target"    : 0,
        "Plan"      : 0,
        "Infra"     : 0,
        "Others"    : 0,
    }
    struct['Success'] = 0
    struct['Other'] = 0
    struct['Domains'] = list()
    struct['Commands'] = list()

    return struct

data = dict()

for command in commandData:
    cohData = coh_table.select().where(
            and_(
                or_(
                    and_(
                        coh_table.c.start_date < options.started_before,
                        coh_table.c.start_date > options.started_after,
                    ),
                    coh_table.c.start_date == None,
                ),
                coh_table.c.fk_commands == command['id']
            )
        ).execute().fetchall()
    dataCommand = getStruct()

    dataCommand['name'] = command['title']
    dataCommand['creator'] = command['creator']
    dataCommand['creation_date'] = command['creation_date']
    dataCommand['max_connection_attempt'] = command['max_connection_attempt']
    dataCommand['start_date'] = command['start_date']
    dataCommand['end_date'] = command['end_date']
    dataCommand['fk_bundle'] = command['fk_bundle']

    for coh in cohData :
        # try to guess domain
        matched = re.search(options.domain, coh['host'])
        if matched :
            if matched.group(0) not in dataCommand['Domains'] :
                dataCommand['Domains'].append(matched.group(0))
        else :
            continue

        historyData = history_table.select().where(
                history_table.c.fk_commands_on_host == coh['id']
            ).execute().fetchall()

        dataCommand['coh'][coh['id']] = list()

        for history in historyData :
            dataCommand['coh'][coh['id']].append([
                time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(float(history['date']))),
                history['error_code'],
                history['stdout'],
                history['state']],
            )

        if not coh['current_state'] in dataCommand['states']:
            dataCommand['states'][coh['current_state']] = 0
        dataCommand['states'][coh['current_state']] += 1

        if coh['current_state'] in ['scheduled']:
            # see how much time the command has been processed
            number_of_try = "%d" % (command['max_connection_attempt'] - coh['attempts_left'])

            if command['max_connection_attempt'] == coh['attempts_left'] : # never processed => Scheduled
                dataCommand['Scheduled'] += 1
                dataCommand['Results']['To Do'] += 1
            else : # not the case => Rescheduled
                dataCommand['Rescheduled'] += 1
                dataCommand['Results']['To Do'] += 1
        elif coh['current_state'] in ['upload_failed', 'execution_failed', 'delete_failed', 'halt_failed']:
            if coh['attempts_left'] > 0 :
                dataCommand['Rescheduled'] += 1
                dataCommand['Results']['To Do'] += 1
            else:
                dataCommand['Other'] += 1
                dataCommand['Results']['Others'] += 1
        elif coh['current_state'] in ['wol_done', 'upload_in_progress', 'execution_in_progress', 'delete_in_progress', 'inventory_in_progress'] :
            # increment corresponding counter
            dataCommand['In Progress'][coh['current_state']] += 1
            dataCommand['Results']['Doing'] += 1

        elif coh['current_state'] in ['stop', 'stopped'] :
            # user action : next_launch_date = "2031-12-31 23:59:59"
            # scheduler action : other cases
            if coh['next_launch_date'] == datetime.datetime(2031, 12, 31, 23, 59, 59):
                dataCommand['Stopped'] += 1
                dataCommand['Results']['Delayed'] += 1
            else :
                dataCommand['Neutralized'] += 1
                dataCommand['Results']['Delayed'] += 1

        elif coh['current_state'] in ['over_timed'] :
            # increment counter
            dataCommand['Over Timed'] += 1
            dataCommand['Results']['Plan'] += 1

        elif coh['current_state'] in ['done'] :
            # increment success counters
            dataCommand['Success'] += 1
            dataCommand['Results']['Done'] += 1

        elif coh['current_state'] in ['failed'] :
            # search reason of failure : get last line of logs with a non-zero error

            last_error = 0
            last_entry = None
            last_message = ''
            last_state = ''
            
            prev_error = 0
            prev_entry = None
            prev_message = ''
            prev_state = ''

            for i in dataCommand['coh'][coh['id']]:
                if i[1] != 0 :
                    (prev_error, prev_entry, prev_message, prev_state) = (last_error, last_entry, last_message, last_state)
                    if last_entry == None :
                        (last_entry, last_error, last_message, last_state) = i
                    elif last_entry <= i[0]:
                        (last_entry, last_error, last_message, last_state) = i

            if last_error == 2001 :
                last_failed = 'not_enought_info'
                dataCommand['Results']['Target'] += 1
            elif last_error == 3001 :
                last_failed = 'bundle_broken'
                dataCommand['Results']['Plan'] += 1
            elif re.findall('E: md5sum: WARNING:', last_message) and last_state == 'upload_failed':
                last_failed = 'package_modified'
                dataCommand['Results']['Plan'] += 1
            elif re.findall('E: md5sum: WARNING:', prev_message) and prev_state == 'upload_failed':
                last_failed = 'package_modified'
                dataCommand['Results']['Plan'] += 1
            elif last_error == 4001 :
                last_failed = 'package_unavailable'
                dataCommand['Results']['Infra'] += 1
            elif last_error == 4002 :
                last_failed = 'package_modified'
                dataCommand['Results']['Plan'] += 1
            elif last_error == 209 :
                last_failed = 'timeout'
                dataCommand['Results']['Plan'] += 1
            elif last_error == 243 :
                last_failed = 'mac_mismatch'
                dataCommand['Results']['Target'] += 1
            elif last_error == 255 :
                last_failed = 'unreachable'
                dataCommand['Results']['Target'] += 1
            elif re.findall('PRE-COMMAND FAILED CLIENT SIDE: exitcode = 1', last_message) :
                last_failed = 'precheck'
                dataCommand['Results']['Target'] += 1
            elif re.findall('PRE-COMMAND FAILED CLIENT SIDE: exitcode = 66', last_message) and last_error == 66 and last_state == 'upload_failed':
                last_failed = 'target_broken'
                dataCommand['Results']['Target'] += 1
            elif re.findall('PRE-COMMAND FAILED CLIENT SIDE: exitcode = 45', last_message) and last_error == 45 and last_state == 'upload_failed':
                last_failed = 'target_broken'
                dataCommand['Results']['Target'] += 1
            elif re.findall('PRE-COMMAND FAILED CLIENT SIDE: exitcode = 23', last_message) and last_error == 23 and last_state == 'upload_failed':
                last_failed = 'target_broken'
                dataCommand['Results']['Target'] += 1
            elif re.findall('PRE-COMMAND FAILED CLIENT SIDE: exitcode = 253', last_message) and last_error == 253:
                last_failed = 'target_broken'
                dataCommand['Results']['Target'] += 1
            elif re.findall('fork: Resource temporarily unavailable', last_message) and last_error == 128:
                last_failed = 'target_broken'
                dataCommand['Results']['Target'] += 1
            elif last_error == 57 and last_state == 'upload_failed':
                last_failed = 'target_broken'
                dataCommand['Results']['Target'] += 1
            elif re.findall('/bin/wget: Permission denied', last_message) and last_error == 126 and last_state == 'upload_failed':
                last_failed = 'target_broken'
                dataCommand['Results']['Target'] += 1
            elif re.findall('wget: command not found', last_message) and last_error == 127 and last_state == 'upload_failed':
                last_failed = 'target_broken'
                dataCommand['Results']['Target'] += 1
            elif last_state == 'delete_failed':
                last_failed = 'delete'
                dataCommand['Results']['Plan'] += 1
            elif last_state == 'inventory_failed':
                last_failed = 'inventory'
                dataCommand['Results']['Target'] += 1
            elif last_state == 'halt_failed':
                last_failed = 'halt'
                dataCommand['Results']['Target'] += 1
            elif last_state == 'upload_failed' and last_error == 1 and len(last_message.splitlines()) :
                last_failed = 'conn_issue'
                dataCommand['Results']['Infra'] += 1
            elif last_state == 'execution_failed' and last_error >= 100 and last_error < 200 :
                last_failed = 'script'
                dataCommand['Results']['Plan'] += 1
            elif last_state == 'execution_failed' and last_error >= 1 and last_error < 100 :
                last_failed = 'execution'
                dataCommand['Results']['Target'] += 1
            else:
                #MDV/NR print coh['id']
                dataCommand['Other'] += 1
                dataCommand['Results']['Others'] += 1
                continue

            # increment failure counters
            dataCommand['Fatal'][last_failed] += 1

        else:
            #MDV/NR print coh['id']
            dataCommand['Other'] += 1
            dataCommand['Results']['Others'] += 1
            continue


    data[command['id']] = dataCommand

if options.format == 'csv' :
    print ';'.join((
        'ID',
        'Name',
        'Creator',
        'Created',
	    'Start',
	    'End',
        'Domains',
        'Total',
        "To Do",
        'Scheduled',
        'Rescheduled',
        "Doing",
        'In Progress',
        "Done",
        'Success',
        "Delayed",
        'Stopped',
        'Neutralized',
        "Not Done",
        "Target",
        'Not Enough Info',
        'Target Broken',
        'Halt',
        'Mac Mismatch',
        'Unreachable',
        'Inventory',
        'Execution',
        'Precheck',
        'Plan',
        'Over Timed',
        'Script',
        'Broken Bundle',
        'Delete',
        'Timeout',
        'Package Modified',
        "Infra",
        'Package Unavailable',
        'Connexion issue'
    ))

def print_human(label, value, total, subtotal):
    fmt = "{0:.<35} : {1:4d} (abs.: {2:3d} %, rel: {4:3d} %)"
    if value == 0:
        return
    if subtotal !=0 and total != 0:
        print fmt.format(label, value, 100 * value / total, total, 100 * value / subtotal, subtotal)
    else:
        print fmt.format(label, value, 0, total, 0, subtotal)
    
ids_command = data.keys()
ids_command.sort()
for id_command in ids_command:
    command = data[id_command]
    if len(command['coh']) > options.min:
        if options.format == 'human':
            print "================== [%s] ==================" % id_command
            print "%s : %s" % ('Name    ', command['name'])
            print "%s : %s" % ('Creator ', command['creator'])
            print "%s : %s" % ('Created ', command['creation_date'])
            print "%s : %s" % ('Start   ', command['start_date'])
            print "%s : %s" % ('End     ', command['end_date'])
            print "%s : %s" % ('Domains ', command['Domains'])
            print "------------------ Results ------------------"
            print_human('Total', len(command['coh']), len(command['coh']), len(command['coh']))
            print_human('    To Do ', command['Results']['To Do'], len(command['coh']), len(command['coh']))
            print_human('        Scheduled ', command['Scheduled'], len(command['coh']), command['Results']['To Do'])
            print_human('        Rescheduled ', command['Rescheduled'], len(command['coh']), command['Results']['To Do'])
            print_human('    Doing ', command['Results']['Doing'], len(command['coh']), len(command['coh']))
            print_human('        In Progress ', sum(command['In Progress'].values()), len(command['coh']), command['Results']['Doing'])
            print_human('        Delayed ', command['Results']['Delayed'], len(command['coh']), command['Results']['Doing'])
            print_human('        Stopped ', command['Stopped'], len(command['coh']), command['Results']['Doing'])
            print_human('        Neutralized ', command['Neutralized'], len(command['coh']), command['Results']['Doing'])
            print_human('    Done ', command['Results']['Done'], len(command['coh']), len(command['coh']))
            print_human('        Success ', command['Success'], len(command['coh']), command['Results']['Done'])
            print_human('    Failed ', command['Results']['Target'] + command['Results']['Plan'] + command['Results']['Infra'], len(command['coh']), len(command['coh']))
            print_human('        Target ', command['Results']['Target'], len(command['coh']), command['Results']['Target'] + command['Results']['Plan'] + command['Results']['Infra'])
            print_human('            Not Enough Info ', command['Fatal']['not_enought_info'], len(command['coh']), command['Results']['Target'])
            print_human('            Target broken ', command['Fatal']['target_broken'], len(command['coh']), command['Results']['Target'])
            print_human('            Halt ', command['Fatal']['halt'], len(command['coh']), command['Results']['Target'])
            print_human('            Mac Mismatch ', command['Fatal']['mac_mismatch'], len(command['coh']), command['Results']['Target'])
            print_human('            Unreachable ', command['Fatal']['unreachable'], len(command['coh']), command['Results']['Target'])
            print_human('            Inventory ', command['Fatal']['inventory'], len(command['coh']), command['Results']['Target'])
            print_human('            Execution ', command['Fatal']['execution'], len(command['coh']), command['Results']['Target'])
            print_human('            Precheck ', command['Fatal']['precheck'], len(command['coh']), command['Results']['Target'])
            print_human('        Plan ', command['Results']['Plan'], len(command['coh']), command['Results']['Target'] + command['Results']['Plan'] + command['Results']['Infra'])
            print_human('            Over Timed ', command['Over Timed'], len(command['coh']), command['Results']['Plan'])
            print_human('            Script ', command['Fatal']['script'], len(command['coh']), command['Results']['Plan'])
            print_human('            Broken Bundle ', command['Fatal']['bundle_broken'], len(command['coh']), command['Results']['Plan'])
            print_human('            Delete ', command['Fatal']['delete'], len(command['coh']), command['Results']['Plan'])
            print_human('            Timeout ', command['Fatal']['timeout'], len(command['coh']), command['Results']['Plan'])
            print_human('            Package Modified ', command['Fatal']['package_modified'], len(command['coh']), command['Results']['Plan'])
            print_human('        Infra ', command['Results']['Infra'], len(command['coh']), command['Results']['Target'] + command['Results']['Plan'] + command['Results']['Infra'])
            print_human('            Package Unavailable ', command['Fatal']['package_unavailable'], len(command['coh']), command['Results']['Infra'])
            print_human('            Connection Issue ', command['Fatal']['conn_issue'], len(command['coh']), command['Results']['Infra'])

        elif options.format == 'csv':
            print "%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s" % (
                id_command,
                command['name'],
                command['creator'],
                command['creation_date'],
                command['start_date'],
                command['end_date'],
                ','.join(command['Domains']),
                len(command['coh']),
                command['Results']['To Do'],
                command['Scheduled'],
                command['Rescheduled'],
                command['Results']['Doing'],
                sum(command['In Progress'].values()),
                command['Results']['Done'],
                command['Success'],
                command['Results']['Delayed'],
                command['Stopped'],
                command['Neutralized'],
                command['Results']['Target'] + command['Results']['Plan'] + command['Results']['Infra'],
                command['Results']['Target'],
                command['Fatal']['not_enought_info'],
                command['Fatal']['target_broken'],
                command['Fatal']['halt'],
                command['Fatal']['mac_mismatch'],
                command['Fatal']['unreachable'],
                command['Fatal']['inventory'],
                command['Fatal']['execution'],
                command['Fatal']['precheck'],
                command['Results']['Plan'],
                command['Over Timed'],
                command['Fatal']['script'],
                command['Fatal']['bundle_broken'],
                command['Fatal']['delete'],
                command['Fatal']['timeout'],
                command['Fatal']['package_modified'],
                command['Results']['Infra'],
                command['Fatal']['package_unavailable'],
                command['Fatal']['conn_issue']
            )

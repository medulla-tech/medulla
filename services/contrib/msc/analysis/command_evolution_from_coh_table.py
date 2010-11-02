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
    print "\tThis is neither a success or a failure, they have not been"
    print "\tprocesseed."
    print "   + Rescheduled : Hosts which have known at least one"
    print "\tfailure"
    print "\tThis is neither a success or a failure, but are not being"
    print "\tprocessed ATM : as failure may be temporary or definitive,"
    print "\tkeep an eye on them : previous failure may be due to"
    print "\tanything."
    print "   + In Progress : Hosts which are currently working"
    print "\tIt those hosts seems to work since a long time (more than"
    print "\t24 hours), you should stop them using the interface.."
    print "   + Stopped : Hosts which have been stopped BY THE USER"
    print "\tThose copmmands can still be a success or a failure, if the"
    print "\tuser start them again"
    print "   + Neutralized : Hosts which have been stopped BY THE SCHEDULER"
    print "\tThoses commands were obviously misbehaving - which should"
    print "\tnot arrive - you can consider thoses as a failure"
    print "  + Aborded : Hosts running out of time"
    print "\tThey were simply running out of time"
    print "  + Success : Hosts which have been successfully deployed"
    print "\tNothing more to add : deployment went as expected"
    print "  + Failure : Hosts which have consummed all attempts, but"
    print "\tdon't blame Pulse 2 yet, details are following"
    print "     --> Not Enough Info : The system had not enought information to deploy"
    print "\t\tThis is generally caused by an out-ot-sync inventory"
    print "\t\tdatase, or a resolv mechanism (DNS) issue."
    print "     --> Broken Bundle : This commands depends on a failed one"
    print "\t\tYou should seek out why the dependency do fail."
    print "     --> Package Unavailable : The required package is not on your server anymore"
    print "\t\tThis is generally because the package was removed from"
    print "\t\tthe server before the host can get it. This may also"
    print "\t\tbe due to network issues."
    print "     --> Package Modified : The required package has been modified on your server"
    print "\t\tThis is generally because the package was modified on"
    print "\t\tthe server before the host can get it. This may also"
    print "\t\tbe due to network issues."
    print "     --> Timeout : The script was killed has it took too much time."
    print "\t\tYour script is probably broken, and waiting for event"
    print "\t\t(keypress for example) which won't occur in silent mode"
    print "     --> Target broken : The target is probably broken."
    print "\t\tIt may be already crashed."
    print "     --> Mac Mismatch : Issue when controlling the target MAC address."
    print "\t\tAlso related to an out-of-sync inventory database"
    print "     --> Unreachable : Issue when attempting to contact the host."
    print "\t\tThe host can be down. Or be firewalled. Or without the agent installed."
    print "     --> Connection issue : Issue while talking to the host."
    print "\t\tIssue cause is unknown. Network issue ? Scheduler dying ?"
    print "     --> Delete : Delete failed."
    print "\t\tThe deletion raised an error, this generaly occurs when"
    print "\t\tthe install script screw the temporary folder. Script is"
    print "\t\tprobably broken."
    print "     --> Inventory : Inventory failed."
    print "\t\tThe inventory command do failed. Please check those hosts;"
    print "\t\tthe inventory may be misconfigured."
    print "     --> Halt : Halt failed."
    print "\t\tThe halt command do failed. Please check those hosts;"
    print "\t\tit is possible that something prevent the computer to be"
    print "\t\tshut down."
    print "     --> Script : Script failed."
    print "\t\tThe script raised an error you told it to raise (in other"
    print "\t\twords : you expected this error; based on this code, you"
    print "\t\tshould now know what to do with those clients."
    print "     --> Execution : Execution failed."
    print "\t\tThe script raised an INTERNAL error; you should have a"
    print "\t\tlook to see why it failed"
    print " - Results : the ammounts, categorized"
    print "  + To Do : deployments till to be done; contains 'Scheduled', 'Rescheduled'"
    print "  + Doing : deployments in progress; contains 'In Progress'"
    print "  + Delayed : deployments postponed by user or scheduler  action, contains 'Stopped', 'Neutralized'"
    print "  + Done : deployments finished on success, contains 'Success'"
    print "  + Not Done : deployments finished on error, contains the following field"
    print "  + Target : deployment which have failed since the target was deficient, contains 'Not Enough Info', 'Target broken', 'Halt', 'Mac Mismatch', 'Unreachable', 'Inventory', 'Execution'"
    print "  + Plan : deployment which have failed since the deployment plan lacked information, contains 'Aborded', 'Script', 'Broken Bundle', 'Delete', 'Timeout', 'Package Modified'"
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
    struct['Aborded'] = 0
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
            dataCommand['Aborded'] += 1
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
            for i in dataCommand['coh'][coh['id']]:
                if i[1] != 0 :
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
                last_failed = 'conn_issue'
                dataCommand['Results']['Infra'] += 1
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
        "Plan",
        'Aborded',
        'Script',
        'Broken Bundle',
        'Delete',
        'Timeout',
        'Package Modified',
        "Infra",
        'Package Unavailable',
        'Connexion issue'
    ))

ids_command = data.keys()
ids_command.sort()
for id_command in ids_command:
    command = data[id_command]
    if len(command['coh']) > options.min:
        if options.format == 'human':
            print "=============== [%s] ===============" % id_command
            print "%s : %s" % ('Name\t\t', command['name'])
            print "%s : %s" % ('Creator\t\t', command['creator'])
            print "%s : %s" % ('Created\t\t', command['creation_date'])
            print "%s : %s" % ('Domains\t\t', command['Domains'])
            print "--------------- Results ---------------"
            print "%s : %s (%s %%)" % ('Total\t\t\t\t\t\t', len(command['coh']), 100)
            print "\t%s : %s (%s %%)" % ('To Do\t\t\t\t\t', command['Results']['To Do'], 100 * command['Results']['To Do'] / len(command['coh']))
            if command['Scheduled'] : print "\t\t%s : %s (%s %%)" % ('Scheduled\t\t\t', command['Scheduled'], 100 * command['Scheduled'] / len(command['coh']))
            if command['Rescheduled'] : print "\t\t%s : %s (%s %%)" % ('Rescheduled\t\t\t', command['Rescheduled'], 100 * command['Rescheduled'] / len(command['coh']))
            print "\t%s : %s (%s %%)" % ('Doing\t\t\t\t\t', command['Results']['Doing'], 100 * command['Results']['Doing'] / len(command['coh']))
            if sum(command['In Progress'].values()) : print "\t\t%s : %s (%s %%)" % ('In Progress\t\t\t', sum(command['In Progress'].values()), 100 * sum(command['In Progress'].values()) / len(command['coh']))
            print "\t%s : %s (%s %%)" % ('Delayed\t\t\t\t\t', command['Results']['Delayed'], 100 * command['Results']['Delayed'] / len(command['coh']))
            if command['Stopped'] : print "\t\t%s : %s (%s %%)" % ('Stopped\t\t\t', command['Stopped'], 100 * command['Stopped'] / len(command['coh']))
            if command['Neutralized'] : print "\t\t%s : %s (%s %%)" % ('Neutralized\t', command['Neutralized'], 100 * command['Neutralized'] / len(command['coh']))
            print "\t%s : %s (%s %%)" % ('Done\t\t\t\t\t', command['Results']['Done'], 100 * command['Results']['Done'] / len(command['coh']))
            if command['Success'] : print "\t\t%s : %s (%s %%)" % ('Success\t\t\t\t', command['Success'], 100 * command['Success'] / len(command['coh']))
            print "\t%s : %s (%s %%)" % ('Not Done\t\t\t\t', command['Results']['Target'] + command['Results']['Plan'] + command['Results']['Infra'], 100 * (command['Results']['Target'] + command['Results']['Plan'] + command['Results']['Infra']) / len(command['coh']))
            print "\t%s : %s (%s %%)" % ('\tTarget\t\t\t\t', command['Results']['Target'], 100 * command['Results']['Target'] / len(command['coh']))
            if command['Fatal']['not_enought_info'] : print "\t\t\t%s : %s (%s %%)" % ('Not Enough Info\t\t', command['Fatal']['not_enought_info'], 100 * command['Fatal']['not_enought_info'] / len(command['coh']))
            if command['Fatal']['target_broken'] : print "\t\t\t%s : %s (%s %%)" % ('Target broken\t\t', command['Fatal']['target_broken'], 100 * command['Fatal']['target_broken'] / len(command['coh']))
            if command['Fatal']['halt'] : print "\t\t\t%s : %s (%s %%)" % ('Halt\t\t\t', command['Fatal']['halt'], 100 * command['Fatal']['halt'] / len(command['coh']))
            if command['Fatal']['mac_mismatch'] : print "\t\t\t%s : %s (%s %%)" % ('Mac Mismatch\t\t', command['Fatal']['mac_mismatch'], 100 * command['Fatal']['mac_mismatch'] / len(command['coh']))
            if command['Fatal']['unreachable'] : print "\t\t\t%s : %s (%s %%)" % ('Unreachable\t\t', command['Fatal']['unreachable'], 100 * command['Fatal']['unreachable'] / len(command['coh']))
            if command['Fatal']['inventory'] : print "\t\t\t%s : %s (%s %%)" % ('Inventory\t\t', command['Fatal']['inventory'], 100 * command['Fatal']['inventory'] / len(command['coh']))
            if command['Fatal']['execution'] : print "\t\t\t%s : %s (%s %%)" % ('Execution\t\t', command['Fatal']['execution'], 100 * command['Fatal']['execution'] / len(command['coh']))
            print "\t%s : %s (%s %%)" % ('\tPlan\t\t\t\t', command['Results']['Plan'], 100 * command['Results']['Plan'] / len(command['coh']))
            if command['Aborded'] : print "\t\t\t%s : %s (%s %%)" % ('Aborded\t\t\t', command['Aborded'], 100 * command['Aborded'] / len(command['coh']))
            if command['Fatal']['script'] : print "\t\t\t%s : %s (%s %%)" % ('Script\t\t\t', command['Fatal']['script'], 100 * command['Fatal']['script'] / len(command['coh']))
            if command['Fatal']['bundle_broken'] : print "\t\t\t%s : %s (%s %%)" % ('Broken Bundle\t\t', command['Fatal']['bundle_broken'], 100 * command['Fatal']['bundle_broken'] / len(command['coh']))
            if command['Fatal']['delete'] : print "\t\t\t%s : %s (%s %%)" % ('Delete\t\t\t', command['Fatal']['delete'], 100 * command['Fatal']['delete'] / len(command['coh']))
            if command['Fatal']['timeout'] : print "\t\t\t%s : %s (%s %%)" % ('Timeout\t\t\t', command['Fatal']['timeout'], 100 * command['Fatal']['timeout'] / len(command['coh']))
            if command['Fatal']['package_modified'] : print "\t\t\t%s : %s (%s %%)" % ('Package Modified\t', command['Fatal']['package_modified'], 100 * command['Fatal']['package_modified'] / len(command['coh']))
            print "\t%s : %s (%s %%)" % ('\tInfra\t\t\t\t', command['Results']['Infra'], 100 * command['Results']['Infra'] / len(command['coh']))
            if command['Fatal']['package_unavailable'] : print "\t\t\t%s : %s (%s %%)" % ('Package Unavailable\t', command['Fatal']['package_unavailable'], 100 * command['Fatal']['package_unavailable'] / len(command['coh']))
            if command['Fatal']['conn_issue'] : print "\t\t\t%s : %s (%s %%)" % ('Connection Issue\t', command['Fatal']['conn_issue'], 100 * command['Fatal']['conn_issue'] / len(command['coh']))

        elif options.format == 'csv':
            print "%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s" % (
                id_command,
                command['name'],
                command['creator'],
                command['creation_date'],
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
                command['Results']['Plan'],
                command['Aborded'],
                command['Fatal']['script'],
                command['Fatal']['bundle_broken'],
                command['Fatal']['delete'],
                command['Fatal']['timeout'],
                command['Fatal']['package_modified'],
                command['Results']['Infra'],
                command['Fatal']['package_unavailable'],
                command['Fatal']['conn_issue']
            )

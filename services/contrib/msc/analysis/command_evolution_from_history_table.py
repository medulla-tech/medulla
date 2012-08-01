#!/usr/bin/python
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

"""
    get a command list
    give a CSV-ouput of the command advancement on its targets, using the history table
    lines are formated like this:
      - timestamp (rounded 60 seconds)
      - amount of upload/exec/delete in progress during those 60 seconds
      - amount of upload/exec/delete failed during those 60 seconds
      - amount of upload/exec/delete done during those 60 seconds
      - ammount of targets in stage 1 (upload done, exec todo)
      - ammount of targets in stage 2 (exec done, delete todo)
      - ammount of targets in stage 3 (delete done)
"""

import sys
import time
from sqlalchemy import *

if len(sys.argv) != 3:
    print "usage: %s <mysql-uri> <command-id-comma-separated>" % sys.argv[0]
    exit(1)

# create connection
mysql_db = create_engine(sys.argv[1])
metadata = MetaData(mysql_db)

coh_table = Table('commands_on_host',
                         metadata,
                         autoload = True)
history_table = Table("commands_history",
                         metadata,
                         Column('fk_commands_on_host', Integer, ForeignKey('commands_on_host.id')),
                         autoload = True)

# prepare command ids
ids = sys.argv[2].split(',')

hist_data = select([
        history_table.c.fk_commands_on_host,
        history_table.c.date,
        history_table.c.state,
        history_table.c.error_code
    ]
    ).select_from(
        history_table.join(coh_table)
    ).where(
        coh_table.c.fk_commands.in_(ids)
    ).order_by(history_table.c.date).execute().fetchall()

class deployStats:

    __keys = [
        "uploading",
        "executing",
        "deleting",
        "rebooting",
        "upload_error",
        "execution_error",
        "delete_error",
        "reboot_error",
        "upload_done",
        "execution_done",
        "delete_done",
        "reboot_done",
        "stage0",
        "stage1",
        "stage2",
        "stage3",
        "stage4",
        "bundle_error",
        "mirror_error"
    ]

    __internal_data = dict()
    for k in __keys:
        __internal_data[k] = set()

    def add(self, where, what):
        self.__internal_data[where].add(what)

    def remove(self, where, what):
        try:
            self.__internal_data[where].remove(what)
        except KeyError:
            pass


    def getkeys(self):
        return self.__keys

    def getcount(self, where):
        return len(self.__internal_data[where])

    def getcounts(self):
        return map(lambda x: str(len(self.__internal_data[x])), self.getkeys())


deploy_stats = deployStats()
lastepoch = 0
laststates = dict()

print "date;%s;" % ';'.join(deploy_stats.getkeys())

for d in hist_data:
    # d is like this: (6445L, '1223597787.8313', 'upload_done', 0)
    (fk, epoch, operation, error_code) = d

    truncated_epoch = int(float(epoch)/60)*60
    #truncated_epoch = int(float(epoch)/1)*1

    if not fk in laststates.keys():
        laststates[fk] = None

    if operation == 'upload_in_progress' and error_code in [4508, 4509]: # mirror probe, ignore
        continue
        
    if operation == None and error_code == 3001 : # broken bundle ?
        operation = 'bundle_failed'
        
    if operation == 'upload_failed' and error_code == 4001 : # package not found ?
        operation = 'mirror_failed'
            
    if laststates[fk] == operation:
        print "ANOMALY: %s for %s " % (operation, fk)
        continue
    else:
        if operation == 'upload_in_progress':
            deploy_stats.remove('upload_error', fk)
            deploy_stats.add('uploading', fk)
        elif operation == 'upload_done':
            deploy_stats.remove('uploading', fk)
            deploy_stats.add('upload_done', fk)
            deploy_stats.add('stage1', fk)
        elif operation == 'upload_failed':
            deploy_stats.remove('uploading', fk)
            deploy_stats.add('upload_error', fk)
        elif operation == 'execution_in_progress':
            deploy_stats.remove('execution_error', fk)
            deploy_stats.add('executing', fk)
        elif operation == 'execution_done':
            deploy_stats.remove('executing', fk)
            deploy_stats.add('execution_done', fk)
            deploy_stats.remove('stage1', fk)
            deploy_stats.add('stage2', fk)
        elif operation == 'execution_failed':
            deploy_stats.remove('executing', fk)
            deploy_stats.add('execution_error', fk)
        elif operation == 'delete_in_progress':
            deploy_stats.remove('delete_error', fk)
            deploy_stats.add('deleting', fk)
        elif operation == 'delete_done':
            deploy_stats.remove('deleting', fk)
            deploy_stats.add('delete_done', fk)
            deploy_stats.remove('stage2', fk)
            deploy_stats.add('stage3', fk)
        elif operation == 'delete_failed':
            deploy_stats.remove('deleting', fk)
            deploy_stats.add('delete_error', fk)
        elif operation == 'reboot_in_progress':
            deploy_stats.remove('reboot_error', fk)
            deploy_stats.add('rebooting', fk)
        elif operation == 'reboot_done':
            deploy_stats.remove('rebooting', fk)
            deploy_stats.add('reboot_done', fk)
            deploy_stats.remove('stage3', fk)
            deploy_stats.add('stage4', fk)
        elif operation == 'reboot_failed':
            deploy_stats.remove('rebooting', fk)
            deploy_stats.add('reboot_error', fk)
        elif operation == 'bundle_failed':
            deploy_stats.add('bundle_error', fk)
        elif operation == 'mirror_failed':
            deploy_stats.remove('upload_error', fk)
            deploy_stats.add('mirror_error', fk)

        if truncated_epoch != lastepoch:
            print "%s;%s;" % (
                time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(float(truncated_epoch))),
                ';'.join(deploy_stats.getcounts())
            )

    laststates[fk] = operation
    lastepoch = truncated_epoch

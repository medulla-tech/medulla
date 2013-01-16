#!/usr/bin/python
#
# (c) 2008 Mandriva, http://www.mandriva.com/
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

import sys
import os
import re
import time
from pychart import *

X_MINOR_TICK_INTERVAL = 600
X_TICK_INTERVAL = 3600

Y_MINOR_TICK_INTERVAL = 20
Y_TICK_INTERVAL = 100

X_GRID_INTERVAL = 600
Y_GRID_INTERVAL = 20

Y_MAX = 299

HEIGHT = 800
WIDTH = 1200
DELTA = 30

def create_graph(label_x, label_y, data_x, alldata_y, filename, title, start_date, end_date):

    # alter file name (linpng do not seems to like spaces in filenames

    filename = filename.replace(' ', '_')
    # Graph style
    theme.get_options()
    theme.use_color = True
    theme.default_font_size = 12
    theme.default_font_family = "AvantGarde-Book"
    theme.reinitialize()

    colors = [
        color.blue,
        color.red,
        color.green,
        color.magenta,
        color.cyan1,
        color.orange,
    ]

    can = canvas.init("%s"%filename)

    # Draw graph title
    newtitle = "/hL/20%s"%title
    left = WIDTH / 2  - font.text_width(newtitle)/2
    can.show(left, HEIGHT + DELTA, newtitle)

    zip(data_x)
    int_to_date = lambda x: '/a60{}' + time.strftime("%H:%M", time.localtime(x))

    xaxis = axis.X(
        format = int_to_date,
        label = "/20%s" % label_x,
        label_offset = (0, -DELTA),
        minor_tic_interval = X_MINOR_TICK_INTERVAL,
        tic_interval = X_TICK_INTERVAL
    )
    yaxis = axis.Y(
        label = "/20%s" % label_y,
        label_offset = (-DELTA, 0),
        minor_tic_interval = Y_MINOR_TICK_INTERVAL,
        tic_interval = Y_TICK_INTERVAL
    )

    ar = area.T(
        size = (WIDTH, HEIGHT),
        x_axis = xaxis,
        y_axis = yaxis,
        x_grid_style = line_style.gray70_dash3,
        x_range = (start_date, end_date),
        y_range = (0, Y_MAX),
        x_grid_interval = X_GRID_INTERVAL,
        y_grid_interval = Y_GRID_INTERVAL
    )

    i = 0
    # Draw a line for each columns
    for title, data_y in alldata_y.iteritems():
        plot = line_plot.T(
            label = title,
            data = zip(data_x,data_y),
            line_style = line_style.T(
                color = colors[i],
                width = 1
            )
        )
        ar.add_plot(plot)
        i += 1

    ar.draw()
    can.close()

    return True

def read_logs(log_dir, start_date, stop_date):
    """
    Read launchers logs in log_dir from start_date to stop_date
    """

    regexp = "([0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}):[0-9]{2},.*launcher ([^:]*): BALANCE: (.*)"
    groups = {}
    launchers = {}

    # Parse all log files in the directory
    for file in os.listdir(log_dir):

        # If this is a real log file
        # TODO : better test
        if ".log" in file:

            print "reading %s"%file
            fh = open(os.path.join(log_dir,file))

            # Parse each line in the log file
            for line in fh:

                # Add the "BALANCE" test to avoid computing regexp if the line doesn't match
                if (("BALANCE:" in line) and re.search(regexp, line)) :

                    # Extract regexp results
                    res = re.search(regexp, line)
                    date = res.group(1)
                    stamp = int(time.mktime(time.strptime(date, '%Y-%m-%d %H:%M')))

                    if (stamp > start_date and stamp < stop_date):

                        launcher = res.group(2)
                        stats = res.group(3)
                        # Convert str to dict
                        dump = eval(stats)

                        if dump.has_key('global'):

                            if not launchers.has_key(launcher):
                                launchers[launcher] = {}
                            if launchers[launcher].has_key(stamp):
                                launchers[launcher][stamp] += int(dump['global']['running'])
                            else:
                                launchers[launcher][stamp] = int(dump['global']['running'])

                        if dump.has_key('by_group'):

                            # For each group available
                            for group in dump['by_group'].keys():
                                if not groups.has_key(group):
                                    groups[group] = {}
                                # If this group as already an entry for this time (from an other launcher), we add the new one
                                if groups[group].has_key(stamp):
                                    groups[group][stamp] += int(dump['by_group'][group]['running'])
                                else:
                                    groups[group][stamp] = int(dump['by_group'][group]['running'])
    return (groups,launchers)

# Main Loop
if __name__ == "__main__":

    if len(sys.argv) != 4:
        sys.exit("Usage : %s <logs_directory> '<start date>' '<end date>'"%sys.argv[0])

    (log_dir, start_str, end_str) = sys.argv[1:]

    if not os.path.isdir(sys.argv[1]):
        sys.exit("ERROR, %s : no such directory."%sys.argv[1])

    groups_actions = {}
    launch_actions = {}

    group_hours = []
    launch_hours = []

    # Parse logs
    start = int(time.mktime(time.strptime(start_str, '%Y-%m-%d %H:%M')))
    stop = int(time.mktime(time.strptime(end_str, '%Y-%m-%d %H:%M')))
    (groups, launchers) = read_logs( log_dir, start, stop)

    if groups:
        group_list = groups.keys()

        # Get all group hours
        for group in group_list:
            group_hours += groups[group].keys()
            # deduplicate list
            group_hours = list(set(group_hours))
            group_hours.sort()

        # Sort groups data for pygraph
        for group in group_list:

            for hour in group_hours:
                if not groups_actions.has_key(group):
                    groups_actions[group] = []
                if groups[group].has_key(hour):
                    groups_actions[group].append(groups[group][hour])
                else:
                    groups_actions[group].append(0)

            create_graph("Horaires", "Nombre d'actions", group_hours, {group: groups_actions[group]}, 'group %s  - %s-%s.png' % (group, start_str, end_str), "Evolution du nombre d'actions en cours sur le group \"%s\" entre %s et %s" % (group, start_str, end_str), start, stop)
        create_graph("Horaires", "Nombre d'actions", group_hours, groups_actions, 'groups - %s-%s.png' % (start_str, end_str), "Evolution du nombre d'actions en cours sur les differents groups entre %s et %s" % (start_str, end_str), start, stop)


    if launchers:
        launcher_list = launchers.keys()

        # Get all launch hours
        for launch in launcher_list:
            launch_hours += launchers[launch].keys()
            # deduplicate list
            launch_hours = list(set(launch_hours))
            launch_hours.sort()

        # Sort launchers data for pygraph
        for launch in launcher_list:

            for hour in launch_hours:
                if not launch_actions.has_key(launch):
                    launch_actions[launch] = []
                if launchers[launch].has_key(hour):
                    launch_actions[launch].append(launchers[launch][hour])
                else:
                    launch_actions[launch].append(0)

            create_graph("Horaires", "Nombre d'actions", launch_hours, {launch: launch_actions[launch]}, '%s - %s-%s.png' % (launch, start_str, end_str), "Evolution du nombre d'actions en cours sur le launcher \"%s\" entre %s et %s" % (launch, start_str, end_str), start, stop)
        create_graph("Horaires", "Nombre d'actions", launch_hours, launch_actions, 'launchers - %s-%s.png' % (start_str, end_str), "Evolution du nombre d'actions en cours sur les differents launchers entre %s et %s" % (start_str, end_str), start, stop)

    sys.exit(0)

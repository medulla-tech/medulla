#!/usr/bin/python
#
# (c) 2008-2009 Mandriva, http://www.mandriva.com
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
A simple Pulse 2 Launchers log analyzer
"""

import sys
import re
import time
from pychart import color, theme, axis, canvas, area, line_style, line_plot, font

X_MINOR_TICK_INTERVAL = 600
X_TICK_INTERVAL = 3600

X_GRID_INTERVAL = 600

HEIGHT = 800
WIDTH = 1200
DELTA = 30

BALANCE_REGEX = "([0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}):[0-9]{2},.*launcher ([^:]*): BALANCE: (.*)"
HEALTH_REGEX = "([0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}):[0-9]{2},.*launcher ([^:]*): HEALTH: (.*)"


def create_graph(label_x, label_y, data_x, alldata_y, filename, title, start_date, end_date, start_y, end_y):
    """
    main func
    """

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
        color.yellow,
        color.darkblue,
        color.darkred,
        color.darkgreen,
        color.darkmagenta,
        color.darkcyan,
        color.gold,
        color.lightblue1,
        color.orangered,
        color.lightgreen,
        color.pink,
        color.lightcyan,
        color.goldenrod,
    ]

    can = canvas.init("%s" % filename)

    # Draw graph title
    newtitle = "/hL/20%s" % title
    left = WIDTH / 2  - font.text_width(newtitle) / 2
    can.show(left, HEIGHT + DELTA, newtitle)

    int_to_date = lambda x: '/a60{}' + time.strftime("%H:%M", time.localtime(x))

    xaxis = axis.X(
        format = int_to_date,
        label = "/20%s" % label_x,
        label_offset = (0, -DELTA),
        minor_tic_interval = X_MINOR_TICK_INTERVAL,
        tic_interval = X_TICK_INTERVAL)
    yaxis = axis.Y(
        label = "/20%s" % label_y,
        label_offset = (-DELTA, 0),
        minor_tic_interval = (end_y - start_y) / 20,
        tic_interval = (end_y - start_y) / 5,
    )

    ar = area.T(
        size = (WIDTH, HEIGHT),
        x_axis = xaxis,
        y_axis = yaxis,
        x_grid_style = line_style.gray70_dash3,
        x_range = (start_date, end_date),
        y_range = (start_y, end_y),
        x_grid_interval = X_GRID_INTERVAL,
        y_grid_interval = (end_y - start_y) / 5
    )

    i = 0
    # Draw a line for each columns
    for title, data_y in alldata_y.iteritems():
        plot = line_plot.T(
            label = title,
            data = zip(data_x, data_y),
            line_style = line_style.T(
                color = colors[i],
                width = 1))
        ar.add_plot(plot)
        i += 1

    ar.draw()
    can.close()

    return True


def read_logs(logfiles, start_date, stop_date):
    """
    Read launchers logs in log_dir from start_date to stop_date
    """

    groups    = {}      # hold running commands per group
    runnings  = {}      # hold running commands per launcher
    zombies   = {}      # hold zombie commands per launcher
    loads     = {}      # hold loads (1 minute) per launcher
    fds       = {}      # hold FD count per launcher

    # Parse all log files in the directory
    for file in logfiles:

        try:
            fh = open(file)
        except IOError:
            print "can't read %s " % file
            continue

        print "parsing %s ... " % file
        for line in fh:  # Parse each line in the log file
            # Add the "BALANCE" test to avoid computing regexp if the line doesn't match
            res = re.search(BALANCE_REGEX, line)

            if not res:  # try another regex
                res = re.search(HEALTH_REGEX, line)

            if not res:  # give up if line do not match
                continue

            stamp = int(time.mktime(time.strptime(res.group(1), '%Y-%m-%d %H:%M')))
            if (stamp < start_date or stamp > stop_date):  # give up if time do not match
                continue

            launcher = res.group(2)
            dump = eval(res.group(3))

            if dump.has_key('global'):
                if not runnings.has_key(launcher):
                    runnings[launcher] = {}
                if not runnings[launcher].has_key(stamp):
                    runnings[launcher][stamp] = int(dump['global']['running'])
                else:
                    runnings[launcher][stamp] += int(dump['global']['running'])
                if not zombies.has_key(launcher):
                    zombies[launcher] = {}
                if not zombies[launcher].has_key(stamp):
                    zombies[launcher][stamp] = int(dump['global']['zombie'])
                else:
                    zombies[launcher][stamp] += int(dump['global']['zombie'])

            if dump.has_key('loadavg'):
                if not loads.has_key(launcher):
                    loads[launcher] = {}
                if not loads[launcher].has_key(stamp):
                    loads[launcher][stamp] = int(dump['loadavg']['1min'])
                else:
                    loads[launcher][stamp] += int(dump['loadavg']['1min'])

            if dump.has_key('fd'):
                if not fds.has_key(launcher):
                    fds[launcher] = {}
                if not fds[launcher].has_key(stamp):
                    fds[launcher][stamp] = sum(dump['fd'].values())
                else:
                    fds[launcher][stamp] += sum(dump['fd'].values())

            if dump.has_key('by_group'):
                # Prevent "None" from beeing eval'ed as None
                if dump['by_group'].has_key(None):
                    dump['by_group']["Other"] = dump['by_group'][None]
                    del dump['by_group'][None]

                # For each group available
                for group in dump['by_group'].keys():
                    if not groups.has_key(group):
                        groups[group] = {}
                    # If this group as already an entry for this time (from an other launcher), we add the new one
                    if groups[group].has_key(stamp):
                        groups[group][stamp] += int(dump['by_group'][group]['running'])
                    else:
                        groups[group][stamp] = int(dump['by_group'][group]['running'])

    return (groups, runnings, zombies, loads, fds)

# Main Loop
if __name__ == "__main__":

    if len(sys.argv) < 4:
        sys.exit("Usage : %s '<start date>' '<end date>' <log1> <log2> ..." % sys.argv[0])
    (start_str, end_str) = sys.argv[1:3]
    logfiles = sys.argv[3:]

    groups_actions = {}

    group_hours = []
    launch_hours = []

    # Parse logs
    start = int(time.mktime(time.strptime(start_str, '%Y-%m-%d %H:%M')))
    stop = int(time.mktime(time.strptime(end_str, '%Y-%m-%d %H:%M')))
    (groups, runnings, zombies, loads, fds) = read_logs(logfiles, start, stop)

    if groups:
        # prevent empty labels, leading to divide-by-zero
        if '' in groups:
            groups['unknown'] = groups.pop('')

        group_list = groups.keys()
        y_max = (max(map(lambda x: max(x.values()), groups.values())) / 50 + 1) * 50

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

            create_graph("Time", "Number of actions", group_hours, {group: groups_actions[group]}, 'group %s  - %s-%s.png' % (group, start_str, end_str), "Running actions on group \"%s\" between %s and %s" % (group, start_str, end_str), start, stop, 0, y_max)
        create_graph("Time", "Number of actions", group_hours, groups_actions, 'groups - %s-%s.png' % (start_str, end_str), "Running actions per group between %s and %s" % (start_str, end_str), start, stop, 0, y_max)


    if runnings:
        launch_actions = {}
        launcher_list = runnings.keys()
        y_max = (max(map(lambda x: max(x.values()), runnings.values())) / 50 + 1) * 50

        # Get all launch hours
        for launch in launcher_list:
            launch_hours += runnings[launch].keys()
            # deduplicate list
            launch_hours = list(set(launch_hours))
            launch_hours.sort()

        # Sort launchers data for pygraph
        for launch in launcher_list:
            for hour in launch_hours:
                if not launch_actions.has_key(launch):
                    launch_actions[launch] = []
                if runnings[launch].has_key(hour):
                    launch_actions[launch].append(runnings[launch][hour])
                else:
                    launch_actions[launch].append(0)
            create_graph("Time", "Number of actions", launch_hours, {launch: launch_actions[launch]}, '%s - running - %s-%s.png' % (launch, start_str, end_str), "Running actions on \"%s\" between %s and %s" % (launch, start_str, end_str), start, stop, 0, y_max)
        create_graph("Time", "Number of actions", launch_hours, launch_actions, 'launchers - running - %s-%s.png' % (start_str, end_str), "Running actions between %s and %s" % (start_str, end_str), start, stop, 0, y_max)

    if zombies:
        launch_zombies = {}
        launcher_list = zombies.keys()
        y_max = (max(map(lambda x: max(x.values()), zombies.values())) / 50 + 1) * 50

        # Get all launch hours
        for launch in launcher_list:
            launch_hours += zombies[launch].keys()
            # deduplicate list
            launch_hours = list(set(launch_hours))
            launch_hours.sort()

        # Sort launchers data for pygraph
        for launch in launcher_list:
            for hour in launch_hours:
                if not launch_zombies.has_key(launch):
                    launch_zombies[launch] = []
                if zombies[launch].has_key(hour):
                    launch_zombies[launch].append(zombies[launch][hour])
                else:
                    launch_zombies[launch].append(0)
            create_graph("Time", "Number of actions", launch_hours, {launch: launch_zombies[launch]}, '%s - zombies - %s-%s.png' % (launch, start_str, end_str), "Zombies on \"%s\" between %s and %s" % (launch, start_str, end_str), start, stop, 0, y_max)
        create_graph("Time", "Number of actions", launch_hours, launch_zombies, 'launchers - zombies - %s-%s.png' % (start_str, end_str), "Zombies between %s and %s" % (start_str, end_str), start, stop, 0, y_max)

    if loads:
        launch_loads = {}
        launcher_list = loads.keys()
        y_max = (max(map(lambda x: max(x.values()), loads.values())) / 1 + 1) * 1

        # Get all launch hours
        for launch in launcher_list:
            launch_hours += loads[launch].keys()
            # deduplicate list
            launch_hours = list(set(launch_hours))
            launch_hours.sort()

        # Sort launchers data for pygraph
        for launch in launcher_list:
            for hour in launch_hours:
                if not launch_loads.has_key(launch):
                    launch_loads[launch] = []
                if loads[launch].has_key(hour):
                    launch_loads[launch].append(loads[launch][hour])
                else:
                    launch_loads[launch].append(0)
            create_graph("Time", "Load", launch_hours, {launch: launch_loads[launch]}, '%s - load - %s-%s.png' % (launch, start_str, end_str), "Load on \"%s\" between %s and %s" % (launch, start_str, end_str), start, stop, 0, y_max)
        create_graph("Time", "Load", launch_hours, launch_loads, 'launchers - load - %s-%s.png' % (start_str, end_str), "Load between %s and %s" % (start_str, end_str), start, stop, 0, y_max)

    sys.exit(0)

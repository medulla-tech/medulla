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
        color.orange,
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
        color.mistyrose,
        color.honeydew,
        color.gainsboro,
        color.yellow,
        color.peachpuff,
        color.turquoise,
        color.chartreuse1,
        color.pink,
        color.brown,
        color.blue,
        color.red,
        color.green,
        color.magenta,
        color.cyan1,
        color.orange,
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
        color.mistyrose,
        color.honeydew,
        color.gainsboro,
        color.yellow,
        color.peachpuff,
        color.turquoise,
        color.chartreuse1,
        color.pink,
        color.brown
    ]

    can = canvas.init(f"{filename}")

    # Draw graph title
    newtitle = f"/hL/20{title}"
    left = WIDTH / 2  - font.text_width(newtitle) / 2
    can.show(left, HEIGHT + DELTA, newtitle)

    int_to_date = lambda x: '/a60{}' + time.strftime("%H:%M", time.localtime(x))

    xaxis = axis.X(
        format=int_to_date,
        label=f"/20{label_x}",
        label_offset=(0, -DELTA),
        minor_tic_interval=X_MINOR_TICK_INTERVAL,
        tic_interval=X_TICK_INTERVAL,
    )
    yaxis = axis.Y(
        label=f"/20{label_y}",
        label_offset=(-DELTA, 0),
        minor_tic_interval=(end_y - start_y) / 20,
        tic_interval=(end_y - start_y) / 5,
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

    # Draw a line for each columns
    for i, (title, data_y) in enumerate(alldata_y.iteritems()):
        plot = line_plot.T(
            label = title,
            data = zip(data_x, data_y),
            line_style = line_style.T(
                color = colors[i],
                width = 1))
        ar.add_plot(plot)
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

            if 'global' in dump:
                if not launcher in runnings:
                    runnings[launcher] = {}
                if not stamp in runnings[launcher]:
                    runnings[launcher][stamp] = int(dump['global']['running'])
                else:
                    runnings[launcher][stamp] += int(dump['global']['running'])
                if not launcher in zombies:
                    zombies[launcher] = {}
                if not stamp in zombies[launcher]:
                    zombies[launcher][stamp] = int(dump['global']['zombie'])
                else:
                    zombies[launcher][stamp] += int(dump['global']['zombie'])

            if 'loadavg' in dump:
                if not launcher in loads:
                    loads[launcher] = {}
                if not stamp in loads[launcher]:
                    loads[launcher][stamp] = int(dump['loadavg']['1min'])
                else:
                    loads[launcher][stamp] += int(dump['loadavg']['1min'])

            if 'fd' in dump:
                if not launcher in fds:
                    fds[launcher] = {}
                if not stamp in fds[launcher]:
                    fds[launcher][stamp] = sum(dump['fd'].values())
                else:
                    fds[launcher][stamp] += sum(dump['fd'].values())

            if 'by_group' in dump:
                # Prevent "None" from beeing eval'ed as None
                if None in dump['by_group']:
                    dump['by_group']["Other"] = dump['by_group'][None]
                    del dump['by_group'][None]

                # For each group available
                for group in dump['by_group'].keys():
                    if not group in groups:
                        groups[group] = {}
                    # If this group as already an entry for this time (from an other launcher), we add the new one
                    if stamp in groups[group]:
                        groups[group][stamp] += int(dump['by_group'][group]['running'])
                    else:
                        groups[group][stamp] = int(dump['by_group'][group]['running'])

    return (groups, runnings, zombies, loads, fds)

# Main Loop
if __name__ == "__main__":

    if len(sys.argv) < 4:
        sys.exit(
            f"Usage : {sys.argv[0]} '<start date>' '<end date>' <log1> <log2> ..."
        )
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
            group_hours = sorted(set(group_hours))
        # Sort groups data for pygraph
        for group in group_list:
            for hour in group_hours:
                if group not in groups_actions:
                    groups_actions[group] = []
                if hour in groups[group]:
                    groups_actions[group].append(groups[group][hour])
                else:
                    groups_actions[group].append(0)

            create_graph(
                "Time",
                "Number of actions",
                group_hours,
                {group: groups_actions[group]},
                f'group {group}  - {start_str}-{end_str}.png',
                "Running actions on group \"%s\" between %s and %s"
                % (group, start_str, end_str),
                start,
                stop,
                0,
                y_max,
            )
        create_graph(
            "Time",
            "Number of actions",
            group_hours,
            groups_actions,
            f'groups - {start_str}-{end_str}.png',
            f"Running actions per group between {start_str} and {end_str}",
            start,
            stop,
            0,
            y_max,
        )


    if runnings:
        launch_actions = {}
        launcher_list = runnings.keys()
        y_max = (max(map(lambda x: max(x.values()), runnings.values())) / 50 + 1) * 50

        # Get all launch hours
        for launch in launcher_list:
            launch_hours += runnings[launch].keys()
            launch_hours = sorted(set(launch_hours))
        # Sort launchers data for pygraph
        for launch in launcher_list:
            for hour in launch_hours:
                if launch not in launch_actions:
                    launch_actions[launch] = []
                if hour in runnings[launch]:
                    launch_actions[launch].append(runnings[launch][hour])
                else:
                    launch_actions[launch].append(0)
            create_graph(
                "Time",
                "Number of actions",
                launch_hours,
                {launch: launch_actions[launch]},
                f'{launch} - running - {start_str}-{end_str}.png',
                "Running actions on \"%s\" between %s and %s"
                % (launch, start_str, end_str),
                start,
                stop,
                0,
                y_max,
            )
        create_graph(
            "Time",
            "Number of actions",
            launch_hours,
            launch_actions,
            f'launchers - running - {start_str}-{end_str}.png',
            f"Running actions between {start_str} and {end_str}",
            start,
            stop,
            0,
            y_max,
        )

    if zombies:
        launch_zombies = {}
        launcher_list = zombies.keys()
        y_max = (max(map(lambda x: max(x.values()), zombies.values())) / 50 + 1) * 50

        # Get all launch hours
        for launch in launcher_list:
            launch_hours += zombies[launch].keys()
            launch_hours = sorted(set(launch_hours))
        # Sort launchers data for pygraph
        for launch in launcher_list:
            for hour in launch_hours:
                if not launch.launch_zombies:
                    launch_zombies[launch] = []
                if hour in zombies[launch]:
                    launch_zombies[launch].append(zombies[launch][hour])
                else:
                    launch_zombies[launch].append(0)
            create_graph(
                "Time",
                "Number of actions",
                launch_hours,
                {launch: launch_zombies[launch]},
                f'{launch} - zombies - {start_str}-{end_str}.png',
                "Zombies on \"%s\" between %s and %s"
                % (launch, start_str, end_str),
                start,
                stop,
                0,
                y_max,
            )
        create_graph(
            "Time",
            "Number of actions",
            launch_hours,
            launch_zombies,
            f'launchers - zombies - {start_str}-{end_str}.png',
            f"Zombies between {start_str} and {end_str}",
            start,
            stop,
            0,
            y_max,
        )

    if loads:
        launch_loads = {}
        launcher_list = loads.keys()
        y_max = (max(map(lambda x: max(x.values()), loads.values())) / 1 + 1) * 1

        # Get all launch hours
        for launch in launcher_list:
            launch_hours += loads[launch].keys()
            launch_hours = sorted(set(launch_hours))
        # Sort launchers data for pygraph
        for launch in launcher_list:
            for hour in launch_hours:
                if launch not in launch_loads:
                    launch_loads[launch] = []
                if hour in loads[launch]:
                    launch_loads[launch].append(loads[launch][hour])
                else:
                    launch_loads[launch].append(0)
            create_graph(
                "Time",
                "Load",
                launch_hours,
                {launch: launch_loads[launch]},
                f'{launch} - load - {start_str}-{end_str}.png',
                "Load on \"%s\" between %s and %s"
                % (launch, start_str, end_str),
                start,
                stop,
                0,
                y_max,
            )
        create_graph(
            "Time",
            "Load",
            launch_hours,
            launch_loads,
            f'launchers - load - {start_str}-{end_str}.png',
            f"Load between {start_str} and {end_str}",
            start,
            stop,
            0,
            y_max,
        )

    sys.exit(0)

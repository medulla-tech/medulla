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

from pychart import theme, color, canvas, font, axis, area, line_style, line_plot

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

    can = canvas.init(f"{filename}")

    # Draw graph title
    newtitle = f"/hL/20{title}"
    left = WIDTH / 2  - font.text_width(newtitle)/2
    can.show(left, HEIGHT + DELTA, newtitle)

    zip(data_x)
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
        minor_tic_interval=Y_MINOR_TICK_INTERVAL,
        tic_interval=Y_TICK_INTERVAL,
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

    # Draw a line for each columns
    for i, (title, data_y) in enumerate(alldata_y.iteritems()):
        plot = line_plot.T(
            label = title,
            data = zip(data_x,data_y),
            line_style = line_style.T(
                color = colors[i],
                width = 1
            )
        )
        ar.add_plot(plot)
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

                        if 'global' in dump:

                            if not launcher in launchers:
                                launchers[launcher] = {}
                            if stamp in launchers[launcher]:
                                launchers[launcher][stamp] += int(dump['global']['running'])
                            else:
                                launchers[launcher][stamp] = int(dump['global']['running'])

                        if 'by_group' in dump:

                            # For each group available
                            for group in dump['by_group'].keys():
                                if not group in groups:
                                    groups[group] = {}
                                # If this group as already an entry for this time (from an other launcher), we add the new one
                                if stamp in groups[group]:
                                    groups[group][stamp] += int(dump['by_group'][group]['running'])
                                else:
                                    groups[group][stamp] = int(dump['by_group'][group]['running'])
    return (groups,launchers)

# Main Loop
if __name__ == "__main__":

    if len(sys.argv) != 4:
        sys.exit(f"Usage : {sys.argv[0]} <logs_directory> '<start date>' '<end date>'")

    (log_dir, start_str, end_str) = sys.argv[1:]

    if not os.path.isdir(sys.argv[1]):
        sys.exit(f"ERROR, {sys.argv[1]} : no such directory.")

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
                "Horaires",
                "Nombre d'actions",
                group_hours,
                {group: groups_actions[group]},
                f'group {group}  - {start_str}-{end_str}.png',
                "Evolution du nombre d'actions en cours sur le group \"%s\" entre %s et %s"
                % (group, start_str, end_str),
                start,
                stop,
            )
        create_graph(
            "Horaires",
            "Nombre d'actions",
            group_hours,
            groups_actions,
            f'groups - {start_str}-{end_str}.png',
            f"Evolution du nombre d'actions en cours sur les differents groups entre {start_str} et {end_str}",
            start,
            stop,
        )


    if launchers:
        launcher_list = launchers.keys()

        # Get all launch hours
        for launch in launcher_list:
            launch_hours += launchers[launch].keys()
            launch_hours = sorted(set(launch_hours))
        # Sort launchers data for pygraph
        for launch in launcher_list:

            for hour in launch_hours:
                if launch not in launch_actions:
                    launch_actions[launch] = []
                if hour in launchers[launch]:
                    launch_actions[launch].append(launchers[launch][hour])
                else:
                    launch_actions[launch].append(0)

            create_graph(
                "Horaires",
                "Nombre d'actions",
                launch_hours,
                {launch: launch_actions[launch]},
                f'{launch} - {start_str}-{end_str}.png',
                "Evolution du nombre d'actions en cours sur le launcher \"%s\" entre %s et %s"
                % (launch, start_str, end_str),
                start,
                stop,
            )
        create_graph(
            "Horaires",
            "Nombre d'actions",
            launch_hours,
            launch_actions,
            f'launchers - {start_str}-{end_str}.png',
            f"Evolution du nombre d'actions en cours sur les differents launchers entre {start_str} et {end_str}",
            start,
            stop,
        )

    sys.exit(0)

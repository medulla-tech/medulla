#!/usr/bin/python
#
# (c) 2009 Mandriva, http://www.mandriva.com
#
# $Id: command_evolution_using_logs.py 4584 2009-09-30 13:58:54Z nrueff $
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
a simple Pulse 2 scheduler log analyser
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

HEALTH_REGEX = "([0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}):[0-9]{2},.*scheduler ([^:]*): HEALTH: (.*)"


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
        y_grid_interval = (end_y - start_y) / 5)

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
    Read scheduler logs in log_dir from start_date to stop_date
    """

    loadavg   = {}
    fds       = {}
    memory    = {}

    # Parse all log files in the directory
    for logfile in logfiles:

        try:
            fh = open(logfile)
        except IOError:
            print "can't read %s " % logfile
            continue

        print "parsing %s ... " % logfile
        for line in fh:  # Parse each line in the log file
            # Add the "BALANCE" test to avoid computing regexp if the line doesn't match
            res = re.search(HEALTH_REGEX, line)

            if not res:  # give up if line do not match
                continue

            stamp = int(time.mktime(time.strptime(res.group(1), '%Y-%m-%d %H:%M')))
            if (stamp < start_date or stamp > stop_date):  # give up if time do not match
                continue

            scheduler = res.group(2)
            dump = eval(res.group(3))

            if 'memory' in dump:
                if not scheduler in memory:
                    memory[scheduler] = {}
                if not stamp in memory[scheduler]:
                    memory[scheduler][stamp] = {}
                    memory[scheduler][stamp]    = int(dump['memory']['free'])
                else:
                    memory[scheduler][stamp]   += int(dump['memory']['free'])

            if 'loadavg' in dump:
                if not scheduler in loadavg:
                    loadavg[scheduler] = {}
                if not stamp in loadavg[scheduler]:
                    loadavg[scheduler][stamp] = int(dump['loadavg']['1min'])
                else:
                    loadavg[scheduler][stamp] += int(dump['loadavg']['1min'])

            if 'fd' in dump:
                if not scheduler in fds:
                    fds[scheduler] = {}
                if not stamp in fds[scheduler]:
                    fds[scheduler][stamp] = sum(dump['fd'].values())
                else:
                    fds[scheduler][stamp] += sum(dump['fd'].values())

    return (memory, loadavg, fds)

# Main Loop
if __name__ == "__main__":

    if len(sys.argv) < 4:
        sys.exit("Usage : %s '<start date>' '<end date>' <log1> <log2> ..." % sys.argv[0])
    (start_str, end_str) = sys.argv[1:3]
    logfiles = sys.argv[3:]

    sched_hours = []

    # Parse logs
    start = int(time.mktime(time.strptime(start_str, '%Y-%m-%d %H:%M')))
    stop = int(time.mktime(time.strptime(end_str, '%Y-%m-%d %H:%M')))
    (memory, loads, fds) = read_logs(logfiles, start, stop)

    if memory:
        sched_memory = {}
        scheduler_list = memory.keys()
        y_max = (max(map(lambda x: max(x.values()), memory.values())) / 1 + 1) * 1

        # Get all sched hours
        for sched in scheduler_list:
            sched_hours += memory[sched].keys()
            # deduplicate list
            sched_hours = list(set(sched_hours))
            sched_hours.sort()

        # Sort scheduler data for pygraph
        for sched in scheduler_list:
            for hour in sched_hours:
                if not sched in sched_memory:
                    sched_memory[sched] = []
                if hour in memory[sched]:
                    sched_memory[sched].append(memory[sched][hour])
                else:
                    sched_memory[sched].append(0)
            create_graph("Time", "Memory", sched_hours, {sched: sched_memory[sched]}, '%s - Memory - %s-%s.png' % (sched, start_str, end_str), "Memory on \"%s\" between %s and %s" % (sched, start_str, end_str), start, stop, 0, y_max)
        create_graph("Time", "Memory", sched_hours, sched_memory, 'schedulers - Memory - %s-%s.png' % (start_str, end_str), "Memory between %s and %s" % (start_str, end_str), start, stop, 0, y_max)

    if loads:
        sched_loads = {}
        scheduler_list = loads.keys()
        y_max = (max(map(lambda x: max(x.values()), loads.values())) / 1 + 1) * 1

        # Get all sched hours
        for sched in scheduler_list:
            sched_hours += loads[sched].keys()
            # deduplicate list
            sched_hours = list(set(sched_hours))
            sched_hours.sort()

        # Sort scheduler data for pygraph
        for sched in scheduler_list:
            for hour in sched_hours:
                if not sched in sched_loads:
                    sched_loads[sched] = []
                if hour in loads[sched]:
                    sched_loads[sched].append(loads[sched][hour])
                else:
                    sched_loads[sched].append(0)
            create_graph("Time", "Load", sched_hours, {sched: sched_loads[sched]}, '%s - load - %s-%s.png' % (sched, start_str, end_str), "Load on \"%s\" between %s and %s" % (sched, start_str, end_str), start, stop, 0, y_max)
        create_graph("Time", "Load", sched_hours, sched_loads, 'schedulers - load - %s-%s.png' % (start_str, end_str), "Load between %s and %s" % (start_str, end_str), start, stop, 0, y_max)

    if fds:
        sched_fds = {}
        scheduler_list = fds.keys()
        y_max = (max(map(lambda x: max(x.values()), fds.values())) / 1 + 1) * 1

        # Get all sched hours
        for sched in scheduler_list:
            sched_hours += fds[sched].keys()
            # deduplicate list
            sched_hours = list(set(sched_hours))
            sched_hours.sort()

        # Sort scheduler data for pygraph
        for sched in scheduler_list:
            for hour in sched_hours:
                if not sched in sched_fds:
                    sched_fds[sched] = []
                if hour in fds[sched]:
                    sched_fds[sched].append(fds[sched][hour])
                else:
                    sched_fds[sched].append(0)
            create_graph("Time", "Fds", sched_hours, {sched: sched_fds[sched]}, '%s - fds - %s-%s.png' % (sched, start_str, end_str), "Fds on \"%s\" between %s and %s" % (sched, start_str, end_str), start, stop, 0, y_max)
        create_graph("Time", "Fds", sched_hours, sched_fds, 'schedulers - fds - %s-%s.png' % (start_str, end_str), "Fds between %s and %s" % (start_str, end_str), start, stop, 0, y_max)

    sys.exit(0)

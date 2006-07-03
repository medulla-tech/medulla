#!/bin/sh
#
# Copyright (C) 2006 Linbox FAS
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# Run linbox-config at the first boot

set -e

PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
DESC="Linbox Management Console XML-RPC Agent"
NAME=lmc-agent
DAEMON=/usr/sbin/$NAME
PIDFILE=/var/run/$NAME.pid
SCRIPTNAME=/etc/init.d/$NAME

# Gracefully exit if the package has been removed.
test -x $DAEMON || exit 0

# Read config file if it is present.
if [ -r /etc/default/$NAME ]
  then
  . /etc/default/$NAME
fi

# If disabled in /etc/default/$NAME
case "$ENABLE" in
        [Nn]*)
                echo "$DESC disabled in /etc/default/$NAME."
		exit 0
                ;;
esac


#
#	Function that starts the daemon/service.
#
d_start() {
	start-stop-daemon --start --quiet --pidfile $PIDFILE \
		--exec $DAEMON
}

#
#	Function that stops the daemon/service.
#
d_stop() {
	start-stop-daemon --stop --quiet --pidfile $PIDFILE
	rm -f $PIDFILE
}

#
#	Function that sends a SIGHUP to the daemon/service.
#
#d_reload() {
#	start-stop-daemon --stop --quiet --pidfile $PIDFILE \
#		--name $NAME --signal 1
#}

case "$1" in
  start)
	echo -n "Starting $DESC: "
	if [ -f $PIDFILE ]
	  then
	    echo "pidfile found ! already running ?"
	  else
	    d_start && echo "done." || echo "failed."
	fi
	;;
  stop)
	echo -n "Stopping $DESC: "
	if [ ! -f $PIDFILE ]
	  then
	    echo "no pidfile found ! not running ?"
	  else
  	    d_stop && echo "done." || echo "failed."
	    rm -f $PIDFILE
	fi
	;;
  #reload)
	#
	#	If the daemon can reload its configuration without
	#	restarting (for example, when it is sent a SIGHUP),
	#	then implement that here.
	#
	#	If the daemon responds to changes in its config file
	#	directly anyway, make this an "exit 0".
	#
	# echo -n "Reloading $DESC configuration..."
	# d_reload
	# echo "done."
  #;;
  restart|force-reload)
	#
	#	If the "reload" option is implemented, move the "force-reload"
	#	option to the "reload" entry above. If not, "force-reload" is
	#	just the same as "restart".
	#
	echo -n "Restarting $DESC: "
	d_stop || true
	d_start && echo "done." || echo -e "failed."
	;;
  *)
	echo "Usage: $SCRIPTNAME {start|stop|restart|force-reload}" >&2
	exit 1
	;;
esac

exit 0

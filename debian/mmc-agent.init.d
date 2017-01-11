#!/bin/bash
### BEGIN INIT INFO
# Provides:          mmc-core
# Required-Start:    $local_fs $remote_fs $syslog $network $time
# Required-Stop:     $local_fs $remote_fs $syslog $network
# Should-Start:      mysql slapd
# Should-Stop:       mysql slapd
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: MMC agent
# Description:       Mandriva Management Console : mmc-agent
### END INIT INFO

# Author: Mandriva S.A.

# PATH should only include /usr/* if it runs after the mountnfs.sh script
PATH=/sbin:/usr/sbin:/bin:/usr/bin
DESC="Mandriva Management Console XML-RPC Agent"
NAME=mmc-agent
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


# Function that starts the daemon/service.
d_start() {
	start-stop-daemon --start --quiet --pidfile $PIDFILE \
		--exec $DAEMON
}

# Function that stops the daemon/service.
d_stop() {
	start-stop-daemon --stop --quiet --pidfile $PIDFILE
	rm -f $PIDFILE
}

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
  restart|force-reload)
	echo -n "Restarting $DESC: "
	d_stop || true
	d_start && echo "done." || echo "failed."
	;;
  reload)
	echo -n "Reloading $DESC: "
	$DAEMON --reload && echo "done." || echo "failed."
	;;
  *)
	echo "Usage: $SCRIPTNAME {start|stop|restart|force-reload}" >&2
	exit 1
	;;
esac

exit 0

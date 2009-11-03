/*
 * (c) 2009 Nicolas Rueff / Mandriva, http://www.mandriva.com
 *
 * $Id: pulse2-imaging-server.c 4713 2009-11-02 14:20:32Z nrueff $
 *
 * This file is part of Pulse 2, http://pulse2.mandriva.org
 *
 * Pulse 2 is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * Pulse 2 is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with Pulse 2; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
 * MA 02110-1301, USA.
 */

#include <stdio.h>
#include <stdarg.h>
#include <sys/types.h>
#include <fcntl.h>
#include <sys/socket.h>
#include <unistd.h>
#include <math.h>
#include <errno.h>
#include <ctype.h>
#include <syslog.h>
#include <time.h>
#include <dirent.h>

#ifdef S_SPLINT_S
# include "/usr/local/splint/include/arpa/inet.h"
#else
# include <arpa/inet.h>
#endif
#include <netinet/in.h>

#include "iniparser.h"

#define BUFLEN 1532
#define PORT 1001
#define CONFIGURATION_FILE "/etc/mmc/pulse2/imaging-server/imaging-server.ini";
#define PID_FILE "/var/run/pulse2-imaging-server.pid"

unsigned char gBuff[80];
unsigned char basedir[255];
dictionary *ini;
char etherpath[255];
char logtxt[256];

const char * gConfigurationFile = CONFIGURATION_FILE;
const char * gPIDFile= PID_FILE;

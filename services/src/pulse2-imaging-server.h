/*
 * (c) 2009-2010 Mandriva, http://www.mandriva.com
 *
 * $Id$
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

#ifndef PULSE_IMAGING_SERVER_H
#define PULSE_IMAGING_SERVER_H

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
#define CONFIGURATION_FILE "/etc/mmc/pulse2/imaging-server/imaging-server.ini";

unsigned char gBuff[80];

char *gConfigurationFile = CONFIGURATION_FILE;

// global config options, main section
char *gHost;
int gPort = 0;
char *gAdminPass;
// global config options, helpers section
char *gDirHooks;
char *gPathProcessInventory;
char *gPathCreateClient;
char *gPathCreateImage;
char *gPathUpdateClient;
char *gPathUpdateImage;
char *gPathLogAction;
char *gPathGetUUID;
char *gPathMTFTPSync;
// global config options, daemon section
char *gUser;
char *gGroup;
int gUMask;
char *gPIDFile;
// global config options, logs section
char *gLogFile;
dictionary *ini;

#endif                          //PULSE_IMAGING_SERVER_H

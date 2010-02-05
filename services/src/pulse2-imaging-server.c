/*
 * (c) 2003-2007 Linbox FAS, http://linbox.com
 * (c) 2008-2009 Mandriva, http://www.mandriva.com
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

#include "pulse2-imaging-server.h"

void initlog(void) {
    openlog("pulse2-imaging-server", 0, LOG_DAEMON | LOG_LOCAL3);
}

/*
 * logging
 */

int myLogger(char* msg) {
    char cmd[1024];
    snprintf(cmd, 1023, "echo \"`date --rfc-3339=seconds` %.900s\" 1>>%s 2>&1", msg, gLogFile);
    return (system(cmd));
}

void logClientActivity( char *smac, int priority, const char *format_str, ... )
{
    va_list ap;
    FILE *f;
    char buf[1024], path[256];

    /* write some info */
    va_start( ap, format_str );
    vsnprintf( buf, 1023, format_str, ap );
    va_end(ap);

    snprintf(path, 255, "%s/images/%s/log", gBaseDir, smac);
    if ((f = fopen(path, "a"))) {
        time_t now;
        char tm[64];

        time(&now);
        strcpy(tm, ctime(&now));
        tm[strlen(tm) - 1] = '\000';
        fprintf(f, "%s: %s\n", tm, buf);
        fclose(f);

        /* log the last restoration */
        if (strstr(buf, "restoration comp") != NULL) {
            snprintf(path, 255, "%s/images/%s/log.lastrestore", gBaseDir, smac);
            if ((f = fopen(path, "w"))){
                fprintf(f, "%s: %s\n", tm, buf);
                fclose(f);
            }
        }

        syslog(priority, buf);

        /* keep only the last 20 lines of the log */
        snprintf(buf, 1023, "%s/bin/rotatelog %s", gBaseDir, path);
        system(buf);
      }
    else
      {
        syslog(priority, buf);
      }
}


void hex2char(char *ptr, char *val)
{
    if ((ptr[1] >= 'A') && (ptr[1] <= 'F'))
        *val = ptr[1] - 'A' + 10;
    else if ((ptr[1] >= 'a') && (ptr[1] <= 'f'))
        *val = ptr[1] - 'a' + 10;
    else if ((ptr[1] >= '0') && (ptr[1] <= '9'))
        *val = ptr[1] - '0';
    else {
        *val = 0;
        return;
    }

    if ((ptr[0] >= 'A') && (ptr[0] <= 'F'))
        *val += (16 * (ptr[0] - 'A' + 10));
    else if ((ptr[0] >= 'a') && (ptr[0] <= 'f'))
        *val += (16 * (ptr[0] - 'a' + 10));
    else if ((ptr[0] >= '0') && (ptr[0] <= '9'))
        *val += (16 * (ptr[0] - '0'));
    else {
        *val = 0;
        return;
    }
}

void diep(char *s)
{
    time_t now;
    char *ts;

    time(&now);
    ts = ctime(&now) + 4;
    ts[20] = '\0';

    if (errno) {
        perror(s);
    } else {
        puts(s);
    }
    syslog(LOG_ERR, s);
    exit(1);
}

/*
 * system() func with logging
 */
int mysystem(const char *s)
{
    char cmd[1024];

    snprintf(cmd, 1023, "echo \"`date --rfc-3339=seconds` %.900s\" 1>>%s 2>&1", s, gLogFile);
    system(cmd);

    snprintf(cmd, 1023, "%.900s 1>>%s 2>&1", s, gLogFile);
    return (system(cmd));
}

/*
 * Get the number of entries
 */
unsigned int getentries(unsigned char *file)
{
    FILE *fi;
    unsigned int s = 0;
    char buf[100];

    fi = fopen((char *)file, "r");
    if (!fi)
        return 0;
    while (fgets(buf, 100, fi))
        if ((buf[0] != '#') && (buf[0] != ';') && (strlen(buf) > 10))
            s++;
    fclose(fi);

    return s;
}

/*
 * get the name corresponding to a MAC addr
 */
int getentry(char *file, char *pktmac)
{
    FILE *fi;
    unsigned int s = 0;
    char buf[100], mac[20], name[33];

    fi = fopen(file, "r");
    if (!fi)
        return 0;
    while (fgets(buf, 100, fi)) {
        if ((buf[0] != '#') && (buf[0] != ';') && (strlen(buf) > 10)) {
            s++;
            if (sscanf(buf, "%19s%*s%32s", mac, name) == 2) {
                //printf("%s*%s\n", mac, name);
                if (!strncasecmp(mac, pktmac, 17)) {
                    /* return the name in the global buffer */
                    strcpy((char *)gBuff, name);
                    fclose(fi);
                    return 1;
                }
            }
        }
    }
    fclose(fi);

    return 0;
}

/*
 *  get mac from the ARP cache
 */
unsigned char *getmac(struct in_addr addr)
{
    FILE *fi;
    unsigned char *ptr;
    char straddr[80];
    int l;

    strcpy(straddr, inet_ntoa(addr));
    l = strlen(straddr);
    straddr[l] = ' ';
    straddr[l + 1] = '\0';

    myLogger("Warning: MAC not found in packet");
    fi = fopen("/proc/net/arp", "r");
    if (!fi) { //can't open file
        myLogger("can't open /proc/net/arp");
        return 0;
    }
    while (fgets((char *)gBuff, 80, fi)) {
        if (strstr((char *)gBuff, straddr)) {
            ptr = (unsigned char *) strchr((char *) gBuff, ':') - 2;
            ptr[17] = 0;
            return ptr;
        }
    }
    return NULL;
}

/*
 *  get the mac from data embedded in the request
 *
 *  format: "Mc:xx:xx:xx:xx:xx:xx" at the end of the packet
 */
unsigned char *getmacfrompkt(char *buf, int l)
{
    if (l <= 20)
        return NULL;
    // check for a magic number and for ':' x6
    if (buf[l - 20] == 'M' && buf[l - 19] == 'c' && buf[l - 18] == ':'
        && buf[l - 15] == ':' && buf[l - 12] == ':' && buf[l - 9] == ':'
        && buf[l - 6] == ':' && buf[l - 3] == ':') {
        // let's copy the mac address
        strncpy((char *)gBuff, buf + l - 17, 17);
        gBuff[17] = 0;
        return gBuff;
    }
    return NULL;
}

/*
 * Process an incoming packet
 */
int process_packet(unsigned char *buf, char *mac, char *smac,
                   struct sockaddr_in *si_other, int s)
{
    char command[256], name[256];
    FILE *fo;
    static unsigned int lastfile = 0, lasttime = 0;

    /* do not log, log requests ! */
    if (buf[0] != 'L' && buf[0] != 0xCD) {
        char *buff = malloc(256);

        snprintf(buff, 255, "Packet from %s:%d, MAC Address:%s, Command: %02x",
             inet_ntoa(si_other->sin_addr), ntohs(si_other->sin_port), mac,
             buf[0]);
        myLogger(buff);
        free(buff);
    }

    // Hardware Info...
    if (buf[0] == 0xAA) {
        snprintf(command, 255, "%s %s", gMenuUpdatePath, smac);
        mysystem(command);
        /* write inventory to file. Must fit in one packet ! */
        snprintf(name, 255, "%s/%s.inf", gInventoryDir, smac);
        if (!(fo = fopen(name, "w"))) { //can't create .inf file
            char *msg = malloc(256);
            sprintf(msg, "can't create %s", name);
            myLogger(msg);
            free(msg);
            return 0;
        }
        fprintf(fo, ">>>Packet from %s:%d\nMAC Address:%s\n%s\n<<<\n",
                inet_ntoa(si_other->sin_addr),
                ntohs(si_other->sin_port), mac, buf + 1);
        snprintf(command, 255, "%s %s/%s.inf %s/%s.ini",
                gClientInventoryPath, gInventoryDir, smac, gInventoryDir, smac);
        fclose(fo);
        mysystem(command);
        return 0;
    }
    // identification
    if (buf[0] == 0xAD) {
        char *ptr, pass[256], hostname[256], buff[256];


        ptr = strrchr((char *)buf + 3, ':');
        *ptr = 0;
        strcpy(pass, ptr + 1);
        strcpy(hostname, (char*)buf + 3);

        snprintf(buff, 255, "Identification from %s:%d (%s) as %s",
                inet_ntoa(si_other->sin_addr),
                ntohs(si_other->sin_port), mac, hostname);
        myLogger(buff);

        snprintf(command, 255, "%s %s %s %s", gClientAddPath, mac, hostname, pass);
        mysystem(command);
        return 0;
    }
    // before a save
    if (buf[0] == 0xEC) {
        snprintf(command, 255, "%s %s %c", gStorageUpdatePath, smac, buf[1]);
        mysystem(command);
        return 0;
    }
    // change menu default
    if (buf[0] == 0xCD) {
        snprintf(command, 255, "%s %s %d", gMenuResetPath, smac, buf[1]);
        mysystem(command);
        logClientActivity(smac, LOG_INFO, "%s default set to %d", mac, buf[1]);
        return 0;
    }
    // log data
    if (buf[0] == 'L') {
        switch (buf[1]) {
        case '0':
            logClientActivity(smac, LOG_INFO, "%s booted", mac);
            break;
        case '1':
            logClientActivity(smac, LOG_INFO, "%s executing menu entry %d",
                   mac, buf[2]);
            break;
        case '2':
            if (buf[2] == '-') {
                logClientActivity(smac, LOG_INFO, "%s restoration started (%s)", mac, &buf[3]);
            } else {
                logClientActivity(smac, LOG_INFO, "%s restoration started", mac);
            }
            break;
        case '3':
            if (buf[2] == '-') {
                logClientActivity(smac, LOG_INFO, "%s restoration completed (%s)", mac, &buf[3]);
            } else {
                logClientActivity(smac, LOG_INFO, "%s restoration completed", mac);
            }
            lasttime = 0;       /* reset MTFTP time barriers */
            lastfile = 0;
            break;
        case '4':
            if (buf[2] == '-') {
                logClientActivity(smac, LOG_INFO, "%s backup started (%s)", mac, &buf[3]);
            } else {
                logClientActivity(smac, LOG_INFO, "%s backup started", mac);
            }
            break;
        case '5':
            if (buf[2] == '-') {
                int bn;

                logClientActivity(smac, LOG_INFO, "%s backup completed (%s)", mac, &buf[3]);
                if (sscanf((char*)&buf[3], "Local-%d", &bn) == 1) {
                        // Local backup
                        snprintf(command, 255, "chown -R 0:0 %s/images/%s/Local-%d", gBaseDir, smac, bn);
                        system(command);
                } else if (sscanf((char*)&buf[3], "Base-%d", &bn) == 1) {
                        // Shared backup
                        snprintf(command, 255, "chown -R 0:0 %s/imgbase/Base-%d", gBaseDir, bn);
                        system(command);
                }
            } else {
                logClientActivity(smac, LOG_INFO, "%s backup completed", mac);
            }
            break;
        case '6':
            logClientActivity(smac, LOG_INFO, "%s postinstall started", mac);
            break;
        case '7':
            logClientActivity(smac, LOG_INFO, "%s postinstall completed", mac);
            break;
        case '8':
            logClientActivity(smac, LOG_INFO, "%s critical error", mac);
            break;

        }
        return 0;
    }
    // return me my Pulse 2 name
    if (buf[0] == 0x1A) {
        if (getentry(etherpath, mac)) {
            //to.sin_family = AF_INET;
            //to.sin_port = htons(1001);
            //inet_aton(inet_ntoa(si_other.sin_addr), &to.sin_addr);
            sendto(s, gBuff, strlen((char*)gBuff)+1, MSG_NOSIGNAL,
                   (struct sockaddr *) si_other, sizeof(*si_other));
        }
        return 0;
    }
    /* time synchro */
    if (buf[0] == 'T') {
      char pnum;
      int bnum, to;

      if (sscanf((char*)buf, "T;%c%d;%d", &pnum, &bnum, &to) == 3) {
        unsigned int file = (pnum<<16) + bnum;
        int wait = 0;

        if (time(NULL) - lasttime > 3600) {
            lasttime = 0;       /* reset MTFTP time barriers */
            lastfile = 0;
        }

        if (file == lastfile) {
          /* wait barrier */
          wait = to + (lasttime - time(NULL));
          if (wait < 0) wait = 0;
        } else if (file < lastfile) {
          wait = 0;
        } else if (file > lastfile) {
          /* reinit barrier */
          wait = to;
          if (lasttime == 0) wait=wait+10; /* 1st wait after a boot */
          lastfile = file;
          lasttime = time(NULL);
        }
        //printf("%c %d %d %d\n", pnum, bnum, to, wait);

        sprintf((char*)buf, "%d", wait);
        sendto(s, buf, strlen((char*)buf), MSG_NOSIGNAL,
               (struct sockaddr *) si_other, sizeof(*si_other));

        return 0;
      }
    }

    return 1;
}

void readConfig(char * config_file_path) {
    char *str;

    ini = iniparser_load(config_file_path);

    if (ini == NULL) {
        char *msg = malloc(256); bzero(msg, 256);
        sprintf(msg, "cannot parse file %s", config_file_path);
        diep(msg);
    }

    // Parse MAIN section //
    if ((str = iniparser_getstr(ini, "main:host"))) {
        strncpy((char*)gHost, str, 254);
    } else {
        char *msg = malloc(256); bzero(msg, 256);
        sprintf(msg, "keyword 'host' not found in section 'main' in file %s", config_file_path);
        diep(msg);
    }
    if ((gPort = iniparser_getint(ini, "main:port", 0))) {
    } else {
        char *msg = malloc(256); bzero(msg, 256);
        sprintf(msg, "keyword 'port' not found in section 'main' in file %s", config_file_path);
        diep(msg);
    }
    if ((str = iniparser_getstr(ini, "main:adminpass"))) {
        strncpy((char*)gAdminPass, str, 254);
    } else {
        char *msg = malloc(256); bzero(msg, 256);
        sprintf(msg, "keyword 'adminpass' not found in section 'main' in file %s", config_file_path);
        diep(msg);
    }


    // Parse FOLDERS section //
    if ((str = iniparser_getstr(ini, "directories:base_folder"))) {
        strncpy((char*)gBaseDir, str, 254);
    } else {
        char *msg = malloc(256); bzero(msg, 256);
        sprintf(msg, "keyword 'base_folder' not found in section 'directories' in file %s", config_file_path);
        diep(msg);
    }
    if ((str = iniparser_getstr(ini, "directories:inventories_folder"))) {
        strncpy((char*)gInventoryDir, str, 254);
    } else {
        char *msg = malloc(256); bzero(msg, 256);
        sprintf(msg, "keyword 'inventories_folder' not found in section 'directories' in file %s", config_file_path);
        diep(msg);
    }

    // Parse DAEMON section //
    if ((str = iniparser_getstr(ini, "daemon:user"))) {
        strncpy((char*)gUser, str, 254);
    } else {
        char *msg = malloc(256); bzero(msg, 256);
        sprintf(msg, "keyword 'user' not found in section 'daemon' in file %s", config_file_path);
        diep(msg);
    }
    if ((str = iniparser_getstr(ini, "daemon:group"))) {
        strncpy((char*)gGroup, str, 254);
    } else {
        char *msg = malloc(256); bzero(msg, 256);
        sprintf(msg, "keyword 'group' not found in section 'daemon' in file %s", config_file_path);
        diep(msg);
    }
    if ((str = iniparser_getstr(ini, "daemon:umask"))) {
        strncpy((char*)gUMask, str, 254);
    } else {
        char *msg = malloc(256); bzero(msg, 256);
        sprintf(msg, "keyword 'umaks' not found in section 'daemon' in file %s", config_file_path);
        diep(msg);
    }
    if ((str = iniparser_getstr(ini, "daemon:pidfile"))) {
        strncpy((char*)gPIDFile, str, 254);
    } else {
        char *msg = malloc(256); bzero(msg, 256);
        sprintf(msg, "keyword 'pidfile' not found in section 'daemon' in file %s", config_file_path);
        diep(msg);
    }

    // Parse HELPERS section //
    if ((str = iniparser_getstr(ini, "helpers:menu_update_path"))) {
        strncpy((char*)gMenuUpdatePath, str, 254);
    } else {
        char *msg = malloc(256); bzero(msg, 256);
        sprintf(msg, "keyword 'menu_update_path' not found in section 'helpers' in file %s", config_file_path);
        diep(msg);
    }
    if ((str = iniparser_getstr(ini, "helpers:client_inventory_path"))) {
        strncpy((char*)gClientInventoryPath, str, 254);
    } else {
        char *msg = malloc(256); bzero(msg, 256);
        sprintf(msg, "keyword 'client_inventory_path' not found in section 'helpers' in file %s", config_file_path);
        diep(msg);
    }
    if ((str = iniparser_getstr(ini, "helpers:client_add_path"))) {
        strncpy((char*)gClientAddPath, str, 254);
    } else {
        char *msg = malloc(256); bzero(msg, 256);
        sprintf(msg, "keyword 'client_add_path' not found in section 'helpers' in file %s", config_file_path);
        diep(msg);
    }
    if ((str = iniparser_getstr(ini, "helpers:client_remove_path"))) {
        strncpy((char*)gClientRemovePath, str, 254);
    } else {
        char *msg = malloc(256); bzero(msg, 256);
        sprintf(msg, "keyword 'client_remove_path' not found in section 'helpers' in file %s", config_file_path);
        diep(msg);
    }
    if ((str = iniparser_getstr(ini, "helpers:storage_create_path"))) {
        strncpy((char*)gStorageCreatePath, str, 254);
    } else {
        char *msg = malloc(256); bzero(msg, 256);
        sprintf(msg, "keyword 'storage_create_path' not found in section 'helpers' in file %s", config_file_path);
        diep(msg);
    }
    if ((str = iniparser_getstr(ini, "helpers:storage_update_path"))) {
        strncpy((char*)gStorageUpdatePath, str, 254);
    } else {
        char *msg = malloc(256); bzero(msg, 256);
        sprintf(msg, "keyword 'storage_update_path' not found in section 'helpers' in file %s", config_file_path);
        diep(msg);
    }
    if ((str = iniparser_getstr(ini, "helpers:menu_reset_path"))) {
        strncpy((char*)gMenuResetPath, str, 254);
    } else {
        char *msg = malloc(256); bzero(msg, 256);
        sprintf(msg, "keyword 'menu_reset_path' not found in section 'helpers' in file %s", config_file_path);
        diep(msg);
    }

    // Parse LOGGERS section //
    if ((str = iniparser_getstr(ini, "logger:log_file_path"))) {
        strncpy((char*)gLogFile, str, 254);
    } else {
        char *msg = malloc(256); bzero(msg, 256);
        sprintf(msg, "keyword 'log_file_path' not found in section 'logger' in file %s", config_file_path);
        diep(msg);
    }

    myLogger("Configuration parsed");
}

/* MAIN */
int main(void)
{
    struct sockaddr_in si_me, si_other, si_tcp;
    int s, slen = sizeof(si_other), plen, stcp;
    unsigned char buf[BUFLEN];
    unsigned int nb;
    char smac[20];
    char *mac;
    fd_set fds;
    int on = 1;
    int pidFileFD;
    int pid = 0;
    char pidBuff[5]; bzero(pidBuff, 5);

    syslog(LOG_INFO, "pulse2-imaging-server r.$Revision$");

    gBaseDir[0] = 0;

    initlog();
    readConfig(gConfigurationFile);

    /* Daemonize here */
    if (( daemon(0, 0) != 0)) diep("daemon");

    pid = getpid();
    if (pid) {
        char *msg = malloc(256); bzero (msg, 256);
        sprintf(msg, "Daemonization succedeed, PID is %d", pid);
        syslog(LOG_INFO, msg);
    } else {
        diep("daemon");
    }

    /* */
    sprintf(etherpath, "%s/etc/ether", gBaseDir);

    if ((s = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)) == -1) diep("udp socket");
    if ((stcp = socket(AF_INET, SOCK_STREAM, 0)) == -1) diep("tcp socket");

    /* UDP sock */
    memset((char *) &si_me, sizeof(si_me), 0);
    si_me.sin_family = AF_INET;
    si_me.sin_port = htons(gPort);
    si_me.sin_addr.s_addr = htonl(INADDR_ANY);
    if (bind(s, (struct sockaddr *) &si_me, sizeof(si_me)) == -1) diep("bind UDP");

    /* TCP sock */
    if (setsockopt (stcp, SOL_SOCKET, SO_REUSEADDR, &on, sizeof(on)) != 0) syslog (LOG_DEBUG, "SO_REUSEADDR failed");

    memset((char *) &si_tcp, sizeof(si_tcp), 0);
    si_tcp.sin_family = AF_INET;
    si_tcp.sin_port = htons(gPort);
    si_tcp.sin_addr.s_addr = htonl(INADDR_ANY);
    if (bind(stcp, (struct sockaddr *) &si_tcp, sizeof(si_tcp)) == -1) diep("bind TCP");
    listen(stcp, 1000);

    pidFileFD = open((char *)gPIDFile, O_WRONLY | O_CREAT | O_TRUNC);
    if (pidFileFD == -1) diep("PID file");
    snprintf(pidBuff, 5, "%d", pid);
    write(pidFileFD, pidBuff, strlen(pidBuff));
    close(pidFileFD);

    while (1) {
        int so;                 /* tcp/udp stream FD */
        /* select */
        FD_ZERO(&fds);
        FD_SET(s, &fds);
        FD_SET(stcp, &fds);

        select(stcp + 1, &fds, NULL, NULL, NULL);
        if (FD_ISSET(stcp, &fds)) {
            so = accept(stcp, (struct sockaddr *) &si_other, (unsigned int *)&slen);
            if (so == -1)
                continue;
            if ((plen =
                 recvfrom(so, buf, BUFLEN, 0,
                          (struct sockaddr *) NULL, NULL)) == -1)
                diep("recvfrom()");
        } else if (FD_ISSET(s, &fds)) {
            so = s;
            if ((plen =
                 recvfrom(so, buf, BUFLEN, 0,
                          (struct sockaddr *) &si_other, (unsigned int *)&slen)) == -1)
                diep("recvfrom()");

        } else {
            continue;
        }

        /* UDP only */
        if ((mac = (char*)getmacfrompkt((char*)buf, plen))) {
            // got it from the request ! good !
        } else {
            // Pas beau...(utilise le cache ARP) (for backward compatibility)
            mac = (char*)getmac(si_other.sin_addr);
        }
        if (!mac) {
            strcpy((char*)gBuff, "?");
            mac = (char*)gBuff;
        }
        /* client port must be 1001 ! */
        if (ntohs(si_other.sin_port) != 1001) {
          if (so != s)
            close(so);
          continue;
        }

        /* short mac */
        sprintf(smac, "%c%c%c%c%c%c%c%c%c%c%c%c", mac[0], mac[1], mac[3],
                mac[4], mac[6], mac[7], mac[9], mac[10], mac[12], mac[13],
                mac[15], mac[16]);

        /* process */
        process_packet(buf, mac, smac, &si_other, so);

        /* eventually close the tcp stream */
        if (so != s)
            close(so);

        nb = getentries((unsigned char*)etherpath);
    }


    close(s);
    return 0;
}

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

  #include <arpa/inet.h>
  #include <netinet/in.h>
  #include <stdio.h>
  #include <sys/types.h>
  #include <sys/socket.h>
  #include <unistd.h>

  #define BUFLEN 1532
  #define PORT 999

  void diep(char *s)
  {
    perror(s);
    exit(1);
  }

  unsigned char buff[80];

  unsigned char *getmac(struct in_addr addr)
  {
        FILE *fi;
        char *ptr;

        fi=fopen("/proc/net/arp","rt");
        while (fgets(buff,80,fi))
        {
         if (strstr(buff,inet_ntoa(addr)))
          {ptr=(unsigned char *)strchr((char*)buff,':')-2;
           ptr[17]=0;
           return ptr;}
        }
        return NULL;
  }

  int main(void)
  {
    struct sockaddr_in si_me, si_other;
    int s, i, slen=sizeof(si_other);
    char buf[BUFLEN],*mac;
    FILE *fo;
    char name[255],smac[20],command[255];

    if ((s=socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP))==-1)
      diep("socket");

    memset((char *) &si_me, sizeof(si_me), 0);
    si_me.sin_family = AF_INET;
    si_me.sin_port = htons(PORT);
    si_me.sin_addr.s_addr = htonl(INADDR_ANY);
    if (bind(s, (struct sockaddr *)&si_me, sizeof(si_me))==-1)
        diep("bind");

    while (1)
    {
     if (recvfrom(s, buf, BUFLEN, 0, (struct sockaddr *)&si_other, &slen)==-1)
        diep("recvfrom()");
     mac=getmac(si_other.sin_addr);
     printf(">>>Packet from %s:%d\nMAC Address:%s\n%s\n<<<\n",
             inet_ntoa(si_other.sin_addr),
             ntohs(si_other.sin_port),mac, buf);
     sprintf(smac,"%c%c%c%c%c%c%c%c%c%c%c%c",
                                                  mac[0],mac[1],
                                                  mac[3],mac[4],
                                                  mac[6],mac[7],
                                                  mac[9],mac[10],
                                                  mac[12],mac[13],
                                                  mac[15],mac[16]);
     sprintf(name,"/tftpboot/revoboot/log/%s.inf",smac);
     fo=fopen(name,"wt");
     fprintf(fo,">>>Packet from %s:%d\nMAC Address:%s\n%s\n<<<\n",
             inet_ntoa(si_other.sin_addr),
             ntohs(si_other.sin_port),mac, buf);
     sprintf(command,"/tftpboot/revoboot/bin/info /tftpboot/revoboot/log/%s.inf >/tftpboot/revoboot/log/%s.ini",smac,smac);
     fclose(fo);
     system(command);
    }

    close(s);
    return 0;
  }

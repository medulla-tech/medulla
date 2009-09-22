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
 *
 * gznbd.c. NBD to mount LRS image files.
 *
 * bench: ls -lR on /home/test/A* : 7"04', 4"38'
 *
 */

#include <stdio.h>
#include <stdlib.h>
#include <zlib.h>
#include <errno.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>

#include <sys/ioctl.h>
#include <sys/types.h>
#include <sys/socket.h>

#include <netinet/in.h>
#include <asm/types.h>

#define u32 __u32
#define u64 __u64

#include <linux/nbd.h>

#define BLOCK 1024
#define CHUNK BLOCK*1024

#define INSIZE 2048
#define DEBUG(x)

unsigned char *BUFFER;
unsigned char *Bitmap;
unsigned char *IN;
unsigned char zero[512];
unsigned char *all;

typedef struct params_
{
  int bitindex;
  int fo;
  unsigned long long offset;
} PARAMS;


/* taken litterally from the original nbd */
#ifdef WORDS_BIGENDIAN
u64 ntohll(u64 a)
{
  return a;
}
#else
u64 ntohll(u64 a)
{
  u32 lo = a & 0xffffffff;
  u32 hi = a >> 32U;
  lo = ntohl(lo);
  hi = ntohl(hi);
  return ((u64) lo) << 32U | hi;
}
#endif

/*
 * Decompress to RAM
 */
void *
flushToDisk (unsigned char *buff, unsigned char *bit, PARAMS * cp, int lg)
{
  unsigned char *ptr = buff;
  unsigned char mask[] = { 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80 };
  int indx = cp->bitindex;

  // printf("Enter : bitindex -> %d\n",indx);
  while (lg > 0)
    {
      while (!(bit[indx >> 3] & mask[indx & 7]))
        {
          indx++;
          cp->offset += 512;
        }
      memcpy (&all[cp->offset], ptr, 512);
      cp->offset += 512;
      ptr += 512;
      indx++;
      lg -= 512;
    }
  cp->bitindex = indx;
  return NULL;

}


/* decompress a file in memory */
void decompress_file(char *prefix, int file, int offset)
{

  /*  */
  z_stream zptr;
  int state, fmax = -1;
  int ret, firstpass, bitmaplg;
  FILE *fi;
  PARAMS currentparams;

  /* open another chunk */
  char filename[256];

  /* clear memory buffer */
  memset(all, 0, 1024*88064);

  state = Z_SYNC_FLUSH;
  firstpass = 1;
  bitmaplg = 0;

  zptr.zalloc = NULL;
  zptr.zfree = NULL;

  sprintf(filename, "%s%03d", prefix, file);

  fi = fopen (filename, "r");
  if (fi == NULL)
    {
      printf ("Cannot open input file %s\n", filename);
    }

  DEBUG(printf("New file opened: %s\n", filename));

  zptr.avail_in = fread (IN, 1, INSIZE, fi);

  currentparams.fo = 0;
  currentparams.offset = 0;
  currentparams.bitindex = 0;

  zptr.next_in = (char *) IN;
  zptr.next_out = (char *) BUFFER;      // was dbuf.data;
  zptr.avail_out = 24064;

  inflateInit (&zptr);

  do
    {
      ret = inflate (&zptr, state);

      /* output buffer full */
      if ((ret == Z_OK) && (zptr.avail_out == 0))
        {
          if (firstpass)
            {
              DEBUG (printf ("Params : *%s\n", BUFFER));
              if (strstr (BUFFER, "BLOCKS="))
                {
                  int i = 0;
                  if (sscanf (strstr (BUFFER, "BLOCKS=") + 7, "%d", &i) == 1) {
                    fmax = i;
                  }
                }
              if (strstr (BUFFER, "ALLOCTABLELG="))
                sscanf (strstr (BUFFER, "ALLOCTABLELG=") + 13, "%d",
                        &bitmaplg);
              memcpy (Bitmap, BUFFER + 2048, 24064 - 2048);
              currentparams.bitindex = 0;
              firstpass = 0;
            }
          else
            {
              flushToDisk (BUFFER, Bitmap, &currentparams, 24064);
            }

          zptr.next_out = (char *) BUFFER;
          zptr.avail_out = 24064;

        }

      /* no more data in */
      if ((ret == Z_OK) && (zptr.avail_in == 0))
        {
          zptr.avail_in = fread (IN, 1, INSIZE, fi);
          zptr.next_in = (char *) IN;
        }
    }
  while (ret == Z_OK);

  /* end of file */
  if (ret == Z_STREAM_END)
    {
      {
        if (firstpass)
          {
            /* only one block */
            DEBUG (printf ("Params : *%s*\n", BUFFER));
            if (strstr (BUFFER, "BLOCKS="))
              {
                int i = 0;
                if (sscanf (strstr (BUFFER, "BLOCKS=") + 7, "%d", &i) == 1) {
                  fmax = i;
                }
              }
            if (strstr (BUFFER, "ALLOCTABLELG="))
              sscanf (strstr (BUFFER, "ALLOCTABLELG=") + 13, "%d",
                      &bitmaplg);
            memcpy (Bitmap, BUFFER + 2048, 24064 - 2048);
            zptr.next_out = (char *) BUFFER;
            zptr.avail_out = 24064;
          }
      }

      flushToDisk (BUFFER, Bitmap, &currentparams, 24064 - zptr.avail_out);
      zptr.next_out = (char *) BUFFER;
      zptr.avail_out = 24064;
    }

  ret = inflate (&zptr, Z_FINISH);
  inflateEnd (&zptr);

  /* ERROR */
  if (ret < 0)
    {
      printf ("Returned : %d\t", ret);
      printf ("(AvailIn : %d / ", zptr.avail_in);
      printf ("AvailOut: %d)\n", zptr.avail_out);
      printf ("(TotalIn : %ld / ", zptr.total_in);
      printf ("TotalOut: %ld)\n", zptr.total_out);
    }

  if (bitmaplg)
    {
      if (bitmaplg * 8 > currentparams.bitindex)
        {
          currentparams.offset +=
            512 * (bitmaplg * 8 - currentparams.bitindex);
          if (currentparams.fo)
            {
              // why fill ?
              //fill(currentparams.fo,512*(bitmaplg*8-currentparams.bitindex),SEEK_CUR);
            }
        }
    }

  fclose(fi);
}

void readit(int f, void *buf, size_t len)
{
  ssize_t res;
  while (len > 0) {
    if ((res = read(f, buf, len)) <= 0)
      DEBUG(printf("Read failed: readit\n"));
    len -= res;
    buf += res;
  }
}


/*  */

int main(int argc, char **argv)
{
  int pr[2];
  int sk;
  int nbd;
  int blocksize = 1024;

  char chunk[CHUNK];
  struct nbd_request request;
  struct nbd_reply reply;

  u64 size;
  u64 from;
  u32 len;
  /*  */
  int file, oldfile = -1;
  u32 offset;
  unsigned char *ptr = NULL;

  if(argc<3){
    printf("Usage: %s nbdevice gzfile\n",argv[0]);
    exit(1);
  }

  /* memory for one decompressed block */
  all = malloc(1024*88064);

  if(argc == 3){
    int nb, fid;
    char buf[512];

    /* find an approximate size */
    for (nb = 0; ; nb++) {
      sprintf(buf, "%s%03d", argv[2], nb);
      if ((fid=open(buf, O_RDONLY)) == -1) {
        break;
      }
      close(fid);
    }
    if (nb == 0) {
      fprintf(stderr,"%s: unable open compressed file %s\n",argv[0], buf);
      exit(1);
    }
    size = (u64)88064*(u64)1024*nb;
  } else {
    exit(1);
  }

  if(socketpair(AF_UNIX, SOCK_STREAM, 0, pr)){
    fprintf(stderr,"%s: unable to create socketpair: %s\n",argv[0],strerror(errno));
    exit(1);
  }

  switch(fork()){
  case -1 :
    fprintf(stderr,"%s: unable to fork: %s\n",argv[0],strerror(errno));
    exit(1);
    break;

  case 0 : /* child */
    close(pr[0]);

    sk=pr[1];

    nbd=open(argv[1], O_RDWR);
    if(nbd<0){
      fprintf(stderr,"%s: unable to open %s: %s\n",argv[0],argv[1],strerror(errno));
      exit(1);
    }

    if (ioctl(nbd, NBD_SET_BLKSIZE, (unsigned long)blocksize) < 0) {
      fprintf(stderr, "NBD_SET_BLKSIZE failed\n");
      exit(1);
    }

    if ((ioctl(nbd, NBD_SET_SIZE_BLOCKS, (unsigned long)(size/blocksize))) < 0) {
      fprintf(stderr, "NBD_SET_SIZE_BLOKS failed\n");
      exit(1);
    }

    ioctl(nbd, NBD_CLEAR_SOCK);

    if(ioctl(nbd,NBD_SET_SOCK,sk)<0){
      fprintf(stderr,"%s: failed to set socket for %s: %s\n",argv[0],argv[1],strerror(errno));
      exit(1);
    }

    if(ioctl(nbd,NBD_DO_IT)<0){
      fprintf(stderr,"%s: block device %s terminated: %s\n",argv[0],argv[1],strerror(errno));
    }

    ioctl(nbd, NBD_CLEAR_QUE);
    ioctl(nbd, NBD_CLEAR_SOCK);

    exit(0);

    break;
  }

  /* only parent here, child always exits */

  close(pr[1]);
  sk=pr[0];

  reply.magic=htonl(NBD_REPLY_MAGIC);
  reply.error=htonl(0);

  BUFFER = malloc(24064);
  Bitmap = malloc(24064 - 2048);
  IN = malloc(INSIZE);

  sleep(1);

  while(1){

    if(read(sk,&request,sizeof(request))!=sizeof(request)){
      fprintf(stderr,"%s: incomplete request\n",argv[0]);
    }

    memcpy(reply.handle,request.handle,sizeof(reply.handle));

    len=ntohl(request.len);
    from=ntohll(request.from);

#ifdef TRACE
    fprintf(stderr,"%s: len=%d, from=%Ld\n",argv[0],len,from);
#endif

    if(request.magic!=htonl(NBD_REQUEST_MAGIC)){
      fprintf(stderr,"%s: bad magic\n",argv[0]);
      reply.error=htonl(EIO); /* is that the right way of doing things ? */
    }

    /* write resquest */
    if(ntohl(request.type) == 1){
      // fprintf(stderr,"%s: unsupported write request (len=%d)\n",argv[0], len);
      readit(sk, chunk, len);
      /* fake write */
      reply.error=htonl(0);
      len = 0;
      memcpy(chunk,&reply,sizeof(struct nbd_reply));
      if(write(sk,chunk,len+sizeof(struct nbd_reply))!=(len+sizeof(struct nbd_reply))){
        fprintf(stderr,"%s: write failed: %s\n",argv[0],strerror(errno));
      }
      continue;
    }

    /* disc request */
    if(ntohl(request.type) == 2){
      fprintf(stderr,"%s: unsupported disc request\n",argv[0]);
      reply.error=htonl(EROFS);
    }

    if(len+sizeof(struct nbd_reply)>CHUNK){
      fprintf(stderr,"%s: request too long (%d)\n",argv[0], len+sizeof(struct nbd_reply));
      //reply.error=htonl(EIO);
    }

    /* read request */
    if(reply.error==htonl(0)){
      int remain = len;
      int offset2 = 0;

      /* which chunk to open */
      file = from / (88064*1024);
      offset = from % (88064*1024);

      while (remain > 0) {
        u32 cpylen;

        if (oldfile != file) {
          decompress_file(argv[2], file, offset);
          oldfile = file;
        }

        ptr = &all[offset];

        if (offset + remain >= 88064*1024) {
          /* request on a block boundary */
          cpylen = (88064*1024)-offset;
          remain -= cpylen;
          file++;
          offset = 0;
        } else {
          /* request within a block */
          cpylen = remain;
          remain = 0;
        }

        /* copy the data */
        memcpy(chunk+sizeof(struct nbd_reply)+offset2, ptr, cpylen);
        offset2 += cpylen;
      }
    } else {
      len=0;
    }

    /* copy the reply header */
    memcpy(chunk,&reply,sizeof(struct nbd_reply));
    /* send data to kernel */
    if(write(sk,chunk,len+sizeof(struct nbd_reply))!=(len+sizeof(struct nbd_reply))){
      fprintf(stderr,"%s: write failed: %s\n",argv[0],strerror(errno));
    }
  }

  exit(0);
}

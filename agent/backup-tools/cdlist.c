/*
 *   cdlist - generates list of files for CD backups
 *
 *   Copyright (C) 2004 Julien BLACHE / Sirius Technologies <julien.blache@siriustech.org>
 *
 *   $Id$
 *
 *   This program is free software; you can redistribute it and/or modify
 *   it under the terms of the GNU General Public License as published by
 *   the Free Software Foundation; either version 2 of the License.
 *
 *   This program is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *   GNU General Public License for more details.
 *
 *   You should have received a copy of the GNU General Public License
 *   along with this program; if not, write to the Free Software
 *   Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA
 */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>

#include <errno.h>

#include <sys/types.h>
#include <sys/stat.h>
#include <dirent.h>

#include <glib.h>

/* A file node */
typedef struct
{
  char *name;
  unsigned long long size;
  int cd;
} filen;

/* A directory node */
typedef struct
{
  char *path;
  unsigned long long files_size;
  unsigned long long dirs_size;
  unsigned long long total_size;
  GSList *files;
  GSList *dirs;
} dirn;


dirn *
dirtree_build (char *path)
{
  filen *f;
  dirn *d, *sd;
  DIR *dir;
  struct dirent *dent;
  struct stat st;
  char *entpath;

  /* Open the directory, bail out on errors */
  dir = opendir(path);

  if (dir == NULL)
    {
      fprintf(stderr, "Error opening %s: %s\n", path, strerror(errno));
      return NULL;
    }

  /* Allocate a directory entry, bail out on errors */
  d = g_malloc(sizeof(dirn));

  if (d == NULL)
    {
      fprintf(stderr, "Couldn't allocate memory !\n");
      closedir(dir);
      return NULL;
    }

  /* Initialize the directory entry */
  d->path = path;
  d->files_size = 0;
  d->dirs_size = 0;
  d->total_size = 0;
  d->files = NULL;
  d->dirs = NULL;

  /* Now, populate the data structure, recursively */
  while ((dent = readdir(dir)) != NULL)
    {
      if ((strcmp(dent->d_name, ".") == 0) || (strcmp(dent->d_name, "..") == 0))
	  continue;

      entpath = g_strdup_printf("%s/%s", path, dent->d_name);

      if (lstat(entpath, &st) != 0)
	{
	  fprintf(stdout, "Couldn't stat %s: %s\n", entpath, strerror(errno));
	  continue;
	}

      if (S_ISREG(st.st_mode))
	{
	  f = g_malloc(sizeof(filen));

	  if (f == NULL)
	    {
	      fprintf(stderr, "Couldn't allocate memory !\n");
	      closedir(dir);
	      return NULL;
	    }

	  f->name = entpath;
	  f->size = st.st_size;
	  f->cd = 0;

	  d->files = g_slist_append(d->files, f);
	  d->files_size += f->size;
	}
      else if (S_ISDIR(st.st_mode))
	{
	  sd = dirtree_build(entpath);

	  if (sd == NULL)
	    {
	      closedir(dir);
	      return NULL;
	    }

	  d->dirs = g_slist_append(d->dirs, sd);
	  d->dirs_size += sd->total_size;
	}
      else
	{
	  fprintf(stdout, "Discarding %s: not a regular file or directory\n", entpath);
	}
    }

  d->total_size = d->files_size + d->dirs_size;

  closedir(dir);

  return d;
}


gint
dirs_comparefunc(gconstpointer a, gconstpointer b)
{
  dirn *da, *db;

  da = (dirn *) a;
  db = (dirn *) b;

  if (da->total_size > db->total_size)
    return -1;
  else if (da->total_size < db->total_size)
    return 1;
  else
    return 0;
}

gint
files_comparefunc(gconstpointer a, gconstpointer b)
{
  filen *fa, *fb;

  fa = (filen *) a;
  fb = (filen *) b;

  if (fa->size > fb->size)
    return -1;
  else if (fa->size < fb->size)
    return 1;
  else
    return 0;
}

void
dirtree_sort(gpointer data, gpointer unused)
{
  dirn *d;

  d = (dirn *) data;

  g_slist_foreach(d->dirs, dirtree_sort, NULL);

  d->dirs = g_slist_sort(d->dirs, dirs_comparefunc);
  d->files = g_slist_sort(d->files, files_comparefunc);
}


void
add_file(gpointer data, gpointer cd)
{
  filen *f;

  f = (filen *) data;

  f->cd = GPOINTER_TO_INT(cd);
}

void
add_dir(gpointer data, gpointer cd)
{
  dirn *d;

  d = (dirn *) data;

  g_slist_foreach(d->dirs, add_dir, GINT_TO_POINTER(cd));
  g_slist_foreach(d->files, add_file, GINT_TO_POINTER(cd));
}

void
add_cd(GSList **cds, unsigned long long mediasize)
{
  unsigned long long *sizep;

  sizep = (unsigned long long *) g_malloc(sizeof(unsigned long long));

  *sizep = mediasize;

  *cds = g_slist_append(*cds, sizep);
}

void
free_cd(gpointer data, gpointer unused)
{
  g_free(data);
}

#define LEFT(cd) g_slist_nth_data(*cds, (cd - 1))

int
distribute_files(GSList *files, int cd, GSList **cds, unsigned long long mediasize)
{
  int i, j;
  filen *f;
  unsigned long long *left;

  for (i = 0; i < g_slist_length(files); i++)
    {
      f = (filen *) g_slist_nth_data(files, i);

      for (j = (cd - 1); j < g_slist_length(*cds); j++)
	{
	  left = LEFT(j+1);

	  if (f->size < *left)
	    {
	      f->cd = j+1;
	      *left -= f->size;
	      break;
	    }
	}

      if (f->cd == 0)
	{
	  if (f->size < mediasize)
	    {
	      add_cd(cds, mediasize);
	      left = LEFT(j+1);
	      f->cd = j+1;
	      *left -= f->size;
	    }
	  else
	    {
	      fprintf(stdout, "Discarding %s: file too big for media !\n", f->name);
	      f->cd = -1;
	    }
	}
    }

  return (g_slist_length(*cds));
}

void
distribute_dirs(dirn *dt, unsigned long long mediasize, int cd, GSList **cds)
{
  unsigned long long *left;
  int i;

  left = LEFT(cd);

  if (dt->total_size < *left)
    {
      add_dir(dt, GINT_TO_POINTER(cd));
      *left -= dt->total_size;
    }
  else
    {
      if (dt->files_size < *left)
	{
	  g_slist_foreach(dt->files, add_file, GINT_TO_POINTER(cd));
	  *left -= dt->files_size;
	}
      else
	{
	  cd = distribute_files(dt->files, cd, cds, mediasize);
	}
      
      for (i = 0; i < g_slist_length(dt->dirs); i++)
	{
	  distribute_dirs(g_slist_nth_data(dt->dirs, i), mediasize, cd, cds);
	}
    }
}

int
dirtree_distribute(dirn *dt, unsigned long long mediasize)
{
  int i, ret;
  GSList *cds = NULL;

  add_cd(&cds, mediasize);
  
  distribute_dirs(dt, mediasize, 1, &cds);

  for (i = 0; i < g_slist_length(cds); i++)
    {
      fprintf(stdout, "Left on media #%d: %llu MB\n", (i+1),
	      *(unsigned long long *)(g_slist_nth_data(cds, i))/1024/1024);
    }

  ret = g_slist_length(cds);
  g_slist_foreach(cds, free_cd, NULL);
  g_slist_free(cds);

  return ret;
}

#undef LEFT


void
print_file(gpointer data, gpointer unused)
{
  filen *f;

  f = (filen *) data;

  fprintf(stdout, "%-15llu %s\n", f->size, f->name);
}

void
dirtree_print(gpointer data, gpointer unused)
{
  dirn *d;

  d = (dirn *) data;

  fprintf(stdout, "%-15llu %s\n", d->total_size, d->path);

  g_slist_foreach(d->files, print_file, NULL);
  g_slist_foreach(d->dirs, dirtree_print, NULL);
}


void
close_files(gpointer data, gpointer unused)
{
  FILE *fp;

  fp = (FILE *) data;

  fclose(fp);
}

void
print_file_to_files(gpointer data, gpointer list)
{
  filen *f;
  GSList **flist;
  FILE *fp;
  char *file;

  f = (filen *) data;

  flist = (GSList **) list;

  fp = (FILE *) g_slist_nth_data(*flist, f->cd);
  
  if (fp == NULL)
    {
      file = g_strdup_printf("%s/list%d",
			     (char *) g_slist_nth_data(*flist, 0),
			     f->cd);

      fp = fopen(file, "w");

      if (fp == NULL)
	{
	  fprintf(stderr, "Couldn't open %s: %s\n", file, strerror(errno));
	  g_free(file);
	  return;
	}

      g_free(file);

      *flist = g_slist_append(*flist, fp);
    }

  fprintf(fp, "%-15llu %s\n", f->size, f->name);
}

void
print_dir_to_files(gpointer data, gpointer list)
{
  dirn *d;

  d = (dirn *) data;

  g_slist_foreach(d->files, print_file_to_files, list);
  g_slist_foreach(d->dirs, print_dir_to_files, list);
}

void
dirtree_print_to_files(dirn *dirtree, const char *path)
{
  GSList *flist = NULL;
  char *p;

  flist = g_slist_append(flist, g_strdup(path));

  print_dir_to_files(dirtree, &flist);

  p = (char *) g_slist_nth_data(flist, 0);
  flist = g_slist_remove(flist, p);
  g_free(p);
  g_slist_foreach(flist, close_files, NULL);
  g_slist_free(flist);
}


void
file_free(gpointer data, gpointer unused)
{
  filen *f;

  f = (filen *) data;

  g_free(f->name);
  g_free(f);
}

void
dirtree_free(gpointer data, gpointer unused)
{
  dirn *d;

  d = (dirn *) data;

  g_slist_foreach(d->dirs, dirtree_free, NULL);
  g_slist_free(d->dirs);

  g_slist_foreach(d->files, file_free, NULL);
  g_slist_free(d->files);

  g_free(d->path);
  g_free(d);
}


int
main (int argc, const char **argv)
{
  dirn *dirtree;
  unsigned long long mediasize;
  int medianum;
  char *end;

  if (argc != 4)
    {
      fprintf(stderr, "Trop ou trop peu d'arguments :\n");
      fprintf(stderr, "Usage: cdlist cible destination taille_du_media\n");
      fprintf(stderr, "Avec taille_du_media en Mo\n");
      return 1;
    }

  mediasize = strtoll(argv[3], &end, 0);

  if ((*end != '\0') || (end == argv[3]))
    {
      fprintf(stderr, "Taille du media invalide !\n");
      return 2;
    }

  dirtree = dirtree_build(g_strdup(argv[1]));

  if (dirtree == NULL)
    exit(123);

  dirtree_sort(dirtree, NULL);

  medianum = dirtree_distribute(dirtree, (mediasize * 1024 * 1024));

  fprintf(stdout, "Distributed files on %d media\n", medianum);

  /* dirtree_print(dirtree, NULL); */

  dirtree_print_to_files(dirtree, argv[2]);

  dirtree_free(dirtree, NULL);

  fprintf(stdout, "%d\n", medianum);

  return 0;
}

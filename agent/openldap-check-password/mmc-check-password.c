/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2009 Mandriva, http://www.mandriva.com
 *
 * $Id$
 *
 * This file is part of Mandriva Management Console (MMC).
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC.  If not, see <http://www.gnu.org/licenses/>.
 */


/**
 * mmc-check-password.c: OpenLDAP password checker module
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <portable.h>
#include <slap.h>
#include <fcntl.h>
#include <unistd.h>
#include <syslog.h>

#ifndef CONFIG_FILE
#define CONFIG_FILE "/etc/openldap/mmc-check-password.conf"
#endif

int check_password (char *pPasswd, char **ppErrStr, Entry *pEntry);
typedef int (*validator) (char*);
static int read_config_file (char *);
static validator valid_word (char *);
static int set_debug (char *);
static int set_password_helper_path (char *value);
int debug = 0;
char *passwordHelperPath = "/usr/bin/mmc-password-helper";

static int set_password_helper_path (char *value) {
    passwordHelperPath = strdup(value);
    return 0;
}

static int set_debug (char *value) {
    if (!isdigit(*value) || atoi(value) == 0)
        return -1;
    if(atoi(value) == 1) {
        debug = 1;
        syslog(LOG_NOTICE, "mmc-check-password: enableDebug = %s", value);
        return 0;
    }
    return 1;
}

static validator valid_word (char *word) {
    struct {
        char * parameter;
        validator dealer;
    } list[] = {{"enableDebug", set_debug},
        {"passwordHelperPath", set_password_helper_path},
        {NULL, NULL} };
    int index = 0;

    if(debug)
        syslog(LOG_NOTICE, "mmc-check-password: Validating parameter [%s]", word);

    while (list[index].parameter != NULL) {
        if (strlen(word) == strlen(list[index].parameter) &&
                strcmp(list[index].parameter, word) == 0) {
            if(debug)
                syslog(LOG_NOTICE, "mmc-check-password: Parameter accepted.");
            return list[index].dealer;
        }
        index++;
    }

    if(debug)
        syslog(LOG_NOTICE, "mmc-check-password: Parameter rejected.");

    return NULL;
}

/**
 * Read the mmc-check-password.conf configuration file
 */
static int read_config_file (char *keyWord) {
    FILE * config;
    char * line;
    int returnValue = -1;

    if ((line = ber_memcalloc(260, sizeof(char))) == NULL) {
        return returnValue;
    }

    if ( (config = fopen(CONFIG_FILE, "r")) == NULL) {
        if(debug)
            syslog(LOG_ERR, "mmc-check-password: Opening file %s failed", CONFIG_FILE);

        ber_memfree(line);
        return returnValue;
    }

    while (fgets(line, 256, config) != NULL) {
        char *start = line;
        char *word, *value;
        validator dealer;

        if(debug)
            syslog(LOG_NOTICE, "mmc-check-password: Got line |%s|", line);
        if(line[0] == '#')
            continue;

        while (isspace(*start) && isascii(*start)) start++;

        if (! isascii(*start))
            continue;

        if ((word = strtok(start, " \t")) && (dealer = valid_word(word)) && (strcmp(keyWord,word)==0)) {
            if ((value = strtok(NULL, " \t")) == NULL)
                continue;
        if(value[strlen(value)-1] == '\n')
            value[strlen(value)-1] = '\0';

            if(debug)
                syslog(LOG_NOTICE, "mmc-check-password: Word = %s, value = %s", word, value);
            returnValue = (*dealer)(value);
        }
    }

    fclose(config);
    ber_memfree(line);
    return returnValue;
}

/**
 * Called by OpenLDAP to check a new password
 */
int check_password (char *pPasswd, char **ppErrStr, Entry *pEntry) {
    char *pwdMinLength=NULL;
    char final_commandline[256]={0};
    char *dn = strdup(pEntry->e_name.bv_val);

    Attribute *attr = NULL;
    for (attr = pEntry->e_attrs; attr; attr = attr->a_next) {
        if (!strcmp(attr->a_desc->ad_cname.bv_val, "pwdMinLength")) {
            pwdMinLength=strdup(attr->a_vals->bv_val);
        }
    }

    read_config_file("enableDebug");
    read_config_file("passwordHelperPath");

    int fd = open(passwordHelperPath, O_RDONLY);
    if(fd == -1) {
        close(fd);
        if(debug)
            syslog(LOG_ERR, "mmc-check-password: invalid password helper path: %s", passwordHelperPath);
        goto error;
    }

    strcat(final_commandline, passwordHelperPath);
    strcat(final_commandline, " -c");
    /* add the user DN */
    strcat(final_commandline, " -u ");
    strcat(final_commandline, dn);

    if (pwdMinLength)
        sprintf(final_commandline, "%s -u %s -l %s -c", passwordHelperPath, dn, pwdMinLength);
    else
        sprintf(final_commandline, "%s -u %s -c", passwordHelperPath, dn);

    if (debug) {
        syslog(LOG_NOTICE, "mmc-check-password: Command line: |%s|",
               final_commandline);
    }

    FILE * file = popen(final_commandline, "w");
    fwrite(pPasswd, strlen(pPasswd), 1, file);
    int ret = pclose(file);

    if (ret)
        goto error;

    *ppErrStr = strdup ("OK");
    return (LDAP_SUCCESS);

error:
    *ppErrStr = strdup ("Unsafe Password");
    return (EXIT_FAILURE);
}


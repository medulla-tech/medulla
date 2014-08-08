#!/bin/bash  
#
# (c) 2014 Mandriva, http://www.mandriva.com/
#
# This file is part of Pulse 2
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

# This script generates metadata for debian and rpm based repositories.
# Includes also a GPG signing.

# ---------------------- GPG KEY GENERATE ----------------------------

BASE_DIR="/var/lib/pulse2/clients"
NAME="Mandriva Support" 
EMAIL="sales@mandriva.com"
GPG_KEY_CONF=$HOME/gpg-key-conf
GPG_KEY_FILE="pulse2-agents.gpg.key"
MACROS=$HOME/.rpmmacros
ID="$NAME <$EMAIL>"
RPM_REPO_NAME="pulse2-agents"
RPM_REPO_FILE="${RPM_REPO_NAME}.repo"
MY_URL=$(hostname -I | cut -d' ' -f1) 

# ---------- Overwrite .rpmmacros file -----------------
echo "%_gpg_name	$ID" > $MACROS
echo "%_signature    gpg" >> $MACROS
echo "%_gpg_path     /root/.gnupg" >> $MACROS
echo "%_topdir             $BASE_DIR" >> $MACROS



if [ ! -f $GPG_KEY_CONF ]; then
    # --------------------- passphrase generate --------------------------
    PASSPHRASE=$(date +%s | sha256sum | base64 | head -c 16)

    echo "%echo Generating a GPG key" > $GPG_KEY_CONF
    echo "Key-Type: DSA" >> $GPG_KEY_CONF
    echo "Key-Length: 1024" >> $GPG_KEY_CONF
    echo "Subkey-Type: ELG-E" >> $GPG_KEY_CONF
    echo "Subkey-Length: 2048" >> $GPG_KEY_CONF
    echo "Name-Real: $NAME" >> $GPG_KEY_CONF
    echo "Name-Email: $EMAIL" >> $GPG_KEY_CONF
    echo "Expire-Date: 0" >> $GPG_KEY_CONF
    echo "Passphrase: $PASSPHRASE" >> $GPG_KEY_CONF
    echo "%commit" >> $GPG_KEY_CONF
    echo "%echo Done" >> $GPG_KEY_CONF
else
    match=$(grep "Passphrase: " $GPG_KEY_CONF)	
    PASSPHRASE=${match#"Passphrase: "}
    echo $PASSPHRASE

fi    

# ------------------------- GPG Key conf -----------------------------

if gpg --list-keys | grep -q "$ID" ; then
    echo "INFO: GPG UID already exists, creation skipped"
else
    echo "INFO: GPG generation started !"

    rngd -r /dev/urandom
    gpg --batch --gen-key /root/gpg-key-conf
	
    echo "INFO: GPG generation done"
    gpg -v --export --armour $ID > $GPG_KEY_FILE
       	
fi	

GPG_KEY_ID=$(gpg --list-keys --with-colons $EMAIL | awk -F: '/^pub:/ { print $5 }')

# -------------------- DEBIAN REPOSITORY --------------------------------

if [ -d deb ]; then
    DIST="common"
    REPO_SUBDIR="debian"

    echo "INFO: Creating DEB repository"

    if [ ! -d $REPO_SUBDIR ]; then
        mkdir $REPO_SUBDIR
    fi  
    if [ ! -d $REPO_SUBDIR/$DIST ]; then
        mkdir $REPO_SUBDIR/$DIST
    fi	   
    if [ ! -d $REPO_SUBDIR/conf ]; then
        mkdir $REPO_SUBDIR/conf
    fi 
    distributions=$REPO_SUBDIR/conf/distributions    
    options=$REPO_SUBDIR/conf/options    


    echo "Origin: Pulse2 Agents" > $distributions 
    echo "Label: Pulse2 Agents - Common Debian Repository" >> $distributions
    echo "Codename: $DIST" >> $distributions
    echo "Architectures: i386 amd64" >> $distributions
    echo "Components: main" >> $distributions
    echo "Description: This repository contains custom Debian packages" >> $distributions
    echo "SignWith: $GPG_KEY_ID" >> $distributions

    echo "verbose" > $options
    echo "basedir $BASE_DIR/$REPO_SUBDIR" >> $options
    echo "ask-passphrase" >> $options

    echo "INFO: Signing the packages:"

    cd $BASE_DIR/$REPO_SUBDIR

    for DEBFILE in `ls ../deb/*.deb`; do
        echo "INFO: ... package $DEBFILE"

        expect -c " 
	        set timeout 1 
                spawn reprepro includedeb ${DIST} ../deb/${DEBFILE}
                expect -exact \"Enter passphrase: \" 		
                send -- \"${PASSPHRASE}\r\"
                expect -exact \"Enter passphrase: \" 		
                send -- \"${PASSPHRASE}\r\"
                expect eof
                "
	    
        if [ $? -ne 0 ]; then
                echo "ERROR: Signing process of package '$DEBFILE' failed."
                echo "ERROR: Exiting."
                exit 1;		
        fi		    
    done

    cd $BASE_DIR
fi

if [ ! -f /usr/bin/createrepo ]; then
    echo "WARNING: Package 'createrepo' missing."
    echo "WARNING: To install, type 'apt-get install createrepo'."
    exit 1;
fi	


# ------------------------ RPM REPOSITORY ------------------------------
if [ -d rpm ]; then
    echo "INFO: Creating RPM repository"

    echo "INFO: Signing the packages:"

    for RPMFILE in `ls rpm/*.rpm`; do
        echo "INFO: ... package $RPMFILE"

        expect -c " 
	        set timeout 2
	        spawn rpmsign --resign ${RPMFILE} 
                expect -exact \"Enter pass phrase: \" 		
                send -- \"${PASSPHRASE}\r\"
                expect eof
                "
	    
        if [ $? -ne 0 ]; then
                echo "ERROR: Signing process of package '$RPMFILE' failed."
                echo "ERROR: Exiting."
                exit 1;		
        fi		    
    done

    /usr/bin/createrepo -d -v rpm
    if [ $? -eq 0 ]; then

    echo "INFO: RPM repository successfully created"	   
 
        if [ -f rpm/repodata/repomd.xml.asc ]; then
	    rm -f rpm/repodata/repomd.xml.asc	
	fi	
	gpg --detach-sign --passphrase $PASSPHRASE --armor rpm/repodata/repomd.xml

        if [ $? -eq 0 ]; then
            echo "INFO: RPM repository successfully signed"
        else	    
            echo "WARNING: Signing of RPM repository failed"
	    exit 1;
        fi    

	echo "INFO: Creating .repo file"
	echo "[$RPM_REPO_NAME]" > rpm/$RPM_REPO_FILE
	echo "name = Pulse2 Agents" >> rpm/$RPM_REPO_FILE
	echo "baseurl = http://$MY_URL/downloads/rpm" >> rpm/$RPM_REPO_FILE
	echo "gpgkey = http://$MY_URL/downloads/$GPG_KEY_FILE" >> rpm/$RPM_REPO_FILE
	echo "enabled=1" >> rpm/$RPM_REPO_FILE
	echo "gpgcheck=1" >> rpm/$RPM_REPO_FILE
		
    else   

        echo "WARNING: RPM repository wasn't created !"	   
        exit 1;	
    fi

else
    echo "WARNING: RPM folder doesn't exists !"	
fi	

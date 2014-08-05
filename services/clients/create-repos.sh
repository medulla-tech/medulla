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

NAME="Mandriva Support" 
EMAIL="sales@mandriva.com"
GPG_KEY_CONF=$HOME/gpg-key-conf
MACROS=$HOME/.rpmmacros
ID="$NAME <$EMAIL>"

# ---------- Overwrite .rpmmacros file -----------------
echo "%_gpg_name=$ID" > $MACROS

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
       	
fi	

# --------------------- END OF GPG SECTION ----------------------------

# -------------------- DEBIAN REPOSITORY --------------------------------
if [ -d deb ]; then
    echo "INFO: Creating debian repository"
    /usr/bin/dpkg-scanpackages deb | gzip -9c > deb/Packages.gz
    if [ $? -eq 0 ]; then
        echo "INFO: Debian repository successfully created"	   
    else   	
        echo "WARNING: Debian repository wasn't created !"	    
    fi	    
else
    echo "WARNING: Debian folder doesn't exists !"	
fi


if [ ! -f /usr/bin/createrepo ]; then
    echo "WARNING: Package 'createrepo' missing."
    echo "WARNING: To install, type 'apt-get install createrepo'."
    exit 1;
fi	


# ------------------------ RPM REPOSITORY ------------------------------
if [ -d rpm ]; then
    echo "INFO: Creating RPM repository"
    /usr/bin/createrepo rpm
    if [ $? -eq 0 ]; then
        echo "INFO: RPM repository successfully created"	   
	echo "INFO: Signing the packages:"
        for RPMFILE in `ls rpm/*.rpm`; do
	    echo "INFO: ... package $RPMFILE"	
            expect -c " 
	        set timeout 2
	        spawn rpmsign --addsign ${RPMFILE} 
                expect -exact \"Enter pass phrase: \" 		
                send -- \"${PASSPHRASE}\r\"
                expect exp_continue
                "
	    
	    if [ $? -ne 0 ]; then
                echo "ERROR: Signing process of package '$RPMFILE' failed."
                echo "ERROR: Exiting."
                exit 1;		
            fi		    
	done	
	gpg --detach-sign --passphrase $PASSPHRASE --armor rpm/repodata/repomd.xml 
        if [ $? -eq 0 ]; then
            echo "INFO: RPM repository successfully signed"
            gpg --export --armour $ID > RPM-GPG-KEY-pulse2	    
	    	
	fi	
    else   	
        echo "WARNING: RPM repository wasn't created !"	    
    fi

else
    echo "WARNING: RPM folder doesn't exists !"	
fi	

#!/bin/bash
#
# (c) 2008-2009 Mandriva, http://www.mandriva.com
#
# $Id$
#
# This file is part of Pulse 2, http://pulse2.mandriva.org
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

PKI_PATH=PULSE2
PKI_KEYS_PATH=$PKI_PATH/private
PKI_CERTS_PATH=$PKI_PATH/newcerts
PKI_REQS_PATH=$PKI_PATH/req
PASSPHRASE=pulse2
PULSE2_SERVICES="mmc_agent launcher_01 scheduler_01 inventory_server package_server"

export PASSPHRASE

# build tree
rm -fr $PKI_PATH
mkdir $PKI_PATH
echo 00 > $PKI_PATH/serial
touch $PKI_PATH/index.txt
mkdir $PKI_KEYS_PATH
mkdir $PKI_CERTS_PATH
mkdir $PKI_REQS_PATH

# initialise PKI
openssl req -passout env:PASSPHRASE -batch -extensions v3_ca -new -keyout $PKI_KEYS_PATH/pulse2-key.pem -out $PKI_REQS_PATH/pulse2-req.pem
# self-sign
openssl ca -passin env:PASSPHRASE -batch -extensions v3_ca -selfsign -keyfile $PKI_KEYS_PATH/pulse2-key.pem -out $PKI_PATH/pulse2.pem -infiles $PKI_REQS_PATH/pulse2-req.pem
# remove sign request
rm $PKI_REQS_PATH/pulse2-req.pem

for service in $PULSE2_SERVICES; do
        # generate key and sign request
        openssl req -passout env:PASSPHRASE -batch -extensions v3_ca -new -keyout $PKI_KEYS_PATH/$service-key.pem -out $PKI_REQS_PATH/$service-req.pem
        # sign cert with PKI
        openssl ca -passin env:PASSPHRASE -batch -extensions v3_ca -policy policy_anything -keyfile $PKI_KEYS_PATH/pulse2-key.pem -out $PKI_CERTS_PATH/$service-cert.pem -infiles $PKI_REQS_PATH/$service-req.pem
        # convert it in the good format
        openssl rsa -passin env:PASSPHRASE -in $PKI_KEYS_PATH/$service-key.pem -out $PKI_KEYS_PATH/$service-key.rsa
        # generate final cert
        cat $PKI_KEYS_PATH/$service-key.rsa $PKI_CERTS_PATH/$service-cert.pem > $PKI_PATH/$service.pem
        echo "in $PKI_PATH, for $service: cacert is pulse2.pem, localcert is $service.pem"
done


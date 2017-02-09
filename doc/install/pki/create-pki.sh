#!/bin/bash
#
# (c) 2017 Siveo, http://www.siveo.net
# (c) 2008-2009 Mandriva, http://www.mandriva.com
#
# $Id$
#
# This file is part of Pulse 2, http://www.siveo.net
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

set -e

PKI_PATH=/var/lib/pulse2/pki
PKI_CNF=$PKI_PATH/conf/pulse.cnf
PKI_KEYS_PATH=$PKI_PATH/private
PKI_CERTS_PATH=$PKI_PATH/newcerts
PKI_REQS_PATH=$PKI_PATH/req
PKI_CRLS_PATH=$PKI_PATH/crl
PASSPHRASE=
PKI_CN_CA_ROOT="PulseRootCA"
PKI_CN_CA_INTERMEDIATE="PulseIntermediateCA"
PKI_COUNTRY=FR
PKI_ORGANIZATION=SIVEO
PKI_SUBJ=/countryName=$PKI_COUNTRY/organizationName=$PKI_ORGANIZATION
CRL_SERVER_ADDRESS=

PULSE_SERVICES="mmc_agent scheduler launcher inventory_server package_server apache"

export PASSPHRASE

# build tree
rm -fr $PKI_PATH
mkdir $PKI_PATH
echo 00 > $PKI_PATH/serial
echo 00 > $PKI_PATH/crlnumber
touch $PKI_PATH/index.txt
mkdir $PKI_PATH/conf
mkdir $PKI_KEYS_PATH
mkdir $PKI_CERTS_PATH
mkdir $PKI_REQS_PATH
mkdir $PKI_CRLS_PATH
chmod 700 $PKI_KEYS_PATH
chmod 700 $PKI_PATH/conf

# Prepare configuration file
cd "`dirname $0`"
sed "s/@@CRL_SERVER_ADDRESS@@/$CRL_SERVER_ADDRESS/" pulse.cnf.in > $PKI_CNF
chmod 400 $PKI_CNF

# initialise PKI

# create root ca
echo "### Creating root CA ###"
openssl req -config $PKI_CNF -subj "$PKI_SUBJ/commonName=$PKI_CN_CA_ROOT" -passout env:PASSPHRASE -batch -extensions v3_ca -new -keyout $PKI_KEYS_PATH/rootca.key.pem -out $PKI_REQS_PATH/careq.pem
echo "### $PKI_KEYS_PATH/rootca.key.pem generated"
chmod 400 $PKI_KEYS_PATH/rootca.key.pem
# self-sign
openssl ca -config $PKI_CNF -name CA_Root -passin env:PASSPHRASE -batch -extensions v3_ca -selfsign -keyfile $PKI_KEYS_PATH/rootca.key.pem -out $PKI_PATH/rootca.cert.pem -infiles $PKI_REQS_PATH/careq.pem
echo "### $PKI_PATH/rootca.cert.pem generated"
chmod 444 $PKI_PATH/rootca.cert.pem
# remove sign request
rm $PKI_REQS_PATH/careq.pem


# create intermediate ca
echo "### Creating intermediate CA ###"
openssl req -config $PKI_CNF -subj "$PKI_SUBJ/commonName=$PKI_CN_CA_INTERMEDIATE" -passout env:PASSPHRASE -batch -extensions v3_ca -new -keyout $PKI_KEYS_PATH/cakey.pem -out $PKI_REQS_PATH/careq.pem
echo "### $PKI_KEYS_PATH/cakey.pem generated"
chmod 400 $PKI_KEYS_PATH/cakey.pem
# sign the req using the rootca key
openssl ca -config $PKI_CNF -name CA_Root -passin env:PASSPHRASE -batch -extensions v3_intermediate_ca -keyfile $PKI_KEYS_PATH/rootca.key.pem -out $PKI_PATH/cacert.pem -infiles $PKI_REQS_PATH/careq.pem
echo "### $PKI_PATH/cacert.pem generated"
chmod 444 $PKI_PATH/cacert.pem
# remove sign request
rm $PKI_REQS_PATH/careq.pem

# create the certificate chain
echo "### Creating the certificate chain ###"
cat $PKI_PATH/cacert.pem $PKI_PATH/rootca.cert.pem > $PKI_PATH/ca-chain.cert.pem
echo "### $PKI_PATH/ca-chain.cert.pem generated"
chmod 444 $PKI_PATH/ca-chain.cert.pem

# create the revocation list
echo "### Creating the revocation list ###"
openssl ca -config $PKI_CNF -name CA_Intermediate -passin env:PASSPHRASE -gencrl -out $PKI_PATH/crl.pem
echo "### $PKI_PATH/crl.pem generated"


# generate the certificates for Pulse services
echo "### Creating the services certificates ###"
for service in $PULSE_SERVICES; do
        # generate key and sign request
        openssl req -config $PKI_CNF -subj "$PKI_SUBJ/commonName=$service" -passout env:PASSPHRASE -batch -extensions server_cert -new -keyout $PKI_KEYS_PATH/$service-key.pem -out $PKI_REQS_PATH/$service-req.pem
        chmod 400 $PKI_KEYS_PATH/$service-key.pem
        # sign cert with PKI
        openssl ca -config $PKI_CNF -name CA_Intermediate -passin env:PASSPHRASE -batch -extensions server_cert -keyfile $PKI_KEYS_PATH/cakey.pem -out $PKI_CERTS_PATH/$service-cert.pem -infiles $PKI_REQS_PATH/$service-req.pem
        chmod 444 $PKI_CERTS_PATH/$service-cert.pem
        # remove sign request
        rm $PKI_REQS_PATH/$service-req.pem
        # convert it in the good format
        openssl rsa -passin env:PASSPHRASE -in $PKI_KEYS_PATH/$service-key.pem -out $PKI_PATH/$service.pem
        # generate final cert
        cat $PKI_CERTS_PATH/$service-cert.pem >> $PKI_PATH/$service.pem
        chmod 444 $PKI_PATH/$service.pem
        echo "### In $PKI_PATH, for $service: cacert is ca-chain.cert.pem, localcert is $service.pem"
done

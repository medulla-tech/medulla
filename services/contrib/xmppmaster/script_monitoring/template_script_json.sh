#!/bin/bash

# script bash

# dans cet exemple la variable event est remplacer par la chaine json
s='@@@@@event@@@@@'
echo "affiche json information"
echo $s | jq '.mon_machine_hostname'

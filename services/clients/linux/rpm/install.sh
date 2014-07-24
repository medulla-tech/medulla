#!/bin/sh
workdir=/tmp/pulse_agents_$(date +%N)/
mkdir -p $workdir
cd $workdir
wget http://tyrion/downloads/linux/deb/deb_agent.tar.gz
tar zxf deb_agent.tar.gz
sh install.sh

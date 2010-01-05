#!/bin/sh
cd /root/python
sh ./init.sh

echo "`date` - Starting Python Pulse2 tests."
echo ""
echo ""
python Pserver.py
python PserverEmpty.py
python Launcher.py
python Scheduler.py
echo ""
echo "Statistics of unittest's Pulse2"
echo ""
echo ""
echo "Statistics of package-server unittest" 
cat /usr/lib/python2.4/site-packages/pulse2/package_server/mirror/__init__.py /usr/lib/python2.4/site-packages/pulse2/package_server/mirror_api/__init__.py /usr/lib/python2.4/site-packages/pulse2/package_server/package_api_put/__init__.py /usr/lib/python2.4/site-packages/pulse2/package_server/package_api_get/__init__.py /usr/lib/python2.4/site-packages/pulse2/package_server/scheduler_api/__init__.py /usr/lib/python2.4/site-packages/pulse2/package_server/user_package_api/__init__.py > /usr/sbin/pserver
echo ""
echo ""
python Statistics.py pserver Pserver.py 
echo ""
echo ""
echo "Statistics of launcher unittest" 
echo ""
echo ""
python Statistics.py pulse2-launcher Launcher.py
echo ""
echo ""
echo "Statistics of scheduler unittest" 
echo ""
echo ""
python Statistics.py pulse2-scheduler Scheduler.py
echo""
echo "" 
echo "`date` - Ending Python Pulse2 tests." 

rm  -f /usr/sbin/pserver

exit 0

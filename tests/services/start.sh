#!/bin/bash -e

RPCPSERVER=`mktemp`
cat /usr/lib/python2.*/site-packages/pulse2/package_server/mirror/__init__.py /usr/lib/python2.*/site-packages/pulse2/package_server/mirror_api/__init__.py /usr/lib/python2.*/site-packages/pulse2/package_server/package_api_put/__init__.py /usr/lib/python2.*/site-packages/pulse2/package_server/package_api_get/__init__.py /usr/lib/python2.*/site-packages/pulse2/package_server/scheduler_api/__init__.py /usr/lib/python2.*/site-packages/pulse2/package_server/user_package_api/__init__.py > $RPCPSERVER

echo ""
echo "Statistics of Pulse 2 unittest"
echo ""
echo ""
echo "Statistics of package-server unittest pserverempty.py"
echo ""
echo ""
python statistics.py $RPCPSERVER pserverempty.py 

echo ""
echo ""
echo "Statistics of package-server unittest pserver.py"
echo ""
echo ""
python statistics.py $RPCPSERVER pserver.py
rm -f $RPCPSERVER

echo ""
echo ""
echo "Statistics of launcher unittest" 
echo ""
echo ""
python statistics.py /usr/sbin/pulse2-launcher launcher.py

echo ""
echo ""
echo "Statistics of scheduler unittest" 
echo ""
echo ""
python statistics.py /usr/sbin/pulse2-scheduler scheduler.py

echo "`date` - Starting Python Pulse 2 tests."
echo ""
echo ""

echo "Testing Package Server with no package (pserverempty.py)"
python pserverempty.py
echo "Testing Package Server with one package (pserver.py)"
python pserver.py
echo "Testing Launcher"
python launcher.py
echo "Testing Scheduler"
python scheduler.py

echo ""
echo "" 
echo "`date` - Ending Python Pulse2 tests." 

exit 0

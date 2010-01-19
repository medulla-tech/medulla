#!/bin/sh

echo "`date` - Starting Python Pulse2 tests."
echo ""
echo ""
python pserverempty.py
python pserver.py
python launcher.py
python scheduler.py

RPCPSERVER=`mktemp`
cat /usr/lib/python2.*/site-packages/pulse2/package_server/mirror/__init__.py /usr/lib/python2.*/site-packages/pulse2/package_server/mirror_api/__init__.py /usr/lib/python2.*/site-packages/pulse2/package_server/package_api_put/__init__.py /usr/lib/python2.*/site-packages/pulse2/package_server/package_api_get/__init__.py /usr/lib/python2.*/site-packages/pulse2/package_server/scheduler_api/__init__.py /usr/lib/python2.*/site-packages/pulse2/package_server/user_package_api/__init__.py > $RPCPSERVER

echo ""
echo "Statistics of unittest's Pulse2"
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

echo""
echo "" 
echo "`date` - Ending Python Pulse2 tests." 

exit 0

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

echo ""
echo ""
echo "Statistics of inventory unittest mmcagent-inventory-empty.py"
echo ""
echo ""
python statistics.py /usr/lib/python2.*/site-packages/mmc/plugins/inventory/__init__.py mmcagent-inventory-empty.py

echo ""
echo ""
echo "Statistics of dyngroup unittest mmcagent-dyngroup-empty.py"
echo ""
echo ""
python statistics.py /usr/lib/python2.*/site-packages/mmc/plugins/dyngroup/__init__.py mmcagent-dyngroup-empty.py

echo ""
echo ""
echo "Statistics of package unittest mmcagent-pkgs-empty.py"
echo ""
echo ""
python statistics.py /usr/lib/python2.*/site-packages/mmc/plugins/pkgs/__init__.py mmcagent-pkgs-empty.py

echo ""
echo ""
echo "`date` - Starting Python Pulse 2 tests."
echo ""
echo ""

echo ""
echo ""
echo "Testing MMC agent plugins on a clean Pulse 2 setup"
echo ""
echo ""
echo "Inventory plugin"
python mmcagent-inventory-empty.py
echo "Dyngroup plugin"
python mmcagent-dyngroup-empty.py
echo "Dyngroup Pkgs"
python mmcagent-pkgs-empty.py

echo "Testing Package Server with no package (pserverempty.py)"
python pserverempty.py
echo "Testing Package Server with one package (pserver.py)"
python pserver.py
echo "Testing Launcher"
python launcher.py
echo "Testing Scheduler"
python scheduler.py
echo "Testing Package Server imaging API"
python pserver-imaging.py

echo ""
echo ""
echo "Testing inventory injection"
echo ""
echo ""
python mmcagent-inventory-inject.py


echo ""
echo ""
echo "`date` - Ending Python Pulse2 tests."

exit 0

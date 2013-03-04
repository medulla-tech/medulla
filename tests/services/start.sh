#!/bin/bash

ERROR=0
ERRORLOG=""

RPCPSERVER=`mktemp`
cat /usr/lib/python2.*/dist-packages/pulse2/package_server/mirror/__init__.py /usr/lib/python2.*/dist-packages/pulse2/package_server/mirror_api/__init__.py /usr/lib/python2.*/dist-packages/pulse2/package_server/package_api_put/__init__.py /usr/lib/python2.*/dist-packages/pulse2/package_server/package_api_get/__init__.py /usr/lib/python2.*/dist-packages/pulse2/package_server/scheduler_api/__init__.py /usr/lib/python2.*/dist-packages/pulse2/package_server/user_package_api/__init__.py > $RPCPSERVER

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
python statistics.py /usr/lib/python2.*/dist-packages/mmc/plugins/inventory/__init__.py mmcagent-inventory-empty.py

echo ""
echo ""
echo "Statistics of dyngroup unittest mmcagent-dyngroup-empty.py"
echo ""
echo ""
python statistics.py /usr/lib/python2.*/dist-packages/mmc/plugins/dyngroup/__init__.py mmcagent-dyngroup-empty.py

echo ""
echo ""
echo "Statistics of package unittest mmcagent-pkgs-empty.py"
echo ""
echo ""
python statistics.py /usr/lib/python2.*/dist-packages/mmc/plugins/pkgs/__init__.py mmcagent-pkgs-empty.py

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
if [ ! $? -eq 0 ]; then
  ERROR=`expr ${ERROR} + 1`;
  ERRORLOG="${ERRORLOG}\nFAILURE: Clean: mmcagent-inventory-empty.py"
fi 
echo "Dyngroup plugin"
python mmcagent-dyngroup-empty.py
if [ ! $? -eq 0 ]; then
  ERROR=`expr ${ERROR} + 1`;
  ERRORLOG="${ERRORLOG}\nFAILURE: Clean: mmcagent-dyngroup-empty.py"
fi 
echo "Dyngroup Pkgs"
python mmcagent-pkgs-empty.py
if [ ! $? -eq 0 ]; then
  ERROR=`expr ${ERROR} + 1`;
  ERRORLOG="${ERRORLOG}\nFAILURE: Clean: mmcagent-pkgs-empty.py"
fi 

echo "Testing Package Server with no package (pserverempty.py)"
python pserverempty.py
if [ ! $? -eq 0 ]; then
  ERROR=`expr ${ERROR} + 1`;
  ERRORLOG="${ERRORLOG}\nFAILURE: Package Server: pserverempty.py"
fi 
echo "Testing Package Server with one package (pserver.py)"
python pserver.py
if [ ! $? -eq 0 ]; then
  ERROR=`expr ${ERROR} + 1`;
  ERRORLOG="${ERRORLOG}\nFAILURE: Package Server: pserver.py"
fi 
echo "Testing Launcher"
python launcher.py
if [ ! $? -eq 0 ]; then
  ERROR=`expr ${ERROR} + 1`;
  ERRORLOG="${ERRORLOG}\nFAILURE: Launcher: launcher.py"
fi 
echo "Testing Scheduler"
python scheduler.py
if [ ! $? -eq 0 ]; then
  ERROR=`expr ${ERROR} + 1`;
  ERRORLOG="${ERRORLOG}\nFAILURE: Scheduler: scheduler.py"
fi 
echo "Testing Package Server imaging API"
python pserver-imaging.py
if [ ! $? -eq 0 ]; then
  ERROR=`expr ${ERROR} + 1`;
  ERRORLOG="${ERRORLOG}\nFAILURE: Package Server / Imaging: pserver-imaging.py"
fi 
echo "Testing Scheduler Balance module"
python balance.py
if [ ! $? -eq 0 ]; then
  ERROR=`expr ${ERROR} + 1`;
  ERRORLOG="${ERRORLOG}\nFAILURE: Scheduler Balance Module: balance.py"
fi 

echo ""
echo ""
echo "Testing inventory injection"
echo ""
echo ""
python mmcagent-inventory-inject.py
if [ ! $? -eq 0 ]; then
  ERROR=`expr ${ERROR} + 1`;
  ERRORLOG="${ERRORLOG}\nFAILURE: Inventory Injection: mmcagent-inventory-inject.py"
fi 

echo "Testing networking utils"
python network.py
if [ ! $? -eq 0 ]; then
  ERROR=`expr ${ERROR} + 1`;
  ERRORLOG="${ERRORLOG}\nFAILURE: networking utils: network.py"
fi 

echo ""
echo ""
echo "`date` - Ending Python Pulse2 tests."

echo
echo
echo
echo
echo
echo "#################################################################"
echo "##################### UNIT TESTS - SUMMARY  #####################"
echo "#################################################################"
echo
echo "Number of failed test: ${ERROR}"
echo -e ${ERRORLOG}
echo
echo

exit ${ERROR}

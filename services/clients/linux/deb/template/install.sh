#!/bin/sh -e

./ssh.sh
./fusion_inventory.sh
vnc/vnc.sh
./shorewall.sh
./update_manager.sh
echo ""
echo "Mandriva Pulse agents installed successfully"

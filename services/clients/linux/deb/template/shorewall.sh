#!/bin/sh

DRAKX=/etc/shorewall/rules.drakx
RULES=/etc/shorewall/rules

if dpkg -l|grep shorewall > /dev/null; then
    echo 'Adding shorewall exceptions'

    if [ -f $DRAKX ];then
        if grep -q -e 22 $DRAKX;then 
            sed  -i '/22/c\ACCEPT  net     fw      tcp    22       -' $DRAKX
        else 
            echo 'ACCEPT  net     fw      tcp    22       -' >> $DRAKX
        fi
        if grep -q -e 8 $DRAKX;then 
            sed  -i '/8/c\ACCEPT  net     fw      icmp    8       -' $DRAKX
        else 
            echo 'ACCEPT  net     fw      icmp    8' >> $DRAKX
        fi
    else
        touch $RULES
        if grep -q -e 22 $RULES;then 
            sed  -i '/22/c\ACCEPT  net     fw      tcp    22       -' $RULES
        else
            echo 'ACCEPT  net     fw      tcp    22       -' >> $RULES
        fi
        if grep -q -e 8 $RULES;then
            sed  -i '/8/c\ACCEPT  net     fw      icmp    8       -' $RULES
        else
            echo 'ACCEPT  net     fw      icmp    8' >> $RULES
        fi
    fi
    service shorewall restart
fi

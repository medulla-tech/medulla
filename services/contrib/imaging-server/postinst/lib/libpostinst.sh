# Global variables which can be intersting in the postinst scripts
#
# Linbox Rescue Server                                                          
# Copyright (C) 2005-2007 Ludovic Drolez, Linbox FAS 
#

. /etc/netinfo.sh
MAC=`cat /etc/shortmac`
HOSTNAME=`cat /revoinfo/$MAC/hostname|tr : /`
HOSTNAME=`basename $HOSTNAME`
IPSERVER=$Next_server

#
export PATH=$PATH:/opt/bin
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/lib

CHNTPWBIN=/opt/bin/chntpw

REGNUM=0

#
# Strip the 2 leading directories of a Win/DOS path
#
Strip2 ()
{
    echo $1 | cut -f 3- -d \\
}


#
# Find the Windows config directory
# return it in the CONFIGDIR variable
#
GetWinConfigDir ()
{    
    # XP paths
    for i in /mnt/[wW][iI][nN]*/[Ss][Yy][Ss][Tt][Ee][Mm]32/[Cc][Oo][Nn][Ff][Ii][Gg]/[Ss][Oo][Ff][Tt][Ww][Aa][Rr][Ee]
    do	
	if [ -d ${i%/*} -a -f $i ] ;then
	    CONFIGDIR=${i%/*}
	    SOFTWAREDIR=$i
	    return 0
	fi
    done
    CONFIGDIR=
    SOFTWAREDIR=
    echo "Could not find the registry..."
    return 1
}

#
# Add a key in the win registry
#
RegistryAddString () 
{
    KEY=$1
    NAM=$2
    VAL=$3
    
    Strip2 $KEY
    KEY2=`Strip2 $KEY`
    
    GetWinConfigDir
    
    # build the script that will be sent to chntpw    
    SCRIPT="cd $KEY2
nv 1 $NAM
ed $NAM
$VAL
ls
q
y
"
    
    case $KEY in
    HKEY_LOCAL_MACHINE\\Software\\*)
	echo "*** modifying $KEY in $SOFTWAREDIR ***"
	echo "$SCRIPT" | $CHNTPWBIN -e $SOFTWAREDIR
	;;
    *)	
	echo "*** modifying $KEY not yet supported ***"
	;;
    esac
}

#
# Add a key(s) in the win registry
#
RegistryAddKey () 
{
    KEY=$1
    shift
    SCRIPT=""
    
    Strip2 $KEY
    KEY2=`Strip2 $KEY`
    
    GetWinConfigDir
    
    # build the script that will be sent to chntpw    
    SCRIPT="cd $KEY2"
    for D in $@
    do
	if [ -z $D ]; then
	    break
	fi
	SCRIPT="$SCRIPT
nk $D
cd $D"
    done
    SCRIPT="$SCRIPT
ls
q
y
"    
    case $KEY in
    HKEY_LOCAL_MACHINE\\Software\\*)
	echo "*** modifying $KEY in $SOFTWAREDIR ***"
	echo "$SCRIPT" | $CHNTPWBIN -e $SOFTWAREDIR
	;;
    *)	
	echo "*** modifying $KEY not yet supported ***"
	;;
    esac
    
}

#
# Modify the registry to run a program once after login (run as superuser)
# Example: RegistryAddRunOnce myprog.exe
#
RegistryAddRunOnce ()
{
    REGNUM=$(($REGNUM+1))
    RegistryAddString "HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\RunOnce" LRS$REGNUM $1
}

RegistryAddRun ()
{
    REGNUM=$(($REGNUM+1))
    RegistryAddString "HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\Run" LRS$REGNUM $1
}

RegistryAddRunServicesOnce ()
{
    # Win 2000. Not for XP.
    REGNUM=$(($REGNUM+1))
    RegistryAddString "HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\RunServicesOnce" LRS$REGNUM $1
}

#
# Copy a sysprep.inf to file and substitute the hostname 
# Example: CopySysprepInf /revoinfo/$MAC/mysysprep.inf
#
CopySysprepInf ()
{
    # Warning ! There's a ^M after $HOSTNAME for DOS compatibility
    SYSPREP=sysprep
    [ -d /mnt/Sysprep ] && SYSPREP=Sysprep
    
    rm -f /mnt/$SYSPREP/[Ss]ysprep.inf    
    sed -e "s/^[ 	]*[Cc]omputer[Nn]ame[^\n\r]*/ComputerName=$HOSTNAME"`echo -e "\015"`"/" <$1 >/mnt/$SYSPREP/Sysprep.inf
}

#
# Return the name of the Nth partition
#
GetNPart ()
{
    I=1
    C4=""
    # read /proc/partitions and find the Nth entry
    while [ $I -le $1 ] ;do
	read C1 C2 C3 C4 C5 || break	    
	if echo "$C4"|grep -q "^[a-z]*[0-9]$"; then
	    I=$(($I+1))
	fi
    done < /proc/partitions
    [ "$C4" ] && echo /dev/$C4
}

#
# Get the start sector for partition NUM on disk DISK
#
GetPartStart ()
{
    DISK=$1
    NUM=$2
    
    L=`parted -s $DISK unit s print|grep ^$NUM|sed 's/  */,/g'|cut -f 2 -d ,`
    echo $L
    
}

#
# Return "yes" if the partition is bootable
#
IsPartBootable ()
{
    DISK=$1
    NUM=$2
    
    parted -s $DISK print|grep ^$NUM|grep -q boot && echo "yes"
}

#
# Set the boot partition flag
#
SetPartBootable ()
{
    DISK=$1
    NUM=$2
    
    parted -s $DISK set $NUM boot on    
}

#
# Resize the Nth partition of the 1st disk (not ntfs compatible) 
#
Resize ()
{
    NUM=$1
    SZ=$2
    
    P=`GetNPart $NUM`
    D=`PartToDisk $P`
    S=`GetPartStart $D $NUM`
    parted -s $D resize $NUM $S $SZ
}

#
# Maximize the Nth partition of the 1st disk (not ntfs compatible) 
#
ResizeMax ()
{
    Resize $1 100%
}

#
# Resize the Nth primary partition of the 1st disk (ntfs only) 
# Should be the last one
#
NtfsResize ()
{
    NUM=$1
    SZ=$2
    
    P=`GetNPart $NUM`
    D=`PartToDisk $P`
    S=`GetPartStart $D $NUM`
    BOOT=`IsPartBootable $D $NUM`
    #
    parted -s $D rm $NUM mkpart primary ntfs $S $SZ
    [ "$BOOT" = "yes" ] && SetPartBootable $D $NUM
    yes|ntfsresize -f $P
    ntfsresize --info --force $P
}

#
# Maximize the Nth primary partition of the 1st disk (ntfs only) 
# Should be the last one
#
NtfsResizeMax ()
{
    NtfsResize $1 100%
}

#
# return the disk device related to the part device
# /dev/hda1 -> /dev/hda 
#
PartToDisk ()
{
    echo $1|
    sed 's/[0-9]*$//'
}

#
# Mount the target device as /mnt
#
Mount ()
{
    if echo "$1" | grep -q "^[0-9]" ;then
	# mount the Nth partition	
	I=1
	# read /proc/partitions and find the Nth entry
	while [ $I -le $1 ] ;do
	    read C1 C2 C3 C4 C5 || break	    
	    if echo "$C4"|grep -q "^[a-z]*[0-9]$"; then
		I=$(($I+1))
	    fi
	done < /proc/partitions
	if [ "$C4" = "" ]; then
	    echo "*** ERROR: partition $1 not found"
	    exit 1
	fi
	mountwin /dev/$C4
    else
	# windows ntfs/fat mount
	mountwin $1
    fi
}

#
# newsid.exe based commands
#
ChangeSID ()
{
    mkdir /mnt/tmp
    unix2dos <<EOF >/mnt/tmp/newsid.bat
\\tmp\\newsid.exe /a
EOF
    chmod 755 /mnt/tmp/newsid.bat
    cp -f /opt/winutils/newsid.exe /mnt/tmp/
    RegistryAddRunOnce '\tmp\newsid.bat'
}

ChangeSIDAndName ()
{
    mkdir /mnt/tmp
    unix2dos <<EOF >/mnt/tmp/newsid.bat
\\tmp\\newsid.exe /a /d 30 $HOSTNAME
EOF
    chmod 755 /mnt/tmp/newsid.bat
    cp -f /opt/winutils/newsid.exe /mnt/tmp/
    RegistryAddRunOnce '\tmp\newsid.bat'
}

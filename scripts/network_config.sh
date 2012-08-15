#!/bin/sh

if [ $# -eq 0 ]; then
echo "usage: sudo $0 dhcp"
echo "usage: sudo $0 static ip-addr netmask broadcast"
exit
fi


lanName="$(ifconfig | awk "/^eth/ {print \$1}")"
wlanName="$(ifconfig | awk "/^wlan/ {print \$1}")"

echo "*********"
echo "Lan:" $lanName "\nWlan:"$wlanName
echo "\n*********"


###/sbin/ifconfig $wlanName down


if [ "$1" = "dhcp" ]; then
echo "Setting the lan with dhcp"
/sbin/dhclient
else
echo "Setting the lan with static add"
/sbin/ifconfig $lanName $2  netmask $3 broadcast $4
fi




#!/bin/sh



lanName="$(ifconfig | awk "/^eth/ {print \$1}")"
hostIpAddr="$(/sbin/ifconfig $lanName | grep "inet addr" | awk -F: '{print $2}' | awk '{print $1}')"

IP1=$(echo $hostIpAddr | awk -F. '{print $1}')
IP2=$(echo $hostIpAddr | awk -F. '{print $2}')
IP3=$(echo $hostIpAddr | awk -F. '{print $3}')
routerIpAddr=$IP1.$IP2.$IP3.1

if [ $# -eq 0 ]; then
ip=$routerIpAddr
else
ip=$1
fi
if eval "/bin/ping -c1 $ip"
then 
	exit 0
fi
exit 1

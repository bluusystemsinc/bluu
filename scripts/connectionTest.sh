#!/bin/sh

if eval "/bin/ping -c1 $1"
then 
	exit 1
fi
exit 0

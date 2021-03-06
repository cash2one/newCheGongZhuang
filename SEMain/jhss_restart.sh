#!/bin/bash

if [ -f ~/.bash_profile ];
then
	. ~/.bash_profile
fi

echo "stopping jhssd"
jhss_pid=$(netstat -anop | grep "0.0.0.0:9999" | awk '{print $7}' | awk -F '/' '{print $1}')
echo $jhss_pid

if [ -n "$jhss_pid" ]; 
then
{
	kill -9 $jhss_pid
}
fi

echo "starting jhssd"
dt=`date +%Y-%m-%d`
nohup python /root/SEWeb/webserver/SEMain/app.py >> /root/SEWeb/webserver/SEMain/logs/log.$dt 2>&1 &


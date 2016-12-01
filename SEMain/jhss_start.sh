#!/bin/bash

if [ -f ~/.bash_profile ];
then
    . ~/.bash_profile
fi
dt=`date +%Y-%m-%d`
echo "starting jhssd"
nohup python /root/SEWeb/webserver/SEMain/SEMain/app.py >> /root/SEWeb/webserver/SEMain/logs/log.$dt 2>&1 &

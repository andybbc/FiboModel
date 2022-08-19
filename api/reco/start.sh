#!/bin/bash

NGINX=/usr/local/openresty/nginx/sbin/nginx

PREFIX=`pwd`

case ${1} in
    start)
        $NGINX -p $PREFIX -c conf/nginx.conf
        ;;
    stop)
        $NGINX -p $PREFIX -s stop
        ;;
    reload)
        $NGINX -p $PREFIX -s reload
        ;;
    *)
        echo ${1}
        echo "`basename ${0}`:useage: [start] | [stop] | [reload]"
        ;;
esac

#!/bin/bash

function log () {
    local DATE=`date "+%Y-%m-%d %H:%M:%S"` ####显示打印日志的时间
    echo "[${DATE}] $*" | tee -a ${LOG_FILE}  # 在控制台显示并且输出到文件,追加的方式
}

# check_is_ok $? $0 $FUNCNAME  $message
function check_is_ok(){
    local state=$1
    local shell_name=$2
    local fun_name=$3
    local error_message=$4

    if [ $state -ne "0" ];then
        log "*************脚本执行失败*************\n
          脚本:${shell_name}\n
          函数:${fun_name}
          error_message:${error_message}
        "
        send_email $error_message
        exit 1
    else
        log "=============脚本${shell_name} , ${fun_name} 执行成功============="
    fi
}

function send_email(){
    local error_message=$1
    cat ${LOG_FILE} | mail -s "${error_message} [${TODAY} ${HOUR}]" malichun@advlion.com
    cat ${LOG_FILE} | mail -s "${error_message} [${TODAY} ${HOUR}]" yongyue@vlion.cn
}



export -f log
export -f check_is_ok
export -f send_email
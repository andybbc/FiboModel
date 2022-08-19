#!/bin/bash
set -e
if [ ! -n "$WORK_DIR" ]||[ ! -n "$TODAY_HOUR" ]; then
   log "请从run开始执行,没有初始化变量,当前路径未知,程序退出!!!"
   exit 1
fi


cd ${PYTHON_APP_PATH}

log "开始导入到redis"
$PYTHON3 save2redis.py \
   --range_file=${COMBINER_TOP_DIR}/out_final.txt \
   --log_path ${log_file}

check_is_ok $? $0 $FUNCNAME
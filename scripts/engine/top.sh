#!/bin/bash

if [ ! -n "$WORK_DIR" ]||[ ! -n "$TODAY_HOUR" ]; then
    log "请从run开始执行,没有初始化变量,当前路径未知,程序退出!!!"
    exit 1
fi


##########
HDFS_INPUT_BASE_DIR="/data/hippo/storm_clk"

##########

log "执行spark程序开始"
HDFS_INPUT_FILE_PATHS=`hdfs dfs -ls ${HDFS_INPUT_BASE_DIR}/*/*  | sed 1d | tail -${INPUT_HOUR_FILE_NUMS} |awk '{print $NF}' | xargs echo | sed 's/ /,/g'`
log "hdfs输入路径:"${HDFS_INPUT_FILE_PATHS}


mkdir -p ${ALGORITHS_TOP_DIR}/top_channel
mkdir -p ${ALGORITHS_TOP_DIR}/top_media


 # 计算,生成top文件
$SPARK_SUBMIT \
    --class com.advlion.www.collaborative.HippoTopJob \
    --master yarn \
    --driver-memory 3g \
    --executor-memory 3g \
    --executor-cores 4 \
    --verbose \
    ${JAR_PATH}/hippo.jar \
    --input_file ${HDFS_INPUT_FILE_PATHS} \
    --local_all_top ${ALGORITHS_TOP_DIR}/top_all.txt \
    --local_channel_top ${ALGORITHS_TOP_DIR}/top_channel \
    --local_media_top ${ALGORITHS_TOP_DIR}/top_media

check_is_ok $? $0 $FUNCNAME
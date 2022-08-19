#!/bin/bash
set -x

if [ ! -n "$WORK_DIR" ]||[ ! -n "$TODAY_HOUR" ]; then
    log "请从run开始执行,没有初始化变量,当前路径未知,程序退出!!!"
    exit 1
fi
####################################################################################################

# 原始点击日志HDFS输入目录
HDFS_INPUT_BASE_DIR="/data/hippo/storm_clk"

HDFS_ALL_OUT_DIR="/home/test/cookie_file"
HDFS_MEDIA_OUT_DIR="/home/test/media_file"
HDFS_CHANNEL_OUT_DIR="/home/test/channel_file"



####################################################################################################


function clean_data(){
    log "开始清除数据...."
    local date_num=`ls ${WORK_DIR}/data | grep 2020 | wc -l`
    local need_del_count=$(( $date_num - $OLD_FILE_RETAIN_DAYS ))
    if [ $need_del_count -gt 0 ];then
        for file in `ls ${WORK_DIR}/data | grep 2020 | head -$need_del_count`;
        do
          rm -rf ${WORK_DIR}/data/$file
        done
    fi

    $HDFS dfs -rm -r -f ${HDFS_ALL_OUT_DIR}
    $HDFS dfs -rm -r -f ${HDFS_MEDIA_OUT_DIR}
    $HDFS dfs -rm -r -f ${HDFS_CHANNEL_OUT_DIR}

    rm -rf $DATA_DIR  # 删除当前目录

    mkdir -p $RAW_DIR
    mkdir -p ${RAW_BEHAVIOR_DIR}
    mkdir -p ${RAW_TEXT_DIR}

    mkdir -p ${ALGORITHS_DIR}
    mkdir -p ${ALGORITHS_TOP_DIR}
    mkdir -p ${ALGORITHS_COLLABORATIVE_DIR}
    mkdir -p ${ALGORITHS_ARTICLE_SIMILARY_DIR}

    mkdir -p ${COMBINE_DIR}
    mkdir -p ${COMBINER_TOP_DIR}
}


function generate_behavior_raw_file(){
    log "执行spark程序开始"
    HDFS_INPUT_FILE_PATHS=`$HDFS dfs -ls ${HDFS_INPUT_BASE_DIR}/*/*  | sed 1d | tail -${INPUT_HOUR_FILE_NUMS} |awk '{print $NF}' | xargs echo | sed 's/ /,/g'`
    log "HDFS输入路径:"${HDFS_INPUT_FILE_PATHS}


    # 计算,生成top文件和初始明细文件
    $SPARK_SUBMIT \
        --class com.advlion.www.collaborative.HippoRawJob \
        --master yarn \
        --driver-memory 3g \
        --executor-memory 3g \
        --executor-cores 4 \
        --verbose \
        ${JAR_PATH}/hippo.jar \
        --input_file ${HDFS_INPUT_FILE_PATHS} \
        --hdfs_detail ${HDFS_ALL_OUT_DIR} \
        --hdfs_media_detail ${HDFS_MEDIA_OUT_DIR} \
        --hdfs_channel_detail ${HDFS_CHANNEL_OUT_DIR}

    check_is_ok $? $0 $FUNCNAME

    # 将HDFS的明细文件拉到本地,并改名
    $HDFS dfs -get ${HDFS_ALL_OUT_DIR}/part* ${RAW_BEHAVIOR_DIR}
    check_is_ok $? $0 $FUNCNAME
    mv ${RAW_BEHAVIOR_DIR}/`ls ${RAW_BEHAVIOR_DIR}/ | grep part` ${RAW_BEHAVIOR_DIR}/all_detail.txt
    mkdir -p ${RAW_BEHAVIOR_DIR}/media
    $HDFS dfs -get ${HDFS_MEDIA_OUT_DIR}/* ${RAW_BEHAVIOR_DIR}/media
    check_is_ok $? $0 $FUNCNAME
    mkdir -p ${RAW_BEHAVIOR_DIR}/channel
    $HDFS dfs -get ${HDFS_CHANNEL_OUT_DIR}/* ${RAW_BEHAVIOR_DIR}/channel
    check_is_ok $? $0 $FUNCNAME
}


function generate_text_raw_file(){
    log "生成文章相似度的输入文件开始:"
    cd ${PYTHON_APP_PATH}

    $PYTHON3 get_news.py \
        --delta_hour $OLD_NEWS_SIMILARITY_DELTA \
        --out_file ${RAW_TEXT_DIR}/old_news_list.json \
        --log_path ${log_file}
    check_is_ok $? $0 $FUNCNAME
}

# 根据频道分类
function generate_text_raw_file_group(){
    local process_type=$1

    mkdir -p ${RAW_TEXT_DIR}/${process_type}

    cd ${PYTHON_APP_PATH}

    for file in `ls ${RAW_BEHAVIOR_DIR}/${process_type}`
    do
        log "开始${file} similarity算法计算文章相似度"
        $PYTHON3 get_news.py \
        --delta_hour $OLD_NEWS_SIMILARITY_DELTA \
        --news_category ${RAW_BEHAVIOR_DIR}/${process_type}/$file \
        --news_file ${RAW_TEXT_DIR}/${process_type}/${file}_old_news_list.json
        check_is_ok $? $0 $FUNCNAME
    done
}


clean_data

generate_behavior_raw_file

generate_text_raw_file
# generate_text_raw_file_group # 根据频道分组

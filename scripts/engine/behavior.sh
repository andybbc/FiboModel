#!/bin/bash

set -x
set -e

if [ ! -n "$WORK_DIR" ]||[ ! -n "$TODAY_HOUR" ]; then
   log "请从run开始执行,没有初始化变量,当前路径未知,程序退出!!!"
   exit 1
fi



function apriori_run(){
    log "开始执行apriori算法"
    # 到Python的目录
    cd ${PYTHON_APP_PATH}

    echo "开始生成推荐数据:"
    # 生成推荐数据
    $PYTHON3 apriori.py \
        --data_path ${RAW_BEHAVIOR_DIR}/all_detail.txt \
        --out_path ${ALGORITHS_COLLABORATIVE_DIR}/out_origin.txt \
        --log_path ${log_file}

    check_is_ok $? $0 $FUNCNAME
}

####下面根据  频道/媒体 分组,输入参数 channel / media
function apriori_run_group(){
    local process_type=$1
    log "开始计算apriori算法,根据${process_type}分组..."

    mkdir -p ${ALGORITHS_COLLABORATIVE_DIR}/${process_type}

    cd ${PYTHON_APP_PATH}
    for file in `ls ${RAW_BEHAVIOR_DIR}/${process_type}`
    do
        log "==${process_type}分组apriori算法:$file"

        $PYTHON3 apriori.py \
            --data_path ${RAW_BEHAVIOR_DIR}/${process_type}/$file \
            --out_path ${ALGORITHS_COLLABORATIVE_DIR}/${process_type}/${file}_out_origin.txt \
            --log_path ${log_file}

        check_is_ok $? $0 $FUNCNAME
  done
}




apriori_run

#apriori_run_group channel



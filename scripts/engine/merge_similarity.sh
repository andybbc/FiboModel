#!/bin/bash
set -e
if [ ! -n "$WORK_DIR" ]||[ ! -n "$TODAY_HOUR" ]; then
    log "请从run开始执行,没有初始化变量,当前路径未知,程序退出!!!"
    exit 1
fi


# TODO 合并两个推荐文件
function merge_similarity_file(){
    log "开始两个推荐系统合并"
    cd ${PYTHON_APP_PATH}

    $PYTHON3 merge_similarity.py \
        --input_path1  ${ALGORITHS_COLLABORATIVE_DIR}/out_origin.txt \
        --input_path2  ${ALGORITHS_ARTICLE_SIMILARY_DIR}/news_similarity_range.txt \
        --out_path  ${COMBINE_DIR}/out_merge.txt \
        --rate1  $APRIORI_MERGE_RATE \
        --rate2  $SIMIARYTIY_MERGE_RATE
    check_is_ok $? $0 $FUNCNAME
}

function merge_top(){
    log "开始合并数据"
    cd ${PYTHON_APP_PATH}
    # 合并推荐数据和top数据
    $PYTHON3 merge_top.py \
        --input_path ${COMBINE_DIR}/out_merge.txt \
        --ref_path ${ALGORITHS_TOP_DIR}/top_all.txt \
        --out_path ${COMBINER_TOP_DIR}/out_final.txt

    check_is_ok $? $0 $FUNCNAME
}


# 合并推荐文件,分组
function merge_similarity_group(){
    local process_type=$1

    mkdir -p ${COMBINE_DIR}/${process_type}

    cd ${PYTHON_APP_PATH}

    for file in `ls ${RAW_BEHAVIOR_DIR}/${process_type}`
    do
      log "开始${file} 合并"
      $PYTHON3 merge_similarity.py \
          --input_path1  ${ALGORITHS_COLLABORATIVE_DIR}/${process_type}/${file}_out_origin.txt \
          --input_path2  ${ALGORITHS_ARTICLE_SIMILARY_DIR}/${process_type}/${file}_news_similarity_range.txt \
          --out_path  ${COMBINE_DIR}/${process_type}/${file}_out_merge.txt \
          --rate1  $APRIORI_MERGE_RATE \
          --rate2  $SIMIARYTIY_MERGE_RATE
      check_is_ok $? $0 $FUNCNAME
    done
}


function merge_top_group(){
    local process_type=$1
    mkdir -p ${COMBINER_TOP_DIR}/${process_type}

    cd ${PYTHON_APP_PATH}

    for file in `ls ${RAW_BEHAVIOR_DIR}/${process_type}`
    do
      log top合并${file}
      $PYTHON3 merge_top.py \
          --input_path ${COMBINE_DIR}/${process_type}/${file}_out_merge.txt \
          --ref_path ${ALGORITHS_TOP_DIR}/top_${process_type}/${file} \
          --out_path ${COMBINER_TOP_DIR}/${process_type}/${file}.txt

      check_is_ok $? $0 $FUNCNAME
    done
}

# 全局合并
merge_similarity_file
merge_top

# 频道合并
#merge_similarity_group channel
#merge_top_group channel



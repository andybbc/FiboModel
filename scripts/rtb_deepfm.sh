#!/bin/bash
set -x
set -e
#######################################################
# 输入的时间全部不带-, 如 20210202
#######################################################
WORK_DIR=$(
    cd $(dirname $0)
    cd ..
    pwd
) # ma路径

source ${WORK_DIR}/scripts/utils/env.sh
source ${WORK_DIR}/scripts/utils/tool.sh

export PYTHON3=/apps/python/python3/bin/python3

if [ $# == 2 ]; then
    ETL_DATE=$1
    ETL_HOUR=$2
else
    ETL_DATE=${LAST_DATE}
    ETL_HOUR=${LAST_HOUR}
fi

ETL_DATE=20210413
ETL_HOUR=12


function init() {

    ###使用的训练模型
    use_model_type="deepfm"                             # deepfm / xgboost /xgboost_lr / xdeepfm
    if_predict=true   # 是否要预估,跑批的时候不用 true / false

    DEL_DATE=$(date -d "${ETL_DATE} -1 days" "+%Y%m%d") # 删除过期数据的时间

    # 2个server服务
    SERVER_HOST=("vlionserver-ctr173" "vlionserver-ctr27")

    # 相关文件名称
    PROJECT_NAME='rtb' # 如果有多个,这边需要切换(android,ios)

    # 目录相关 ################################
    DATA_DIR=/data/algorithm/data2/${PROJECT_NAME}/${use_model_type}

    ETL_DIR=${DATA_DIR}/etl/${ETL_DATE}/${ETL_HOUR}               # 上游输入目录
    PREPROCESS_DIR=${DATA_DIR}/preprocess/${ETL_DATE}/${ETL_HOUR} # 拆分列
    FEATURE_DIR=${DATA_DIR}/feature/${ETL_DATE}/${ETL_HOUR}       # label_encode
    TRAIN_DIR=${DATA_DIR}/train/${ETL_DATE}/${ETL_HOUR}           # 训练
    PREDICT_DIR=${DATA_DIR}/predict/${ETL_DATE}/${ETL_HOUR}       # 预测的结果

    mkdir -p "${ETL_DIR}"         # 上游输入目录
    mkdir -p "${PREPROCESS_DIR}"  # 拆分列
    mkdir -p "${FEATURE_DIR}"     # label_encode
    mkdir -p "${TRAIN_DIR}"       # 训练
    mkdir -p "${PREDICT_DIR}"     # 预测的结果

    APPS_DIR=${WORK_DIR}/src/apps # 脚本路径

    mkdir -p ${WORK_DIR}/logs/rtb/${ETL_DATE}/
    LOG_file=${WORK_DIR}/logs/rtb/${ETL_DATE}/xgb_lr.log.${ETL_HOUR}
    touch ${LOG_file}

    REMOTE_HTTP_SERVER_DATA_DIR=/home/apps/rtb_dsp_79_20210131 # # 远程接口服务器的数据路径
    #######################################################

    echo "工作目录:${WORK_DIR}"
    echo "数据目录:"${DATA_DIR}
    echo "业务处理时间:${ETL_DATE}  ${ETL_HOUR}"
}

# 根据指定的特征列生成训练文件
function _preprocess_split_train() {
    cd ${APPS_DIR}
    ${PYTHON3} ${APPS_DIR}/rtb/preprocess/split_train.py \
        --log_path ${LOG_file} \
        --in_file ${ETL_DIR}/train.txt \
        --out_file ${PREPROCESS_DIR}/train.txt

    check_is_ok $? $0 $FUNCNAME "预处理训练文件报错"
}

# 训练文件预处理,生成label_encode的映射文件,转换原始文件,生成拆分文件
function _feature_train() {
    cd ${APPS_DIR}
    ${PYTHON3} ${APPS_DIR}/rtb/feature/train_.py \
        --log_path ${LOG_file} \
        --in_file ${PREPROCESS_DIR}/train.txt \
        --out_encode_file ${FEATURE_DIR}/train_encode.txt \
        --out_label_path ${FEATURE_DIR}/label.out \
        --out_label_detail_path ${FEATURE_DIR}/label_detail.json \
        --out_train_file "${FEATURE_DIR}/train.txt" \
        --out_vali_file "${FEATURE_DIR}/vali.txt" \
        --out_test_file "${FEATURE_DIR}/test.txt" \
        --out_mms_save_file "${FEATURE_DIR}/mms.save"

    check_is_ok $? $0 $FUNCNAME "预处理训练文件报错"
}

##########################################
# 训练模型
function _xgboost_train() {
    cd ${APPS_DIR}
    ${PYTHON3} ${APPS_DIR}/rtb/train/xgboost_train.py \
        --log_path ${LOG_file} \
        --in_encode_file ${FEATURE_DIR}/train_encode.txt \
        --out_train_file "${FEATURE_DIR}/train.txt" \
        --out_vali_file "${FEATURE_DIR}/vali.txt" \
        --out_test_file "${FEATURE_DIR}/test.txt" \
        --out_xgb_model_path "${TRAIN_DIR}/xgb_model.pkl"

    check_is_ok $? $0 $FUNCNAME "训练文件报错"
}

function _xgboost_lr_train() {
    cd ${APPS_DIR}

    ${PYTHON3} ${APPS_DIR}/rtb/train/xgboost_lr_train_.py \
        --log_path ${LOG_file} \
        --in_encode_file ${FEATURE_DIR}/train_encode.txt \
        --in_train_file "${FEATURE_DIR}/train.txt" \
        --in_vali_file "${FEATURE_DIR}/vali.txt" \
        --in_test_file "${FEATURE_DIR}/test.txt" \
        --out_one_hot_encoder_path ${TRAIN_DIR}/one_hot.out \
        --out_xgb_model_path "${TRAIN_DIR}/xgb_model.pkl" \
        --out_lr_model_path "${TRAIN_DIR}/lr_model.pkl"

    check_is_ok $? $0 $FUNCNAME "训练文件报错"
}

function _deepfm_train() {
    cd ${APPS_DIR}

    ${PYTHON3} ${APPS_DIR}/rtb/train/deepfm_train.py \
        --log_path ${LOG_file} \
        --in_encode_file ${FEATURE_DIR}/train_encode.txt \
        --out_model_path "${TRAIN_DIR}/deepfm_model.h5"

    check_is_ok $? $0 $FUNCNAME "训练文件报错"
}

function _xdeepfm_train(){
     cd ${APPS_DIR}

    ${PYTHON3} ${APPS_DIR}/rtb/train/xdeepfm_train.py \
        --log_path ${LOG_file} \
        --in_encode_file ${FEATURE_DIR}/train_encode.txt \
        --out_model_path "${TRAIN_DIR}/xdeepfm_model.h5"

    check_is_ok $? $0 $FUNCNAME "训练文件报错"
}

################################
# 根据原始文件生成需要训练的特征的预测文件(第一列比训练文件少了lable字段)
function _preprocess_split_predict() {
    cd ${APPS_DIR}

    ${PYTHON3} ${APPS_DIR}/rtb/preprocess/split_predict.py \
        --log_path ${LOG_file} \
        --in_file ${ETL_DIR}/test.txt \
        --out_file ${PREPROCESS_DIR}/test.txt

    check_is_ok $? $0 $FUNCNAME "拆分预测文件报错"

}

###########################################################
# label_encode预测文件,通过训练生成的label.out转换
function _feature_predict() {
    cd ${APPS_DIR}

    ${PYTHON3} ${APPS_DIR}/rtb/feature/predict_.py \
        --log_path ${LOG_file} \
        --in_split_cols_file ${PREPROCESS_DIR}/test.txt \
        --in_label_path ${FEATURE_DIR}/label.out \
        --in_mms_save_file "${FEATURE_DIR}/mms.save" \
        --out_encode_file ${FEATURE_DIR}/test_encode.txt

    check_is_ok $? $0 $FUNCNAME "预处理预测文件报错"

}

###########################################################
# 预测
function _xgboost_predict() {
    cd ${APPS_DIR}

    ${PYTHON3} ${APPS_DIR}/rtb/predict/xgboost_predict.py \
        --log_path ${LOG_file} \
        --in_predict_input_file ${FEATURE_DIR}/test_encode.txt \
        --in_xgb_model_path "${TRAIN_DIR}/xgb_model.pkl" \
        --out_predict_output_file ${PREDICT_DIR}/label_res.txt

    check_is_ok $? $0 $FUNCNAME "预估报错"
}

function _xgboost_lr_predict() {
    cd ${APPS_DIR}

    ${PYTHON3} ${APPS_DIR}/rtb/predict/xgboost_lr_predict_.py \
        --log_path ${LOG_file} \
        --in_predict_input_file ${FEATURE_DIR}/test_encode.txt \
        --in_one_hot_encoder_path ${TRAIN_DIR}/one_hot.out \
        --in_xgb_model_path "${TRAIN_DIR}/xgb_model.pkl" \
        --in_lr_model_path "${TRAIN_DIR}/lr_model.pkl" \
        --out_predict_output_file ${PREDICT_DIR}/label_res.txt

    check_is_ok $? $0 $FUNCNAME "预估报错"
}

function _deepfm_predict() {
    cd ${APPS_DIR}

    ${PYTHON3} ${APPS_DIR}/rtb/predict/deepfm_predict.py \
        --log_path ${LOG_file} \
        --in_predict_input_file ${FEATURE_DIR}/test_encode.txt \
        --in_deepfm_model_path "${TRAIN_DIR}/deepfm_model.h5" \
        --out_predict_output_file ${PREDICT_DIR}/label_res.txt

    check_is_ok $? $0 $FUNCNAME "预估报错"
}

function _xdeepfm_predict() {
    cd ${APPS_DIR}

    ${PYTHON3} ${APPS_DIR}/rtb/predict/xdeepfm_predict.py \
        --log_path ${LOG_file} \
        --in_predict_input_file ${FEATURE_DIR}/test_encode.txt \
        --in_deepfm_model_path "${TRAIN_DIR}/xdeepfm_model.h5" \
        --out_predict_output_file ${PREDICT_DIR}/label_res.txt

    check_is_ok $? $0 $FUNCNAME "预估报错"
}

#######################################
##评估相关
#######################################
function _auc() {
    echo "====auc===="
    cd ${APPS_DIR}
    ${PYTHON3} ${WORK_DIR}/src/apps/rtb/evaluate/auc.py \
        --log_path ${LOG_file} \
        --in_predict_real_file "${ETL_DIR}"/test.label \
        --in_predict_res_file ${PREDICT_DIR}/label_res.txt
}

# 混淆矩阵
function _confusion_matrix() {
    # 校验(1,0) 准确度的
    env JAVA_OPTS="-Xms256m -Xmx512m" scala \
        -savecompiled ${WORK_DIR}/src/evaluate/confusion_matrix.scala \
        "${ETL_DIR}"/test.label \
        ${PREDICT_DIR}/label_res.txt

    # 混淆矩阵
    # ${PYTHON3} ${WORK_DIR}/src/apps/rtb/evaluate/confusion_matrix.py \
    #    --log_path ${LOG_file} \
    #    --in_predict_real_file "${ETL_DIR}"/test.label \
    #    --in_predict_res_file ${PREDICT_DIR}/label_res.txt
}

# CTR 0.1 0.2........0.9出现的概率统计
function _ctr_rate_stat() {
    echo "ctr_rate_stat"
    env JAVA_OPTS="-Xms256m -Xmx512m" scala \
        -savecompiled ${WORK_DIR}/src/evaluate/ctr_rate_stat.scala \
        ${PREDICT_DIR}/label_res.txt
}

###################################
## 更新模型
function update_online_models() {
    for server_host in ${SERVER_HOST[@]}; do
        # 删除接口服务器的过期文件
        ssh apps@${server_host} rm -rf ${REMOTE_HTTP_SERVER_DATA_DIR}/${DEL_DATE}_${ETL_HOUR}
        check_is_ok $? $0 $FUNCNAME

        ssh apps@${server_host} mkdir -p ${REMOTE_HTTP_SERVER_DATA_DIR}/${ETL_DATE}_${ETL_HOUR}
        check_is_ok $? $0 $FUNCNAME

        scp ${FEATURE_DIR}/label.out apps@${server_host}:${REMOTE_HTTP_SERVER_DATA_DIR}/${ETL_DATE}_${ETL_HOUR}/
        scp ${TRAIN_DIR}/xgb_model.pkl apps@${server_host}:${REMOTE_HTTP_SERVER_DATA_DIR}/${ETL_DATE}_${ETL_HOUR}/
        check_is_ok $? $0 $FUNCNAME

        # 更新model
        ssh apps@${server_host} sh ${REMOTE_HTTP_SERVER_DATA_DIR}/script/curl_process.sh ${ETL_DATE} ${ETL_HOUR}
        check_is_ok $? $0 $FUNCNAME
    done
}

########################################
## 删除本地历史文件
function del_history_data() {
    #    rm -rf ${DATA_DIR}/etl/${DEL_DATE}/${ETL_HOUR}               # 上游输入目录
    #    rm -rf ${DATA_DIR}/preprocess/${DEL_DATE}/${ETL_HOUR} # 拆分列
    #    rm -rf ${DATA_DIR}/feature/${DEL_DATE}/${ETL_HOUR}       # label_encode
    #    rm -rf ${DATA_DIR}/train/${DEL_DATE}/${ETL_HOUR}           # 训练
    #    rm -rf ${DATA_DIR}/predict/${DEL_DATE}/${ETL_HOUR}       # 预测的结果
    rm -rf ${DATA_DIR}/*/${DEL_DATE}/${ETL_HOUR} # 预测的结果

    if [ "$ETL_HOUR" == "23" ]; then
        rm -rf ${DATA_DIR}/*/${DEL_DATE}
    fi
}

##############################################################################

# 数据预处理,包括label_encode
function preprocess_all_train() {
    # 训练
    _preprocess_split_train
    _feature_train
}

# 包括label_encode
function preprocess_all_predict(){
    _preprocess_split_predict
    _feature_predict
}


# 训练模型
function train() {
    case $use_model_type in
    "xgboost")
        _xgboost_train
        ;;
    "xgboost_lr")
        _xgboost_lr_train
        ;;
    "deepfm")
        _deepfm_train
        ;;
    "xdeepfm")
        _xdeepfm_train
        ;;
    *)
        echo "未知的use_model_type"
        ;;
    esac
}

# 预测模型
function predict() {
     case $use_model_type in
    "xgboost")
        _xgboost_predict
        ;;
    "xgboost_lr")
        _xgboost_lr_predict
        ;;
    "deepfm")
        _deepfm_predict
        ;;
    "xdeepfm")
        _xdeepfm_predict
        ;;
    *)
        echo "未知的use_model_type"
        ;;
    esac
}

# 评估
function evaluate() {
    _auc
    _confusion_matrix
    _ctr_rate_stat
}

###################################
##############  main ##############
###################################
init

#del_history_data
#
## 预处理,包括选择字段和label_encode
#preprocess_all_train
#
## 训练
#train

if [ "${if_predict}" == "true" ];then
    # 选择字段和label_encode
#    preprocess_all_predict
    # 预测
    predict

    # 检验
    evaluate
fi

# update_online_models

exit 0

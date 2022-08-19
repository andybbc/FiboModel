#!/bin/bash

set -x
set -e

#########################################
export WORK_DIR=$(cd $(dirname $0);cd ..; pwd)  # ma路径



TODAY_HOUR=`date "+%Y-%m-%d_%H"`
export TODAY=`echo ${TODAY_HOUR} | awk -F '_' '{print $1}'`
export HOUR=`echo ${TODAY_HOUR} | awk -F '_' '{print $2}'`

if [ $# == 2 ];then
    TODAY=$1
    HOUR=$2
fi


echo "业务处理时间:${TODAY}  ${HOUR}"
export TODAY_HOUR="${TODAY}_${HOUR}"


#############################
export INPUT_HOUR_FILE_NUMS=5  # 日志数据几小时前的数据进行统计

# 删除5天前的报告数据
export OLD_FILE_RETAIN_DAYS=5

# 文章相似度 取多长时间的文章(小时)
export OLD_NEWS_SIMILARITY_DELTA=120

# 两个算法合并的权重
export APRIORI_MERGE_RATE=1
export SIMIARYTIY_MERGE_RATE=0.1

##############################################
# 初始化一些路径
function init(){
    mkdir -p ${WORK_DIR}/logs/${TODAY}  # 日志目录

    # 本地输出目录
    export DATA_DIR=${WORK_DIR}/data/${TODAY_HOUR}

    export RAW_DIR="${DATA_DIR}/raw"                            # 原始数据目录
    export RAW_BEHAVIOR_DIR="${RAW_DIR}/behavior"               # 生成的行为全局明细文件和 按媒体分组的文件
    export RAW_TEXT_DIR="${RAW_DIR}/text"                       # 文本数据目录

    export ALGORITHS_DIR="${DATA_DIR}/algorithms"                            # 推算算法中间目录
    export ALGORITHS_TOP_DIR="${ALGORITHS_DIR}/top"                            # 全局TOP1000,按频道分组TOP100,按媒体分组TOP100
    export ALGORITHS_COLLABORATIVE_DIR="${ALGORITHS_DIR}/collaborative"        # 推荐算法生成的文件
    export ALGORITHS_ARTICLE_SIMILARY_DIR="${ALGORITHS_DIR}/article_similary"  # 新闻相似度

    export COMBINE_DIR="${DATA_DIR}/combine"                        # top合并后的最终文件的dir
    export COMBINER_TOP_DIR="${COMBINE_DIR}/top"                 # top合并后的最终文件的dir

    export log_file=${WORK_DIR}/logs/${TODAY}/log_${HOUR}.log

    # 一些脚本位置
    export PYTHON_APP_PATH=${WORK_DIR}/src/app  # src/app
    export SHELL_ENGINE_PATH=${WORK_DIR}/shell/engine  # shell/engine
    export SHELL_UTILS_PATH=${WORK_DIR}/shell/utils  # shell/utils
    export JAR_PATH=${WORK_DIR}/lib
}

init



. ${SHELL_UTILS_PATH}/env.sh
. ${SHELL_UTILS_PATH}/tool.sh
#########################################

# 生成raw文件,包括行为推荐和文章相似度
sh ${SHELL_ENGINE_PATH}/get_file.sh

# 生成TOP文件
sh ${SHELL_ENGINE_PATH}/top.sh

# 生成行为规则文件
sh ${SHELL_ENGINE_PATH}/behavior.sh

# 生成文章相似度文件
sh ${SHELL_ENGINE_PATH}/text.sh

# 合并关联规则推荐和文章相似度,合并TOP
sh ${SHELL_ENGINE_PATH}/merge_similarity.sh

# 加载到redis
sh ${SHELL_ENGINE_PATH}/load_to_redis.sh




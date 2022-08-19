#!/bin/bash

set -x
set -e

export WORK_DIR=$(cd $(dirname $0);cd ..; pwd)
. ${WORK_DIR}/shell/utils/env.sh

# 分析脚本
TODAY=`date "+%Y-%m-%d"`


hdfs_data_path="/data/hippo/storm_clk/${TODAY}"
local_out_path="${WORK_DIR}/data/analysis"



if [ ! -e $local_out_path  ];then
    mkdir -p $local_out_path
fi

# 统计原始日志中的新闻id出现的最大值,最小值,平均数,中位数,输出文本到${local_out_path}中
spark-submit \
    --master yarn \
    --class com.advlion.www.collaborative.analysis.AnalysisTask \
    ${WORK_DIR}/lib/hippo.jar \
    --hdfs_input_path ${hdfs_data_path} \
    --local_out_path ${local_out_path}/analysis`date "+%Y-%m-%d_%H_%M_%S"`.txt

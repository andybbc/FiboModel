#!/bin/bash

# 运行环境

export PYTHON3=/usr/bin/python3
export SPARK_SUBMIT='/usr/bin/spark-submit'
export HDFS=/usr/bin/hdfs

export LAST_DATE=$(date -d '1 hour ago' "+%Y%m%d")
export LAST_HOUR=$(date -d '1 hour ago' "+%H")

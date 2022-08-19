#!/bin/bash
set -x
if [ ! -n "$WORK_DIR" ]||[ ! -n "$TODAY_HOUR" ]; then
   log "请从run开始执行,没有初始化变量,当前路径未知,程序退出!!!"
   exit 1
fi

# 提取新闻关键字
function gen_news_tag(){
	log "文本相似度开始提取新闻关键字"
	cd ${PYTHON_APP_PATH}
	$PYTHON3 gen_news_tag.py \
		--in_file ${RAW_TEXT_DIR}/old_news_list.json \
  		--out_file ${RAW_TEXT_DIR}/tags_list.json \
		--log_path ${log_file}
	check_is_ok $? $0 $FUNCNAME
}


# TODO 通过机器学习生成的推荐文件
function similarity_run(){

	log "开始全局similarity算法计算文章相似度"
	cd ${PYTHON_APP_PATH}
	$PYTHON3 cal_similarity.py \
		--in_file ${RAW_TEXT_DIR}/tags_list.json \
		--similarity_file ${ALGORITHS_ARTICLE_SIMILARY_DIR}/news_similarity_range.txt \
		--log_path ${log_file}

  check_is_ok $? $0 $FUNCNAME
    # sed -i 's/,$//g' $SIMILARITY_OUT_FILE
}


# 根据频道分组来生成文件
function similarity_run_group(){
	local process_type=$1

	mkdir -p ${ALGORITHS_ARTICLE_SIMILARY_DIR}/${process_type}

	cd ${PYTHON_APP_PATH}

	for file in `ls ${RAW_BEHAVIOR_DIR}/${process_type}`
	do
		log "开始${file} similarity算法计算文章相似度"
		$PYTHON3 cal_similarity.py \
			--news_file ${RAW_TEXT_DIR}/${process_type}/${file}_old_news_list.json \
			--range_file ${ALGORITHS_ARTICLE_SIMILARY_DIR}/${process_type}/${file}_news_similarity_range.txt \
			--log_path ${log_file}

	  check_is_ok $? $0 $FUNCNAME
	done
}

gen_news_tag  # 2. 提取新闻关键字
similarity_run

#similarity_run_group channel

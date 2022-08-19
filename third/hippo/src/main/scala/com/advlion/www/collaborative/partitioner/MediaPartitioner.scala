package com.advlion.www.collaborative.partitioner

import org.apache.spark.Partitioner


class MediaPartitioner(mediaWithIndex:Map[String,Int]) extends Partitioner{
    //给每个cid配一个分区号(使用它们的索引)
    override def numPartitions: Int = {
        mediaWithIndex.size
    }

    override def getPartition(key: Any): Int = {
        key match{
            case channel:String =>mediaWithIndex(channel) //partitionBy是根据key来分区
        }
    }
}

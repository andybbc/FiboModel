package com.advlion.www.realtime.handler

import com.advlion.www.collaborative.Clk_log
import com.advlion.www.realtime.util.RedisUtil
import org.apache.spark.sql.SparkSession
import org.apache.spark.streaming.{Minutes, Seconds}
import org.apache.spark.streaming.dstream.DStream

import scala.collection.{SortedMap, mutable}


/**
  * 点击量前1000的排名
  */
object TopNewsIdParseHandler {
    // 想用structedStreaming,但是不支持limit操作
    //    def statTopAll(spark:SparkSession,clkLogs:Dataset[Clk])={
    //        import spark.implicits._
    //
    //        //
    //    }

    def statTopAll(windowClkLogDStream: DStream[Clk_log]) = {


        //2.转换数据结构
        windowClkLogDStream.transform(rdd => {
            rdd.map(c => (c.contentId, 1))
                .reduceByKey(_ + _)
                .repartition(1)
                .mapPartitions(iter => {
                    val strings = iter.toList.sortWith(_._2 < _._2)
                        .take(1000).map(x => x._1)
                    strings.iterator
                })
        })
            .foreachRDD(rdd => {
                //                println("======================"+rdd.collect().mkString("."))
                //对每个分区单独处理
                rdd.foreachPartition(iter => {
                    if (iter.nonEmpty) {
                        val topAllKey = "TopN:all"
                        val client = RedisUtil.getJedisClient
                        try {
                            client.select(1)

                            val pipe = client.pipelined

                            val arr = iter.toArray
                            client.lpush(topAllKey, arr: _*)

                            client.ltrim(topAllKey, 0, if (arr.length > 999) 999 else arr.length - 1)
                            pipe.sync()
                        } catch {
                            case e: Exception => e.printStackTrace()
                        } finally {
                            if (client != null) client.close()
                        }


                    }
                })
            })


    }

    /**
      * 根据频道分组,每组100个
      *
      * @param windowClkLogDStream
      */
    def statTOPChannel(windowClkLogDStream: DStream[Clk_log]) = {
        windowClkLogDStream.transform { rdd =>
            rdd.map(c => ((c.channel, c.contentId), 1))
                .reduceByKey(_ + _)
                .map(c => (c._1._1, (c._1._2, c._2)))
                .groupByKey()
                .map {
                    case (channel, items) =>
                        //每个渠道前100个
                        val filterItems = items.toArray.sortWith(_._2 < _._2).take(100).map(x => x._1)
                        (channel, filterItems)
                }
        }.repartition(1)
            .foreachRDD { rdd =>
                rdd.foreachPartition(iter => {
                    if (iter.nonEmpty) {
                        val client = RedisUtil.getJedisClient
                        client.select(1)
                        val pipe/**/ = client.pipelined
                        iter.foreach { case (channel, arr) =>

                            val topChannelKey = "TopN:" + channel
                            try {
                                client.lpush(topChannelKey, arr: _*)
                                client.ltrim(topChannelKey, 0, if (arr.length > 99) 99 else arr.length - 1)
                            } catch {
                                case e: Exception => e.printStackTrace()
                            }
                        }//
//                        pipe.sync()
                        if (client != null) client.close()
                    }
                })
            }
    }

    /**
      * 获取topN
      * @param items
      * @param topN
      * @return
      */
    def getTopN( items:List[(String, Int)],topN:Int) = {
        var sortedSet = mutable.SortedSet.empty[(String,Int)](Ordering.by((x:(String,Int)) => x._2))
        items.foreach({ tuple => {
            sortedSet += tuple
            if (sortedSet.size > topN) {
                sortedSet = sortedSet.takeRight(topN)
            }
        }
        })
        sortedSet.takeRight(topN).toIterator

    }

    def loadToRedis(topArray:Array[String],channelType:String,topN:Int): Unit ={
        val client = RedisUtil.getJedisClient
        client.select(1)

        val topChannelKey = "TopN:" + channelType
        try {
            client.lpush(topChannelKey, topArray : _*)
            client.ltrim(topChannelKey, 0, if (topArray.length > topN-1) topN-1 else topArray.length - 1)
        } catch {
            case e: Exception => e.printStackTrace()
        }finally {
            if (client != null) client.close()
        }
    }


    def statTop(clkLogDStream: DStream[Clk_log])= {
        clkLogDStream.map(c => ((c.channel, c.contentId), 1))
            .reduceByKeyAndWindow((x:Int,y:Int) => x + y,Minutes(120),Minutes(1))
            .map(c => (c._1._1, (c._1._2, c._2)))  //(channel,(content_id,count))
            .groupByKey()  //同一个频道
            .flatMap{
                case (channel, items) =>
                   val list= items.toList
                    //每个渠道前100个
                    val topNItems = getTopN(list,100).map(x => x._1).toArray

                    //直接导入到redis
                    if(topNItems.nonEmpty){
                        loadToRedis(topNItems,channel,100)
                    }

                    list
            }
            .reduceByKey(_+_) //每个内容id出现的次数
            .repartition(1)
            .mapPartitions(iter => {
                val tuples = getTopN(iter.toList,1000).map(x => x._1)
                tuples
            })
            .foreachRDD(rdd =>
                rdd.foreachPartition(iter => {
                    loadToRedis(iter.toArray,"all",1000)
                })
            )

    }

}

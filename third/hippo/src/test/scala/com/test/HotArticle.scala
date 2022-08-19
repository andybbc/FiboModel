package com.test

import java.io.{BufferedWriter, FileWriter}

import org.apache.log4j.{Level, Logger}
import org.apache.spark.rdd.RDD
import org.apache.spark.sql.SparkSession

object HotArticle {


    def main(args: Array[String]): Unit = {
        Logger.getLogger("org").setLevel(Level.WARN)
        val etlDate = args(0)
        val spark = SparkSession
            .builder()
            .appName("Hippo")
//            .config("hive.metastore.uris","thrift://www.bigdata02.com:9083")
            .config("spark.debug.maxToStringFields", "100")
//            .enableHiveSupport()
            .getOrCreate()
        spark.sparkContext.setLogLevel("WARN")

        //增加一个脚本，每天统计一下热门文章,top100
        //曝光,展示相关
        //与推荐有关的
        //文章有关
        //不同业务,只要和推荐有关数据
        // 全局top1000, 按频道每个前100
        val sc=spark.sparkContext

        val rdd= sc.textFile(s"hdfs://www.bigdata02.com:8020/data/hippo/storm_clk/${etlDate}/*")

        val clkLogRDD = rdd.mapPartitions(iter => {
            val clkLogs = iter.map(line => {
                val arr = line.split("\t")
                //  频道,//类型,1新闻 2广告,    //新闻id或广告位置 //cookie
                //channel:String,logType:String,contentId:String,cookie:String
                Clk_log(arr(15).trim, arr(18).trim,  arr(19).trim,arr(20).trim)
            }).filter(c => c.logType == "1" && (c.contentId!=null || c.contentId !="" ) && (c.channel!= null && c.channel != ""))  //只取1的
            clkLogs
        })

        clkLogRDD.cache()

        //下面是统计top
        //粒度是全局


//        writeFiles("aa.txt",allResult)



        // 统计出 cookie对应的 内容id的集合




    }

    /**
      * 根据cookie分组,各种新闻id的集合
      * s010669uQNMRjZNiF   yd_375b27bf8c7f0005a3f448b4541f033c,edn_015555d06ae6777b2e0b0e73d8e2a7b9,edn_d94565821e6a252fda1a9a8400ada6d3
      *
      * 返回RDD[String]
      */
    def getCookieDetail(clkLogRDD:RDD[Clk_log])={
        val value = clkLogRDD.map(c => (c.cookie, c.contentId)).distinct()
            .groupByKey()
            .map { case (c, iter) => c + "\t" + iter.mkString(",") }
        value
    }

    /**
      * 计算点击根据频道分组的top100
      * 在Driver端返回数组
      * @param clkLogRDD
      * @return
      */
    def computeChannelResult(clkLogRDD:RDD[Clk_log]):Array[String]={
        //粒度到频道,分组排序求TOPN
        val channleResult = clkLogRDD.map(c => ((c.channel, c.contentId), 1))
            .reduceByKey(_ + _)
            .map{ case ((channel,contentId),count) =>
                (channel,(contentId,count))
            }
            .groupByKey()  //根据channel分组
            .flatMap{case (channel,items) =>
                //每个渠道前100个
                val filterItems: Array[(String, Int)] = items.toArray.sortWith(_._2 > _._2).take(100)
                filterItems.map(item => channel + "," + item._1 + "," + item._2)
            }
            .collect()

        channleResult
    }

    /**
      * 计算全局的TOP1000
      * @param clkLogRDD
      * @return
      */
    def computeAllResult(clkLogRDD:RDD[Clk_log]):Array[String]={
        //总粒度,出现次数最高的top1000
        val allResult = clkLogRDD.map(c => (c.contentId, 1)).reduceByKey(_ + _)
            .sortBy(_._2, ascending = false).take(1000).map(tuple => tuple._1 + "," + tuple._2)
        allResult
    }

    def writeFiles(fileName:String,seq:Seq[String])={
        val writer = new BufferedWriter(new FileWriter(fileName))
        seq.foreach(line => {
            writer.write(line)
            writer.flush()
            writer.newLine()
        })
        writer.close()
    }
}

case class Clk_log(channel:String,logType:String,contentId:String,cookie:String)

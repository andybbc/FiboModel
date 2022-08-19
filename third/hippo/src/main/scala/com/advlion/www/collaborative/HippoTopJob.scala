package com.advlion.www.collaborative

import com.advlion.www.collaborative.HippoTask2.{computeAllResult, computeChannelResult, computeMediaResult, writeFiles}
import com.advlion.www.utils.Flag
import org.apache.log4j.{Level, Logger}
import org.apache.spark.sql.SparkSession

/**
  * 生成top内容
  */
object HippoTopJob {
    def main(args: Array[String]): Unit = {
        Logger.getLogger("org").setLevel(Level.WARN)
        Flag.Parse(args)
        val inputFile=Flag.GetString("input_file")
        val localAllResult=Flag.GetString("local_all_top")
        val localChannelResult = Flag.GetString("local_channel_top")
        val localMediaResult=Flag.GetString("local_media_top")


        val spark = SparkSession
            .builder()
            //        .master("local[*]")
            .appName("HippoTask")
            .config("hive.metastore.uris", "thrift://www.bigdata02.com:9083")
            .config("spark.debug.maxToStringFields", "100")
            .enableHiveSupport()
            .getOrCreate()
        spark.sparkContext.setLogLevel("WARN")
        import  spark.implicits._

        val sc = spark.sparkContext

        val rdd = sc.textFile(inputFile)

        //        val rdd=sc.textFile(s"/data/hippo/storm_clk/2020-07-30,/data/hippo/storm_clk/2020-07-31,/data/hippo/storm_clk/2020-08-01,/data/hippo/storm_clk/2020-08-02,/data/hippo/storm_clk/2020-08-03,/data/hippo/storm_clk/2020-08-04,/data/hippo/storm_clk/2020-08-05")
        val clkLogRDD = rdd.mapPartitions(iter => {
            val clkLogs = iter.map(line => {
                val arr = line.split("\t")
                //  频道,//类型,1新闻 2广告,    //新闻id或广告位置 //cookie
                //channel:String,logType:String,contentId:String,cookie:String
                Clk_log(arr(3).trim,arr(15).trim, arr(18).trim, arr(19).trim, arr(20).trim)
            }).filter(c => c.logType == "1" && (c.contentId != null || c.contentId != "") && c.contentId.length > 32 && c.contentId.contains("_")) //过滤内容ID为空的和前提 logType为新闻的
            clkLogs
        })

        //            .filter(c => c.logType == "1" && (c.contentId!=null || c.contentId !="" ) && (c.channel!= null && c.channel != ""))  //只取1的

        clkLogRDD.cache()


        // 过滤掉渠道为空的
        val clkLogRddFilterChannel = clkLogRDD.filter(c => c.channel != null && c.channel.trim != "")
        val clkLogRddFilterMedia = clkLogRDD.filter(c => c.mediaId != null && c.mediaId.trim != "")

        // TODO 1.下面是统计全局top 内容id,不需要过滤渠道为空的
        val allResult = computeAllResult(clkLogRDD)
        writeFiles(localAllResult, allResult) //输出到本地

        // TODO 2.每个渠道统计前100个,要过滤渠道
        if(localChannelResult != ""){
            val channelResult = computeChannelResult(clkLogRddFilterChannel)
            channelResult.map(_.split(",")).groupBy(_(0)).par.foreach(kv => {
                val name = kv._1
                val iter = kv._2
                val strings = iter.map(arr => arr(1) + "," + arr(2))
                writeFiles(localChannelResult+"/"+name, strings) //输出到本地
            })
        }



        // TODO 3.每个媒体统计前100个,要过滤媒体
        if(localMediaResult!=""){
            val mediaResult = computeMediaResult(clkLogRddFilterMedia,spark)
            mediaResult.map(_.split(",")).groupBy(_(0)).par.foreach(kv => {
                val name = kv._1
                val iter = kv._2
                val strings = iter.map(arr => arr(1) + "," + arr(2))
                writeFiles(localMediaResult+"/"+name, strings) //输出到本地
            })
        }

    }
}

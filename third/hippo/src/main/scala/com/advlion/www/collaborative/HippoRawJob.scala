package com.advlion.www.collaborative

import com.advlion.www.collaborative.HippoTask2.{getCookieDetail, getCookieDetailGroupByChannel, getCookieDetailGroupByMedia}
import com.advlion.www.utils.Flag
import org.apache.log4j.{Level, Logger}
import org.apache.spark.sql.SparkSession

object HippoRawJob {
    def main(args: Array[String]): Unit = {
        Logger.getLogger("org").setLevel(Level.WARN)
        Flag.Parse(args)
        val inputFile=Flag.GetString("input_file")
        val hdfsDetail = Flag.GetString("hdfs_detail")
        val hdfsMediaDetailDir= Flag.GetString("hdfs_media_detail")  //根据媒体分组的目录,为空,最后不要带/
        val hdfsChannelDetailDir = Flag.GetString("hdfs_channel_detail") //根据频道分组目录,为空,最后不要带/

        println(
            s"""输入参数:
               |input_file:${inputFile}
               |hdfs_detail:${hdfsDetail}
               |hdfs_media_detail:${hdfsMediaDetailDir}
               |hdfs_channel_detail:${hdfsChannelDetailDir}
               |
               |""".stripMargin)

        //    val etlDate = "2020-04-27"
        //    val etlHour = "14"
        val spark = SparkSession
            .builder()
            //        .master("local[*]")
            .appName("HippoRawJob")
            .config("hive.metastore.uris", "thrift://www.bigdata02.com:9083")
            .config("spark.debug.maxToStringFields", "100")
            .enableHiveSupport()
            .getOrCreate()
        spark.sparkContext.setLogLevel("WARN")
        import  spark.implicits._

        val sc = spark.sparkContext

        val rdd = sc.textFile(inputFile)

        val clkLogRDD = rdd.mapPartitions(iter => {
            val clkLogs = iter.map(line => {
                val arr = line.split("\t")
                //  频道,//类型,1新闻 2广告,    //新闻id或广告位置 //cookie
                //channel:String,logType:String,contentId:String,cookie:String
                Clk_log(arr(3).trim,arr(15).trim, arr(18).trim, arr(19).trim, arr(20).trim)
            }).filter(c => c.logType == "1" && (c.contentId != null || c.contentId != "") && c.contentId.length > 32 && c.contentId.contains("_")) //过滤内容ID为空的和前提 logType为新闻的
            clkLogs
        })

        clkLogRDD.cache()

        // TODO 4.生成cookie  内容id的组合
        if(hdfsDetail != ""){
            val value = getCookieDetail(clkLogRDD)
            value.coalesce(1).saveAsTextFile(hdfsDetail)
        }

        // TODO 5. 按媒体分组生成文件
        if(hdfsMediaDetailDir!=""){
            getCookieDetailGroupByMedia(sc,clkLogRDD,hdfsMediaDetailDir)
        }

        // TODO 6. 按频道分组生成文件
        if(hdfsChannelDetailDir!=""){
            getCookieDetailGroupByChannel(clkLogRDD,hdfsChannelDetailDir)
        }

        spark.stop
        sc.stop


    }
}

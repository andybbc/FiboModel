package com.advlion.www.collaborative

import java.io.{BufferedWriter, File, FileWriter}

import com.vlion.io.IOFactory
import org.apache.log4j.{Level, Logger}
import org.apache.spark.SparkContext
import org.apache.spark.rdd.RDD
import org.apache.spark.sql.SparkSession

/**
  * 增加一个脚本，每天统计一下热门文章,top100
  * 曝光,展示相关
  * 与推荐有关的
  * 文章有关
  * 不同业务,只要和推荐有关数据
  *
  * 点击日志统计:
  * 需求1:
  * 内容id,取全局top1000, 按频道每个前1000
  *
  * 需求2:
  * 内容id,根据频道分组,每组top100
  *
  * 需求3:
  * 内容id,根据媒体分组,每组top100
  *
  * 需求4:
  * 根据日志解析出指定格式的文件: cookie     concat(内容id)
  *
  * 需求5:
  * cookie concat(内容id) 是分组后的
  *
  * 需求6:
  * channel 分组,concat(内容id) 是分组后的
  */
object HippoTask2 {
    def main(args: Array[String]): Unit = {
        Logger.getLogger("org").setLevel(Level.WARN)
        //    val url = "jdbc:mysql://172.16.189.204:3306/hippo?user=VLION_HIPPO&password=VLION_HIPPO"
        val inputFile = args(0)
        val localAllResult = args(1)
        val localChannelResult = args(2) //本地channel输出目录
        val localMediaResult = args(3)
        val hdfsDetail = args(4)
        val hdfsMediaDetailDir= args(5)  //根据媒体分组的目录,为空,最后不要带/
        val hdfsChannelDetailDir = args(6) //根据频道分组目录,为空,最后不要带/

        //    val etlDate = "2020-04-27"
        //    val etlHour = "14"
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
        val channelResult = computeChannelResult(clkLogRddFilterChannel)
        channelResult.map(_.split(",")).groupBy(_(0)).par.foreach(kv => {
            val name = kv._1
            val iter = kv._2
            val strings = iter.map(arr => arr(1) + "," + arr(2))
            writeFiles(localChannelResult+"/"+name, strings) //输出到本地
        })


        // TODO 3.每个媒体统计前100个,要过滤媒体
        val mediaResult = computeMediaResult(clkLogRddFilterMedia,spark)
        mediaResult.map(_.split(",")).groupBy(_(0)).par.foreach(kv => {
            val name = kv._1
            val iter = kv._2
            val strings = iter.map(arr => arr(1) + "," + arr(2))
            writeFiles(localMediaResult+"/"+name, strings) //输出到本地
        })

        // TODO 4.生成cookie  内容id的组合
        val value = getCookieDetail(clkLogRDD)
        value.coalesce(1).saveAsTextFile(hdfsDetail)

        // TODO 5. 按媒体分组生成文件
        getCookieDetailGroupByMedia(sc,clkLogRDD,hdfsMediaDetailDir)

        // TODO 6. 按频道分组生成文件
        getCookieDetailGroupByChannel(clkLogRDD,hdfsChannelDetailDir)

        spark.stop
        sc.stop


    }

    /**
      * 5.根据频道分组,分别生成文件
      * @param clkLogRDD
      * @param splitFileBasePath 拆分文件的基础路径
      * @return
      */
    def getCookieDetailGroupByChannel(clkLogRDD:RDD[Clk_log],splitFileBasePath:String)={
        clkLogRDD.map(log => (log.channel,(log.cookie,log.contentId)))
            .filter(_._1 nonEmpty)
            .distinct()
            .groupByKey()
            .foreach(s => {
                val channel = s._1
                val contents = s._2
                val strings = contents.groupBy(_._1)
                    .filter(x => (x._2.size > 1 && x._2.size<=200))
                    .map( x=> x._1 + "\t" + x._2.map(_._2).mkString(","))

                if(strings.nonEmpty){
                    splitFileFun((channel,strings),splitFileBasePath)
                }

            })
    }

    /**
      * 5.根据媒体分组,分别生成文件
      * @param sc
      * @param clkLogRDD
      * @param splitFileBasePath 拆分文件的基础路径
      * @return
      */
    def getCookieDetailGroupByMedia(sc:SparkContext,clkLogRDD: RDD[Clk_log],splitFileBasePath:String) = {
//        val distinctMedia =getDistinctMedia(clkLogRDD).zipWithIndex.toMap
        //根据媒体分组,分别生成文件
        clkLogRDD.map( log => (log.mediaId,(log.cookie,log.contentId)))
                .filter(_._1 nonEmpty)
                .distinct
//                .groupByKey(new MediaPartitioner(distinctMedia)) //value已经包含所有数据了
                .groupByKey()
                .foreach(s => {
                    val mediaId=s._1  //key
                    val contents = s._2  // Iterable(cookie,contentId)
                    val strings = contents.groupBy(_._1) //根据cookie分组,返回一个Map[String,List[(String, String)]]
                        .filter(x => (x._2.size > 1 && x._2.size<=200))
                        .map(x => x._1 + "\t" + x._2.map(_._2).mkString(","))
                    if(strings.nonEmpty){
                        splitFileFun((mediaId,strings),splitFileBasePath)
                    }

                })

    }

    def getDistinctMedia(clkLogRDD: RDD[Clk_log]): Array[String] ={
        clkLogRDD.map(_.mediaId).distinct().sortBy(x => x,ascending = false).collect
    }

    /**
      * 根据 media分组,取出每个媒体的文件
      * @param input
      * @param splitFileBasePath
      * @return 返回文件路径的集合
      */
    def splitFileFun(input: (String, Iterable[String] ), splitFileBasePath: String): Iterator[String] = {

        val index = input._1
        val lines = input._2


        val splitFilePath = splitFileBasePath+"/"+index
        val writer = IOFactory.getSingleFileHdfsWriter
        val actualSplitFilePath = writer.create(splitFilePath)

        lines.foreach {
            line =>
                writer.write(line + "\n","UTF-8")
        }

        writer.close()

        List(  actualSplitFilePath ).toIterator
    }


    /**
      * 根据cookie分组,各种新闻id的集合
      * s010669uQNMRjZNiF   yd_375b27bf8c7f0005a3f448b4541f033c,edn_015555d06ae6777b2e0b0e73d8e2a7b9,edn_d94565821e6a252fda1a9a8400ada6d3
      *
      * 返回RDD[String]
      */
    def getCookieDetail(clkLogRDD: RDD[Clk_log]) = {
        val value = clkLogRDD.map(c => (c.cookie, c.contentId)).distinct()
            .groupByKey()
            .filter(x => (x._2.size > 1 && x._2.size<=200))
            .map { case (c, iter) => c + "\t" + iter.mkString(",") }

        value
    }


    /**
      * 计算点击根据频道分组的top100
      *
      * 在Driver端返回数组
      *
      * @param clkLogRDD
      * @return
      */
    def computeChannelResult(clkLogRDD: RDD[Clk_log]) = {
        //粒度到频道,分组排序求TOPN
        val channleResult = clkLogRDD.map(c => ((c.channel, c.contentId), 1))
            .reduceByKey(_ + _)
            .map { case ((channel, contentId), count) =>
                (channel, (contentId, count))
            }
            .groupByKey() //根据channel分组
            .flatMap { case (channel, items) =>
                //每个渠道前100个
                val filterItems: Array[(String, Int)] = items.toArray.sortWith(_._2 > _._2).take(100)
                filterItems.map(item => channel + "," + item._1 + "," + item._2)
            }
            .collect()

        channleResult
    }

    /**
      * 计算点击根据媒体分组top100的contentId
      * @param clkLogRDD
      */
    def computeMediaResult(clkLogRDD: RDD[Clk_log],spark:SparkSession) = {

        import spark.implicits._
        val clkLogDF = clkLogRDD.toDF
        clkLogDF.createOrReplaceTempView("clktable")
        val frame = spark.sql(
            s"""
               |
               |select
               |mediaId,
               |contentId,
               |cnt
               |from
               |(
               |    select
               |    mediaId,
               |    contentId,
               |    cnt,
               |    row_number() over(partition by mediaId order by cnt desc ) as r_n
               |    from
               |    (
               |    select
               |    mediaId,
               |    contentId,
               |    count(1) as cnt
               |    from
               |    clktable
               |    group by
               |    mediaId,contentId
               |    ) t
               |) t2
               |where r_n<=100
               |
               |""".stripMargin)

        val mediaResult= frame.map(r => r.getAs[String]("mediaId")+","+r.getAs[String]("contentId")+","+r.getAs[Int]("cnt"))
            .collect()

        //        val mediaResult = clkLogRDD.map(c => ((c.mediaId,c.contentId),1))
        //            .reduceByKey(_+_)
        //            .map(c => (c._1._1, (c._1._2, c._2)))
        //            .groupByKey()
        //            .flatMap{case (mediaId,items) =>
        //                //每个媒体前100个
        //                val filterItems=items.toArray.sortBy(_._2)(Ordering.Int.reverse)  //降序
        //                    .take(100)
        //                filterItems.map(item => mediaId + "," + item._1 + "," + item._2)
        //            }
        //            .collect

        mediaResult
    }

    /**
      * 计算全局的TOP1000
      *
      * @param clkLogRDD
      * @return
      */
    def computeAllResult(clkLogRDD: RDD[Clk_log]): Array[String] = {
        //出现次数最高的top1000
        val allResult = clkLogRDD.map(c => (c.contentId, 1)).combineByKey((v:Int) => v,(c:Int,v:Int) =>c+v, (c1:Int,c2:Int)=> c1+c2)
            .sortBy(_._2, ascending = false).take(1000).map(tuple => tuple._1 + "," + tuple._2)
        allResult
    }

    def writeFiles(fileName: String, seq: Seq[String]) = {
        val writer = new BufferedWriter(new FileWriter(new File(fileName)))
        seq.foreach(line => {
            writer.write(line)
            writer.newLine()
            writer.flush()
        })
        writer.close()
    }

}






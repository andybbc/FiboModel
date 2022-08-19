package com.advlion.www.load

import com.advlion.www.log.{ApiReq, Clk, H5Req, Imp, Incentives}
import org.apache.spark.rdd.RDD
import org.apache.spark.sql.SparkSession
import org.apache.spark.storage.StorageLevel

import scala.collection.mutable

/**
  * Created by Admin on 2020/4/8.
  */
object LoadLog {
  def readLog(spark: SparkSession, etlDate: String, etlHour: String): Unit = {
    //  val etlDate = args(0).toString
    //  val etlHour = args(1).toString
    println("读取日志")
    println("etlDate=" + etlDate)
    println("etlHour=" + etlHour)
    val etlTime = etlDate + "_" + etlHour
    val hourTime = etlDate + " " + etlHour + ":00:00"
    import spark.implicits._
    //从hdfs上读取
    val h5ReqRDD = spark.sparkContext
      .textFile(s"/data/hippo/storm_h5_req/$etlDate/storm_h5_req_vlionserver-*_$etlTime.log")
      .persist(StorageLevel.MEMORY_AND_DISK_SER)
    val apiReqRDD = spark.sparkContext
      .textFile(s"/data/hippo/storm_api_req/$etlDate/storm_api_req_vlionserver-*_$etlTime.log")
      .persist(StorageLevel.MEMORY_AND_DISK_SER)
    val impRDD = spark.sparkContext
      .textFile(s"/data/hippo/storm_imp/$etlDate/storm_imp_vlionserver-*_$etlTime.log")
      .persist(StorageLevel.MEMORY_AND_DISK_SER)
    val clkRDD = spark.sparkContext
      .textFile(s"/data/hippo/storm_clk/$etlDate/storm_clk_vlionserver-*_$etlTime.log")
      .persist(StorageLevel.MEMORY_AND_DISK_SER)

//    val h5Reqbroadcast = spark.sparkContext.broadcast(h5ReqRDD)
//    val apiReqbroadcast = spark.sparkContext.broadcast(apiReqRDD)
//    val impqbroadcast = spark.sparkContext.broadcast(impRDD)
//    val clkeqbroadcast = spark.sparkContext.broadcast(clkRDD)
    //从本地服务器上读的file:///
    //  val h5ReqRDD = spark.sparkContext.textFile(s"file:///home/ETL/DATA/HIPPO/SEND_HIPPO/STORM_H5_REQ/$etlDate/storm_h5_req_vlionserver-226_$etlTime.log")
    //  val apiReqRDD = spark.sparkContext.textFile(s"file:///home/ETL/DATA/HIPPO/STORM_API_REQ/$etlDate/storm_api_req_vlionserver-226_$etlTime.log")
    //  val impRDD = spark.sparkContext.textFile(s"file:///home/ETL/DATA/HIPPO/STORM_IMP/$etlDate/storm_imp_vlionserver-226_$etlTime.log")
    //  val clkRDD = spark.sparkContext.textFile(s"file:///home/ETL/DATA/HIPPO/STORM_CLK/$etlDate/storm_clk_vlionserver-226_$etlTime.log")

    val h5ReqDF = h5ReqRDD.map(item => {
      val x = item.split("\\t",-1)
      H5Req(x(1).toInt, x(2).trim, x(3).trim, x(16).trim)
    }).toDF()


    val apiReqDF = apiReqRDD.map(item => {
      val x = item.split("\\t",-1)
      ApiReq(x(1).toInt, x(2).trim, x(3).trim, x(4).trim,x(7).trim,x(8).trim,x(10).trim,x(15).trim, x(20).trim, x(22).trim)
    }).toDF()

    val impDF = impRDD.map(item => {
      val x = item.split("\\t",-1)
      Imp(x(1).toInt, x(2).trim, x(3).trim, x(15).trim, x(17).trim.replaceAll(",",""), x(18).trim, x(21).trim, x(22).trim, x(23).trim, x(25).trim)
    }).toDF()

    val clkDF = clkRDD.map(item => {
      val x = item.split("\\t",-1)
      Clk(x(1).toInt, x(2).trim, x(3).trim, x(15).trim, x(17).trim.replaceAll(",",""), x(18).trim, x(21).trim, x(22).trim, x(23).trim, x(25).trim)
    }).toDF()

//      clkDF.map(_.getAs[String]("mediaGateID")).map((_,1)).rdd.reduceByKey(_+_).collect().foreach(println)

    //创建临时表
    h5ReqDF.createOrReplaceTempView("h5Req")
    apiReqDF.createOrReplaceTempView("apiReq")
    impDF.createOrReplaceTempView("imp")
    clkDF.createOrReplaceTempView("clk")

    val h5ReqSummary = spark.sql(
      s"""select '$hourTime' time,
         |    case when mediaID = ''  then '-1' else mediaID end mediaID,
         |		case when mediaGateID = ''  then '-1' else mediaGateID end mediaGateID,
         |		'-1' channel,
         |		'-1' contentID,
         |		'-1' advSource,
         |		'-1' advSourceID,
         |		'-1' advTypeID,
         |		case when cityID = ''  then '-1' else cityID end cityID,
         |		count(1) h5Req,
         |		0 apiReq,
         |		0 crImp,
         |		0 adImp,
         |		0 crClk,
         |		0 adClk
         |from 	h5Req
         |group by mediaID,mediaGateID,cityID
         |""".stripMargin).cache()
    //    h5ReqSummary.createTempView("h5ReqSummary")

    val apiReqSummary = spark.sql(
      s"""select  '$hourTime' time,
         |    case when mediaID = ''  then '-1' else mediaID end mediaID,
         |		case when mediaGateID = ''  then '-1' else mediaGateID end mediaGateID,
         |		case when channel='' then '固定' else channel end channel,
         |		'-1' contentID,
         |		'-1' advSource,
         |		'-1' advSourceID,
         |		'-1' advTypeID,
         |		case when cityID = ''  then '-1' else cityID end cityID,
         |		0 h5Req,
         |		count(1) apiReq,
         |		0 crImp,
         |		0 adImp,
         |		0 crClk,
         |		0 adClk
         |from 	apiReq
         |group by mediaID,mediaGateID,case when channel='' then '固定' else channel end,cityID
         |""".stripMargin).cache()
    //    apiReqSummary.createTempView("apiReqSummary")

    val impSummary = spark.sql(
      s"""
         |select '$hourTime' time,
         |    case when mediaID = ''  then '-1' else mediaID end mediaID,
         |		case when mediaGateID = ''  then '-1' else mediaGateID end mediaGateID,
         |		case when channel='' then '固定' else channel end channel,
         |		case when contentID = ''  then '-1' else contentID end as contentID,
         |		case when advSource = ''  then '-1' else advSource end as advSource,
         |		case when advSourceID = ''  then '-1' else advSourceID end as advSourceID,
         |		case when advTypeID = ''  then '-1' else advTypeID end as advTypeID,
         |		case when cityID = ''  then '-1' else cityID end cityID,
         |		0 h5Req,
         |		0 apiReq,
         |    count(case when advType='1' then 1 end) crImp,
         |		count(case when advType='2' then 1 end) adImp,
         |		0 crClk,
         |		0 adClk
         |from 	imp
         |group by mediaID,mediaGateID,case when channel='' then '固定' else channel end,case when contentID = ''  then '-1' else contentID end,
         |         case when advSource = ''  then '-1' else advSource end,case when advSourceID = ''  then '-1' else advSourceID end,
         |         case when advTypeID = ''  then '-1' else advTypeID end,cityID
         |""".stripMargin).cache()

    val clkSummary = spark.sql(
      s"""
         |select  '$hourTime' time,
         |    case when mediaID = ''  then '-1' else mediaID end mediaID,
         |		case when mediaGateID = ''  then '-1' else mediaGateID end mediaGateID,
         |		case when channel='' then '固定' else channel end channel,
         |		case when contentID = ''  then '-1' else contentID end as contentID,
         |		case when advSource = ''  then '-1' else advSource end as advSource,
         |		case when advSourceID = ''  then '-1' else advSourceID end as advSourceID,
         |		case when advTypeID = ''  then '-1' else advTypeID end as advTypeID,
         |		case when cityID = ''  then '-1' else cityID end cityID,
         |		0 h5Req,
         |		0 apiReq,
         |    0 crImp,
         |		0 adImp,
         |		count(case when advType='1' then 1 end) crClk,
         |		count(case when advType='2' then 1 end) adClk
         |from 	clk
         |group by mediaID,mediaGateID,case when channel='' then '固定' else channel end,case when contentID = ''  then '-1' else contentID end,
         |         case when advSource = ''  then '-1' else advSource end,case when advSourceID = ''  then '-1' else advSourceID end,
         |         case when advTypeID = ''  then '-1' else advTypeID end,cityID
         |""".stripMargin).cache()
    //    clkSummary.createTempView("clkSummary")

        val unionSummary = h5ReqSummary.union(apiReqSummary).union(impSummary).union(clkSummary)
          .groupBy( "mediaID", "mediaGateID", "channel", "contentID", "advSource", "advSourceID", "advTypeID", "cityID")
//          .agg(("h5Req","sum"),("apiReq","sum"),("crImp", "sum"),("adImp","sum"),("crClk","sum"), ("adClk" ,"sum"))
          .sum("h5Req", "apiReq", "crImp", "adImp", "crClk", "adClk")
          .toDF("mediaID","mediaGateID","channel","contentID",
                "advSource","advSourceID","advTypeID","cityID",
                "h5Req","apiReq","crImp","adImp","crClk","adClk")
        unionSummary.createOrReplaceTempView("unionSummary")




    //20200908需要求一天的uv,需要把当天的日志拿过来分析
    /*
        hippo项目，需要加一个日uv统计，日志类型：api_req

        根据字段5操作系统判断，安卓取imei（8），ios取idfa（11）

        数据库，new_stat_province 这个表的h5_uv字段

        按天去重计数

        每天凌晨跑前一天的

      */
    val apiReqDayRDD = spark.sparkContext.textFile(s"/data/hippo/storm_api_req/$etlDate")

    val apiReqDay = apiReqDayRDD.map(item => {
      val x = item.split("\\t",-1)
      ApiReq(x(1).toInt, x(2).trim, x(3).trim, x(4).trim,x(7).trim,x(8).trim,x(10).trim,x(15).trim, x(20).trim, x(22).trim)
    }).toDF()

    apiReqDay.createOrReplaceTempView("apiReqDay")

//    spark.sql(
//      s"""
//         |select  '$etlDate' time,
//         |    case when mediaID = ''  then '-1' else mediaID end mediaID,
//         |		case when mediaGateID = ''  then '-1' else mediaGateID end mediaGateID,
//         |		case when channel='' then '固定' else channel end channel,
//         |		case when cityID = ''  then '-1' else cityID end cityID,
//         |      count(distinct case when os in ('1','2') then coalesce(imei,idfa) else cookie end ) as uv
//         |from 	apiReqDay
//         |group by mediaID,mediaGateID,case when channel='' then '固定' else channel end,cityID
//         |
//         |""".stripMargin)

//    spark.sql(
//      s"""
//         |select '$etlDate' time,
//         |      case when mediaID = ''  then '-1' else mediaID end mediaID,
//         |		case when mediaGateID = ''  then '-1' else mediaGateID end mediaGateID,
//         |		case when channel='' then '固定' else channel end channel,
//         |		case when cityID = ''  then '-1' else cityID end cityID,
//         |  case when os in ('1','2') then coalesce(imei,idfa) else cookie end as u_id -- uv用
//         |from   apiReqDay
//         |
//         |""".stripMargin).createOrReplaceTempView("apiReqDay2")



  }

    /**
      * 20200921需求,新的服务器vlionserver-126,按天统计日志
      * 分时段 APP 启动次数柱状图
      *  http://wiki.vlion.cn/pages/viewpage.action?pageId=36438151
      *
      * @param spark
      * @param etlDate
      * @return
      */
  def readDayLog(spark: SparkSession, etlDate: String): Unit ={

        val _126AnalysisRDD = spark.sparkContext
                .textFile(s"/data/hippo/incentives/${etlDate}")

        val incentivesRDD: RDD[Incentives] = _126AnalysisRDD.mapPartitions(iter => {
            iter.filter(_.matches(".*\\[\\[\\[.*\\]\\]\\].*")) //可以过滤
                .map[Incentives](log => {
                    val map = mutable.Map[String, String]()
                    log.substring(log.indexOf("[[[") + 3, log.indexOf("]]]"))
                        .split("&")
                        .foreach(kv => {
                            val arr = kv.split("=",-1)
                            map += (arr(0) -> arr(1))
                        })
                    Incentives(map("ts").toLong, map("type").toInt, map("uid"), map("obj"), map("cnt").toLong)
                })

        })


      import spark.implicits._
      incentivesRDD
          .persist(StorageLevel.MEMORY_AND_DISK_SER)
          .toDF()
          .createOrReplaceTempView("incentives")
  }


    //20201027 上面的相同逻辑,-A
    def readDayLogA(spark: SparkSession, etlDate: String): Unit ={

        //20201027 126服务器处理相同的日志,-A结尾的
        val _126Analysis_A_RDD = spark.sparkContext
            .textFile(s"/data/hippo/incentives-A/${etlDate}")

        val incentives_A_RDD: RDD[Incentives] = _126Analysis_A_RDD.mapPartitions(iter => {
            iter.filter(_.matches(".*\\[\\[\\[.*\\]\\]\\].*")) //可以过滤
                .map[Incentives](log => {
                    val map = mutable.Map[String, String]()
                    log.substring(log.indexOf("[[[") + 3, log.indexOf("]]]"))
                        .split("&")
                        .foreach(kv => {
                            val arr = kv.split("=",-1)
                            map += (arr(0) -> arr(1))
                        })
                    Incentives(map("ts").toLong, map("type").toInt, map("uid"), map("obj"), map("cnt").toLong)
                })

        })

        import spark.implicits._

        incentives_A_RDD
            .persist(StorageLevel.MEMORY_AND_DISK_SER)
            .toDF()
            .createOrReplaceTempView("incentives_A")

    }


}
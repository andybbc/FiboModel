package com.advlion.www.task

import com.advlion.www.analysis.Summary
import com.advlion.www.load.LoadLog
import com.advlion.www.sync.ImportData
import com.advlion.www.utils.MysqlUtils
import org.apache.log4j.{Level, Logger}
import org.apache.spark.sql.SparkSession

/**
  * Created by Admin on 2020/4/8.
  */
object Hippo {
  def main(args: Array[String]): Unit = {
    Logger.getLogger("org").setLevel(Level.WARN)
//    val url = "jdbc:mysql://172.16.189.204:3306/hippo?user=VLION_HIPPO&password=VLION_HIPPO"
    val etlDate = args(0).toString
    val etlHour = args(1).toString
//    val etlDate = "2020-04-27"
//    val etlHour = "14"
    val spark = SparkSession
        .builder()
//        .master("local[*]")
        .appName("Hippo")
        .config("hive.metastore.uris","thrift://www.bigdata02.com:9083")
        .config("spark.debug.maxToStringFields", "100")
        .enableHiveSupport()
        .getOrCreate()
    spark.sparkContext.setLogLevel("WARN")
    ImportData.importMySQL(spark:SparkSession)
    LoadLog.readLog(spark:SparkSession,etlDate:String,etlHour:String)
    Summary.hourSummary(spark: SparkSession, etlDate, etlHour) //往stat_day表塞小时数据
    Summary.daySummary(spark:SparkSession,etlDate:String,etlHour:String)
    Summary.provinceSummary(spark:SparkSession,etlDate:String,etlHour:String)
    Summary.tagMap(spark:SparkSession)
      Summary.dataComparison(spark)

      //按天统计的
    if(etlHour == "23"){
      LoadLog.readDayLog(spark,etlDate)
        LoadLog.readDayLogA(spark,etlDate)
      Summary.incentivesSummaryByDay(spark,etlDate)
        Summary.incentivesASummaryByDay(spark,etlDate)
    }

    spark.stop()
  }
}

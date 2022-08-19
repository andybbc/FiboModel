package com.advlion.www.sync

import com.advlion.www.utils.MysqlJdbcUtils
import org.apache.spark.rdd.RDD
import org.apache.spark.sql.{DataFrame, Row, SparkSession}
import org.apache.spark.sql.types.{StringType, StructField, StructType}
import org.apache.spark.storage.StorageLevel

/**
  * Created by Admin on 2020/4/8.
  */
object ImportData {
  val APP = "app"
  val CITY = "city"
  val NEWS_CHANNEL = "news_channel"
  val OVERALL_REPORT = "overall_report"
  val url = MysqlJdbcUtils.url
  val user = MysqlJdbcUtils.user
  val password = MysqlJdbcUtils.password
  val uri = url + "?user=" + user + "&password=" + password

  def importMySQL(spark:SparkSession): Unit = {
    val appDF = spark.read.format("jdbc").options(Map("url" -> uri, "dbtable" -> APP)).load()
      .persist(StorageLevel.MEMORY_AND_DISK_SER)
    val cityDF = spark.read.format("jdbc").options(Map("url" -> uri, "dbtable" -> CITY)).load()
      .persist(StorageLevel.MEMORY_AND_DISK_SER)
    val newsChennelDF = spark.read.format("jdbc").options(Map("url" -> uri, "dbtable" -> NEWS_CHANNEL)).load()
      .persist(StorageLevel.MEMORY_AND_DISK_SER)
    val overallReportDF = spark.read.format("jdbc").options(Map("url" -> uri, "dbtable" -> OVERALL_REPORT)).load()
      .persist(StorageLevel.MEMORY_AND_DISK_SER)

    //创建一个channel = -1 表，后面关联使用，主要用来内连接NEWS_CHANNEL，以去除日志中的乱码问题
    val rdd: RDD[String] = spark.sparkContext.parallelize(Array("-1"))
    //4.将RDD[Int]转换为RDD[Row]
    val rowRDD: RDD[Row] = rdd.map(x => {
      Row(x)
    })
    val newsChennel_1 = StructType(StructField("name", StringType) :: Nil)
    //6.创建DF
    val newsChennelDF_1: DataFrame = spark.createDataFrame(rowRDD, newsChennel_1)

    //创建临时表
    appDF.createOrReplaceTempView("app")
    cityDF.createOrReplaceTempView("city")
    newsChennelDF.createOrReplaceTempView("newsChennel")
    overallReportDF.createOrReplaceTempView("overallReport")
    newsChennelDF_1.createOrReplaceTempView("newsChennel_1")


    //20201012按天统计,inactive task_info表和click_match_tab表
    val taskInfo = "task_info"
    val clickMatchTab = "click_match_tab"
    val urlIncentives = MysqlJdbcUtils.urlIncentives
    val userIncentives = MysqlJdbcUtils.userIncentives
    val passwordIncentives = MysqlJdbcUtils.passwordIncentives
    val uriIncentives = urlIncentives + "?user=" + userIncentives + "&password=" + passwordIncentives

    val taskInfoDF = spark.read.format("jdbc").options(Map("url" -> uriIncentives, "dbtable" -> taskInfo)).load()
        .persist(StorageLevel.MEMORY_AND_DISK_SER)


    val clickMatchTabDF = spark.read.format("jdbc").options(Map("url" -> uriIncentives, "dbtable" -> clickMatchTab)).load()
        .persist(StorageLevel.MEMORY_AND_DISK_SER)

    taskInfoDF.createOrReplaceTempView("taskInfo")
    clickMatchTabDF.createOrReplaceTempView("clickMatchTab")



  //20201027新增A,和上面一样
    val urlIncentivesA = MysqlJdbcUtils.urlIncentivesA
    val userIncentivesA = MysqlJdbcUtils.userIncentivesA
    val passwordIncentivesA = MysqlJdbcUtils.passwordIncentivesA
    val uriIncentivesA = urlIncentivesA + "?user=" + userIncentivesA + "&password=" + passwordIncentivesA

    val taskInfoDFA = spark.read.format("jdbc").options(Map("url" -> uriIncentivesA, "dbtable" -> taskInfo)).load()
        .persist(StorageLevel.MEMORY_AND_DISK_SER)


    val clickMatchTabDFA = spark.read.format("jdbc").options(Map("url" -> uriIncentivesA, "dbtable" -> clickMatchTab)).load()
        .persist(StorageLevel.MEMORY_AND_DISK_SER)

    taskInfoDFA.createOrReplaceTempView("taskInfoA")
    clickMatchTabDFA.createOrReplaceTempView("clickMatchTabA")


  }
}

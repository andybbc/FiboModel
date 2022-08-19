package com.test

import java.text.SimpleDateFormat
import java.util.Date

import com.advlion.www.utils.MysqlJdbcUtils.prop
import junit.framework.Test
import org.apache.parquet.format.IntType
import org.apache.spark.SparkContext
import org.apache.spark.rdd.RDD
import org.apache.spark.sql.{DataFrame, Row, SparkSession}
import org.apache.spark.sql.types.{DataType, IntegerType, StringType, StructField, StructType}
import org.apache.spark.storage.StorageLevel

/**
  * @Title: ${file_name}
  * @Package ${package_name}
  * @Description: ${todo}
  * @author malichun
  * @date 2020/7/20 002013:09
  */
object ParseLog {
    val sdf = new SimpleDateFormat("yyyy-MM-dd HH")

    def main(args: Array[String]): Unit = {
        // println(stampToDate("1595167201"))


    }


    def parse(spark: SparkSession) = {

        //        val APP = "app"
        //        val CITY = "city"
        //        val NEWS_CHANNEL = "news_channel"
        //        val OVERALL_REPORT = "overall_report"
        //
        //
        //        val url: String = "jdbc:mysql://172.16.189.204:3306/hippo"
        //        // val dbtable: String  = "hippo"
        //        val user: String  = "VLION_HIPPO"
        //        val password: String  = "VLION_HIPPO"
        //        val driver: String  = "com.mysql.jdbc.Driver"
        //
        //        val uri = url + "?user=" + user + "&password=" + password
        //
        //        val appDF = spark.read.format("jdbc").options(Map("url" -> uri, "dbtable" -> APP)).load().persist(StorageLevel.MEMORY_AND_DISK_SER)
        //        val cityDF = spark.read.format("jdbc").options(Map("url" -> uri, "dbtable" -> CITY)).load().persist(StorageLevel.MEMORY_AND_DISK_SER)
        //        val newsChennelDF = spark.read.format("jdbc").options(Map("url" -> uri, "dbtable" -> NEWS_CHANNEL)).load().persist(StorageLevel.MEMORY_AND_DISK_SER)
        //        val overallReportDF = spark.read.format("jdbc").options(Map("url" -> uri, "dbtable" -> OVERALL_REPORT)).load().persist(StorageLevel.MEMORY_AND_DISK_SER)
        //
        //        //创建一个channel = -1 表，后面关联使用，主要用来内连接NEWS_CHANNEL，以去除日志中的乱码问题
        //        val rdd: RDD[String] = spark.sparkContext.parallelize(Array("-1"))
        //        //4.将RDD[Int]转换为RDD[Row]
        //        val rowRDD: RDD[Row] = rdd.map(x => {
        //            Row(x)
        //        })
        //        val newsChennel_1 = StructType(StructField("name", StringType) :: Nil)
        //        //6.创建DF
        //        val newsChennelDF_1: DataFrame = spark.createDataFrame(rowRDD, newsChennel_1)
        //
        //        //创建临时表
        //        appDF.createOrReplaceTempView("app")
        //        cityDF.createOrReplaceTempView("city")
        //        newsChennelDF.createOrReplaceTempView("newsChennel")
        //        overallReportDF.createOrReplaceTempView("overallReport")
        //        newsChennelDF_1.createOrReplaceTempView("newsChennel_1")

        case class Imp(timestamp: Int, mediaID: String, mediaGateID: String, channel: String, contentID: String, advType: String,
                       advSource: String, advSourceID: String, advTypeID: String, cityID: String)

        val sc = new SparkContext

        //曝光
        val impRDD = sc.textFile("/data/hippo/storm_imp/*/*")

        import spark.implicits._
//
//        val impDF = impRDD.map(item => {
//            val x = item.split("\\t")
//            Imp(x(1).toInt, x(2).trim, x(3).trim, x(15).trim, x(17).trim, x(18).trim, x(21).trim, x(22).trim, x(23).trim, x(25).trim)
//        }).toDF()

//        impDF.createOrReplaceTempView("impDF")


        spark.sql(
            s"""
               | select
               |    from_unixtime(a.timestamp,'yyyy-MM-dd') as time,
               |    count(case when advType='1' then 1 end) crImp
               | from
               | impDF a
               | where mediaGateID='1234'
               | group by
               |from_unixtime(a.timestamp,'yyyy-MM-dd')
               |order by
               |from_unixtime(a.timestamp,'yyyy-MM-dd')
               |""".stripMargin)



        //点击
//        case class Clk(timestamp: Int, mediaID: String, mediaGateID: String, channel: String, contentID: String, advType: String,
//                       advSource: String, advSourceID: String, advTypeID: String, cityID: String)

        import spark.implicits._

//        val clkRDD = sc.textFile("/data/hippo/storm_clk/*/*")
//        val clkDF = clkRDD.map(item => {
//            val x = item.split("\\t")
//            Clk(x(1).toInt, x(2).trim, x(3).trim, x(15).trim, x(17).trim, x(18).trim, x(21).trim, x(22).trim, x(23).trim, x(25).trim)
//        }).toDF()
//
//        val rdd1 = clkRDD.map(line => {
//            val x = line.split("\\t")
//            Row(x(1).toInt, x(2).trim, x(3).trim, x(15).trim, x(17).trim, x(18).trim, x(21).trim, x(22).trim, x(23).trim, x(25).trim)
//        })
//
//        val structType = StructType(
//            StructField("timestamp", IntegerType)
//                :: StructField("mediaID", StringType)
//                :: StructField("mediaGateID", StringType)
//                :: StructField("channel", StringType)
//                :: StructField("contentID", StringType)
//                :: StructField("advType", StringType)
//                :: StructField("advSource", StringType)
//                :: StructField("advSourceID", StringType)
//                :: StructField("advTypeID", StringType)
//                :: StructField("cityID", StringType)
//                :: Nil
//
//        )

//        val frame = spark.createDataFrame(rdd1, structType)

//
//        val value = clkDF.mapPartitions(items => {
//            val sdf = new SimpleDateFormat("yyyy-MM-dd")
//            items.filter(_.getAs[String]("mediaGateID") == "1243").map(x => {
//                val timestamp = sdf.format(new Date((x.getAs[Int]("timestamp") + "000").toLong))
//                val advType = x.getAs[String]("advType")
//                val advType2 = advType match {
//                    case i if i == "1" => 1
//                    case _ => 0
//                }
//                (timestamp, advType2)
//            })
//        }
//        )
//        value.rdd.reduceByKey(_ + _)


                case class Clk(timestamp: Int, mediaID: String, mediaGateID: String, channel: String, contentID: String, advType: String,
                               advSource: String, advSourceID: String, advTypeID: String, cityID: String)

                import spark.implicits._

//                val clkRDD = sc.textFile("/data/hippo/storm_clk/*/*")
//                val clkDF = clkRDD.map(item => {
//                    val x = item.split("\\t")
//                    Clk(x(1).toInt, x(2).trim, x(3).trim, x(15).trim, x(17).trim, x(18).trim, x(21).trim, x(22).trim, x(23).trim, x(25).trim)
//                }).toDF()

//                clkDF.createOrReplaceTempView("clkDF")

                spark.sql(
                    s"""
                       | select
                       |    from_unixtime(a.timestamp,'yyyy-MM-dd') as time,
                       |    count(case when advType='1' then 1 end) crClk
                       | from
                       | clkDF a
                       | where mediaGateID='1234'
                       | group by
                       |from_unixtime(a.timestamp,'yyyy-MM-dd')
                       |order by
                       |from_unixtime(a.timestamp,'yyyy-MM-dd')
                       |
                       |""".stripMargin)


    }
}
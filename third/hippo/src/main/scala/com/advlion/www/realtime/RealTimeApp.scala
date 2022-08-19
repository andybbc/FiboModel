package com.advlion.www.realtime

import com.advlion.www.collaborative.Clk_log
import com.advlion.www.log.Clk
import com.advlion.www.realtime.handler.TopNewsIdParseHandler
import com.advlion.www.realtime.util.{MyKafkaUtil, PropertiesUtil}
import org.apache.spark.SparkConf
import org.apache.spark.sql.SparkSession
import org.apache.spark.streaming.{Minutes, Seconds, StreamingContext}

object RealTimeApp {
//    def main(args: Array[String]): Unit = {
//
//        val spark = SparkSession
//            .builder()
//            .appName("HippoRealTimeApp")
//            .master("local[*]")
//            .getOrCreate()
//
//        import spark.implicits._
//        spark.sparkContext.setLogLevel("warn")
//        //从kafka读取数据,为了方便后续处理,封装数据到clickInfo样例类中
//       val clkDS= spark.readStream
//            .format("kafka")
//            .option("","")
//            .option("","")
//            .load()
//            .select("value")
//            .as[String]
//            .map(item => {
//                val x = item.split("\\t")
//                Clk(x(1).toInt, x(2).trim, x(3).trim, x(15).trim, x(17).trim, x(18).trim, x(21).trim, x(22).trim, x(23).trim, x(25).trim)
//            })
//           .withWatermark("timestamp","2 hours") //2小时的数据,超过就过期了
//
//        //需求:全局top推荐
//
//    }

    def main(args: Array[String]): Unit = {
        //1.创建SparkConf
        val conf = new SparkConf().setAppName("HippoStreaming")
            .setMaster("local[*]")
            .set("spark.streaming.kafka.consumer.poll.ms", "30000");


        //2.创建SparkStreaming 的入口对象:StreamingContext
        val ssc = new StreamingContext(conf,Minutes(1))
        ssc.sparkContext.setLogLevel("warn")
//        ssc.checkpoint("./hippo_clk_checkpoint")
        //3.创建DStream
        val kafkaDStream= MyKafkaUtil.getKafkaStream(PropertiesUtil.load("config.properties").getProperty("kafka.topic.clk"),ssc)

        //4.将Kafka读出的数据转换为样例类对象
        val clkLogDStream = kafkaDStream.mapPartitions(iter => {
            val clkLogs = iter
                .map(record => if(record.value() == null ) null else record.value().split("\t"))
                .filter(arr =>  arr !="" && arr.length > 21)
                .map( arr =>{
                    //  频道,//类型,1新闻 2广告,    //新闻id或广告位置 //cookie
                    //channel:String,logType:String,contentId:String,cookie:String
                    Clk_log(arr(3).trim,arr(15).trim, arr(18).trim, arr(19).trim, arr(20).trim)
                 })
                .filter(
                    c => (c!=null) &&
                        c.logType == "1" &&
                        (c.contentId != null || c.contentId != "") &&
                        c.contentId.length > 32 &&
                        c.contentId.contains("_") &&
                        c.channel.matches("[\\u4e00-\\u9fa5]*") //频道为中文
                ) //过滤内容ID为空的和前提 logType为新闻的
            clkLogs
        })

        //1.开窗 => 时间间隔为2小时 window
//        val windowClkLogDStream = clkLogDStream.window(Minutes(120),Minutes(1))
//        windowClkLogDStream.cache()

        //5.需求1.统计两小时的全局TopN
//        TopNewsIdParseHandler.statTopAll(windowClkLogDStream)
//        TopNewsIdParseHandler.statTOPChannel(windowClkLogDStream)
        TopNewsIdParseHandler.statTop(clkLogDStream)
        ssc.start()
        ssc.awaitTermination()




    }
}

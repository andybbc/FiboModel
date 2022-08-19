package com.advlion.www.collaborative.analysis

import java.io.{BufferedWriter, File, FileWriter}

import com.advlion.www.collaborative.Clk_log
import com.advlion.www.collaborative.analysis.handler.DemandRealize
import com.advlion.www.utils.Flag
import org.apache.spark.rdd.RDD
import org.apache.spark.sql.SparkSession
import org.apache.spark.{SparkConf, SparkContext, sql}

object AnalysisTask {
    def main(args: Array[String]): Unit = {

        Flag.Parse(args)
        val hdfsInputPath = Flag.GetString("hdfs_input_path") //hdfs文件输入路径
        val localOutPath = Flag.GetString("local_out_path")

        val sparkConf = new SparkConf().setAppName("HippoAnalysis")

        val sc = new SparkContext(sparkConf)
        val spark = SparkSession.builder().getOrCreate()
        import spark.implicits._

        val rdd = sc.textFile(hdfsInputPath)

        val clkLogRDD = parseRawRDD(rdd)
        //分析
        val clkDF = clkLogRDD.toDF()
        clkDF.createOrReplaceTempView("clk")

        var bw: BufferedWriter = null
        try {
            bw = new BufferedWriter(new FileWriter(new File(localOutPath)))
            DemandRealize.getMaxORMin(spark, bw)
        } catch {
            case exception: Exception => exception.printStackTrace()
        } finally {
            if (bw != null) {
                bw.close()
            }
        }


    }


    /**
      * 转换RDD
      */
    def parseRawRDD(rdd: RDD[String]): RDD[Clk_log] = {
        val clkLogRDD = rdd.mapPartitions(iter => {
            val clkLogs = iter.map(line => {
                val arr = line.split("\t")
                //  频道,//类型,1新闻 2广告,    //新闻id或广告位置 //cookie
                //channel:String,logType:String,contentId:String,cookie:String
                Clk_log(arr(3).trim, arr(15).trim, arr(18).trim, arr(19).trim, arr(20).trim)
            })
                .filter(c => c.logType == "1" && (c.contentId != null || c.contentId != "") && c.contentId.length > 32 && c.contentId.contains("_")) //过滤内容ID为空的和前提 logType为新闻的
            clkLogs
        })
        clkLogRDD
    }
}

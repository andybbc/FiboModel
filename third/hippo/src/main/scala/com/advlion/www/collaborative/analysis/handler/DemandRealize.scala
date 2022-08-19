package com.advlion.www.collaborative.analysis.handler

import java.io.BufferedWriter

import com.advlion.www.collaborative.Clk_log
import org.apache.spark.rdd.RDD
import org.apache.spark.sql.SparkSession

/**
  * 需求实现
  */
object DemandRealize {

    /**
      * 获取次数最大值
      */
    def getMaxCount(rdd: RDD[Clk_log]) = {
        val reduceRDD = rdd.map(c => (c.contentId, 1))
            .reduceByKey(_ + _)

        reduceRDD.cache()

        //最大值
        val maxRes = reduceRDD.max()(new Ordering[(String, Int)]() {
            override def compare(x: (String, Int), y: (String, Int)): Int = {
                Ordering[Int].compare(x._2, y._2)
            }
        })


        //最小值
        val minRes = reduceRDD.min()(new Ordering[(String, Int)]() {
            override def compare(x: (String, Int), y: (String, Int)): Int = {
                Ordering[Int].compare(x._2, y._2)
            }
        })


    }


    def getMaxORMin(spark: SparkSession, bw: BufferedWriter) = {
        //每个cookie_id对应的distinct 新闻id的count
        val df = spark.sql(
            s"""
               |
               |select
               |  max(cnt) as max_cnt,
               |  min(cnt) as min_cnt,
               |  avg(cnt) as avg_cnt,
               |  percentile(cnt,0.5) as mid_count
               |from
               |(
               |select
               |contentId,
               |count(1) cnt
               |from
               |(
               |select
               |   distinct contentId,cookie
               |from
               |clk
               |) t
               |group by contentId
               |) t
               |
               |""".stripMargin)

        //要拉会本地处理,不然会报错
        df.collect().foreach { row =>
            bw.write("max_count:"+row.getAs[Long]("max_cnt").toString)
            bw.newLine()
            bw.flush()
            bw.write("mix_count:"+row.getAs[Long]("min_cnt").toString)
            bw.newLine()
            bw.flush()
            bw.write("avg_count:"+row.getAs[Long]("avg_cnt").toString)
            bw.newLine()
            bw.flush()
            bw.write("mid_count:"+row.getAs[Long]("mid_count").toString)
            bw.newLine()
            bw.flush()
        }


    }
}

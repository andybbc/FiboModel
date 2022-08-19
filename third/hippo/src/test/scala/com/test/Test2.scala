package com.test

import org.apache.spark.rdd.RDD
import org.apache.spark.sql.SparkSession
import org.apache.spark.{SparkConf, SparkContext}

import scala.annotation.tailrec
import scala.collection.mutable.ListBuffer
import scala.collection.{immutable, mutable}

object Test2 {
    def main(args: Array[String]): Unit = {
        //        val list = List(("a",210),("b",33),("c",71),("d",11),("e",77))
        //        println(getTopN(list,3).toList)
        //
        //        println("中文".matches("[\\u4e00-\\u9fa5]*"))

        val conf = new SparkConf().setAppName("HippoStreaming")
            .setMaster("local[*]")
            .set("spark.streaming.kafka.consumer.poll.ms", "30000")
        //
        val sc = new SparkContext(conf)
//        val spark= SparkSession.builder().getOrCreate()
//        import spark.implicits._


        val list1 = sc.makeRDD(mutable.ListBuffer(1, 2, 3))
        val list2 = sc.makeRDD(mutable.ListBuffer(4, 5, 6))
        val list3 = sc.makeRDD(mutable.ListBuffer(7, 8, 9))
        val list4 = sc.makeRDD(mutable.ListBuffer(10, 11, 12))
        val list5 = sc.makeRDD(mutable.ListBuffer(13, 14, 15))
        val list6 = sc.makeRDD(mutable.ListBuffer(16, 17, 18))
        val list7 = sc.makeRDD(mutable.ListBuffer(19, 20, 21))


        val rdd = list1.zip(list2).zip(list3).zip(list4).zip(list5).zip(list6).zip(list7)
            .map(t => {
                val listBuffer = ListBuffer[Int]()
                myFlatMap(t, listBuffer).reverse
            }).map(x => (x(0),x(1),x(2),x(3),x(4),x(5),x(6)))


        println(rdd.collect().foreach(println(_)))
        println("==========")

//        rdd.toDF("a","b","c","d")









        //

        //
        //        10
        //
        //        import spark.implicits._
        //
        //       val rdd = sc.makeRDD(listn)
        //               .foldByKey()
        //           rdd.map(t => (t._1,t._2(0),t._2(1),t._2(2))).toDF("row","a","b","c")

        val listBuffer = ListBuffer[Int]()
        myFlatMap((((1, 2), 3), 4), listBuffer)
        println(listBuffer)

    }

    def getTopN(items: scala.Iterable[(String, Int)], topN: Int) = {
        var sortedSet = mutable.SortedSet.empty[(String, Int)](Ordering.by((x: (String, Int)) => x._2))
        items.foreach({ tuple => {
            sortedSet += tuple
            if (sortedSet.size > topN) {
                sortedSet = sortedSet.takeRight(topN)
            }
        }
        })
        sortedSet.takeRight(topN).toIterator

    }


    def myFlatMap(tuple2: (Any, Int), listBuffer: ListBuffer[Int]): ListBuffer[Int] = {
        listBuffer.append(tuple2._2)
        val t1 = tuple2._1
        t1 match {
            case (t: Any, i: Int) =>
                myFlatMap((t, i), listBuffer)
            case _ => listBuffer.append(t1.asInstanceOf[Int])
        }
        listBuffer
    }


}

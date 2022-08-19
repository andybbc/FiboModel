package com.test

import scala.util.control.Breaks._
import scala.collection.mutable.ArrayBuffer
import java.util.BitSet
import org.apache.spark.SparkContext
import org.apache.spark.SparkContext._
import org.apache.spark._


object Apriori {
    def main(args: Array[String]) {
        if (args.length != 2) {
            println("USage:<Datapath> <Output>")
        }
        //initial SparkContext
        val sc = new SparkContext()
        val SUPPORT_NUM = 15278611 //Transactions total is num=17974836, SUPPORT_NUM = num*0.85
        val TRANSACITON_NUM = 17974836.0
        val K = 8


        //All transactions after removing transaction ID, and here we combine the same transactions.
        val transactions = sc.textFile(args(0)).map(line =>
            line.substring(line.indexOf(" ") + 1).trim).map((_, 1)).reduceByKey(_ + _).map(line => {
            val bitSet = new BitSet()
            val ss = line._1.split(" ")
            for (i <- 0 until ss.length) {
                bitSet.set(ss(i).toInt, true)
            }
            (bitSet, line._2)
        }).cache()


        //To get 1 frequent itemset, here, fi represents frequent itemset
        var fi = transactions.flatMap { line =>
            val tmp = new ArrayBuffer[(String, Int)]
            for (i <- 0 until line._1.size()) {
                if (line._1.get(i)) tmp += ((i.toString, line._2))
            }
            tmp
        }.reduceByKey(_ + _).filter(line1 => line1._2 >= SUPPORT_NUM).cache()
        val result = fi.map(line => line._1 + ":" + line._2 / TRANSACITON_NUM)
        result.saveAsTextFile(args(1) + "/result-1")


        for (i <- 2 to K) {
            val candiateFI = getCandiateFI(fi.map(_._1).collect(), i)
            val bccFI = sc.broadcast(candiateFI)
            //To get the final frequent itemset
            fi = transactions.flatMap { line =>
                val tmp = new ArrayBuffer[(String, Int)]()
                //To check if each itemset of candiateFI in transactions
                bccFI.value.foreach { itemset =>
                    val itemArray = itemset.split(",")
                    var count = 0
                    for (item <- itemArray) if (line._1.get(item.toInt)) count += 1
                    if (count == itemArray.size) tmp += ((itemset, line._2))
                }
                tmp
            }.reduceByKey(_ + _).filter(_._2 >= SUPPORT_NUM).cache()
            val result = fi.map(line => line._1 + ":" + line._2 / TRANSACITON_NUM)
            result.saveAsTextFile(args(1) + "/result-" + i)
            bccFI.unpersist()
        }
    }


    //To get the candiate k frequent itemset from k-1 frequent itemset
    def getCandiateFI(f: Array[String], tag: Int) = {
        val separator = ","
        val arrayBuffer = ArrayBuffer[String]()
        for (i <- 0 until f.length; j <- i + 1 until f.length) {
            var tmp = ""
            if (2 == tag) tmp = (f(i) + "," + f(j)).split(",").sortWith((a, b) => a.toInt <= b.toInt).reduce(_ + "," + _)
            else {
                if (f(i).substring(0, f(i).lastIndexOf(',')).equals(f(j).substring(0, f(j).lastIndexOf(',')))) {
                    tmp = (f(i) + f(j).substring(f(j).lastIndexOf(','))).split(",").sortWith((a, b) => a.toInt <= b.toInt).reduce(_ + "," + _)
                }
            }
            var hasInfrequentSubItem = false //To filter the item which has infrequent subitem
            if (!tmp.equals("")) {
                val arrayTmp = tmp.split(separator)
                breakable {
                    for (i <- 0 until arrayTmp.size) {
                        var subItem = ""
                        for (j <- 0 until arrayTmp.size) {
                            if (j != i) subItem += arrayTmp(j) + separator
                        }
                        //To remove the separator "," in the end of the item
                        subItem = subItem.substring(0, subItem.lastIndexOf(separator))
                        if (!f.contains(subItem)) {
                            hasInfrequentSubItem = true
                            break
                        }
                    }
                } //breakable
            }
            else hasInfrequentSubItem = true
            //If itemset has no sub inftequent itemset, then put it into candiateFI
            if (!hasInfrequentSubItem) arrayBuffer += (tmp)
        } //for
        arrayBuffer.toArray
    }
}

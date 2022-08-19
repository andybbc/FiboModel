package com.test

import scala.collection.mutable

object Test4 {
    def main(args: Array[String]): Unit = {
        val items = List(("a",1),("b",-7),("c",4),("d",7),("e",-4))
        println(getTopN(items,3))
    }


    def getTopN( items:List[(String, Int)],topN:Int) = {
        var sortedSet = mutable.SortedSet.empty[(String,Int)](Ordering.by((x:(String,Int)) => x._2))
        items.foreach({ tuple => {
            sortedSet += tuple
            if (sortedSet.size > topN) {
                sortedSet = sortedSet.takeRight(topN)
            }
        }
        })
        sortedSet.takeRight(topN).toIterator

    }
}

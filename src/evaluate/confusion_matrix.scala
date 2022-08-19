import scala.io.Source

/**
 * @description:
 * @author: malichun
 * @time: 2021/1/5/0005 15:34
 *
 */
object confusion_matrix {
    def main(args: Array[String]): Unit = {
        val originFilePath = args(0)
        val predictFilePath: String = args(1)

        val originFile = Source.fromFile(originFilePath)
        val predictFile = Source.fromFile(predictFilePath)
        //真实的
        val originLines = originFile.getLines().toList

        //predict
        val predictLines = predictFile.getLines().toList.map(line => {
            val arr = line.split(" ")
            val d = arr(arr.length - 1)
            val bigDecimal = BigDecimal(d)
            //前面一个0.5的准确率,后面一个0.4当成1的准确率
            (if(bigDecimal >= 0.5) "1" else "0",if(bigDecimal >= 0.4) "1" else "0")

        })

        val zippedLines:List[(String,(String,String))] = originLines zip predictLines

        val resMap = (scala.collection.mutable.Map[String,scala.collection.mutable.Map[(String,String),Int]]() /: zippedLines){ case (m,v:(String,(String,String)))=>
            val real = v._1
            val predict5 = v._2._1
            val predict4 = v._2._2
            val m5 = m.getOrElse("predict5",scala.collection.mutable.Map[(String,String),Int]())
            val m4 = m.getOrElse("predict4",scala.collection.mutable.Map[(String,String),Int]())

            val value5 =  m5.getOrElse((real,predict5),0)
            m5((real,predict5))= value5+1

            val value4 =  m4.getOrElse((real,predict4),0)
            m4((real,predict4))= value4+1

            m("predict5") = m5
            m("predict4") = m4
            m
        }
        resMap.foreach(m => {
            val key = m._1
            val mm = m._2
            val sum = mm.values.sum
            println("left : real     right: pred")
            println(s"============${key}===============")
            mm.foreach{ case ((k,v),count) =>
                println(((k,v),count,count.toDouble/sum))
            }
            println("")
            val FN = mm.getOrElse(("1","0"),0)
            val FP = mm.getOrElse(("0","1"),0)
            val TP = mm.getOrElse(("1","1"),0)
            val TN = mm.getOrElse(("0","0"),0)

            val TPR = TP.toDouble / (TP + FN)  //
            val FPR = FP.toDouble / (FP + TN)
            val TNR = TN.toDouble / (TN + FP)
            val FNR = FN.toDouble / (FN + TP)  // miss rate丢失率
            println(
                s"""
                  |TPR(事实为真预估为真的概率(真正率,越大越好)):${TPR}
                  |FPR(事实为假预估为真的概率(假正率)):${FPR}
                  |TNR(事实为假预估为假的概率(真负率)):${TNR}
                  |FNR(事实为真预估为假的概率(假负率/丢失率,越小越好)):${FNR}
                  |""".stripMargin)
        })


    }


}

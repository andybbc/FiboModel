import scala.io.Source

/**
 * @description:
 * @author: malichun
 * @time: 2021/1/12/0012 18:42
 *
 */
object ctr_rate_stat {
    def main(args: Array[String]): Unit = {
        //输出0.1,0.2.....0.9出现的概率
        val inputFile = args(0)
        val bufferedSource = Source.fromFile(inputFile)
        val lines: Iterator[String] = bufferedSource.getLines()
        val resMap = (scala.collection.mutable.Map[String,Int]() /: lines)((m,v )=>{
	        val arr = v.split(" ")
	        val d = arr(arr.length -1 )
            val bigDecimal = BigDecimal(d)
            val key = bigDecimal toString() substring(0,3)

            val value = m.getOrElse(key,0)
            m(key)= value+1
            m("total") = m.getOrElse("total",0) +1
            m
        })

        val totalNum = resMap.remove("total").get
        resMap.toList.sortBy(_._1).foreach{ case (k,v) =>
            if(k == "0.5"){
                println("=========")
            }
            println(s"$k => $v\trate => ${v.toDouble/totalNum}")
        }
        println()
        println("<0.5=========")
        println((resMap.getOrElse("0.0",0)+resMap.getOrElse("0.1",0)+resMap.getOrElse("0.2",0)+resMap.getOrElse("0.3",0)+resMap.getOrElse("0.4",0))/totalNum.toDouble)
        println()
        println(">0.5=========")
        println((resMap.getOrElse("0.5",0)+resMap.getOrElse("0.6",0)+resMap.getOrElse("0.7",0)+resMap.getOrElse("0.8",0)+resMap.getOrElse("0.9",0))/totalNum.toDouble)


        bufferedSource.close()
    }
}

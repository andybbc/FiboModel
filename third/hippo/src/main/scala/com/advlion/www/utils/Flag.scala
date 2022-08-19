package com.advlion.www.utils

import collection.mutable.Map

/**
  * 解析命令行参数
  * 命令行格式
  * （1）、-project=test -date=2019-01-01
  * （2）、-project test -date 2019-01-01
  * eg:
  * Flag.Parse(args)
  * Flag.GetInt("num", 0)
  */
object Flag {
    //存放参数map
    private val argsMap = Map[String, Any]()
    //参数个数
    var ArgsNum = 0

    /**
      * 解析args
      * @param args
      */
    def Parse(args: Array[String]): Unit = {
        var flag = false
        for (argLine <- args) {
            val argArr = argLine.split("=")
            if (argLine.startsWith("-") && argArr.length == 2) {
                flag = true
                argsMap += (argArr(0).replaceAll("^-*","") -> argArr(1))
            }
        }

        //解析另一种模式
        if (!flag) {
            val length = args.length
            for (index <- 0 until length) {
                if (index % 2 == 0 && index + 1 < length) {
                    argsMap += (args(index).replaceAll("^-*","") -> args(index + 1))
                }
            }
        }
        ArgsNum = this.argsMap.count(_ => true)

        println(
            s"""
               |==输入参数个数:$ArgsNum==
               |${argsMap.foreach(t => println(t._1+":"+t._2))}
               |""".stripMargin)
    }

    /**
      * 获取int型参数
      * @param key
      * @param default
      * @return
      */
    def GetInt(key: String, default: Any = 0): Int = {
        argsMap.getOrElse(key, default).toString.toInt
    }

    /**
      * 获取Char型参数
      * @param key
      * @param default
      * @return
      */
    def GetChar(key: String, default: Any = ""): Char = {
        argsMap.getOrElse(key, default).toString.charAt(0)
    }

    /**
      * 获取Double型参数
      * @param key
      * @param default
      * @return
      */
    def GetDouble(key: String, default: Any = 0): Double = {
        argsMap.getOrElse(key, default).toString.toDouble
    }

    /**
      * 获取Boolean型参数
      * @param key
      * @param default
      * @return
      */
    def GetBoolean(key: String, default: Any = false): Boolean = {
        argsMap.getOrElse(key, default).toString.toBoolean
    }

    /**
      * 获取string型参数
      * @param key
      * @param default
      * @return
      */
    def GetString(key: String, default: Any = ""): String = {
        argsMap.getOrElse(key, default).toString
    }

    def printParam = {
        println(argsMap.toString())
    }

    def main(args: Array[String]): Unit = {
            Flag.Parse(args)
            val name = Flag.GetString("name")
        val age = Flag.GetInt("age")
        val input= Flag.GetString("input_file")
        println(name,age,input)

    }
}


package com.advlion.www.collaborative.analysis.udfs

import org.apache.spark.sql.Row
import org.apache.spark.sql.expressions.{MutableAggregationBuffer, UserDefinedAggregateFunction}
import org.apache.spark.sql.types.{DataType, LongType, StructField, StructType}

/**
  * 求中位数的函数
  */
class CustomMedianUDAF extends UserDefinedAggregateFunction{

    /**
      * 返回聚合函数输入参数的数据类型
      * @return
      */
    override def inputSchema: StructType = StructType(StructField("inputColum",LongType) :: Nil)

    /**
      * 聚合缓冲区中值的类型
      * @return
      */
    override def bufferSchema: StructType = StructType(StructField("sum", LongType) :: StructField("count", LongType) :: Nil)

    /**
      * 最终返回值类型
      * @return
      */
    override def dataType: DataType = LongType

    /**
      * 确定性:如果同样的输入是否返回同样的输出
      * @return
      */
    override def deterministic: Boolean = ???

    /**
      * 初始化
      * @param buffer
      */
    override def initialize(buffer: MutableAggregationBuffer): Unit = ???

    /**
      *同一个Executor间的合并
      * @param buffer
      * @param input
      */
    override def update(buffer: MutableAggregationBuffer, input: Row): Unit = ???

    /**
      * 不同Executor间的合并
      * @param buffer1
      * @param buffer2
      */
    override def merge(buffer1: MutableAggregationBuffer, buffer2: Row): Unit = ???

    /**
      * 计算最终结果,因为是聚合函数,所以最后只有一行了
      * @param buffer
      * @return
      */
    override def evaluate(buffer: Row): Any = ???
}

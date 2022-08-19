package com.test

import org.apache.spark.ml.fpm.FPGrowth
import org.apache.spark.sql.SparkSession

object FPGrowthDemo {
    def main(args: Array[String]): Unit = {
        val spark = SparkSession
            .builder
            .appName("FPGrowthDemo").master("local[*]")
            //            .config("spark.sql.warehouse.dir", "C:\\study\\sparktest")
            .getOrCreate()
        //val spark = getSparkSession("FPGrowthDemo")

        import spark.implicits._
        val dataset = spark.createDataset(Seq(
            "1 2 5",
            "1 2 3 5",
            "1 2  ")
        ).map(t => t.split(" ")).toDF("items")

        val fpgroth = new FPGrowth().setItemsCol("items").setMinSupport(0.5).setMinConfidence(0.6)
        val model = fpgroth.fit(dataset)
        // Display frequent itemsets.
        model.freqItemsets.show()

        // Display generated association rules.
        model.associationRules.show()
        // transform examines the input items against all the association rules and summarize the
        // consequents as prediction
        model.transform(dataset).show()
        // $example off$

        spark.stop()
    }
}
package xgboostJava.convert

import java.io.{BufferedWriter, File, FileWriter}

import scala.io.Source

/**
 * @description:
 * @author: malichun
 * @time: 2021/5/5/0005 15:53
 *
 */
object Csv2LibSvm extends App {
    val sep = ","

    val trainFilePath = "E:\\gitdir\\projects\\untitled\\src\\main\\resources2\\train.txt"
    val trainFilePath2 = "E:\\gitdir\\projects\\untitled\\src\\main\\resources2\\train.libsvm"
    convertCsv(trainFilePath, trainFilePath2, "train")


    val testFilePath = "E:\\gitdir\\projects\\untitled\\src\\main\\resources2\\test.txt"
    val testFilePath2 = "E:\\gitdir\\projects\\untitled\\src\\main\\resources2\\test.libsvm"
    convertCsv(testFilePath, testFilePath2, "train")

    val predictFilePath = "E:\\gitdir\\projects\\untitled\\src\\main\\resources2\\predict.txt"
    val predictFilePath2 = "E:\\gitdir\\projects\\untitled\\src\\main\\resources2\\predict.libsvm"
    convertCsv(predictFilePath, predictFilePath2, "predict")


    def convertCsv(originPath: String, outPath: String, fileType: String): Unit = {
        fileType match {
            case "train" =>
                val path = Source.fromFile(originPath)
                val strings = path.getLines()

                val bw = new BufferedWriter(new FileWriter(new File(outPath)))
                strings.foldLeft(bw)((bw, line) => {
                    val arr = line.split(sep)

                    val label = arr(0)

                    val str = arr.zipWithIndex
                        .map(t => s"${t._2}:${t._1}")
                        .tail
                        .mkString(" ")

                    bw.write(label + " " + str)
                    bw.newLine()
                    bw.flush
                    bw
                }) close

                path.close()

            case "predict" =>
                val path = Source.fromFile(originPath)
                val strings = path.getLines()

                val bw = new BufferedWriter(new FileWriter(new File(outPath)))

                strings.foldLeft(bw)((bw, line) => {
                    val str = line.split(sep)
                        .zipWithIndex
                        .map(t => s"${t._2 + 1}:${t._1}")
                        .mkString(" ")

                    bw.write("0 " + str)
                    bw.newLine()
                    bw.flush
                    bw
                }) close

        }
    }


}

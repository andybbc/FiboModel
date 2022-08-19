package xgboostJava.product;

import ml.dmlc.xgboost4j.java.Booster;
import ml.dmlc.xgboost4j.java.DMatrix;
import ml.dmlc.xgboost4j.java.XGBoost;
import ml.dmlc.xgboost4j.java.XGBoostError;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;

/**
 * @description:
 * @author: malichun
 * @time: 2021/5/5/0005 13:31
 */
public class XgboostPredictBatchProduct {
    private static DMatrix predictMat = null;

    // 传入参数
    public static void main(String [] args) throws XGBoostError, IOException {
        String predictFilePath ="E:\\gitdir\\projects\\untitled\\src\\main\\resources2\\predict.libsvm";
        String predictResFilePath = "E:\\gitdir\\projects\\untitled\\src\\main\\resources2\\predict_res.libsvm";
        predictMat = new DMatrix(predictFilePath);

        Booster booster = XGBoost.loadModel("src/main/resources2/out_test.bin");
        float[][] predicts = booster.predict(predictMat);

        BufferedWriter bw = new BufferedWriter(new FileWriter(new File(predictResFilePath)));

        for (float[] array : predicts) {
            for (float values : array) {
//                System.out.print(values + " ");
                bw.write(String.valueOf(values));
                bw.newLine();
                bw.flush();
            }
//            System.out.println();
        }

        bw.close();




    }

}

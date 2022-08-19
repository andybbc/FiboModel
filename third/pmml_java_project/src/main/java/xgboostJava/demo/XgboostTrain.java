package xgboostJava.demo;

import ml.dmlc.xgboost4j.java.Booster;
import ml.dmlc.xgboost4j.java.DMatrix;
import ml.dmlc.xgboost4j.java.XGBoost;
import ml.dmlc.xgboost4j.java.XGBoostError;

import java.util.HashMap;
import java.util.Map;

/**
 * @description: https://blog.csdn.net/qq_24834541/article/details/103797256
 * @author: malichun
 * @time: 2021/4/30/0030 13:58
 */
public class XgboostTrain {
    private static DMatrix trainMat = null;
    private static DMatrix testMat = null;
    //传入参数
    public static void main(String [] args) throws XGBoostError {
//        String trainFile = args[0];
//        String testFile = args[1];
//        String outModelPath = args[2];

        String trainFile="E:\\gitdir\\projects\\untitled\\src\\main\\resources2\\train.txt";
//        String testFile ="E:\\gitdir\\projects\\untitled\\src\\main\\resources\\test.txt";
        String outModelPath="E:\\gitdir\\projects\\untitled\\src\\main\\resources2\\out_test.bin";

        try {
//            trainMat = new DMatrix("/data/algorithm/test/train.txt");
            trainMat = new DMatrix(trainFile);
        } catch (XGBoostError xgBoostError) {
            xgBoostError.printStackTrace();
        }
//        try {
////            testMat = new DMatrix("/data/algorithm/test/test.txt");
//            testMat = new DMatrix(testFile);
//        } catch (XGBoostError xgBoostError) {
//            xgBoostError.printStackTrace();
//        }

        Map<String, Object> params = new HashMap<String, Object>() {
            {
                put("eta", 1.0);
                put("max_depth", 6);
                put("learning_rate",0.1);
                put("n_estimator",100);
                put("objective", "binary:logistic");
                put("eval_metric", "logloss");
                put("scale_pos_weight",2.5);
                put("min_child_weight",0.9);
                put("gamma",0.1);
                put("subsample",0.9);
                put("colsample_bylevel",0.5);
                put("n_jobs",4);
                put("seed",27);
                put("nthread",-1);


            }
        };

        Map<String, DMatrix> watches = new HashMap<String, DMatrix>() {
            {
                put("train",trainMat);
//                put("test", testMat);
            }
        };
        int nround = 10;
        try {
            Booster booster = XGBoost.train(trainMat, params, nround, watches, null, null);
            booster.saveModel(outModelPath);
//            booster.saveModel("/data/algorithm/test/model.bin");


        } catch (XGBoostError xgBoostError) {
            xgBoostError.printStackTrace();
        }
    }


//    public static void main(String [] args) throws XGBoostError {
//
//        try {
////            trainMat = new DMatrix("/data/algorithm/test/train.txt");
//            trainMat = new DMatrix("E:\\gitdir\\projects\\untitled\\src\\main\\resources\\train.txt");
//        } catch (XGBoostError xgBoostError) {
//            xgBoostError.printStackTrace();
//        }
//        try {
////            testMat = new DMatrix("/data/algorithm/test/test.txt");
//            testMat = new DMatrix("E:\\gitdir\\projects\\untitled\\src\\main\\resources\\test.txt");
//        } catch (XGBoostError xgBoostError) {
//            xgBoostError.printStackTrace();
//        }
//
//        Map<String, Object> params = new HashMap<String, Object>() {
//            {
//                put("eta", 1.0);
//                put("max_depth", 3);
//                put("objective", "binary:logistic");
//                put("eval_metric", "logloss");
//            }
//        };
//
//        Map<String, DMatrix> watches = new HashMap<String, DMatrix>() {
//            {
//                put("train",trainMat);
//                put("test", testMat);
//            }
//        };
//        int nround = 10;
//        try {
//            Booster booster = XGBoost.train(trainMat, params, nround, watches, null, null);
//            booster.saveModel("E:\\gitdir\\projects\\untitled\\src\\main\\resources\\model.bin");
////            booster.saveModel("/data/algorithm/test/model.bin");
//
//
//        } catch (XGBoostError xgBoostError) {
//            xgBoostError.printStackTrace();
//        }
//    }
}
